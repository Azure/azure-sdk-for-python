from common import IssueProcess, Common
from typing import Any, List


class IssueProcessJs(IssueProcess):
    pass


class Js(Common):
    pass


def js_process(issues: List[Any]):
    instance = Js(issues)
    instance.run()