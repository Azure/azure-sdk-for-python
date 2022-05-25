import os
import re
import json
import logging
import subprocess

import yaml
from pathlib import Path
from typing import Any, Set, Dict
from github import Github
from tempfile import TemporaryDirectory
import importlib.util

from github.GithubException import UnknownObjectException

_LOG = logging.getLogger()

SOURCE_FILE = {
    "azure-cli": "https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/profiles/_shared.py",
    "rest-api-profiles": "https://github.com/Azure/azure-rest-api-specs/tree/main/profiles/definitions",
    "rest-api-profile": "https://github.com/Azure/azure-rest-api-specs/tree/main/profile",
    "rest-api-specification": "https://github.com/Azure/azure-rest-api-specs/tree/main/specification",
}


class CollectApiVersion:
    """
    This class can collect api-version that may be used by azure stack
    """

    def __init__(self):
        self.github = Github(os.getenv("TOKEN"))
        self.rest_repo = self.github.get_repo("Azure/azure-rest-api-specs")
        self.package_api_version = {}
        self.multi_api_version_from_profiles = {}
        self.multi_api_version_from_profile = {}
        self.provider_mapping_package = {}
        self.output_files = {
            "package_api_version": "package_api_version_from_cli.json",
            "multi_api_version_from_profiles": "package_api_version_from_profiles.json",
            "multi_api_version_from_profile": "package_api_version_from_profile.json",
        }

    def get_api_version_from_azure_cli(self):
        # read content from github
        url_path = SOURCE_FILE["azure-cli"]
        cli_repo = self.github.get_repo("Azure/azure-cli")
        git_path = url_path.split("dev/")[-1]
        file_content = cli_repo.get_contents(git_path)

        # write to temp file
        temp_dir = TemporaryDirectory()
        file_name = str(Path(f"{temp_dir.name}/cli.py"))
        with open(file_name, "wb") as file_in:
            file_in.write(file_content.decoded_content)

        # import target object that contains api-version
        module_name = "AZURE_API_PROFILES"
        spec = importlib.util.spec_from_file_location(module_name, file_name)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        version_dict = getattr(foo, module_name)

        # extract api version
        for info in version_dict.values():
            for package_info in info:
                package_name = package_info.import_prefix
                if re.search("azure.mgmt.", package_name):
                    api_version = self.extract_api_version(info[package_info])
                    # eg: change them like azure.mgmt.resource to azure-mgmt-resource
                    package_name = package_name.replace(".", "-")
                    if package_name not in self.package_api_version:
                        self.package_api_version[package_name] = set()
                    self.package_api_version[package_name].update(api_version)

    def get_multiapi_from_rest_api(self):
        # map provider to package name, like: {'microsoft.insights': {'azure-mgmt-applicationinsights'}}
        url_path = SOURCE_FILE["rest-api-specification"]
        git_path = url_path.split("main/")[-1]
        service_paths = self.rest_repo.get_contents(git_path)
        packge_pattern = re.compile(b"package-name: (azure-mgmt-.*?)\n")
        for service_path in service_paths:
            try:
                resource_manager = self.rest_repo.get_contents(f"{service_path.path}/resource-manager")
            except UnknownObjectException:
                continue
            package_name, providers, multi_api_readme_python = "", set(), False
            for resource in resource_manager:
                if "Microsoft." in resource.name:
                    providers.add(resource.name.lower())
                if "readme.python.md" in resource.name:
                    if b"multiapiscript: true" not in resource.decoded_content:
                        break
                    multi_api_readme_python = True
                    package_name_line = re.search(packge_pattern, resource.decoded_content)
                    package_name = package_name_line.groups()[0].decode(encoding="utf-8")
            if not multi_api_readme_python:
                continue
            for n in providers:
                if not self.provider_mapping_package.get(n):
                    self.provider_mapping_package[n] = {package_name, }
                else:
                    self.provider_mapping_package[n].add(package_name)

    def find_versions_from_json(self, provider: str, version: Dict[str, Any], multi_api_version: Dict):
        if self.provider_mapping_package.get(provider):
            for p in self.provider_mapping_package.get(provider):
                if not multi_api_version.get(p):
                    multi_api_version[p] = set(version.keys())
                else:
                    multi_api_version[p].update(set(version.keys()))

    def get_api_version_from_rest_api_profiles(self):
        self.get_multiapi_from_rest_api()
        # Find api version mapping to {'azure-mgmt-msi': {'2018-11-30'}}
        url_path = SOURCE_FILE["rest-api-profiles"]
        git_path = url_path.split("main/")[-1]
        file_paths = self.rest_repo.get_contents(git_path)
        for file in file_paths:
            file_name, file_contents = file.name.replace(".md", ""), file.decoded_content
            profiles_content = str(file_contents).split("profiles:")[1].split("operations:")[0]
            profiles_content = profiles_content.strip(r"\n").strip().replace(r"\n", "\n")
            # Convert to JSON format
            content_dict = yaml.load(profiles_content, Loader=yaml.FullLoader)
            for provider, version in content_dict[file_name]["resources"].items():
                self.find_versions_from_json(provider, version, self.multi_api_version_from_profiles)

    def get_api_version_from_rest_api_profile(self):
        if not self.provider_mapping_package:
            self.get_multiapi_from_rest_api()
        # map package name to api version like {'azure-mgmt-msi': {'2018-11-30'}}
        url_path = SOURCE_FILE["rest-api-profile"]
        git_path = url_path.split("main/")[-1]
        file_paths = self.rest_repo.get_contents(git_path)
        for file in file_paths:
            if ".json" not in file.name:
                continue
            file_name, file_contents = (file.name.replace(".json", ""), file.decoded_content)
            content_dict = json.loads(file_contents.decode())
            resource_manager = "resource-manager" if content_dict.get("resource-manager") else "resourcemanager"
            for provider, version in content_dict[resource_manager].items():
                self.find_versions_from_json(provider, version, self.multi_api_version_from_profile)

    @staticmethod
    def extract_api_version(api_version_info: Any) -> Set[str]:
        # convert to string
        if isinstance(api_version_info, str):
            api_version = api_version_info
        else:
            api_version = api_version_info.default_api_version + str(api_version_info.profile)

        return set(re.findall("\d{4}-\d{2}-\d{2}[-a-z]*", api_version))

    @staticmethod
    def write_file(file_name, content):
        json_out = {k: sorted(content[k], reverse=True) for k in content}
        with open(file_name, "w") as file_out:
            json.dump(json_out, file_out, indent=4)

    def output(self):
        # output service and api version from cli or profiles or profile
        for k, v in self.output_files.items():
            self.write_file(v, getattr(self, k))
        # merge multi_api_version_from_profiles to package_api_version
        for k, v in self.multi_api_version_from_profiles.items():
            self.package_api_version[k] = self.package_api_version[k] | v if self.package_api_version.get(k) else v
        # merge multi_api_version_from_profile to package_api_version
        for k, v in self.multi_api_version_from_profile.items():
            self.package_api_version[k] = self.package_api_version[k] | v if self.package_api_version.get(k) else v

        # output all apiversion
        self.write_file("package_api_version_all.json", self.package_api_version)

    def run(self):
        self.get_api_version_from_azure_cli()
        self.get_api_version_from_rest_api_profiles()
        self.get_api_version_from_rest_api_profile()
        self.output()


def print_exec(cmd):
    _LOG.info("==" + cmd + " ==\n")
    subprocess.call(cmd, shell=True)


def print_check(cmd):
    _LOG.info("==" + cmd + " ==\n")
    subprocess.check_call(cmd, shell=True)


def upload_to_github():
    print_exec("git add .")
    print_exec('git commit -m "update json files"')
    print_check("git push origin HEAD -f")


if __name__ == "__main__":
    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.INFO)

    instance = CollectApiVersion()
    instance.run()
    upload_to_github()
