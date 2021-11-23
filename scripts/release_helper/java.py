from common import IssueProcess, Common
from typing import Any, List
import os

# 'github assignee': 'token'
_ASSIGNEE_TOKEN = {'weidongxu-microsoft': os.getenv('JAVA_WEIDONGXU_TOKEN')}


class IssueProcessJava(IssueProcess):
    pass


class Java(Common):
    pass


def java_process(issues: List[Any]):
    instance = Java(issues)
    instance.run()
