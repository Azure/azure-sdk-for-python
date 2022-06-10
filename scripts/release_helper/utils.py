import datetime
import logging
from typing import List

from bs4 import BeautifulSoup
from github.Issue import Issue
from github.Repository import Repository
import requests

REQUEST_REPO = 'Azure/sdk-release-request'
REST_REPO = 'Azure/azure-rest-api-specs'
AUTO_ASSIGN_LABEL = 'assigned'
AUTO_PARSE_LABEL = 'auto-link'
AUTO_CLOSE_LABEL = 'auto-close'
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

def get_last_released_date(package_name):
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

class IssuePackage:
    issue = None  # origin issue instance
    rest_repo = None  # repo instance: Azure/azure-rest-api-specs
    labels_name = {}  # name set of issue labels

    def __init__(self, issue: Issue, rest_repo: Repository):
        self.issue = issue
        self.issue_num =
        self.rest_repo = rest_repo
        self.labels_name = {label.name for label in issue.labels}
