import re
from typing import Any, List, Dict, Set

from github.Repository import Repository

from common import IssueProcess, Common, get_origin_link_and_tag, IssuePackage
from utils import AUTO_CLOSE_LABEL, get_last_released_date, record_release, get_python_release_pipeline, run_pipeline

# assignee dict which will be assigned to handle issues
_PYTHON_OWNER = {'BigCat20196', 'msyyc', 'Wzb123456789', 'azure-sdk'}
# labels
_CONFIGURED = 'Configured'
_AUTO_ASK_FOR_CHECK = 'auto-ask-check'
# record published issues
_FILE_OUT = 'published_issues_python.csv'


class IssueProcessPython(IssueProcess):

    def __init__(self, issue_package: IssuePackage, request_repo_dict: Dict[str, Repository],
                 assignee_candidates: Set[str], language_owner: Set[str]):
        IssueProcess.__init__(self, issue_package, request_repo_dict, assignee_candidates, language_owner)
        self.output_folder = ''
        self.is_multiapi = False
        self.pattern_resource_manager = re.compile(r'/specification/([\w-]+/)+resource-manager')

    def init_readme_link(self) -> None:
        issue_body_list = self.get_issue_body()

        # Get the origin link and readme tag in issue body
        origin_link, self.target_readme_tag = get_origin_link_and_tag(issue_body_list)

        # get readme_link
        self.get_readme_link(origin_link)

    def get_package_and_output(self) -> None:
        self.init_readme_link()
        readme_python_path = self.pattern_resource_manager.search(self.readme_link).group() + '/readme.python.md'
        contents = str(self.issue_package.rest_repo.get_contents(readme_python_path).decoded_content)
        pattern_package = re.compile(r'package-name: [\w+-.]+')
        pattern_output = re.compile(r'\$\(python-sdks-folder\)/(.*?)/azure-')
        self.package_name = pattern_package.search(contents).group().split(':')[-1].strip()
        self.output_folder = pattern_output.search(contents).group().split('/')[1]
        self.is_multiapi = ('MultiAPI' in self.issue_package.labels_name) or ('multi-api' in contents)

    def get_edit_content(self) -> None:
        self.edit_content = f'\n{self.readme_link.replace("/readme.md", "")}\n{self.package_name}'

    @property
    def readme_comparison(self) -> bool:
        # to see whether need change readme
        self.log(f'**** issue_package.labels_name: {self.issue_package.labels_name}')
        if 'package-' not in self.target_readme_tag:
            return True
        if _CONFIGURED in self.issue_package.labels_name:
            return False
        readme_path = self.pattern_resource_manager.search(self.readme_link).group() + '/readme.md'
        contents = str(self.issue_package.rest_repo.get_contents(readme_path).decoded_content)
        pattern_tag = re.compile(r'tag: package-[\w+-.]+')
        package_tags = pattern_tag.findall(contents)
        whether_same_tag = self.target_readme_tag in package_tags
        whether_change_readme = not whether_same_tag or self.is_multiapi
        return whether_change_readme

    def auto_reply(self) -> None:
        if self.issue_package.issue.comments == 0 or _CONFIGURED in self.issue_package.labels_name:
            issue_number = self.issue_package.issue.number
            if not self.readme_comparison:
                issue_link = self.issue_package.issue.html_url
                release_pipeline_url = get_python_release_pipeline(self.output_folder)
                res_run = run_pipeline(issue_link=issue_link,
                                       pipeline_url=release_pipeline_url,
                                       spec_readme=self.readme_link + '/readme.md'
                                       )
                if res_run:
                    self.log(f'{issue_number} run pipeline successfully')
                    if _CONFIGURED in self.issue_package.labels_name:
                        self.issue_package.issue.remove_from_labels(_CONFIGURED)
                else:
                    self.log(f'{issue_number} run pipeline fail')
                self.issue_package.issue.add_to_labels(_AUTO_ASK_FOR_CHECK)
            else:
                print(f'*** issue {issue_number} need config readme')
                self.log(f'issue {issue_number} need config readme')

    def auto_close(self) -> None:
        if AUTO_CLOSE_LABEL in self.issue_package.labels_name:
            return
        last_version, last_time = get_last_released_date(self.package_name)
        if last_time and last_time > self.created_time:
            comment = f'Hi @{self.owner}, pypi link: https://pypi.org/project/{self.package_name}/{last_version}/'
            self.issue_package.issue.create_comment(body=comment)
            self.issue_package.issue.edit(state='closed')
            self.issue_package.issue.add_to_labels('auto-closed')
            self.is_open = False
            self.log(f"{self.issue_package.issue.number} has been closed!")
            record_release(self.package_name, self.issue_package.issue, _FILE_OUT)

    def run(self) -> None:
        self.get_package_and_output()
        super().run()
        self.auto_reply()
        self.auto_close()


class Python(Common):
    def __init__(self, issues, language_owner):
        super(Python, self).__init__(issues, language_owner)
        self.file_out_name = 'release_python_status.md'
        self.issue_process_function = IssueProcessPython


def python_process(issues: List[Any]):
    instance = Python(issues, _PYTHON_OWNER)
    instance.run()
