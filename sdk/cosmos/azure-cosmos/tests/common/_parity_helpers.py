# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Shared helpers for the cross-backend parity test suites.

Each individual test only writes the call shape it cares about; this
module handles the rest: build a core-python and a rust ``CosmosClient``,
invoke the same closure against each, capture return value plus
``last_response_headers`` plus any raised exception, and diff the two
outcomes.

The helpers are operation-agnostic. ``run_on_both_backends(call_fn)``
accepts any ``Callable[[CosmosClient], Any]`` so the same harness covers
``create_item``, ``read_item``, ``delete_item``, ``query_items``, etc.

Tests that hit a known driver gap are marked with
``@pytest.mark.skip(reason="...")`` and use the reason string to name the
limitation in plain English.

The suite skips cleanly when ``ACCOUNT_HOST`` / ``ACCOUNT_KEY`` are not
set or when the compiled ``azure.cosmos._rust`` binding is not present.
"""
from __future__ import annotations

import asyncio
import json as _json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Dict, List, Optional, Tuple

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AioCosmosClient


# ---------------------------------------------------------------------------
# Environment gating
# ---------------------------------------------------------------------------

#: Standard env var consulted for the account endpoint.
ENV_ENDPOINT = "ACCOUNT_HOST"
#: Standard env var consulted for the master key.
ENV_KEY = "ACCOUNT_KEY"


def have_emulator_or_account() -> bool:
    """True when both ``ACCOUNT_HOST`` and ``ACCOUNT_KEY`` are set."""
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
        reason="Compiled azure.cosmos._rust binding missing -- run `maturin develop`.",
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

        The "header diff" filter must match the prefixes ``_verdict``
        recognises (see ``_HEADER_DIFF_PREFIXES``) so the two helpers
        agree on what counts as a header-only divergence.
        """
        non_header_diffs = [
            d for d in self.diffs
            if not any(d.startswith(p) for p in self._HEADER_DIFF_PREFIXES)
        ]
        if non_header_diffs:
            print(self.format_report())
            assert False, (
                "Functional parity diffs (excluding response-header surface):\n"
                "  - " + "\n  - ".join(non_header_diffs)
            )
        # Always print the report so the user sees the verdict line.
        self.print_report()

    def assert_exception_parity(self):
        """Both backends raised the same typed exception with the same
        status_code and sub_status. The message text is not compared: the rust
        path appends the raw server error body, which is informational, not part
        of the typed-exception contract a caller catches on.
        """
        self._assert_exception_contract()
        exception_diffs = diff_outcomes(self.core_python, self.rust)
        assert not exception_diffs, (
            "Exception parity diffs:\n  - " + "\n  - ".join(exception_diffs)
        )

    def assert_functional_exception_parity(self):
        """Assert the typed exception contract while reporting known header gaps."""
        self._assert_exception_contract()
        non_header_diffs = [
            diff
            for diff in diff_outcomes(self.core_python, self.rust)
            if not any(diff.startswith(prefix) for prefix in self._HEADER_DIFF_PREFIXES)
        ]
        if non_header_diffs:
            print(self.format_report())
            assert False, (
                "Functional exception parity diffs "
                "(excluding response-header surface):\n  - "
                + "\n  - ".join(non_header_diffs)
            )
        self.print_report()

    def _assert_exception_contract(self):
        core_exc, rust_exc = self.core_python.raised, self.rust.raised
        if core_exc is None or rust_exc is None:
            print(self.format_report())
        assert core_exc is not None and rust_exc is not None, "both backends must raise"
        assert type(core_exc) is type(rust_exc), (
            "exception type: core-python {} / rust {}".format(
                type(core_exc).__name__, type(rust_exc).__name__))
        for attr in ("status_code", "sub_status"):
            assert getattr(core_exc, attr, None) == getattr(rust_exc, attr, None), (
                "exception.{} differs: core-python {!r} / rust {!r}".format(
                    attr, getattr(core_exc, attr, None), getattr(rust_exc, attr, None)))
        core_message = _normalize_exception_message(core_exc)
        rust_message = _normalize_exception_message(rust_exc)
        assert core_message == rust_message, (
            "exception.message differs after normalization: core-python {!r} / "
            "rust {!r}".format(core_message, rust_message)
        )

    def format_report(self) -> str:
        """Return a side-by-side string dump of inputs + outputs."""
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
        # The verdict may be multi-line when it lists the pushback
        # cross-references for a HEADER GAP. Indent every line so
        # the VERDICT section stays visually aligned with DIFFS above.
        for vl in self._verdict().splitlines() or [""]:
            lines.append("  " + vl)
        lines.append("=" * 78)
        return "\n".join(lines)

    # ----- Verdict helpers ---------------------------------------------------
    #
    # The three diff-line shapes that count as "header diffs" -- prefixes
    # we recognise in ``_verdict`` and ``assert_functional_parity``. Any
    # diff line not matching one of these is a body / return-value diff
    # and means a real functional divergence.
    _HEADER_DIFF_PREFIXES: ClassVar[Tuple[str, ...]] = (
        "headers only on ",       # presence: header set differs
        "header ",                # value: same header, different value
        "value-volatile header ", # presence: required volatile header missing one side
    )

    # Header-name -> pushback cross-reference. Used by ``_verdict`` to
    # tell a reader, for every header gap in DIFFS, whether the gap is
    # already tracked as a known rust-side pushback and where. Keys are
    # lower-cased header names; values are the pushback number plus a
    # one-line summary of that pushback's status. Any header mentioned
    # in a diff line and not in this dict gets bucketed under "not yet
    # recorded" so the next reviewer knows whether to file a new entry
    # or strengthen an existing one.
    _PUSHBACK_RAW_HEADERS: ClassVar[Tuple[int, str]] = (
        6,
        "raw-headers accessor on the diagnostics object — half-landed "
        "(error path shipped in driver v0.4.0; success path still open)",
    )
    _PUSHBACK_TYPED_HEADERS: ClassVar[Tuple[int, str]] = (
        7,
        "five typed headers missing from CosmosResponseHeaders — open "
        "against driver v0.4.0",
    )
    _PUSHBACK_CONTAINER_IDENTITY: ClassVar[Tuple[int, str]] = (
        8,
        "container-identity headers parsed but pub(crate) in the driver "
        "— wont-fix (revisit only with a customer escalation)",
    )
    _PUSHBACK_DIAGNOSTIC_HEADERS: ClassVar[Tuple[int, str]] = (
        21,
        "diagnostic/networking headers that differ by backend — low "
        "customer impact, tracked for audit-signal cleanup",
    )
    _HEADER_TO_PUSHBACK: ClassVar[Dict[str, Tuple[int, str]]] = {
        # #6 — HTTP framing headers azure-core surfaces but the rust
        # binding's typed projection drops.
        "date": _PUSHBACK_RAW_HEADERS,
        "server": _PUSHBACK_RAW_HEADERS,
        "content-type": _PUSHBACK_RAW_HEADERS,
        "content-length": _PUSHBACK_RAW_HEADERS,
        "cache-control": _PUSHBACK_RAW_HEADERS,
        "pragma": _PUSHBACK_RAW_HEADERS,
        "strict-transport-security": _PUSHBACK_RAW_HEADERS,
        # #7 — five typed Cosmos headers not modelled on
        # CosmosResponseHeaders.
        "x-ms-cosmos-physical-partition-id": _PUSHBACK_TYPED_HEADERS,
        "x-ms-current-replica-set-size": _PUSHBACK_TYPED_HEADERS,
        "x-ms-current-write-quorum": _PUSHBACK_TYPED_HEADERS,
        "x-ms-xp-role": _PUSHBACK_TYPED_HEADERS,
        "x-ms-schemaversion": _PUSHBACK_TYPED_HEADERS,
        # #8 — container-identity headers explicitly declined.
        "x-ms-alt-content-path": _PUSHBACK_CONTAINER_IDENTITY,
        "x-ms-content-path": _PUSHBACK_CONTAINER_IDENTITY,
        # #21 — diagnostic/networking headers that differ by backend
        # (one dropped by rust, two added only by rust). No body impact.
        "x-ms-thinclient-route-via-proxy": _PUSHBACK_DIAGNOSTIC_HEADERS,
        "x-ms-cosmos-internal-partition-id": _PUSHBACK_DIAGNOSTIC_HEADERS,
        "x-ms-cosmos-sdk-diagnostics": _PUSHBACK_DIAGNOSTIC_HEADERS,
    }

    def _is_header_diff(self, line: str) -> bool:
        return any(line.startswith(p) for p in self._HEADER_DIFF_PREFIXES)

    @staticmethod
    def _extract_header_names(line: str) -> List[str]:
        """Pull the header name(s) referenced by a diff line.

        Returns a list because ``headers only on core-python: ['a', 'b']``
        names more than one. The other shapes name exactly one.
        Returns ``[]`` for any line we don't recognise as a header diff.
        """
        # "headers only on core-python: ['a', 'b']" or same with rust
        if line.startswith("headers only on "):
            try:
                bracket_open = line.index("[")
                bracket_close = line.rindex("]")
                inner = line[bracket_open + 1:bracket_close]
                return [
                    s.strip().strip("'").strip('"').lower()
                    for s in inner.split(",")
                    if s.strip()
                ]
            except ValueError:
                return []
        # "header x-ms-foo: core-python '...' / rust '...'"
        if line.startswith("header "):
            rest = line[len("header "):]
            if ":" in rest:
                return [rest.split(":", 1)[0].strip().lower()]
            return []
        # "value-volatile header 'x-ms-foo': present on core-python, missing on rust"
        if line.startswith("value-volatile header "):
            rest = line[len("value-volatile header "):]
            if "'" in rest:
                # name is single-quoted
                first_q = rest.index("'")
                second_q = rest.index("'", first_q + 1)
                return [rest[first_q + 1:second_q].lower()]
            return []
        return []

    def _verdict(self) -> str:
        """Plain-English summary of what the diff means.

        For HEADER-GAP verdicts the output is multi-line: the first
        line names the bucket, then a per-pushback breakdown lists
        every header gap in DIFFS grouped by the pushback that already
        tracks it (or under "not yet recorded" so the next reviewer
        knows to file a new entry).
        """
        core_ok = self.core_python.succeeded
        rust_ok = self.rust.succeeded
        if not self.diffs:
            return "FULL PARITY: both backends produced equivalent outcomes."
        if core_ok != rust_ok:
            return ("FUNCTIONAL DIVERGENCE: one backend succeeded, the other "
                    "raised. The operation behaves differently -- investigate.")
        if core_ok and rust_ok:
            header_diffs = [d for d in self.diffs if self._is_header_diff(d)]
            body_diffs = [d for d in self.diffs if not self._is_header_diff(d)]
            if body_diffs:
                return ("FUNCTIONAL DIVERGENCE: response bodies or values "
                        "differ between the backends. {} body-or-value diff(s); "
                        "{} header diff(s).".format(len(body_diffs), len(header_diffs)))
            # Header-only divergence. Group by pushback.
            grouped: Dict[tuple, List[str]] = {}
            unrecorded: List[str] = []
            seen: set = set()
            for d in header_diffs:
                for name in self._extract_header_names(d):
                    if name in seen:
                        continue
                    seen.add(name)
                    pb = self._HEADER_TO_PUSHBACK.get(name)
                    if pb is None:
                        unrecorded.append(name)
                    else:
                        grouped.setdefault(pb, []).append(name)
            out: List[str] = [
                "FUNCTIONAL PARITY, HEADER GAP: both backends performed "
                "the operation successfully and returned response bodies "
                "that match on every customer-visible field (the harness "
                "filters the six per-document server-stamped fields it "
                "treats as test noise: id, _rid, _self, _ts, _etag, "
                "_attachments). The header-surface differences below are "
                "all known rust-binding gaps; the tracked pushback for each "
                "follows."
            ]
            # Render recorded buckets in pushback-number order.
            for pb_key in sorted(grouped.keys(), key=lambda k: k[0]):
                pb_num, pb_desc = pb_key
                hdrs = sorted(grouped[pb_key])
                out.append("  - Pushback #{n} ({desc}):".format(n=pb_num, desc=pb_desc))
                out.append("      {}".format(", ".join(hdrs)))
            if unrecorded:
                out.append(
                    "  - NOT YET RECORDED as a known pushback "
                    "(file a new entry if this persists):"
                )
                out.append("      {}".format(", ".join(sorted(unrecorded))))
            else:
                out.append(
                    "  - NEW PUSHBACK NOT NEEDED: every header gap above is "
                    "already tracked as a known pushback."
                )
            return "\n".join(out)
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
    # HTTP transport-layer headers core-python surfaces via azure-core's
    # underlying HTTP transport. Values are legitimately noisy (``date``
    # ticks every second; ``server`` identifies the transport / gateway
    # software and differs between core-python and rust), but customer
    # code and ops dashboards read them, so the parity contract is
    # "both backends must surface *some* value." Presence is enforced.
    # On the Rust path today both are missing because the binding only
    # projects fields the driver explicitly models in ``cosmos_headers.rs``
    # and HTTP-framing headers aren't modeled. That's a binding-projection
    # gap (the driver needs a raw-headers accessor on its response so the
    # binding can forward them) — the failing presence check is the
    # signal that closes the loop.
    "date",
    "server",
    # Resource accounting — capacity dashboards read these. Values tick
    # up between the two back-to-back parity calls because the first
    # call creates the item the second call's response then sees, so
    # the value diff has to skip; both backends must surface them.
    "x-ms-resource-quota",
    "x-ms-resource-usage",
    # LSN family — replica/replication-progress counters. Different
    # replicas legitimately answer different calls so the value
    # legitimately differs, but the presence is part of the diagnostics
    # contract. Two name families coexist on the wire, both gateway-
    # emitted and faithfully surfaced by both backends:
    #   * the cosmos-prefixed double-l names (``x-ms-cosmos-llsn``,
    #     ``x-ms-cosmos-item-llsn``);
    #   * the un-prefixed single-l names (``x-ms-item-lsn``, ``lsn``).
    # The un-prefixed *double*-l aliases (``x-ms-llsn`` /
    # ``x-ms-item-llsn``) are not on this list: the gateway does not
    # emit them and neither backend surfaces them, so there is nothing
    # to presence-check.
    "x-ms-cosmos-llsn",
    "x-ms-cosmos-item-llsn",
    "x-ms-item-lsn",
    # Topology / diagnostic IDs — which replica answered, the routing
    # decision the gateway made, the schema version of the responding
    # replica. Values differ across replicas / calls; presence is part
    # of the diagnostics contract customer ops code and the SDK's own
    # routing logic depend on.
    "x-ms-documentdb-partitionkeyrangeid",
    "x-ms-cosmos-physical-partition-id",
    "x-ms-current-write-quorum",
    "x-ms-current-replica-set-size",
    "x-ms-xp-role",
    "x-ms-schemaversion",
    # Per-container internal-partition UUID. Both backends emit it,
    # but the value is a fresh GUID minted per physical partition by
    # the service, so each backend's freshly-created test container
    # gets its own value. Presence is part of the diagnostics surface
    # support engineers correlate against; value is per-container
    # noise.
    "x-ms-cosmos-internal-partition-id",
    # Cluster-side "last partition-map state change" timestamp. Both
    # backends surface it, but the value moves whenever the cluster's
    # partition map ticks (which happens at minute-scale intervals on
    # a live account), so two parity calls captured even seconds apart
    # routinely land on different values. Presence is part of the
    # routing-diagnosis surface; value is wall-clock noise.
    "x-ms-last-state-change-utc",
})

# Headers (and one body field) where both value and presence
# are dropped from the diff. The bar for adding to this set is very
# high: an entry only qualifies if *neither* backend can plausibly
# surface the value to a customer. "Undocumented" alone is not enough,
# because the core-python transport copies *every* response header the
# service returns through to ``last_response_headers`` (the request
# path does ``headers = copy.copy(response.headers)`` on both sync and
# async), so any header the gateway emits can legitimately appear on
# the Python side — and silently ignoring it here would mask a real
# Python↔Rust header-surface drift (the binding dropping something the
# legacy path is surfacing).
#
# So a header the gateway may echo into core-python's
# ``last_response_headers`` -- ``x-ms-session-token-rid`` and
# ``x-ms-cosmos-replica-side-cache-token`` are two -- does not belong
# here. It belongs in the full presence-and-value diff bucket (the
# implicit "everything else" population), where the diff will show how
# often it appears and whether either backend needs a tweak.
_FULLY_IGNORED_HEADERS = frozenset({
    # Body field, not a response header (the ``etag`` response header
    # is a separate key). Kept as defence in depth alongside
    # ``_DEFAULT_IGNORED_BODY_FIELDS`` below, in case a caller wires
    # the body field set into the header filter by mistake. Safe to
    # keep because it is structurally not a header name either backend
    # could ever surface from a response.
    "_etag",
})

# Headers the Cosmos gateway emits *non-deterministically* -- whether
# the header appears on a given response depends on which replica
# answered, the consistency level on the request, and other server-
# side conditions outside the SDK's control. The evidence is that the
# SAME header can appear "only on core-python" in one test and "only
# on rust" in the next test of the same parity run (compare the
# ``read_item`` ``TestNoneOptions`` and ``TestNoneOptionsAsync``
# results). Enforcing presence here would produce false-positive
# "rust gaps" the binding cannot fix, so these headers are dropped
# from BOTH the value diff (they're in ``_DEFAULT_IGNORED_HEADERS``
# below) AND the value-volatile presence-required loop
# (``diff_outcomes`` skips them explicitly).
#
# The bar for adding to this set is high: pick this only when the
# evidence shows the gateway sometimes-emits-sometimes-omits on the
# SAME backend, not just "one backend doesn't surface it". The
# latter is a real binding gap and belongs in a tracked rust-side
# issue.
_WIRE_NONDETERMINISTIC_HEADERS = frozenset({
    # Quorum-acked family -- replication-quorum diagnostics that the
    # gateway emits per request based on which replica answered.
    "x-ms-quorum-acked-lsn",
    "x-ms-quorum-acked-llsn",
    "x-ms-cosmos-quorum-acked-llsn",
})

# Combined set used to filter the value-diff. Tests that want a custom
# scope can pass their own frozenset to ``diff_outcomes(ignored_headers=...)``.
# The presence check below always runs against ``_VALUE_VOLATILE_REQUIRED_HEADERS``
# regardless of what's passed for ``ignored_headers``, but
# ``_WIRE_NONDETERMINISTIC_HEADERS`` is excluded from BOTH passes.
_DEFAULT_IGNORED_HEADERS = (
    _VALUE_VOLATILE_REQUIRED_HEADERS
    | _FULLY_IGNORED_HEADERS
    | _WIRE_NONDETERMINISTIC_HEADERS
)

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
    # List-returning operations (e.g. read_items) hand back a list of
    # documents. Strip the same server-stamped / per-run fields from
    # each element so the diff compares only the customer-authored
    # content; otherwise every element's random ``id`` and server
    # ``_rid``/``_ts``/``_etag`` would read as a false divergence.
    if isinstance(b, list):
        return [_filtered_body(item, ignored) for item in b]
    return b


# Boundary marker for the SDK's appended diagnostics JSON blob. The
# ``CosmosHttpResponseError`` formatter renders ``str(exc)`` as
#   "(<reason-phrase>) <server-error-text>, {"Summary":...}"
# where the trailing ``, {"Summary":...`` is a JSON-stringified dump
# of the client-side request-stats / diagnostics tree -- per-call AND
# per-backend by construction. core-python's call stack hits the
# document endpoint directly and produces ``"DirectCalls": {...}``;
# the rust path goes through one or more metadata-cache pre-flights
# and produces ``"DirectCalls": {...}, "GatewayCalls": {...}`` with
# different call counts each time. Comparing that tail across the two
# backends is comparing routing decisions, not error behaviour. The
# cross-backend contract is the canonical server-error text *before*
# this comma -- that's what a customer error handler reads, and that's
# what both backends agree on when the typed exception matches.
#
# ``_normalize_exception_message`` trims everything from this marker
# onward before running the per-request-noise scrubbers below. If the
# pattern isn't found (binding-side errors, transport failures, any
# exception that didn't go through the diagnostics formatter), the
# whole string is normalised as before.
_DIAGNOSTICS_BLOB_START = re.compile(r',\s*\{"Summary":')

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
    # ISO-8601 timestamps the driver embeds in diagnostics summaries.
    (re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?"), "<ts>"),
    # The service-generated replica identifier in a not-found Request URI.
    # Separate backend calls can legitimately reach different replicas.
    (re.compile(r"(?<=/replicas/)\d+(?=s\b)"), "<replica>"),
    # Collapse any whitespace run -- including embedded newlines from
    # the driver's multi-line diagnostics dump -- to a single space so
    # platform line-endings don't matter.
    (re.compile(r"\s+"), " "),
]


def _normalize_exception_message(exc: BaseException) -> str:
    """Strip per-request noise out of an exception's text for diffing.

    Two-stage normalisation:

    1. If the message carries the SDK's appended ``, {"Summary":...``
       diagnostics blob (the standard ``CosmosHttpResponseError``
       formatter does this on every typed error from the gateway),
       trim everything from that marker onward. The diagnostics blob
       is per-backend by construction -- core-python emits a
       ``DirectCalls`` summary, the rust path emits
       ``DirectCalls`` + ``GatewayCalls`` because of its metadata-
       cache pre-flights. Comparing it across backends is comparing
       internal routing, not error behaviour.

    2. Run the remaining text through the per-request-noise scrubbers
       (UUIDs, RIDs, timestamps, numeric counters, whitespace).

    The complete normalized message is compared. Rendering code may truncate
    display text, but comparison must not discard a semantic suffix.
    """
    if exc is None:
        return ""
    text = str(exc)
    # Strip the appended diagnostics blob before scrubbing so the
    # presence/shape of ``DirectCalls`` vs ``DirectCalls + GatewayCalls``
    # doesn't end up in the diff. Search-and-truncate is intentionally
    # done BEFORE the regex substitutions so the marker is matched
    # against the unscrubbed text (the base64-ish RID scrubber would
    # otherwise rewrite ``"Summary"`` to ``"<rid>"`` and break it).
    blob_match = _DIAGNOSTICS_BLOB_START.search(text)
    if blob_match:
        text = text[:blob_match.start()]
    for pattern, replacement in _EXCEPTION_MESSAGE_NOISE:
        text = pattern.sub(replacement, text)
    text = text.strip()
    return text


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
    else:
        # 2. Both succeeded — diff filtered body.
        cb = _filtered_body(core.return_value, ignored_body_fields)
        rb = _filtered_body(rust.return_value, ignored_body_fields)
        if cb != rb:
            diffs.append("return_value: core-python {!r} / rust {!r}".format(cb, rb))

    # Response headers are customer-visible on both success and error paths.
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
    # Wire-nondeterministic headers are excluded from BOTH the key-set
    # diff above (via ``_DEFAULT_IGNORED_HEADERS``) and this presence
    # loop. See ``_WIRE_NONDETERMINISTIC_HEADERS`` for the rationale.
    presence_check_headers = (
        _VALUE_VOLATILE_REQUIRED_HEADERS - _WIRE_NONDETERMINISTIC_HEADERS
    )
    for header in sorted(presence_check_headers):
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
    """Build a sync CosmosClient for the named backend against ACCOUNT_HOST/KEY."""
    return CosmosClient(
        os.environ[ENV_ENDPOINT],
        os.environ[ENV_KEY],
        _backend=backend_name,  # type: ignore[arg-type]
    )


def _observed_backend_name(client: Any) -> str:
    """Return the backend the constructed client will actually use."""
    connection = getattr(client, "client_connection", None)
    if connection is None:
        raise AssertionError("parity client has no client_connection")
    backend = getattr(connection, "_backend", None)
    if backend is None:
        return "core-python"
    name = getattr(backend, "name", None)
    if name != "rust":
        raise AssertionError(
            "parity client has an unexpected backend object: {!r}".format(name)
        )
    return name


def _assert_expected_backend(client: Any, expected: str) -> None:
    observed = _observed_backend_name(client)
    if observed != expected:
        raise AssertionError(
            "parity client factory requested {!r} but constructed {!r}".format(
                expected, observed
            )
        )


def _binding_operation_count() -> int:
    try:
        from azure.cosmos import _rust
        counter = getattr(_rust, "operation_count", None)
        if callable(counter):
            return int(counter())
    except (ImportError, TypeError, ValueError):
        pass
    raise AssertionError("Rust binding operation counter is unavailable")


def _rust_fallback_count() -> int:
    from azure.cosmos._backend.base import rust_compatibility_fallback_count
    from azure.cosmos._query_rust_routing import rust_query_fallback_count
    return rust_compatibility_fallback_count() + rust_query_fallback_count()


def run_target_operation(
    client: Any,
    call: Callable[[], Any],
    *,
    expect_rust: bool = True,
) -> Any:
    """Run one target call and prove whether that exact call entered Rust."""
    if _observed_backend_name(client) == "core-python":
        return call()
    before = _binding_operation_count()
    fallback_before = _rust_fallback_count()
    try:
        return call()
    finally:
        delta = _binding_operation_count() - before
        fallback_delta = _rust_fallback_count() - fallback_before
        if expect_rust:
            assert delta > 0, "target operation did not enter the Rust binding"
            assert fallback_delta == 0, "target operation fell back to core-python"
        else:
            assert delta == 0, "target operation unexpectedly entered the Rust binding"
            assert fallback_delta == 0, "target fallback unexpectedly attempted Rust first"


async def run_target_operation_async(
    client: Any,
    call: Callable[[], Any],
    *,
    expect_rust: bool = True,
) -> Any:
    """Async twin of :func:`run_target_operation`."""
    if _observed_backend_name(client) == "core-python":
        return await call()
    before = _binding_operation_count()
    fallback_before = _rust_fallback_count()
    try:
        return await call()
    finally:
        delta = _binding_operation_count() - before
        fallback_delta = _rust_fallback_count() - fallback_before
        if expect_rust:
            assert delta > 0, "target operation did not enter the Rust binding"
            assert fallback_delta == 0, "target operation fell back to core-python"
        else:
            assert delta == 0, "target operation unexpectedly entered the Rust binding"
            assert fallback_delta == 0, "target fallback unexpectedly attempted Rust first"


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
        client = client_factory(backend_name)
        _assert_expected_backend(client, backend_name)
        try:
            outcome.return_value = call_fn(client)
            outcome.response_headers = dict(
                client.client_connection.last_response_headers or {}
            )
        except Exception as exc:  # pylint: disable=broad-except
            outcome.raised = exc
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


async def run_on_both_backends_async(
    call_fn: Callable[[Any], Any],
    *,
    description: str = "",
    request_body: Any = None,
    request_kwargs: Optional[Dict[str, Any]] = None,
) -> BackendComparison:
    """Async twin of :func:`run_on_both_backends`.

    Builds an ``azure.cosmos.aio`` client per backend, ``await``s
    ``call_fn(client)``, captures return value / headers / exception, and
    diffs the two with the same :func:`diff_outcomes`. ``call_fn`` is an
    async callable receiving the aio client.
    """
    outcomes: Dict[str, CallOutcome] = {}
    for backend_name in ("core-python", "rust"):
        outcome = CallOutcome(backend=backend_name)
        # ``async with`` so the aio client (and its HTTP session) is always
        # fully closed, even when call_fn raises -- otherwise the session is
        # left for the garbage collector and shows up as an unclosed-session
        # warning attributed to the test.
        async with AioCosmosClient(os.environ[ENV_ENDPOINT], os.environ[ENV_KEY],
                                   _backend=backend_name) as client:  # type: ignore[arg-type]
            _assert_expected_backend(client, backend_name)
            try:
                outcome.return_value = await call_fn(client)
            except Exception as exc:  # pylint: disable=broad-except
                outcome.raised = exc
            try:
                outcome.response_headers = dict(client.client_connection.last_response_headers or {})
            except Exception:  # pylint: disable=broad-except
                pass
        # Let aiohttp finish closing the connector's TLS transports before the
        # next client opens, so a late close can't surface as an unclosed-session
        # warning against an unrelated test.
        await asyncio.sleep(0.25)
        outcomes[backend_name] = outcome
    comparison = BackendComparison(
        core_python=outcomes["core-python"], rust=outcomes["rust"],
        call_description=description, request_body=request_body, request_kwargs=request_kwargs,
    )
    comparison.diffs = diff_outcomes(comparison.core_python, comparison.rust)
    return comparison
