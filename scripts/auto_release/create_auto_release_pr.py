import os

from ghapi.all import GhApi

NEW_BRANCH = os.getenv('NEW_BRANCH')
TARGET_BRANCH = os.getenv('TARGET_BRANCH')
ISSUE_LINK = os.getenv('ISSUE_LINK')
TEST_RESULT = os.getenv('TEST_RESULT')

# Generate PR for auto release SDK
def create_auto_release_pr(api):
    pr_title = "[AutoRelease] {}(Do not merge)".format(NEW_BRANCH)
    pr_head = "{}:{}".format(os.getenv('USR_NAME'), NEW_BRANCH)
    pr_base = TARGET_BRANCH
    pr_body = TEST_RESULT
    res_create = api.pulls.create(pr_title, pr_head, pr_base, pr_body)

    return res_create.number

# Add issue link on PR
def add_comment(api, pr_number):
    api.issues.create_comment(issue_number=pr_number, body='issue link:{}'.format(ISSUE_LINK))


def main():
    api = GhApi(owner='Azure', repo='azure-sdk-for-python', token=os.getenv('USR_TOKEN'))
    pr_number = create_auto_release_pr(api)

    api = GhApi(owner='Azure', repo='azure-sdk-for-python', token=os.getenv('UPDATE_TOKEN'))
    add_comment(api, pr_number)

if __name__ == '__main__':
    main()
