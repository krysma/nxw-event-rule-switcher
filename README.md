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
