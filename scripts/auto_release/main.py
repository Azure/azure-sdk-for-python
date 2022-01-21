import os
import subprocess as sp
import logging
from ghapi.all import GhApi
from pathlib import Path
import json
from typing import List, Any, Dict
from glob import glob
import time
from util import add_certificate
from functools import wraps
from packaging.version import Version
import base64

_LOG = logging.getLogger()


def return_origin_path(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_path = os.getcwd()
        result = func(*args, **kwargs)
        os.chdir(current_path)
        return result

    return wrapper


def my_print(cmd):
    _LOG.info('==' + cmd + ' ==\n')


def print_exec(cmd):
    my_print(cmd)
    sp.call(cmd, shell=True)


def print_exec_output(cmd) -> List[str]:
    my_print(cmd)
    return sp.getoutput(cmd).split('\n')


def print_check(cmd):
    my_print(cmd)
    sp.check_call(cmd, shell=True)


def preview_version_plus(preview_label: str, last_version: str) -> str:
    num = last_version.split(preview_label)
    num[1] = str(int(num[1]) + 1)
    return f'{num[0]}{preview_label}{num[1]}'


def stable_version_plus(add_content: List[str], last_version: str):
    flag = [False, False, False]  # breaking, feature, bugfix
    content = ''.join(add_content)
    flag[0] = '**Breaking changes**' in content
    flag[1] = '**Features**' in content
    flag[2] = '**Bugfixes**' in content

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
    usr = 'msyyc'
    branch = 'temp'
    print_exec(f'git remote add {usr} https://github.com/{usr}/azure-sdk-for-python.git')
    print_check(f'git fetch {usr} {branch}')
    print_check(f'git checkout {usr}/{branch}')


def modify_file(file_path: str, func: Any):
    with open(file_path, 'r') as file_in:
        content = file_in.readlines()
    func(content)
    with open(file_path, 'w') as file_out:
        file_out.writelines(content)


def current_time():
    date = time.localtime(time.time())
    return '{}-{:02d}-{:02d}'.format(date.tm_year, date.tm_mon, date.tm_mday)


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
        self.usr_token = os.getenv('USR_TOKEN')
        self.pipeline_link = os.getenv('PIPELINE_LINK')
        self.bot_token = os.getenv('UPDATE_TOKEN')
        self.spec_readme = os.getenv('SPEC_README', '')
        self.spec_repo = os.getenv('SPEC_REPO', '')

        self.package_name = ''
        self.new_branch = ''
        self.sdk_folder = ''  # 'compute' in 'sdk/compute/azure-mgmt-dns'
        self.autorest_result = ''
        self.next_version = ''
        self.test_result = ''

    @return_origin_path
    def get_latest_commit_in_swagger_repo(self) -> str:
        os.chdir(Path(self.spec_repo))
        head_sha = print_exec_output('git rev-parse HEAD')[0]
        return head_sha

    def readme_local_folder(self) -> Path:
        html_link = 'https://github.com/Azure/azure-rest-api-specs/blob/main/'
        return Path(self.spec_readme.replace(html_link, '')) / 'readme.md'

    def get_sdk_folder_with_readme(self):
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

        my_print(input_data['headSha'])
        my_print(input_data['specFolder'])
        my_print(input_data['relatedReadmeMdFiles'][0])
        path = f'{input_data["specFolder"]}/{input_data["relatedReadmeMdFiles"][0]}'
        if os.path.exists(path):
            with open(path, 'r') as file_in:
                temp = file_in.readlines()
        else:
            my_print(f'{path} does not exist')

        temp_folder = Path(os.getenv('TEMP_FOLDER'))
        self.autorest_result = str(temp_folder / 'temp.json')
        with open(self.autorest_result, 'w') as file:
            json.dump(input_data, file)

        # generate code
        print_exec('python scripts/dev_setup.py -p azure-core')
        print_check(f'python -m packaging_tools.auto_codegen {self.autorest_result} {self.autorest_result}')

        my_print(str(self.get_autorest_result()))

        print_check(f'python -m packaging_tools.auto_package {self.autorest_result} {self.autorest_result}')

    def get_package_name_with_readme(self):
        generate_result = self.get_autorest_result()
        self.package_name = generate_result["packages"][0]["packageName"].split('-')[-1]

    def prepare_branch_with_readme(self):
        self.generate_code()
        self.get_package_name_with_readme()
        self.get_sdk_folder_with_readme()
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
        sdk_readme = str(Path(f'sdk/{self.sdk_folder}/{self.package_name}/README.md'))

        def edit_sdk_readme(content: List[str]):
            for i in range(0, len(content)):
                if content[i].find('MyService') > 0:
                    content[i] = content[i].replace('MyService', self.package_name.capitalize())

        modify_file(sdk_readme, edit_sdk_readme)

    def check_sdk_setup(self):
        sdk_setup = str(Path(f'sdk/{self.sdk_folder}/azure-mgmt-{self.package_name}/setup.py'))

        def edit_sdk_setup(content: List[str]):
            for i in range(0, len(content)):
                content[i] = content[i].replace('msrestazure>=0.4.32,<2.0.0', 'azure-mgmt-core>=1.3.0,<2.0.0')
                content[i] = content[i].replace('azure-mgmt-core>=1.2.0,<2.0.0', 'azure-mgmt-core>=1.3.0,<2.0.0')
                content[i] = content[i].replace('msrest>=0.5.0', 'msrest>=0.6.21')

        modify_file(sdk_setup, edit_sdk_setup)

    def check_pprint_name(self):
        path = str(Path(f'sdk/{self.sdk_folder}/azure-mgmt-{self.package_name}'))
        pprint_name = self.package_name.capitalize()

        def edit_file_for_pprint_name(content: List[str]):
            for i in range(0, len(content)):
                content[i] = content[i].replace('MyService', pprint_name)

        for file in os.listdir(path):
            if os.path.isfile(file):
                modify_file(file, edit_file_for_pprint_name)
        my_print(f' replace \"MyService\" with \"{pprint_name}\" successfully ')

    def get_all_files(self) -> List[str]:
        path = str(Path(f'sdk/{self.sdk_folder}/azure-mgmt-{self.package_name}'))
        files = []
        all_files(path, files)
        return files

    def judge_tag(self) -> bool:
        files = self.get_all_files()
        default_api_version = ''  # for multi-api
        api_version = ''  # for single-api
        for file in files:
            if '.py' not in file or '.pyc' in file:
                continue
            try:
                with open(file, 'r') as file_in:
                    list_in = file_in.readlines()
            except:
                _LOG.info(f'can not open {file}')
                continue

            for line in list_in:
                if line.find('DEFAULT_API_VERSION = ') > -1:
                    default_api_version += line.split('=')[-1].strip('\n')  # collect all default api version
                if default_api_version == '' and line.find('api_version = ') > -1:
                    api_version += line.split('=')[-1].strip('\n')  # collect all single api version
        if default_api_version != '':
            my_print(f'find default api version:{default_api_version}')
            return 'preview' in default_api_version
        my_print(f'find single api version:{api_version}')
        return 'preview' in api_version

    def calculate_next_version_proc(self, last_version: str):
        preview_tag = self.judge_tag()
        add_content = self.get_changelog()
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
            next_version = stable_version_plus(add_content, last_version) + preview_label + '1'
        else:
            next_version = stable_version_plus(add_content, last_version)

        return next_version

    def get_autorest_result(self) -> Dict[Any, Any]:
        with open(self.autorest_result, 'r') as file_in:
            content = json.load(file_in)
        return content

    def get_changelog(self) -> List[str]:
        content = self.get_autorest_result()
        return content["packages"][0]["changelog"]["content"].split('\n')

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
        files = self.get_all_files()

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
        path = str(Path(f'sdk/{self.sdk_folder}/azure-mgmt-{self.package_name}/CHANGELOG.md'))

        def edit_changelog_for_new_service_proc(content: List[str]):
            for i in range(0, len(content)):
                if '##' in content[i]:
                    content[i] = f'## {self.next_version}({current_time()})'
                    break

        modify_file(path, edit_changelog_for_new_service_proc)

    def edit_changelog(self):
        path = str(Path(f'sdk/{self.sdk_folder}/azure-mgmt-{self.package_name}/CHANGELOG.md'))

        def edit_changelog_proc(content: List[str]):
            add_content = ['\n', f'## {self.next_version} ({current_time()})\n\n']
            changelog = [item + '\n' for item in self.get_changelog()]
            add_content.extend(changelog)
            content[1:1] = add_content

        modify_file(path, edit_changelog_proc)

    def check_changelog_file(self):
        if self.next_version == '1.0.0b1':
            self.edit_changelog_for_new_service()
        else:
            self.edit_changelog()

    def check_ci_file_proc(self, dependency: str):
        path = str(Path('shared_requirements.txt'))

        def edit_ci_file(content: List[str]):
            new_line = f'#override azure-mgmt-{self.package_name} {dependency}'
            for i in range(len(content)):
                if new_line in content[i]:
                    return
            prefix = '' if '\n' in content[-1] else '\n'
            content.append(prefix + new_line + '\n')

        modify_file(path, edit_ci_file)
        print_exec('git add shared_requirements.txt')

    def check_ci_file(self):
        self.check_ci_file_proc('msrest>=0.6.21')
        self.check_ci_file_proc('azure-mgmt-core>=1.3.0,<2.0.0')

    def check_file(self):
        self.check_pprint_name()
        self.check_sdk_setup()
        self.check_version()
        self.check_changelog_file()
        self.check_ci_file()

    @return_origin_path
    def install_package_locally(self):
        setup_path = str(Path(f'sdk/{self.sdk_folder}/azure-mgmt-{self.package_name}'))
        os.chdir(setup_path)
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
        os.chdir(Path(f'sdk/{self.sdk_folder}/azure-mgmt-{self.package_name}'))
        succeeded_result = 'Live test success'
        failed_result = 'Live test fail, detailed info is in pipeline log(search keyword FAILED)!!!'
        try:
            print_check(f'pytest  --collect-only')
        except:
            my_print('live test run done, do not find any test !!!')
            self.test_result = succeeded_result
            return

        try:
            print_check(f'pytest -s')
        except:
            my_print('some test failed, please fix it locally')
            self.test_result = failed_result
        else:
            my_print('live test run done, do not find failure !!!')
            self.test_result = succeeded_result

    def run_test(self):
        self.prepare_test_env()
        self.run_test_proc()

    def create_pr_proc(self):
        api = GhApi(owner='Azure', repo='azure-sdk-for-python', token=self.usr_token)
        pr_title = "[AutoRelease] {}(Do not merge)".format(self.new_branch)
        pr_head = "{}:{}".format(os.getenv('USR_NAME'), self.new_branch)
        pr_base = 'main'
        pr_body = "{} \n{} \n{}".format(self.issue_link, self.test_result, self.pipeline_link)
        res_create = api.pulls.create(pr_title, pr_head, pr_base, pr_body)
        pr_number = res_create.number

        # Add issue link on PR
        api = GhApi(owner='Azure', repo='azure-sdk-for-python', token=self.bot_token)
        api.issues.create_comment(issue_number=pr_number, body='issue link:{}'.format(self.issue_link))

    def zero_version_policy(self):
        if self.next_version == '0.0.0':
            api_request = GhApi(owner='Azure', repo='sdk-release-request', token=self.bot_token)
            issue_number = self.issue_link.split('/')[-1]
            api_request.issues.add_labels(issue_number=int(issue_number), labels=['base-branch-attention'])

    # def get_package_encoded(self):
    #     content = self.get_autorest_result()
    #     package_path = content["packages"][0]["artifacts"][0]
    #     with open(package_path, 'rb') as file_in:
    #         package_content = file_in.read()
    #     return base64.b64encode(package_content)

    def upload_private_package_policy(self):
        pass

    def issue_comment(self):
        self.zero_version_policy()

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
