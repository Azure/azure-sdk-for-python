import datetime
from common import IssueProcess, Common
from typing import Any, List

# assignee dict which will be assigned to handle issues
_JS_OWNER = {'lirenhe', 'kazrael2119', 'azure-sdk'}
_JS_ASSIGNEE = {'qiaozha', 'MaryGao'}


class IssueProcessJs(IssueProcess):
    def auto_assign_policy(self) -> str:
        weeks = datetime.datetime.now().isocalendar()[1]
        assignees = list(self.assignee_candidates)
        assignees.sort()
        random_idx = weeks % len(assignees)
        return assignees[random_idx]


class Js(Common):
    def __init__(self, issues, language_owner, sdk_assignees):
        super(Js, self).__init__(issues, language_owner, sdk_assignees)
        self.file_out_name = 'release_js_status.md'
        self.issue_process_function = IssueProcessJs


def js_process(issues: List[Any]) -> Js:
    return Js(issues, _JS_OWNER, _JS_ASSIGNEE)
