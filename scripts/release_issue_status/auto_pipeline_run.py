import requests
import json
import os

url = "https://dev.azure.com/azure-sdk/590cfd2a-581c-4dcb-a12e-6568ce786175/_apis/pipelines/2500/runs"


def run_pipeline(issue_link, sdk_issue_object):
    payload = json.dumps({
        "stagesToSkip": [],
        "resources": {
            "repositories": {
                "self": {
                    "refName": "refs/heads/main"
                }
            }
        },
        "variables": {
            "BASE_BRANCH": {
                "value": f"{sdk_issue_object.head.label}",
                "isSecret": False
            },
            "ISSUE_LINK": {
                "value": f"{issue_link}",
                "isSecret": False
            }
        }
    })
    headers = json.loads(os.getenv('HEADERS'))
    response = requests.request("POST", url, headers=headers, data=payload)
    if 200 <= response.status_code < 300:
        return True
    else:
        print(response.text)
        return False
