import os
import argparse

from version_shared import get_packages, set_version_py, set_dev_classifier

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Increments version for a given package name based on the released version')
    
    parser.add_argument('--package-name', required=True, help='name of package (accetps both formats: azure-service-package and azure_service_pacage)')
    parser.add_argument('--new-version', required=True, help='new package version')
    parser.add_argument('--service', help='name of the service for which to set the dev build id (e.g. keyvault)')

    args = parser.parse_args()

    package_name = args.package_name.replace('_', '-')
    new_version = args.new_version

    if args.service:
        target_dir = os.path.join(root_dir, "sdk", args.service)
    else:
        target_dir = os.path.join(root_dir, "sdk")
    
    packages = get_packages(args.glob_string, target_dir)
    package_map = { pkg[1][0]: pkg for pkg in packages }

    if package_name not in package_map:
        raise ValueError("Package name not found: %s" % package_name)

    target_package = package_map[package_name]

    print(f'{package_name}: {target_package[1][1]} -> {new_version}')

    set_version_py(target_package[0], new_version)
    set_dev_classifier(target_package[0], new_version)