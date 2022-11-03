import logging
import importlib
from common_tasks import get_package_details, get_all_track2_packages

if __name__ == "__main__":
    packages = get_all_track2_packages('.')
    logging.info('list of packages being tested: {}'.format(packages))
    for pkg in packages:
        qualified_namespace = get_package_details(pkg[2] + "/setup.py")[1]
        logging.info("Importing the library {}".format(qualified_namespace))
        try:
            package = importlib.__import__(qualified_namespace, fromlist=["__all__"])
        except ModuleNotFoundError as err:
            logging.warning(err)
