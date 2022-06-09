from github import Github
from utils import REQUEST_REPO, REST_REPO, IssuePackage

from python import python_process
from go import go_process
from java import java_process
from js import js_process
from common import common_process, Common
import subprocess as sp


import os
from typing import List
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s')
_LOG = logging.getLogger(__name__)

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
    hub = Github(os.getenv('TOKEN'))
    request_repo = hub.get_repo(REQUEST_REPO)
    mgmt_label = request_repo.get_label('ManagementPlane')
    open_issues = request_repo.get_issues(state='open', labels=[mgmt_label])
    rest_repo = hub.get_repo(REST_REPO)
    issues = [IssuePackage(issue, rest_repo) for issue in open_issues]
    _LOG.info(f'collect {len(issues)} open issues')

    return issues


def select_language_issues(issues: List[IssuePackage], language: str) -> List[IssuePackage]:
    return [issue for issue in issues if language in issue.labels_name]


def main():
    issues = collect_open_issues()
    language = os.getenv('LANGUAGE')
    languages = {_CONVERT[language]: _LANGUAGES[_CONVERT[language]]} if language in _CONVERT else _LANGUAGES
    for language in languages:
        try:
            language_issues = select_language_issues(issues, language)
            languages[language](language_issues)
        except Exception as e:
            _LOG.error(f'Error happened during handling {language} issue: {e}')

    # output
    cmd_list = ['git add -u', 'git commit -m \"update excel\"', 'git push -f origin HEAD']
    [sp.call(cmd, shell=True) for cmd in cmd_list]


if __name__ == '__main__':
    main()
