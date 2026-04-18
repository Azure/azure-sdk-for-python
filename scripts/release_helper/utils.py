import logging
import os
import json
from typing import List, Any
from datetime import datetime

from github.Issue import Issue
from github.Repository import Repository
from packaging.version import parse as Version
from urllib3 import Retry, PoolManager

REQUEST_REPO = 'Azure/sdk-release-request'
REST_REPO = 'Azure/azure-rest-api-specs'
AUTO_ASSIGN_LABEL = 'assigned'
AUTO_PARSE_LABEL = 'auto-link'
AUTO_CLOSE_LABEL = 'auto-close'
MULTI_LINK_LABEL = 'MultiLink'
INCONSISTENT_TAG = 'Inconsistent tag'
TYPESPEC_LABEL = 'TypeSpec'

_LOG = logging.getLogger(__name__)


def get_origin_link_and_tag(issue_body_list: List[str]) -> (str, str):
    link, readme_tag = '', ''
    for row in issue_body_list:
        if 'link' in row.lower() and 'release request' not in row.lower() and link == '':
            link = row.split(":", 1)[-1].strip()
        if 'readme tag' in row.lower() and readme_tag == '':
            readme_tag = row.split(":", 1)[-1].strip()
        if link and readme_tag:
            break

    if link.count('https') > 1:
        link = link.split(']')[0]
        link = link.replace('[', "").replace(']', "").replace('(', "").replace(')', "")
    return link, readme_tag

def to_datetime(data: str) -> datetime:
    return datetime.strptime(data, '%Y-%m-%dT%H:%M:%S')

def get_last_released_date(package_name: str) -> (str, datetime):
    try:
        pypi = PyPIClient()
        latest_release, latest_stable = pypi.get_relevant_versions(package_name)
        latest_release_date = pypi.project_release(package_name, latest_release)["urls"][0]["upload_time"]
        latest_stable_date = pypi.project_release(package_name, latest_stable)["urls"][0]["upload_time"]
        if latest_release_date > latest_stable_date:
            return str(latest_release), to_datetime(latest_release_date)
        return str(latest_stable), to_datetime(latest_stable_date)
    except:
        return '', to_datetime('1970-01-01T00:00:00')



def record_release(package_name: str, issue_info: Any, file: str, version: str) -> None:
    created_at = issue_info.created_at.strftime('%Y-%m-%d')
    closed_at = issue_info.closed_at.strftime('%Y-%m-%d')
    assignee = issue_info.assignee.login
    author = issue_info.user.login
    link = issue_info.html_url
    is_stable = True if 'b' not in version else ''
    closed_issue_info = f'{package_name},{author},{assignee},{created_at},{closed_at},{link},{version},{is_stable}\n'
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

class PyPIClient:
    def __init__(self, host="https://pypi.org"):
        self._host = host
        self._http = PoolManager(
            retries=Retry(total=3, raise_on_status=True), ca_certs=os.getenv("REQUESTS_CA_BUNDLE", None)
        )

    def project(self, package_name):
        response = self._http.request(
            "get", "{host}/pypi/{project_name}/json".format(host=self._host, project_name=package_name)
        )
        return json.loads(response.data.decode("utf-8"))

    def project_release(self, package_name, version):
        response = self._http.request(
            "get",
            "{host}/pypi/{project_name}/{version}/json".format(
                host=self._host, project_name=package_name, version=version
            ),
        )
        return json.loads(response.data.decode("utf-8"))

    def get_ordered_versions(self, package_name) -> List[Version]:
        project = self.project(package_name)

        versions = [Version(package_version) for package_version in project["releases"].keys()]
        versions.sort()

        return versions

    def get_relevant_versions(self, package_name):
        """Return a tuple: (latest release, latest stable)
        If there are different, it means the latest is not a stable
        """
        versions = self.get_ordered_versions(package_name)
        pre_releases = [version for version in versions if not version.is_prerelease]
        if pre_releases:
            return versions[-1], pre_releases[-1]
        return versions[-1], versions[-1]
