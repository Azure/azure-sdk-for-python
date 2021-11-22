from common import IssueProcess, Common
from typing import Any, List


class IssueProcessGo(IssueProcess):
    pass


class Go(Common):
    pass


def go_process(issues: List[Any]):
    instance = Go(issues)
    instance.run()