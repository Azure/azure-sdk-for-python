from common import IssueProcess, Common
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_PYTHON_OWNER = {'BigCat20196', 'msyyc'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_PYTHON = {
    'BigCat20196': os.getenv('PYTHON_BIGCAT_TOKEN'),
    'msyyc': os.getenv('PYTHON_MSYYC_TOKEN'),
}


class IssueProcessPython(IssueProcess):
    pass


class Python(Common):
    def __init__(self, issues, assignee_token, language_owner):
        super(Python, self).__init__(issues, assignee_token, language_owner)
        self.file_out_name = 'release_java_status.md'


def python_process(issues: List[Any]):
    instance = Python(issues, _ASSIGNEE_TOKEN_PYTHON, _PYTHON_OWNER)
    instance.run()
