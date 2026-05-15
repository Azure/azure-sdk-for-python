# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Helpers for the create_item parity test suite.

A "test harness" here means a small wrapper that does the boilerplate
each parity test would otherwise repeat: build two ``CosmosClient``s
(one core-python, one rust), run the same call against each, capture
the return value + ``last_response_headers`` + raised exception, and
diff the two outcomes side-by-side. Each individual test then only
writes the *call shape* it cares about — the harness handles setup,
teardown, capture, and reporting.

This file implements:

  * ``run_on_both_backends(call_fn)`` — the harness. Returns a
    ``BackendComparison`` with the two outcomes and a list of diffs.
  * ``BackendComparison.print_report()`` — side-by-side dump of inputs
    and outputs (run pytest with ``-s`` to see it).
  * ``xfail_on_backend("rust", reason="...")`` — pytest marker that
    activates only when the parametrised backend matches.

What ``xfail_on_backend`` does (it's a two-way ratchet, easy to misread):

  * Gap exists today → test fails → marker absorbs the failure → pytest
    reports it as ``xfailed`` (yellow), suite stays GREEN. Quiet.
  * Gap closes (the underlying issue is fixed) → test now passes →
    because the marker uses ``strict=True``, pytest flips the result to
    ``XPASSED`` which COUNTS AS A FAILURE. Suite goes RED. This is the
    signal: "remove this marker, the gap closed."

So the marker is invisible while the gap is open and loud the moment
it closes. Pair every marker with a short ``reason="..."`` describing
what's broken so the report is self-explanatory.

The suite skips cleanly when no Cosmos account is configured. A real
parity run needs both the emulator (or a real account) **and** the
compiled ``azure.cosmos._rust`` binding present; either missing → skip,
not fail.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import pytest


# ---------------------------------------------------------------------------
# Environment gating
# ---------------------------------------------------------------------------

#: Standard env var the harness consults for the account endpoint.
ENV_ENDPOINT = "ACCOUNT_URI"
#: Standard env var the harness consults for the master key.
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
# xfail_on_backend marker
# ---------------------------------------------------------------------------

def xfail_on_backend(backend: str, *, reason: str):
    """Strict xfail that activates only for the named backend.

    Use one per known backend gap so the marker location is greppable
    by its ``reason`` string. ``strict=True`` makes the suite fail
    loudly the moment the gap closes (so the marker gets removed).

    The marker reads the parametrised ``backend`` argument the test
    receives from the harness fixture.
    """
    return pytest.mark.xfail_on_backend(backend=backend, reason=reason, strict=True)


# Pytest discovery hook — register the marker so pytest doesn't warn.
def register_xfail_on_backend_marker(config):
    config.addinivalue_line(
        "markers",
        "xfail_on_backend(backend, reason, strict): xfail test when "
        "the parametrised backend matches. Pair with 'C# pending' reason.",
    )


def apply_xfail_on_backend(item, backend: str):
    """Apply matching xfail_on_backend markers to a test item.

    Called from the autouse fixture below; exposed so other test files
    can opt in if they parametrise differently.
    """
    for mark in item.iter_markers(name="xfail_on_backend"):
        wanted = mark.kwargs.get("backend") or (mark.args[0] if mark.args else None)
        if wanted == backend:
            item.add_marker(
                pytest.mark.xfail(
                    reason=mark.kwargs.get("reason", ""),
                    strict=mark.kwargs.get("strict", True),
                )
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

    @property
    def is_parity(self) -> bool:
        return not self.diffs

    def assert_parity(self):
        # Always print the side-by-side report on failure so the diff
        # is visible without having to rerun with -s.
        if self.diffs:
            print(self.format_report())
        assert self.is_parity, "Backend parity diffs:\n  - " + "\n  - ".join(self.diffs)

    def format_report(self) -> str:
        """Return a side-by-side string dump of inputs + outputs."""
        lines: List[str] = []
        lines.append("=" * 78)
        lines.append("PARITY CALL: {}".format(self.call_description or "(unset)"))
        lines.append("=" * 78)
        for label, oc in (("CORE-PYTHON", self.core_python), ("RUST", self.rust)):
            lines.append("--- {} ---".format(label))
            if oc.succeeded:
                lines.append("  status:        OK")
                lines.append("  return_value:  {!r}".format(oc.return_value))
            else:
                lines.append("  status:        RAISED")
                lines.append("  exception:     {}".format(type(oc.raised).__name__))
                lines.append("  message:       {}".format(oc.raised))
                for attr in ("status_code", "sub_status"):
                    v = getattr(oc.raised, attr, None)
                    if v is not None:
                        lines.append("  {}: {!r}".format(attr, v))
            hdrs = oc.response_headers or {}
            interesting = {
                k: v for k, v in hdrs.items()
                if k.lower() not in _DEFAULT_IGNORED_HEADERS
            }
            lines.append("  headers ({} total, {} interesting):".format(
                len(hdrs), len(interesting)
            ))
            for k in sorted(interesting):
                lines.append("    {}: {}".format(k, interesting[k]))
        lines.append("--- DIFFS ---")
        if not self.diffs:
            lines.append("  (none — parity)")
        for d in self.diffs:
            lines.append("  - " + d)
        lines.append("=" * 78)
        return "\n".join(lines)

    def print_report(self):
        """Print the side-by-side report unconditionally. Use ``-s`` to see it."""
        print(self.format_report())


# Headers that legitimately differ per request even on the same backend
# (request charges, activity ids, dates). Excluded from header diffs by
# default; tests that care about them can pass their own ignore list.
_DEFAULT_IGNORED_HEADERS = frozenset({
    "x-ms-request-charge",
    "x-ms-activity-id",
    "x-ms-session-token",
    "x-ms-cosmos-llsn",
    "x-ms-session-token-rid",
    "etag",
    "_etag",
    "date",
    "lsn",
    "x-ms-current-write-quorum",
    "x-ms-current-replica-set-size",
    "x-ms-xp-role",
    "x-ms-global-committed-lsn",
    "x-ms-number-of-read-regions",
    "x-ms-transport-request-id",
    "x-ms-cosmos-physical-partition-id",
    "x-ms-serviceversion",
    "x-ms-gatewayversion",
    "x-ms-schemaversion",
    "x-ms-cosmos-quorum-acked-lsn",
    "x-ms-cosmos-item-llsn",
    "x-ms-cosmos-quorum-acked-llsn",
    "x-ms-cosmos-replica-side-cache-token",
    "server",
})

# Body fields the server fills in that legitimately differ between
# create calls (rid, self link, ts, etag) — excluded from return-value
# diffs by default.
_DEFAULT_IGNORED_BODY_FIELDS = frozenset({
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
        # Both raised — compare exception type + sub_status + message.
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
) -> BackendComparison:
    """Run ``call_fn(client)`` against both backends and diff the outcomes.

    ``call_fn`` is the customer-shaped piece — it receives a
    ``CosmosClient`` and returns whatever the call under test returns
    (typically a ``CosmosDict`` from ``container.create_item``). It
    must be deterministic given the same client (same body, same id,
    same kwargs) so the diff is meaningful.

    The harness records the return value, the
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
    )
    comparison.diffs = diff_outcomes(comparison.core_python, comparison.rust)
    return comparison

