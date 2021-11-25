from common import IssueProcess, Common
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_GO_OWNER = {'ArcturusZhang'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_GO = {'ArcturusZhang': os.getenv('PYTHON_ZED_TOKEN')}


class IssueProcessGo(IssueProcess):
    pass


class Go(Common):
    pass


def go_process(issues: List[Any]):
    instance = Go(issues, _ASSIGNEE_TOKEN_GO, _GO_OWNER)
    instance.run()
