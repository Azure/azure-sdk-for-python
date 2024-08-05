import os
from typing import Optional
from pathlib import Path
import logging
from subprocess import check_call, check_output, CalledProcessError

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


def change_log_new(package_folder: str, lastest_pypi_version: bool) -> str:
    cmd = "tox run -c ../../../eng/tox/tox.ini --root . -e breaking --  --changelog "
    if lastest_pypi_version:
        cmd += "--latest-pypi-version"
    try:
        output = check_output(cmd, cwd=package_folder, shell=True)
    except CalledProcessError as e:
        _LOGGER.warning(f"Failed to generate sdk from typespec: {e.output.decode('utf-8')}")
        raise e
    result = [l for l in output.decode("utf-8").split(os.linesep)]
    begin = result.index("===== changelog start =====")
    end = result.index("===== changelog end =====")
    if begin == -1 or end == -1:
        warn_info = "Failed to get changelog from breaking change detector"
        _LOGGER.warning(warn_info)
        raise Exception(warn_info)
    return "\n".join(result[begin + 1 : end]).strip()


def change_log_generate(
    package_name,
    last_version,
    tag_is_stable: bool = False,
    *,
    prefolder: Optional[str] = None,
    is_multiapi: bool = False,
):
    from pypi_tools.pypi import PyPIClient

    client = PyPIClient()
    try:
        ordered_versions = client.get_ordered_versions(package_name)
        last_release = ordered_versions[-1]
        stable_releases = [x for x in ordered_versions if not x.is_prerelease]
        last_stable_release = stable_releases[-1] if stable_releases else None
        if tag_is_stable:
            last_version[-1] = str(last_stable_release) if last_stable_release else str(last_release)
        else:
            last_version[-1] = str(last_release)
    except:
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
