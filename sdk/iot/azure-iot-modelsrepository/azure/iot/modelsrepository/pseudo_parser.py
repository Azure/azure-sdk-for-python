# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""This module contains a partial parsing implementation that is strictly
scoped for parsing dependencies. Ideally, this would be made obsolete by
a full Python parser implementation, as it is supposed to be a single source
of truth for the DTDL model specifications.

Note that this implementation is not representative of what an eventual full
parser implementation would necessarily look like from an API perspective
"""


class PseudoParser(object):
    def __init__(self, resolver):
        self.resolver = resolver

    def expand(self, models):
        """"""
        expanded_map = {}
        for model in models:
            expanded_map[model["@id"]] = model
            self._expand(model, expanded_map)
        return expanded_map

    def _expand(self, model, model_map):
        dependencies = get_dependency_list(model)
        dependencies_to_resolve = [
            dependency for dependency in dependencies if dependency not in model_map
        ]

        if dependencies_to_resolve:
            resolved_dependency_map = self.resolver.resolve(dependencies_to_resolve)
            model_map.update(resolved_dependency_map)
            for dependency_model in resolved_dependency_map.items():
                self._expand(dependency_model, model_map)


def get_dependency_list(model):
    """Return a list of DTMIs for model dependencies"""
    if "contents" in model:
        components = [item["schema"] for item in model["contents"] if item["@type"] == "Component"]
    else:
        components = []

    if "extends" in model:
        # Models defined in a DTDL can implement extensions of up to two interfaces
        if isinstance(model["extends"], list):
            interfaces = model["extends"]
        else:
            interfaces = [model["extends"]]
    else:
        interfaces = []

    dependencies = components + interfaces
    return dependencies
