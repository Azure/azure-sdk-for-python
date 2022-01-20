import logging
from common_tasks import get_all_track2_packages

if __name__ == '__main__':
    packages = get_all_track2_packages('.')
    print(packages)
    for pkg in packages:
        logging.info('Importing the library {}'.format(pkg[0]))
        qualified_namespace = pkg[0].replace('-', '.')
        logging.info('Importing the library {}'.format(qualified_namespace))
        exec('from {} import *'.format(qualified_namespace))
