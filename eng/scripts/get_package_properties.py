import sys
import glob
import os

sys.path.append(os.path.join('scripts', 'devops_tasks'))
from common_tasks import get_package_properties

def get_all_package_properties(search_path):
    for p in glob.glob(search_path, recursive=True):
        if os.path.basename(os.path.dirname(p)) != 'azure-mgmt' and os.path.basename(os.path.dirname(p)) != 'azure' and os.path.basename(os.path.dirname(p)) != 'azure-storage':
            print(get_package_properties(os.path.dirname(p)))