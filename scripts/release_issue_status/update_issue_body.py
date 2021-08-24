import os
import re

from github import Github


def update_issue_body(issue_link):
    # Get Issue Number
    issue_number = int(issue_link.replace("https://github.com/Azure/sdk-release-request/issues/", ""))
    g = Github(os.getenv('TOKEN'))
    sdk_repo = g.get_repo('Azure/sdk-release-request')
    rest_repo = g.get_repo('Azure/azure-rest-api-specs')
    issue_info = sdk_repo.get_issue(number=issue_number)
    issue_body = issue_info.body

    issue_body_list = [i for i in issue_body.split("\n") if i]
    # Get the link in issue body
    for row in issue_body_list:
        if 'link' in row.lower():
            link = row.split(":", 1)[-1].strip()
            break

    if link.count('https') > 1:
        link = link.split(']')[0]
        link = link.replace('[', "").replace(']', "").replace('(', "").replace(')', "")

    try:
        package_name, readme_link = get_pkname_and_readme_link(rest_repo, link)
    except Exception as e:
        print(e)
        return False

    readme_link = readme_link.replace('python.', '')
    issue_body_list.insert(0, f'\n{readme_link}')
    issue_body_list.insert(1, package_name)
    issue_body_up = ''
    for raw in issue_body_list:
        if raw == '---\r' or raw == '---':
            issue_body_up += '\n'
        issue_body_up += raw + '\n'
    try:
        issue_info.edit(body=issue_body_up)
        return True
    except Exception as e:
        print(e)
        return False


def get_pkname_and_readme_link(rest_repo, link):
    # change commit link to pull json link
    pk_name = ''
    if 'commit' in link:
        commit_sha = link.split('commit/')[-1]
        commit = rest_repo.get_commit(commit_sha)
        link = commit.files[0].blob_url

    # if link is a pr, it can get both pakeage name and readme link.
    if 'pull' in link:
        pk_name, readme_link = get_pkname_and_readme_from_pull(rest_repo, link)
    elif '/resource-manager' not in link:
        readme_link = link + '/resource-manager/readme.python.md'
    else:
        readme_link = link.split('/resource-manager')[0] + '/resource-manager/readme.python.md'
    # get the package name by readme link
    if not pk_name:
        readme_link_part = '/specification' + readme_link.split('/specification')[-1]
        readme_contents = str(rest_repo.get_contents(readme_link_part).decoded_content)
        pk_name = re.findall(r'package-name: (.*?)\\n', readme_contents)[0]

    return pk_name, readme_link


def get_pkname_and_readme_from_pull(rest_repo, pr_link):
    pr_number = int(pr_link.replace("https://github.com/Azure/azure-rest-api-specs/pull/", "").strip('/'))
    pr_info = rest_repo.get_issue(number=pr_number)

    # Get package name
    pr_comments = pr_info.get_comments()
    package_names = []
    for comment in pr_comments:
        if "Swagger Generation Artifacts" in comment.body:
            package_names = re.findall(r"<b>track\d_(.*?)</b>", comment.body)
            break

    if len(package_names) != 1:
        return '', ''
    package_name = package_names[0]

    # Get Readme link
    pr_info1 = rest_repo.get_pull(number=pr_number)
    for pr_changed_file in pr_info1.get_files():
        contents_url = pr_changed_file.contents_url
        if '/resource-manager' in contents_url:
            pk_url_name = re.findall(r'/specification/(.*?)/resource-manager/', contents_url)[0]
            break
    readme_link = 'https://github.com/Azure/azure-rest-api-specs/blob/main/specification/{}/' \
                  'resource-manager/readme.python.md'.format(pk_url_name)
