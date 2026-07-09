# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Serialize a partition-key value into the ``x-ms-documentdb-partitionkey`` header string.

Input → output mapping:

==================================================  =================================
Input value                                         On-wire header value
==================================================  =================================
``"customerA"``                                     ``["customerA"]``
``123``                                             ``[123]``
``True``                                            ``[true]``
``None``                                            ``[null]``
``_Undefined()`` (path missing in body)             ``[{}]``
``_Empty()`` / ``NonePartitionKeyValue``            ``[]``
``["t1", "r1"]`` (hierarchical)                     ``["t1","r1"]``
``["t1", _Empty()]`` (hierarchical, missing leaf)   ``["t1",null]``
==================================================  =================================

Pure-function helper; produces the same byte output as the legacy
header-build path so both backends ship identical headers.
"""
from __future__ import annotations

import json
from typing import Any, Sequence

from ..partition_key import (
    NonePartitionKeyValue,
    _Empty,
    _Undefined,
)

# Compact separators (no spaces) match the byte sequence the existing
# core-python pipeline writes today.
_COMPACT_SEPARATORS = (",", ":")


def serialize_partition_key_to_wire(pk_value: Any) -> str:
    """Return the exact string for the ``x-ms-documentdb-partitionkey`` header.

    :param pk_value: Partition-key value in any of the accepted shapes
        (see the module mapping table). Not mutated.
    :type pk_value: Any
    :returns: JSON-encoded string. Always a string, never a list.
    :rtype: str
    """
    # Partition-key path is defined on the container but missing in the document.
    if isinstance(pk_value, _Undefined):
        return "[{}]"

    # Partitionless container.
    if isinstance(pk_value, _Empty) or pk_value is NonePartitionKeyValue:
        return "[]"

    # Hierarchical partition key: list / tuple of components; a missing
    # leaf becomes JSON null at that position.
    if isinstance(pk_value, Sequence) and not isinstance(pk_value, (str, bytes)) and pk_value:
        normalized = [
            None if isinstance(component, (_Empty, _Undefined)) else component
            for component in pk_value
        ]
        return json.dumps(normalized, separators=_COMPACT_SEPARATORS)

    # Single-value partition key wrapped in a one-element JSON array.
    return json.dumps([pk_value], separators=_COMPACT_SEPARATORS)
