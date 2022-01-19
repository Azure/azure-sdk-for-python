import os
import subprocess as sp
import logging
from ghapi.all import GhApi
from pathlib import Path
import json
from typing import List, Any
from glob import glob
import time
from util import add_certificate
from pypi import PyPIClient

SERVICE_NAME = 'servicename'
SDK_FOLDER = 'servicename'
TRACK = '1'
VERSION_NEW = '0.0.0'
VERSION_LAST_RELEASE = '1.0.0b1'
BRANCH_BASE = ''
OUT_PATH = ''
NEW_BRANCH = ''
USER_REPO = ''

_LOG = logging.getLogger()


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


def preview_version_plus(preview_label: str) -> str:
    num = VERSION_LAST_RELEASE.split(preview_label)
    num[1] = str(int(num[1]) + 1)
    return f'{num[0]}{preview_label}{num[1]}'


def stable_version_plus(add_content: List[str]):
    flag = [False, False, False]  # breaking, feature, bugfix
    for line in add_content:
        if line.find('**Breaking changes**') > -1:
            flag[0] = True
            break
        elif line.find('**Features**') > -1:
            flag[1] = True
        elif line.find('**Bugfixes**') > -1:
            flag[2] = True
    num = VERSION_LAST_RELEASE.split('.')
    if flag[0]:
        return f'{int(num[0]) + 1}.0.0'
    elif flag[1]:
        return f'{num[0]}.{int(num[1]) + 1}.0'
    elif flag[2]:
        return f'{num[0]}.{num[1]}.{int(num[2]) + 1}'
    else:
        return '0.0.0'


def edit_version(add_content):
    global VERSION_NEW

    preview_tag = judge_tag()
    preview_version = 'rc' in VERSION_LAST_RELEASE or 'b' in VERSION_LAST_RELEASE
    #                                           |   preview tag                     | stable tag
    # preview version(1.0.0rc1/1.0.0b1)         | 1.0.0rc2(track1)/1.0.0b2(track2)  |  1.0.0
    # stable  version (1.0.0) (breaking change) | 2.0.0rc1(track1)/2.0.0b1(track2)  |  2.0.0
    # stable  version (1.0.0) (feature)         | 1.1.0rc1(track1)/1.1.0b1(track2)  |  1.1.0
    # stable  version (1.0.0) (bugfix)          | 1.0.1rc1(track1)/1.0.1b1(track2)  |  1.0.1
    preview_label = 'rc' if TRACK == '1' else 'b'
    if preview_version and preview_tag:
        VERSION_NEW = preview_version_plus(preview_label)
    elif preview_version and not preview_tag:
        VERSION_NEW = VERSION_LAST_RELEASE.split(preview_label)[0]
    elif not preview_version and preview_tag:
        VERSION_NEW = stable_version_plus(add_content) + preview_label + '1'
    else:
        VERSION_NEW = stable_version_plus(add_content)

    # additional rule for track1: if version is 0.x.x, next version is 0.x+1.0
    if TRACK == '1' and VERSION_LAST_RELEASE[0] == '0':
        num = VERSION_LAST_RELEASE.split('.')
        VERSION_NEW = f'{num[0]}.{int(num[1]) + 1}.0'
    # '0.0.0' means there must be abnormal situation
    if VERSION_NEW == '0.0.0':
        api_request = GhApi(owner='Azure', repo='sdk-release-request', token=os.getenv('UPDATE_TOKEN'))
        link = os.getenv('ISSUE_LINK')
        issue_number = link.split('/')[-1]
        api_request.issues.add_labels(issue_number=int(issue_number), labels=['base-branch-attention'])











def livetest_env_init():
    file = f'{SCRIPT_PATH}/livetest_package_{PACKAGE_NAME}_track{TRACK}.txt'
    if os.path.exists(file):
        print_exec(f'pip install -r {file}')
    else:
        my_print(f'{file} does not exist')

    # edit mgmt_settings_real.py
    with open(f'{SCRIPT_PATH}/mgmt_settings_real_.py', 'r') as file_in:
        list_in = file_in.readlines()

    ENV_TENANT_ID = os.environ['TENANT_ID']
    ENV_CLIENT_ID = os.environ['CLIENT_ID']
    ENV_CLIENT_SECRET = os.environ['CLIENT_SECRET']
    ENV_SUBSCRIPTION_ID = os.environ['SUBSCRIPTION_ID']

    for i in range(0, len(list_in)):
        list_in[i] = list_in[i].replace('ENV_TENANT_ID', ENV_TENANT_ID)
        list_in[i] = list_in[i].replace('ENV_CLIENT_ID', ENV_CLIENT_ID)
        list_in[i] = list_in[i].replace('ENV_CLIENT_SECRET', ENV_CLIENT_SECRET)
        list_in[i] = list_in[i].replace('ENV_SUBSCRIPTION_ID', ENV_SUBSCRIPTION_ID)

    with open('tools/azure-sdk-tools/devtools_testutils/mgmt_settings_real.py', 'w') as file_out:
        file_out.writelines(list_in)


def run_live_test():
    livetest_env_init()
    print_exec(f'python scripts/dev_setup.py -p azure-mgmt-{PACKAGE_NAME}')
    # run live test
    try:
        print_check(f'pytest sdk/{SDK_FOLDER}/azure-mgmt-{PACKAGE_NAME}/  --collect-only')
    except:
        my_print('live test run done, do not find any test !!!')
        return

    try:
        print_check(f'pytest -s sdk/{SDK_FOLDER}/azure-mgmt-{PACKAGE_NAME}/')
    except:
        with open(f'{OUT_PATH}/live_test_fail.txt', 'w') as file_out:
            file_out.writelines([''])
        my_print('some test failed, please fix it locally')
    else:
        my_print('live test run done, do not find failure !!!')


# find all the files of one folder, including files in subdirectory
def all_files(path: str, files: List[str]):
    all_folder = os.listdir(path)
    for item in all_folder:
        folder = str(Path(f'{path}/{item}'))
        if os.path.isdir(folder):
            all_files(folder, files)
        else:
            files.append(folder)




def commit_test():
    print_exec('git add sdk/')
    print_exec('git commit -m \"test"')
    print_exec('git push -f origin HEAD')
    my_print(f'== {PACKAGE_NAME}(track{TRACK}) Automatic Release live test done !!! ==')


def init_env():
    print_exec(f'python scripts/dev_setup.py -p azure-mgmt-{PACKAGE_NAME}')








def git_clean():
    print_exec('git checkout . && git clean -fd && git reset --hard HEAD ')



def commit_file():
    print_exec('git add sdk/')
    print_exec('git add shared_requirements.txt')
    print_exec('git commit -m \"version,CHANGELOG\"')
    print_exec('git push -f origin HEAD')
    my_print(f'== {PACKAGE_NAME}(track{TRACK}) Automatic Release file-edit done !!! ==')






def checkout_azure_default_branch():
    print_exec('git remote add Azure https://github.com/Azure/azure-sdk-for-python.git')
    print_check('git fetch Azure main')
    print_check('git checkout Azure/main')


def modify_file(file_path: str, func: Any):
    with open(file_path, 'r') as file_in:
        content = file_in.readlines()
    func(content)
    with open(file_path, 'w') as file_out:
        file_out.writelines(content)


def current_time():
    date = time.localtime(time.time())
    return '{}-{:02d}-{:02d}'.format(date.tm_year, date.tm_mon, date.tm_mday)


def get_latest_commit_in_swagger_repo() -> str:
    current_folder = os.getcwd()
    os.chdir(Path(os.getenv('SPEC_REPO')))
    head_sha = print_exec_output('git rev-parse HEAD')[0]
    os.chdir(current_folder)
    return head_sha


class CodegenTestPR:
    """
    This class can generate SDK code, run live test and create RP
    """

    def __init__(self):
        self.spec_readme = os.getenv('SPEC_README', '')
        self.package_name = ''
        self.new_branch = ''
        self.sdk_folder = ''  # 'compute' in 'sdk/compute/azure-mgmt-dns'
        self.autorest_result = ''
        self.next_version = ''

    def readme_local_folder(self) -> Path:
        html_link = 'https://github.com/Azure/azure-rest-api-specs/blob/main/'
        return Path(self.spec_readme.replace(html_link, '')) / 'readme.md'

    def get_sdk_folder_with_readme(self):
        with open(self.autorest_result, 'r') as file:
            generate_result = json.load(file)
        self.sdk_folder = generate_result["packages"][0]["path"][0].split('/')[-1]

    def generate_code(self):
        checkout_azure_default_branch()

        # prepare input data
        input_data = {
            'headSha': get_latest_commit_in_swagger_repo(),
            'repoHttpsUrl': "https://github.com/Azure/azure-rest-api-specs",
            'specFolder': os.getenv('SPEC_REPO'),
            'relatedReadmeMdFiles': [str(self.readme_local_folder())]
        }
        temp_folder = Path(os.getenv('TEMP_FOLDER'))
        self.autorest_result = str(temp_folder / 'temp.json')
        with open(self.autorest_result, 'w') as file:
            json.dump(input_data, file)

        # generate code
        print_exec('python scripts/dev_setup.py -p azure-core')
        print_check(f'python -m packaging_tools.auto_codegen {self.autorest_result} {self.autorest_result}')
        print_check(f'python -m packaging_tools.auto_package {self.autorest_result} {self.autorest_result}')

    def get_package_name_with_readme(self):
        with open(self.autorest_result, 'r') as file:
            generate_result = json.load(file)
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
        git_clean()
        if self.spec_readme:
            self.prepare_branch_with_readme()
        else:
            self.prepare_branch_with_base_branch()

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
            if '.py' not in file:
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
            next_version = preview_version_plus(preview_label)
        elif preview_version and not preview_tag:
            next_version = last_version.split(preview_label)[0]
        elif not preview_version and preview_tag:
            next_version = stable_version_plus(add_content) + preview_label + '1'
        else:
            next_version = stable_version_plus(add_content)

        # '0.0.0' means there must be abnormal situation
        if next_version == '0.0.0':
            api_request = GhApi(owner='Azure', repo='sdk-release-request', token=os.getenv('UPDATE_TOKEN'))
            link = os.getenv('ISSUE_LINK')
            issue_number = link.split('/')[-1]
            api_request.issues.add_labels(issue_number=int(issue_number), labels=['base-branch-attention'])

        return next_version

    def get_changelog(self) -> List[str]:
        with open(self.autorest_result, 'r') as file_in:
            content = json.load(file_in)
        return content["packages"][0]["changelog"]["content"].split('\n')

    def get_last_release_version(self) -> str:
        client = PyPIClient()
        try:
            versions = client.get_ordered_versions(f'azure-mgmt-{self.package_name}')
        except:
            return ''
        return str(versions[-1])

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

    def check_ci_file(self):
        self.check_ci_file_proc('msrest>=0.6.21')
        self.check_ci_file_proc('azure-mgmt-core>=1.3.0,<2.0.0')

    def check_file(self):
        self.check_pprint_name()
        self.check_sdk_setup()
        self.check_version()
        self.check_changelog_file()
        self.check_ci_file()

    def run_test(self):
        pass

    def create_pr(self):
        pass

    def run(self):
        self.prepare_branch()
        self.check_file()
        self.run_test()
        self.create_pr()

        # add_certificate()
        # init_env()
        # edit_file()
        # edit_useless_file()
        # check_pprint_name()
        # commit_file()
        # run_live_test()
        # build_wheel()
        # commit_test()


if __name__ == '__main__':
    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.INFO)

    instance = CodegenTestPR()
    instance.run()
