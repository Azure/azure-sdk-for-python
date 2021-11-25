from utils import run_pipeline
import re
import logging

issue_object_rg = None
logging.basicConfig(level=logging.INFO,
                    format='[auto-reply  log] - %(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def readme_comparison(rest_repo, link_dict, labels):
    # to see whether need change readme
    contents = str(rest_repo.get_contents(link_dict['readme_path']).decoded_content)
    pattern_tag = re.compile(r'tag: package-[\w+-.]+')
    package_tag = pattern_tag.findall(contents)
    readme_python_contents = str(rest_repo.get_contents(link_dict['readme_python_path']).decoded_content)
    whether_multi_api = 'multi-api' in readme_python_contents
    whether_same_tag = link_dict['readme_tag'] in package_tag
    whether_change_readme = not whether_same_tag or whether_multi_api and not 'MultiAPI' in labels
    if 'Configured' in labels:
        whether_change_readme = False
    return whether_change_readme


# parse owner's comment and get links
def get_links(readme_link):
    link_dict = {}
    comment_body = issue_object_rg.body
    pattern_readme = re.compile(r'/specification/([\w-]+/)+readme.md')
    pattern_resource_manager = re.compile(r'/specification/([\w-]+/)+resource-manager')
    pattern_tag = re.compile(r'package-[\w+-.]+')
    readme_path = pattern_readme.search(readme_link).group()
    readme_tag = pattern_tag.search(comment_body).group()
    resource_manager = pattern_resource_manager.search(readme_link).group()
    link_dict['readme_path'] = readme_path
    link_dict['readme_python_path'] = readme_path[:readme_path.rfind('/')] + '/readme.python.md'
    link_dict['readme_tag'] = 'tag: ' + readme_tag
    link_dict['resource_manager'] = resource_manager
    return link_dict


def get_latest_pr_from_readme(rest_repo, link_dict):
    commits = rest_repo.get_commits(path=link_dict['resource_manager'])
    latest_commit = [commit for commit in commits][0]
    latest_pr_brief = latest_commit.commit.message
    latest_pr_number = re.findall('\(\#[0-9]+\)', latest_pr_brief)
    latest_pr_number_int = []
    for number in latest_pr_number:
        number = int(re.search('\d+', number).group())
        latest_pr_number_int.append(number)
    latest_pr_number_int.sort()

    return latest_pr_number_int[-1]


def reply_owner(assigner_issue, reply_content):
    assigner_issue.create_comment(reply_content)
    user_tips = 'Tips: If you have special needs for release date or other things, please let us know. Otherwise we will release it ASAP after your check.'
    assigner_issue.create_comment(user_tips)



def get_reply_and_sdk_number_from_readme(rest_repo, link_dict, item):
    commits = rest_repo.get_commits(path=link_dict['resource_manager'])
    latest_commit = commits[0]
    check_run_id = latest_commit.get_check_runs(check_name='SDK azure-sdk-for-python-track2')[0].id
    latest_pr_number = latest_commit.get_pulls()[0].number
    details = rest_repo.get_check_run(check_run_id).output.text
    sdk_link_number = re.findall(r'/azure-sdk-for-python/pull/(\d*)">Release SDK Changes</a>', details)[0]
    changelog = = re.search(rf'</code><b>track2_{item.package}(.)+?</pre></li>',details,re.DOTALL).group()
    info_model = 'hi @{} Please check the package whether works well and the changelog info ' \
                 'is as below:\n{}\n' \
                 '\n* (The version of the package is only a temporary version for testing)\n' \
                 '\nhttps://github.com/Azure/azure-rest-api-specs/pull/{}\n' \
        .format(issue_object_rg.user.login, changelog, str(latest_pr_number))
    return info_model, sdk_link_number


def begin_reply_generate(item, rest_repo, readme_link, sdk_repo, pipeline_url, assigner_repo):
    global issue_object_rg
    issue_object_rg = item.issue_object
    link_dict = get_links(readme_link)
    labels = item.labels
    whether_change_readme = readme_comparison(rest_repo, link_dict, labels)

    if not whether_change_readme:
        reply_content, sdk_link_number = get_reply_and_sdk_number_from_readme(rest_repo, link_dict, item)
        res_run = run_pipeline(issue_link=issue_object_rg.html_url,
                                        sdk_issue_object=sdk_repo.get_pull(int(sdk_link_number)),
                                        pipeline_url=pipeline_url
                                        )
        if res_run:
            logging.info(f'{issue_object_rg.number} run pipeline successfully')
        else:
            logging.info(f'{issue_object_rg.number} run pipeline fail')
        assigner_issue = assigner_repo.get_issue(number=issue_object_rg.number)
        reply_owner(assigner_issue, reply_content)
        issue_object_rg.add_to_labels('auto-ask-check')
    else:
        logging.info('issue {} need config readme'.format(issue_object_rg.number))
