# nxw-event-rule-switcher
Allows switching of disabled status in NX Witness from python

## How to use

You can create credentials.py file, with following values, to set your custom credentials outside the script:
```Python
DEFAULT_HOST="https://localhost"
DEFAULT_PORT="7001"
DEFAULT_USER="admin"
DEFAULT_PASSWORD="*****"
```

In NX Witness, you must add a comment to your rule (bottom left corner in the rule window) you want to be able to swtich. Default value in script is `MY_RULE_IDENTIFIER`.

If you run the script, rule with comment used as an input parameter will switch it's `disabled` status.

```Bash
./event_rule_enable.py -r MY_RULE_IDENTIFIER
```

## More info about NX Witness REST API
- Authentication: https://support.networkoptix.com/hc/en-us/articles/4410505014423-Nx-Witness-Authentication-APIs
- General info about NX REST API: https://support.networkoptix.com/hc/en-us/articles/219573367-HTTP-REST-API
- Standard API documentation for your server: https://${YOUR_SERVER_IP}:${PORT}/#/api-tool/main?type=1
  - For local testing, the values usually can be:
    - YOUR_SERVER_IP=localhost
    - PORT=7001
