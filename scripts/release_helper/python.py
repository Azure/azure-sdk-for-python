import re

from common import IssueProcess, Common
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_PYTHON_OWNER = {'BigCat20196', 'msyyc', 'azure-sdk'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_PYTHON = {
    'BigCat20196': os.getenv('PYTHON_BIGCAT_TOKEN'),
    'msyyc': os.getenv('PYTHON_MSYYC_TOKEN'),
}


class IssueProcessPython(IssueProcess):

    def get_package_name(self) -> None:
        pattern_resource_manager = re.compile(r'/specification/([\w-]+/)+resource-manager')
        readme_python_path = pattern_resource_manager.search(self.readme_link).group() + '/readme.python.md'
        contents = str(self.issue_package.rest_repo.get_contents(readme_python_path).decoded_content)
        pattern_package = re.compile(r'package-name: [\w+-.]+')
        self.package_name = pattern_package.search(contents).group().split(':')[-1].strip()
        print(f'*** package_name: {self.package_name}')

    def get_edit_content(self) -> None:
        self.get_package_name()
        self.edit_content = f'\n{self.readme_link.replace("/readme.md", "")}\n{self.package_name}'

class Python(Common):
    def __init__(self, issues, assignee_token, language_owner):
        super(Python, self).__init__(issues, assignee_token, language_owner)
        self.file_out_name = 'release_python_status.md'
        self.issue_process_function = IssueProcessPython


def python_process(issues: List[Any]):
    instance = Python(issues, _ASSIGNEE_TOKEN_PYTHON, _PYTHON_OWNER)
    instance.run()
