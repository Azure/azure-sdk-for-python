import os
import argparse
import logging

from ghapi.all import GhApi

ISSUE_LINK = ''
PULL_NUMBER = 0
NEW_BRANCH = ''
TARGET_BRANCH = ''

_LOG = logging.getLogger()
USER_TOKEN = os.getenv('USR_TOKEN')


def create_auto_release_pr(api):
    pr_title = "[AutoRelease] {}(Do not merge)".format(NEW_BRANCH)
    pr_head = "{}:{}".format(USER_NAME, NEW_BRANCH)
    pr_base = TARGET_BRANCH
    pr_body = "issue link {}".format(ISSUE_LINK)

    res_create = api.pulls.create(pr_title, pr_head, pr_base, pr_body)
    print(res_create)


def get_pr_number():
    pass


def main():
    api = GhApi(owner='Azure', repo='azure-sdk-for-python', token=USER_TOKEN)

    pr = create_auto_release_pr(api)
    return

    api.pulls.update(pull_number=20050, body='https://github.com/Azure/sdk-release-request/issues/1739')
    # api.pulls.update(pull_number=PULL_NUMBER, body=ISSUE_LINK)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Add Issue link',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("new_branch", help="new branch for SDK")
    parser.add_argument("target_branch", help="target branch for SDK")
    parser.add_argument("user_name", help="user name")
    parser.add_argument("issue_link", help="issue link")
    args = parser.parse_args()

    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.INFO)

    NEW_BRANCH = args.new_branch
    TARGET_BRANCH = args.target_branch
    USER_NAME = args.user_name
    ISSUE_LINK = args.issue_link

    main()
# python create_auto_release_pr.py "$(new_branch)" "$(target_branch)" $USER_NAME $ISSUE_LINK
