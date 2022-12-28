# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import hashlib
import logging
import os.path
from collections import defaultdict
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import List, Dict, Optional

from azure.ai.ml._utils._asset_utils import get_object_hash
from azure.ai.ml._utils.utils import is_on_disk_cache_enabled
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._builders import BaseNode


logger = logging.getLogger(__name__)

_ANONYMOUS_HASH_PREFIX = "anonymous-component-"
_YAML_SOURCE_PREFIX = "yaml-source-"


@dataclass
class _CacheContent:
    component_ref: Component
    in_memory_hash: str
    on_disk_hash: Optional[str] = None
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
        """Get a hash for a component, assuming there is no change in code folder among hash calculations.
        """
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
    def _get_on_disk_hash_for_component(component: Component, in_memory_hash: str) -> str:
        """Get a hash for a component."""
        if not isinstance(component, Component):
            # this shouldn't happen; handle it in case invalid call is made outside this class
            raise ValueError(f"Component {component} is not a Component object.")

        # TODO: calculate hash without resolving additional includes (copy code to temp folder)
        # note that it's still thread-safe with current implementation, as only read operations are
        # done on the original code folder
        with component._resolve_local_code() as code:  # pylint: disable=protected-access
            if code is None or code._is_remote:  # pylint: disable=protected-access
                return in_memory_hash

            object_hash = hashlib.sha256()
            object_hash.update(in_memory_hash.encode("utf-8"))
            if hasattr(code, "_upload_hash"):
                content_hash = code._upload_hash  # pylint: disable=protected-access
            else:
                path = code.path if os.path.isabs(code.path) else os.path.join(code.base_path, code.path)
                content_hash = get_object_hash(path, code._ignore_file)  # pylint: disable=protected-access
            object_hash.update(content_hash.encode("utf-8"))
            return object_hash.hexdigest()

    @staticmethod
    def _get_on_disk_cache_base_dir() -> Path:
        """Get the base path for on disk cache."""
        from azure.ai.ml._version import VERSION
        return Path.home().joinpath(".azureml", "azure-ai-ml", VERSION, "cache", "components")

    @staticmethod
    def _get_on_disk_cache_path(on_disk_hash: str) -> Path:
        """Get the on disk cache path for a component."""
        return CachedNodeResolver._get_on_disk_cache_base_dir().joinpath(on_disk_hash)

    @staticmethod
    def _load_from_on_disk_cache(on_disk_hash: str) -> Optional[str]:
        """Load component arm id from on disk cache."""
        on_disk_cache_path = CachedNodeResolver._get_on_disk_cache_path(on_disk_hash)
        if on_disk_cache_path.is_file():
            return on_disk_cache_path.read_text().strip()
        return None

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
        if not is_on_disk_cache_enabled():
            return cache_contents_to_resolve[:]

        # Note that we should recalculate the hash based on code for local cache, as
        # we can't assume that the code folder won't change among dependency resolution
        for cache_content in cache_contents_to_resolve:
            cache_content.on_disk_hash = cls._get_on_disk_hash_for_component(
                cache_content.component_ref,
                cache_content.in_memory_hash
            )

        left_cache_contents_to_resolve = []
        # need to dedup disk hash first if concurrent resolution is enabled
        for cache_content in cache_contents_to_resolve:
            cache_content.arm_id = cls._load_from_on_disk_cache(cache_content.on_disk_hash)
            if not cache_content.arm_id:
                left_cache_contents_to_resolve.append(cache_content)

        return left_cache_contents_to_resolve

    @classmethod
    def _save_cache_contents_to_disk(cls, cache_contents_to_resolve: List[_CacheContent]):
        """Save cache contents to disk."""
        if not is_on_disk_cache_enabled():
            return

        for cache_content in cache_contents_to_resolve:
            on_disk_cache_path = cls._get_on_disk_cache_path(cache_content.on_disk_hash)
            on_disk_cache_path.parent.mkdir(parents=True, exist_ok=True)
            on_disk_cache_path.write_text(cache_content.arm_id)

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

        self._save_cache_contents_to_disk(cache_contents_to_resolve)

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
