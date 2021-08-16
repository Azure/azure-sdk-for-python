import time
import os
import re
from github import Github
from datetime import date, datetime
import subprocess as sp
from azure.storage.blob import BlobClient

_NULL = ' '
_FILE_OUT = 'release_issue_status.csv'
_PYTHON_SDK_ADMINISTRATORS = {'msyyc', 'RAY-316', 'BigCat20196'}


def my_print(cmd):
    print('==' + cmd + ' ==\n')


def print_check(cmd):
    my_print(cmd)
    sp.check_call(cmd, shell=True)


class IssueStatus:
    link = _NULL
    author = _NULL
    package = _NULL
    create_date = 0.0
    delay_from_create_date = 0
    latest_update = 0.0
    delay_from_latest_update = 0
    status = 'confirm'
    bot_advice = _NULL
    comment_num = 0
    language = _NULL
    author_latest_comment = _NULL
    whether_author_comment = True
    issue_object = _NULL
    labels = _NULL

    def output(self):
        return '{},{},{},{},{},{},{},{},{},{}\n'.format(self.language, self.link, self.author,
                                                        self.package,
                                                        str(date.fromtimestamp(self.create_date)),
                                                        self.delay_from_create_date,
                                                        str(date.fromtimestamp(self.latest_update)),
                                                        self.delay_from_latest_update,
                                                        self.status, self.bot_advice)


def _extract(str_list, key_word):
    for item in str_list:
        if re.fullmatch(key_word, item):
            return item.strip()
    return _NULL


def _time_format_transform(time_gmt):
    return str(datetime.strptime(time_gmt, '%a, %d %b %Y %H:%M:%S GMT'))


def _judge_status(labels):
    for label in labels:
        if label.name == 'release':
            return 'release'
    return 'confirm'


def _extract_language(labels):
    language = {'Python', 'JS', 'Go', 'Java', 'Ruby'}
    label_set = {label.name for label in labels}
    intersect = language.intersection(label_set)
    return _NULL if not intersect else intersect.pop()


def _key_select(item):
    return item.package


def _extract_author_latest_comment(comments):
    q = [(comment.updated_at.timestamp(), comment.user.login) for comment in comments]
    q.sort()

    return _NULL if not q else q[-1][1]


def _whether_author_comment(comments):
    q = set(comment.user.login for comment in comments)
    diff = q.difference(_PYTHON_SDK_ADMINISTRATORS)

    return  len(diff) > 0

def _latest_comment_time(comments, delay_from_create_date):
    q = [(comment.updated_at.timestamp(), comment.user.login)
         for comment in comments if comment.user.login not in _PYTHON_SDK_ADMINISTRATORS]
    q.sort()

    return delay_from_create_date if not q else int((time.time() - q[-1][0]) / 3600 / 24)

def main():
    # get latest issue status
    g = Github(os.getenv('TOKEN'))  # please fill user_token
    repo = g.get_repo('Azure/sdk-release-request')
    label1 = repo.get_label('ManagementPlane')
    open_issues = repo.get_issues(state='open', labels=[label1])
    issue_status = []
    duplicated_issue = dict()
    start_time = time.time()
    for item in open_issues:
        if not item.number:
            continue
        issue = IssueStatus()
        issue.link = f'https://github.com/Azure/sdk-release-request/issues/{item.number}'
        issue.author = item.user.login
        issue.package = _extract(item.body.split('\n'), 'azure-.*')
        issue.create_date = item.created_at.timestamp()
        issue.delay_from_create_date = int((time.time() - item.created_at.timestamp()) / 3600 / 24)
        issue.latest_update = item.updated_at.timestamp()
        issue.delay_from_latest_update = int((time.time() - item.updated_at.timestamp()) / 3600 / 24)
        issue.status = _judge_status(item.labels)
        issue.comment_num = item.comments
        issue.language = _extract_language(item.labels)
        issue.author_latest_comment = _extract_author_latest_comment(item.get_comments())
        issue.whether_author_comment = _whether_author_comment(item.get_comments())
        issue.issue_object = item
        issue.labels = [label.name for label in item.labels]
        issue.days_from_latest_commit = _latest_comment_time(item.get_comments(), issue.delay_from_create_date)

        issue_status.append(issue)
        key = (issue.language, issue.package)
        duplicated_issue[key] = duplicated_issue.get(key, 0) + 1

    my_print('Have cost {} seconds'.format(int(time.time() - start_time)))

    # rule1: if status is 'release', need to release asap
    # rule2: if latest comment is from author, need response asap
    # rule3: if comment num is 0, it is new issue, better to deal with it asap
    # rule4: if delay from latest update is over 7 days, better to deal with it soon.
    # rule5: if delay from created date is over 30 days and owner never reply, close it.
    # rule6: if delay from created date is over 15 days and owner never reply, remind owner to handle it.
    for item in issue_status:
        if item.status == 'release':
            item.bot_advice = 'better to release asap.'
        elif item.author == item.author_latest_comment:
            item.bot_advice = 'new comment for author.'
        elif item.comment_num == 0:
            item.bot_advice = 'new issue and better to confirm quickly.'
        elif item.delay_from_latest_update >= 7:
            item.bot_advice = 'delay for a long time and better to handle now.'
  
        if item.delay_from_create_date >= 30 and item.language == 'Python' and '30days attention' not in item.labels:
            item.labels.append('30days attention')
            item.issue_object.set_labels(*item.labels)
            item.issue_object.create_comment(f'hi @{item.author}, the issue is closed since there is no reply for a long time. Please reopen it if necessary or create new one.')
            item.issue_object.edit(state='close')
        elif item.delay_from_create_date >= 15 and item.language == 'Python' and '15days attention' not in item.labels:
            item.issue_object.create_comment(f'hi @{item.author}, this release-request has been delayed more than 15 days,'
                                             ' please deal with it ASAP. We will close the issue if there is still no response after 15 days!')
            item.labels.append('15days attention')
            item.issue_object.set_labels(*item.labels)
            
            
        # judge whether there is duplicated issue for same package
        if item.package != _NULL and duplicated_issue.get((item.language, item.package)) > 1:
            item.bot_advice = f'Warning:There is duplicated issue for {item.package}. ' + item.bot_advice

    # output result
    with open(_FILE_OUT, 'w') as file_out:
        file_out.write('language,issue,author,package,created date,delay from created date,latest update time,'
                       'delay from latest update,status,bot advice\n')
        file_out.writelines([item.output() for item in sorted(issue_status, key=_key_select)])

    # commit to github
    print_check('git add .')
    print_check('git commit -m \"update excel\"')
    print_check('git push -f origin HEAD')

    # upload to storage account(it is created in advance)
    blob = BlobClient.from_connection_string(conn_str=os.getenv('CONN_STR'), container_name=os.getenv('FILE'),
                                             blob_name=_FILE_OUT)
    with open(_FILE_OUT, 'rb') as data:
        blob.upload_blob(data, overwrite=True)


if __name__ == '__main__':
    main()
