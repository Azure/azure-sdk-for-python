from common import IssueProcess, Common
from utils import AUTO_PARSE_LABEL, get_origin_link_and_tag
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_JAVA_OWNER = {'weidongxu-microsoft', 'haolingdong-msft', 'XiaofeiCao', 'azure-sdk'}


class IssueProcessJava(IssueProcess):
    pass

class Java(Common):
    def __init__(self, issues, language_owner):
        super(Java, self).__init__(issues, language_owner)
        self.file_out_name = 'release_java_status.md'



def java_process(issues: List[Any]):
    instance = Java(issues, _JAVA_OWNER)
    instance.run()
