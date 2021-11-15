import os

from ghapi.all import GhApi

def main():
    # Generate PR for auto release SDK
    api = GhApi(owner='Azure', repo='azure-sdk-for-python', token=os.getenv('USR_TOKEN'))
    pr_title = "[AutoRelease] {}(Do not merge)".format(os.getenv('NEW_BRANCH'))
    pr_head = "{}:{}".format(os.getenv('USR_NAME'), os.getenv('NEW_BRANCH'))
    pr_base = os.getenv('TARGET_BRANCH')
    pr_body = "{} \n{} \n{}".format(os.getenv('ISSUE_LINK'), os.getenv('TEST_RESULT'), os.getenv('PIPELINE_LINK'))
    res_create = api.pulls.create(pr_title, pr_head, pr_base, pr_body)
    pr_number = res_create.number

    # Add issue link on PR
    api = GhApi(owner='Azure', repo='azure-sdk-for-python', token=os.getenv('UPDATE_TOKEN'))
    api.issues.create_comment(issue_number=pr_number, body='issue link:{}'.format(os.getenv('ISSUE_LINK')))
    
if __name__ == '__main__':
    main()
