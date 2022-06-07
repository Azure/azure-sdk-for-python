import os
import re
import json
import time
import logging
from glob import glob
import subprocess
from pathlib import Path
from functools import wraps
from typing import List, Any, Dict
from packaging.version import Version
from ghapi.all import GhApi
from azure.storage.blob import BlobServiceClient, ContainerClient
from util import add_certificate

_LOG = logging.getLogger()


def return_origin_path(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_path = os.getcwd()
        result = func(*args, **kwargs)
        os.chdir(current_path)
        return result

    return wrapper


def log(cmd: str):
    _LOG.info('==' + cmd + ' ==\n')


def print_exec(cmd: str):
    log(cmd)
    subprocess.call(cmd, shell=True)


def print_exec_output(cmd: str) -> List[str]:
    log(cmd)
    return subprocess.getoutput(cmd).split('\n')


def print_check(cmd):
    log(cmd)
    subprocess.check_call(cmd, shell=True)


def preview_version_plus(preview_label: str, last_version: str) -> str:
    num = last_version.split(preview_label)
    num[1] = str(int(num[1]) + 1)
    return f'{num[0]}{preview_label}{num[1]}'


def stable_version_plus(changelog: str, last_version: str):
    flag = [False, False, False]  # breaking, feature, bugfix
    flag[0] = '**Breaking changes**' in changelog
    flag[1] = '**Features**' in changelog
    flag[2] = '**Bugfixes**' in changelog

    num = last_version.split('.')
    if flag[0]:
        return f'{int(num[0]) + 1}.0.0'
    elif flag[1]:
        return f'{num[0]}.{int(num[1]) + 1}.0'
    elif flag[2]:
        return f'{num[0]}.{num[1]}.{int(num[2]) + 1}'
    else:
        return '0.0.0'


# find all the files of one folder, including files in subdirectory
def all_files(path: str, files: List[str]):
    all_folder = os.listdir(path)
    for item in all_folder:
        folder = str(Path(f'{path}/{item}'))
        if os.path.isdir(folder):
            all_files(folder, files)
        else:
            files.append(folder)


def checkout_azure_default_branch():
    usr = 'azure-sdk'
    branch = 't2-communication-2022-06-06-53443'
    print_exec(f'git remote add {usr} https://github.com/{usr}/azure-sdk-for-python.git')
    print_check(f'git fetch {usr} {branch}')
    print_check(f'git checkout {usr}/{branch}')


def modify_file(file_path: str, func: Any):
    with open(file_path, 'r') as file_in:
        content = file_in.readlines()
    func(content)
    with open(file_path, 'w') as file_out:
        file_out.writelines(content)


def current_time() -> str:
    date = time.localtime(time.time())
    return '{}-{:02d}-{:02d}'.format(date.tm_year, date.tm_mon, date.tm_mday)


def current_time_month() -> str:
    date = time.localtime(time.time())
    return '{}-{:02d}'.format(date.tm_year, date.tm_mon)


def set_test_env_var():
    setting_path = str(Path(os.getenv('SCRIPT_PATH')) / 'mgmt_settings_real_.py')
    # edit mgmt_settings_real.py
    with open(setting_path, 'r') as file_in:
        list_in = file_in.readlines()

    for i in range(0, len(list_in)):
        list_in[i] = list_in[i].replace('ENV_TENANT_ID', os.environ['TENANT_ID'])
        list_in[i] = list_in[i].replace('ENV_CLIENT_ID', os.environ['CLIENT_ID'])
        list_in[i] = list_in[i].replace('ENV_CLIENT_SECRET', os.environ['CLIENT_SECRET'])
        list_in[i] = list_in[i].replace('ENV_SUBSCRIPTION_ID', os.environ['SUBSCRIPTION_ID'])
    with open(str(Path('tools/azure-sdk-tools/devtools_testutils/mgmt_settings_real.py')), 'w') as file_out:
        file_out.writelines(list_in)


def start_test_proxy():
    print_check('pwsh eng/common/testproxy/docker-start-proxy.ps1 \"start\"')


class CodegenTestPR:
    """
    This class can generate SDK code, run live test and create RP
    """

    def __init__(self):
        self.issue_link = os.getenv('ISSUE_LINK')
        self.pipeline_link = os.getenv('PIPELINE_LINK')
        self.bot_token = os.getenv('AZURESDK_BOT_TOKEN')
        self.spec_readme = os.getenv('SPEC_README', '')
        self.spec_repo = os.getenv('SPEC_REPO', '')
        self.conn_str = os.getenv('STORAGE_CONN_STR')
        self.storage_endpoint = os.getenv('STORAGE_ENDPOINT').strip('/')

        self.package_name = ''
        self.new_branch = ''
        self.sdk_folder = ''  # 'compute' in 'sdk/compute/azure-mgmt-dns'
        self.autorest_result = ''
        self.next_version = ''
        self.test_result = ''
        self.pr_number = 0
        self.container_name = ''
        self.private_package_link = []  # List[str]
        self.tag_is_stable = False

    @return_origin_path
    def get_latest_commit_in_swagger_repo(self) -> str:
        os.chdir(Path(self.spec_repo))
        head_sha = print_exec_output('git rev-parse HEAD')[0]
        return head_sha

    def readme_local_folder(self) -> Path:
        result = re.findall('specification/[a-zA-Z-]+/resource-manager', self.spec_readme)
        if len(result) == 0:
            service_name = self.spec_readme
        else:
            service_name = result[0].split('/')[1]
        return Path(f'specification/{service_name}/resource-manager/readme.md')

    def get_sdk_folder_with_autorest_result(self):
        generate_result = self.get_autorest_result()
        self.sdk_folder = generate_result["packages"][0]["path"][0].split('/')[-1]

    def generate_code(self):
        checkout_azure_default_branch()

        # prepare input data
        input_data = {
            'headSha': self.get_latest_commit_in_swagger_repo(),
            'repoHttpsUrl': "https://github.com/Azure/azure-rest-api-specs",
            'specFolder': self.spec_repo,
            'relatedReadmeMdFiles': [str(self.readme_local_folder())]
        }

        self.autorest_result = str(Path(os.getenv('TEMP_FOLDER')) / 'temp.json')
        with open(self.autorest_result, 'w') as file:
            json.dump(input_data, file)

        # generate code(be careful about the order)
        print_exec('python scripts/dev_setup.py -p azure-core')
        print_check(f'python -m packaging_tools.auto_codegen {self.autorest_result} {self.autorest_result}')

        generate_result = self.get_autorest_result()
        self.tag_is_stable = list(generate_result.values())[0]['tagIsStable']
        log(f"tag_is_stable is {self.tag_is_stable}")
        
        print_check(f'python -m packaging_tools.auto_package {self.autorest_result} {self.autorest_result}')

    def get_package_name_with_autorest_result(self):
        generate_result = self.get_autorest_result()
        self.package_name = generate_result["packages"][0]["packageName"].split('-')[-1]

    def prepare_branch_with_readme(self):
        self.generate_code()
        self.get_package_name_with_autorest_result()
        self.get_sdk_folder_with_autorest_result()
        self.create_new_branch()

    def get_package_name_with_branch(self) -> (str, str):
        origin_base_branch = os.getenv('BASE_BRANCH')
        # e.g. AzureSDKAutomation:sdkAuto/track2_azure-mgmt-network or azclibot:t2-network-2022-01-05-26928
        branch_info = origin_base_branch.split(':')
        split_str = 'azure-mgmt-'
        if 'azure-mgmt-' in branch_info[1]:
            self.package_name = branch_info[1].split(split_str)[-1]
        else:
            self.package_name = branch_info[1].split('-')[1]

        return branch_info[0], branch_info[1]

    def create_new_branch(self):
        self.new_branch = f't2-{self.package_name}-{current_time()}-{str(time.time())[-5:]}'
        print_check(f'git checkout -b {self.new_branch}')

    def create_branch_with_base_branch(self, github_usr: str, base_branch: str):
        # checkout base branch
        print_exec(f'git remote add {github_usr} https://github.com/{github_usr}/azure-sdk-for-python.git')
        print_check(f'git fetch {github_usr} {base_branch}')
        print_check(f'git checkout {github_usr}/{base_branch}')

        # create new branch
        self.create_new_branch()

    def prepare_branch_with_base_branch(self):
        github_usr, base_branch = self.get_package_name_with_branch()
        self.create_branch_with_base_branch(github_usr, base_branch)
        self.get_sdk_folder_with_package_name()

    def get_sdk_folder_with_package_name(self):
        folder_info = glob(f'sdk/*/azure-mgmt-{self.package_name}')[0]
        self.sdk_folder = Path(folder_info).parts[1]

    def prepare_branch(self):
        if self.spec_readme:
            self.prepare_branch_with_readme()
        # else:
        # self.prepare_branch_with_base_branch()

    def check_sdk_readme(self):
        sdk_readme = str(Path(f'sdk/{self.sdk_folder}/azure-mgmt-{self.package_name}/README.md'))

        def edit_sdk_readme(content: List[str]):
            for i in range(0, len(content)):
                if content[i].find('MyService') > 0:
                    content[i] = content[i].replace('MyService', self.package_name.capitalize())

        modify_file(sdk_readme, edit_sdk_readme)

    def check_sdk_setup(self):
        def edit_sdk_setup(content: List[str]):
            for i in range(0, len(content)):
                content[i] = content[i].replace('msrestazure>=0.4.32,<2.0.0', 'azure-mgmt-core>=1.3.0,<2.0.0')
                content[i] = content[i].replace('azure-mgmt-core>=1.2.0,<2.0.0', 'azure-mgmt-core>=1.3.0,<2.0.0')
                content[i] = content[i].replace('msrest>=0.5.0', 'msrest>=0.6.21')

        modify_file(str(Path(self.sdk_code_path()) / 'setup.py'), edit_sdk_setup)

    # Use the template to update readme and setup by packaging_tools
    @return_origin_path
    def check_file_with_packaging_tool(self):
        os.chdir(Path(f'sdk/{self.sdk_folder}'))
        print_check(f'python -m packaging_tools --build-conf azure-mgmt-{self.package_name}')
        print("**** path: ", Path(f'sdk/{self.sdk_folder}'))
        print("**** path now:", os.getcwd())
        with open('MANIFEST.in', 'r', encoding='utf-8') as f:
            print(f'**** {f.read()}')
        log('packaging_tools --build-conf successfully ')

    def check_pprint_name(self):
        pprint_name = self.package_name.capitalize()

        def edit_file_for_pprint_name(content: List[str]):
            for i in range(0, len(content)):
                content[i] = content[i].replace('MyService', pprint_name)

        for file in os.listdir(self.sdk_code_path()):
            file_path = str(Path(self.sdk_code_path()) / file)
            if os.path.isfile(file_path):
                modify_file(file_path, edit_file_for_pprint_name)
        log(f' replace \"MyService\" with \"{pprint_name}\" successfully ')

    def get_all_files_under_package_folder(self) -> List[str]:
        files = []
        all_files(self.sdk_code_path(), files)
        return files

    def calculate_next_version_proc(self, last_version: str):
        preview_tag = not self.tag_is_stable
        changelog = self.get_changelog()
        if changelog == '':
            return '0.0.0'
        preview_version = 'rc' in last_version or 'b' in last_version
        #                                           |   preview tag                     | stable tag
        # preview version(1.0.0rc1/1.0.0b1)         | 1.0.0rc2(track1)/1.0.0b2(track2)  |  1.0.0
        # stable  version (1.0.0) (breaking change) | 2.0.0rc1(track1)/2.0.0b1(track2)  |  2.0.0
        # stable  version (1.0.0) (feature)         | 1.1.0rc1(track1)/1.1.0b1(track2)  |  1.1.0
        # stable  version (1.0.0) (bugfix)          | 1.0.1rc1(track1)/1.0.1b1(track2)  |  1.0.1
        preview_label = 'b'
        if preview_version and preview_tag:
            next_version = preview_version_plus(preview_label, last_version)
        elif preview_version and not preview_tag:
            next_version = last_version.split(preview_label)[0]
        elif not preview_version and preview_tag:
            next_version = stable_version_plus(changelog, last_version) + preview_label + '1'
        else:
            next_version = stable_version_plus(changelog, last_version)

        return next_version

    def get_autorest_result(self) -> Dict[Any, Any]:
        with open(self.autorest_result, 'r') as file_in:
            content = json.load(file_in)
        return content

    def get_changelog(self) -> str:
        content = self.get_autorest_result()
        return content["packages"][0]["changelog"]["content"]

    def get_last_release_version(self) -> str:
        content = self.get_autorest_result()
        last_version = content["packages"][0]["version"]
        try:
            return str(Version(last_version))
        except:
            return ''

    def calculate_next_version(self):
        last_version = self.get_last_release_version()
        if last_version:
            self.next_version = self.calculate_next_version_proc(last_version)
        else:
            self.next_version = '1.0.0b1'

    def edit_all_version_file(self):
        files = self.get_all_files_under_package_folder()

        def edit_version_file(content: List[str]):
            for i in range(0, len(content)):
                if content[i].find('VERSION') > -1:
                    content[i] = f'VERSION = "{self.next_version}"\n'
                    break

        for file in files:
            if '_version.py' in file:
                modify_file(file, edit_version_file)

    def check_version(self):
        self.calculate_next_version()
        self.edit_all_version_file()

    def edit_changelog_for_new_service(self):
        def edit_changelog_for_new_service_proc(content: List[str]):
            for i in range(0, len(content)):
                if '##' in content[i]:
                    content[i] = f'## {self.next_version} ({current_time()})\n'
                    break

        modify_file(str(Path(self.sdk_code_path()) / 'CHANGELOG.md'), edit_changelog_for_new_service_proc)

    def edit_changelog(self):
        def edit_changelog_proc(content: List[str]):
            content[1:1] = ['\n', f'## {self.next_version} ({current_time()})\n\n', self.get_changelog(), '\n']

        modify_file(str(Path(self.sdk_code_path()) / 'CHANGELOG.md'), edit_changelog_proc)

    def check_changelog_file(self):
        if self.next_version == '1.0.0b1':
            self.edit_changelog_for_new_service()
        else:
            self.edit_changelog()

    def check_ci_file_proc(self, dependency: str):
        def edit_ci_file(content: List[str]):
            new_line = f'#override azure-mgmt-{self.package_name} {dependency}'
            for i in range(len(content)):
                if new_line in content[i]:
                    return
            prefix = '' if '\n' in content[-1] else '\n'
            content.append(prefix + new_line + '\n')

        modify_file(str(Path('shared_requirements.txt')), edit_ci_file)
        print_exec('git add shared_requirements.txt')

    def check_ci_file(self):
        self.check_ci_file_proc('msrest>=0.6.21')
        self.check_ci_file_proc('azure-mgmt-core>=1.3.0,<2.0.0')

    def check_file(self):
        self.check_file_with_packaging_tool()
        self.check_pprint_name()
        self.check_sdk_readme()
        self.check_sdk_setup()
        self.check_version()
        self.check_changelog_file()
        self.check_ci_file()

    def sdk_code_path(self) -> str:
        return str(Path(f'sdk/{self.sdk_folder}/azure-mgmt-{self.package_name}'))

    @property
    def is_single_path(self) -> bool:
        path = str(Path(f'sdk/{self.sdk_folder}'))
        num = sum([os.path.isdir(str(Path(f'{path}/{listx}'))) for listx in os.listdir(path)])
        return num == 1

    @return_origin_path
    def install_package_locally(self):
        os.chdir(self.sdk_code_path())
        print_check('pip install -e .')
        print_exec('pip install -r dev_requirements.txt')

    def prepare_test_env(self):
        self.install_package_locally()
        set_test_env_var()
        add_certificate()
        start_test_proxy()

    @return_origin_path
    def run_test_proc(self):
        # run test
        os.chdir(self.sdk_code_path())
        succeeded_result = 'Live test success'
        failed_result = 'Live test fail, detailed info is in pipeline log(search keyword FAILED)!!!'
        try:
            print_check(f'pytest  --collect-only')
        except:
            log('live test run done, do not find any test !!!')
            self.test_result = succeeded_result
            return

        try:
            print_check(f'pytest -s')
        except:
            log('some test failed, please fix it locally')
            self.test_result = failed_result
        else:
            log('live test run done, do not find failure !!!')
            self.test_result = succeeded_result

    def run_test(self):
        self.prepare_test_env()
        self.run_test_proc()

    def create_pr_proc(self):
        api = GhApi(owner='Azure', repo='azure-sdk-for-python', token=self.bot_token)
        pr_title = "[AutoRelease] {}(Do not merge)".format(self.new_branch)
        pr_head = "{}:{}".format(os.getenv('USR_NAME'), self.new_branch)
        pr_base = 'main'
        pr_body = "{} \n{} \n{}".format(self.issue_link, self.test_result, self.pipeline_link)
        if not self.is_single_path:
            pr_body += f'\nBuildTargetingString\n  azure-mgmt-{self.package_name}\nSkip.CreateApiReview\ntrue'
        res_create = api.pulls.create(pr_title, pr_head, pr_base, pr_body)

        # Add issue link on PR
        api = GhApi(owner='Azure', repo='azure-sdk-for-python', token=self.bot_token)
        api.issues.create_comment(issue_number=res_create.number, body='issue link:{}'.format(self.issue_link))
        self.pr_number = res_create.number

    def zero_version_policy(self):
        if self.next_version == '0.0.0':
            api_request = GhApi(owner='Azure', repo='sdk-release-request', token=self.bot_token)
            issue_number = int(self.issue_link.split('/')[-1])
            api_request.issues.add_labels(issue_number=issue_number, labels=['base-branch-attention'])

    def get_container_name(self) -> str:
        container_name = current_time_month()
        service_client = BlobServiceClient.from_connection_string(conn_str=self.conn_str)
        containers_exist = [container for container in service_client.list_containers()]
        containers_name = {container.name for container in containers_exist}
        # create new container if it does not exist
        if container_name not in containers_name:
            container_client = service_client.get_container_client(container=container_name)
            container_client.create_container(public_access='container', timeout=60 * 24 * 3600)
        return container_name

    def get_private_package(self) -> List[str]:
        content = self.get_autorest_result()
        return content["packages"][0]["artifacts"]

    def upload_private_package_proc(self, container_name: str):
        container_client = ContainerClient.from_connection_string(conn_str=self.conn_str, container_name=container_name)
        private_package = self.get_private_package()
        for package in private_package:
            package_name = Path(package).parts[-1]
            # package will be uploaded to storage account in the folder : container_name / pr_number / package_name
            blob_name = f'sdk_pr_{self.pr_number}/{package_name}'
            blob_client = container_client.get_blob_client(blob=blob_name)
            with open(package, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            self.private_package_link.append(f'{self.storage_endpoint}/{container_name}/{blob_name}')

    def upload_private_package(self):
        container_name = self.get_container_name()
        self.upload_private_package_proc(container_name)

    def get_private_package_link(self) -> str:
        self.upload_private_package()
        result = []
        # it is for markdown
        for link in self.private_package_link:
            package_name = link.split('/')[-1]
            result.append(f'* [{package_name}]({link})\n')
        return ''.join(result)

    def ask_check_policy(self):
        changelog = self.get_changelog()
        if changelog == '':
            changelog = 'no new content found by changelog tools!'

        # comment to ask for check from users
        issue_number = int(self.issue_link.split('/')[-1])
        api = GhApi(owner='Azure', repo='sdk-release-request', token=self.bot_token)
        author = api.issues.get(issue_number=issue_number).user.login
        body = f'Hi @{author}, Please check whether the package works well and the CHANGELOG info is as below:\n' \
               f'{self.get_private_package_link()}' \
               f'```\n' \
               f'CHANGELOG:\n' \
               f'{changelog}\n' \
               f'```\n' \
               f'* (If you are not a Python User, you can mainly check whether the changelog meets your requirements)\n\n' \
               f'* (The version of the package is only a temporary version for testing)\n\n' \
               f'https://github.com/Azure/azure-sdk-for-python/pull/{self.pr_number}'
        api.issues.create_comment(issue_number=issue_number, body=body)

        # comment for hint
        body = 'Tips: If you have special needs for release date or other things, please let us know. ' \
               'Otherwise we will release it ASAP after your check.'
        api.issues.create_comment(issue_number=issue_number, body=body)

    def issue_comment(self):
        self.zero_version_policy()
        self.ask_check_policy()

    def create_pr(self):
        # commit all code
        print_exec('git add sdk/')
        print_exec('git commit -m \"code and test\"')
        print_check('git push origin HEAD -f')

        # create PR
        self.create_pr_proc()

        # create release issue comment
        self.issue_comment()

    def run(self):
        self.prepare_branch()
        self.check_file()
        self.run_test()
        self.create_pr()


if __name__ == '__main__':
    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.INFO)

    instance = CodegenTestPR()
    instance.run()
