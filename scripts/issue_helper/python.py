from typing import List
from datetime import datetime

from github.Issue import Issue

from common import Common

_PYTHON_OWNER = {'msyyc', 'BigCat20196', 'Wzb123456789', 'kazrael2119'}
_PYTHON_REPO = 'Azure/azure-sdk-for-python'
_FILE_OUT_NAME_PYTHON = 'sdk_issue_python.md'

class Python(Common):

    def collect_open_issues(self) -> List[Issue]:
        open_issues = super().collect_open_issues()
        # Skip issue created by owners
        filtered_issues = [i for i in open_issues if i.user.login not in self.language_owner]
        return filtered_issues

    def judge_status(self, issue: Issue) -> str:
        bot_advice = super().judge_status(issue)
        # Prompt to add `issue-addressed` tag if customer has not replied > 7 days
        issue_labels = [label.name for label in issue.labels]
        if not bot_advice and 'issue-addressed' not in issue_labels and 'needs-author-feedback' not in issue_labels:
            if (datetime.today() - list(issue.get_comments())[-1].updated_at).days > 7:
                return 'no reply > 7'
        return bot_advice


def python_process() -> None:
    instance = Python(_PYTHON_OWNER, _PYTHON_REPO, _FILE_OUT_NAME_PYTHON)
    instance.run()
