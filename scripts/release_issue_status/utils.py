import datetime
import json
import os
import re
import logging
import urllib.parse

from azure.devops.v6_0.pipelines.pipelines_client import PipelinesClient
from azure.devops.v6_0.pipelines import models
from bs4 import BeautifulSoup
from msrest.authentication import BasicAuthentication
import requests

_FILE_OUT = 'published_issues_python.csv'

logging.basicConfig(level=logging.INFO,
                    format='[auto-reply  log] - %(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s')

# Add readme link and package name to the user's issue
def update_issue_body(sdk_repo, rest_repo, issue_number):
    # Get Issue Number
    issue_info = sdk_repo.get_issue(number=issue_number)
    issue_body = issue_info.body
    issue_body_list = [i for i in issue_body.split("\n") if i]
    # Get the link and readme tag in issue body
    link, readme_tag = '', ''
    for row in issue_body_list:
        if 'link' in row.lower():
            link = row.split(":", 1)[-1].strip()
        if 'readme tag' in row.lower():
            readme_tag = row.split(":", 1)[-1].strip()
        if link and readme_tag:
            break

    if link.count('https') > 1:
        link = link.split(']')[0]
        link = link.replace('[', "").replace(']', "").replace('(', "").replace(')', "")

    package_name, readme_link, output_folder = _get_pkname_and_readme_link(rest_repo, link, issue_info)
    # Check readme tag format
    if 'package' not in readme_tag:
        readme_tag = 'package-{}'.format(readme_tag)
        issue_body_list.insert(0, f'Readme Tag: {readme_tag}')

    issue_body_list.insert(0, f'\n{readme_link.replace("/readme.md", "")}')
    issue_body_list.insert(1, package_name)
    issue_body_up = ''
    for raw in issue_body_list:
        if raw == '---\r' or raw == '---':
            issue_body_up += '\n'
        issue_body_up += raw + '\n'

    issue_info.edit(body=issue_body_up)
    return package_name, readme_link, output_folder


def _get_pkname_and_readme_link(rest_repo, link, issue_info):
    # change commit link to pull json link(i.e. https://github.com/Azure/azure-rest-api-specs/commit/77f5d3b5d2fbae17621ea124485788f496786758#diff-708c2fb843b022cac4af8c6f996a527440c1e0d328abb81f54670747bf14ab1a)
    pk_name = ''
    if 'commit' in link:
        commit_sha = link.split('commit/')[-1]
        commit = rest_repo.get_commit(commit_sha)
        link = commit.files[0].blob_url
        link = re.sub('blob/(.*?)/specification', 'blob/main/specification', link)

    # if link is a pr, it can get both pakeage name and readme link.
    if 'pull' in link:
        pr_number = int(link.replace("https://github.com/Azure/azure-rest-api-specs/pull/", "").strip('/'))

        # Get Readme link
        pr_info = rest_repo.get_pull(number=pr_number)
        
        if not pr_info.merged:
            issue_info.create_comment(f' @{issue_info.user.login},please merge your pr first. {link}')
            raise Exception('PR has not been merged')
            
        pk_url_name = set()
        for pr_changed_file in pr_info.get_files():
            contents_url = urllib.parse.unquote(pr_changed_file.contents_url)
            if '/resource-manager' in contents_url:
                try:
                    pk_url_name.add(re.findall(r'/specification/(.*?)/resource-manager/', contents_url)[0])
                except Exception as e:
                    continue
                if len(pk_url_name) > 1:
                    logging.info("\nexists multiple package names: {} \n".format(pk_url_name))
                    raise Exception('Not find readme link, because it exists multiple package names')

        readme_link = 'https://github.com/Azure/azure-rest-api-specs/blob/main/specification/{}/' \
                      'resource-manager/readme.python.md'.format(list(pk_url_name)[0])
    # if link is a rest url(i.e. https://github.com/Azure/azure-rest-api-specs/blob/main/specification/xxx/resource-manager/readme.python.md)
    elif '/resource-manager' not in link:
        # (i.e. https://github.com/Azure/azure-rest-api-specs/tree/main/specification/xxxx)
        readme_link = link + '/resource-manager/readme.python.md'
    else:
        readme_link = link.split('/resource-manager')[0] + '/resource-manager/readme.python.md'
    # get the package name by readme link
    pk_name, out_folder = _find_package_name_and_output(rest_repo, readme_link)
    readme_link = readme_link.replace('python.', '')
    return pk_name, readme_link, out_folder


# Get readme link and output folder in user issue
def get_readme_and_output_folder(sdk_repo, rest_repo, issue_number):
    # Get Issue Number
    issue_info = sdk_repo.get_issue(number=issue_number)
    issue_body = issue_info.body
    issue_body_list = issue_body.split("\n")
    for row in issue_body_list:
        if 'resource-manager' in row:
            readme_link = '{}/readme.md'.format(row.strip("\r"))
            # Get output folder from readme.python.md
            readme_python_link = readme_link.split('/resource-manager')[0] + '/resource-manager/readme.python.md'
            _, output_folder = _find_package_name_and_output(rest_repo, readme_python_link)
            return readme_link, output_folder
    raise Exception('Not find readme link,please check')


# Find package name and output folder from readme link
def _find_package_name_and_output(rest_repo, readme_link):
    readme_link_part = '/specification' + readme_link.split('/specification')[-1]
    readme_contents = str(rest_repo.get_contents(readme_link_part).decoded_content)
    pk_name = re.findall(r'package-name: (.*?)\\n', readme_contents)[0]
    out_folder = re.findall(r'\$\(python-sdks-folder\)/(.*?)/azure-', readme_contents)[0]
    return pk_name, out_folder


# get python pipeline name and definitionId from web
def get_python_pipelines():
    python_piplines = {}
    pipeline_client = PipelinesClient(base_url='https://dev.azure.com/azure-sdk',
                                      creds=BasicAuthentication(os.getenv('PIPELINE_TOKEN'), ''))
    pipelines = pipeline_client.list_pipelines(project='internal')
    for pipeline in pipelines:
        if re.findall('^python - \w*$', pipeline.name):
            key = pipeline.name.replace('python - ', '')
            python_piplines[key] = pipeline.id
    return python_piplines

# get the pipeline url through definitionid
def get_pipeline_url(python_piplines, output_folder):
    definitionId = python_piplines.get(output_folder)
    if definitionId:
        pipeline_url = 'https://dev.azure.com/azure-sdk/internal/_build?definitionId={}'.format(definitionId)
    else:
        logging.info('Cannot find definitionId, Do not display pipeline_url')
        pipeline_url = ''
    return pipeline_url


# Run sdk-auto-release(main) to generate SDK
def run_pipeline(issue_link, pipeline_url, spec_readme):
    paramaters = {
        "stages_to_skip": [],
        "resources": {
            "repositories": {
                "self": {
                    "refName": "refs/heads/main"
                }
            }
        },
        "variables": {
            "BASE_BRANCH": {
                "value": "",
                "isSecret": False
            },
            "ISSUE_LINK": {
                "value": issue_link,
                "isSecret": False
            },
            "PIPELINE_LINK": {
                "value": pipeline_url,
                "isSecret": False
            },
            "SPEC_README": {
                "value": spec_readme,
                "isSecret": False
            }
        }
    }
    # Fill in with your personal access token and org URL
    personal_access_token = os.getenv('PIPELINE_TOKEN')
    organization_url = 'https://dev.azure.com/azure-sdk'

    # Create a connection to the org
    credentials = BasicAuthentication('', personal_access_token)
    run_parameters = models.RunPipelineParameters(**paramaters)
    client = PipelinesClient(base_url=organization_url, creds=credentials)
    result = client.run_pipeline(project='internal', pipeline_id=2500, run_parameters=run_parameters)
    if result.state == 'inProgress':
        return True
    else:
        return False


# Auto reply to the user pypi link and close the issue. If the new version is successfully published.
def auto_close_issue(sdk_repo, item):
    issue_number, package_name = item.issue_object.number, item.package
    issue_info = sdk_repo.get_issue(number=issue_number)
    issue_author = issue_info.user.login
    issue_created_date = issue_info.created_at
    last_version, last_time = _get_last_released_date(package_name)
    if last_time and last_time > issue_created_date and 'auto-closed' not in item.labels:
        comment = f'Hi @{issue_author}, pypi link: https://pypi.org/project/{package_name}/{last_version}/'
        issue_info.create_comment(body=comment)
        issue_info.edit(state='closed')
        item.issue_object.add_to_labels('auto-closed')
        logging.info(f"issue number：{issue_number} has been closed!")
     
        created_at = issue_info.created_at.strftime('%Y-%m-%d')
        closed_at = issue_info.closed_at.strftime('%Y-%m-%d')
        assignee = issue_info.assignee.login
        link = issue_info.html_url
        closed_issue_info = f'{package_name},{assignee},{created_at},{closed_at},{link}\n'
        with open(_FILE_OUT, 'r') as file_read:
            lines = file_read.readlines()
        with open(_FILE_OUT, 'w') as file_write:
            lines.insert(1, closed_issue_info)
            file_write.writelines(lines)

def _get_last_released_date(package_name):
    pypi_link = f'https://pypi.org/project/{package_name}/#history'
    res = requests.get(pypi_link)
    soup = BeautifulSoup(res.text, 'html.parser')
    # find top div from <div class="release-timeline">
    try:
        package_info = soup.select('div[class="release-timeline"]')[0].find_all('div')[0]
        last_version_mix = package_info.find_all('p', class_="release__version")[0].contents[0]
    except IndexError as e:
        return '', ''
    last_version = last_version_mix.replace(' ', '').replace('\n', '')
    last_version_date_str = package_info.time.attrs['datetime'].split('+')[0]
    last_version_date = datetime.datetime.strptime(last_version_date_str, '%Y-%m-%dT%H:%M:%S')
    return last_version, last_version_date
