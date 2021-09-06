import requests
import json
import os

url = os.getenv('URL')

headers = {
    'x-vss-reauthenticationaction': 'Suppress',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.73',
    'accept': 'application/json;api-version=5.1-preview.1;excludeUrls=true;enumsAsNumbers=true;msDateFormat=true;noArrayWrap=true',
    'Content-Type': 'application/json',
    'Cookie': ''
}


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
    headers['Cookie'] = os.getenv('COOKIE')
    response = requests.request("POST", url, headers=headers, data=payload)
    if 200 <= response.status_code < 300:
        return True
    else:
        print(response.text)
        return False
