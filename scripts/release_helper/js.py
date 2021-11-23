from common import IssueProcess, Common
from typing import Any, List
import os

# 'github assignee': 'token'
_ASSIGNEE_TOKEN = {'lirenhe': os.getenv('JS_QIAOQIAO_TOKEN')}


class IssueProcessJs(IssueProcess):
    pass


class Js(Common):
    pass


def js_process(issues: List[Any]):
    instance = Js(issues)
    instance.run()
