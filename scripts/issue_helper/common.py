from datetime import date
from typing import Set, List, Dict, Any
import os
import logging
from github import Github
from github.Issue import Issue
from subprocess import check_call

_LOG = logging.getLogger(__name__)

_LANGUAGE_OWNER = {'msyyc'}
_LANGUAGE_REPO = 'Azure/azure-sdk-for-python'
_FILE_OUT_NAME = 'common.md'


class Common:
    """ The class defines some function for all languages to reference
    language_owner = {}  # language owner who may handle issue
    repo_name = ''  # base repo. For example: Azure/azure-sdk-for-python
    file_out_name = ''  # report name. For example: sdk_issue_status_python.md
    issue_html = ''  # issue url. For example: https://github.com/Azure/azure-sdk-for-python/issues

    """

    def __init__(self, language_owner: Set[str], repo_name: str, file_out_name: str):
        self.language_owner = language_owner
        self.repo_name = repo_name
        self.file_out_name = file_out_name
        self.issue_html = f'https://github.com/{repo_name}/issues'
        self.bot_assignees = {'msftbot[bot]'}

    @staticmethod
    def push_md_to_storage():
        cmd_list = ['git add .', 'git commit -m \"update excel\"', 'git push -f origin HEAD']
        [check_call(cmd, shell=True) for cmd in cmd_list]

    def collect_open_issues(self) -> List[Issue]:
        hub = Github(os.getenv('TOKEN'))
        repo = hub.get_repo(self.repo_name)
        mgmt_label = repo.get_label('Mgmt')
        open_issues = repo.get_issues(state='open', labels=[mgmt_label])
        return [issue for issue in open_issues if not issue.pull_request]

    def judge_status(self, issue: Issue) -> str:
        if issue.user.login in self.language_owner:
            return ''
        latest_comments = ''
        comments = [(comment.updated_at.timestamp(), comment.user.login) for comment in issue.get_comments()
                    if comment.user.login not in self.bot_assignees]
        comments.sort()
        if comments:
            latest_comments = comments[-1][1]
        if issue.comments == 0:
            return 'new issue'
        elif latest_comments not in self.language_owner:
            return 'new comment'
        else:
            return ''

    def extract_info(self, open_issues: List[Issue]) -> List[Dict[str, Any]]:
        issues_info = []
        _LOG.info(f'collect {len(open_issues)} open issues in {self.issue_html}')
        idx = 1
        for issue in open_issues:
            assignees = {assignee.login for assignee in issue.assignees}
            if assignees.intersection(self.language_owner):
                issue_info = {
                    'idx': idx,
                    'number': issue.number,
                    'html': f'{self.issue_html}/{issue.number}',
                    'title': issue.title,
                    'labels': [label.name for label in issue.labels],
                    'assignees': assignees,
                    'created_date': str(date.fromtimestamp(issue.created_at.timestamp()).strftime('%Y-%m-%d')),
                    'status': self.judge_status(issue)
                }
                issues_info.append(issue_info)
                idx = idx + 1
        _LOG.info(f'collect {len(issues_info)} open issues assigned to {str(self.language_owner)}')
        return issues_info

    @staticmethod
    def output_line(issue_info: Dict[str, Any]) -> str:
        return '|{No}|[#{number}]({issue_html})|{title}|{labels}|{assignees}|{bot_advice}|{created_date}|\n'.format(
            No=issue_info['idx'],
            number=issue_info['number'],
            issue_html=issue_info['html'],
            title=issue_info['title'],
            labels=', '.join(issue_info['labels']),
            assignees=', '.join(issue_info['assignees']),
            bot_advice=issue_info['status'],
            created_date=issue_info['created_date'],
        )

    def report(self, issues_info: List[Dict[str, Any]]) -> None:
        with open(self.file_out_name, 'w') as file_out:
            file_out.write(
                '| No. | issue | title | labels | assignees | bot advice | created date |\n')
            file_out.write('| ------ | ------ | ------ | ------ | ------ | ------ | :-----: |\n')
            file_out.writelines([Common.output_line(issue_info) for issue_info in issues_info])

    def run(self):
        open_issues = self.collect_open_issues()
        issues_info = self.extract_info(open_issues)
        self.report(issues_info)


def common_process():
    instance = Common(_LANGUAGE_OWNER, _LANGUAGE_REPO, _FILE_OUT_NAME)
    instance.run()
