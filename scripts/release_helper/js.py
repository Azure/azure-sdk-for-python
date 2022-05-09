import datetime
from common import IssueProcess, Common
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_JS_OWNER = {'qiaozha', 'lirenhe', 'MaryGao'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_JS = {'qiaozha': os.getenv('AZURESDK_BOT_TOKEN'), 'MaryGao': os.getenv('AZURESDK_BOT_TOKEN')}


class IssueProcessJs(IssueProcess):
    def auto_assign_policy(self) -> str:
        weeks = datetime.datetime.now().isocalendar()[1]
        assignees = list(self.assignee_candidates)
        assignees.sort()
        random_idx = weeks % len(assignees)
        return assignees[random_idx]


class Js(Common):
    def __init__(self, issues, assignee_token, language_owner):
        super(Js, self).__init__(issues, assignee_token, language_owner)
        self.file_out_name = 'release_js_status.md'
        self.issue_process_function = IssueProcessJs

def js_process(issues: List[Any]):
    instance = Js(issues, _ASSIGNEE_TOKEN_JS, _JS_OWNER)
    instance.run()
