import argparse
import logging
import json
from pathlib import Path

CONFIG_FILE = '../swagger_to_sdk_config.json'

_LOGGER = logging.getLogger(__name__)

SUBMODULE_TEMPLATE = """{namespace}.{submodule} module
===========================================

.. automodule:: {namespace}.{submodule}
    :members:
    :undoc-members:
    :show-inheritance:
"""
PACKAGE_TEMPLATE = """{namespace} package
==========================

Submodules
----------

.. toctree::

   {namespace}.models
   {namespace}.operations

Module contents
---------------

.. automodule:: {namespace}
    :members:
    :undoc-members:
    :show-inheritance:
"""
def generate_doc(config_path, project_pattern=None):

    with Path(config_path).open() as config_fd:
        config = json.load(config_fd)

    for project, local_conf in config["projects"].items():
        if project_pattern and not any(project.startswith(p) for p in project_pattern):
            _LOGGER.info("Skip project %s", project)
            continue

        if 'unreleased' in local_conf['output_dir'].lower():
            _LOGGER.info("Skip unreleased project %s", project)
            continue            

        _LOGGER.info("Working on %s", project)
        namespace = local_conf['autorest_options']['Namespace']

        with Path('./ref/{}.rst'.format(namespace)).open('w') as rst_file:
            rst_file.write(PACKAGE_TEMPLATE.format(
                namespace=namespace
            ))

        for module in ["operations", "models"]:
            with Path('./ref/{}.{}.rst'.format(namespace, module)).open('w') as rst_file:
                rst_file.write(SUBMODULE_TEMPLATE.format(
                    namespace=namespace,
                    submodule=module
                ))

def main():
    parser = argparse.ArgumentParser(
        description='Generate documentation file.'
    )
    parser.add_argument('--project', '-p',
                        dest='project', action='append',
                        help='Select a specific project. Do all by default. You can use a substring for several projects.')
    parser.add_argument('--config', '-c',
                        dest='config_path', default=CONFIG_FILE,
                        help='The JSON configuration format path [default: %(default)s]')
    parser.add_argument("-v", "--verbose",
                        dest="verbose", action="store_true",
                        help="Verbosity in INFO mode")
    parser.add_argument("--debug",
                        dest="debug", action="store_true",
                        help="Verbosity in DEBUG mode")

    args = parser.parse_args()

    main_logger = logging.getLogger()
    if args.verbose or args.debug:
        logging.basicConfig()
        main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    generate_doc(args.config_path, args.project)

if __name__ == "__main__":
    main()
