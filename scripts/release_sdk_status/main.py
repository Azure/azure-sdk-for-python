import requests
import re
import os
import glob
from lxml import etree
import lxml.html
import subprocess as sp
from typing import List, Dict
from github import Github
from github.Repository import Repository
import time
from packaging.version import parse
from pathlib import Path

from util import add_certificate

MAIN_REPO_SWAGGER = 'https://github.com/Azure/azure-rest-api-specs/tree/main'
PR_URL = 'https://github.com/Azure/azure-rest-api-specs/pull/'
FAILED_RESULT = []
SKIP_TEXT = '-, -, -, -\n'

def my_print(cmd):
    print('== ' + cmd + ' ==\n')


def print_check(cmd, path=''):
    my_print(cmd)
    if path:
        sp.check_output(cmd, shell=True, cwd=path)
    else:
        sp.check_call(cmd, shell=True)


def print_call(cmd):
    my_print(cmd)
    sp.call(cmd, shell=True)


def version_sort(versions: List[str]) -> List[str]:
    versions_package = [parse(version) for version in versions]
    versions_package.sort()
    return [str(version) for version in versions_package]


class PyPIClient:
    def __init__(self, host="https://pypi.org", package_name='', track_config='',
                 readme_link='', rm_link='', cli_version='', multi_api=''):
        self._host = host
        self._session = requests.Session()
        self._package_name = package_name
        self.version_date_dict = {}
        self.whether_track2 = None  # whether published track2 to pypi
        self.track1_ga_version = 'NA'
        self.track1_latest_version = 'NA'
        self.track2_ga_version = 'NA'
        self.track2_latest_version = 'NA'
        self.pypi_link = 'NA'
        self.track_config = track_config
        self.readme_link = readme_link
        self.rm_link = rm_link
        self.cli_version = cli_version
        self.bot_warning = ''
        self.multi_api = multi_api
        self.package_size = ''  # Byte

    def get_package_name(self):
        return self._package_name

    def project_html(self, folder: str):
        self.pypi_link = "{host}/pypi/{project_name}".format(
            host=self._host,
            project_name=self._package_name
        )
        response = self._session.get(self.pypi_link + folder)

        return response

    def get_release_info(self, response, xpath, type):
        DATE_DICT = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                     'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12', }
        text = response.text
        parse_text = lxml.etree.HTML(text)
        release_info = parse_text.xpath(xpath)
        strip_info = []
        for info in release_info:
            info = info.strip()
            if type == 'date':
                info = info.replace(',', '').split(' ')
                info = info[2] + '/' + DATE_DICT[info[0]] + '/' + info[1]
            if not len(info) == 0:
                strip_info.append(info)

        return strip_info

    def get_latest_package_size(self):
        response = self.project_html("/json")
        try:
            response.raise_for_status()
            result = response.json()
            version = self.track2_latest_version if self.track2_latest_version != 'NA' else self.track1_latest_version
            self.package_size = result['releases'][version][0]['size']
        except:
            self.package_size = 'failed'

    def get_release_dict(self, response):
        version_list = self.get_release_info(response, xpath='//p[@class="release__version"]/text()', type='version')
        self.version_handler(version_list)
        data_list = self.get_release_info(response, xpath='//p[@class="release__version-date"]/time/text()',
                                          type='date')
        self.version_date_dict = dict(zip(version_list, data_list))
        self.version_date_dict['NA'] = 'NA'

        self.get_latest_package_size()

    def output_package_size(self) -> str:
        if isinstance(self.package_size, int):
            return '%.3f' % float(self.package_size / 1024 / 1024)
        else:
            return self.package_size

    def write_to_list(self, sdk_folder: str) -> str:
        response = self.project_html("/#history")
        if 199 < response.status_code < 400:
            self.get_release_dict(response)
            self.bot_analysis()
            return '{sdk_folder}/{package_name},{pypi_link},{track1_latest_version},{track1_latest_release_date},' \
                   '{track1_ga_version},{track2_latest_version},{track2_latest_release_date},{track2_ga_version},' \
                   '{cli_version},{track_config},{bot},{readme_link},{multiapi},{whl_size},'.format(
                        sdk_folder=sdk_folder.split('/')[0],
                        package_name=self._package_name,
                        pypi_link=self.pypi_link,
                        track1_latest_version=self.track1_latest_version,
                        track1_latest_release_date=self.version_date_dict[self.track1_latest_version],
                        track1_ga_version=self.track1_ga_version,
                        track2_latest_version=self.track2_latest_version,
                        track2_latest_release_date=self.version_date_dict[self.track2_latest_version],
                        track2_ga_version=self.track2_ga_version,
                        cli_version=self.cli_version,
                        track_config=self.track_config,
                        bot=self.bot_warning,
                        readme_link=self.rm_link,
                        multiapi=self.multi_api,
                        whl_size=self.output_package_size())
        else:
            self.pypi_link = 'NA'
        return ''

    def find_track1_ga_version(self, versions: List[str]) -> None:
        if '1.0.0' in versions:
            self.track1_ga_version = '1.0.0'

    def find_track2_ga_version(self, versions: List[str]) -> None:
        for version in versions:
            if re.search(r'[a-zA-z]', version) is None:
                self.track2_ga_version = version
                break

    def handle_cli_version(self, track1_versions: List[str], track2_versions: List[str]) ->None:
        if self.cli_version == 'NA':
            return
        if self.cli_version in track1_versions:
            self.cli_version = 'track1_' + self.cli_version
        elif self.cli_version in track2_versions:
            self.cli_version = 'track2_' + self.cli_version
        else:
            my_print(f'do not find cli_version {self.cli_version} in track1 versions {str(track1_versions)} and '
                     f'track2 versions {str(track2_versions)}')

    def get_track1_track2_versions(self, versions: List[str]) -> (List[str], List[str]):
        first_track2_version = ''
        for version in versions:
            if 'b' in version:
                first_track2_version = version
                my_print(f'get first track2 version {version} in {versions}')
                break

        # azure-mgmt-streamanalytics set 1.0.0rc1 as first track2 version
        if self.get_package_name() == 'azure-mgmt-streamanalytics':
            first_track2_version = '1.0.0rc1'

        if first_track2_version:
            idx = versions.index(first_track2_version)
            return versions[0:idx], versions[idx:]
        else:
            return versions, []

    def version_handler(self, version_list: List[str]):
        versions_sorted = version_sort(version_list)
        track1_versions, track2_versions = self.get_track1_track2_versions(versions_sorted)
        self.find_track1_ga_version(track1_versions)
        self.find_track2_ga_version(track2_versions)
        self.handle_cli_version(track1_versions, track2_versions)
        self.track1_latest_version = self.track1_latest_version if len(track1_versions) == 0 else track1_versions[-1]
        self.track2_latest_version = self.track2_latest_version if len(track2_versions) == 0 else track2_versions[-1]

    def bot_analysis(self):
        # rule 1: readme.python.md must exist
        # rule 2: track1 config must be deleted if azure-cli doesn't use track1
        # rule 3: track2 config must be added if track2 package has been published to pypi
        if self.readme_link == 'NA':
            self.bot_warning += 'The readme.python.md has not been created.  '
        if self.cli_version != 'NA':
            cli_version = int(self.cli_version.split('_')[1].split('.')[0])
            if self.whether_track2 is not None:
                whether_track2 = int(self.whether_track2.split('.')[0])
                if cli_version >= whether_track2 and self.track_config == 'both':
                    self.bot_warning += 'The cli using track2 now but readme.python still have track1 config.'
        if self.whether_track2 and self.track_config == 'track1':
            self.bot_warning += 'Need to add track2 config.'


def sdk_info_from_pypi(sdk_info: List[Dict[str, str]], cli_dependency):
    all_sdk_status = []
    add_certificate(str(Path('../venv-sdk/lib/python3.8/site-packages/certifi/cacert.pem')))
    for package in sdk_info:
        sdk_name = package['package_name']
        if sdk_name in cli_dependency.keys():
            cli_version = cli_dependency[sdk_name]
        else:
            cli_version = 'NA'
        track_config = package['track_config']
        readme_link = package['readme_python_path']
        rm_link = package['readme_html']
        multi_api = package['multi_api']
        pypi_ins = PyPIClient(package_name=sdk_name, track_config=track_config,
                              readme_link=readme_link, rm_link=rm_link, cli_version=cli_version, multi_api=multi_api)
        sdk_folder = package['sdk_folder']
        text_to_write = pypi_ins.write_to_list(sdk_folder)
        service_name = package['service_name']
        if pypi_ins.pypi_link != 'NA':
            test_result = SKIP_TEXT
            try:
                test_result = run_playback_test(service_name, sdk_folder)
            except:
                print(f'[Error] fail to play back test recordings: {sdk_name}')
            text_to_write += test_result
            all_sdk_status.append(text_to_write)

    my_print(f'total pypi package kinds: {len(all_sdk_status)}')
    return all_sdk_status


def get_test_result(txt_path):
    with open(txt_path, 'r+') as f:
        coverage = ' - '
        for line in f.readlines():
            if 'TOTAL' in line:
                coverage = line.split()[3]
            if '=====' in line and ('passed' in line or 'failed' in line or 'skipped' in line):
                # print(line)
                passed, failed, skipped = 0, 0, 0
                if 'passed' in line:
                    passed = re.findall('(\d{1,2}) passed', line)[0]
                if 'failed' in line:
                    failed = re.findall('(\d{1,2}) failed', line)[0]
                if 'skipped' in line:
                    skipped = re.findall('(\d{1,2}) skipped', line)[0]
                # print(f'{passed} {failed} {skipped}')

    return f'{coverage}, {passed}, {failed}, {skipped}\n'


def run_playback_test(service_name: str, sdk_folder: str):
    if os.getenv('SKIP_COVERAGE') in ('true', 'yes'):
        return SKIP_TEXT

    # eg: coverage_path='$(pwd)/sdk-repo/sdk/containerregistry/azure-mgmt-containerregistry/azure/mgmt/containerregistry/'
    coverage_path = ''.join([os.getenv('SDK_REPO'), '/sdk/', sdk_folder])
    service_path = coverage_path.split('/azure/mgmt')[0]
    test_path = service_path + '/tests'
    if os.path.exists(test_path):
        print_check('pip install -r dev_requirements.txt', path=service_path)
        print_check('pip install -e .', path=service_path)
        # print_check('python setup.py install', path=service_path)
        if os.path.exists(coverage_path+'/operations') and os.path.exists(coverage_path+'/models'):
            operations_path = coverage_path+'/operations'
            models_path = coverage_path+'/models'
            try:
                start_time = int(time.time())
                print_check(f'pytest -s tests --cov={operations_path} --cov={models_path} >result.txt', path=service_path)
                cost_time = int(time.time()) - start_time
                my_print(f'{service_name} play_back cost {cost_time} seconds({cost_time // 60} minutes)')
            except Exception as e:
                print(f'{service_name} test ERROR')
                return '-, 0, 0, 0\n'
        else:
            try:
                print_check(f'pytest -s tests >result.txt', path=service_path)
            except Exception as e:
                return '-, 0, 0, 0\n'
        if os.path.exists(service_path+'/result.txt'):
            return get_test_result(service_path+'/result.txt')

    return SKIP_TEXT


def write_to_csv(sdk_status_list, csv_name):
    with open(csv_name, 'w') as file_out:
        file_out.write('foler/package name,'
                       'pypi link,'
                       'latest track1 version,'
                       'latest track1 release date,'
                       'track1 GA version,'
                       'latest track2 version,'
                       'latest track2 release date,'
                       'track2 GA version,'
                       'cli dependency,'
                       'readme config,'
                       'bot advice,'
                       'readme link,'
                       'multi api,'
                       'whl size(MB),'
                       'test coverage,'
                       'passed,'
                       'failed,'
                       'skipped\n')
        file_out.writelines(
            [package for package in sorted(sdk_status_list, key=lambda x: x.split(',')[10], reverse=True)])


def complement_version(version: str) -> str:
    num = version.count('.')
    if num == 0:
        return f'{version}.0.0'
    elif num == 1:
        return f'{version}.0'
    return version


def get_cli_dependency():
    g = Github(os.getenv('TOKEN'))  # please fill user_token
    repo = g.get_repo('Azure/azure-cli')
    cli_lines = repo.get_contents('src/azure-cli/setup.py').decoded_content.decode('UTF-8').split('\n')
    cli_dependency = {}
    for line in cli_lines:
        if 'azure-mgmt-' in line:
            name_pattern = re.compile(r'azure-mgmt-[a-zA-z\-]+')
            version_pattern = re.compile(r'\d+[\.\da-z]+')
            name = name_pattern.search(line).group(0)
            version = version_pattern.search(line).group(0)
            cli_dependency[name] = complement_version(version)
    return cli_dependency


def project_html(url):
    response = requests.Session().get(url)
    response.encoding = 'gbk'
    text = response.text
    parse_result = lxml.etree.HTML(text)
    return parse_result


def read_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as file_in:
        content = file_in.readlines()
    return content


def find_test_path(line: str) -> str:
    line = line.strip('\n') + '\n'
    try:
        return re.findall('output-folder: \$\(python-sdks-folder\)/(.*?)\n', line)[0]
    except:
        FAILED_RESULT.append('[Fail to find sdk path] ' + line)
        return ''


def sdk_info_from_swagger() -> List[Dict[str, str]]:
    sdk_name_re = re.compile(r'azure-mgmt-[a-z]+-*([a-z])+')
    sdk_folder_re = re.compile('output-folder: \$\(python-sdks-folder\)/')
    resource_manager = []
    SWAGGER_FOLDER = os.getenv('SWAGGER_REPO')
    target_file_pattern = str(Path(f'{SWAGGER_FOLDER}/specification/*/resource-manager/readme.md'))
    readme_folders = glob.glob(target_file_pattern)
    my_print(f'total readme folders: {len(readme_folders)}')
    for folder in readme_folders:
        sdk_folder = ''
        multi_api = ''
        linux_folder = Path(folder).as_posix()
        service_name = re.findall(r'specification/(.*?)/resource-manager/', linux_folder)[0]
        track_config = 0
        package_name = ''
        folder = folder.replace('readme.md', '')
        readme_python = 'NA' if 'readme.python.md' not in os.listdir(folder) else f'{folder}readme.python.md'
        readme_text = read_file(folder + 'readme.md')
        for line in readme_text:
            if line.find('azure-sdk-for-python-track2') > -1:
                track_config += 2
            elif line.find('azure-sdk-for-python') > -1:
                track_config += 1
            if readme_python == 'NA' and sdk_name_re.search(line) is not None and package_name == '':
                package_name = sdk_name_re.search(line).group()
            if sdk_folder_re.search(line) and not sdk_folder:
                sdk_folder = find_test_path(line)

        if readme_python != 'NA':
            readme_python_text = read_file(readme_python)
            for text in readme_python_text:
                if sdk_name_re.search(text) is not None:
                    package_name = sdk_name_re.search(text).group()
                if sdk_folder_re.search(text) and not sdk_folder:
                    sdk_folder = find_test_path(text)
                if 'batch:' in text and multi_api == '':
                    multi_api = 'fake'
                    print(f'*********{service_name} is fake ')
                if 'multiapiscript: true' in text:
                    multi_api = 'True'

        TRACK_CONFIG = {0: 'NA', 1: 'track1', 2: 'track2', 3: 'both'}
        track_config = TRACK_CONFIG.get(track_config, 'Rule error')
        readme_html = folder.replace(SWAGGER_FOLDER, MAIN_REPO_SWAGGER)
        readme_html = Path(readme_html).as_posix()
        if package_name != '':
            resource_manager.append({
                'package_name': package_name.strip(),
                'track_config': track_config,
                'readme_python_path': readme_python.strip(),
                'readme_html': readme_html.strip(),
                'multi_api': multi_api.strip(),
                'sdk_folder': sdk_folder.strip(),  # eg: resources/azure-mgmt-resource/azure/mgmt/resource
                'service_name': service_name,
            })
        my_print(f'{folder} : {package_name}')

    my_print(f'total package kinds: {len(resource_manager)}')

    return resource_manager


def commit_to_github():
    print_call('git add .')
    print_call('git commit -m \"update excel\"')
    print_call('git push -f origin HEAD')


def get_latest_pr_from_readme(rest_repo: Repository, service_html: str):
    commit_url = service_html.split('main/')[-1]
    commits = rest_repo.get_commits(path=commit_url)
    latest_commit = None
    for commit in commits:
        latest_commit = commit
        break
    latest_pr_brief = latest_commit.commit.message
    latest_pr_number = re.findall('\(\#[0-9]+\)', latest_pr_brief)
    latest_pr_number_int = []
    for number in latest_pr_number:
        number = int(re.search('\d+', number).group())
        latest_pr_number_int.append(number)
    latest_pr_number_int.sort()

    return latest_pr_number_int[-1]


def log_failed():
    print('\n'.join(FAILED_RESULT))


def main():
    cli_dependency = get_cli_dependency()
    sdk_info = sdk_info_from_swagger()
    all_sdk_status = sdk_info_from_pypi(sdk_info, cli_dependency)

    out_file = 'release_sdk_status.csv'
    write_to_csv(all_sdk_status, out_file)
    commit_to_github()

    log_failed()


if __name__ == '__main__':
    main()
