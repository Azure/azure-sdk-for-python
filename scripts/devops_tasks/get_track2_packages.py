import os
import ast
import io
import re
import logging
import textwrap
import sys
from subprocess import check_call
from common_tasks import get_all_track2_packages

TEST_TYPE = sys.argv[1]

def build_requirements_nightly(packages):
    file_path = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..", "..", "..",
            "./eng/scripts/smoketest",
        ))
    f = open(file_path + "/requirements-nightly.txt", 'w')
    for package in packages:
        pkg_name, _, setup_py_path = package
        f.write(setup_py_path + '\n')
    f.close()

def build_requirements_release(packages):
    file_path = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..", "..", "..",
            "./eng/scripts/smoketest",
        ))
    f = open(file_path + "/requirements-release.txt", 'w')
    from pypi_tools.pypi import PyPIClient
    client = PyPIClient()
    for package in packages:
        pkg_name, _, _ = package
        try:
            versions = [str(v) for v in client.get_ordered_versions(pkg_name, False)]
            f.write(pkg_name + '\n')
        except Exception as err:
            logging.info(err)
            logging.info("Skipping Package {} since it is not available on PyPI".format(pkg_name))
    f.close()

if __name__ == '__main__':
    print("Running get_track2_packages.py")
    packages = get_all_track2_packages('.')
    if TEST_TYPE == 'nightly':
        build_requirements_nightly(packages)
    elif TEST_TYPE == 'release':
        build_requirements_release(packages)
