import datetime
import logging
import os
import re
from typing import List, Any

from bs4 import BeautifulSoup
from github.Issue import Issue
from github.Repository import Repository
import requests
from azure.devops.v6_0.pipelines.pipelines_client import PipelinesClient
from azure.devops.v6_0.pipelines import models
from msrest.authentication import BasicAuthentication

REQUEST_REPO = 'Azure/sdk-release-request'
REST_REPO = 'Azure/azure-rest-api-specs'
AUTO_ASSIGN_LABEL = 'assigned'
AUTO_PARSE_LABEL = 'auto-link'
AUTO_CLOSE_LABEL = 'auto-close'
MULTI_LINK_LABEL = 'MultiLink'
INCONSISTENT_TAG = 'Inconsistent tag'

_LOG = logging.getLogger(__name__)


def get_origin_link_and_tag(issue_body_list: List[str]) -> (str, str):
    link, readme_tag = '', ''
    for row in issue_body_list:
        if 'link' in row.lower() and link == '':
            link = row.split(":", 1)[-1].strip()
        if 'readme tag' in row.lower() and readme_tag == '':
            readme_tag = row.split(":", 1)[-1].strip()
        if link and readme_tag:
            break

    if link.count('https') > 1:
        link = link.split(']')[0]
        link = link.replace('[', "").replace(']', "").replace('(', "").replace(')', "")
    return link, readme_tag


def get_last_released_date(package_name: str) -> (str, str):
    pypi_link = f'https://pypi.org/project/{package_name}/#history'
    res = requests.get(pypi_link)
    soup = BeautifulSoup(res.text, 'html.parser')
    # find top div from <div class="release-timeline">
    try:
        package_info = soup.select('div[class="release-timeline"]')[0].find_all('div')[0]
        last_version_mix = package_info.find_all('p', class_="release__version")[0].contents[0]
    except IndexError as e:
        return '', ''
    last_version = last_version_mix.replace(' ', '').replace('\n', '')
    last_version_date_str = package_info.time.attrs['datetime'].split('+')[0]
    last_version_date = datetime.datetime.strptime(last_version_date_str, '%Y-%m-%dT%H:%M:%S')
    return last_version, last_version_date


# get python release pipeline link from web
def get_python_release_pipeline(output_folder):
    pipeline_client = PipelinesClient(base_url='https://dev.azure.com/azure-sdk',
                                      creds=BasicAuthentication(os.getenv('PIPELINE_TOKEN'), ''))
    pipelines = pipeline_client.list_pipelines(project='internal')
    for pipeline in pipelines:
        if re.findall('^python - \w*$', pipeline.name):
            key = pipeline.name.replace('python - ', '')
            if key == output_folder:
                pipeline_url = 'https://dev.azure.com/azure-sdk/internal/_build?definitionId={}'.format(pipeline.id)
                return pipeline_url
    else:
        _LOG.info('Cannot find definitionId, Do not display pipeline_url')
    return ''


# Run sdk-auto-release(main) to generate SDK
def run_pipeline(issue_link, pipeline_url, spec_readme, python_tag=""):
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
                "value": "",
                "isSecret": False
            },
            "ISSUE_LINK": {
                "value": issue_link,
                "isSecret": False
            },
            "PIPELINE_LINK": {
                "value": pipeline_url,
                "isSecret": False
            },
            "SPEC_README": {
                "value": spec_readme,
                "isSecret": False
            },
            "PYTHON_TAG": {
                "value": python_tag,
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
    result = client.run_pipeline(project='internal', pipeline_id=2500, run_parameters=run_parameters)
    return result.state == 'inProgress'


def record_release(package_name: str, issue_info: Any, file: str, version: str) -> None:
    created_at = issue_info.created_at.strftime('%Y-%m-%d')
    closed_at = issue_info.closed_at.strftime('%Y-%m-%d')
    assignee = issue_info.assignee.login
    link = issue_info.html_url
    is_stable = True if 'b' not in version else ''
    closed_issue_info = f'{package_name},{assignee},{created_at},{closed_at},{link},{version},{is_stable}\n'
    with open(file, 'r') as file_read:
        lines = file_read.readlines()
    with open(file, 'w') as file_write:
        lines.insert(1, closed_issue_info)
        file_write.writelines(lines)


class IssuePackage:
    issue = None  # origin issue instance
    rest_repo = None  # repo instance: Azure/azure-rest-api-specs
    labels_name = {}  # name set of issue labels

    def __init__(self, issue: Issue, rest_repo: Repository):
        self.issue = issue
        self.rest_repo = rest_repo
        self.labels_name = {label.name for label in issue.labels}
