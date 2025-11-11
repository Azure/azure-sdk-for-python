import re
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
from typing import Optional, Tuple, Any, List
from pathlib import Path
import logging
from subprocess import check_call, CalledProcessError, getoutput
from .generate_utils import return_origin_path
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



def modify_file(file_path: str, func: Any):
    with open(file_path, "r") as file_in:
        content = file_in.readlines()
    func(content)
    with open(file_path, "w") as file_out:
        file_out.writelines(content)


class CheckFile:

    def __init__(self, package_path: Path):
        self.package_path = package_path
        self.package_name = package_path.name
        self.package_name_last_part = self.package_name.split("-", 2)[-1]

    @property
    def pprint_name(self) -> str:
        return " ".join([word.capitalize() for word in self.package_name_last_part.split("-")])


    @property
    def extract_client_title_from_init(self) -> str:
        """
        Extract the client title from a package's __init__.py file.

        Returns:
            str: The client title if found, empty string otherwise
        """
        init_file = Path(self.package_name) / self.package_name.replace("-", "/") / "__init__.py"
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
    
    def version_from_changelog(self) -> str:
        changelog_file = self.package_path / "CHANGELOG.md"
        if not changelog_file.exists():
            _LOGGER.info(f"{changelog_file} does not exist.")
            return ""
        
        try:
            with open(changelog_file, "r") as f:
                for line in f:
                    # use regex to extract version "1.2.3" from lines like "## 1.2.3 (2024-01-01)" or
                    # "1.2.3b1" from "## 1.2.3b1 (2025-01-01)"
                    match = re.match(r"## (\d+\.\d+\.\d+(?:b\d+)?)\s+\((\d{4}-\d{2}-\d{2})\)", line)
                    if match:
                        return match.group(1)
        except Exception as e:
            _LOGGER.info(f"Failed to extract version from {changelog_file}: {e}")
        
        return ""

    # Use the template to update readme and setup by packaging_tools
    @return_origin_path
    def check_file_with_packaging_tool(self):

        os.chdir(self.package_path.parent)
        title = self.extract_client_title_from_init

        if not title:
            _LOGGER.info(f"Can not find the title for {self.package_name}")

        # add `title` and update `is_stable` in pyproject.toml
        pyproject_toml = Path(self.package_name) / "pyproject.toml"
        
        version = self.version_from_changelog()
        if not version:
            _LOGGER.info(f"Can not find the version from CHANGELOG.md for {self.package_name}")
        
        is_stable = "b" in version
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
            packages=[self.package_name],
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


    def check_pprint_name(self):

        def edit_file_for_pprint_name(content: List[str]):
            for i in range(0, len(content)):
                content[i] = content[i].replace("MyService", self.pprint_name)

        for file in os.listdir(str(self.package_path)):
            file_path = str(self.package_path / file)
            if os.path.isfile(file_path):
                modify_file(file_path, edit_file_for_pprint_name)
        _LOGGER.info(f' replace "MyService" with "{self.pprint_name}" successfully ')

    def check_sdk_readme(self):
        sdk_readme = str(Path(self.package_path) / "README.md")

        def edit_sdk_readme(content: List[str]):
            for i in range(0, len(content)):
                if content[i].find("MyService") > 0:
                    content[i] = content[i].replace("MyService", self.pprint_name)

        modify_file(sdk_readme, edit_sdk_readme)

    def check_dev_requirement(self):
        file = self.package_path / "dev_requirements.txt"
        content = ["-e ../../../eng/tools/azure-sdk-tools\n", "-e ../../identity/azure-identity\naiohttp\naiohttp\n"]
        if not file.exists():
            with open(file, "w") as file_out:
                file_out.writelines(content)

    @return_origin_path
    def check_pyproject_toml(self):
        os.chdir(self.package_path)
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


def check_file(package_path: Path):
    client = CheckFile(package_path)
    client.run()
