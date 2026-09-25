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
        """Assert that no differences remain after filtering header-diff categories.

        This ignores header values as well as header presence. It does not prove
        that ignored headers are unimportant or that service behavior is identical.
        Body exclusions and exception normalization also limit the comparison.
        The full report still includes the observed header differences.
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
        """Compare exception type, status, substatus, and normalized message.

        Also require no differences under diff_outcomes' default body/header
        exclusions. This is stricter than functional exception parity, but does
        not compare raw exception text or every response header value.
        """
        self._assert_exception_contract()
        exception_diffs = diff_outcomes(self.core_python, self.rust)
        assert not exception_diffs, (
            "Exception parity diffs:\n  - " + "\n  - ".join(exception_diffs)
        )

    def assert_functional_exception_parity(self):
        """Check the normalized exception contract while ignoring header-diff categories."""
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
        accepted_additions = _accepted_rust_header_additions(self.core_python, self.rust)
        if accepted_additions:
            lines.append("--- ACCEPTED vNext ADDITIONS (not gaps) ---")
            for name in sorted(accepted_additions):
                lines.append("  {}: SDK-generated Rust diagnostics; not a legacy service header.".format(name))
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
        26,
        "Original service response headers are discarded",
    )
    _HEADER_TO_PUSHBACK: ClassVar[Dict[str, Tuple[int, str]]] = {
        "date": _PUSHBACK_RAW_HEADERS,
        "server": _PUSHBACK_RAW_HEADERS,
        "content-type": _PUSHBACK_RAW_HEADERS,
        "content-length": _PUSHBACK_RAW_HEADERS,
        "content-location": _PUSHBACK_RAW_HEADERS,
        "cache-control": _PUSHBACK_RAW_HEADERS,
        "pragma": _PUSHBACK_RAW_HEADERS,
        "strict-transport-security": _PUSHBACK_RAW_HEADERS,
        "transfer-encoding": _PUSHBACK_RAW_HEADERS,
        "x-ms-cosmos-min-throughput": _PUSHBACK_RAW_HEADERS,
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
        if core_ok or all(self._is_header_diff(diff) for diff in self.diffs):
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
            outcome_description = (
                "both backends performed the operation successfully and returned response bodies "
                "that match under the comparison rules (which ignore "
                "id, _rid, _self, _ts, _etag, and _attachments). "
                if core_ok else
                "both backends raised equivalent exceptions under the comparison rules. "
            )
            out: List[str] = [
                "FUNCTIONAL PARITY, HEADER GAP: " + outcome_description +
                "Header differences are grouped by documented pushback below; "
                "unrecorded observations require triage and are not "
                "automatically Rust defects."
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
        return ("EXCEPTION DIVERGENCE: both backends raised, but the exception type, "
                "status, substatus, or normalized message differs.")


    def print_report(self):
        """Print the side-by-side report unconditionally. Use ``-s`` to see it."""
        print(self.format_report())


# Default comparison policy: ignore these values but report asymmetric presence
# on captured success and error responses. Absence from both sides passes.
# Membership does not establish that a service response must contain the header.
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
    # Compare presence, not the date or server string from separate calls.
    "date",
    "server",
    # Resource-accounting values are outside the default value comparison.
    "x-ms-resource-quota",
    "x-ms-resource-usage",
    # These specific LSN spellings receive presence-only comparison.
    "x-ms-cosmos-llsn",
    "x-ms-cosmos-item-llsn",
    "x-ms-item-lsn",
    # Compare topology/diagnostic header presence rather than values.
    "x-ms-documentdb-partitionkeyrangeid",
    "x-ms-cosmos-physical-partition-id",
    "x-ms-current-write-quorum",
    "x-ms-current-replica-set-size",
    "x-ms-xp-role",
    "x-ms-schemaversion",
    "x-ms-cosmos-internal-partition-id",
    "x-ms-last-state-change-utc",
})

# These header names are omitted from default key/value comparisons.
# Each exclusion can hide an observed difference and is a test policy choice.
_FULLY_IGNORED_HEADERS = frozenset({
    # Distinct from the HTTP "etag" spelling; ignored here if captured as a header.
    "_etag",
})

# Quorum headers excluded by default from key/value and presence-only checks.
# This policy does not attribute an observed omission to the service or binding.
# A custom ignored_headers set can reintroduce ordinary key/value comparisons.
_WIRE_NONDETERMINISTIC_HEADERS = frozenset({
    "x-ms-quorum-acked-lsn",
    "x-ms-quorum-acked-llsn",
    "x-ms-cosmos-quorum-acked-llsn",
})

# Combined set used to filter the value-diff. Tests that want a custom
# scope can pass their own frozenset to ``diff_outcomes(ignored_headers=...)``.
# The presence check below always runs against ``_VALUE_VOLATILE_REQUIRED_HEADERS``
# regardless of what's passed for ``ignored_headers``, but
# the presence loop explicitly skips ``_WIRE_NONDETERMINISTIC_HEADERS``.
_DEFAULT_IGNORED_HEADERS = (
    _VALUE_VOLATILE_REQUIRED_HEADERS
    | _FULLY_IGNORED_HEADERS
    | _WIRE_NONDETERMINISTIC_HEADERS
)

# Default body exclusions accommodate separately created resources and ids.
# Filtering removes top-level keys in dictionaries and recurses through lists,
# not through nested dictionary values. Ignoring id can conceal returned-id bugs.
# Request-preparation unit tests check outgoing bytes, not service round-tripping;
# that needs a separate end-to-end assertion against each requested id.
_DEFAULT_IGNORED_BODY_FIELDS = frozenset({
    "id",
    "_rid", "_self", "_ts", "_etag", "_attachments",
})


def _filtered_headers(h: Optional[Dict[str, str]],
                      ignored: frozenset) -> Dict[str, str]:
    """Return comparable response headers with ignored names removed."""
    if h is None:
        return {}
    return {k.lower(): v for k, v in h.items() if k.lower() not in ignored}


def _filtered_body(b: Any, ignored: frozenset) -> Any:
    """Remove service-generated fields from one result or result list."""
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


# Textual cutoff used by the comparison policy. Everything from this marker
# onward is discarded regardless of its origin or whether it contains differences.
_DIAGNOSTICS_BLOB_START = re.compile(r',\s*\{"Summary":')

# From a matching tail, keep only ResourceType and OperationType matches.
# This intentionally ignores all other tail content and repeated field occurrences.
_SERVICE_DIAGNOSTICS_TAIL_START = re.compile(r",\s*RequestStartTime:")
_SERVICE_DIAGNOSTICS_SEMANTIC_FIELDS = re.compile(
    r"\b(ResourceType|OperationType):\s*([A-Za-z]+)")

# Truncation/removal patterns for comparison; neither verifies provenance or
# that the removed text repeats information retained elsewhere.
_SERVICE_ERROR_BODY_ECHO = re.compile(r"\s+Code:\s+\w+\s+Message:\s")
_SERVICE_HOST_AGENT = re.compile(r",\s*\S+/\S+\s+cosmos-netstandard-sdk/\S+")

# Patterns used to scrub per-request noise out of exception messages
# before comparing them across backends. Each entry is (regex, replacement).
# Order matters only inasmuch as later substitutions see the output of
# earlier ones. The intent is "two backends raising semantically the
# same error produce the same normalised text" -- *not* byte-identity
# of the raw ``str(exc)``.
_EXCEPTION_MESSAGE_NOISE = [
    # Any UUID-shaped token, including customer text matching this pattern.
    (re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"), "<uuid>"),
    # ISO-8601 timestamps the driver embeds in diagnostics summaries.
    (re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?"), "<ts>"),
    # The service-generated replica identifier in a not-found Request URI.
    # Separate backend calls can legitimately reach different replicas.
    # The trailing letter says which kind answered -- ``p`` for the primary,
    # ``s`` for a secondary -- and that also varies per call, so both the
    # number and the letter have to be redacted or the comparison flakes
    # whenever the two backends happen to land on different replica kinds.
    (re.compile(r"(?<=/replicas/)\d+[ps]\b"), "<replica>"),
    # Collapse any whitespace run -- including embedded newlines from
    # the driver's multi-line diagnostics dump -- to a single space so
    # platform line-endings don't matter.
    (re.compile(r"\s+"), " "),
]


def _strip_service_error_decorations(text: str) -> str:
    """Cut text at the configured Code/Message marker and remove matching build labels.

    The helper does not verify that the discarded suffix duplicates the prefix.
    Differences confined to that suffix are outside this comparison.
    """
    echo = _SERVICE_ERROR_BODY_ECHO.search(text)
    if echo:
        text = text[:echo.start()]
    return _SERVICE_HOST_AGENT.sub("", text)


def _summarize_service_diagnostics_tail(text: str) -> str:
    """Keep the prefix and selected fields from a matching RequestStartTime tail.

    ResourceType and OperationType matches are deduplicated and sorted.
    All other tail text is discarded. Without the marker, return the input.
    """
    match = _SERVICE_DIAGNOSTICS_TAIL_START.search(text)
    if not match:
        return text
    head, tail = text[:match.start()], text[match.start():]
    fields = sorted({
        "{}: {}".format(name, value)
        for name, value in _SERVICE_DIAGNOSTICS_SEMANTIC_FIELDS.findall(tail)
    })
    if not fields:
        return head
    return "{} [{}]".format(head, ", ".join(fields))


def _normalize_exception_message(exc: BaseException) -> str:
    """Normalize exception text using this harness's comparison policy.

    Cut at a Summary marker; reduce a RequestStartTime tail to selected fields;
    strip Code/Message suffixes and matching build labels; then replace UUIDs,
    timestamps, replica identifiers, and whitespace with normalized forms.

    The entire resulting string is compared, but discarded text is not.
    These pattern-based rules can hide meaningful differences and do not
    establish semantic equivalence of arbitrary exceptions.
    """
    if exc is None:
        return ""
    text = str(exc)
    # Match the cutoff against the original text before applying other patterns.
    blob_match = _DIAGNOSTICS_BLOB_START.search(text)
    if blob_match:
        text = text[:blob_match.start()]
    # Keep only the selected fields from a matching RequestStartTime tail.
    text = _summarize_service_diagnostics_tail(text)
    # Apply the remaining truncation/removal patterns before noise substitutions.
    text = _strip_service_error_decorations(text)
    for pattern, replacement in _EXCEPTION_MESSAGE_NOISE:
        text = pattern.sub(replacement, text)
    text = text.strip()
    return text


def _accepted_rust_header_additions(core: CallOutcome, rust: CallOutcome) -> frozenset[str]:
    """Recognize only the explicitly accepted, nonempty Rust diagnostic addition.

    Keep it in captured headers and reports. Do not exempt a missing Rust header,
    an empty value, or any unrelated extra/missing service header.
    """
    name = "x-ms-cosmos-sdk-diagnostics"
    core_names = {key.lower() for key in (core.response_headers or {})}
    rust_headers = {key.lower(): value for key, value in (rust.response_headers or {}).items()}
    value = rust_headers.get(name)
    if name not in core_names and isinstance(value, str) and value.strip():
        return frozenset({name})
    return frozenset()


def diff_outcomes(
    core: CallOutcome,
    rust: CallOutcome,
    *,
    ignored_headers: frozenset = _DEFAULT_IGNORED_HEADERS,
    ignored_body_fields: frozenset = _DEFAULT_IGNORED_BODY_FIELDS,
) -> List[str]:
    """Return differences under the supplied filters and default normalization.

    An empty list means this comparison found no differences, not exhaustive
    SDK or service parity. Presence-only headers may be absent from both sides.
    Both successes and errors have their captured headers compared.
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
    for name in _accepted_rust_header_additions(core, rust):
        rh.pop(name, None)
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

    # Compare asymmetric presence using unfiltered captured headers, including
    # error outcomes. This policy runs independently of ignored_headers.
    core_names = {k.lower() for k in (core.response_headers or {})}
    rust_names = {k.lower() for k in (rust.response_headers or {})}
    # These exclusions always apply to this loop. A custom ignored_headers set
    # can still cause those names to participate in the ordinary diff above.
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
    backend = connection._backend
    name = getattr(backend, "name", None)
    if name not in ("core-python", "rust"):
        raise AssertionError(
            "parity client has an unexpected backend object: {!r}".format(name)
        )
    return name


def _assert_expected_backend(client: Any, expected: str) -> None:
    """Fail when a client uses a different backend than requested."""
    observed = _observed_backend_name(client)
    if observed != expected:
        raise AssertionError(
            "parity client factory requested {!r} but constructed {!r}".format(
                expected, observed
            )
        )


def _binding_operation_count() -> int:
    """Read the process-wide counter at instrumented Rust binding entry points."""
    try:
        from azure.cosmos import _rust
        counter = getattr(_rust, "_debug_operation_count", None)
        if callable(counter):
            return int(counter())
    except (ImportError, TypeError, ValueError):
        pass
    raise AssertionError("Rust binding operation counter is unavailable")


def _rust_fallback_count() -> int:
    """Return the number of Rust calls that continued through Python."""
    from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count
    return rust_compatibility_fallback_count()


def run_target_operation(
    client: Any,
    call: Callable[[], Any],
    *,
    expect_rust: bool = True,
) -> Any:
    """Run the closure and check process-wide binding/fallback counter deltas.

    A positive binding delta indicates instrumented entry during this window,
    not successful driver execution or a network request. Unrelated concurrent
    work can affect the counters; keep target-call checks isolated.
    """
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

    AssertionError propagates as a failed test check, never as a comparable
    operation error. Matching failed assertions must not establish parity.
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
        except AssertionError:
            raise
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
            except AssertionError:
                raise
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
