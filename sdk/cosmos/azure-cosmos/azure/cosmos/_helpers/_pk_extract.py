# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Extract a partition-key value from a document.

This needs only two inputs: the container's partition-key definition (its
``kind`` / ``paths`` / ``systemKey``) and the document. The extraction is a
plain walk of the document -- no client connection, no I/O.

These functions match the connection's ``_ExtractPartitionKey`` /
``_retrieve_partition_key`` (single- and multi-hash, system-key handling) so
the backend produces the same value the legacy path does. The backend uses
them instead of calling ``CosmosClientConnection._AddPartitionKey``.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, List, Optional, Union

from .._base import ParsePaths
from ..partition_key import (
    _Empty,
    _PartitionKeyKind,
    _Undefined,
    _return_undefined_or_empty_partition_key,
)


def extract_partition_key_value(
    partition_key_definition: Mapping[str, Any],
    document: Mapping[str, Any],
) -> Any:
    """Return the partition-key value for ``document`` per the definition.

    Mirror of the legacy ``_ExtractPartitionKey``: a MultiHash definition
    yields a list with one value per path (an ``_Undefined`` / ``_Empty``
    level collapses to ``None``); a single-hash definition yields the one
    value (or an ``_Undefined`` / ``_Empty`` sentinel when the path is
    absent).

    :param partition_key_definition: The container's partition-key
        definition (``kind`` / ``paths`` / optional ``systemKey``).
    :type partition_key_definition: Mapping[str, Any]
    :param document: The Cosmos document to read the value out of.
    :type document: Mapping[str, Any]
    :returns: The extracted partition-key value (or sentinel / list).
    :rtype: Any
    """
    if partition_key_definition["kind"] == _PartitionKeyKind.MULTI_HASH:
        ret: List[Optional[Union[str, float, bool]]] = []
        for partition_key_level in partition_key_definition["paths"]:
            # Parse one path into a token per property, then walk to its leaf.
            partition_key_parts = ParsePaths([partition_key_level])
            is_system_key = partition_key_definition.get("systemKey", False)
            val = _retrieve_partition_key(partition_key_parts, document, is_system_key)
            if isinstance(val, (_Undefined, _Empty)):
                val = None
            ret.append(val)
        return ret

    partition_key_parts = ParsePaths(partition_key_definition["paths"])
    is_system_key = partition_key_definition.get("systemKey", False)
    return _retrieve_partition_key(partition_key_parts, document, is_system_key)


def _retrieve_partition_key(
    partition_key_parts: List[str],
    document: Mapping[str, Any],
    is_system_key: bool,
) -> Union[str, float, bool, _Empty, _Undefined]:
    """Walk ``document`` along ``partition_key_parts`` to the leaf value.

    Mirror of the legacy ``_retrieve_partition_key``: an absent or non-leaf
    path returns the ``_Undefined`` / ``_Empty`` sentinel (system-key
    dependent), never a partial.

    :param partition_key_parts: The parsed property tokens for one path.
    :type partition_key_parts: List[str]
    :param document: The Cosmos document being navigated.
    :type document: Mapping[str, Any]
    :param is_system_key: Whether the definition marks a system key.
    :type is_system_key: bool
    :returns: The leaf value, or an ``_Undefined`` / ``_Empty`` sentinel.
    :rtype: Union[str, float, bool, _Empty, _Undefined]
    """
    expected_match_count = len(partition_key_parts)
    match_count = 0
    partition_key: Any = document
    for part in partition_key_parts:
        # Once we reach a non-mapping leaf, stop descending.
        if not isinstance(partition_key, Mapping):
            break
        # A missing sub-property means the value is undefined for this doc.
        if part not in partition_key:
            return _return_undefined_or_empty_partition_key(is_system_key)
        partition_key = partition_key[part]
        match_count += 1

    # Validate we hopped exactly as many levels as the path has, and that we
    # did not stop on a sub-object rather than a leaf value.
    if (match_count != expected_match_count) or isinstance(partition_key, Mapping):
        return _return_undefined_or_empty_partition_key(is_system_key)
    return partition_key

