# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization helpers for the golden smoke suite.

These helpers turn a REST object (produced by ``entity._to_rest_object()``) into the canonical
camelCase JSON body that the SDK actually PUTs on the wire. The suite is designed to run against
EITHER:

* the pre-migration ``main`` code, where ``_to_rest_object()`` returns a **msrest** model
  (``_models_py3.JobBase`` etc.) whose wire body is produced by ``.serialize()``, OR
* a migration branch, where ``_to_rest_object()`` returns an **arm_ml_service hybrid** model whose
  wire body is produced by ``SdkJSONEncoder`` with ``exclude_readonly=True``.

``serialize_wire`` detects the model flavour and produces the SAME canonical dict for both, so a
golden captured from ``main`` can be asserted byte-for-byte against a migration branch. That is the
whole point: a wire-preserving client swap must produce identical wire.
"""
import json
import os

from azure.ai.ml._restclient.arm_ml_service._utils.model_base import SdkJSONEncoder

GOLDENS_DIR = os.path.join(os.path.dirname(__file__), "goldens")


def serialize_wire(rest_obj):
    """Return the canonical camelCase wire dict for a msrest OR arm-hybrid REST object.

    :param rest_obj: The object returned by ``entity._to_rest_object()``.
    :return: A plain ``dict`` matching the JSON body the SDK sends on the wire.
    :rtype: dict
    """
    # ``_is_model`` is the arm_ml_service hybrid marker. ``getattr(..., False) is True`` is the
    # mock-safe check (a bare ``hasattr`` is satisfied by test mocks).
    if getattr(rest_obj, "_is_model", False) is True:
        # arm hybrid: serialize exactly the way the generated operation does.
        return json.loads(json.dumps(rest_obj, cls=SdkJSONEncoder, exclude_readonly=True))
    # msrest: ``.serialize()`` already returns the camelCase wire dict and omits readonly fields.
    return rest_obj.serialize()


def golden_path(name):
    """Return the absolute path to a golden fixture file.

    :param name: Golden base name without extension (e.g. ``"command_job_full"``).
    :return: Absolute path to ``goldens/<name>.json``.
    :rtype: str
    """
    return os.path.join(GOLDENS_DIR, name + ".json")


def load_golden(name):
    """Load and parse a committed golden wire fixture.

    :param name: Golden base name without extension.
    :return: The parsed golden wire dict.
    :rtype: dict
    """
    with open(golden_path(name), "r", encoding="utf-8") as f:
        return json.load(f)


def save_golden(name, wire):
    """Write a wire dict as a pretty-printed golden fixture (used only by ``generate_goldens.py``).

    :param name: Golden base name without extension.
    :param wire: The canonical wire dict to persist.
    """
    os.makedirs(GOLDENS_DIR, exist_ok=True)
    with open(golden_path(name), "w", encoding="utf-8") as f:
        json.dump(wire, f, indent=2, sort_keys=True)
        f.write("\n")


def assert_serializes(rest_obj):
    """Class-A guard: the REST object must serialize to JSON without raising.

    A ``TypeError: Object of type X is not JSON serializable`` means a msrest child is sitting in an
    arm-hybrid envelope; an ``AttributeError: 'X' has no attribute '_attribute_map'`` means an arm
    child is in a msrest envelope. Both are mixed-tree migration bugs.

    :param rest_obj: The object returned by ``entity._to_rest_object()``.
    :return: The canonical wire dict (so callers can reuse it).
    :rtype: dict
    """
    return serialize_wire(rest_obj)


def assert_matches_golden(name, rest_obj):
    """Class-B guard: the produced wire must equal the golden captured from ``main``.

    :param name: Golden base name without extension.
    :param rest_obj: The object returned by ``entity._to_rest_object()``.
    """
    actual = serialize_wire(rest_obj)
    expected = load_golden(name)
    assert actual == expected, _diff_message(name, expected, actual)


def _diff_message(name, expected, actual):
    """Build a readable assertion message showing the first differing keys.

    :param name: Golden base name.
    :param expected: The golden wire dict.
    :param actual: The produced wire dict.
    :return: A human-readable diff summary.
    :rtype: str
    """
    exp = json.dumps(expected, indent=2, sort_keys=True)
    act = json.dumps(actual, indent=2, sort_keys=True)
    return (
        "Wire mismatch vs golden '{0}'. The migration changed the wire body.\n"
        "--- EXPECTED (golden from main) ---\n{1}\n--- ACTUAL (this branch) ---\n{2}".format(name, exp, act)
    )
