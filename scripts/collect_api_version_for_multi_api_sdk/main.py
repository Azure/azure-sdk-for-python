import os
import re
import json
import logging
from pathlib import Path
from typing import Any, Set
from github import Github
from tempfile import TemporaryDirectory
import importlib.util

_LOG = logging.getLogger()

SOURCE_FILE = {
    'azure-cli': 'https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/profiles/_shared.py'
}


class CollectApiVersion:
    """
    This class can collect api-version that may be used by azure stack
    """

    def __init__(self):
        self.github = Github(os.getenv('TOKEN'))
        self.package_api_version = {}

    def get_api_version_from_azure_cli(self):
        # read content from github
        url_path = SOURCE_FILE['azure-cli']
        cli_repo = self.github.get_repo('Azure/azure-cli')
        git_path = url_path.split('dev/')[-1]
        file_content = cli_repo.get_contents(git_path)

        # write to temp file
        temp_dir = TemporaryDirectory()
        file_name = str(Path(f'{temp_dir.name}/cli.py'))
        with open(file_name, 'wb') as file_in:
            file_in.write(file_content.decoded_content)

        # import target object that contains api-version
        module_name = 'AZURE_API_PROFILES'
        spec = importlib.util.spec_from_file_location(module_name, file_name)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        version_dict = getattr(foo, module_name)

        # extract api version
        for info in version_dict.values():
            for package_info in info:
                package_name = package_info.import_prefix
                if re.search('azure.mgmt.', package_name):
                    api_version = self.extract_api_version(info[package_info])
                    if package_name not in self.package_api_version:
                        self.package_api_version[package_name] = set()
                    self.package_api_version[package_name].update(api_version)

    @staticmethod
    def extract_api_version(api_version_info: Any) -> Set[str]:
        # convert to string
        if isinstance(api_version_info, str):
            api_version = api_version_info
        else:
            api_version = api_version_info.default_api_version + str(api_version_info.profile)

        return set(re.findall('\d{4}-\d{2}-\d{2}[-a-z]*', api_version))

    def output(self):
        # output service and api version
        json_out = {k: sorted(self.package_api_version[k], reverse=True) for k in self.package_api_version}
        with open('package_api_version.json', 'w') as file_out:
            json.dump(json_out, file_out, indent=4)

        # output readme.md
        files_name = '  \n'.join(list(SOURCE_FILE.values()))
        content = f'The data is collected from the following files:  \n{files_name}'
        with open('README.md', 'w') as file_out:
            file_out.write(content)

    def run(self):
        self.get_api_version_from_azure_cli()

        self.output()


if __name__ == '__main__':
    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.INFO)

    instance = CollectApiVersion()
    instance.run()
