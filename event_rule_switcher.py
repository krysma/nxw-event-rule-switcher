#!/usr/bin/env python3

import json
import requests
import urllib3

from argparse import ArgumentParser

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from credentials import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_USER, DEFAULT_PASSWORD
except:
    DEFAULT_HOST="https://localhost"
    DEFAULT_PORT="7001"
    DEFAULT_USER="admin"
    DEFAULT_PASSWORD="*******"


def check_status(request, verbose):
    if request.status_code == requests.codes.ok:
        if verbose:
            print(f"Request successful\n{request.text}")
        return True
    print(f"{request.url} Request error {request.status_code}\n{request.text}")
    return False


def request_api(url, uri, method, **kwargs):
    server_url = f"{url}{uri}"
    response = requests.request(
        method,
        server_url,
        **kwargs
    )
    if not check_status(response, False):
        exit(1)
    if method == "DELETE":
        return response
    return response.json()


def create_header(bearer_token):
    return {"Authorization": f"Bearer {bearer_token}"}


def create_local_payload(username, password):
    return {
        "username": username,
        "password": password,
        "setCookie": False
    }


def is_local_user(apiResponse):
    return apiResponse["username"] == "admin"


def get_cloud_system_id(apiResponse):
    return apiResponse["cloudId"]


def is_expired(apiResponse):
    return int(apiResponse["expiresInS"]) < 1


def login(url, user, password):
    # STEP 1
    cloud_state = request_api(url, f"/rest/v1/login/users/{user}", "GET", verify=False)
    if not is_local_user(cloud_state):
        print(user + " is not a local user.")
        exit(1)

    # STEP 2
    payload = create_local_payload(user, password)
    primarySession = request_api(url, "/rest/v1/login/sessions", "POST", verify=False, json=payload)
    primaryToken = primarySession["token"]

    secondarySession = request_api(url, "/rest/v1/login/sessions", "POST", verify=False, json=payload)
    secondaryToken = secondarySession["token"]

    # STEP 3
    primaryTokenInfo = request_api(url, f"/rest/v1/login/sessions/{primaryToken}", "GET", verify=False)
    if is_expired(primaryTokenInfo):
        print("Expired token")
        exit(1)

    secondaryTokenInfo = request_api(url, f"/rest/v1/login/sessions/{secondaryToken}", "GET", verify=False)
    if is_expired(secondaryTokenInfo):
        print("Expired token")
        exit(1)

    return primaryToken, secondaryToken

def logout(url, token):
    request_api(url, f"/rest/v1/login/sessions/{token}", "DELETE", verify=False,
                headers=create_header(token))

def main(ruleCommentToSwitch):

    url = f"{DEFAULT_HOST}:{DEFAULT_PORT}"
    primaryToken, secondaryToken = login(url, DEFAULT_USER, DEFAULT_PASSWORD)

    primaryHeader = create_header(primaryToken)
    secondaryHeader = create_header(secondaryToken)

    eventRules = request_api(url, "/ec2/getEventRules?format=json", "GET", verify=False,
                              headers=primaryHeader)
    
    ruleToChange = None
    for rule in eventRules:
        if rule["comment"] == ruleCommentToSwitch:
            # print(json.dumps(rule, indent=2))
            ruleToChange = rule
            break
    
    if ruleToChange is None:
        print(f"Rule with comment {ruleCommentToSwitch} not found")
        logout(url, secondaryToken)
        exit(1)

    for key, value in ruleToChange.items():
        if isinstance(value, str) and value.startswith("{") and value[1] != "\"":
            # print(f"\nConverting {key} to JSON\n{value}")
            ruleToChange[key] = value[1:-1]
        elif isinstance(value, str) and (value.startswith("{") or value.startswith("[")):
            # print(f"\nConverting {key} to JSON\n{value}")
            ruleToChange[key] = json.loads(value)

    ruleToChange["disabled"] = not ruleToChange["disabled"]

    # print(json.dumps(ruleToChange, indent=2))

    rulePayload = {
        "comment": ruleToChange["comment"],
        "disabled": ruleToChange["disabled"],
        "eventState": ruleToChange["eventState"],
        "eventType": ruleToChange["eventType"],
        "id": ruleToChange["id"],
    }

    request_api(url, "/ec2/saveEventRule", "POST", verify=False, headers=secondaryHeader, json=rulePayload)

    logout(url, primaryToken)


def parseArgs():
    parser = ArgumentParser(description="Enable/Disable Event Rule")
    parser.add_argument(
        "-r", "--rule-comment",
        help="Comment of the rule to switch. Default: MY_RULE_IDENTIFIER",
        default="MY_RULE_IDENTIFIER"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parseArgs()
    main(args.rule_comment)
