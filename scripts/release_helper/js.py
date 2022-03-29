import datetime
from common import IssueProcess, Common
from typing import Any, List, Dict
import os

# assignee dict which will be assigned to handle issues
_JS_OWNER = {'qiaozha', 'lirenhe'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_JS = {'qiaozha': os.getenv('AZURESDK_BOT_TOKEN'), 'dw511214992': os.getenv('AZURESDK_BOT_TOKEN')}

# Set the start time to 2022-02-28
SATRAT_DAY = datetime.datetime(2022, 2, 28).date()

class IssueProcessJs(IssueProcess):
    pass


class Js(Common):
    def __init__(self, issues, assignee_token, language_owner):
        super(Js, self).__init__(issues, self.assign_policy(assignee_token), language_owner)
        self.file_out_name = 'release_js_status.md'

    @staticmethod
    def assign_policy(assignee_token):
        assignees = list(assignee_token.keys())
        today = datetime.datetime.today().date()
        apart_days = (today - SATRAT_DAY).days
        index = (apart_days // 7) % len(assignees)
        return {assignees[index]: _ASSIGNEE_TOKEN_JS[assignees[index]]}


def js_process(issues: List[Any]):
    instance = Js(issues, _ASSIGNEE_TOKEN_JS, _JS_OWNER)
    instance.run()
