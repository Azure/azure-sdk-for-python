from common import IssueProcess, Common
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_ASSIGNEE_CANDIDATES_JS = {'lirenhe'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_JS = {'lirenhe': os.getenv('JS_QIAOQIAO_TOKEN')}


class IssueProcessJs(IssueProcess):
    pass


class Js(Common):
    pass


def js_process(issues: List[Any]):
    instance = Js(issues, _ASSIGNEE_TOKEN_JS, _ASSIGNEE_CANDIDATES_JS)
    instance.run()
