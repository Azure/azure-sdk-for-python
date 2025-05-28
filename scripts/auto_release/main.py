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
from github import Github
from datetime import datetime, timedelta

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
    _LOG.info("==" + cmd + " ==\n")


def print_exec(cmd: str):
    log(cmd)
    subprocess.call(cmd, shell=True)


def print_exec_output(cmd: str) -> List[str]:
    log(cmd)
    return subprocess.getoutput(cmd).split("\n")


def print_check(cmd):
    log(cmd)
    subprocess.check_call(cmd, shell=True)


def modify_file(file_path: str, func: Any):
    with open(file_path, "r") as file_in:
        content = file_in.readlines()
    func(content)
    with open(file_path, "w") as file_out:
        file_out.writelines(content)


def current_time() -> str:
    date = time.localtime(time.time())
    return "{}-{:02d}-{:02d}".format(date.tm_year, date.tm_mon, date.tm_mday)


def current_time_month() -> str:
    date = time.localtime(time.time())
    return "{}-{:02d}".format(date.tm_year, date.tm_mon)


class CodegenTestPR:
    """
    This class can generate SDK code, run live test and create RP
    """

    def __init__(self):
        self.issue_link = os.getenv("ISSUE_LINK", "")
        self.pipeline_link = os.getenv("PIPELINE_LINK", "")
        self.bot_token = os.getenv("BOT_TOKEN")
        self.spec_readme = os.getenv("SPEC_README", "")
        self.spec_repo = os.getenv("SPEC_REPO", "")
        self.target_date = os.getenv("TARGET_DATE", "")
        self.test_folder = os.getenv("TEST_FOLDER", "")
        self.issue_owner = os.getenv("ISSUE_OWNER", "")

        self.package_name = ""  # 'dns' of 'sdk/compute/azure-mgmt-dns'
        self.whole_package_name = ""  # 'azure-mgmt-dns'
        self.new_branch = ""
        self.sdk_folder = ""  # 'compute' of 'sdk/compute/azure-mgmt-dns'
        self.autorest_result = ""
        self.next_version = ""
        self.test_result = ""
        self.pr_number = 0
        self.tag_is_stable = False
        self.has_test = False
        self.check_package_size_result = []  # List[str]
        self.version_suggestion = ""  # if can't calculate next version, give a suggestion

    @property
    def target_release_date(self) -> str:
        try:
            if self.target_date:
                return (datetime.fromisoformat(self.target_date) + timedelta(days=-4)).strftime("%Y-%m-%d")
        except:
            log(f"Invalid target date: {self.target_date}")
        return current_time()

    @return_origin_path
    def get_latest_commit_in_swagger_repo(self) -> str:
        os.chdir(Path(self.spec_repo))
        head_sha = print_exec_output("git rev-parse HEAD")[0]
        return head_sha

    def readme_local_folder(self) -> str:
        return "specification" + self.spec_readme.split("specification")[-1]

    def get_sdk_folder_with_autorest_result(self):
        generate_result = self.get_autorest_result()
        self.sdk_folder = generate_result["packages"][0]["path"][0].split("/")[-1]

    @staticmethod
    def checkout_branch(env_key: str, repo: str):
        env_var = os.getenv(env_key, "")
        usr = env_var.split(":")[0] or "Azure"
        branch = env_var.split(":")[-1] or "main"
        print_exec(f"git remote add {usr} https://github.com/{usr}/{repo}.git")
        print_check(f"git fetch {usr} {branch}")
        print_check(f"git checkout {usr}/{branch}")

    @return_origin_path
    def checkout_azure_default_branch(self):
        # checkout branch in sdk repo
        self.checkout_branch("DEBUG_SDK_BRANCH", "azure-sdk-for-python")

        # checkout branch in rest repo
        if self.spec_repo:
            os.chdir(Path(self.spec_repo))
            self.checkout_branch("DEBUG_REST_BRANCH", "azure-rest-api-specs")

    @property
    def from_swagger(self) -> bool:
        return "readme.md" in self.spec_readme

    def generate_code(self):
        self.checkout_azure_default_branch()

        # prepare input data
        file_name = "relatedReadmeMdFiles" if self.from_swagger else "relatedTypeSpecProjectFolder"
        input_data = {
            "headSha": self.get_latest_commit_in_swagger_repo(),
            "repoHttpsUrl": "https://github.com/Azure/azure-rest-api-specs",
            "specFolder": self.spec_repo,
            file_name: [self.readme_local_folder()],
            "targetReleaseDate": self.target_release_date,
            "allowInvalidNextVersion": True,
        }
        log(str(input_data))

        # if Python tag exists
        if os.getenv("PYTHON_TAG"):
            input_data["python_tag"] = os.getenv("PYTHON_TAG")

        self.autorest_result = str(Path(os.getenv("TEMP_FOLDER")) / "temp.json")
        with open(self.autorest_result, "w") as file:
            json.dump(input_data, file)

        # generate code(be careful about the order)
        print_exec("python scripts/dev_setup.py -p azure-core")
        print_check(f"python -m packaging_tools.sdk_generator {self.autorest_result} {self.autorest_result}")

        generate_result = self.get_autorest_result()
        self.tag_is_stable = list(generate_result.values())[0]["tagIsStable"]
        log(f"tag_is_stable is {self.tag_is_stable}")

        print_check(f"python -m packaging_tools.sdk_package {self.autorest_result} {self.autorest_result}")

    def get_package_name_with_autorest_result(self):
        generate_result = self.get_autorest_result()
        self.whole_package_name = generate_result["packages"][0]["packageName"]
        self.package_name = self.whole_package_name.split("-", 2)[-1]

    def prepare_branch_with_readme(self):
        self.generate_code()
        self.get_package_name_with_autorest_result()
        self.get_sdk_folder_with_autorest_result()
        self.create_new_branch()

    def create_new_branch(self):
        self.new_branch = f"t2-{self.package_name}-{current_time()}-{str(time.time())[-5:]}"
        print_check(f"git checkout -b {self.new_branch}")

    @property
    def readme_md_path(self) -> Path:
        return Path(self.spec_repo) / "specification" / self.spec_readme.split("specification/")[-1]

    @property
    def readme_python_md_path(self) -> Path:
        return Path(str(self.readme_md_path).replace("readme.md", "readme.python.md"))

    def get_autorest_result(self) -> Dict[Any, Any]:
        with open(self.autorest_result, "r") as file_in:
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
            return ""

    def check_package_size(self):
        if self.after_multiapi_combiner:
            packages = self.get_private_package()
            for package in packages:
                if os.path.getsize(package) > 2 * 1024 * 1024:
                    self.check_package_size_result.append(
                        f"ERROR: Package size is over 2MBytes: {Path(package).name}!!!"
                    )

    def check_model_flatten(self):
        if self.whole_package_name in [
            "azure-mgmt-mysqlflexibleservers",
            "azure-mgmt-postgresqlflexibleservers",
            "azure-mgmt-kubernetesconfiguration-extensiontypes",
            "azure-mgmt-kubernetesconfiguration-extensions",
            "azure-mgmt-kubernetesconfiguration-fluxconfigurations",
        ]:
            return
        if self.from_swagger:
            last_version = self.get_last_release_version()
            if last_version == "" or last_version.startswith("1.0.0b"):
                with open(self.readme_md_path, "r") as file_in:
                    readme_md_content = file_in.read()

                with open(self.readme_python_md_path, "r") as file_in:
                    readme_python_md_content = file_in.read()

                if (
                    "flatten-models: false" not in readme_md_content
                    and "flatten-models: false" not in readme_python_md_content
                    and self.issue_link
                ):
                    api = Github(self.bot_token).get_repo("Azure/sdk-release-request")
                    issue_number = int(self.issue_link.split("/")[-1])
                    issue = api.get_issue(issue_number)
                    assignee = issue.assignee.login if issue.assignee else ""
                    message = "please set `flatten-models: false` in readme.md or readme.python.md"
                    issue.create_comment(f"@{assignee}, {message}")
                    raise Exception(message)

    def check_file(self):
        self.check_package_size()
        self.check_model_flatten()

    def sdk_code_path(self) -> str:
        return str(Path(f"sdk/{self.sdk_folder}/{self.whole_package_name}"))

    @property
    def has_multi_packages(self) -> bool:
        sdk_path = Path("sdk") / self.sdk_folder
        packages = [l for l in sdk_path.iterdir() if l.is_dir() and l.name.startswith("azure")]
        return len(packages) > 1

    @return_origin_path
    def install_package_locally(self):
        os.chdir(self.sdk_code_path())
        print_check("pip install -e .")
        print_exec("pip install -r dev_requirements.txt")

    def prepare_test_env(self):
        self.install_package_locally()

    @staticmethod
    def is_live_test() -> bool:
        return str(os.getenv("AZURE_TEST_RUN_LIVE")).lower() == "true"

    @return_origin_path
    def run_test_proc(self):
        # run test
        os.chdir(self.sdk_code_path())
        test_mode = "Live test" if self.is_live_test() else "Recording test"
        succeeded_result = f"{test_mode} success"
        failed_result = f"{test_mode} fail, detailed info is in pipeline log(search keyword FAILED)!!!"
        try:
            print_check(f"pytest  --collect-only")
        except:
            try:
                assert "error" not in print_exec_output(f"pytest  --collect-only")[-1]
                log(f"{test_mode} run done, do not find any test !!!")
                self.test_result = succeeded_result
            except:
                log("some test collected failed, please fix it locally")
                self.test_result = failed_result
            return
        try:
            print_check(f"pytest -s")
        except:
            log("some test failed, please fix it locally")
            self.test_result = failed_result
        else:
            log(f"{test_mode} run done, do not find failure !!!")
            self.test_result = succeeded_result

        self.has_test = True

    @staticmethod
    def clean_test_env():
        for item in ("SSL_CERT_DIR", "REQUESTS_CA_BUNDLE"):
            if os.getenv(item):
                os.environ.pop(item)

    @return_origin_path
    def upload_recording_files(self):
        if self.is_live_test() and self.has_test:
            os.chdir(self.sdk_code_path())
            print_exec("python ../../../scripts/manage_recordings.py push")

    def run_test(self):
        self.prepare_test_env()
        self.run_test_proc()
        self.clean_test_env()
        # self.upload_recording_files()

    def create_pr_proc(self):
        api = GhApi(owner="Azure", repo="azure-sdk-for-python", token=self.bot_token)
        pr_title = "[AutoRelease] {}(can only be merged by SDK owner)".format(self.new_branch)
        pr_head = "{}:{}".format(os.getenv("USR_NAME"), self.new_branch)
        pr_base = "main"
        pr_body = "" if not self.check_package_size_result else "{}\n".format("\n".join(self.check_package_size_result))
        pr_body = pr_body + "{} \n{} \n{}".format(self.issue_link, self.test_result, self.pipeline_link)
        if self.has_multi_packages:
            pr_body += f"\nBuildTargetingString\n  {self.whole_package_name}\nSkip.CreateApiReview"
        res_create = api.pulls.create(pr_title, pr_head, pr_base, pr_body)

        # Add issue link on PR
        api = GhApi(owner="Azure", repo="azure-sdk-for-python", token=self.bot_token)
        api.issues.create_comment(issue_number=res_create.number, body="issue link:{}".format(self.issue_link))
        self.pr_number = res_create.number

    def zero_version_policy(self):
        if re.match(re.compile(r"0\.0\.0"), self.next_version):
            api_request = GhApi(owner="Azure", repo="sdk-release-request", token=self.bot_token)
            if self.issue_link:
                issue_number = int(self.issue_link.split("/")[-1])
                api_request.issues.add_labels(issue_number=issue_number, labels=["base-branch-attention"])

    @property
    def after_multiapi_combiner(self) -> bool:
        content = self.get_autorest_result()
        return content["packages"][0]["afterMultiapiCombiner"]

    def get_private_package(self) -> List[str]:
        content = self.get_autorest_result()
        return content["packages"][0]["artifacts"]

    def ask_check_policy(self):
        changelog = self.get_changelog()
        if changelog == "":
            changelog = "no new content found by changelog tools!"

        if self.issue_link:
            # comment to ask for check from users
            issue_number = int(self.issue_link.split("/")[-1])
            api = GhApi(owner="Azure", repo="sdk-release-request", token=self.bot_token)
            author = self.issue_owner or api.issues.get(issue_number=issue_number).user.login
            body = (
                f"Hi @{author}, please check whether CHANGELOG for this release meet requirements:\n"
                f"```\n"
                f"CHANGELOG:\n"
                f"{changelog}\n"
                f"```\n"
                "* (If you want private package for test or development, "
                f"please build it locally based on https://github.com/Azure/azure-sdk-for-python/pull/{self.pr_number} with [guidance](https://github.com/Azure/azure-sdk-for-python/wiki/Common-issues-about-Python-SDK#build-private-package-with-pr))\n\n"
            )
            api.issues.create_comment(issue_number=issue_number, body=body)

            # comment for hint
            body = (
                "Tips: If you have special needs for release date or other things, please let us know. "
                "Otherwise we will follow "
                "[Management-SDK-Release-Cycle](https://eng.ms/docs/products/azure-developer-experience/develop/sdk-release/sdk-release?tabs=management) "
                "to release it before target date"
            )
            api.issues.create_comment(issue_number=issue_number, body=body)

    def issue_comment(self):
        self.zero_version_policy()
        self.ask_check_policy()

    @staticmethod
    def commit_code():
        print_exec("git add sdk/")
        print_exec('git commit -m "code and test"')
        print_check("git push origin HEAD -f")

    def create_pr(self):
        # commit all code
        self.commit_code()

        # create PR
        self.create_pr_proc()

        # create release issue comment
        self.issue_comment()

    def run(self):
        if "https:" in self.spec_readme:
            self.prepare_branch_with_readme()
            self.check_file()
            self.run_test()
            self.create_pr()
        elif self.test_folder:
            self.sdk_folder = self.test_folder.split("/")[0]
            self.package_name = self.test_folder.split("/")[-1].split("-")[-1]
            env_var = os.getenv("DEBUG_SDK_BRANCH", "")
            branch = env_var.split(":")[-1]

            print_check(f"git checkout {branch}")
            self.run_test()

            # commit all code
            self.commit_code()


if __name__ == "__main__":
    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.INFO)

    instance = CodegenTestPR()
    instance.run()
