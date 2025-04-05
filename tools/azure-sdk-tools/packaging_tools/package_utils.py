import os
import time
import importlib
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path
import logging
from subprocess import check_call, CalledProcessError, getoutput
from .generate_utils import return_origin_path
from packaging.version import Version

from .change_log import main as change_log_main

DEFAULT_DEST_FOLDER = "./dist"

_LOGGER = logging.getLogger(__name__)


# prefolder: "sdk/compute"; name: "azure-mgmt-compute"
def create_package(prefolder, name, dest_folder=DEFAULT_DEST_FOLDER):
    absdirpath = Path(prefolder, name).absolute()
    check_call(["python", "setup.py", "bdist_wheel", "-d", dest_folder], cwd=absdirpath)
    check_call(
        ["python", "setup.py", "sdist", "--format", "zip", "-d", dest_folder],
        cwd=absdirpath,
    )


@return_origin_path
def change_log_new(package_folder: str, lastest_pypi_version: bool) -> str:
    os.chdir(package_folder)
    cmd = "tox run -c ../../../eng/tox/tox.ini --root . -e breaking --  --changelog "
    if lastest_pypi_version:
        cmd += "--latest-pypi-version"
    try:
        _LOGGER.info(f"Run breaking change detector with command: {cmd}")
        output = getoutput(cmd)
    except CalledProcessError as e:
        _LOGGER.warning(f"Error ocurred when call breaking change detector: {e.output.decode('utf-8')}")
        raise e
    _LOGGER.info(f"Breaking change detector output: {output}")
    result = [l for l in output.split("\n")]
    begin = result.index("===== changelog start =====")
    end = result.index("===== changelog end =====")
    return "\n".join(result[begin + 1 : end]).strip()


def get_version_info(package_name: str, tag_is_stable: bool = False) -> Tuple[str, str]:
    from pypi_tools.pypi import PyPIClient

    try:
        client = PyPIClient()
        ordered_versions = client.get_ordered_versions(package_name)
        last_release = ordered_versions[-1]
        stable_releases = [x for x in ordered_versions if not x.is_prerelease]
        last_stable_release = stable_releases[-1] if stable_releases else ""
        if tag_is_stable:
            last_version = str(last_stable_release) if last_stable_release else str(last_release)
        else:
            last_version = str(last_release)
    except:
        last_version = ""
        last_stable_release = ""
    return last_version, str(last_stable_release)


def change_log_generate(
    package_name,
    last_version,
    tag_is_stable: bool = False,
    *,
    last_stable_release: Optional[str] = None,
    prefolder: Optional[str] = None,
    is_multiapi: bool = False,
):
    if not last_version:
        return "### Other Changes\n\n  - Initial version"

    # try new changelog tool
    if prefolder and not is_multiapi:
        try:
            return change_log_new(str(Path(prefolder) / package_name), not (last_stable_release and tag_is_stable))
        except Exception as e:
            _LOGGER.warning(f"Failed to generate changelog with breaking_change_detector: {e}")

    # fallback to old changelog tool
    _LOGGER.info("Fallback to old changelog tool")
    return change_log_main(f"{package_name}:pypi", f"{package_name}:latest", tag_is_stable)


def extract_breaking_change(changelog):
    log = changelog.split("\n")
    breaking_change = []
    idx = -1
    try:
        idx = log.index("### Breaking Changes")
    except ValueError:
        pass
    if idx > -1:
        for i in range(idx + 1, len(log)):
            if log[i].find("###") > -1:
                break
            if log[i]:
                breaking_change.append(log[i])
    return sorted([x.replace("  - ", "") for x in breaking_change])


def current_time() -> str:
    date = time.localtime(time.time())
    return "{}-{:02d}-{:02d}".format(date.tm_year, date.tm_mon, date.tm_mday)


# find all the files of one folder, including files in subdirectory
def all_files(path: str, files: List[str]):
    all_folder = os.listdir(path)
    for item in all_folder:
        folder = str(Path(f"{path}/{item}"))
        if os.path.isdir(folder):
            all_files(folder, files)
        else:
            files.append(folder)


def modify_file(file_path: str, func: Any):
    with open(file_path, "r") as file_in:
        content = file_in.readlines()
    func(content)
    with open(file_path, "w") as file_out:
        file_out.writelines(content)


def preview_version_plus(preview_label: str, last_version: str) -> str:
    num = last_version.split(preview_label)
    num[1] = str(int(num[1]) + 1)
    return f"{num[0]}{preview_label}{num[1]}"


def stable_version_plus(changelog: str, last_version: str):
    flag = [False, False, False]  # breaking, feature, bugfix
    flag[0] = "### Breaking Changes" in changelog
    flag[1] = "### Features Added" in changelog
    flag[2] = "### Bugs Fixed" in changelog

    num = last_version.split(".")
    if flag[0]:
        return f"{int(num[0]) + 1}.0.0"
    elif flag[1]:
        return f"{num[0]}.{int(num[1]) + 1}.0"
    elif flag[2]:
        return f"{num[0]}.{num[1]}.{int(num[2]) + 1}"
    else:
        return "0.0.0"


class CheckFile:

    def __init__(self, package_info: Dict[str, Any]):
        self.package_info = package_info
        self.whole_package_name = package_info["packageName"]
        self.package_name = self.whole_package_name.split("-", 2)[-1]
        self.sdk_folder = package_info["path"][0].split("/")[-1]
        self.tag_is_stable = package_info["tagIsStable"]
        self.target_release_date = package_info["targetReleaseDate"] or current_time()
        self.allow_invalid_next_version = package_info["allowInvalidNextVersion"]
        self._next_version = None
        self.version_suggestion = ""

    @property
    def next_version(self) -> str:
        if self._next_version is None:
            self._next_version = self.calculate_next_version()
        return self._next_version

    # Use the template to update readme and setup by packaging_tools
    @return_origin_path
    def check_file_with_packaging_tool(self):
        module = importlib.import_module(self.whole_package_name.replace("-", "."))
        title = ""
        for item in getattr(module, "__all__", []):
            if item.endswith("Client"):
                title = item
                break

        if not title:
            _LOGGER.info(f"Can not find the title in {self.whole_package_name}")

        os.chdir(Path(f"sdk/{self.sdk_folder}"))
        # add `title` and update `is_stable` in sdk_packaging.toml
        toml = Path(self.whole_package_name) / "sdk_packaging.toml"
        stable_config = "is_stable = " + ("true" if self.tag_is_stable else "false") + "\n"
        if toml.exists():

            def edit_toml(content: List[str]):
                has_title = False
                has_isstable = False
                for idx in range(len(content)):
                    if "title" in content[idx]:
                        has_title = True
                    if "is_stable" in content[idx]:
                        has_isstable = True
                        content[idx] = stable_config
                if not has_title:
                    content.append(f'title = "{title}"\n')
                if not has_isstable:
                    content.append(stable_config)

            modify_file(str(toml), edit_toml)
        else:
            _LOGGER.info(f"{os.getcwd()}/{toml} does not exist")

        check_call(f"python -m packaging_tools --build-conf {self.whole_package_name}", shell=True)
        _LOGGER.info("packaging_tools --build-conf successfully")

    def sdk_code_path(self) -> str:
        return str(Path(f"sdk/{self.sdk_folder}/{self.whole_package_name}"))

    def check_pprint_name(self):
        pprint_name = self.package_name.capitalize()

        def edit_file_for_pprint_name(content: List[str]):
            for i in range(0, len(content)):
                content[i] = content[i].replace("MyService", pprint_name)

        for file in os.listdir(self.sdk_code_path()):
            file_path = str(Path(self.sdk_code_path()) / file)
            if os.path.isfile(file_path):
                modify_file(file_path, edit_file_for_pprint_name)
        _LOGGER.info(f' replace "MyService" with "{pprint_name}" successfully ')

    def check_sdk_readme(self):
        sdk_readme = str(Path(f"sdk/{self.sdk_folder}/{self.whole_package_name}/README.md"))

        def edit_sdk_readme(content: List[str]):
            for i in range(0, len(content)):
                if content[i].find("MyService") > 0:
                    content[i] = content[i].replace("MyService", self.package_name.capitalize())

        modify_file(sdk_readme, edit_sdk_readme)

    def get_last_release_version(self) -> str:
        last_version = self.package_info["version"]
        try:
            return str(Version(last_version))
        except:
            return ""

    def get_changelog(self) -> str:
        return self.package_info["changelog"]["content"]

    def calculate_next_version_proc(self, last_version: str) -> str:
        preview_tag = not self.tag_is_stable
        changelog = self.get_changelog()
        if changelog == "":
            self.version_suggestion = "(it should be stable)" if self.tag_is_stable else "(it should be perview)"
            return "0.0.0"
        preview_version = "rc" in last_version or "b" in last_version
        #                                           |   preview tag                     | stable tag
        # preview version(1.0.0rc1/1.0.0b1)         | 1.0.0rc2(track1)/1.0.0b2(track2)  |  1.0.0
        # stable  version (1.0.0) (breaking change) | 2.0.0rc1(track1)/2.0.0b1(track2)  |  2.0.0
        # stable  version (1.0.0) (feature)         | 1.1.0rc1(track1)/1.1.0b1(track2)  |  1.1.0
        # stable  version (1.0.0) (bugfix)          | 1.0.1rc1(track1)/1.0.1b1(track2)  |  1.0.1
        preview_label = "b"
        if preview_version and preview_tag:
            next_version = preview_version_plus(preview_label, last_version)
        elif preview_version and not preview_tag:
            next_version = last_version.split(preview_label)[0]
        elif not preview_version and preview_tag:
            next_version = stable_version_plus(changelog, last_version) + preview_label + "1"
        else:
            next_version = stable_version_plus(changelog, last_version)

        return next_version

    def calculate_next_version(self) -> str:
        last_version = self.get_last_release_version()
        if last_version:
            return self.calculate_next_version_proc(last_version)
        return "1.0.0b1"

    def get_all_files_under_package_folder(self) -> List[str]:
        files = []
        all_files(self.sdk_code_path(), files)
        return files

    def edit_all_version_file(self):
        files = self.get_all_files_under_package_folder()

        def edit_version_file(content: List[str]):
            for i in range(0, len(content)):
                if content[i].find("VERSION") > -1:
                    content[i] = f'VERSION = "{self.next_version}"\n'
                    break

        for file in files:
            if Path(file).name == "_version.py":
                modify_file(file, edit_version_file)

    @property
    def has_invalid_next_version(self) -> bool:
        return self.next_version == "0.0.0"

    def check_version(self):
        if self.has_invalid_next_version and not self.allow_invalid_next_version:
            _LOGGER.info(f"next version is invalid, skip check _version.py")
            return
        self.edit_all_version_file()

    def check_changelog_file(self):
        if self.has_invalid_next_version and not self.allow_invalid_next_version:
            _LOGGER.info(f"next version is invalid, skip check CHANGELOG.md")
            return

        def edit_changelog_proc(content: List[str]):
            next_version = self.next_version
            content[1:1] = [
                "\n",
                f"## {next_version}{self.version_suggestion} ({self.target_release_date})\n\n",
                self.get_changelog(),
                "\n",
            ]
            if next_version == "1.0.0b1":
                for _ in range(4):
                    content.pop()

        modify_file(str(Path(self.sdk_code_path()) / "CHANGELOG.md"), edit_changelog_proc)

    def check_dev_requirement(self):
        file = Path(f"sdk/{self.sdk_folder}/{self.whole_package_name}/dev_requirements.txt")
        content = ["-e ../../../tools/azure-sdk-tools\n", "../../identity/azure-identity\n"]
        if not file.exists():
            with open(file, "w") as file_out:
                file_out.writelines(content)

    @return_origin_path
    def check_pyproject_toml(self):
        os.chdir(Path("sdk") / self.sdk_folder / self.whole_package_name)
        # add `breaking = false` in pyproject.toml
        toml = Path("pyproject.toml")
        if not toml.exists():
            with open(toml, "w") as file:
                file.write("[tool.azure-sdk-build]\nbreaking = false\n")
                _LOGGER.info("create pyproject.toml")

        def edit_toml(content: List[str]):
            has_breaking = False
            for line in content:
                if "breaking = false" in line:
                    has_breaking = True
                    break
            if not has_breaking:
                _LOGGER.info("add breaking = false to pyproject.toml")
                content.append("breaking = false\n")

        modify_file(str(toml), edit_toml)

    def run(self):
        self.check_file_with_packaging_tool()
        self.check_pprint_name()
        self.check_sdk_readme()
        self.check_version()
        self.check_changelog_file()
        self.check_dev_requirement()
        self.check_pyproject_toml()


def check_file(package: Dict[str, Any]):
    client = CheckFile(package)
    client.run()
    if not client.has_invalid_next_version:
        package["version"] = client.next_version
