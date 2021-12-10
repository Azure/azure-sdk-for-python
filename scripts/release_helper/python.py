from common import IssueProcess, Common
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_PYTHON_OWNER = {'RAY-316', 'BigCat20196', 'msyyc'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_PYTHON = {
    'RAY-316': os.getenv('PYTHON_ZED_TOKEN'),
    'BigCat20196': os.getenv('PYTHON_BIGCAT_TOKEN'),
}


class IssueProcessPython(IssueProcess):
    pass


class Python(Common):
    pass


def python_process(issues: List[Any]):
    instance = Python(issues, _ASSIGNEE_TOKEN_PYTHON, _PYTHON_OWNER)
    instance.run()
