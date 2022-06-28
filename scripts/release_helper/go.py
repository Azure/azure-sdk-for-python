from common import IssueProcess, Common
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_GO_OWNER = {'ArcturusZhang', 'Alancere', 'azure-sdk'}
_SKIPPED_ASSIGNEES = {'ArcturusZhang', 'azure-sdk'}


class IssueProcessGo(IssueProcess):
    pass


class Go(Common):
    def __init__(self, issues, language_owner, skipped_assignees):
        super(Go, self).__init__(issues, language_owner, skipped_assignees)
        self.file_out_name = 'release_go_status.md'


def go_process(issues: List[Any]):
    instance = Go(issues, _GO_OWNER, _SKIPPED_ASSIGNEES)
    instance.run()
