# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import uuid
from collections import defaultdict
from typing import Union, Tuple, List

from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._builders import BaseNode


class CachedNodeResolver(object):
    """Class to resolve component in nodes with cached component resolution results.

    This class is thread-safe if:
    1) self._resolve_nodes and self._register_node_to_resolve are not called concurrently in the same thread
    2) self._resolve_component is only called concurrently on independent components
        a) we have used a component hash to deduplicate components to resolve;
        b) nodes are registered & resolved layer by layer, so all child components are already resolved
          when we register a pipeline node;
        c) potential shared dependencies like compute and data have been resolved before calling self._resolve_nodes.
    """
    _ANONYMOUS_HASH_PREFIX = "anonymous_component:"
    _YAML_SOURCE_PREFIX = "yaml_source:"
    _ORIGIN_PREFIX = "origin:"

    def __init__(self, resolver):
        self._resolver = resolver
        self._component_resolution_cache = {}
        self._components_to_resolve: List[Tuple[str, Component]] = []
        self._nodes_to_apply = defaultdict(list)

    def _resolve_component(self, component: Union[str, Component]) -> str:
        """Resolve a component with self._resolver."""
        return self._resolver(component, azureml_type=AzureMLResourceType.COMPONENT)

    @classmethod
    def _get_component_hash(cls, component: Union[Component, str]):
        """Get a hash for a component."""
        if isinstance(component, str):
            # component can be arm string like "train_model:1"
            return cls._ORIGIN_PREFIX + component

        # TODO: add hash function here
        # for pipeline component, all dependencies of pipeline component has already been resolved
        # so we can safely use its anonymous hash
        # for non-pipeline component, we can't directly use anonymous hash as code hasn't been uploaded yet
        # return a random hash by default
        return cls._ANONYMOUS_HASH_PREFIX + str(uuid.uuid4())

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
            self._components_to_resolve.append((component_hash, component))
            # set corresponding resolution cache to None to avoid duplicate resolution
            self._component_resolution_cache[component_hash] = None

        self._nodes_to_apply[component_hash].append(node)

    def _resolve_components_without_in_memory_cache(self):
        """Resolve all components to resolve and save the results in cache.
        """
        # TODO: Shouldn't reach this function when trying to resolve a subgraph
        # TODO: apply local cache controlled by an environment variable here
        # TODO: do concurrent resolution controlled by an environment variable here
        # given deduplication has already been done, we can safely assume that there is no
        # conflict in concurrent local cache access
        # multiprocessing need to dump input objects before starting a new process, which will fail
        # on _AttrDict for now, so put off the concurrent resolution
        for component_hash, component in self._components_to_resolve:
            self._component_resolution_cache[component_hash] = self._resolve_component(component)

        self._components_to_resolve.clear()

    def resolve_nodes(self):
        """Resolve all dependent components with resolver and set resolved component arm id back to newly
        registered nodes. Registered nodes will be cleared after resolution.
        """
        if self._components_to_resolve:
            self._resolve_components_without_in_memory_cache()

        for component_hash, nodes in self._nodes_to_apply.items():
            for node in nodes:
                node._component = self._component_resolution_cache[component_hash]  # pylint: disable=protected-access
        self._nodes_to_apply.clear()
