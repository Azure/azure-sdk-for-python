# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import uuid
from collections import defaultdict
from typing import Union, Callable, Dict

from azure.ai.ml.entities import Component
from azure.ai.ml.entities._builders import BaseNode


class CachedNodeResolver(object):
    """Class to resolve component in nodes with cached component resolution results.
    """
    def __init__(self, resolver: Callable[[Union[str, Component]], str]):
        self._resolver = resolver
        self._component_resolution_cache = {}
        self._new_components: Dict[str, Component] = {}
        self._nodes_to_apply = defaultdict(list)

    @classmethod
    def _get_component_hash(cls, component: Union[Component, str]):
        """Get a hash for a component."""
        if isinstance(component, str):
            # component can be arm string like "train_model:1"
            return component
        # TODO: add hash function here
        # for pipeline component, all dependencies of pipeline component has already been resolved
        # so we can safely use its anonymous hash
        # for non-pipeline component, we can't directly use anonymous hash as code hasn't been uploaded yet
        # return a random hash by default
        return str(uuid.uuid4())

    def register_node_to_resolve(self, node: BaseNode):
        """Register a node with its component to resolve.
        """
        component = node._component  # pylint: disable=protected-access
        # 1 possible optimization is to save an id(component) -> component hash map here to
        # avoid duplicate hash calculation. The risk is that we haven't implicitly forbidden component
        # modification after it's been used in a node, and we can't guarantee that the hash is still
        # valid after modification.
        component_hash = self._get_component_hash(component)
        if component_hash not in self._component_resolution_cache:
            self._new_components[component_hash] = component
            self._component_resolution_cache[component_hash] = None

        self._nodes_to_apply[component_hash].append(node)

    def resolve_nodes(self):
        """Resolve all dependent components with resolver and set resolved component arm id back to newly
        registered nodes. Registered nodes will be cleared after resolution.
        """
        for component_hash, component in self._new_components.items():
            # TODO: apply local cache controlled by an environment variable here
            # TODO: do concurrent resolution controlled by an environment variable here
            # given deduplication has already been done, we can safely assume that there is no
            # conflict in concurrent local cache access
            component_id = self._resolver(component)
            self._component_resolution_cache[component_hash] = component_id

        self._new_components.clear()

        for component_hash, nodes in self._nodes_to_apply.items():
            for node in nodes:
                node._component = self._component_resolution_cache[component_hash]  # pylint: disable=protected-access
        self._nodes_to_apply.clear()
