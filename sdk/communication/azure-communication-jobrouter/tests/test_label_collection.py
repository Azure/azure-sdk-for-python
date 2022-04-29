# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.communication.jobrouter import LabelCollection


class CompositeKey(object):
    def __init__(self, value):
        self.key = value

def test_label_collection_creation():
    labels = LabelCollection(a = 10, b = '10', c = "10", d = 10.01)
    assert labels is not None
    assert labels['a'] == 10
    assert labels['b'] == '10'
    assert labels['c'] == "10"
    assert labels['d'] == 10.01


def test_label_collection_creation_with_dict():
    my_existing_labels = {'a': 10, 'b': '10', 'c': "10", 'd': 10.01}
    labels = LabelCollection(my_existing_labels)
    assert labels is not None
    assert labels['a'] == 10
    assert labels['b'] == '10'
    assert labels['c'] == "10"
    assert labels['d'] == 10.01


def test_label_collection_creation_with_label_collection():
    original_labels = LabelCollection(a = 10)
    copied_labels = LabelCollection(original_labels)

    assert id(copied_labels) != id(original_labels)
    assert copied_labels['a'] == 10


def test_label_collection_creation_with_composite_keys_fails():
    composite_key = CompositeKey(10)
    complex_labels = dict([(composite_key, 1)])
    with pytest.raises(ValueError):
        labels = LabelCollection(complex_labels)


unacceptable_keys = [
    10,
    True,
    False,
    10.01
]
@pytest.mark.parametrize("value", unacceptable_keys)
def test_label_collection_creation_with_non_string_keys_fails(value):
    complex_labels = dict([
        (value, 10),
    ])
    with pytest.raises(ValueError) as ex_info:
        labels = LabelCollection(complex_labels)

    assert len(ex_info.value.args) == 1
    assert str(ex_info.value.args[0]).startswith("Unsupported key type") is True


unacceptable_values = [
    CompositeKey(10),
]
@pytest.mark.parametrize("value", unacceptable_values)
def test_label_collection_creation_with_unsupported_value_fails(value):
    complex_labels = dict([
        ("value", value),
    ])
    with pytest.raises(ValueError) as ex_info:
        labels = LabelCollection(complex_labels)

    assert len(ex_info.value.args) == 1
    assert str(ex_info.value.args[0]).startswith("Unsupported value type") is True
