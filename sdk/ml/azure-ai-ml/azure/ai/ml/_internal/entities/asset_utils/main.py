# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from typing import Union
from uuid import UUID

from azure.ai.ml._utils._asset_utils import IgnoreFile, get_ignore_file

from .merkle_tree import create_merkletree


def get_snapshot_id(code_path: Union[str, PathLike]) -> str:
    # Only calculate hash for local files
    _ignore_file: IgnoreFile = get_ignore_file(code_path)
    curr_root = create_merkletree(code_path, lambda x: _ignore_file.is_file_excluded(code_path))
    snapshot_id = str(UUID(curr_root.hexdigest_hash[::4]))
    return snapshot_id
