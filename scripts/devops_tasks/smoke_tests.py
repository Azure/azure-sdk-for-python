import importlib
import pkg_resources
from common_tasks import get_all_track2_packages

if __name__ == '__main__':
    packages = get_all_track2_packages('.')
    for pkg in packages:
        importlib.import_module(pkg[0].replace('-', '.'))
