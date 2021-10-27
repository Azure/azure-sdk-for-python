import os
import sys
import subprocess as sp
import time
import argparse
import logging
from ghapi.all import GhApi


SERVICE_NAME = 'servicename'
SDK_FOLDER = 'servicename'
TRACK = '1'
VERSION_NEW = '0.0.0'
VERSION_LAST_RELEASE = '1.0.0b1'
BRANCH_BASE = ''
OUT_PATH = ''
NEW_BRANCH = ''

_LOG = logging.getLogger()


def my_print(cmd):
    _LOG.info(f'({SERVICE_NAME})==' + cmd + ' ==\n')


def print_exec(cmd):
    my_print(cmd)
    sp.call(cmd, shell=True)


def print_exec_output(cmd):
    my_print(cmd)
    return sp.getoutput(cmd).split('\n')


def print_check(cmd):
    my_print(cmd)
    sp.check_call(cmd, shell=True)


def find_report_name(result):
    pattern = 'written to'
    merged = 'merged_report'
    for line in result:
        idx = line.find(pattern)
        idx1 = line.find(merged)
        if idx > 0 and idx1 > 0:
            return line[idx + len(pattern):]

    for line in result:
        idx = line.find(pattern)
        if idx > 0:
            return line[idx + len(pattern):]

    return ''


def get_version(report):
    global VERSION_LAST_RELEASE
    pattern = 'code_reports/'
    idx1 = report.find(pattern)
    idx2 = report.find('/', idx1 + len(pattern))
    if idx2 > -1 and idx1 > -1:
        VERSION_LAST_RELEASE = report[idx1 + len(pattern):idx2]


def create_changelog_content():
    result1 = print_exec_output(f'python -m packaging_tools.code_report --last-pypi azure-mgmt-{SERVICE_NAME}')
    report1 = find_report_name(result1)
    result2 = print_exec_output(f'python -m packaging_tools.code_report azure-mgmt-{SERVICE_NAME}')
    report2 = find_report_name(result2)
    result = print_exec_output(f'python -m packaging_tools.change_log {report1} {report2}')
    if len(result) > 0:
        add_content = result[1:]
        get_version(report1)
    else:
        add_content = []

    return add_content


def judge_tag():
    path = f'{os.getcwd()}/sdk/{SDK_FOLDER}/azure-mgmt-{SERVICE_NAME}'
    files = []
    all_files(path, files)
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


def preview_version_plus(preview_label):
    num = VERSION_LAST_RELEASE.split(preview_label)
    num[1] = str(int(num[1]) + 1)
    return f'{num[0]}{preview_label}{num[1]}'


def stable_version_plus(add_content):
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


def edit_changelog(add_content):
    path = f'sdk/{SDK_FOLDER}/azure-mgmt-{SERVICE_NAME}'
    with open(f'{path}/CHANGELOG.md', 'r') as file_in:
        list_in = file_in.readlines()
    list_out = [list_in[0], '\n']
    date = time.localtime(time.time())
    list_out.append('## {} ({}-{:02d}-{:02d})\n\n'.format(VERSION_NEW, date.tm_year, date.tm_mon, date.tm_mday))
    for line in add_content:
        list_out.append(line + '\n')
    list_out.extend(list_in[1:])
    with open(f'{path}/CHANGELOG.md', 'w') as file_out:
        file_out.writelines(list_out)


def print_changelog(add_content):
    for line in add_content:
        _LOG.info('[CHANGELOG] ' + line)


def edit_file_setup():
    path = f'sdk/{SDK_FOLDER}/azure-mgmt-{SERVICE_NAME}'
    with open(f'{path}/setup.py', 'r') as file_in:
        list_in = file_in.readlines()
    for i in range(0, len(list_in)):
        list_in[i] = list_in[i].replace('msrestazure>=0.4.32,<2.0.0', 'azure-mgmt-core>=1.2.0,<2.0.0')
        list_in[i] = list_in[i].replace('msrest>=0.5.0', 'msrest>=0.6.21')
    with open(f'{path}/setup.py', 'w') as file_out:
        file_out.writelines(list_in)

    # avoid pipeline check fail
    with open(f'shared_requirements.txt', 'r') as file_in:
        list_in = file_in.readlines()
    new_line = f'#override azure-mgmt-{SERVICE_NAME} msrest>=0.6.21'
    for i in range(0, len(list_in)):
        if list_in[i].find(f'{new_line}') > -1:
            return
    list_in.append(f'{new_line}\n')
    with open(f'shared_requirements.txt', 'w') as file_out:
        file_out.writelines(list_in)


def edit_file_readme():
    path = f'sdk/{SDK_FOLDER}/azure-mgmt-{SERVICE_NAME}'
    # edit README
    with open(f'{path}/README.md', 'r') as file_in:
        list_in = file_in.readlines()
    for i in range(0, len(list_in)):
        if list_in[i].find('MyService') > 0:
            list_in[i] = list_in[i].replace('MyService', SERVICE_NAME.capitalize())
    with open(f'{path}/README.md', 'w') as file_out:
        file_out.writelines(list_in)


def edit_first_release():
    global VERSION_NEW
    VERSION_NEW = '1.0.0b1'
    # edit version.py
    path = f'sdk/{SDK_FOLDER}/azure-mgmt-{SERVICE_NAME}/azure/mgmt/{SERVICE_NAME}'
    file_name = 'version.py' if TRACK == '1' else '_version.py'
    print_check(f'cp {SCRIPT_PATH}/version.py {path}/{file_name}')

    # edit CHANGELOG.md
    with open(f'{SCRIPT_PATH}/CHANGELOG.md', 'r') as file_in:
        content = file_in.readlines()

    date = time.localtime(time.time())
    data_format = '{}-{:02d}-{:02d}'.format(date.tm_year, date.tm_mon, date.tm_mday)
    for i in range(0, len(content)):
        content[i] = content[i].replace('data_format', data_format)
    with open(f'sdk/{SDK_FOLDER}/azure-mgmt-{SERVICE_NAME}/CHANGELOG.md', 'w') as file_out:
        file_out.writelines(content)


def edit_file():
    from pypi import PyPIClient
    client = PyPIClient()
    try:
        client.get_ordered_versions(f'azure-mgmt-{SERVICE_NAME}')
    except:
        print_changelog(['* Initial Release'])
        edit_first_release()
        edit_file_readme()
        if TRACK == '2':
            edit_file_setup()
        my_print(f'CHANGELOG and version(new:{VERSION_NEW}) generate successfully. It is first release')
    else:
        add_content = create_changelog_content()
        if len(add_content) == 0:
            raise Exception('changelog and version generate failed, please do it manually')
        else:
            print_changelog(add_content)
            edit_version(add_content)
            edit_changelog(add_content)
            edit_file_readme()
            if TRACK == '2':
                edit_file_setup()
            my_print(f'CHANGELOG and version(new:{VERSION_NEW}) generate successfully, please check it(compare with '
                     f'{VERSION_LAST_RELEASE}[https://pypi.org/pypi/azure-mgmt-{SERVICE_NAME}/{VERSION_LAST_RELEASE}])')


def build_wheel():
    path = os.getcwd()
    setup_path = f'{path}/sdk/{SDK_FOLDER}/azure-mgmt-{SERVICE_NAME}'
    print_check(f'cd {setup_path} && python setup.py bdist_wheel')
    print_check(f'cd {path}')

    # check whether package can install
    print_check(f'python -c "import azure.mgmt.{SERVICE_NAME}"')
    print_check(f'python -m packaging_tools.code_report azure-mgmt-{SERVICE_NAME}')


def test_env_init():
    print_exec(f'pip install -r {SCRIPT_PATH}/livetest_package.txt')
    file = f'{SCRIPT_PATH}/livetest_package_{SERVICE_NAME}_track{TRACK}.txt'
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
    test_env_init()
    print_exec(f'python scripts/dev_setup.py -p azure-mgmt-{SERVICE_NAME}')
    # run live test
    try:
        print_check(f'pytest sdk/{SDK_FOLDER}/azure-mgmt-{SERVICE_NAME}/  --collect-only')
    except:
        my_print('live test run done, do not find any test !!!')
        return

    try:
        print_check(f'pytest -s sdk/{SDK_FOLDER}/azure-mgmt-{SERVICE_NAME}/')
    except:
        with open(f'{OUT_PATH}/live_test_fail.txt', 'w') as file_out:
            file_out.writelines([''])
        my_print('some test failed, please fix it locally')
    else:
        my_print('live test run done, do not find failure !!!')


# find all the files of one folder, including files in subdirectory
def all_files(path, files):
    all_folder = os.listdir(path)
    for folder in all_folder:
        if os.path.isdir(f'{path}/{folder}'):
            all_files(f'{path}/{folder}', files)
        else:
            files.append(f'{path}/{folder}')


def edit_useless_file():
    target_file = 'version.py'
    path = f'{os.getcwd()}/sdk/{SDK_FOLDER}/azure-mgmt-{SERVICE_NAME}'
    files = []
    all_files(path, files)
    for file in files:
        if target_file in file:
            with open(file, 'r') as file_in:
                list_in = file_in.readlines()
            for i in range(0, len(list_in)):
                if list_in[i].find('VERSION') > -1:
                    list_in[i] = f'VERSION = "{VERSION_NEW}"\n'
            with open(file, 'w') as file_output:
                file_output.writelines(list_in)


def commit_test():
    print_exec('git add sdk/')
    print_exec('git commit -m \"test"')
    print_exec('git push -f origin HEAD')
    my_print(f'== {SERVICE_NAME}(track{TRACK}) Automatic Release live test done !!! ==')


def init_env():
    print_exec(f'python scripts/dev_setup.py -p azure-mgmt-{SERVICE_NAME}')


def check_pprint_name():
    path = f'{os.getcwd()}/sdk/{SDK_FOLDER}/azure-mgmt-{SERVICE_NAME}'
    pprint_name = SERVICE_NAME.capitalize()
    for file in os.listdir(path):
        file_path = f'{path}/{file}'
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding="utf-8") as file_in:
                list_in = file_in.readlines()
            for i in range(0, len(list_in)):
                list_in[i] = list_in[i].replace('MyService', pprint_name)
            with open(file_path, 'w') as file_out:
                file_out.writelines(list_in)
    my_print(f' replace \"MyService\" with \"{pprint_name}\" successfully ')


def judge_sdk_folder():
    global SDK_FOLDER, TRACK
    from livetest_folder_link import FOLDER_LINK

    SDK_FOLDER = FOLDER_LINK[SERVICE_NAME] if SERVICE_NAME in FOLDER_LINK else SERVICE_NAME
    sdk_path = f'sdk/{SDK_FOLDER}/azure-mgmt-{SERVICE_NAME}'
    if not os.path.exists(sdk_path):
        raise Exception(f'{sdk_path} does not exist, please update livetest_folder_link.py')

    # additional rule to judge track1 or track2
    if os.path.exists('swagger_to_sdk_config_autorest.json'):
        with open('swagger_to_sdk_config_autorest.json', 'r') as file_in:
            content = file_in.readlines()
        for line in content:
            if line.find('azure-sdk-for-python-track2') > 0:
                TRACK = '2'
                break


def git_remote_add():
    global TRACK, NEW_BRANCH
    # init git
    print_exec('git checkout . && git clean -fd && git reset --hard HEAD ')
    print_exec('git remote add autosdk https://github.com/AzureSDKAutomation/azure-sdk-for-python.git')
    print_check(f'git fetch autosdk {BRANCH_BASE}')
    print_check(f'git checkout autosdk/{BRANCH_BASE}')


def create_branch():
    global NEW_BRANCH
    # create new branch
    t = time.time()
    d = time.localtime(t)
    NEW_BRANCH = 't{}-{}-{}-{:02d}-{:02d}-{}'.format(TRACK, SERVICE_NAME, d.tm_year, d.tm_mon, d.tm_mday, str(t)[-5:])
    print_exec(f'git checkout -b {NEW_BRANCH}')


def commit_file():
    print_exec('git add sdk/')
    print_exec('git add shared_requirements.txt')
    print_exec('git commit -m \"version,CHANGELOG\"')
    print_exec('git push -f origin HEAD')
    my_print(f'== {SERVICE_NAME}(track{TRACK}) Automatic Release file-edit done !!! ==')


def main():
    git_remote_add()
    judge_sdk_folder()
    create_branch()
    init_env()
    edit_file()
    edit_useless_file()
    check_pprint_name()
    commit_file()
    run_live_test()
    build_wheel()
    commit_test()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Auto release',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("branch", help="branch name")
    parser.add_argument("script_path", help="path where the script is")
    parser.add_argument("out_path", help="path where the output is")
    args = parser.parse_args()

    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.INFO)

    BRANCH_BASE = args.branch.replace('AzureSDKAutomation:', '')
    SCRIPT_PATH = args.script_path
    OUT_PATH = args.out_path

    # extract info
    sys.path.append(OUT_PATH)
    TRACK = '2' if BRANCH_BASE.find('track2_') > -1 else '1'
    SERVICE_NAME = BRANCH_BASE.replace('sdkAuto/', '').replace('sdkAutomation/', '').replace('track2_', '').replace(
        'azure-mgmt-', '')
    try:
        main()
    except Exception as e:
        my_print(e)
    except sp.CalledProcessError as e:
        my_print(e)
    else:
        with open(f'{OUT_PATH}/output.txt', 'w') as file_out:
            file_out.writelines([f'{NEW_BRANCH}\n', "main\n" if TRACK == '2' else 'release/v3\n'])

