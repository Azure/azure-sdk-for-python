from common import IssueProcess, Common
from typing import Any, List
import os

# 'github assignee': 'token'
_ASSIGNEE_TOKEN = {
    'msyyc': os.getenv('PYTHON_MSYYC_TOKEN'),
    'RAY-316': os.getenv('PYTHON_ZED_TOKEN'),
    'BigCat20196': os.getenv('PYTHON_BIGCAT_TOKEN'),
}


class IssueProcessPython(IssueProcess):
    pass


class Python(Common):
    pass


def python_process(issues: List[Any]):
    instance = Python(issues)
    instance.run()
