# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit coverage for the rules that deliberately make requests fail, used in testing.

The driver can be told to inject faults: delay a request, return a particular error, do
it to a fraction of calls. It is how failure handling gets tested without an actual
outage. These tests check the rules are understood correctly before any driver exists.

Almost everything here is about refusing a rule that is not quite right, and the reason
is unusual. A misread rule does not cause a visible failure -- it causes faults not to be
injected. The test then passes, and reports that code survives a failure it never saw.
A silently ignored rule is worse than a rejected one, so anything unrecognized is an
error.
"""
import pytest

from azure.cosmos._backend.client_config import _prepare_fault_injection_rules


def _rule(**overrides):
    """Build a valid rule, with any field replaced by the caller."""
    return {"id": "test-fault", "operation_type": "CreateItem", "status_code": 502, **overrides}


@pytest.mark.parametrize("rules", [None, [], ()])
def test_absent_or_empty_rule_sequence_disables_injection(rules):
    """Asking for no faults, in any of the three ways, means no faults.

    Nothing at all and two kinds of empty collection all mean the same thing, and all
    produce the same empty result, so the normal case needs no special handling anywhere
    downstream.
    """
    assert _prepare_fault_injection_rules(rules) == ()


@pytest.mark.parametrize("rules", [{}, "", b"", bytearray(), False, 0, 1, set()])
def test_invalid_collection_is_rejected_even_when_empty(rules):
    """Things that merely look empty are refused rather than quietly accepted.

    All eight are empty or false in the way Python judges such things, so a check written
    as "if there are no rules" would treat every one as asking for nothing. But a mapping,
    a piece of text, or a number is not a list of rules; it is a mistake in how the option
    was passed.

    Accepting them would mean the caller's real intent was never carried out and nothing
    said so.
    """
    with pytest.raises(ValueError, match="sequence of rule mappings"):
        _prepare_fault_injection_rules(rules)


@pytest.mark.parametrize("field", ["error_type", "hit_limt", 42])
def test_unknown_rule_fields_do_not_silently_change_the_test(field):
    """A field name that is not recognized is an error, including a near miss.

    The three cases are a name that sounds plausible, the same name as a real one with a
    letter missing, and something that is not text at all. The misspelling is the one
    that matters: the intended field keeps its default, the rule does less than the
    author believed, and the test that relies on it still passes.
    """
    with pytest.raises(ValueError, match="unsupported fields"):
        _prepare_fault_injection_rules([{**_rule(), field: "ConnectionError"}])


@pytest.mark.parametrize(
    "field, value",
    [
        ("delay_ms", -1), ("delay_ms", True), ("delay_ms", 2**64),
        ("hit_limit", -1), ("hit_limit", True), ("hit_limit", 2**32),
        ("probability", True), ("probability", -1), ("probability", 2),
        ("probability", float("nan")), ("probability", float("inf")),
        ("probability", 10**1000),
        ("operation_type", []), ("operation_type", "PatchItem"),
    ],
)
def test_invalid_values_raise_value_error_before_native_conversion(field, value):
    """Fourteen bad values, each refused in Python with the field named in the message.

    The delay and the hit limit must be whole numbers that fit the sizes the driver uses,
    so negatives and values one past the top are refused. True is refused everywhere a
    number belongs, because Python would otherwise accept it as one and a rule meaning
    "delay by one millisecond" is not what anyone wrote.

    A probability must sit between none and all, which rules out negatives, values above
    one, not-a-number, infinity, and a number too large to represent. The last two cases
    cover the operation being named: not text at all, and an operation that exists in the
    SDK but cannot have faults injected.

    Checking here rather than at the boundary means the message names the field. The same
    value rejected further down would surface as a failure to convert, with nothing to
    say which of the rule's fields was wrong.
    """
    with pytest.raises(ValueError, match=field):
        _prepare_fault_injection_rules([_rule(**{field: value})])


def test_native_integer_boundaries_are_preserved_without_mutating_inputs():
    """The largest accepted values survive exactly, and the caller's rule is not altered.

    One below each size limit, passed through unchanged rather than rounded or wrapped.
    A value that wrapped would turn the largest possible delay into no delay at all,
    which is the opposite of what was asked for and produces a passing test.

    The caller's mapping is compared against a copy taken beforehand, so preparing a rule
    is proved to leave the original alone. Rules are often shared between tests, and one
    test changing another's rule would be very hard to trace.
    """
    rule = _rule(delay_ms=2**64 - 1, hit_limit=2**32 - 1)
    before = dict(rule)
    prepared, = _prepare_fault_injection_rules([rule])
    assert prepared.delay_ms == 2**64 - 1
    assert prepared.hit_limit == 2**32 - 1
    assert rule == before


def test_zero_and_false_are_values_not_missing_options():
    """Zero and off are real choices, not the same as leaving a field out.

    All four are values Python treats as false, so anything deciding "was this set?" by
    truth alone would replace every one with its default. A probability of zero would
    become certainty, and a rule switched off would switch itself back on.

    That is the worst kind of failure here: faults injected into a run that asked for
    none.
    """
    prepared, = _prepare_fault_injection_rules([
        _rule(delay_ms=0, hit_limit=0, probability=0, enabled=False),
    ])
    assert prepared.delay_ms == 0
    assert prepared.hit_limit == 0
    assert prepared.probability == 0.0
    assert prepared.enabled is False


def test_rule_defaults_and_duplicate_detection_are_preserved():
    """A minimal rule gets sensible defaults, and two rules cannot share one name.

    Left alone, a rule applies every time with no limit on how often, is switched on, and
    adds no delay. Those are the settings someone writing the shortest possible rule
    expects.

    Two rules with the same name are refused. Otherwise one would take effect and the
    other would not, with no way to tell which, and a test relying on the ignored one
    would pass having injected nothing.
    """
    prepared, = _prepare_fault_injection_rules([_rule()])
    assert prepared.hit_limit is None
    assert prepared.probability == 1.0
    assert prepared.enabled is True
    assert prepared.sub_status == prepared.delay_ms == 0
    with pytest.raises(ValueError, match="duplicate"):
        _prepare_fault_injection_rules([_rule(), _rule()])
