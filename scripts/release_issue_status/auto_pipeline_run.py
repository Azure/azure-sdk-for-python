import json
import os
import re
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.pipelines.pipelines_client import PipelinesClient
from azure.devops.v6_0.pipelines import models
import requests


def run_pipeline(issue_link, sdk_issue_object, pipeline_url):
    paramaters = {
        "stages_to_skip": [],
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
    }
    # Fill in with your personal access token and org URL
    personal_access_token = os.getenv('PIPELINE_TOKEN')
    organization_url = 'https://dev.azure.com/azure-sdk'

    # Create a connection to the org
    credentials = BasicAuthentication('', personal_access_token)
    run_parameters = models.RunPipelineParameters(**paramaters)
    client = PipelinesClient(base_url=organization_url, creds=credentials)
    result = client.run_pipeline(project='internal',pipeline_id=2500,run_parameters=run_parameters)
    if result.state == 'inProgress':
        return True
    else:
        return False
