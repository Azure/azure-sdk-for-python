from common import IssueProcess, Common
from utils import AUTO_PARSE_LABEL, get_origin_link_and_tag
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_JAVA_OWNER = {'azure-sdk'}
_JS_ASSIGNEE = {'weidongxu-microsoft', 'haolingdong-msft', 'XiaofeiCao'}

class IssueProcessJava(IssueProcess):
    pass

class Java(Common):
    def __init__(self, issues, language_owner, sdk_assignees):
        super(Java, self).__init__(issues, language_owner, sdk_assignees)
        self.file_out_name = 'release_java_status.md'



def java_process(issues: List[Any]):
    instance = Java(issues, _JAVA_OWNER, _JS_ASSIGNEE)
    instance.run()
