import os
import re
from typing import Any, List

from common import IssueProcess, Common
from utils import AUTO_CLOSE_LABEL, get_last_released_date, record_release

# assignee dict which will be assigned to handle issues
_PYTHON_OWNER = {'BigCat20196', 'msyyc', 'azure-sdk'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_PYTHON = {
    'BigCat20196': os.getenv('PYTHON_BIGCAT_TOKEN'),
    'msyyc': os.getenv('PYTHON_MSYYC_TOKEN'),
}

# record published issues
_FILE_OUT = 'published_issues_python.csv'


class IssueProcessPython(IssueProcess):

    def get_package_name(self) -> None:
        pattern_resource_manager = re.compile(r'/specification/([\w-]+/)+resource-manager')
        readme_python_path = pattern_resource_manager.search(self.readme_link).group() + '/readme.python.md'
        contents = str(self.issue_package.rest_repo.get_contents(readme_python_path).decoded_content)
        pattern_package = re.compile(r'package-name: [\w+-.]+')
        self.package_name = pattern_package.search(contents).group().split(':')[-1].strip()
        print(f'*** package_name: {self.package_name}')

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
            self.log("has been closed!")
            record_release(self.package_name, self.issue_package.issue, _FILE_OUT)

    def run(self) -> None:
        # common part(don't change the order)
        self.auto_assign()  # necessary flow
        self.auto_parse()  # necessary flow
        self.get_package_name()
        self.get_target_date()
        self.auto_bot_advice()  # make sure this is the last step
        self.auto_close()

    def __repr__(self):
        return self.issue_package.issue.number, self.package_name


class Python(Common):
    def __init__(self, issues, assignee_token, language_owner):
        super(Python, self).__init__(issues, assignee_token, language_owner)
        self.file_out_name = 'release_python_status.md'
        self.issue_process_function = IssueProcessPython


def python_process(issues: List[Any]):
    instance = Python(issues, _ASSIGNEE_TOKEN_PYTHON, _PYTHON_OWNER)
    instance.run()
