# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------
from typing import Dict, Any, Iterable, Optional, Union
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
        if self.is_leaf:
            raise ValueError("Please don't call __contains__ on a leaf TrieNode")
        return item in self.children

    def get(self, key):
        if self.is_leaf:
            raise ValueError("Please don't get a child from a leaf TrieNode")
        return self.children.get(key)

    def put(self, key, value):
        if self.is_leaf:
            raise ValueError("Please don't put a value to a leaf TrieNode")
        self.children[key] = value


def _lookup_trie(root, path, path_index):
    if path_index == len(path) - 1:
        return root.get(path[path_index])
    if path[path_index] in root:
        return _lookup_trie(root.children[path[path_index]], path, path_index + 1)
    return None


def _list_leaves_trie(root, result):
    if root.is_leaf:
        result.append(root.value)
        return
    for child in root.children.values():
        _list_leaves_trie(child, result)


def _set_ele_trie(root, ele, keys_path, path_index):
    if path_index == len(keys_path) - 1:
        root.children[ele[keys_path[path_index]]] = _TrieNode(ele, True)
        return
    next_node = root.get(ele[keys_path[path_index]])
    if not next_node:
        next_node = _TrieNode(ele[keys_path[path_index]], False)
        root.put(ele[keys_path[path_index]], next_node)
    _set_ele_trie(next_node, ele, keys_path, path_index + 1)


class _DictTrie(object):
    def __init__(self, root_name, keys_path):
        self._root = _TrieNode(root_name, False)
        self._keys_path = keys_path

    def lookup(self, path):
        return _lookup_trie(self._root, path, 0)

    def list_leaves(self, node):
        if not node:
            node = self._root
        result = []
        _list_leaves_trie(node, result)
        return result

    def set_ele(self, ele):
        _set_ele_trie(self._root, ele, self._keys_path, 0)


class InMemoryCheckpointStore(CheckpointStore):
    def __init__(self):
        self._ownerships_trie = _DictTrie(
            "ownerships_trie",
            keys_path=(
                "fully_qualified_namespace",
                "eventhub_name",
                "consumer_group",
                "partition_id",
            ),
        )
        self._checkpoints_trie = _DictTrie(
            "checkpoints_trie",
            keys_path=(
                "fully_qualified_namespace",
                "eventhub_name",
                "consumer_group",
                "partition_id",
            ),
        )

    def list_ownership(
        self, fully_qualified_namespace, eventhub_name, consumer_group, **kwargs
    ):
        # type: (str, str, str, Any) -> Iterable[Dict[str, Any]]
        consumer_group_node = self._ownerships_trie.lookup(
            (fully_qualified_namespace, eventhub_name, consumer_group)
        )
        return self._ownerships_trie.list_leaves(consumer_group_node)

    def claim_ownership(self, ownership_list, **kwargs):
        # type: (Iterable[Dict[str, Any]], Any) -> Iterable[Dict[str, Any]]
        result = []
        for ownership in ownership_list:
            fully_qualified_namespace = ownership["fully_qualified_namespace"]
            eventhub_name = ownership["eventhub_name"]
            consumer_group = ownership["consumer_group"]
            partition_id = ownership["partition_id"]
            etag = ownership.get("etag")
            old_ownership_node = self._ownerships_trie.lookup(
                (fully_qualified_namespace, eventhub_name, consumer_group, partition_id)
            )
            if old_ownership_node:
                old_ownership = old_ownership_node.value
                if etag == old_ownership["etag"]:
                    ownership["etag"] = str(uuid.uuid4())
                    ownership["last_modified_time"] = time.time()
                    old_ownership["etag"] = ownership["etag"]
                    old_ownership["last_modified_time"] = ownership[
                        "last_modified_time"
                    ]
                    old_ownership["owner_id"] = ownership["owner_id"]
                    result.append(old_ownership)
            else:
                ownership["etag"] = str(uuid.uuid4())
                ownership["last_modified_time"] = time.time()
                self._ownerships_trie.set_ele(ownership)
                result.append(ownership)
        return result

    def update_checkpoint(self, checkpoint, **kwargs):
        # type: (Dict[str, Optional[Union[str, int]]], Any) -> None
        return self._checkpoints_trie.set_ele(checkpoint)

    def list_checkpoints(
        self, fully_qualified_namespace, eventhub_name, consumer_group, **kwargs
    ):
        consumer_group_node = self._checkpoints_trie.lookup(
            (fully_qualified_namespace, eventhub_name, consumer_group)
        )
        return self._checkpoints_trie.list_leaves(consumer_group_node)
