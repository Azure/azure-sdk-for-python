from common import IssueProcess, Common
from typing import Any, List


class IssueProcessPython(IssueProcess):
    pass


class Python(Common):
    pass


def python_process(issues: List[Any]):
    instance = Python(issues)
    instance.run()
