import argparse
import sys
import glob
import os
import re

sys.path.append(os.path.join('scripts', 'devops_tasks'))
from common_tasks import get_package_properties

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get package version details from the repo')
    parser.add_argument('-s', '--search_path', required=True, help='The scope of the search')
    args = parser.parse_args()

    # Use abspath for the os.walk because if setup parsing fails it often changes cwd which throws off the relative walk
    for root, dirs, files in os.walk(os.path.abspath(args.search_path)):
        if re.search(r"sdk[\\/][^\\/]+[\\/][^\\/]+$", root):
            if "setup.py" in files:
                try:
                    pkgName, version, is_new_sdk, setup_py_path = get_package_properties(root)
                    print("{0} {1} {2} {3}".format(pkgName, version, is_new_sdk, setup_py_path))
                except:
                    # Skip setup.py if the package cannot be parsed
                    pass