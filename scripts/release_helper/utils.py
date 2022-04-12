from github.Issue import Issue
from github.Repository import Repository
import logging
from typing import List

REQUEST_REPO = 'Azure/sdk-release-request'
REST_REPO = 'Azure/azure-rest-api-specs'
AUTO_ASSIGN_LABEL = 'assigned'
AUTO_PARSE_LABEL = 'auto-link'
MULTI_LINK_LABEL = 'MultiLink'

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


class IssuePackage:
    issue = None  # origin issue instance
    rest_repo = None  # repo instance: Azure/azure-rest-api-specs
    labels_name = {}  # name set of issue labels

    def __init__(self, issue: Issue, rest_repo: Repository):
        self.issue = issue
        self.rest_repo = rest_repo
        self.labels_name = {label.name for label in issue.labels}
