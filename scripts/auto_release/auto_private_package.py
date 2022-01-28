import os
from glob import glob
from subprocess import check_call, call
from pathlib import Path


def print_check(cmd: str):
    check_call(cmd, shell=True)


def print_exec(cmd: str):
    call(cmd, shell=True)


def step_into_sdk_repo() -> str:
    return os.chdir(Path(os.getcwd()) / 'azure-sdk-for-python')


def git_clean():
    print_check('git checkout .')
    print_check('git clean -fd')
    print_check('git reset --hard HEAD')


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
        branch = input('Please input your target branch(e.g. azclibot:t2-compute-2022-01-21-22956):')
        info = branch.split(':')
        self.usr = info[0]
        self.target_branch = info[1]
        self.package_name = info[1].split('-')[1]

    def checkout_target_branch(self):
        step_into_sdk_repo()
        git_clean()
        print_exec(f'git remote add {self.usr} https://github.com/{self.usr}/azure-sdk-for-python.git')
        print_check(f'git fetch {self.usr} {self.target_branch}')
        print_check(f'git checkout {self.usr}/{self.target_branch}')

    def step_into_package_folder(self):
        root_path = os.getcwd()
        result = glob(f'{root_path}/sdk/*/azure-mgmt-{self.package_name}')
        if len(result) == 0:
            raise Exception(f'do not find azure-mgmt-{self.package_name}')
        elif len(result) > 1:
            raise Exception(f'find multi target package: {str(result)}')
        os.chdir(str(Path(result[0])))

    def generate_private_package(self):
        self.step_into_package_folder()
        check_call('python setup.py bdist_wheel')
        check_call('python setup.py sdist --format zip')
        print(f'\n package in : {str(Path(os.getcwd()) / "dist")}')
        os.system("pause")

    def run(self):
        self.get_input()
        self.checkout_target_branch()
        self.generate_private_package()


if __name__ == '__main__':
    instance = AutoPrivatePackage()
    instance.run()
