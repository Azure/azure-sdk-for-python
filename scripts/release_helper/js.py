from common import IssueProcess, Common
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_JS_OWNER = {'qiaozha', 'lirenhe'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_JS = {'qiaozha': os.getenv('AZURESDK_BOT_TOKEN')}


class IssueProcessJs(IssueProcess):
    pass


class Js(Common):
    def __init__(self, issues, assignee_token, language_owner):
        super(Js, self).__init__(issues, assignee_token, language_owner)
        self.file_out_name = 'release_js_status.md'


def js_process(issues: List[Any]):
    instance = Js(issues, _ASSIGNEE_TOKEN_JS, _JS_OWNER)
    instance.run()
