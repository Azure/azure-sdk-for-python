# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------
from typing import List, Dict, Any, Iterable, Optional, Union
import time
import uuid
import logging

from .checkpoint_store import CheckpointStore

_LOGGER = logging.getLogger(__name__)


class _TrieNode(object):
    def __init__(self, value, is_leaf):
        self.value = value
        self.is_leaf = is_leaf
        if is_leaf:
            self.children = None
        else:
            self.children = {}

    def __contains__(self, item):
        return item in self.children

    def get(self, key):
        return self.children.get(key)

    def put(self, key, value):
        self.children[key] = value


def _lookup_trie(root, path, path_index):
    if path_index == len(path) - 1:
        return root.get(path[path_index])
    if path[path_index] in root:
        return _lookup_trie(root.children[path[path_index]], path, path_index+1)
    return None


def _list_leaves_trie(root, result):
    if root.is_leaf:
        result.append(root.value)
        return
    for child in root.children.values():
        _list_leaves_trie(child, result)


def _set_ele_trie(root, ele, path_names, path_index):
    if path_index == len(path_names) - 1:
        root.children[ele[path_names[path_index]]] = _TrieNode(ele, True)
        return
    next_node = root.get(ele[path_names[path_index]])
    if not next_node:
        next_node = _TrieNode(ele[path_names[path_index]], False)
        root.put(ele[path_names[path_index]], next_node)
    _set_ele_trie(next_node, ele, path_names, path_index + 1)


class _DictTrie(object):
    def __init__(self, root_name, path_names):
        self._root = _TrieNode(root_name, False)
        self._path_names = path_names

    def lookup(self, path):
        return _lookup_trie(self._root, path, 0)

    def list_leaves(self, node):
        if not node:
            node = self._root
        result = []
        _list_leaves_trie(node, result)
        return result

    def set_ele(self, ele):
        _set_ele_trie(self._root, ele, self._path_names, 0)


class InMemoryCheckpointStore(CheckpointStore):
    def __init__(
        self
    ):
        self.ownerships_trie = _DictTrie(
            "ownerships_trie",
            path_names=("fully_qualified_namespace", "eventhub_name", "consumer_group", "partition_id")
        )
        self.checkpoints_trie = _DictTrie(
            "checkpoints_trie",
            path_names=("fully_qualified_namespace", "eventhub_name", "consumer_group", "partition_id")
        )

    def list_ownership(self, fully_qualified_namespace, eventhub_name, consumer_group):
        # type: (str, str, str) -> Iterable[Dict[str, Any]]
        consumer_group_node = self.ownerships_trie.lookup((fully_qualified_namespace, eventhub_name, consumer_group))
        return self.ownerships_trie.list_leaves(consumer_group_node)

    def claim_ownership(self, ownership_list):
        # type: (Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]
        result = []
        for ownership in ownership_list:
            fully_qualified_namespace = ownership["fully_qualified_namespace"]
            eventhub_name = ownership["eventhub_name"]
            consumer_group = ownership["consumer_group"]
            partition_id = ownership["partition_id"]
            etag = ownership.get("etag")
            old_ownership_node = self.ownerships_trie.lookup(
                (fully_qualified_namespace, eventhub_name, consumer_group, partition_id)
            )
            if old_ownership_node:
                old_ownership = old_ownership_node.value
                if etag == old_ownership["etag"]:
                    ownership["etag"] = str(uuid.uuid4())
                    ownership["last_modified_time"] = time.time()
                    old_ownership["etag"] = ownership["etag"]
                    old_ownership["last_modified_time"] = ownership["last_modified_time"]
                    old_ownership["owner_id"] = ownership["owner_id"]
                    result.append(old_ownership)
            else:
                ownership["etag"] = str(uuid.uuid4())
                ownership["last_modified_time"] = time.time()
                self.ownerships_trie.set_ele(
                    ownership
                )
        return result

    def update_checkpoint(self, checkpoint):
        # type: (Dict[str, Optional[Union[str, int]]]) -> None
        return self.checkpoints_trie.set_ele(checkpoint)

    def list_checkpoints(
            self, fully_qualified_namespace, eventhub_name, consumer_group
    ):
        consumer_group_node = self.ownerships_trie.lookup((fully_qualified_namespace, eventhub_name, consumer_group))
        return self.checkpoints_trie.list_leaves(consumer_group_node)
