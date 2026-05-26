# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Unit tests for the Condition values customization in ``azure.mgmt.monitorslis``."""

import pytest

from azure.mgmt.monitorslis.models import Condition, ConditionOperator


def test_values_round_trip_through_wire_value():
    c = Condition(operator=ConditionOperator.IN, value="east^^west^^north")
    assert c.values == ["east", "west", "north"]


def test_values_setter_joins_with_separator():
    c = Condition(operator=ConditionOperator.IN, value="placeholder")
    c.values = ["east", "west", "north"]
    assert c.value == "east^^west^^north"


def test_values_setter_none_clears_value():
    c = Condition(operator=ConditionOperator.IN, value="east^^west")
    c.values = None
    assert c.value is None


def test_values_getter_empty_when_value_none():
    c = Condition(operator=ConditionOperator.IN, value="placeholder")
    c.values = None
    assert c.values == []


def test_for_list_operator_in():
    c = Condition.for_list_operator(
        ConditionOperator.IN,
        ["east", "west"],
        dimension_name="region",
    )
    assert c.operator == ConditionOperator.IN
    assert c.value == "east^^west"
    assert c.dimension_name == "region"


def test_for_list_operator_not_in():
    c = Condition.for_list_operator(ConditionOperator.NOT_IN, ["only"])
    assert c.operator == ConditionOperator.NOT_IN
    assert c.value == "only"


def test_for_list_operator_rejects_wrong_operator():
    with pytest.raises(ValueError):
        Condition.for_list_operator(ConditionOperator.EQUAL, ["east"])


def test_for_list_operator_rejects_empty():
    with pytest.raises(ValueError):
        Condition.for_list_operator(ConditionOperator.IN, [])


def test_for_list_operator_rejects_item_containing_separator():
    with pytest.raises(ValueError):
        Condition.for_list_operator(ConditionOperator.IN, ["ok", "bad^^value"])
