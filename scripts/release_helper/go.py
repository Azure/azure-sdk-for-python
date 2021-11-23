from common import IssueProcess, Common
from typing import Any, List


# 'github assignee': 'token'
_ASSIGNEE_TOKEN = {'ArcturusZhang': os.getenv('GO_DAPENGZHANG_TOKEN')}

class IssueProcessGo(IssueProcess):
    pass


class Go(Common):
    pass


def go_process(issues: List[Any]):
    instance = Go(issues)
    instance.run()