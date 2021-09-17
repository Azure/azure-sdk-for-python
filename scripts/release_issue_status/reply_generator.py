from utils import run_pipeline
import re
import logging

import requests
from bs4 import BeautifulSoup

issue_object_rg = None
logging.basicConfig(level=logging.DEBUG,
                    format='[auto-reply  log]%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def weather_change_readme(rest_repo, link_dict, labels):
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


def latest_pr_parse(rest_repo, latest_pr_number):
    latest_pr = rest_repo.get_issue(latest_pr_number)
    latest_pr_comments = latest_pr.get_comments()
    b = [i for i in latest_pr_comments]
    for comment in latest_pr_comments:
        if '<h3>Swagger Generation Artifacts</h3>' in comment.body:
            return swagger_generator_parse(comment.body, latest_pr_number)


def swagger_generator_parse(context, latest_pr_number):
    track1_info_model = ''
    try:
        if '<b> azure-sdk-for-python</b>' in context:
            pattern_python_t1 = re.compile('<b> azure-sdk-for-python</b>.+?</details>', re.DOTALL)
            python_t1 = re.search(pattern_python_t1, context).group()
            prttern_python_track1 = re.compile('<ul>\s+?<li>\s+?<a.+</ul>', re.DOTALL)
            python_track1_info = re.search(prttern_python_track1, python_t1).group()
            track1_info_model = '<details open><summary><b> python-track1</b></summary>{} </details>'.format(
                python_track1_info)
    except Exception as e:
        logging.error('track1 generate error')
    pattern_python = re.compile('<b> azure-sdk-for-python-track2</b>.+?</details>', re.DOTALL)
    python = re.search(pattern_python, context).group()
    # the way that reply not contains [Release SDK Changes]
    # pattern_python_track2 = re.compile('<ul>\s*?<li>\s*?<a.*</ul>', re.DOTALL)
    pattern_python_track2 = re.compile('<b>track2_.*</ul>', re.DOTALL)
    python_track2_info = re.search(pattern_python_track2, python).group()
    track2_info_model = '<details open><summary><b> python-track2</b></summary>{} </details>'.format(
        python_track2_info)
    pattern_sdk_changes = re.compile('/azure-sdk-for-python/pull/\d*">Release SDK Changes</a>', re.DOTALL)
    sdk_link = re.search(pattern_sdk_changes, python_track2_info).group()
    sdk_link_number = re.search(re.compile('[0-9]+'), sdk_link).group()
    info_model = 'hi @{} Please check the package whether works well and the changelog info is as below:\n' \
                 '{}\n{}\n' \
                 '\n* (The version of the package is only a temporary version for testing)\n' \
                 '\nhttps://github.com/Azure/azure-rest-api-specs/pull/{}\n' \
        .format(issue_object_rg.user.login, track1_info_model, track2_info_model, str(latest_pr_number))

    return info_model, sdk_link_number


def reply_owner(reply_content):
    issue_object_rg.create_comment(reply_content)


def add_label(label_name, labels):
    if label_name not in labels:
        labels.append(label_name)
    issue_object_rg.set_labels(*labels)


# Get SDK changelog by the latest PR's Checks
def get_chanelog_and_sdk_number(rest_repo, latest_pr_number):

    # latest_pr = rest_repo.get_pull(latest_pr_number)
    url = f'https://github.com/Azure/azure-rest-api-specs/pull/{latest_pr_number}'
    res = requests.get(url=url)
    soup = BeautifulSoup(res.text, 'html.parser')
    # checks = soup.select('strong[class="text-emphasized"]')
    checks = soup.select('div[class="d-flex flex-items-baseline Box-row"]')
    for check in checks:
        if 'SDK azure-sdk-for-python-track2' in check.text:
            for content in check.contents:
                if content.name == 'a' and '/Azure/azure-rest-api-specs/runs' in content.get('href'):
                    check_run_id = int(content.get('href').replace('/Azure/azure-rest-api-specs/runs/', ''))
                    details = rest_repo.get_check_run(check_run_id).output.text
                    # print(details)
                    sdk_link_number = re.findall(r'/azure-sdk-for-python/pull/(\d*)">Preview SDK Changes</a>', details)[0]
                    changelog = '<details open><summary><b> python-track2</b></summary> track2_azure-mgmt-{} </details>'.format(details.split('</code><b>track2_azure-mgmt-')[-1])
                    info_model = 'hi @{} Please check the package whether works well and the changelog info ' \
                                 'is as below:\n{}\n' \
                                 '\n* (The version of the package is only a temporary version for testing)\n' \
                                 '\nhttps://github.com/Azure/azure-rest-api-specs/pull/{}\n' \
                        .format(issue_object_rg.user.login, changelog, str(latest_pr_number))
                    return info_model, sdk_link_number
    raise Exception('cannot get info_model or sdk_link_number')


def begin_reply_generate(item, rest_repo, readme_link, sdk_repo, pipeline_url):
    global issue_object_rg
    issue_object_rg = item.issue_object
    link_dict = get_links(readme_link)
    labels = item.labels
    whether_change_readme = weather_change_readme(rest_repo, link_dict, labels)

    if not whether_change_readme:
        latest_pr_number = get_latest_pr_from_readme(rest_repo, link_dict)
        reply_content, sdk_link_number = get_chanelog_and_sdk_number(rest_repo, latest_pr_number)
        res_run = run_pipeline(issue_link=issue_object_rg.html_url,
                                        sdk_issue_object=sdk_repo.get_pull(int(sdk_link_number)),
                                        pipeline_url=pipeline_url
                                        )
        if res_run:
            logging.info(f'{issue_object_rg.number} run pipeline successfully')
        else:
            logging.info(f'{issue_object_rg.number} run pipeline fail')
        reply_owner(reply_content)
        add_label('auto-ask-check', labels)
    else:
        logging.info('issue {} need config readme'.format(issue_object_rg.number))
