import re
import importlib
import pkgutil
import sys
from pathlib import Path

sdk_root = Path(__file__).parents[1]

package_name = sys.argv[1]
module_name = package_name.replace("-", ".")

sys.path.append(str((sdk_root / package_name).resolve()))

module_to_generate = importlib.import_module(module_name)
versionned_modules = [(label, importlib.import_module('.'+label, module_to_generate.__name__))
                       for (_, label, ispkg) in pkgutil.iter_modules(module_to_generate.__path__)
                       if label.startswith("v20") and ispkg]

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


# Print models
print("""    @classmethod
    def models(cls, api_version=DEFAULT_API_VERSION):""")

template_models_if = """        {first}if api_version == '{api_version}':
            from .{api_version_module} import models
            return models"""
template_models_end_def = """        raise NotImplementedError("APIVersion {} is not available".format(api_version))
"""

template_intro_doc= '        """Module depends on the API version:\n'
template_inside_doc="           * {api_version}: :mod:`{api_version_module}.models<{module_name}.{api_version_module}.models>`"
template_end_doc='        """'

print(template_intro_doc)
for attr in sorted(mod_to_api_version.keys()):
    print(template_inside_doc.format(
        module_name=module_name,
        api_version=mod_to_api_version[attr],
        api_version_module=attr))
print(template_end_doc)

first = True
for attr in sorted(mod_to_api_version.keys()):
    print(template_models_if.format(
        first='' if first else 'el',
        api_version=mod_to_api_version[attr],
        api_version_module=attr))
    first = False
print(template_models_end_def)


# Print operation group

template_def = "    @property\n    def {attr}(self):"
template_intro_doc= '        """Instance depends on the API version:\n'
template_inside_doc="           * {api_version}: :class:`{clsname}<{module_name}.{api_version_module}.operations.{clsname}>`"
template_end_doc='        """'
template_if = """        {first}if self.api_version == '{api_version}':
            from .{api_version_module}.operations import {clsname} as OperationClass"""
template_end_def = """        else:
            raise NotImplementedError("APIVersion {} is not available".format(self.api_version))
        return OperationClass(self._client, self.config, self._serialize, self._deserialize)
"""

for attr in sorted(version_dict.keys()):
    versions = version_dict[attr]
    print(template_def.format(attr=attr))
    print(template_intro_doc)
    for version in versions:
        print(template_inside_doc.format(
            api_version=mod_to_api_version[version[0]],
            api_version_module=version[0],
            module_name=module_name,
            clsname=version[1]))            
    print(template_end_doc)
    first = True
    for version in versions:
        print(template_if.format(
            first='' if first else 'el',
            api_version=mod_to_api_version[version[0]],
            api_version_module=version[0],
            clsname=version[1]))
        first = False
    print(template_end_def)
