import argparse
from os import path
from packaging.version import parse

from version_shared import get_packages, set_version_py, set_dev_classifier

DEFAULT_SDK_PATH = "../../sdk/"

def format_build_id(build_id):
    split_build_id = build_id.split('.', 1)
    if len(split_build_id[1]) > 2:
        raise ValueError("Build number suffix is out of acceptable range for package sorting (0 < r < 100)")
    return ''.join([split_build_id[0], split_build_id[1].zfill(2)])

def get_dev_version(current_version, build_id):
    parsed_version = parse(current_version)
    release = parsed_version.release
    return f"{release[0]}.{release[1]}.{release[2]}.dev{build_id}"

def is_in_service(sdk_path, setup_py_location, service_name):
    sdk_prefix = path.normpath(sdk_path)
    normalized_setup = path.normpath(setup_py_location)

    return normalized_setup.startswith(path.join(sdk_prefix, service_name))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Increments version for a given package name based on the released version')
    parser.add_argument('--sdk-path', default=DEFAULT_SDK_PATH, help='path to the sdk folder')
    parser.add_argument('--service-name', required=True, help='name of the service for which to set the dev build id (e.g. keyvault)')
    parser.add_argument('--build-id', required=True, help='id of the build (generally of the form YYYYMMDD.r) dot characters(.) will be removed')

    args = parser.parse_args()

    service_name = args.service_name.replace('_', '-')
    build_id = format_build_id(args.build_id)
    sdk_path = args.sdk_path

    packages = get_packages(sdk_path)
    target_packages = [pkg for pkg in packages if is_in_service(sdk_path, pkg[0], service_name)]

    if not target_packages:
        print(f"No packages found for service {service_name}")

    for target_package in target_packages:
        try:
            new_version = get_dev_version(target_package[1][1], build_id)
            print(f'{target_package[1][0]}: {target_package[1][1]} -> {new_version}')

            set_version_py(target_package[0], new_version)
            set_dev_classifier(target_package[0], new_version)
        except:
            print(f'Could not set dev version for package: {target_package[1][0]}')