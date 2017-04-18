import argparse
import logging
import json
from pathlib import Path

CONFIG_FILE = '../swagger_to_sdk_config.json'
GENERATED_PACKAGES_LIST_FILE = 'autorest_generated_packages.rst'

_LOGGER = logging.getLogger(__name__)

def make_title(title):
    """Create a underlined title with the correct number of =."""
    return "\n".join([title, len(title)*"="])

SUBMODULE_TEMPLATE = """{title}

.. automodule:: {namespace}.{submodule}
    :members:
    :undoc-members:
    :show-inheritance:
"""
PACKAGE_TEMPLATE = """{title}

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


RST_AUTODOC_TOCTREE = """.. toctree::
  :maxdepth: 5
  :glob:
  :caption: Developer Documentation

  ref/azure.common
{generated_packages}
  ref/azure.servicebus
  ref/azure.servicemanagement  
"""

MULTIAPI_VERSION_PACKAGE_TEMPLATE = """{title}

Module contents
---------------

.. automodule:: {namespace}
    :members:
    :undoc-members:
    :show-inheritance:

Submodules
----------

.. toctree::

"""

# Update the code to compute this list automatically
MULTIAPI_VERSION_NAMESPACE = [
    "azure.mgmt.storage",
    "azure.mgmt.network",
    "azure.mgmt.compute.compute",
    "azure.mgmt.compute.containerservice",
    "azure.mgmt.resource.resources",
    "azure.mgmt.resource.features",
    "azure.mgmt.resource.links",
    "azure.mgmt.resource.locks",
    "azure.mgmt.resource.policy",
    "azure.mgmt.resource.subscriptions",
]

def generate_doc(config_path, project_pattern=None):

    multiapi_found_apiversion = {}

    with Path(config_path).open() as config_fd:
        config = json.load(config_fd)
    package_list_path = []

    for project, local_conf in config["projects"].items():
        if project_pattern and not any(project.startswith(p) for p in project_pattern):
            _LOGGER.info("Skip project %s", project)
            continue

        if 'unreleased' in local_conf['output_dir'].lower():
            _LOGGER.info("Skip unreleased project %s", project)
            continue

        _LOGGER.info("Working on %s", project)
        namespace = local_conf['autorest_options']['Namespace']

        # Hack for KV, we don't release the generated code, but a wrapper
        # We do manually the doc
        if "azure.keyvault.generated" == namespace:
            package_list_path.append('./ref/azure.keyvault.rst')
            continue

        rst_path = './ref/{}.rst'.format(namespace) 
        with Path(rst_path).open('w') as rst_file:
            rst_file.write(PACKAGE_TEMPLATE.format(
                title=make_title(namespace+" package"),
                namespace=namespace
            ))

        for module in ["operations", "models"]:
            with Path('./ref/{}.{}.rst'.format(namespace, module)).open('w') as rst_file:
                rst_file.write(SUBMODULE_TEMPLATE.format(
                    title=make_title(namespace+"."+module+" module"),
                    namespace=namespace,
                    submodule=module
                ))

        for multiapi_namespace in MULTIAPI_VERSION_NAMESPACE:
            if namespace.startswith(multiapi_namespace):
                api_package = namespace.split(multiapi_namespace+".")[1]
                multiapi_found_apiversion.setdefault(multiapi_namespace, []).append(api_package)
                break
        else:
            package_list_path.append(rst_path)

    for multiapi_namespace, apilist in multiapi_found_apiversion.items():
        apilist.sort()
        apilist.reverse()
        rst_path = './ref/{}.rst'.format(multiapi_namespace)
        with Path(rst_path).open('w') as rst_file:
            rst_file.write(MULTIAPI_VERSION_PACKAGE_TEMPLATE.format(
                title=make_title(multiapi_namespace+" package"),
                namespace=multiapi_namespace
            ))
            for version in apilist:
                rst_file.write("   {namespace}.{version}\n".format(
                    namespace=multiapi_namespace,
                    version=version))
        package_list_path.append(rst_path)

    package_list_path.sort()
    with Path(GENERATED_PACKAGES_LIST_FILE).open('w') as generate_file_list_fd:
        lines_to_write = "\n".join(["  "+package for package in package_list_path])
        generate_file_list_fd.write(RST_AUTODOC_TOCTREE.format(generated_packages=lines_to_write))

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
