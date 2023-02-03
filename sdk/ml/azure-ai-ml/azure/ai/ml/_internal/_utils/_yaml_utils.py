# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import strictyaml


class _SafeLoaderWithBaseLoader(strictyaml.ruamel.SafeLoader):
    def fetch_comment(self, comment):
        pass

    def add_version_implicit_resolver(self, version, tag, regexp, first):
        """Overwrite the method to use base resolver instead of version default resolver."""
        self._version_implicit_resolver.setdefault(version, {})


def yaml_safe_load_with_base_resolver(stream):
    """Load yaml string with base resolver instead of version default resolver."""
    return strictyaml.ruamel.load(stream, Loader=_SafeLoaderWithBaseLoader)
