import datetime
from common import IssueProcess, Common
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_JS_OWNER = {'qiaozha', 'lirenhe', 'MaryGao', 'azure-sdk'}


class IssueProcessJs(IssueProcess):
    def auto_assign_policy(self) -> str:
        weeks = datetime.datetime.now().isocalendar()[1]
        assignees = list(self.assignee_candidates)
        assignees.sort()
        random_idx = weeks % len(assignees)
        return assignees[random_idx]


class Js(Common):
    def __init__(self, issues, language_owner):
        super(Js, self).__init__(issues, language_owner)
        self.file_out_name = 'release_js_status.md'
        self.issue_process_function = IssueProcessJs

def js_process(issues: List[Any]):
    instance = Js(issues, _JS_OWNER)
    instance.run()
