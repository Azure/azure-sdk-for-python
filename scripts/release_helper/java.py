from common import IssueProcess, Common
from typing import Any, List

# assignee dict which will be assigned to handle issues
_JAVA_OWNER = {'azure-sdk', 'haolingdong-msft'}
_JAVA_ASSIGNEE = {'weidongxu-microsoft', 'XiaofeiCao', 'v-hongli1'}


class IssueProcessJava(IssueProcess):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language_name = 'java'


class Java(Common):
    def __init__(self, issues, language_owner, sdk_assignees):
        super(Java, self).__init__(issues, language_owner, sdk_assignees)
        if not self.for_test():
            self.file_out_name = 'release_java_status.md'


def java_process(issues: List[Any]) -> Java:
    return Java(issues, _JAVA_OWNER, _JAVA_ASSIGNEE)
