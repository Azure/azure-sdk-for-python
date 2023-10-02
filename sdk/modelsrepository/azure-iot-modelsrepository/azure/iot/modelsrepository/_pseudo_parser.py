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
import logging

_LOGGER = logging.getLogger(__name__)


class PseudoParser(object):
    def __init__(self, resolver):
        """
        :param resolver: The resolver for the parser to use to resolve model dependencies
        :type resolver: :class:`azure.iot.modelsrepository._resolver.DtmiResolver`
        """
        self.resolver = resolver

    def expand(self, models):
        """Return a dictionary containing all the provided models, as well as their dependencies,
        indexed by DTMI

        :param list[str] models: List of models

        :returns: Dictionary containing models and their dependencies, indexed by DTMI
        :rtype: dict
        """
        expanded_map = {}
        for model in models:
            expanded_map[model["@id"]] = model
            self._expand(model, expanded_map)
        return expanded_map

    def _expand(self, model, model_map):
        _LOGGER.debug("Expanding model: %s", model["@id"])
        dependencies = _get_model_dependencies(model)
        dependencies_to_resolve = [
            dependency for dependency in dependencies if dependency not in model_map
        ]

        if dependencies_to_resolve:
            _LOGGER.debug("Outstanding dependencies found: %s", dependencies_to_resolve)
            resolved_dependency_map = self.resolver.resolve(dependencies_to_resolve)
            model_map.update(resolved_dependency_map)
            for dependency_model in resolved_dependency_map.values():
                self._expand(dependency_model, model_map)
        else:
            _LOGGER.debug("No outstanding dependencies found")


def _get_model_dependencies(model):
    """Return a list of dependency DTMIs for a given model"""
    dependencies = []

    if "contents" in model:
        components = [item["schema"] for item in model["contents"] if item["@type"] == "Component"]
        dependencies += components

    if "extends" in model:
        # Models defined in a DTDL can implement extensions of up to two interfaces.
        # These interfaces can be in the form of a DTMI reference, or a nested model (which would
        # have it's own dependencies)
        if isinstance(model["extends"], str):
            # If it's just a string, that's a single DTMI reference, so just add that to our list
            dependencies.append(model["extends"])
        elif isinstance(model["extends"], list):
            # If it's a list, could have DTMIs or nested models
            for item in model["extends"]:
                if isinstance(item, str):
                    # If there are strings in the list, that's a DTMI reference, so add it
                    dependencies.append(item)
                elif isinstance(item, dict):
                    # This is a nested model. Now go get its dependencies and add them
                    dependencies += _get_model_dependencies(item)

    # Remove duplicate dependencies
    dependencies = list(set(dependencies))
    return dependencies
