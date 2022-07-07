import os
import re
from glob import glob
from pathlib import Path
from typing import Set, List
from subprocess import check_call, call


def print_check(cmd: str):
    check_call(cmd, shell=True)


def print_exec(cmd: str):
    call(cmd, shell=True)


def step_into_rest_repo():
    os.chdir(str(Path(os.getcwd()) / 'azure-rest-api-specs'))


def git_clean():
    print_check('git checkout .')
    print_check('git clean -fd')
    print_check('git reset --hard HEAD')


class MultiApiConfigHelper:
    """
    This class can generate private SDK package
    """

    def __init__(self):
        self.service_name = ''
        self.tag = ''
        self.tag_files = {}  # Dict[str, List(str)]
        self.configured_files = set()  # Set[str]

    def get_input(self):
        print('Please commit your code before execute this script!!!')
        self.service_name = input('Please input your target service link(e.g. '
                                  '"https://github.com/Azure/azure-rest-api-specs/blob/main/specification/applicationinsights/resource-manager" '
                                  'or "applicationinsights"):\n')
        if 'resource-manager' in self.service_name:
            self.service_name = self.service_name.split('/')[-2]
        tag = input('Please input your target tag(e.g. "Readme Tag: package-2022-01-11" or "package-2022-01-11"):\n')
        self.tag = tag.split(':')[-1].strip()

    @staticmethod
    def checkout_main_branch():
        step_into_rest_repo()
        git_clean()
        usr = 'Azure'
        branch = 'main'
        print_exec(f'git remote add {usr} https://github.com/{usr}/azure-rest-api-specs.git')
        print_check(f'git fetch {usr} {branch}')
        print_check(f'git checkout {usr}/{branch}')

    def step_into_service_folder(self):
        root_path = os.getcwd()
        target_service_info = f'{root_path}/specification/{self.service_name}/resource-manager'
        result = glob(target_service_info)
        if len(result) == 0:
            raise Exception(f'do not find {target_service_info}')
        elif len(result) > 1:
            raise Exception(f'find multi target folder: {str(result)}')
        os.chdir(str(Path(result[0])))

    @staticmethod
    def judge_tag(line: str) -> bool:
        # ``` yaml $(tag) == 'package-2021-11-01'
        elements = ['```', 'tag', '==', 'package-']
        result = [re.search(element, line) for element in elements]
        return all(result)

    @staticmethod
    def get_tags(line: str) -> Set[str]:
        # extract 'package-2021-11-01' from "``` yaml $(tag) == 'package-2021-11-01'"
        result = re.findall("[\'\"][^\'^\"]+[\'\"]", line)
        if not result:
            raise Exception(f'Can not find valid tag name in {line}')
        return {item[1:-1] for item in result}

    @staticmethod
    def get_file_name(line: str) -> str:
        #   - Microsoft.Insights/stable/2015-05-01/aiOperations_API.json
        if '.json' in line and 'Microsoft.' in line:
            line = line.strip('\n ')
            line = line[1:] if line[0] == '-' else line
            return line.strip()
        return ''

    def get_tag_and_file(self, content: List[str], start_idx: int) -> int:
        tags_name = self.get_tags(content[start_idx])
        end_idx = start_idx
        for end_idx in range(start_idx + 1, len(content)):
            if '```' in content[end_idx]:
                break

        files = []
        for idx in range(start_idx + 1, end_idx):
            file_name = self.get_file_name(content[idx])
            if file_name:
                files.append(file_name)
        for tag_name in tags_name:
            if not self.tag_files.get(tag_name) and files:
                self.tag_files[tag_name] = files
        return end_idx + 1

    def get_all_tag_files(self):
        with open('readme.md', 'r') as file_in:
            content = file_in.readlines()

        i = 0
        while i < len(content):
            if self.judge_tag(content[i]):
                i = self.get_tag_and_file(content, i)
            else:
                i += 1

    @staticmethod
    def judge_config(line: str) -> bool:
        return 'batch' in line

    @staticmethod
    def get_configured_tag_name(line: str) -> str:
        # '  - tag: package-2017-10'
        if 'multiapiscript' in line:
            return ''
        return line.split('tag:')[-1].strip('\n ')

    def get_configured_tags(self, content: List[str], start_idx: int, tags: List[str]):
        end_idx = start_idx
        for end_idx in range(start_idx + 1, len(content)):
            if '```' in content[end_idx]:
                break

        for idx in range(start_idx + 1, end_idx):
            tag_name = self.get_configured_tag_name(content[idx])
            if tag_name:
                tags.append(tag_name)

    def get_configured_files(self):
        with open('readme.python.md', 'r') as file_in:
            content = file_in.readlines()

        configured_files = []
        configured_tags = []
        for i in range(len(content)):
            if self.judge_config(content[i]):
                self.get_configured_tags(content, i, configured_tags)
                break
        for tag in configured_tags:
            if tag not in self.tag_files:
                raise Exception(f'find {tag} in readme.python.md but it is not in readme.md!')
            configured_files.extend(self.tag_files[tag])

        self.configured_files = set(configured_files)

    def get_missing_files(self):
        missing_files = []
        if self.tag not in self.tag_files:
            raise Exception(f'Do not find \"{self.tag}\" in \"{self.service_name}/readme.md\"'
                            f'({str(self.tag_files.keys())})')
        print(f'find the following tiles in {self.tag}:')
        for file_name in self.tag_files[self.tag]:
            print(file_name)
            if file_name not in self.configured_files:
                missing_files.append('  - ' + file_name)

        print('Program done!')
        if missing_files:
            print(f'There are {len(missing_files)} files that are not configured in readme.python.md:')
            for file_name in missing_files:
                print(file_name)
        else:
            print('There are not missing files!!')
        os.system("pause")

    def compare_tag(self):
        self.step_into_service_folder()
        self.get_all_tag_files()
        self.get_configured_files()
        self.get_missing_files()

    def run(self):
        self.get_input()
        self.checkout_main_branch()
        self.compare_tag()


if __name__ == '__main__':
    instance = MultiApiConfigHelper()
    instance.run()
