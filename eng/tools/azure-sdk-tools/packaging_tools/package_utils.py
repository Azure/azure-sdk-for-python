import sys
import os
import ast
import time
import shutil

try:
    # py 311 adds this library natively
    import tomllib as toml
except:
    # otherwise fall back to pypi package tomli
    import tomli as toml
import tomli_w as tomlw
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path
import logging
from subprocess import check_call, CalledProcessError, getoutput
from .generate_utils import return_origin_path
from packaging.version import Version
from . import build_packaging
from .change_log import main as change_log_main

_LOGGER = logging.getLogger(__name__)


# prefolder: "sdk/compute"; name: "azure-mgmt-compute"
def create_package(prefolder, name):
    absdirpath = Path(prefolder, name).absolute()
    check_call([sys.executable, "-m", "build"], cwd=absdirpath)


@return_origin_path
def change_log_new(package_folder: str, lastest_pypi_version: bool) -> str:
    os.chdir(package_folder)
    cmd = "python -m tox run -c ../../../eng/tox/tox.ini --root . -e breaking --  --changelog "
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
    try:
        begin = result.index("===== changelog start =====")
        end = result.index("===== changelog end =====")
    except ValueError:
        raise Exception("\n".join(result))
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
):
    if not last_version:
        return "### Other Changes\n\n  - Initial version"

    # try new changelog tool
    if prefolder:
        try:
            tox_cache_path = Path(prefolder, package_name, ".tox")
            if tox_cache_path.exists():
                _LOGGER.info(f"Remove {tox_cache_path} to avoid potential tox cache conflict")
                shutil.rmtree(tox_cache_path)
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
        self._next_version = None
        self.version_suggestion = ""

    @property
    def pprint_name(self) -> str:
        return " ".join([word.capitalize() for word in self.package_name.split("-")])

    @property
    def next_version(self) -> str:
        if self._next_version is None:
            self._next_version = self.calculate_next_version()
        return self._next_version

    @property
    def extract_client_title_from_init(self) -> str:
        """
        Extract the client title from a package's __init__.py file.

        Args:
            package_name (str): The package name (e.g., "azure-mgmt-compute")

        Returns:
            str: The client title if found, empty string otherwise
        """
        init_file = Path(self.whole_package_name) / self.whole_package_name.replace("-", "/") / "__init__.py"
        try:
            with open(init_file, "r") as f:
                content = f.read()
            tree = ast.parse(content)
            # Look for __all__ assignment
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    # Check if any target is __all__
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__" and isinstance(node.value, ast.List):
                            # Extract the value
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and elt.value.endswith("Client"):
                                    return elt.value
        except Exception as e:
            _LOGGER.info(f"Failed to extract title from {init_file}: {e}")

        return ""

    # Use the template to update readme and setup by packaging_tools
    @return_origin_path
    def check_file_with_packaging_tool(self):

        os.chdir(Path(f"sdk/{self.sdk_folder}"))
        title = self.extract_client_title_from_init

        if not title:
            _LOGGER.info(f"Can not find the title for {self.whole_package_name}")

        # add `title` and update `is_stable` in pyproject.toml
        pyproject_toml = Path(self.whole_package_name) / "pyproject.toml"
        is_stable = self.tag_is_stable and self.next_version != "1.0.0b1"
        if pyproject_toml.exists():
            with open(pyproject_toml, "rb") as fd:
                toml_data = toml.load(fd)
            if "packaging" not in toml_data:
                toml_data["packaging"] = {}
            if title and not toml_data["packaging"].get("title"):
                toml_data["packaging"]["title"] = title
            toml_data["packaging"]["is_stable"] = is_stable
            with open(pyproject_toml, "wb") as fd:
                tomlw.dump(toml_data, fd)
            _LOGGER.info(f"Update {pyproject_toml} successfully")
        else:
            _LOGGER.info(f"{os.getcwd()}/{pyproject_toml} does not exist")

        build_packaging(
            output_folder=".",
            packages=[self.whole_package_name],
            build_conf=True,
            template_names=["README.md", "__init__.py"],
        )
        _LOGGER.info("packaging_tools --build-conf successfully")

        if pyproject_toml.exists():
            stable_classifier = "Development Status :: 5 - Production/Stable"
            beta_classifier = "Development Status :: 4 - Beta"

            def edit_file(content: List[str]):
                for i in range(0, len(content)):
                    if "Development Status" in content[i]:
                        if is_stable and beta_classifier in content[i]:
                            content[i] = content[i].replace(beta_classifier, stable_classifier)
                            _LOGGER.info(f"Replace '{beta_classifier}' with '{stable_classifier}' in {pyproject_toml}")
                        if (not is_stable) and stable_classifier in content[i]:
                            content[i] = content[i].replace(stable_classifier, beta_classifier)
                            _LOGGER.info(f"Replace '{stable_classifier}' with '{beta_classifier}' in {pyproject_toml}")
                        break

            modify_file(str(pyproject_toml), edit_file)
            _LOGGER.info(f"Check {pyproject_toml} for classifiers successfully")

    def sdk_code_path(self) -> str:
        return str(Path(f"sdk/{self.sdk_folder}/{self.whole_package_name}"))

    def check_pprint_name(self):

        def edit_file_for_pprint_name(content: List[str]):
            for i in range(0, len(content)):
                content[i] = content[i].replace("MyService", self.pprint_name)

        for file in os.listdir(self.sdk_code_path()):
            file_path = str(Path(self.sdk_code_path()) / file)
            if os.path.isfile(file_path):
                modify_file(file_path, edit_file_for_pprint_name)
        _LOGGER.info(f' replace "MyService" with "{self.pprint_name}" successfully ')

    def check_sdk_readme(self):
        sdk_readme = str(Path(f"sdk/{self.sdk_folder}/{self.whole_package_name}/README.md"))

        def edit_sdk_readme(content: List[str]):
            for i in range(0, len(content)):
                if content[i].find("MyService") > 0:
                    content[i] = content[i].replace("MyService", self.pprint_name)

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

    def check_dev_requirement(self):
        file = Path(f"sdk/{self.sdk_folder}/{self.whole_package_name}/dev_requirements.txt")
        content = ["-e ../../../eng/tools/azure-sdk-tools\n", "-e ../../identity/azure-identity\naiohttp\n"]
        if not file.exists():
            with open(file, "w") as file_out:
                file_out.writelines(content)

    @return_origin_path
    def check_pyproject_toml(self):
        os.chdir(Path("sdk") / self.sdk_folder / self.whole_package_name)
        # Configure and ensure pyproject.toml exists with required settings
        toml_path = Path("pyproject.toml")

        # Default configurations to enforce
        default_configs = {
            "breaking": "false",
            "pyright": "false",
            "mypy": "false",
        }

        # Load existing TOML or create new structure
        if toml_path.exists():
            try:
                with open(toml_path, "rb") as file:
                    toml_data = toml.load(file)
            except Exception as e:
                _LOGGER.warning(f"Error parsing pyproject.toml: {e}, creating new one")
                toml_data = {}
        else:
            toml_data = {}

        # Ensure [tool.azure-sdk-build] section exists
        if "tool" not in toml_data:
            toml_data["tool"] = {}

        if "azure-sdk-build" not in toml_data["tool"]:
            toml_data["tool"]["azure-sdk-build"] = {}

        # Update configurations
        azure_sdk_build = toml_data["tool"]["azure-sdk-build"]

        for key, value in default_configs.items():
            if key not in azure_sdk_build:
                _LOGGER.info(f"Adding {key} = {value} to pyproject.toml")
                if isinstance(value, str):
                    if value.lower() == "true":
                        azure_sdk_build[key] = True
                    elif value.lower() == "false":
                        azure_sdk_build[key] = False
                    else:
                        azure_sdk_build[key] = value
                else:
                    azure_sdk_build[key] = value
        # Write back to file
        with open(toml_path, "wb") as file:
            tomlw.dump(toml_data, file)

        _LOGGER.info("Updated pyproject.toml with required azure-sdk-build configurations")

    def run(self):
        self.check_file_with_packaging_tool()
        self.check_pprint_name()
        self.check_sdk_readme()
        self.check_dev_requirement()
        self.check_pyproject_toml()


def check_file(package: Dict[str, Any]):
    client = CheckFile(package)
    client.run()
    if not client.has_invalid_next_version:
        package["version"] = client.next_version
