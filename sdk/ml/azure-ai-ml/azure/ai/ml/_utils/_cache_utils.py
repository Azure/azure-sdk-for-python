# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import hashlib
import logging
from collections import defaultdict
from dataclasses import dataclass
from functools import partial
from typing import List, Dict, Optional

from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._builders import BaseNode


logger = logging.getLogger(__name__)

_ANONYMOUS_HASH_PREFIX = "anonymous_component:"
_YAML_SOURCE_PREFIX = "yaml_source:"


@dataclass
class _CacheContent:
    component_ref: Component
    in_memory_hash: Optional[str]
    arm_id: Optional[str] = None


class CachedNodeResolver(object):
    """Class to resolve component in nodes with cached component resolution results.

    This class is thread-safe if:
    1) self._resolve_nodes is not called concurrently in the same main thread
    2) self._resolve_component is only called concurrently on independent components
        a) we have used an in-memory component hash to deduplicate components to resolve first;
        b) nodes are registered & resolved layer by layer, so all child components are already resolved
          when we register a pipeline node;
        c) potential shared dependencies like compute and data have been resolved before
          calling self._resolve_component.
    """

    def __init__(self, resolver):
        self._resolver = resolver
        self._cache: Dict[str, _CacheContent] = {}
        self._nodes_to_resolve: List[BaseNode] = []

    @staticmethod
    def _get_in_memory_hash_for_component(component: Component) -> str:
        """Get a hash for a component."""
        if not isinstance(component, Component):
            # this shouldn't happen; handle it in case invalid call is made outside this class
            raise ValueError(f"Component {component} is not a Component object.")

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
            return _YAML_SOURCE_PREFIX + object_hash.hexdigest()
        # For components without code, like pipeline component, their dependencies have already
        # been resolved before calling this function, so we can use their anonymous hash directly
        return _ANONYMOUS_HASH_PREFIX + component._get_anonymous_hash()  # pylint: disable=protected-access

    @staticmethod
    def _resolve_cache_contents(cache_content_to_resolve: List[_CacheContent], resolver):
        """Resolve all components to resolve and save the results in cache.
        """
        _components = list(map(lambda x: x.component_ref, cache_content_to_resolve))

        # TODO: do concurrent resolution controlled by an environment variable here
        # given deduplication has already been done, we can safely assume that there is no
        # conflict in concurrent local cache access
        # multiprocessing need to dump input objects before starting a new process, which will fail
        # on _AttrDict for now, so put off the concurrent resolution
        _arm_ids = map(partial(resolver, azureml_type=AzureMLResourceType.COMPONENT), _components)

        for _cache_content, _arm_id in zip(cache_content_to_resolve, _arm_ids):
            _cache_content.arm_id = _arm_id

    def _prepare_items_to_resolve(self):
        """Pop all nodes in self._nodes_to_resolve to prepare cache contents to resolve and nodes to resolve.
        Nodes in self._nodes_to_resolve will be grouped by component hash and saved to a dict of list.
        Distinct dependent components not in current cache will be saved to a list.

        :return: a tuple of (dict of nodes to resolve, list of cache contents to resolve)
        """
        _components = list(map(lambda x: x._component, self._nodes_to_resolve))  # pylint: disable=protected-access
        # we can do concurrent component in-memory hash calculation here
        in_memory_component_hashes = map(self._get_in_memory_hash_for_component, _components)

        dict_of_nodes_to_resolve = defaultdict(list)
        cache_contents_to_resolve: List[_CacheContent] = []
        for node, component_hash in zip(self._nodes_to_resolve, in_memory_component_hashes):
            dict_of_nodes_to_resolve[component_hash].append(node)
            if component_hash not in self._cache:
                cache_content = _CacheContent(
                    component_ref=node._component,  # pylint: disable=protected-access
                    in_memory_hash=component_hash,
                )
                self._cache[component_hash] = cache_content
                cache_contents_to_resolve.append(cache_content)
        self._nodes_to_resolve.clear()
        return dict_of_nodes_to_resolve, cache_contents_to_resolve

    @classmethod
    def _resolve_cache_contents_from_disk(
        cls,
        cache_contents_to_resolve: List[_CacheContent]
    ) -> List[_CacheContent]:
        """Check on-disk cache to resolve cache contents in cache_contents_to_resolve and return
        unresolved cache contents.
        """
        # TODO: apply local cache controlled by an environment variable here
        # Note that we should recalculate the hash based on code for local cache, as
        # we can't assume that the code folder won't change among dependency resolution
        return cache_contents_to_resolve[:]

    def _fill_back_component_to_nodes(self, dict_of_nodes_to_resolve: Dict[str, List[BaseNode]]):
        """Fill back resolved component to nodes."""
        for component_hash, nodes in dict_of_nodes_to_resolve.items():
            cache_content = self._cache[component_hash]
            for node in nodes:
                # hack: parallel.task.code won't be resolved for now, but parallel.task can be a reference
                # to parallel._component.task, then it will change to an arm id after resolving parallel._component
                # However, if we have avoided duplicate resolution with in-memory cache, such change won't happen,
                # so we need to do it manually here
                # The ideal solution should be done after PRS team decides how to handle parallel.task.code
                from azure.ai.ml.entities import ParallelComponent, Parallel
                resolved_component = cache_content.component_ref
                if isinstance(node, Parallel) and isinstance(resolved_component, ParallelComponent):
                    origin_component: ParallelComponent = node._component  # pylint: disable=protected-access
                    if id(node.task) == id(origin_component.task):
                        node.task.code = resolved_component.task.code

                node._component = cache_content.arm_id  # pylint: disable=protected-access

    def _resolve_nodes(self):
        """Processing logic of self.resolve_nodes.
        Should not be called in subgraph creation.
        """
        dict_of_nodes_to_resolve, cache_contents_to_resolve = self._prepare_items_to_resolve()

        cache_contents_to_resolve = self._resolve_cache_contents_from_disk(cache_contents_to_resolve)

        self._resolve_cache_contents(cache_contents_to_resolve, resolver=self._resolver)

        self._fill_back_component_to_nodes(dict_of_nodes_to_resolve)

    def register_node_to_resolve(self, node: BaseNode):
        """Register a node with its component to resolve.
        """
        component = node._component  # pylint: disable=protected-access

        # directly resolve node if the resolution involves no remote call
        # so that no node will be registered when create_or_update a subgraph
        if isinstance(component, str):
            node._component = self._resolver(  # pylint: disable=protected-access
                component,
                azureml_type=AzureMLResourceType.COMPONENT
            )
            return
        if component.id is not None:
            node._component = component.id  # pylint: disable=protected-access
            return

        self._nodes_to_resolve.append(node)

    def resolve_nodes(self):
        """Resolve all dependent components with resolver and set resolved component arm id back to newly
        registered nodes. Registered nodes will be cleared after resolution.
        """
        if not self._nodes_to_resolve:
            return

        self._resolve_nodes()
