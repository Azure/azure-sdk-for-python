from common import IssueProcess, Common
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_ASSIGNEE_CANDIDATES_JAVA = {'weidongxu-microsoft'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_JAVA = {'weidongxu-microsoft': os.getenv('JAVA_WEIDONGXU_TOKEN')}


class IssueProcessJava(IssueProcess):
    pass


class Java(Common):
    pass


def java_process(issues: List[Any]):
    instance = Java(issues, _ASSIGNEE_TOKEN_JAVA, _ASSIGNEE_CANDIDATES_JAVA)
    instance.run()
