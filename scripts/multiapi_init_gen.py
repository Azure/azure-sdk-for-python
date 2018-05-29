import importlib
import os
import pkgutil
import re
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

try:
    import msrestazure
except:  # Install msrestazure. Would be best to mock it, since we don't need it, but all scenarios I know are fine with a pip install for now
    import subprocess
    subprocess.call(sys.executable + " -m pip install msrestazure", shell=True)  # Use shell to use venv if available

try:
    import azure.common
except:
    sdk_root = Path(__file__).parents[1]
    sys.path.append(str((sdk_root / "azure-common").resolve()))
    import azure.common

import pkg_resources
pkg_resources.declare_namespace('azure')

_GENERATE_MARKER = "############ Generated from here ############\n"

def parse_input(input_parameter):
    """From a syntax like package_name#submodule, build a package name
    and complete module name.
    """
    split_package_name = input_parameter.split('#')
    package_name = split_package_name[0]
    module_name = package_name.replace("-", ".")
    if len(split_package_name) >= 2:
        module_name = ".".join([module_name, split_package_name[1]])
    return package_name, module_name

def get_versionned_modules(package_name, module_name, sdk_root=None):
    if not sdk_root:
        sdk_root = Path(__file__).parents[1]

    azure.__path__.append(str((sdk_root / package_name / "azure").resolve()))
    # Doesn't work with namespace package
    # sys.path.append(str((sdk_root / package_name).resolve()))
    module_to_generate = importlib.import_module(module_name)
    return [(label, importlib.import_module('.'+label, module_to_generate.__name__))
            for (_, label, ispkg) in pkgutil.iter_modules(module_to_generate.__path__)
            if label.startswith("v20") and ispkg]

def build_operation_meta(versionned_modules):
    version_dict = {}
    mod_to_api_version = {}
    for versionned_label, versionned_mod in versionned_modules:
        extracted_api_version = None
        client_doc = versionned_mod.__dict__[versionned_mod.__all__[0]].__doc__
        operations = list(re.finditer(r':ivar (?P<attr>[a-z_]+): \w+ operations\n\s+:vartype (?P=attr): .*.operations.(?P<clsname>\w+)\n', client_doc))
        for operation in operations:
            attr, clsname = operation.groups()
            version_dict.setdefault(attr, []).append((versionned_label, clsname))
            if not extracted_api_version:
                # Create a fake operation group to extract easily the real api version
                try:
                    extracted_api_version = versionned_mod.operations.__dict__[clsname](None, None, None, None).api_version
                except Exception:
                    # Should not happen. I guess it mixed operation groups like VMSS Network...
                    pass
        if not extracted_api_version:
            sys.exit("Was not able to extract api_version of %s" % versionned_label)
        mod_to_api_version[versionned_label] = extracted_api_version

    # latest: api_version=mod_to_api_version[versions[-1][0]]

    return version_dict, mod_to_api_version


def build_models_string(module_name, mod_to_api_version):
    result = """    @classmethod
    def models(cls, api_version=DEFAULT_API_VERSION):
"""

    template_models_if = """
        {first}if api_version == '{api_version}':
            from .{api_version_module} import models
            return models"""
    template_models_end_def = """        raise NotImplementedError("APIVersion {} is not available".format(api_version))
    """

    template_intro_doc= '        """Module depends on the API version:\n'
    template_inside_doc="           * {api_version}: :mod:`{api_version_module}.models<{module_name}.{api_version_module}.models>`"
    template_end_doc='        """'

    result += template_intro_doc
    for attr in sorted(mod_to_api_version.keys()):
        result += "\n"
        result += template_inside_doc.format(
            module_name=module_name,
            api_version=mod_to_api_version[attr],
            api_version_module=attr)
    result += "\n"
    result += template_end_doc

    first = True
    for attr in sorted(mod_to_api_version.keys()):
        result += template_models_if.format(
            first='' if first else 'el',
            api_version=mod_to_api_version[attr],
            api_version_module=attr)
        first = False
    result += "\n"
    result += template_models_end_def
    return result


def build_operation_group(module_name, operation_name, versions):

    template_def = "    @property\n    def {attr}(self):\n"
    template_intro_doc= '        """Instance depends on the API version:\n\n'
    template_inside_doc="           * {api_version}: :class:`{clsname}<{module_name}.{api_version_module}.operations.{clsname}>`\n"
    template_end_doc='        """\n'
    template_code_prefix="        api_version = self._get_api_version('{attr}')"
    template_if = """        {first}if api_version == '{api_version}':
            from .{api_version_module}.operations import {clsname} as OperationClass"""
    template_end_def = """        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return OperationClass(self._client, self.config, Serializer(self._models_dict(api_version)), Deserializer(self._models_dict(api_version)))
"""
    result = template_def.format(attr=operation_name)
    result += template_intro_doc
    for version in versions:
        result += template_inside_doc.format(
            api_version=mod_to_api_version[version[0]],
            api_version_module=version[0],
            module_name=module_name,
            clsname=version[1])
    result += template_end_doc
    result += template_code_prefix.format(attr=operation_name)
    first = True
    for version in versions:
        result += "\n"
        result += template_if.format(
            first='' if first else 'el',
            api_version=mod_to_api_version[version[0]],
            api_version_module=version[0],
            clsname=version[1])
        first = False
    result += "\n"
    result += template_end_def
    return result

def find_client_file(package_name, module_name):
    module_path = Path(package_name) / Path(module_name.replace(".", os.sep))
    return next(module_path.glob('*_client.py'))

_CODE_PREFIX = """
    @classmethod
    def _models_dict(cls, api_version):
        return {k: v for k, v in cls.models(api_version).__dict__.items() if isinstance(v, type)}

"""

if __name__ == "__main__":
    package_name, module_name = parse_input(sys.argv[1])
    versionned_modules = get_versionned_modules(package_name, module_name)
    version_dict, mod_to_api_version = build_operation_meta(versionned_modules)
    model_string = build_models_string(module_name, mod_to_api_version)

    operations_string = []
    for attr in sorted(version_dict.keys()):
        versions = version_dict[attr]
        operations_string.append(build_operation_group(module_name, attr, versions))

    client_file = find_client_file(package_name, module_name)
    with open(client_file, "r") as read_client:
        lines = read_client.readlines()
    with open(client_file, "w", newline='\n') as write_client:
        for line in lines:
            write_client.write(line)
            if line == _GENERATE_MARKER:
                break
        else:
            sys.exit("Didn't find generate lines!!!!")

        write_client.write(_CODE_PREFIX)
        write_client.write(model_string)
        for operation in operations_string:
            write_client.write("\n")
            write_client.write(operation)

