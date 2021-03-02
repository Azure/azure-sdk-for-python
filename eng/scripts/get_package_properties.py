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

    for p in glob.glob(args.search_path, recursive=True):
        if os.path.basename(os.path.dirname(p)) != 'azure-mgmt' and os.path.basename(os.path.dirname(p)) != 'azure' and os.path.basename(os.path.dirname(p)) != 'azure-storage':
            print(get_package_properties(os.path.dirname(p)))