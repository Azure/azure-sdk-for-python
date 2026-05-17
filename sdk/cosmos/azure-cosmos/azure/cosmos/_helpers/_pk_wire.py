# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Serialize a partition-key value into the exact string that goes on the wire.

The Cosmos service identifies the physical partition for an item
operation by reading the ``x-ms-documentdb-partitionkey`` HTTP
header. The header carries a JSON-encoded array. Different inputs the
SDK accepts (a single string, a hierarchical list, an explicitly
"undefined" sentinel, a partitionless container marker) each map to a
*specific* on-wire JSON shape, and any drift in that shape lands the
request in a different physical partition than the one previous writes
landed in. That symptom looks like an item "disappearing" without
anyone deleting it, which is the failure mode this module exists to
prevent.

The mapping table this module enforces matches the existing core-python
header-build logic in ``_base.GetHeaders`` so both backends produce
byte-identical request headers:

==================================================  =================================
Input value                                         On-wire header value
==================================================  =================================
``"customerA"``                                     ``["customerA"]``
``123``                                             ``[123]``
``True``                                            ``[true]``
``None``                                            ``[null]``
``_Undefined()`` (the path is missing in the body)  ``[{}]``
``_Empty()`` / ``NonePartitionKeyValue``            ``[]``
``["t1", "r1"]`` (hierarchical)                     ``["t1","r1"]``
``["t1", _Empty()]`` (hierarchical, missing leaf)   ``["t1",null]``
==================================================  =================================

The function is a pure-function helper (no I/O, no globals) so it can
be unit-tested without a network or a Cosmos client. The unit tests
live in ``tests/test_pk_wire_unit.py`` and cover every row of the
table above plus a few edge cases.
"""
from __future__ import annotations

import json
from typing import Any, Sequence

from ..partition_key import (
    NonePartitionKeyValue,
    _Empty,
    _Undefined,
)

# json.dumps with these separators emits no spaces between elements or
# after the colon in dicts. The resulting bytes match what the existing
# core-python pipeline writes today for the same input — that byte
# equality is the entire point of routing this through one helper.
_COMPACT_SEPARATORS = (",", ":")


def serialize_partition_key_to_wire(pk_value: Any) -> str:
    """Return the exact string to put in the ``x-ms-documentdb-partitionkey`` header.

    The function maps a partition-key value (in any of the shapes the
    Cosmos SDK accepts) to the JSON-encoded string the service expects.
    See the module docstring for the full input → output mapping table.

    :param pk_value: Partition-key value the caller supplied. Accepted
        shapes are documented in the module table above. The function
        does not mutate ``pk_value``.
    :type pk_value: Any
    :returns: A JSON-encoded string ready to assign as the value of the
        ``x-ms-documentdb-partitionkey`` HTTP header. The return value
        is always a string, never a Python list — header values must be
        strings on the wire.
    :rtype: str
    """
    # Sentinel: the partition-key path is *defined* in the container
    # but missing in the document. The Cosmos service distinguishes
    # this case from a literal null and from a partitionless container.
    if isinstance(pk_value, _Undefined):
        return "[{}]"

    # Sentinel: the container has no partition key at all (a legacy
    # partitionless container). NonePartitionKeyValue is the class
    # itself, not an instance, so check identity rather than isinstance.
    if isinstance(pk_value, _Empty) or pk_value is NonePartitionKeyValue:
        return "[]"

    # Hierarchical partition key. The user passes a list/tuple of values,
    # one per partition-key path defined on the container. A missing
    # leaf is represented by an _Empty / _Undefined sentinel inside the
    # list and renders as JSON null at that position.
    if isinstance(pk_value, Sequence) and not isinstance(pk_value, (str, bytes)) and pk_value:
        normalized = [
            None if isinstance(component, (_Empty, _Undefined)) else component
            for component in pk_value
        ]
        return json.dumps(normalized, separators=_COMPACT_SEPARATORS)

    # Single-value partition key (string / int / float / bool / None).
    # The service expects it wrapped in a one-element JSON array.
    return json.dumps([pk_value], separators=_COMPACT_SEPARATORS)
