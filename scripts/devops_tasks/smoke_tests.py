import logging
import importlib
import pkg_resources
from common_tasks import get_package_details

if __name__ == "__main__":
    packages = [
        (p.project_name, p.version, p.module_path)
        for p in pkg_resources.working_set
        if p.project_name.startswith("azure")
    ]
    logging.info('')
    for pkg in packages:
        if not pkg[0].startswith('azure'):
            continue
        qualified_namespace = get_package_details(pkg[2] + "/setup.py")[1]
        logging.info("Importing the library {}".format(qualified_namespace))
        try:
            package = importlib.__import__(qualified_namespace, fromlist=["__all__"])
            clients = [p for p in package.__all__ if p.endswith('Client')]
            importlib.__import__(qualified_namespace, fromlist=clients)
        except ModuleNotFoundError as err:
            logging.warning(err)
