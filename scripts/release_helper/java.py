from common import IssueProcess, Common
from typing import Any, List


class IssueProcessJava(IssueProcess):
    pass


class Java(Common):
    pass


def java_process(issues: List[Any]):
    instance = Java(issues)
    instance.run()