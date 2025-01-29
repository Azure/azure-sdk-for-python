from common import IssueProcess, Common
from typing import Any, List

# assignee dict which will be assigned to handle issues
_GO_OWNER = {'ArcturusZhang', 'azure-sdk', 'tadelesh'}
_GO_ASSIGNEE = {'jliusan'}


class IssueProcessGo(IssueProcess):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language_name = 'go'


class Go(Common):
    def __init__(self, issues, language_owner, sdk_assignees):
        super(Go, self).__init__(issues, language_owner, sdk_assignees)
        if not self.for_test():
            self.file_out_name = 'release_go_status.md'


def go_process(issues: List[Any]) -> Go:
    return Go(issues, _GO_OWNER, _GO_ASSIGNEE)
