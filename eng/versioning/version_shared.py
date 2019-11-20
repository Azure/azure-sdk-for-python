from glob import glob
from os import path
from packaging.version import parse
import re


from setup_parser import parse_setup

SETUP_PY_GLOB = "**/setup.py"
VERSION_PY_GLOB = "**/_version.py"
VERSION_REGEX = r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]'
VERSION_STRING = "VERSION = '%s'"

DEV_STATUS_REGEX = r'(classifiers=\[(\s)*)(["\']Development Status :: .*["\'])'


def path_excluded(path):
    return "-nspkg" in path or "tests" in path or "mgmt" in path or is_metapackage(path)

# Metapackages do not have an 'azure' folder within them
def is_metapackage(package_path):
    dir_path = package_path if path.isdir(package_path) else path.split(package_path)[0]

    azure_path = path.join(dir_path, 'azure')
    return not path.exists(azure_path)

def get_setup_py_paths(base_path):
    glob_expression = path.join(base_path, SETUP_PY_GLOB)
    setup_paths = glob(glob_expression, recursive=True)

    filtered_paths = [path for path in setup_paths if not path_excluded(path)]
    return filtered_paths


def get_packages(sdk_location):
    paths = get_setup_py_paths(sdk_location)
    packages = []
    for setup_path in paths:
        try:
            setup_info = parse_setup(setup_path)
            setup_entry = (setup_path, setup_info)
            packages.append(setup_entry)
        except:
            print(f'Error parsing {setup_path}')
            raise

    return packages

def get_version_py(setup_py_location):
    file_path, _ = path.split(setup_py_location)
    glob_expression = path.join(file_path, VERSION_PY_GLOB)

    version_py_path = glob(glob_expression,  recursive=True)
    return version_py_path[0]

def set_version_py(setup_py_location, new_version):
    version_py_location = get_version_py(setup_py_location)

    version_contents = ''
    with open(version_py_location, 'r') as version_py_file:
        version_contents = version_py_file.read()

    with open(version_py_location, 'w') as version_py_file:
        replaced_version_contents = re.sub(
            VERSION_REGEX,
            VERSION_STRING % new_version,
            version_contents,
            flags=re.MULTILINE)

        version_py_file.write(replaced_version_contents)

# Get classification for PyPI (https://pypi.org/classifiers/)
def get_classification(version):
    parsed_version = parse(version)
    if not parsed_version.is_prerelease:
        return 'Development Status :: 5 - Production/Stable'
    else:
        return 'Development Status :: 4 - Beta'

def set_dev_classifier(setup_py_location, version):
    classification = get_classification(version)

    setup_contents = ''
    with open(setup_py_location, 'r+') as setup_py_file:
        setup_contents = setup_py_file.read()

        # Reset position and truncate the file for new contents
        setup_py_file.seek(0)
        setup_py_file.truncate()

        replaced_setup_contents = re.sub(
            DEV_STATUS_REGEX,
            f"\g<1>'{classification}'",
            setup_contents
        )

        setup_py_file.write(replaced_setup_contents)

