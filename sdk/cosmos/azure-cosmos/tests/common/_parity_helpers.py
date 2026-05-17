# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Helpers for the create_item parity test suite.

These helpers do the boilerplate each parity test would otherwise
repeat: build two ``CosmosClient``s (one core-python, one rust), run
the same call against each, capture the return value +
``last_response_headers`` + raised exception, and diff the two
outcomes side-by-side. Each individual test only writes the *call
shape* it cares about — setup, teardown, capture, and reporting all
live in this module.

Despite the file name and the create_item-flavored running examples,
**nothing in this module is specific to create_item**. The same
helpers work for every CRUD operation:

* ``run_on_both_backends(call_fn)`` accepts any
  ``Callable[[CosmosClient], Any]`` — the closure can call
  ``read_item``, ``upsert_item``, ``replace_item``, ``delete_item``,
  ``query_items``, even ``create_database``. The wrapper itself does
  not know or care which operation ran.
* ``diff_outcomes()`` accepts custom ``ignored_headers`` /
  ``ignored_body_fields`` so non-item responses (database /
  container metadata, query result pages) can plug in their own
  ignore set instead of the item-shaped defaults that live here.

This file implements:

  * ``run_on_both_backends(call_fn)`` — runs the call against both
    backends, returns a ``BackendComparison`` with the two outcomes
    and a list of diffs.
  * ``BackendComparison.print_report()`` — side-by-side dump of inputs
    and outputs (run pytest with ``-s`` to see it).

For tests that hit a known driver-side gap, mark them with pytest's
built-in ``@pytest.mark.skip(reason="...")`` and use the *reason* string
to name the specific limitation in plain English (e.g. "binding does
not yet wire <X>"). A grep against a phrase from any one reason then
finds every test waiting on the same fix. With only a handful of open
driver-team gaps today, a custom xfail-with-strict-mode marker would be
more machinery than the problem warrants.

The suite skips cleanly when no Cosmos account is configured. A real
parity run needs both the emulator (or a real account) **and** the
compiled ``azure.cosmos._rust`` binding present; either missing → skip,
not fail.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import pytest


# ---------------------------------------------------------------------------
# Environment gating
# ---------------------------------------------------------------------------

#: Standard env var consulted for the account endpoint.
ENV_ENDPOINT = "ACCOUNT_URI"
#: Standard env var consulted for the master key.
ENV_KEY = "ACCOUNT_KEY"


def have_emulator_or_account() -> bool:
    """True when both ``ACCOUNT_URI`` and ``ACCOUNT_KEY`` are set."""
    return bool(os.environ.get(ENV_ENDPOINT)) and bool(os.environ.get(ENV_KEY))


def have_rust_binding() -> bool:
    """True when the compiled ``azure.cosmos._rust`` module imports."""
    try:
        from azure.cosmos import _rust  # noqa: F401
        return True
    except ImportError:
        return False


def skip_unless_emulator():
    """Decorator: skip the test if no Cosmos account is configured."""
    return pytest.mark.skipif(
        not have_emulator_or_account(),
        reason="Set {} and {} to run parity tests.".format(ENV_ENDPOINT, ENV_KEY),
    )


def skip_unless_rust_binding():
    """Decorator: skip if ``azure.cosmos._rust`` was not built."""
    return pytest.mark.skipif(
        not have_rust_binding(),
        reason="Compiled azure.cosmos._rust binding missing — run `maturin develop`.",
    )



# ---------------------------------------------------------------------------
# BackendComparison
# ---------------------------------------------------------------------------

@dataclass
class CallOutcome:
    """One backend's observed result for a single call."""

    backend: str
    return_value: Any = None
    response_headers: Optional[Dict[str, str]] = None
    raised: Optional[BaseException] = None

    @property
    def succeeded(self) -> bool:
        return self.raised is None


@dataclass
class BackendComparison:
    """Side-by-side outcome from running the same call on both backends."""

    core_python: CallOutcome
    rust: CallOutcome
    diffs: List[str] = field(default_factory=list)
    #: Free-form description of the call that produced the two outcomes.
    #: Set by ``run_on_both_backends``; printed by ``print_report``.
    call_description: str = ""
    #: Optional request body that was sent (test-supplied, for reporting).
    request_body: Any = None
    #: Optional kwargs passed to the operation (test-supplied, for reporting).
    request_kwargs: Optional[Dict[str, Any]] = None

    @property
    def is_parity(self) -> bool:
        return not self.diffs

    def assert_parity(self):
        # Always print the side-by-side report on failure so the diff
        # is visible without having to rerun with -s.
        if self.diffs:
            print(self.format_report())
        assert self.is_parity, "Backend parity diffs:\n  - " + "\n  - ".join(self.diffs)

    def assert_functional_parity(self):
        """Assert parity ignoring response-header-surface-only differences.

        Today the rust backend exposes a smaller set of response headers
        than core-python (it omits things like ``x-ms-resource-quota`` /
        ``content-type`` / ``x-ms-content-path``). That's a known
        rust-binding reporting gap, not a behavioural difference: the
        request was sent, the server accepted it, the response body is
        equivalent. ``assert_functional_parity`` lets baseline tests pass
        in that state while the printed report still calls the gap out
        in the VERDICT line. Use ``assert_parity`` (strict) for tests
        that explicitly cover header-surface parity itself.
        """
        non_header_diffs = [
            d for d in self.diffs
            if not d.startswith("headers only on ") and not d.startswith("header ")
        ]
        if non_header_diffs:
            print(self.format_report())
            assert False, (
                "Functional parity diffs (excluding response-header surface):\n"
                "  - " + "\n  - ".join(non_header_diffs)
            )
        # Always print the report so the user sees the verdict line.
        self.print_report()

    def format_report(self) -> str:
        """Return a side-by-side string dump of inputs + outputs."""
        import json as _json
        lines: List[str] = []
        lines.append("=" * 78)
        lines.append("PARITY CALL: {}".format(self.call_description or "(unset)"))
        lines.append("=" * 78)
        # --- Request side (test-supplied, identical for both backends) ---
        if self.request_body is not None or self.request_kwargs:
            lines.append("--- REQUEST (sent to both backends) ---")
            if self.request_body is not None:
                try:
                    body_str = _json.dumps(self.request_body, indent=2, default=str)
                except (TypeError, ValueError):
                    body_str = repr(self.request_body)
                lines.append("  body:")
                for bl in body_str.splitlines():
                    lines.append("    " + bl)
            if self.request_kwargs:
                lines.append("  kwargs: {!r}".format(self.request_kwargs))
            else:
                lines.append("  kwargs: (none -- body + mandatory fields only)")
        for label, oc in (("CORE-PYTHON", self.core_python), ("RUST", self.rust)):
            lines.append("--- {} ---".format(label))
            if oc.succeeded:
                lines.append("  status:        OK")
                try:
                    rv_str = _json.dumps(oc.return_value, indent=2, default=str)
                except (TypeError, ValueError):
                    rv_str = repr(oc.return_value)
                lines.append("  response body:")
                for rl in rv_str.splitlines():
                    lines.append("    " + rl)
            else:
                lines.append("  status:        RAISED")
                lines.append("  exception:     {}".format(type(oc.raised).__name__))
                msg = str(oc.raised)
                if len(msg) > 400:
                    msg = msg[:400] + " ...[truncated]"
                lines.append("  message:       {}".format(msg))
                for attr in ("status_code", "sub_status"):
                    v = getattr(oc.raised, attr, None)
                    if v is not None:
                        lines.append("  {}: {!r}".format(attr, v))
            hdrs = oc.response_headers or {}
            lines.append("  response headers ({} total):".format(len(hdrs)))
            for k in sorted(hdrs):
                lines.append("    {}: {}".format(k, hdrs[k]))
        lines.append("--- DIFFS ---")
        if not self.diffs:
            lines.append("  (none -- full parity)")
        else:
            lines.append("  (note: 'headers only on core-python' = headers that "
                         "core-python returned but the rust binding did NOT "
                         "surface; 'headers only on rust' = the reverse.)")
        for d in self.diffs:
            lines.append("  - " + d)
        lines.append("--- VERDICT ---")
        lines.append("  " + self._verdict())
        lines.append("=" * 78)
        return "\n".join(lines)

    def _verdict(self) -> str:
        """Plain-English summary of what the diff means."""
        core_ok = self.core_python.succeeded
        rust_ok = self.rust.succeeded
        if not self.diffs:
            return "FULL PARITY: both backends produced equivalent outcomes."
        if core_ok != rust_ok:
            return ("FUNCTIONAL DIVERGENCE: one backend succeeded, the other "
                    "raised. The operation behaves differently — investigate.")
        if core_ok and rust_ok:
            non_header = [d for d in self.diffs
                          if not d.startswith("headers only on ")
                          and not d.startswith("header ")]
            if not non_header:
                return ("FUNCTIONAL PARITY, REPORTING GAP: both backends "
                        "performed the operation successfully and returned "
                        "equivalent response bodies. The rust backend exposes "
                        "a smaller set of response headers -- this is a known "
                        "rust-binding limitation, not a create_item failure.")
            return ("FUNCTIONAL DIVERGENCE: response bodies or values differ "
                    "between the backends.")
        return ("EXCEPTION DIVERGENCE: both backends raised, but the typed "
                "exception or status code differs.")


    def print_report(self):
        """Print the side-by-side report unconditionally. Use ``-s`` to see it."""
        print(self.format_report())


# Response headers Cosmos guarantees on every successful response (and that
# customer code reads back) — the *value* is per-request noisy (a fresh
# request charge / activity id / etag / etc. every call) but the *header*
# must be present on both backends. ``diff_outcomes`` skips these in the
# value-diff but enforces presence: if one backend emits the header and the
# other doesn't, that's a parity failure.
_VALUE_VOLATILE_REQUIRED_HEADERS = frozenset({
    "x-ms-request-charge",
    "x-ms-activity-id",
    "x-ms-session-token",
    "etag",
    "x-ms-serviceversion",
    "x-ms-gatewayversion",
    "x-ms-request-duration-ms",
    "x-ms-global-committed-lsn",
    "x-ms-number-of-read-regions",
    "x-ms-transport-request-id",
    "lsn",
})

# Headers whose *presence itself* is environment-, replica-, topology-, or
# transport-dependent — both the value and the presence are dropped from
# the diff. These either have legitimate naming conflicts across the two
# backends, surface only on certain account configurations, or come from
# the underlying HTTP transport rather than from Cosmos.
_FULLY_IGNORED_HEADERS = frozenset({
    # Body field, not a response header — leftover in the original ignore
    # set from when body and header filtering shared code.
    "_etag",
    # HTTP ``date`` header: emitted by every HTTP server, but the rust
    # driver does not yet expose it (HTTP-framing headers need a
    # ``raw_headers()`` accessor that hasn't landed). Once the driver
    # surfaces it, move this back to the value-volatile bucket.
    "date",
    # Per-container counters that tick up with each create. When the parity
    # harness runs the same call against both backends consecutively, the
    # second backend's response shows the count after the first backend's
    # insert — so value-diffs here are harness artefacts, not backend
    # divergences.
    "x-ms-resource-usage",
    "x-ms-resource-quota",
    "x-ms-session-token-rid",
    # Cross-backend naming wart: the legacy core-python path emits this
    # *without* the ``cosmos-`` prefix and the rust path emits it *with*
    # (see lib.rs::write_response_headers). We can't presence-check
    # because the *names* differ; fully ignored until the binding aligns.
    "x-ms-cosmos-llsn",
    "x-ms-quorum-acked-lsn",
    "x-ms-cosmos-quorum-acked-lsn",
    "x-ms-cosmos-item-llsn",
    "x-ms-cosmos-quorum-acked-llsn",
    # Replica / topology diagnostics — presence varies with account
    # configuration and routing decisions.
    "x-ms-current-write-quorum",
    "x-ms-current-replica-set-size",
    "x-ms-xp-role",
    "x-ms-cosmos-physical-partition-id",
    "x-ms-cosmos-replica-side-cache-token",
    "x-ms-schemaversion",
    # HTTP ``server`` header: differs by transport (azure-core uses
    # urllib3 / requests; rust transport uses reqwest), no parity
    # guarantee on presence.
    "server",
})

# Combined set used to filter the value-diff. Tests that want a custom
# scope can pass their own frozenset to ``diff_outcomes(ignored_headers=...)``.
# The presence check below always runs against ``_VALUE_VOLATILE_REQUIRED_HEADERS``
# regardless of what's passed for ``ignored_headers``.
_DEFAULT_IGNORED_HEADERS = _VALUE_VOLATILE_REQUIRED_HEADERS | _FULLY_IGNORED_HEADERS

# Body fields that legitimately differ between create calls and so
# are excluded from return-value diffs by default:
#
#   - ``_rid``, ``_self``, ``_ts``, ``_etag``, ``_attachments`` — the
#     five server-stamped per-document fields (resource id, self
#     link, timestamp, etag, attachments link). Different on every
#     successful create even when the request body is identical.
#
#   - ``id`` — for create-style parity tests the test harness in
#     ``test_create_item_parity.py::_call`` deep-copies the body
#     template and rewrites ``id`` with a fresh UUID4 *per backend
#     invocation*. That keeps the second backend from getting a 409
#     on what would otherwise look like a duplicate create. The cost
#     is that backend 1 and backend 2 genuinely create different
#     items, so their returned ``id`` values differ by construction.
#     That's a harness artefact, not
#     a backend-behaviour difference, so the diff ignores it.
#
#     KNOWN COVERAGE GAP: because ``id`` is rewritten per-backend AND
#     ignored on the return-value diff, the create-item parity suite
#     CANNOT detect id-handling parity bugs end-to-end -- e.g. a
#     binding that silently lower-cased the id, or stripped a
#     trailing space, or rejected a legitimate id format. Customer-
#     level "the id we sent matches the id we got back" is therefore
#     covered separately by the unit tests in
#     ``test_request_prep_unit.py`` and ``test_auto_id_unit.py``,
#     which build a ``PreparedRequest`` deterministically and assert
#     on the body bytes before any backend dispatch. If a parity gap
#     opens up specifically around id round-tripping, add a focused
#     test that uses ``id_factory_per_backend=lambda: SAME_ID`` (or
#     equivalent) and removes ``"id"`` from ``ignored_body_fields``
#     for just that one assertion -- do NOT broaden the default
#     ignore-set here.
_DEFAULT_IGNORED_BODY_FIELDS = frozenset({
    "id",
    "_rid", "_self", "_ts", "_etag", "_attachments",
})


def _filtered_headers(h: Optional[Dict[str, str]],
                      ignored: frozenset) -> Dict[str, str]:
    if h is None:
        return {}
    return {k.lower(): v for k, v in h.items() if k.lower() not in ignored}


def _filtered_body(b: Any, ignored: frozenset) -> Any:
    if isinstance(b, dict):
        return {k: v for k, v in b.items() if k not in ignored}
    return b


# Patterns used to scrub per-request noise out of exception messages
# before comparing them across backends. Each entry is (regex, replacement).
# Order matters only inasmuch as later substitutions see the output of
# earlier ones. The intent is "two backends raising semantically the
# same error produce the same normalised text" -- *not* byte-identity
# of the raw ``str(exc)``.
_EXCEPTION_MESSAGE_NOISE = [
    # Activity / correlation IDs, transport request IDs, RIDs, etc. --
    # any UUID-shaped token. Covers both lowercase (azure-core default)
    # and uppercase variants the driver sometimes emits.
    (re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"), "<uuid>"),
    # Cosmos resource ids (base64-ish, often 8-22 chars with == padding)
    # that appear inside diagnostics blobs and self-links.
    (re.compile(r"\b[A-Za-z0-9+/]{8,}={0,2}\b"), "<rid>"),
    # ISO-8601 timestamps the driver embeds in diagnostics summaries.
    (re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?"), "<ts>"),
    # Numeric durations / counters that appear in diagnostics
    # ("duration in milliseconds":1.9737, "Count":1, etc.).
    (re.compile(r":\s*\d+(?:\.\d+)?"), ":<n>"),
    # Collapse any whitespace run -- including embedded newlines from
    # the driver's multi-line diagnostics dump -- to a single space so
    # platform line-endings don't matter.
    (re.compile(r"\s+"), " "),
]


def _normalize_exception_message(exc: BaseException) -> str:
    """Strip per-request noise out of an exception's text for diffing.

    Replaces UUIDs, RIDs, timestamps, and numeric counters with stable
    placeholders. Truncates after the first 240 characters so an
    arbitrarily long diagnostics blob does not dominate the report.
    """
    if exc is None:
        return ""
    text = str(exc)
    for pattern, replacement in _EXCEPTION_MESSAGE_NOISE:
        text = pattern.sub(replacement, text)
    text = text.strip()
    return text[:240]


def diff_outcomes(
    core: CallOutcome,
    rust: CallOutcome,
    *,
    ignored_headers: frozenset = _DEFAULT_IGNORED_HEADERS,
    ignored_body_fields: frozenset = _DEFAULT_IGNORED_BODY_FIELDS,
) -> List[str]:
    """Compare two outcomes and return a list of human-readable diff lines.

    Empty list = parity. Each diff line names the dimension and the
    two values, so a failure message is self-explanatory.
    """
    diffs: List[str] = []

    # 1. Success vs failure must agree.
    if core.succeeded != rust.succeeded:
        diffs.append(
            "outcome: core-python {} / rust {}".format(
                "succeeded" if core.succeeded else "raised " + type(core.raised).__name__,
                "succeeded" if rust.succeeded else "raised " + type(rust.raised).__name__,
            )
        )
        return diffs  # downstream comparisons are meaningless if outcomes differ

    if not core.succeeded:
        # Both raised -- compare exception type, status_code, sub_status,
        # and a normalised form of the message. The raw ``str(exc)`` is
        # full of per-request noise (activity-ids, RIDs, timestamps,
        # transport-request-ids, free-form diagnostics blobs) that would
        # diff on every run even at true parity, so we strip those
        # before comparing. The goal is to catch *semantic* message
        # divergence ("BadRequest: trigger not present" vs "Unknown
        # 409") -- not to enforce byte-identical exception text.
        if type(core.raised) is not type(rust.raised):
            diffs.append(
                "exception type: core-python {} / rust {}".format(
                    type(core.raised).__name__, type(rust.raised).__name__,
                )
            )
        for attr in ("status_code", "sub_status"):
            cv = getattr(core.raised, attr, None)
            rv = getattr(rust.raised, attr, None)
            if cv != rv:
                diffs.append("exception.{}: core-python {!r} / rust {!r}".format(attr, cv, rv))
        cm = _normalize_exception_message(core.raised)
        rm = _normalize_exception_message(rust.raised)
        if cm != rm:
            diffs.append(
                "exception.message (normalised): core-python {!r} / rust {!r}".format(cm, rm)
            )
        return diffs

    # 2. Both succeeded — diff filtered body and headers.
    cb = _filtered_body(core.return_value, ignored_body_fields)
    rb = _filtered_body(rust.return_value, ignored_body_fields)
    if cb != rb:
        diffs.append("return_value: core-python {!r} / rust {!r}".format(cb, rb))

    ch = _filtered_headers(core.response_headers, ignored_headers)
    rh = _filtered_headers(rust.response_headers, ignored_headers)
    if set(ch) != set(rh):
        only_core = sorted(set(ch) - set(rh))
        only_rust = sorted(set(rh) - set(ch))
        if only_core:
            diffs.append("headers only on core-python: {}".format(only_core))
        if only_rust:
            diffs.append("headers only on rust: {}".format(only_rust))
    for k in set(ch) & set(rh):
        if ch[k] != rh[k]:
            diffs.append("header {}: core-python {!r} / rust {!r}".format(k, ch[k], rh[k]))

    # Presence check for the value-volatile headers Cosmos guarantees on
    # every successful response. Without this loop, the filter above drops
    # those headers from both sides before the key-set diff, so a binding
    # silently dropping (say) ``x-ms-request-charge`` would go undetected.
    # The presence check runs against the *unfiltered* response headers and
    # uses ``_VALUE_VOLATILE_REQUIRED_HEADERS`` regardless of the
    # ``ignored_headers`` override, since those headers are part of the
    # cross-backend contract.
    core_names = {k.lower() for k in (core.response_headers or {})}
    rust_names = {k.lower() for k in (rust.response_headers or {})}
    for header in sorted(_VALUE_VOLATILE_REQUIRED_HEADERS):
        in_core = header in core_names
        in_rust = header in rust_names
        if in_core and not in_rust:
            diffs.append(
                "value-volatile header {!r}: present on core-python, missing on rust"
                .format(header)
            )
        elif in_rust and not in_core:
            diffs.append(
                "value-volatile header {!r}: present on rust, missing on core-python"
                .format(header)
            )

    return diffs


# ---------------------------------------------------------------------------
# run_on_both_backends
# ---------------------------------------------------------------------------

ClientFactory = Callable[[str], Any]
"""Signature: ``factory(backend_name) -> CosmosClient``."""


def _default_client_factory(backend_name: str):
    """Build a sync CosmosClient for the named backend against ACCOUNT_URI/KEY."""
    from azure.cosmos import CosmosClient
    return CosmosClient(
        os.environ[ENV_ENDPOINT],
        os.environ[ENV_KEY],
        _backend=backend_name,  # type: ignore[arg-type]
    )


def run_on_both_backends(
    call_fn: Callable[[Any], Any],
    *,
    client_factory: ClientFactory = _default_client_factory,
    description: str = "",
    request_body: Any = None,
    request_kwargs: Optional[Dict[str, Any]] = None,
) -> BackendComparison:
    """Run ``call_fn(client)`` against both backends and diff the outcomes.

    ``call_fn`` is the customer-shaped piece — it receives a
    ``CosmosClient`` and returns whatever the call under test returns
    (typically a ``CosmosDict`` from ``container.create_item``). It
    must be deterministic given the same client (same body, same id,
    same kwargs) so the diff is meaningful.

    This function records the return value, the
    ``client_connection.last_response_headers`` snapshot, and (on
    failure) the raised exception. The two outcomes are then run
    through :func:`diff_outcomes`. The optional ``description`` is
    just a label for the printed report — usually the test name.
    """
    outcomes: Dict[str, CallOutcome] = {}
    for backend_name in ("core-python", "rust"):
        outcome = CallOutcome(backend=backend_name)
        client = None
        try:
            client = client_factory(backend_name)
            outcome.return_value = call_fn(client)
            outcome.response_headers = dict(
                client.client_connection.last_response_headers or {}
            )
        except BaseException as exc:  # pylint: disable=broad-except
            outcome.raised = exc
            if client is not None:
                outcome.response_headers = dict(
                    client.client_connection.last_response_headers or {}
                )
        outcomes[backend_name] = outcome

    comparison = BackendComparison(
        core_python=outcomes["core-python"],
        rust=outcomes["rust"],
        call_description=description,
        request_body=request_body,
        request_kwargs=request_kwargs,
    )
    comparison.diffs = diff_outcomes(comparison.core_python, comparison.rust)
    return comparison

