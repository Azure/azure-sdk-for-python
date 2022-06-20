import os
import re
from typing import Any, List

from common import IssueProcess, Common, get_origin_link_and_tag
from utils import AUTO_CLOSE_LABEL, get_last_released_date, record_release

# assignee dict which will be assigned to handle issues
_PYTHON_OWNER = {'BigCat20196', 'msyyc', 'azure-sdk'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_PYTHON = os.getenv('AZURESDK_BOT_TOKEN')

# record published issues
_FILE_OUT = 'published_issues_python.csv'


class IssueProcessPython(IssueProcess):

    def init_readme_link(self) -> None:
        issue_body_list = self.get_issue_body()

        # Get the origin link and readme tag in issue body
        origin_link, self.target_readme_tag = get_origin_link_and_tag(issue_body_list)

        # get readme_link
        self.get_readme_link(origin_link)

    def get_package_name(self) -> None:
        self.init_readme_link()
        pattern_resource_manager = re.compile(r'/specification/([\w-]+/)+resource-manager')
        readme_python_path = pattern_resource_manager.search(self.readme_link).group() + '/readme.python.md'
        contents = str(self.issue_package.rest_repo.get_contents(readme_python_path).decoded_content)
        pattern_package = re.compile(r'package-name: [\w+-.]+')
        self.package_name = pattern_package.search(contents).group().split(':')[-1].strip()

    def get_edit_content(self) -> None:
        self.edit_content = f'\n{self.readme_link.replace("/readme.md", "")}\n{self.package_name}'

    def auto_close(self) -> None:
        if AUTO_CLOSE_LABEL in self.issue_package.labels_name:
            return
        last_version, last_time = get_last_released_date(self.package_name)
        if last_time and last_time > self.created_time:
            comment = f'Hi @{self.owner}, pypi link: https://pypi.org/project/{self.package_name}/{last_version}/'
            self.issue_package.issue.create_comment(body=comment)
            self.issue_package.issue.edit(state='closed')
            self.issue_package.issue.add_to_labels('auto-closed')
            self.is_open = False
            self.log(f"{self.issue_package.issue.number} has been closed!")
            record_release(self.package_name, self.issue_package.issue, _FILE_OUT)

    def run(self) -> None:
        self.get_package_name()
        super().run()
        self.auto_close()

class Python(Common):
    def __init__(self, issues, assignee_token, language_owner):
        super(Python, self).__init__(issues, assignee_token, language_owner)
        self.file_out_name = 'release_python_status.md'
        self.issue_process_function = IssueProcessPython


def python_process(issues: List[Any]):
    instance = Python(issues, _ASSIGNEE_TOKEN_PYTHON, _PYTHON_OWNER)
    instance.run()
