import glob
import os

from subprocess import check_call

from .change_log import main as change_log_main

DEFAULT_DEST_FOLDER = "./dist"


def create_package(name, dest_folder=DEFAULT_DEST_FOLDER):
    # a package will exist in either one, or the other folder. this is why we can resolve both at the same time.
    absdirs = [
        os.path.dirname(package)
        for package in (glob.glob("{}/setup.py".format(name)) + glob.glob("sdk/*/{}/setup.py".format(name)))
    ]

    absdirpath = os.path.abspath(absdirs[0])
    check_call(["python", "setup.py", "bdist_wheel", "-d", dest_folder], cwd=absdirpath)
    check_call(
        ["python", "setup.py", "sdist", "--format", "zip", "-d", dest_folder],
        cwd=absdirpath,
    )


def change_log_generate(package_name, last_version, tag_is_stable: bool = False):
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
        return "  - Initial Release"
    else:
        return change_log_main(f"{package_name}:pypi", f"{package_name}:latest", tag_is_stable)


def extract_breaking_change(changelog):
    log = changelog.split("\n")
    breaking_change = []
    for i in range(0, len(log)):
        if log[i].find("Breaking Changes") > -1:
            breaking_change = log[min(i + 2, len(log) - 1) :]
            break
    return sorted([x.replace("  - ", "") for x in breaking_change])
