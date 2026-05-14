# The MIT License (MIT)
# Copyright (c) Microsoft Corporation

"""Unit tests for the public hedging-detection value types.

Covers AC6 (``RequestedRegionReason._missing_`` forward-compat) and basic
``RequestedRegion`` invariants (frozen / hashable / equality / slots).
Explicitly avoids the anti-patterns called out in public-spec §7:
  * no JSON serialization round-trips
  * no ``__slots__`` membership introspection
  * no monkey-patching of the enum to exercise ``_missing_``
"""

import enum
import pickle
import pytest

from azure.cosmos import RequestedRegion, RequestedRegionReason


class TestRequestedRegionReason:
    """AC6 + enum-value coverage."""

    def test_known_values(self):
        # Sanity: every documented variant is present and has the expected
        # wire-format string (cross-SDK contract — internal-spec §5).
        expected = {
            "INITIAL": "initial",
            "OPERATION_RETRY": "operation_retry",
            "TRANSPORT_RETRY": "transport_retry",
            "HEDGING": "hedging",
            "REGION_FAILOVER": "region_failover",
            "CIRCUIT_BREAKER_PROBE": "circuit_breaker_probe",
            "UNKNOWN": "unknown",
        }
        actual = {m.name: m.value for m in RequestedRegionReason}
        assert actual == expected

    def test_missing_returns_unknown_for_arbitrary_strings(self):
        # AC6: SDK-A receiving a reason emitted by a future SDK-B must not raise.
        for raw in ("future_value_42", "some_new_reason", "", "🚀"):
            assert RequestedRegionReason(raw) is RequestedRegionReason.UNKNOWN

    def test_missing_returns_unknown_for_non_string_values(self):
        # Defensive: non-string raw values also fall through to UNKNOWN.
        for raw in (42, None, object()):
            assert RequestedRegionReason(raw) is RequestedRegionReason.UNKNOWN

    def test_known_value_round_trips_through_constructor(self):
        # Constructing from a known wire value returns the SAME enum member.
        assert RequestedRegionReason("hedging") is RequestedRegionReason.HEDGING
        assert (
            RequestedRegionReason("operation_retry")
            is RequestedRegionReason.OPERATION_RETRY
        )

    def test_is_enum_subclass(self):
        # Customers may pattern-match `isinstance(x, RequestedRegionReason)`.
        assert issubclass(RequestedRegionReason, enum.Enum)


class TestRequestedRegion:
    """Frozen / hashable / equality semantics."""

    def test_construct_and_field_access(self):
        r = RequestedRegion(
            region_name="East US", reason=RequestedRegionReason.HEDGING
        )
        assert r.region_name == "East US"
        assert r.reason is RequestedRegionReason.HEDGING

    def test_is_frozen(self):
        r = RequestedRegion("East US", RequestedRegionReason.INITIAL)
        # Frozen dataclass — assignment must raise. Dataclasses raise
        # ``FrozenInstanceError`` (subclass of ``AttributeError``).
        with pytest.raises((AttributeError, Exception)):
            r.region_name = "West US"  # type: ignore[misc]

    def test_equality_and_hash(self):
        a = RequestedRegion("East US", RequestedRegionReason.INITIAL)
        b = RequestedRegion("East US", RequestedRegionReason.INITIAL)
        c = RequestedRegion("West US", RequestedRegionReason.INITIAL)
        d = RequestedRegion("East US", RequestedRegionReason.HEDGING)
        assert a == b
        assert hash(a) == hash(b)
        assert a != c
        assert a != d
        # Set membership relies on hash + eq.
        s = {a, b, c, d}
        assert len(s) == 3

    def test_pickleable(self):
        # Frozen slots dataclasses must remain pickleable for users that store
        # diagnostics state (e.g., for offline replay). Not part of the public
        # wire contract — purely a Python-language invariant for value types.
        r = RequestedRegion("East US", RequestedRegionReason.HEDGING)
        restored = pickle.loads(pickle.dumps(r))
        assert restored == r
