# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for the parity harness's exception-message normalizer.

These run offline -- they exercise ``_parity_helpers`` itself, not the SDK.

Why they exist: when a Cosmos gateway call fails, the service appends a large
diagnostics tail to the error text. A real captured example, elided:

    (NotFound) Entity with the specified id does not exist in the system.
    More info: https://aka.ms/cosmosdb-tsg-not-found,
    RequestStartTime: ..., Number of regions attempted:1
    {"systemHistory":[{"cpu":0.713,"memory":856364468.000,...}]}
    ... StorePhysicalAddress: rntbd://...:15657/... BELatencyMs: 0.264 ...
    ; ResourceType: Document, OperationType: Read

Two calls a second apart produced ``cpu 0.713 / memory 856364468`` on one and
``cpu 0.334 / memory 848174492`` on the other, plus a different replica port
and different byte counts. That is the *service's* health at two instants --
nothing to do with which client engine sent the request. Comparing the raw
text across backends therefore fails at random, which is what these tests
exist to prevent.

The normalizer's contract has two halves, and both are pinned here:

* **Noise must go.** Everything in that tail that describes the machine
  rather than the operation is dropped.
* **Signal must survive.** The canonical server error text, and the
  ``ResourceType`` / ``OperationType`` fields buried inside the tail, are
  kept -- so a backend that issued the wrong kind of request is still
  caught. A normalizer that flattened everything to a constant would pass
  the first half and fail the second.
"""
from __future__ import annotations

from common._parity_helpers import _normalize_exception_message


class _FakeError(Exception):
    """Stand-in for a typed SDK error; the normalizer only reads ``str(exc)``."""


# A realistic service diagnostics tail, parameterised on the two fields that
# carry meaning plus one telemetry value that must be ignored.
_TAIL = (
    ", RequestStartTime: 2026-01-01T00:00:00Z, RequestEndTime: 2026-01-01T00:00:01Z,"
    ' Number of regions attempted:1 {{"systemHistory":[{{"dateUtc":"2026-01-01T00:00:00Z",'
    '"cpu":{cpu},"memory":856364468.000,"threadInfo":{{"availableThreads":32765}}}}]}}'
    " StoreResult: StorePhysicalAddress: rntbd://cdb-ms-prod-westus2-be316.documents.azure.com:{port}/"
    "apps/a/services/b/partitions/c/replicas/1p/, BELatencyMs: {latency},"
    " TransportRequestTimeline: {{\"requestSizeInBytes\":{size}}}"
    "; ResourceType: {resource_type}, OperationType: {operation_type}"
    " , Microsoft.Azure.Documents.Common/2.14.0"
)


def _service_error(head="(NotFound) Entity with the specified id does not exist in the system.",
                   *, resource_type="Document", operation_type="Read",
                   cpu="0.713", memory_port="15657", latency="0.264", size="715"):
    """Build an error whose text mimics a real gateway failure."""
    return _FakeError(head + _TAIL.format(
        cpu=cpu, port=memory_port, latency=latency, size=size,
        resource_type=resource_type, operation_type=operation_type))


# ---------------------------------------------------------------------------
# Noise must be removed
# ---------------------------------------------------------------------------

def test_two_calls_differing_only_in_service_telemetry_normalize_equal():
    """The exact failure this normalizer was written for.

    Same operation, same error, two different samples of the service's health
    and a different replica port. These must compare equal, or every live
    error-parity test flakes.
    """
    first = _service_error(cpu="0.713", memory_port="15657", latency="0.264", size="715")
    second = _service_error(cpu="0.334", memory_port="15989", latency="0.246", size="707")
    assert _normalize_exception_message(first) == _normalize_exception_message(second)


def test_telemetry_values_are_absent_from_the_normalized_text():
    """None of the machine-state readings survive normalization."""
    normalized = _normalize_exception_message(_service_error())
    for noise in ("systemHistory", "cpu", "memory", "BELatencyMs",
                  "requestSizeInBytes", "15657", "rntbd"):
        assert noise not in normalized, (
            "{!r} is per-request telemetry and must not survive normalization; "
            "got {!r}".format(noise, normalized))


def test_retry_that_repeats_the_tail_reads_the_same_as_one_attempt():
    """A retried request can carry the diagnostics tail twice.

    The two backends need not retry the same number of times, so a doubled
    tail must normalize to the same text as a single one.
    """
    once = _service_error()
    twice = _FakeError(str(once) + _TAIL.format(
        cpu="0.9", port="15383", latency="1.1", size="800",
        resource_type="Document", operation_type="Read"))
    assert _normalize_exception_message(once) == _normalize_exception_message(twice)


# ---------------------------------------------------------------------------
# Signal must survive
# ---------------------------------------------------------------------------

def test_canonical_server_error_text_is_preserved():
    """The part a customer's error handler actually reads stays intact."""
    normalized = _normalize_exception_message(_service_error())
    assert "(NotFound) Entity with the specified id does not exist in the system." in normalized


def test_operation_and_resource_type_are_preserved():
    """The two meaningful fields inside the tail are kept.

    Without these, a backend that issued the wrong operation kind would
    normalize identically to a correct one.
    """
    normalized = _normalize_exception_message(_service_error())
    assert "ResourceType: Document" in normalized
    assert "OperationType: Read" in normalized


def test_different_error_text_still_differs():
    """Normalization must not flatten genuinely different failures together."""
    not_found = _service_error("(NotFound) Entity with the specified id does not exist.")
    bad_request = _service_error("(BadRequest) Invalid partition key.")
    assert _normalize_exception_message(not_found) != _normalize_exception_message(bad_request)


def test_different_operation_type_still_differs():
    """A backend issuing Upsert where the other issued Read must be caught."""
    read = _service_error(operation_type="Read")
    upsert = _service_error(operation_type="Upsert")
    assert _normalize_exception_message(read) != _normalize_exception_message(upsert)


def test_different_resource_type_still_differs():
    """A backend addressing the wrong resource kind must be caught."""
    document = _service_error(resource_type="Document")
    stored_proc = _service_error(resource_type="StoredProcedure")
    assert _normalize_exception_message(document) != _normalize_exception_message(stored_proc)


# ---------------------------------------------------------------------------
# The two shapes the same service error arrives in
# ---------------------------------------------------------------------------
#
# Both strings below were captured live, from the same test, on the same
# account. Which backend produced which shape flipped between runs, which is
# how we know the difference is not a backend property.

_CANONICAL = ("(NotFound) Entity with the specified id does not exist in the system. "
              "More info: https://aka.ms/cosmosdb-tsg-not-found")
_SHORT_FORM = _CANONICAL
_LONG_FORM = (
    _CANONICAL + ", Windows/10.0.20348 cosmos-netstandard-sdk/3.18.0"
    " Code: NotFound Message: " + _CANONICAL
    + ", Windows/10.0.20348 cosmos-netstandard-sdk/3.18.0"
)


def test_echoed_and_plain_forms_of_the_same_error_normalize_equal():
    """The long form only repeats the short form; they must compare equal.

    Otherwise the missing-id tests fail roughly half the time, depending on
    which shape each backend happened to receive.
    """
    assert (_normalize_exception_message(_FakeError(_SHORT_FORM))
            == _normalize_exception_message(_FakeError(_LONG_FORM)))


def test_normalized_form_keeps_the_canonical_sentence_once():
    """The result is the canonical error text -- no echo, no host build tag."""
    normalized = _normalize_exception_message(_FakeError(_LONG_FORM))
    assert normalized == _CANONICAL, normalized
    assert "cosmos-netstandard-sdk" not in normalized
    assert normalized.count("Entity with the specified id") == 1


def test_echo_stripping_does_not_merge_different_errors():
    """Two different errors in the echoed shape must still differ."""
    other = _LONG_FORM.replace("(NotFound) Entity with the specified id does not exist",
                               "(BadRequest) Partition key is invalid")
    assert (_normalize_exception_message(_FakeError(_LONG_FORM))
            != _normalize_exception_message(_FakeError(other)))


def test_message_mentioning_code_without_the_echo_shape_is_untouched():
    """Only the ``Code: <reason> Message:`` echo is cut, not any mention of it.

    Guards against an over-broad rule that would truncate a legitimate error
    whose text happens to contain the word "Code".
    """
    exc = _FakeError("(BadRequest) Error Code: see docs for details")
    assert _normalize_exception_message(exc) == "(BadRequest) Error Code: see docs for details"


# ---------------------------------------------------------------------------
# Messages without a service tail must pass through untouched
# ---------------------------------------------------------------------------

def test_message_without_a_service_tail_is_left_alone():
    """Client-side errors never carry a diagnostics tail.

    ``ValueError``\\ s raised before any network call (the
    ``etag``-without-``match_condition`` gate, for instance) must compare on
    their full text.
    """
    plain = _FakeError("'etag' specified without 'match_condition'.")
    assert _normalize_exception_message(plain) == "'etag' specified without 'match_condition'."


def test_tail_carrying_no_meaningful_fields_reduces_to_the_error_text():
    """If the tail has no ResourceType/OperationType, only the head remains."""
    exc = _FakeError("(ServiceUnavailable) backend busy"
                     ", RequestStartTime: 2026-01-01T00:00:00Z, BELatencyMs: 3.2")
    assert _normalize_exception_message(exc) == "(ServiceUnavailable) backend busy"
