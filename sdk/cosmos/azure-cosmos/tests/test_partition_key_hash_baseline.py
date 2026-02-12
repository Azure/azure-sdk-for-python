# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests validating Python SDK partition key hash computation against baselines.

Uses the production code path (PartitionKey._write_for_hashing /
_write_for_hashing_v2) which includes the string suffix byte (0x00 for V1,
0xFF for V2), then feeds the serialised bytes into MurmurHash3.

Baseline XML files live in tests/test_data/partition_key_hash_baseline/.
To regenerate them after intentional changes to the hashing logic, run::

    UPDATE_BASELINE=1 python -m pytest tests/test_partition_key_hash_baseline.py
"""

import json
import os
import struct
from io import BytesIO
from xml.etree import ElementTree
from xml.dom import minidom

import pytest

from azure.cosmos._cosmos_integers import _UInt128
from azure.cosmos._cosmos_murmurhash3 import murmurhash3_128, murmurhash3_32
from azure.cosmos.partition_key import PartitionKey, _Undefined

TEST_DATA_DIR = os.path.join(
    os.path.dirname(__file__), "test_data", "partition_key_hash_baseline"
)

# .NET double.NaN has bit pattern 0xFFF8000000000000 (negative quiet NaN),
# while Python float('nan') uses 0x7FF8000000000000 (positive quiet NaN).
_DOTNET_NAN = struct.unpack('<d', bytes.fromhex('000000000000f8ff'))[0]


# ---------------------------------------------------------------------------
# Baseline regeneration flag
# ---------------------------------------------------------------------------

_UPDATE_BASELINE = os.environ.get("UPDATE_BASELINE", "").lower() in ("1", "true", "yes")


# ---------------------------------------------------------------------------
# Hash helpers — use the production PartitionKey serialisation functions
# ---------------------------------------------------------------------------

def _compute_hash_v1(value):
    """Compute V1 partition key hash using the production serialisation path.

    Serialises *value* with ``PartitionKey._write_for_hashing`` (which appends a
    0x00 suffix after strings), hashes with MurmurHash3-32, and returns the
    result formatted as a 32-hex-char UInt128 string (big-endian, no dashes).
    """
    ms = BytesIO()
    PartitionKey._write_for_hashing(value, ms)
    hash32 = murmurhash3_32(bytearray(ms.getvalue()), 0)
    h = int(hash32)
    low_bytes = list(h.to_bytes(8, byteorder='little'))
    high_bytes = [0] * 8
    uint128_bytes = low_bytes + high_bytes
    uint128_bytes.reverse()
    return ''.join('{:02X}'.format(b) for b in uint128_bytes)


def _compute_hash_v2(value):
    """Compute V2 partition key hash using the production serialisation path.

    Serialises *value* with ``PartitionKey._write_for_hashing_v2`` (which appends
    a 0xFF suffix after strings), hashes with MurmurHash3-128, and returns the
    result formatted as a 32-hex-char UInt128 string (big-endian, no dashes).
    """
    ms = BytesIO()
    PartitionKey._write_for_hashing_v2(value, ms)
    hash128 = murmurhash3_128(bytearray(ms.getvalue()), _UInt128(0, 0))
    ba = hash128.to_byte_array()
    ba_reversed = list(reversed(ba))
    return ''.join('{:02X}'.format(b) for b in ba_reversed)


def _compute_multi_hash_v1(values):
    """Compute V1 multi-hash (concatenated per-element UInt128 hashes)."""
    return ''.join(_compute_hash_v1(v) for v in values)


def _compute_multi_hash_v2(values):
    """Compute V2 multi-hash (concatenated per-element UInt128 hashes)."""
    return ''.join(_compute_hash_v2(v) for v in values)


# ---------------------------------------------------------------------------
# Input parsing
# ---------------------------------------------------------------------------

def _parse_partition_key_value(value_str):
    """Parse a partition key value from XML baseline format into a Python object.

    Values are valid JSON or the special string ``UNDEFINED``.  JSON strings
    ``"NaN"``, ``"-Infinity"``, ``"Infinity"`` are mapped to corresponding
    float values since they represent numbers encoded as strings in the test
    data.  The bare JSON number ``-0`` is converted to ``float('-0.0')``
    because :func:`json.loads` normalises it to positive zero.
    """
    if value_str == 'UNDEFINED':
        return _Undefined()

    parsed = json.loads(value_str)

    if isinstance(parsed, str):
        if parsed == 'NaN':
            return _DOTNET_NAN
        if parsed == '-Infinity':
            return float('-inf')
        if parsed == 'Infinity':
            return float('inf')
        if parsed == '-0':
            return float('-0.0')
        return parsed

    if isinstance(parsed, bool):
        return parsed

    if isinstance(parsed, int) and parsed == 0 and value_str.strip().startswith('-'):
        return float('-0.0')

    if isinstance(parsed, int):
        return float(parsed)

    return parsed


# ---------------------------------------------------------------------------
# XML baseline loading / writing
# ---------------------------------------------------------------------------

def _load_test_cases(filename):
    """Load test cases from a baseline XML file.

    Returns a list of dicts with keys: description, value_str, expected_v1, expected_v2.
    """
    filepath = os.path.join(TEST_DATA_DIR, filename)
    tree = ElementTree.parse(filepath)
    root = tree.getroot()

    cases = []
    for result in root.findall('Result'):
        inp = result.find('Input')
        out = result.find('Output')
        cases.append({
            'description': inp.find('Description').text,
            'value_str': inp.find('PartitionKeyValue').text,
            'expected_v1': out.find('PartitionKeyHashV1').text,
            'expected_v2': out.find('PartitionKeyHashV2').text,
        })
    return cases


def _write_baseline(filename, cases):
    """Write *cases* (list of dicts) back to a baseline XML file."""
    root = ElementTree.Element('Results')
    for case in cases:
        result = ElementTree.SubElement(root, 'Result')
        inp = ElementTree.SubElement(result, 'Input')
        ElementTree.SubElement(inp, 'Description').text = case['description']
        ElementTree.SubElement(inp, 'PartitionKeyValue').text = case['value_str']
        out = ElementTree.SubElement(result, 'Output')
        ElementTree.SubElement(out, 'PartitionKeyHashV1').text = case['expected_v1']
        ElementTree.SubElement(out, 'PartitionKeyHashV2').text = case['expected_v2']

    rough = ElementTree.tostring(root, encoding='unicode')
    pretty = minidom.parseString(rough).toprettyxml(indent='  ')
    # Remove the XML declaration that minidom adds.
    lines = pretty.splitlines(keepends=True)
    body = ''.join(lines[1:])

    filepath = os.path.join(TEST_DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(body)


def _regenerate_baseline(filename, is_list=False):
    """Regenerate a baseline XML file using the current SDK hash functions."""
    cases = _load_test_cases(filename)
    for case in cases:
        if is_list:
            values = json.loads(case['value_str'])
            case['expected_v1'] = _compute_multi_hash_v1(values)
            case['expected_v2'] = _compute_multi_hash_v2(values)
        else:
            value = _parse_partition_key_value(case['value_str'])
            case['expected_v1'] = _compute_hash_v1(value)
            case['expected_v2'] = _compute_hash_v2(value)
    _write_baseline(filename, cases)
    return cases


# ---------------------------------------------------------------------------
# Baseline file definitions
# ---------------------------------------------------------------------------

_BASELINE_FILES = [
    ("PartitionKeyHashBaselineTest.Singletons.xml", False),
    ("PartitionKeyHashBaselineTest.Numbers.xml", False),
    ("PartitionKeyHashBaselineTest.Strings.xml", False),
    ("PartitionKeyHashBaselineTest.Lists.xml", True),
]


# ---------------------------------------------------------------------------
# Regeneration at import time so parametrised cases pick up new values
# ---------------------------------------------------------------------------

if _UPDATE_BASELINE:
    for _fn, _is_list in _BASELINE_FILES:
        _regenerate_baseline(_fn, is_list=_is_list)


# ---------------------------------------------------------------------------
# Collect all cases for parametrisation
# ---------------------------------------------------------------------------

def _all_cases():
    """Return ``(id_str, case_dict, is_list)`` tuples for every test case."""
    items = []
    for filename, is_list in _BASELINE_FILES:
        suite = filename.rsplit('.', 2)[0].split('.')[-1]  # e.g. "Singletons"
        cases = _load_test_cases(filename)
        for case in cases:
            test_id = f"{suite}/{case['description']}"
            items.append((test_id, case, is_list))
    return items


_ALL = _all_cases()


@pytest.mark.cosmosEmulator
@pytest.mark.parametrize(
    "case,is_list", [(c, il) for _, c, il in _ALL], ids=[tid for tid, _, _ in _ALL]
)
class TestPartitionKeyHash:
    def test_v1(self, case, is_list):
        if is_list:
            values = json.loads(case['value_str'])
            actual = _compute_multi_hash_v1(values)
        else:
            value = _parse_partition_key_value(case['value_str'])
            actual = _compute_hash_v1(value)
        assert actual == case['expected_v1'], (
            f"V1 mismatch for {case['description']}: {actual} != {case['expected_v1']}"
        )

    def test_v2(self, case, is_list):
        if is_list:
            values = json.loads(case['value_str'])
            actual = _compute_multi_hash_v2(values)
        else:
            value = _parse_partition_key_value(case['value_str'])
            actual = _compute_hash_v2(value)
        assert actual == case['expected_v2'], (
            f"V2 mismatch for {case['description']}: {actual} != {case['expected_v2']}"
        )

