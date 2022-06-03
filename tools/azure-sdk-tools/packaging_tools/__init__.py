from contextlib import suppress
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

from jinja2 import Template, PackageLoader, Environment
from .conf import read_conf, build_default_conf, CONF_NAME

_LOGGER = logging.getLogger(__name__)

_CWD = Path(__file__).resolve().parent
_TEMPLATE_PATH = _CWD / "template"


def build_config(config: Dict[str, Any]) -> Dict[str, str]:
    """Will build the actual config for Jinja2, based on SDK config."""
    result = config.copy()
    # Manage the classifier stable/beta
    is_stable = result.pop("is_stable", False)
    if is_stable:
        result["classifier"] = "Development Status :: 5 - Production/Stable"
    else:
        result["classifier"] = "Development Status :: 4 - Beta"
    # Manage the nspkg
    package_name = result["package_name"]
    result["package_nspkg"] = result.pop("package_nspkg", package_name[: package_name.rindex("-")] + "-nspkg")
    # ARM?
    result["is_arm"] = result.pop("is_arm", True)

    # Do I need msrestazure for this package?
    result["need_msrestazure"] = result.pop("need_msrestazure", False)

    # Do I need azure-mgmt-core for this package?
    result["need_azuremgmtcore"] = result.pop("need_azuremgmtcore", True)

    # Pre-compute some Jinja variable that are complicated to do inside the templates
    package_parts = result["package_nspkg"][: -len("-nspkg")].split("-")
    result["nspkg_names"] = [".".join(package_parts[: i + 1]) for i in range(len(package_parts))]
    result["init_names"] = ["/".join(package_parts[: i + 1]) + "/__init__.py" for i in range(len(package_parts))]

    # Return result
    return result


def build_packaging(
    output_folder: str,
    gh_token: Optional[str] = None,
    jenkins: bool = False,
    packages: List[str] = None,
    build_conf: bool = False,
) -> None:
    package_names = set(packages) or set()
    if jenkins:
        sdk_id = os.environ["ghprbGhRepository"]
        pr_number = int(os.environ["ghprbPullId"])

        from github import Github

        con = Github(gh_token)
        repo = con.get_repo(sdk_id)
        sdk_pr = repo.get_pull(pr_number)
        # "get_files" of Github only download the first 300 files. Might not be enough.
        package_names |= {f.filename.split("/")[0] for f in sdk_pr.get_files() if f.filename.startswith("azure")}

    if not package_names:
        raise ValueError("Was unable to find out the package names.")

    for package_name in package_names:
        build_packaging_by_package_name(package_name, output_folder, build_conf)


def build_packaging_by_package_name(package_name: str, output_folder: str, build_conf: bool = False) -> None:
    _LOGGER.info("Building template %s", package_name)
    package_folder = Path(output_folder) / Path(package_name)

    if build_conf:
        build_default_conf(package_folder, package_name)

    conf = read_conf(package_folder)
    if not conf:
        raise ValueError("Create a {} file before calling this script".format(package_folder / CONF_NAME))

    if not conf.get("auto_update", True):
        _LOGGER.info(f"Package {package_name} has no auto-packaging update enabled")
        return

    env = Environment(loader=PackageLoader("packaging_tools", "templates"), keep_trailing_newline=True)
    conf = build_config(conf)

    for template_name in env.list_templates():
        future_filepath = Path(output_folder) / package_name / template_name

        # Might decide to make it more generic one day
        if template_name == "CHANGELOG.md" and future_filepath.exists():
            _LOGGER.info("Skipping CHANGELOG.md template, since a previous one was found")
            # Never overwirte the ChangeLog
            continue

        template = env.get_template(template_name)
        result = template.render(**conf)

        # __init__.py is a weird one
        if template_name == "__init__.py":
            split_package_name = package_name.split("-")[:-1]
            for i in range(len(split_package_name)):
                init_path = Path(output_folder).joinpath(package_name, *split_package_name[: i + 1], template_name)
                with open(init_path, "w") as fd:
                    fd.write(result)

            continue

        with open(future_filepath, "w") as fd:
            fd.write(result)
    # azure_bdist_wheel had been removed, but need to delete it manually
    with suppress(FileNotFoundError):
        (Path(output_folder) / package_name / "azure_bdist_wheel.py").unlink()

    _LOGGER.info("Template done %s", package_name)
