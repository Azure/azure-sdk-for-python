# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=pointless-string-statement

import hashlib
import json
import os
from collections import deque
from datetime import datetime
from os import listdir
from os.path import isfile, join

HASH_FILE_CHUNK_SIZE = 65536
HASH_ALGORITHM = "sha512"

""" Copied from ml-components
Create a merkle tree for the given directory path
The directory would typically represent a project directory"""


def create_merkletree(file_or_folder_path, exclude_function):
    root = DirTreeNode("", "Directory", datetime.fromtimestamp(os.path.getmtime(file_or_folder_path)).isoformat())
    if os.path.isdir(file_or_folder_path):
        folder_path = file_or_folder_path
        _create_merkletree_helper(folder_path, root, exclude_function)
    else:
        file_path = file_or_folder_path
        file_node = DirTreeNode(file_path, "File", datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat())
        hexdigest_hash, bytehash = _get_hash(os.path.normpath(file_path), file_path, "File")
        if hexdigest_hash and bytehash:
            file_node.add_hash(hexdigest_hash, bytehash)
            root.add_child(file_node)

    _populate_hashes(root)
    return root


""" Populate hashes for directory nodes
by hashing the hashes of child nodes under them"""


def _populate_hashes(rootNode):
    if rootNode.is_file():
        return rootNode.bytehash
    h = hashlib.new(HASH_ALGORITHM)
    for child in rootNode.children:
        if child.is_file():
            h.update(child.bytehash)
        else:
            h.update(_populate_hashes(child))
    rootNode.bytehash = h.digest()
    rootNode.hexdigest_hash = h.hexdigest()
    return h.digest()


""" Create a merkle tree for the given directory path
    :param projectDir: Directory for which to create a tree.
    :param rootNode: Root node .
    Walks the directory and create a dirTree """


def _create_merkletree_helper(projectDir, rootNode, exclude_function):
    for f in sorted(listdir(projectDir)):
        path = os.path.normpath(join(projectDir, f))
        if not exclude_function(path):
            if isfile(join(projectDir, f)):
                newNode = DirTreeNode(f, "File", datetime.fromtimestamp(os.path.getmtime(path)).isoformat())
                hexdigest_hash, bytehash = _get_hash(path, f, "File")
                if hexdigest_hash and bytehash:
                    newNode.add_hash(hexdigest_hash, bytehash)
                    rootNode.add_child(newNode)
            else:
                newNode = DirTreeNode(f, "Directory", datetime.fromtimestamp(os.path.getmtime(path)).isoformat())
                rootNode.add_child(newNode)
                _create_merkletree_helper(path, newNode, exclude_function)


def _get_hash(filePath, name, file_type):
    h = hashlib.new(HASH_ALGORITHM)
    if not os.access(filePath, os.R_OK):
        print(filePath, os.R_OK)
        print("Cannot access file, so excluded from snapshot: {}".format(filePath))
        return (None, None)
    with open(filePath, "rb") as f:
        while True:
            data = f.read(HASH_FILE_CHUNK_SIZE)
            if not data:
                break
            h.update(data)
    h.update(name.encode("utf-8"))
    h.update(file_type.encode("utf-8"))
    return (h.hexdigest(), h.digest())


""" We compute both hexdigest and digest for hashes.
digest (bytes) is used so that we can compute the bytehash of a parent directory based on bytehash of its children
hexdigest is used so that we can serialize the tree using json"""


class DirTreeNode(object):
    def __init__(self, name=None, file_type=None, timestamp=None, hexdigest_hash=None, bytehash=None):
        self.file_type = file_type
        self.name = name
        self.timestamp = timestamp
        self.children = []
        self.hexdigest_hash = hexdigest_hash
        self.bytehash = bytehash

    def load_children_from_dict(self, node_dict):
        if len(node_dict.items()) == 0:
            return None
        self.name = node_dict["name"]
        self.file_type = node_dict["type"]
        self.hexdigest_hash = node_dict["hash"]
        self.timestamp = node_dict["timestamp"]
        for _, child in node_dict["children"].items():
            node = DirTreeNode()
            node.load_children_from_dict(child)
            self.add_child(node)
        return self

    def load_children_from_json(self, node_dict):
        self.name = node_dict["name"]
        self.file_type = node_dict["type"]
        self.hexdigest_hash = node_dict["hash"]
        self.timestamp = node_dict["timestamp"]
        for child in node_dict["children"]:
            node = DirTreeNode()
            node.load_children_from_json(child)
            self.add_child(node)
        return self

    def load_object_from_dict(self, node_dict):
        self.load_children_from_dict(node_dict)

    def load_root_object_from_json_string(self, jsondata):
        node_dict = json.loads(jsondata)
        self.load_children_from_json(node_dict)

    def add_hash(self, hexdigest_hash, bytehash):
        self.hexdigest_hash = hexdigest_hash
        self.bytehash = bytehash

    def add_child(self, node):
        self.children.append(node)

    def is_file(self):
        return self.file_type == "File"

    """ Only for debugging purposes"""

    def print_tree(self):
        queue = deque()
        print("Name: " + self.name)
        print("Type: " + self.file_type)
        for child in self.children:
            print("    " + child.name)
            queue.append(child)
        for i in queue:
            i.print_tree()


""" Serialize merkle tree.
Serialize all fields except digest (bytes)
"""


class DirTreeJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if not isinstance(o, DirTreeNode):
            return super(DirTreeJsonEncoder, self).default(o)
        _dict = o.__dict__
        _dict.pop("bytehash", None)
        _dict["type"] = _dict.pop("file_type")
        _dict["hash"] = _dict.pop("hexdigest_hash")

        return _dict


class DirTreeJsonEncoderV2(json.JSONEncoder):
    def default(self, o):
        if not isinstance(o, DirTreeNode):
            return super(DirTreeJsonEncoderV2, self).default(o)
        _dict = o.__dict__
        _dict.pop("bytehash", None)
        if "file_type" in _dict:
            _dict["type"] = _dict.pop("file_type")
        if "hexdigest_hash" in _dict:
            _dict["hash"] = _dict.pop("hexdigest_hash")
        if isinstance(_dict["children"], list):
            _dict["children"] = {x.name: x for x in _dict["children"]}

        return _dict
