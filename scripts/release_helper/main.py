from github import Github
from utils import REQUEST_REPO, REST_REPO, IssuePackage

from python import python_process
from go import go_process
from java import java_process
from js import js_process
from common import common_process, Common, IssueProcess
import subprocess as sp


import os
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s')
_LOG = logging.getLogger(__name__)

_HOLD_ON = "HoldOn"

_CONVERT = {
    'python': 'Python',
    'java': 'Java',
    'go': 'Go',
    'js': 'JS',
    't': 'Test'
}
_LANGUAGES = {
    'Test': common_process,
    'Python': python_process,
    'Java': java_process,
    'Go': go_process,
    'JS': js_process
}


def collect_open_issues() -> List[IssuePackage]:
    hub = Github(os.getenv('AZURESDK_BOT_TOKEN'))
    request_repo = hub.get_repo(REQUEST_REPO)
    mgmt_label = request_repo.get_label('ManagementPlane')
    open_issues = request_repo.get_issues(state='open', labels=[mgmt_label])
    rest_repo = hub.get_repo(REST_REPO)
    issues = [IssuePackage(issue, rest_repo) for issue in open_issues]
    _LOG.info(f'collect {len(issues)} open issues')

    return issues


def select_language_issues(issues: List[IssuePackage], language: str) -> List[IssuePackage]:
    return [issue for issue in issues if language in issue.labels_name]


def output(result: Dict[str, Dict[str, IssueProcess]]):
    with open("release_issues_summary.md", 'w') as file_out:
        file_out.write('| id | title | Python | Go | Java | Js | created date | target date | status |\n')
        file_out.write('| ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ | :-----: |\n')
        idx = 1
        for title, language_issue in result.items():
            created_date = ""
            target_date = ""
            line = f"| {idx} | {title} "
            status = ""
            enable_out = False
            for language in ["Python", "Go", "Java", "JS"]:
                issue_processor = language_issue.get(language)
                if issue_processor:
                    created_date = issue_processor.created_date_format if not created_date else created_date
                    target_date = issue_processor.target_date_format if not target_date else target_date
                    status = f"{language}/{status}" if _HOLD_ON in issue_processor.issue_package.labels_name else status
                    html_url = issue_processor.issue_package.issue.html_url
                    number = html_url.split("/")[-1]
                    line = f"{line} | [#{number}]({html_url}) "
                    enable_out = True
                else:
                    line = f"{line} | "
            if enable_out:
                idx = idx + 1
                status = f"Hold on by {status}" if status else status
                line = f"{line} | {created_date} | {target_date} | {status} |\n"
                file_out.write(line)


def main():
    issues = collect_open_issues()
    language = os.getenv('LANGUAGE')
    languages = {_CONVERT[language]: _LANGUAGES[_CONVERT[language]]} if language in _CONVERT else _LANGUAGES
    result = dict()
    for language in languages:
        try:
            language_issues = select_language_issues(issues, language)
            language_processor = languages[language](language_issues)
            language_processor.run()
            for item in language_processor.result:
                if item.issue_title not in result:
                    result[item.issue_title] = {language: item}
                result[item.issue_title].update({language: item})
        except Exception as e:
            _LOG.error(f'Error happened during handling {language} issue: {e}')

    # output
    output(result)
    cmd_list = ['git add -u', 'git commit -m \"update excel\"', 'git push -f origin HEAD']
    [sp.call(cmd, shell=True) for cmd in cmd_list]


if __name__ == '__main__':
    main()
