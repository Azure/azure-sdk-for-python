import os
import json
import time
import logging
from glob import glob
from subprocess import check_call, call
from pathlib import Path
from functools import wraps
from typing import List, Any, Dict
from packaging.version import Version
from ghapi.all import GhApi
from util import add_certificate


def print_check(cmd: str):
    check_call(cmd, shell=True)


def print_exec(cmd: str):
    call(cmd, shell=True)


def get_repo_root_folder() -> str:
    current_path = os.getcwd()
    return str(Path(current_path.split('azure-sdk-for-python')[0]) / 'azure-sdk-for-python')


class AutoPrivatePackage:
    """
    This class can generate private SDK package
    """

    def __init__(self):
        self.usr = ''
        self.target_branch = ''
        self.package_name = ''

    def get_input(self):
        print('Please commit your code before execute this script!!!')
        branch = input('Please input your target branch(e.g. azclibot:t2-compute-2022-01-21-22956)')
        info = branch.split(':')
        self.usr = info[0]
        self.target_branch = info[1]
        self.package_name = info[1].split('-')[1]

    def git_clean(self):
        print_check('git checkout .')
        print_check('git clean -fd')
        print_check('git reset --hard HEAD')

    def checkout_target_branch(self):
        print_exec(f'git remote add {self.usr} https://github.com/{self.usr}/azure-sdk-for-python.git')
        print_check(f'git fetch {self.usr} {self.target_branch}')
        print_check(f'git checkout {self.usr}/{self.target_branch}')

    def step_into_package_folder(self):
        root_path = get_repo_root_folder()
        result = glob(f'{root_path}/sdk/*/azure-mgmt-{self.package_name}')
        if len(result) == 0:
            raise Exception(f'do not find azure-mgmt-{self.package_name}')
        elif len(result) > 1:
            raise Exception(f'find multi target package: {str(result)}')
        os.chdir(str(Path(result[0])))

    def generate_private_package(self):
        self.step_into_package_folder()
        check_call('python setup.py bdist')
        check_call('python setup.py sdist --format zip')
        print(f'package in : {str(Path(os.getcwd()) / "dist")}')

    def run(self):
        self.get_input()
        # self.git_clean()
        # self.checkout_target_branch()
        self.generate_private_package()


if __name__ == '__main__':
    instance = AutoPrivatePackage()
    instance.run()
