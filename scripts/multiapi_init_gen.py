import argparse
import ast
import importlib
import inspect
import logging
import os
import pkgutil
import re
import sys
import shutil
import json
from collections import defaultdict
from pathlib import Path

from typing import List, Tuple, Any, Union

try:
    import msrestazure
except:  # Install msrestazure. Would be best to mock it, since we don't need it, but all scenarios I know are fine with a pip install for now
    import subprocess

    subprocess.call(
        sys.executable + " -m pip install msrestazure", shell=True
    )  # Use shell to use venv if available

try:
    from jinja2 import Template, FileSystemLoader, Environment
except:
    import subprocess

    subprocess.call(
        sys.executable + " -m pip install jinja2", shell=True
    )  # Use shell to use venv if available
    from jinja2 import Template, FileSystemLoader, Environment


try:
    import azure.common
except:
    sys.path.append(
        str((Path(__file__).parents[1] / "sdk" / "core" / "azure-common").resolve())
    )
    import azure.common

import pkg_resources

pkg_resources.declare_namespace("azure")

_LOGGER = logging.getLogger(__name__)


def parse_input(input_parameter):
    """From a syntax like package_name#submodule, build a package name
    and complete module name.
    """
    split_package_name = input_parameter.split("#")
    package_name = split_package_name[0]
    module_name = package_name.replace("-", ".")
    if len(split_package_name) >= 2:
        module_name = ".".join([module_name, split_package_name[1]])
    return package_name, module_name


# given an input of a name, we need to return the appropriate relative diff between the sdk_root and the actual package directory
def resolve_package_directory(package_name, sdk_root=None):
    packages = [
        p.parent
        for p in (
            list(sdk_root.glob("{}/setup.py".format(package_name)))
            + list(sdk_root.glob("sdk/*/{}/setup.py".format(package_name)))
        )
    ]

    if len(packages) > 1:
        print(
            "There should only be a single package matched in either repository structure. The following were found: {}".format(
                packages
            )
        )
        sys.exit(1)

    return str(packages[0].relative_to(sdk_root))

def get_paths_to_versions(path_to_package: str) -> List[str]:

    paths_to_versions = []
    for child in [x for x in path_to_package.iterdir() if x.is_dir()]:
        child_dir = (path_to_package / child).resolve()
        if Path(child_dir / '_metadata.json') in [x for x in child_dir.iterdir()]:
            paths_to_versions.append(child_dir)
    return paths_to_versions


class ApiVersionExtractor(ast.NodeVisitor):
    def __init__(self, *args, **kwargs):
        self.api_version = None
        super(ApiVersionExtractor, self).__init__(*args, **kwargs)

    def visit_Assign(self, node):
        try:
            if node.targets[0].id == "api_version":
                self.api_version = node.value.s
        except Exception:
            pass


def extract_api_version_from_code(function):
    """Will extract from __code__ the API version. Should be use if you use this is an operation group with no constant api_version.
    """
    try:
        srccode = inspect.getsource(function)
        try:
            ast_tree = ast.parse(srccode)
        except IndentationError:
            ast_tree = ast.parse("with 0:\n" + srccode)

        api_version_visitor = ApiVersionExtractor()
        api_version_visitor.visit(ast_tree)
        return api_version_visitor.api_version
    except Exception:
        raise


def get_client_class_name_from_module(module):
    """Being a module that is an Autorest generation, get the client name."""
    # Using the fact that Client is always the first element in __all__
    # I externalize that code in a class in case we need to be smarter later
    return module.__all__[0]


def build_operation_meta(paths_to_versions):
    """Introspect the client:

    version_dict => {
        'application_gateways': [
            ('v2018_05_01', 'ApplicationGatewaysOperations')
        ]
    }
    mod_to_api_version => {'v2018_05_01': '2018-05-01'}
    """
    mod_to_api_version = defaultdict(str)
    versioned_operations_dict = defaultdict(list)
    for version_path in paths_to_versions:
        with open(version_path / "_metadata.json") as f:
            metadata_json = json.load(f)
        operation_groups = metadata_json['operation_groups']
        version = metadata_json['version']
        mod_to_api_version[version_path.name] = version
        for operation_group, operation_group_class_name in operation_groups.items():
            versioned_operations_dict[operation_group].append((version_path.name, operation_group_class_name))
    # raise ValueError(versioned_operations_dict)
    return versioned_operations_dict, mod_to_api_version


def build_operation_mixin_meta(paths_to_versions):
    """Introspect the client:

    version_dict => {
        'check_dns_name_availability': {
            'doc': 'docstring',
            'signature': '(self, p1, p2, **operation_config),
            'call': 'p1, p2',
            'available_apis': [
                'v2018_05_01'
            ]
        }
    }
    """
    mixin_operations = {}
    for version_path in paths_to_versions:
        with open(version_path / "_metadata.json") as f:
            metadata_json = json.load(f)
        if not metadata_json.get('operation_mixin_functions'):
            continue
        for func_name, func in metadata_json['operation_mixin_functions'].items():
            if func_name.startswith("_"):
                continue
            mixin_operations.setdefault(func_name, {}).setdefault(
                "available_apis", []
            ).append(version_path.name)
            mixin_operations[func_name]['doc'] = func['doc']
            mixin_operations[func_name]['signature'] = func['signature']
            mixin_operations[func_name][call] = func['call']
    return mixin_operations


def build_last_rt_list(
    versioned_operations_dict, mixin_operations, last_api_version, preview_mode
):
    """Build the a mapping RT => API version if RT doesn't exist in latest detected API version.

    Example:
    last_rt_list = {
       'check_dns_name_availability': '2018-05-01'
    }

    There is one subtle scenario if PREVIEW mode is disabled:
    - RT1 available on 2019-05-01 and 2019-06-01-preview
    - RT2 available on 2019-06-01-preview
    - RT3 available on 2019-07-01-preview

    Then, if I put "RT2: 2019-06-01-preview" in the list, this means I have to make
    "2019-06-01-preview" the default for models loading (otherwise "RT2: 2019-06-01-preview" won't work).
    But this likely breaks RT1 default operations at "2019-05-01", with default models at "2019-06-01-preview"
    since "models" are shared for the entire set of operations groups (I wished models would be split by operation groups, but meh, that's not the case)

    So, until we have a smarter Autorest to deal with that, only preview RTs which do not share models with a stable RT can be added to this map.
    In this case, RT2 is out, RT3 is in.
    """

    def there_is_a_rt_that_contains_api_version(rt_dict, api_version):
        "Test in the given api_version is is one of those RT."
        for rt_api_version in rt_dict.values():
            if api_version in rt_api_version:
                return True
        return False

    last_rt_list = {}

    # Operation groups
    versioned_dict = {
        operation_name: [meta[0] for meta in operation_metadata]
        for operation_name, operation_metadata in versioned_operations_dict.items()
    }
    # Operations at client level
    versioned_dict.update(
        {
            operation_name: operation_metadata["available_apis"]
            for operation_name, operation_metadata in mixin_operations.items()
        }
    )
    for operation, api_versions_list in versioned_dict.items():
        local_last_api_version = get_floating_latest(api_versions_list, preview_mode)
        if local_last_api_version == last_api_version:
            continue
        # If some others RT contains "local_last_api_version", and it's greater than the future default, danger, don't profile it
        if (
            there_is_a_rt_that_contains_api_version(
                versioned_dict, local_last_api_version
            )
            and local_last_api_version > last_api_version
        ):
            continue
        last_rt_list[operation] = local_last_api_version
    return last_rt_list


def get_floating_latest(api_versions_list, preview_mode):
    """Get the floating latest, from a random list of API versions.
    """
    api_versions_list = list(api_versions_list)
    absolute_latest = sorted(api_versions_list)[-1]
    trimmed_preview = [
        version for version in api_versions_list if "preview" not in version
    ]

    # If there is no preview, easy: the absolute latest is the only latest
    if not trimmed_preview:
        return absolute_latest

    # If preview mode, let's use the absolute latest, I don't care preview or stable
    if preview_mode:
        return absolute_latest

    # If not preview mode, and there is preview, take the latest known stable
    return sorted(trimmed_preview)[-1]


def find_module_folder(package_name, module_name):
    sdk_root = Path(__file__).parents[1]
    _LOGGER.debug("SDK root is: %s", sdk_root)
    path_to_package = resolve_package_directory(package_name, sdk_root)
    module_path = (
        sdk_root / Path(path_to_package) / Path(module_name.replace(".", os.sep))
    )
    _LOGGER.debug("Module path is: %s", module_path)
    return module_path


def find_client_file(package_name, module_name):
    module_path = find_module_folder(package_name, module_name)
    return next(module_path.glob("*_client.py"))


def patch_import(file_path: Union[str, Path]) -> None:
    """If multi-client package, we need to patch import to be
    from ..version
    and not
    from .version

    That should probably means those files should become a template, but since right now
    it's literally one dot, let's do it the raw way.
    """
    # That's a dirty hack, maybe it's worth making configuration a template?
    with open(file_path, "rb") as read_fd:
        conf_bytes = read_fd.read()
    conf_bytes = conf_bytes.replace(
        b" .version", b" ..version"
    )  # Just a dot right? Worth its own template for that? :)
    with open(file_path, "wb") as write_fd:
        write_fd.write(conf_bytes)


def main(input_str, default_api=None):

    # If True, means the auto-profile will consider preview versions.
    # If not, if it exists a stable API version for a global or RT, will always be used
    preview_mode = default_api and "preview" in default_api

    # The only known multi-client package right now is azure-mgmt-resource
    is_multi_client_package = "#" in input_str

    package_name, module_name = parse_input(input_str)
    sdk_root = Path(__file__).parents[1]

    path_to_package = (
        sdk_root / resolve_package_directory(package_name, sdk_root) /
        "azure" / "mgmt" / "storage"
    ).resolve()
    paths_to_versions = get_paths_to_versions(path_to_package)
    versioned_operations_dict, mod_to_api_version = build_operation_meta(
        paths_to_versions
    )

    last_api_version = get_floating_latest(mod_to_api_version.keys(), preview_mode)

    # I need default_api to be v2019_06_07_preview shaped if it exists, let's be smart
    # and change it automatically so I can take both syntax as input
    if default_api and not default_api.startswith("v"):
        last_api_version = [
            mod_api
            for mod_api, real_api in mod_to_api_version.items()
            if real_api == default_api
        ][0]
        _LOGGER.info("Default API version will be: %s", last_api_version)

    last_api_path = path_to_package / last_api_version

    # In case we are transitioning from a single api generation, clean old folders
    shutil.rmtree(str(path_to_package / "operations"), ignore_errors=True)
    shutil.rmtree(str(path_to_package / "models"), ignore_errors=True)

    shutil.copy(
        str(path_to_package / last_api_version / "_configuration.py"),
        str(path_to_package / "_configuration.py"),
    )
    shutil.copy(
        str(path_to_package / last_api_version / "__init__.py"),
        str(path_to_package / "__init__.py"),
    )
    if is_multi_client_package:
        _LOGGER.warning("Patching multi-api client basic files")
        patch_import(path_to_package / "_configuration.py")
        patch_import(path_to_package / "__init__.py")



    # Detect if this client is using an operation mixin (Network)
    # Operation mixins are available since Autorest.Python 4.x
    mixin_operations = build_operation_mixin_meta(paths_to_versions)

    # get client name from latest api version
    with open(paths_to_versions[-1] / "_metadata.json") as f:
        metadata_json = json.load(f)


    # versioned_operations_dict => {
    #     'application_gateways': [
    #         ('v2018-05-01', 'ApplicationGatewaysOperations')
    #     ]
    # }
    # mod_to_api_version => {'v2018-05-01': '2018-05-01'}
    # mixin_operations => {
    #     'check_dns_name_availability': {
    #         'doc': 'docstring',
    #         'signature': '(self, p1, p2, **operation_config),
    #         'call': 'p1, p2',
    #         'available_apis': [
    #             'v2018_05_01'
    #         ]
    #     }
    # }
    # last_rt_list = {
    #    'check_dns_name_availability': '2018-05-01'
    # }

    last_rt_list = build_last_rt_list(
        versioned_operations_dict, mixin_operations, last_api_version, preview_mode
    )

    conf = {
        "client_name": metadata_json["client"]["name"],
        "has_subscription_id": metadata_json["client"]["has_subscription_id"],
        "module_name": module_name,
        "operations": versioned_operations_dict,
        "mixin_operations": mixin_operations,
        "mod_to_api_version": mod_to_api_version,
        "last_api_version": mod_to_api_version[last_api_version],
        "client_doc": metadata_json["client"]["description"],
        "last_rt_list": last_rt_list,
        "default_models": sorted(
            {last_api_version} | {versions for _, versions in last_rt_list.items()}
        ),
    }

    env = Environment(
        loader=FileSystemLoader(str(Path(__file__).parents[0] / "templates")),
        keep_trailing_newline=True,
    )

    for template_name in env.list_templates():
        # Don't generate files if they is not operations mixins
        if template_name == "_operations_mixin.py" and not mixin_operations:
            continue

        # Some file doesn't use the template name
        if template_name == "_multiapi_client.py":
            output_filename = metadata_json["client"]["filename"]
        else:
            output_filename = template_name

        future_filepath = path_to_package / output_filename

        template = env.get_template(template_name)
        result = template.render(**conf)

        with future_filepath.open("w") as fd:
            fd.write(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Multi-API client generation for Azure SDK for Python"
    )
    parser.add_argument(
        "--debug", dest="debug", action="store_true", help="Verbosity in DEBUG mode"
    )
    parser.add_argument(
        "--default-api-version",
        dest="default_api",
        default=None,
        help="Force default API version, do not detect it. [default: %(default)s]",
    )
    parser.add_argument("package_name", help="The package name.")

    args = parser.parse_args()

    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    main(args.package_name, default_api=args.default_api)
