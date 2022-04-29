import logging
import importlib
from common_tasks import get_all_track2_packages

if __name__ == '__main__':
    packages = get_all_track2_packages('.')
    for pkg in packages:
        qualified_namespace = pkg[0].replace('-', '.')
        logging.info('Importing the library {}'.format(qualified_namespace))
        try:
            importlib.__import__(qualified_namespace, globals(), locals(), ['__all__'], 0)
        except ModuleNotFoundError as err:
            logging.warning(err)
