from common import IssueProcess, Common
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_GO_OWNER = {'ArcturusZhang', 'Alancere'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_GO = {'Alancere': os.getenv('AZURESDK_BOT_TOKEN')}


class IssueProcessGo(IssueProcess):
    pass


class Go(Common):
    def __init__(self, issues, assignee_token, language_owner):
        super(Go, self).__init__(issues, assignee_token, language_owner)
        self.file_out_name = 'release_go_status.md'


def go_process(issues: List[Any]):
    instance = Go(issues, _ASSIGNEE_TOKEN_GO, _GO_OWNER)
    instance.run()
