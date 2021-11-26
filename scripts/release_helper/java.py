from common import IssueProcess, Common
from utils import AUTO_PARSE_LABEL, get_origin_link_and_tag
from typing import Any, List
import os

# assignee dict which will be assigned to handle issues
_JAVA_OWNER = {'weidongxu-microsoft', 'haolingdong-msft', 'XiaofeiCao'}

# 'github assignee': 'token'
_ASSIGNEE_TOKEN_JAVA = {
    'weidongxu-microsoft': os.getenv('JAVA_WEIDONGXU_TOKEN'),
    'haolingdong-msft': os.getenv('JAVA_WEIDONGXU_TOKEN'),
    'XiaofeiCao': os.getenv('JAVA_WEIDONGXU_TOKEN'),
}


class IssueProcessJava(IssueProcess):

    def auto_parse(self) -> None:
        if AUTO_PARSE_LABEL in self.issue_package.labels_name:
            return

        self.add_label(AUTO_PARSE_LABEL)
        issue_body_list = self.get_issue_body()

        # Get the origin link and readme tag in issue body
        origin_link, self.target_readme_tag = get_origin_link_and_tag(issue_body_list)

        # get readme_link
        self.get_readme_link(origin_link)

        self.edit_issue_body()


class Java(Common):
    pass


def java_process(issues: List[Any]):
    instance = Java(issues, _ASSIGNEE_TOKEN_JAVA, _JAVA_OWNER)
    instance.run()
