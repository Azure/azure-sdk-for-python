import time
import os
import re
from datetime import date, datetime
import subprocess as sp
import logging

from github import Github

_NULL = ' '
_BASE_ASSIGNEE = 'msyyc'
_BASE_LABEL = 'Mgmt'
_EPIC = 'epic'
_FILE_OUT_PYTHON = 'sdk_python_status.md'


def my_print(cmd):
    print('==' + cmd + ' ==\n')


def print_check(cmd):
    my_print(cmd)
    sp.check_call(cmd, shell=True)


def output_python_md(issue_status):
    with open(_FILE_OUT_PYTHON, 'w') as file_out:
        file_out.write(
            '| issue | author | package | assignee | bot advice | created date of issue | target release date | date from target |\n')
        file_out.write('| ------ | ------ | ------ | ------ | ------ | ------ | ------ | :-----: |\n')
        file_out.writelines([item.output_python() for item in sorted(issue_status)])


class IssueStatus:
    link = _NULL
    title = ''
    create_date = 0.0
    delay_from_create_date = 0
    latest_update = 0.0
    delay_from_latest_update = 0
    status = 'confirm'
    bot_advice = _NULL
    comment_num = 0
    author_latest_comment = _NULL
    whether_author_comment = True
    issue_object = _NULL
    labels = _NULL
    assignee = _NULL

    def output_python(self):
        labels = self.labels
        create_date = str(date.fromtimestamp(self.create_date).strftime('%m-%d'))
        return '| [#{}]({}) | {} | {} | {} | {} | {}  |\n'.format(self.link.split('/')[-1], self.link,
                                                                  self.title, labels, self.assignee, self.bot_advice,
                                                                  create_date,
                                                                  )


def main():
    g = Github(os.getenv('TOKEN'))
    sdk_repo = g.get_repo('Azure/azure-sdk-for-python')
    open_issue = sdk_repo.get_issues(state='open', assignee=_BASE_ASSIGNEE, labels=[_BASE_LABEL])
    issue_status = []
    start_time = time.time()
    for item in open_issue:
        if not item.number:
            continue
        issue = IssueStatus()
        issue.link = f'https://github.com/Azure/azure-sdk-for-python/issues/{item.number}'
        issue.title = item.title
        issue.labels = [label.name for label in item.labels if label.name != _BASE_LABEL or label.name != _EPIC]
        issue.assignee = [assignee.login for assignee in item.assignees if assignee.login != _BASE_ASSIGNEE]
        issue.create_date = item.created_at.timestamp()
        issue.bot_advice = 'new issue'
        issue_status.append(issue)

    my_print('Have cost {} seconds'.format(int(time.time() - start_time)))

    # output result
    output_python_md(issue_status)

    # commit to github
    print_check('git add .')
    print_check('git commit -m \"update excel\"')
    print_check('git push -f origin HEAD')


if __name__ == '__main__':
    main()
