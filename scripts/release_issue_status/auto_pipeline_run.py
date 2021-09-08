import json
import os
import re

import requests

_headers = {
    'x-vss-reauthenticationaction': 'Suppress',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.73',
    'accept': 'application/json;api-version=5.1-preview.1;excludeUrls=true;enumsAsNumbers=true;msDateFormat=true;noArrayWrap=true',
    'Content-Type': 'application/json',
    'Cookie': ''
}

def run_pipeline(issue_link, sdk_issue_object, pipeline_url):
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
            },
            "PIPELINE_LINK": {
                "value": f"{pipeline_url}",
                "isSecret": False
            }
        }
    })
    _headers['Cookie'] = os.getenv('COOKIE')
    response = requests.request("POST", os.getenv('URL'), headers=_headers, data=payload)
    if response.status_code == 200:
        return True
    else:
        print(response.status_code)
        return False


def get_pipeline_url(search_url):
    _headers['Cookie'] = os.getenv('COOKIE')
    res = requests.get(search_url, headers=_headers)
    try:
        definitionId = re.findall('"pipelines":\[{"id":(.*?),"name":"python', res.text)[0]
        pipeline_url = 'https://dev.azure.com/azure-sdk/internal/_build?definitionId={}'.format(definitionId)
    except Exception as e:
        print('Cannot find definitionId, Do not display pipeline_url')
        pipeline_url = ''
    return pipeline_url
