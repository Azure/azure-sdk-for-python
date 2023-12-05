# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import typing

import strictyaml


class _SafeLoaderWithBaseLoader(strictyaml.ruamel.SafeLoader):
    """This is a SafeLoader with base resolver instead of version default resolver.

    Differences between BaseResolver and VersionedResolver:
    1) BaseResolver won't try to resolve node value. For example, "yes" and "no" will be resolved to "true"(bool)
    and "false"(bool) by VersionedResolver, but won't be resolved by BaseResolver.
    2) VersionedResolver will delay loading the pattern matching rules to pass yaml versions on loading.

    Given SafeLoader inherits from VersionedResolver, we can't directly remove VersionedResolver
    from the inheritance list. Instead, we overwrite add_version_implicit_resolver method to make
    _SafeLoaderWithBaseLoader._version_implicit_resolver empty. Then the resolver will act like a BaseResolver.
    """

    def fetch_comment(self, comment):
        pass

    def add_version_implicit_resolver(self, version, tag, regexp, first):
        """Overwrite the method to make the resolver act like a base resolver instead of version default resolver.

        :param version: version of yaml, like (1, 1)(yaml 1.1) and (1, 2)(yaml 1.2)
        :type version: VersionType
        :param tag: a tag indicating the type of the resolved node, e.g., tag:yaml.org,2002:bool.
        :type tag: Any
        :param regexp: the regular expression to match the node to be resolved
        :type regexp: Any
        :param first: a list of first characters to match
        :type first: Any
        """
        self._version_implicit_resolver.setdefault(version, {})


def yaml_safe_load_with_base_resolver(stream: typing.IO):
    """Load yaml string with base resolver instead of version default resolver.

    For example:
    1) "yes" and "no" will be loaded as "yes"(string) and "no"(string) instead of "true"(bool) and "false"(bool);
    2) "0.10" will be loaded as "0.10"(string) instead of "0.1"(float).
    3) "2019-01-01" will be loaded as "2019-01-01"(string) instead of "2019-01-01T00:00:00Z"(datetime).
    4) "1" will be loaded as "1"(string) instead of "1"(int).
    5) "1.0" will be loaded as "1.0"(string) instead of "1.0"(float).
    6) "~" will be loaded as "~"(string) instead of "None"(NoneType).

    Please refer to strictyaml.ruamel.resolver.implicit_resolvers for more details.

    :param stream: A readable stream
    :type stream: typing.IO
    :return: The return value of strictyaml.ruamel.load
    :rtype: Any
    """
    return strictyaml.ruamel.load(stream, Loader=_SafeLoaderWithBaseLoader)
