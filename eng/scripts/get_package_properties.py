import argparse
import sys
import glob
import os

sys.path.append(os.path.join('scripts', 'devops_tasks'))
from common_tasks import get_package_properties

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get package version details from the repo')
    parser.add_argument('-s', '--search_path', required=True, help='The scope of the search')
    args = parser.parse_args()

    for root, dirs, files in os.walk(args.search_path):
        for filename in files:
            if os.path.basename(filename) == "setup.py":
                if os.path.basename(root) != 'azure-mgmt' and os.path.basename(root) != 'azure' and os.path.basename(root) != 'azure-storage' and os.path.basename(root) != 'tests':
                    pkgName, version, is_new_sdk, setup_py_path = get_package_properties(root)
                    print("{0} {1} {2} {3}".format(pkgName, version, is_new_sdk, setup_py_path))