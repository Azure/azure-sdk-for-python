# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import hashlib
import logging
from collections import defaultdict
from typing import Union, List, Dict

from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._builders import BaseNode


logger = logging.getLogger(__name__)


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

    def __init__(self, resolver):
        self._resolver = resolver
        self._component_resolution_cache: Dict[str, str] = {}
        self._component_cache: Dict[str, Component] = {}
        self._hash_of_components_to_resolve: List[str] = []
        self._nodes_to_apply: Dict[str, List[BaseNode]] = defaultdict(list)

    def _resolve_component(self, component: Union[str, Component]) -> str:
        """Resolve a component with self._resolver."""
        return self._resolver(component, azureml_type=AzureMLResourceType.COMPONENT)

    @classmethod
    def _get_component_hash(cls, component: Component) -> str:
        """Get a hash for a component."""
        # For components with code, its code will be an absolute path before uploaded to blob,
        # so we can use a mixture of its anonymous hash and its source path as its hash, in case
        # there are 2 components with same code but different ignore files
        # Here we can check if the component has a source path instead of check if it has code, as
        # there is no harm to add a source path to the hash even if the component doesn't have code
        # Note that here we assume that the content of code folder won't change during the submission
        if component._source_path:  # pylint: disable=protected-access
            object_hash = hashlib.sha256()
            object_hash.update(component._get_anonymous_hash().encode("utf-8"))  # pylint: disable=protected-access
            object_hash.update(component._source_path.encode("utf-8"))  # pylint: disable=protected-access
            return cls._YAML_SOURCE_PREFIX + object_hash.hexdigest()
        # For components without code, like pipeline component, their dependencies have already
        # been resolved before calling this function, so we can use their anonymous hash directly
        return cls._ANONYMOUS_HASH_PREFIX + component._get_anonymous_hash()  # pylint: disable=protected-access

    def register_node_to_resolve(self, node: BaseNode):
        """Register a node with its component to resolve.
        """
        component = node._component  # pylint: disable=protected-access

        # directly resolve node if the resolution involves no remote call
        # so that no node will be registered when create_or_update a subgraph
        if isinstance(component, str):
            node._component = self._resolve_component(component)  # pylint: disable=protected-access
            return
        if component.id is not None:
            node._component = component.id  # pylint: disable=protected-access
            return

        # 1 possible optimization is to save an id(component) -> component hash map here to
        # avoid duplicate hash calculation. The risk is that we haven't implicitly forbidden component
        # modification after it's been used in a node, and we can't guarantee that the hash is still
        # valid after modification.
        component_hash = self._get_component_hash(component)
        if component_hash not in self._component_cache:
            self._hash_of_components_to_resolve.append(component_hash)
            self._component_cache[component_hash] = component

        self._nodes_to_apply[component_hash].append(node)

    def _resolve_components_without_in_memory_cache(self):
        """Resolve all components to resolve and save the results in cache.
        """
        # TODO: apply local cache controlled by an environment variable here
        # Note that we should recalculate the hash based on code for local cache, as
        # we can't assume that the code folder won't change among dependency resolution
        # TODO: do concurrent resolution controlled by an environment variable here
        # given deduplication has already been done, we can safely assume that there is no
        # conflict in concurrent local cache access
        # multiprocessing need to dump input objects before starting a new process, which will fail
        # on _AttrDict for now, so put off the concurrent resolution
        for component_hash in self._hash_of_components_to_resolve:
            self._component_resolution_cache[component_hash] = self._resolve_component(
                self._component_cache[component_hash]
            )

        self._hash_of_components_to_resolve.clear()

    def resolve_nodes(self):
        """Resolve all dependent components with resolver and set resolved component arm id back to newly
        registered nodes. Registered nodes will be cleared after resolution.
        """
        if self._hash_of_components_to_resolve:
            self._resolve_components_without_in_memory_cache()

        for component_hash, nodes in self._nodes_to_apply.items():
            for node in nodes:
                resolution_result = self._component_resolution_cache[component_hash]

                # hack: parallel.task.code won't be resolved for now, but parallel.task can be a reference
                # to parallel._component.task, then it will change to an arm id after resolving parallel._component
                # However, if we have avoided duplicate resolution with in-memory cache, such change won't happen,
                # so we need to do it manually here
                # The ideal solution should be done after PRS team decides how to handle parallel.task.code
                from azure.ai.ml.entities import ParallelComponent, Parallel
                resolved_component = self._component_cache[component_hash]
                if isinstance(node, Parallel) and isinstance(resolved_component, ParallelComponent):
                    origin_component: ParallelComponent = node._component  # pylint: disable=protected-access
                    if id(node.task) == id(origin_component.task):
                        node.task.code = resolved_component.task.code

                node._component = resolution_result  # pylint: disable=protected-access
        self._nodes_to_apply.clear()
