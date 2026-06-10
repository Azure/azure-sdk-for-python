#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Legacy-folder parity reporter.

Reads two ``pytest -v`` transcripts -- one from the originals
(core-python column) and one from the ``tests/<op>/<surface>/legacy/``
copies (rust column) -- pairs them by ``(surface, class name, method
name)``, and emits the per-operation parity audit markdown.

Usage::

    python scripts/v5/build_legacy_parity_audit.py \\
        --op read_item \\
        --corepy docs/V5/_parity_runs/read_item_corepy_<ts>.txt \\
        --rust   docs/V5/_parity_runs/read_item_rust_<ts>.txt \\
        --out    docs/V5/V5_PARITY_AUDIT_read_item_LEGACY.md

The reporter does **no test execution** -- it only diffs the two
transcripts. The pairing model:

* The rust column comes from a separate pytest invocation against the
  ``legacy/`` folders, whose test classes hard-code ``_backend="rust"``
  in ``setUp``.
* The core-python column comes from a separate pytest invocation
  against the originals, which never pass ``_backend`` and therefore
  use the SDK default.

If the reporter cannot find a pair for a given test, the missing column
is reported as ``MISSING`` (e.g. async-only methods that have no sync
twin or vice versa). That row's verdict is ``UNPAIRED`` -- the human
reviewer decides whether the test should have a twin or is correctly
single-surface-only.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# The reporter renders the per-test PARITY CALL block using the same
# diff + verdict logic the in-process parity tests use at
# ``tests/common/_parity_helpers.py``. Importing from ``tests/`` is
# the standard pattern in this repo's docs scripts -- the path
# manipulation below puts the tests/ folder on sys.path so the
# ``from common import _parity_helpers`` below resolves.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_TESTS_DIR = os.path.join(_REPO_ROOT, "tests")
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

# Imported lazily inside the renderer so the reporter still runs when
# the test tree is missing or the helpers move; see
# ``_load_parity_helpers``.
_parity_helpers = None  # type: ignore[var-annotated]


def _load_parity_helpers():
    global _parity_helpers
    if _parity_helpers is None:
        from common import _parity_helpers as ph  # type: ignore[import-not-found]
        _parity_helpers = ph
    return _parity_helpers


# -----------------------------------------------------------------------------
# Transcript parsing
# -----------------------------------------------------------------------------

# Matches lines like:
#   tests/read_item/sync/legacy/test_headers.py::TestHeaders::test_xxx PASSED [ 20%]
#   tests/test_headers_async.py::TestHeadersAsync::test_xxx PASSED [ 80%]
#   tests/test_xxx.py::Cls::method FAILED
#   tests/test_xxx.py::Cls::method SKIPPED (reason)
#   tests/test_xxx.py::Cls::method ERROR
_RESULT_LINE = re.compile(
    r"^(?P<path>tests[/\\][^\s:]+\.py)::(?P<cls>[A-Za-z_][\w]*)::(?P<method>[A-Za-z_][\w\[\]\-_.]*)"
    r"\s+(?P<outcome>PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)"
    r"(?:\s+\((?P<reason>[^)]*)\))?",
)

# When the capture plugin is active, pytest's "<nodeid> <OUTCOME>"
# single-line shape gets split: pytest writes "<nodeid> " (note the
# trailing space), the plugin writes its capture block on the next
# lines, and pytest then writes the outcome word on a fresh line. The
# two-stage parser below handles that case: a "<nodeid> $" line on
# its own (capturing path/cls/method) followed any number of
# capture-block / blank lines later by a line consisting of just the
# outcome keyword. ``_PENDING_NODEID_LINE`` matches the first half;
# ``_BARE_OUTCOME_LINE`` matches the second.
_PENDING_NODEID_LINE = re.compile(
    r"^(?P<path>tests[/\\][^\s:]+\.py)::(?P<cls>[A-Za-z_][\w]*)::"
    r"(?P<method>[A-Za-z_][\w\[\]\-_.]*)\s*$",
)
_BARE_OUTCOME_LINE = re.compile(
    r"^(?P<outcome>PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)"
    r"(?:\s+\((?P<reason>[^)]*)\))?\s*$",
)


@dataclass
class TestResult:
    surface: str         # "sync" or "aio"
    file_key: str        # normalized file stem used for pairing
    class_name: str
    method_name: str
    outcome: str         # PASSED / FAILED / SKIPPED / ERROR / XFAIL / XPASS / MISSING
    raw_path: str        # the path pytest printed (for debugging)
    reason: str = ""     # skip reason if any


def _surface_of(path: str, method_name: str) -> str:
    """Decide whether this nodeid belongs to the sync or aio surface.

    Rules in order:
      1. If the path contains ``/aio/`` or ``\\aio\\``, it is aio (the
         legacy copies live under ``tests/<op>/aio/legacy/``).
      2. Otherwise, if the basename ends with ``_async.py`` (the
         original-source naming convention for async tests), it is aio.
      3. Otherwise, if the method name ends with ``_async``, it is aio
         (defensive — covers an async-suffixed method living in a file
         whose name does not carry the suffix).
      4. Otherwise it is sync.
    """
    norm = path.replace("\\", "/").lower()
    if "/aio/" in norm:
        return "aio"
    base = os.path.basename(norm)
    if base.endswith("_async.py"):
        return "aio"
    if method_name.endswith("_async"):
        return "aio"
    return "sync"


def _file_key_of(path: str) -> str:
    """Return a normalized file stem used to pair core/rust rows.

    The legacy aio copies intentionally drop the ``_async`` suffix from
    their file names (source ``test_x_async.py`` -> legacy
    ``tests/<op>/aio/legacy/test_x.py``). We normalize both shapes to
    the same key (``test_x``) so pairing remains stable while still
    disambiguating rows that share class+method names across different
    files.
    """
    base = os.path.basename(path.replace("\\", "/")).lower()
    if base.endswith(".py"):
        base = base[:-3]
    if base.endswith("_async"):
        base = base[: -len("_async")]
    return base


def _detect_encoding(path: str) -> str:
    """Detect the file's text encoding from its BOM.

    Tee-Object on Windows PowerShell 5.1 writes UTF-16 LE by default;
    redirected python stdout is UTF-8; bash here-docs are UTF-8. Handle
    all three plus UTF-16 BE and UTF-8-with-BOM so a contributor running
    pytest under any shell can hand the resulting transcript to the
    reporter without conversion.
    """
    with open(path, "rb") as fh:
        head = fh.read(4)
    if head.startswith(b"\xff\xfe"):
        return "utf-16-le"
    if head.startswith(b"\xfe\xff"):
        return "utf-16-be"
    if head.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    return "utf-8"


def parse_transcript(path: str) -> List[TestResult]:
    """Parse a pytest -v transcript into a list of ``TestResult``.

    Handles two visual formats:

    * **Combined**: ``<nodeid> PASSED [ 20%]`` on one line (pytest's
      default when no other output landed between the test start and
      its outcome).
    * **Split**: ``<nodeid>`` on one line, capture-block / other
      stdout in between, then a bare ``PASSED`` / ``FAILED`` /
      ``SKIPPED (...)`` on a later line. This is what happens when
      the parity-capture plugin emits a JSON block mid-test.

    The same test may appear more than once in a transcript (rare;
    can happen if pytest re-runs on failure). The last occurrence
    wins.
    """
    seen: "OrderedDict[Tuple[str, str, str, str], TestResult]" = OrderedDict()
    encoding = _detect_encoding(path)
    pending: Optional[Dict[str, str]] = None
    with open(path, "r", encoding=encoding, errors="replace") as fh:
        for raw_line in fh:
            line = raw_line.rstrip("\r\n")
            # 1. Combined nodeid+outcome line (no plugin output in
            #    between, or any other test that ran without a
            #    capture block).
            m = _RESULT_LINE.search(line)
            if m:
                surface = _surface_of(m.group("path"), m.group("method"))
                tr = TestResult(
                    surface=surface,
                    file_key=_file_key_of(m.group("path")),
                    class_name=m.group("cls"),
                    method_name=m.group("method"),
                    outcome=m.group("outcome"),
                    raw_path=m.group("path"),
                    reason=(m.group("reason") or "").strip(),
                )
                seen[(surface, tr.file_key, tr.class_name, tr.method_name)] = tr
                pending = None
                continue
            # 2. Pending nodeid (start of split form). Remember the
            #    nodeid; the matching bare-outcome line will land
            #    later.
            pm = _PENDING_NODEID_LINE.match(line)
            if pm:
                pending = {
                    "path": pm.group("path"),
                    "cls": pm.group("cls"),
                    "method": pm.group("method"),
                }
                continue
            # 3. Bare outcome line -- pair it with the most recent
            #    pending nodeid. If there's nothing pending we skip;
            #    that's a stray bare keyword (e.g. a captured echo).
            om = _BARE_OUTCOME_LINE.match(line)
            if om and pending is not None:
                surface = _surface_of(pending["path"], pending["method"])
                tr = TestResult(
                    surface=surface,
                    file_key=_file_key_of(pending["path"]),
                    class_name=pending["cls"],
                    method_name=pending["method"],
                    outcome=om.group("outcome"),
                    raw_path=pending["path"],
                    reason=(om.group("reason") or "").strip(),
                )
                seen[(surface, tr.file_key, tr.class_name, tr.method_name)] = tr
                pending = None
                continue
    return list(seen.values())


# -----------------------------------------------------------------------------
# Capture-block parsing
# -----------------------------------------------------------------------------
#
# The parity-capture pytest plugin
# (``tests/common/parity_capture_plugin.py``) emits a fenced JSON
# block per intercepted call. The block carries the per-test
# request/return/headers/exception payload the reporter needs to
# render the rich PARITY CALL section.
#
# Format (real sentinels carry a per-session 8-hex token so a stray
# ``===PARITY-CAPTURE-...===`` literal in test stdout cannot confuse
# the parser; see ``SENTINEL_REGEX`` below)::
#
#     ===PARITY-CAPTURE-a1b2c3d4-START===
#     {"nodeid": "...", "backend": "core-python", "surface": "sync",
#      "op": "read_item", "ordinal": 0, "status": "ok",
#      "plugin_version": "v2",
#      "request": {"args": [...], "kwargs": {...}},
#      "return_value": {...},
#      "response_headers": {...},
#      "exception": null}
#     ===PARITY-CAPTURE-a1b2c3d4-END===
#
# Multi-line whitespace is tolerated between the sentinels even
# though the plugin writes single-line JSON, so a future plugin
# revision (or a contributor hand-editing a transcript for a repro)
# can pretty-print without breaking the parser.

# Token is whatever ``secrets.token_hex(4)`` would produce -- 8 hex
# chars, lower-case. We match both lower and upper hex defensively
# in case a future plugin uses ``secrets.token_urlsafe``.
_SENTINEL_TOKEN_RE = r"[0-9A-Fa-f]{8}"
_CAPTURE_START_RE = re.compile(
    r"===PARITY-CAPTURE-(" + _SENTINEL_TOKEN_RE + r")-START==="
)
_CAPTURE_END_TEMPLATE = "===PARITY-CAPTURE-{token}-END==="
# Bridge constants for the V1 (token-less) format so old transcripts
# in ``docs/V5/_parity_runs/`` still parse. Drop these once every
# transcript on disk has been regenerated with the v2 plugin.
_CAPTURE_START_V1 = "===PARITY-CAPTURE-START==="
_CAPTURE_END_V1 = "===PARITY-CAPTURE-END==="


@dataclass
class CaptureBlock:
    """One observed SDK call as recorded by the capture plugin."""
    nodeid: str
    backend: str
    surface: str
    op: str
    ordinal: int
    status: str  # "ok" / "raised" / "capture-error"
    request_args: List[Any] = field(default_factory=list)
    request_kwargs: Dict[str, Any] = field(default_factory=dict)
    return_value: Any = None
    response_headers: Dict[str, str] = field(default_factory=dict)
    exception: Optional[Dict[str, Any]] = None
    # Human-readable one-liner -- the first non-empty line of the
    # test method's docstring as captured by the plugin. ``None``
    # when the method has no docstring (the reporter then falls back
    # to a humanised version of the method name for the scoreboard's
    # Description column).
    test_doc: Optional[str] = None
    # Plugin protocol version this block was emitted under. ``"v1"``
    # for legacy transcripts (the plugin didn't write the field);
    # ``"v2"`` and up for transcripts that include
    # ``plugin_version`` explicitly. Used by ``parse_captures`` to
    # warn when the two transcripts being diffed came from different
    # plugin versions.
    plugin_version: str = "v1"

    @property
    def class_name(self) -> str:
        # nodeid is "<path>::<class>::<method>"
        parts = self.nodeid.split("::")
        return parts[1] if len(parts) >= 3 else ""

    @property
    def method_name(self) -> str:
        parts = self.nodeid.split("::")
        return parts[2] if len(parts) >= 3 else parts[-1]


def _find_next_capture_block(text: str, pos: int) -> Optional[Tuple[int, int, int]]:
    """Locate the next capture block in ``text`` starting at ``pos``.

    Returns ``(payload_start, payload_end, advance_past)`` where
    ``advance_past`` is the offset to resume scanning from. The
    tokenised v2 sentinels are matched by regex; the legacy literal
    v1 sentinels are also accepted so old on-disk transcripts still
    parse. Returns ``None`` when no further block is found.
    """
    # v2: regex-matched, per-session 8-hex token.
    m = _CAPTURE_START_RE.search(text, pos)
    v2_start = m.start() if m else -1
    # v1: literal fallback.
    v1_start = text.find(_CAPTURE_START_V1, pos)
    if v2_start < 0 and v1_start < 0:
        return None
    # Pick whichever comes first.
    if v2_start >= 0 and (v1_start < 0 or v2_start < v1_start):
        token = m.group(1)  # type: ignore[union-attr]
        end_marker = _CAPTURE_END_TEMPLATE.format(token=token)
        end = text.find(end_marker, m.end())  # type: ignore[union-attr]
        if end < 0:
            return None
        return (m.end(), end, end + len(end_marker))  # type: ignore[union-attr]
    end = text.find(_CAPTURE_END_V1, v1_start + len(_CAPTURE_START_V1))
    if end < 0:
        return None
    return (v1_start + len(_CAPTURE_START_V1), end, end + len(_CAPTURE_END_V1))


def parse_captures(path: str) -> List[CaptureBlock]:
    """Extract every capture block from a pytest transcript.

    Tolerates BOM-prefixed UTF-16 (PowerShell Tee-Object default) and
    UTF-8. A malformed block (truncated, invalid JSON) is skipped
    with a warning to stderr -- the reporter prefers to surface
    partial data over crashing on one bad block.
    """
    captures: List[CaptureBlock] = []
    encoding = _detect_encoding(path)
    with open(path, "r", encoding=encoding, errors="replace") as fh:
        text = fh.read()
    pos = 0
    while True:
        found = _find_next_capture_block(text, pos)
        if found is None:
            break
        payload_start, payload_end, advance_past = found
        payload_text = text[payload_start:payload_end].strip()
        pos = advance_past
        # PowerShell Tee-Object may embed CRs; json.loads is fine
        # with them, but a stray non-JSON line (e.g. a pytest progress
        # marker that landed mid-block) would break parsing. Defensive
        # try/except keeps the rest of the run intact.
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as je:
            sys.stderr.write(
                f"WARNING: malformed capture block at offset {payload_start} in {path}: {je}\n"
            )
            continue
        try:
            cb = CaptureBlock(
                nodeid=payload["nodeid"],
                backend=payload.get("backend", "unknown"),
                surface=payload.get("surface", "sync"),
                op=payload.get("op", ""),
                ordinal=int(payload.get("ordinal", 0)),
                status=payload.get("status", "ok"),
                request_args=list((payload.get("request") or {}).get("args") or []),
                request_kwargs=dict((payload.get("request") or {}).get("kwargs") or {}),
                return_value=payload.get("return_value"),
                response_headers=dict(payload.get("response_headers") or {}),
                exception=payload.get("exception"),
                test_doc=payload.get("test_doc"),
                plugin_version=payload.get("plugin_version", "v1"),
            )
        except (KeyError, TypeError, ValueError) as ve:
            sys.stderr.write(
                f"WARNING: malformed capture payload at offset {payload_start} in {path}: {ve}\n"
            )
            continue
        captures.append(cb)
    return captures


def index_captures(blocks: List[CaptureBlock]) -> Dict[Tuple[str, str, str, str], List[CaptureBlock]]:
    """Group captures by ``(surface, file_key, class_name, method_name)``.

    Pairing cannot use full nodeid because legacy copies live at
    different paths. It also cannot key on class+method alone because
    different files can legitimately reuse those names. ``file_key``
    gives us stable pairing across original vs legacy while avoiding
    those collisions.
    """
    idx: Dict[Tuple[str, str, str, str], List[CaptureBlock]] = {}
    for cb in blocks:
        key = (cb.surface, _file_key_of(cb.nodeid.split("::", 1)[0]), cb.class_name, cb.method_name)
        idx.setdefault(key, []).append(cb)
    # Sort each list by ordinal so multi-call tests pair in order.
    for k in idx:
        idx[k].sort(key=lambda b: b.ordinal)
    return idx


# -----------------------------------------------------------------------------
# Capture → PARITY CALL block rendering
# -----------------------------------------------------------------------------
#
# The rendered block must match the shape that
# ``BackendComparison.format_report`` emits for the in-process parity
# tests, so a reader can flip between the two audit-doc styles
# without retraining. The five sections are:
#
#   REQUEST       — args + kwargs (identical inputs by construction)
#   CORE-PYTHON   — status / response body or exception / response headers
#   RUST          — same three things for the rust path
#   DIFFS         — output of diff_outcomes() from _parity_helpers.py
#   VERDICT       — one of FULL PARITY / FUNCTIONAL PARITY, REPORTING
#                   GAP / FUNCTIONAL DIVERGENCE / EXCEPTION DIVERGENCE
#                   (same vocabulary as BackendComparison._verdict)

def _format_value(v: Any, indent: int = 4) -> List[str]:
    try:
        body = json.dumps(v, indent=2, default=str)
    except (TypeError, ValueError):
        body = repr(v)
    pad = " " * indent
    return [pad + ln for ln in body.splitlines()]


def _build_call_outcome(cb: Optional[CaptureBlock], backend: str):
    """Construct a parity-helpers ``CallOutcome`` from a CaptureBlock.

    ``None`` capture → ``CallOutcome`` with the missing-capture
    marker so the diff helper still has something to work with.
    """
    ph = _load_parity_helpers()
    if cb is None:
        return ph.CallOutcome(backend=backend, raised=RuntimeError("no capture recorded"))
    if cb.status == "raised" and cb.exception:
        # Reconstruct an exception-shaped object that satisfies the
        # attribute access diff_outcomes() does on ``status_code`` /
        # ``sub_status`` / ``type()``. The class is memoised by name
        # via ``_synthesise_exception_class`` so the same recorded
        # type name on both columns ends up as the same Python class
        # object -- without that memoisation,
        # ``type(core_oc.raised) is type(rust_oc.raised)`` returns
        # False even when both columns raised an identically-named
        # exception, and the verdict falsely says EXCEPTION DIVERGENCE.
        exc_type_name = cb.exception.get("type", "Exception")
        exc_cls = _synthesise_exception_class(exc_type_name)
        exc = exc_cls(cb.exception.get("message", ""))
        for attr in ("status_code", "sub_status"):
            v = cb.exception.get(attr)
            if v is not None:
                setattr(exc, attr, v)
        oc = ph.CallOutcome(
            backend=backend,
            response_headers=dict(cb.response_headers),
            raised=exc,
        )
        return oc
    return ph.CallOutcome(
        backend=backend,
        return_value=cb.return_value,
        response_headers=dict(cb.response_headers),
    )


# Module-level cache of synthesised exception classes keyed by the
# string type name recorded in the capture block. The reporter
# rebuilds an exception-shaped stand-in object for each captured
# ``status: "raised"`` payload so the shared diff helper has something
# to compare. Without a cache, the two stand-ins for the same recorded
# type name come from two separate ``type(name, (Exception,), {})``
# calls and Python treats them as different classes -- which makes
# ``diff_outcomes`` report "EXCEPTION DIVERGENCE" even for identical
# typed errors on both columns. With the cache, the same recorded
# name yields the same class object on every call, the ``is`` identity
# check passes, and the verdict reduces to FULL PARITY (or to the
# expected differences on message / status_code).
#
# KNOWN LIMITATION (Bug 4 of the principal-engineer review). The
# cache keys on ``__name__`` only -- not on a fully-qualified
# ``__module__.__name__`` -- because the capture-plugin payload only
# records the type name (see ``_serialise_exception`` in the
# plugin). If two genuinely-different exception classes ever happen
# to share the same simple name across modules (e.g. a hypothetical
# ``mypkg.A.MyError`` raised on one side and ``mypkg.B.MyError`` on
# the other), this cache would falsely merge them into one synthetic
# class and the verdict would under-report the divergence. Safe in
# practice today because every cosmos SDK exception name is unique
# within the SDK namespace; revisit if we ever ingest a third-party
# exception type whose name might clash.
_SYNTHESISED_EXCEPTION_CLASSES: Dict[str, type] = {}


def _synthesise_exception_class(name: str) -> type:
    cls = _SYNTHESISED_EXCEPTION_CLASSES.get(name)
    if cls is None:
        cls = type(name, (Exception,), {})
        _SYNTHESISED_EXCEPTION_CLASSES[name] = cls
    return cls


def _build_comparison(
    class_name: str,
    method_name: str,
    cp_cb: Optional[CaptureBlock],
    rs_cb: Optional[CaptureBlock],
):
    """Build the shared BackendComparison (DIFFS already computed).

    Centralised so the per-test PARITY CALL renderer and the
    scoreboard verdict resolver share one diff result per row.
    """
    ph = _load_parity_helpers()
    cp_oc = _build_call_outcome(cp_cb, "core-python")
    rs_oc = _build_call_outcome(rs_cb, "rust")
    seed = cp_cb or rs_cb
    request_kwargs = seed.request_kwargs if seed else {}
    request_args = seed.request_args if seed else []
    cmp = ph.BackendComparison(
        core_python=cp_oc,
        rust=rs_oc,
        call_description=f"{class_name}::{method_name}",
        request_body=request_args or None,
        request_kwargs=request_kwargs or None,
    )
    if cp_cb is not None and rs_cb is not None:
        cmp.diffs = ph.diff_outcomes(cp_oc, rs_oc)
    else:
        cmp.diffs = [
            "no capture on "
            + ("core-python" if cp_cb is None else "rust")
            + " -- cannot compute backend diff"
        ]
    return cmp


# Short single-line labels that the scoreboard column shows. These
# are the *first line* of the multi-line VERDICT string that the
# PARITY CALL block emits, so a reader looking at the scoreboard row
# and then jumping to the per-test block sees the same vocabulary
# top-to-bottom.
_FULL_PARITY_LABEL = "FULL PARITY"
_HEADER_GAP_LABEL = "FUNCTIONAL PARITY, HEADER GAP"
_FUNCTIONAL_DIVERGENCE_LABEL = "FUNCTIONAL DIVERGENCE"
_EXCEPTION_DIVERGENCE_LABEL = "EXCEPTION DIVERGENCE"


def _short_call_verdict(cmp_obj) -> str:
    """Collapse BackendComparison._verdict() to one of four labels.

    The full verdict text is multi-line for HEADER GAP rows (it
    enumerates every pushback bucket and the unrecorded gaps). The
    scoreboard only needs the headline, so we read the first line and
    snap to one of the four published categories.
    """
    full = cmp_obj._verdict()  # pylint: disable=protected-access
    head = full.splitlines()[0] if full else ""
    if head.startswith(_FULL_PARITY_LABEL):
        return _FULL_PARITY_LABEL
    if head.startswith(_HEADER_GAP_LABEL):
        return _HEADER_GAP_LABEL
    if head.startswith(_FUNCTIONAL_DIVERGENCE_LABEL):
        return _FUNCTIONAL_DIVERGENCE_LABEL
    if head.startswith(_EXCEPTION_DIVERGENCE_LABEL):
        return _EXCEPTION_DIVERGENCE_LABEL
    # Defensive: an unrecognised verdict string still gets surfaced
    # rather than silently dropped.
    return head or "UNKNOWN"


def render_parity_call_block(
    class_name: str,
    method_name: str,
    cp_cb: Optional[CaptureBlock],
    rs_cb: Optional[CaptureBlock],
) -> str:
    """Render one PARITY CALL block for a paired test.

    Mirrors ``BackendComparison.format_report``'s line-by-line shape
    so contributors who know the in-process parity audit can read this
    one without re-training. Reuses ``diff_outcomes`` and the
    verdict logic from ``tests/common/_parity_helpers.py`` so the
    DIFFS and VERDICT lines come from the same source of truth as
    the in-process parity tests.
    """
    cmp = _build_comparison(class_name, method_name, cp_cb, rs_cb)
    return cmp.format_report()


# -----------------------------------------------------------------------------
# Pairing + verdict
# -----------------------------------------------------------------------------

def pair_results(
    corepy: List[TestResult],
    rust: List[TestResult],
) -> List[Tuple[Optional[TestResult], Optional[TestResult]]]:
    """Pair core-python and rust results by ``(surface, class, method)``.

    Returns a list of ``(corepy_result, rust_result)`` tuples. Either
    element may be ``None`` if no pair was found. The list is ordered:
    paired entries first (in the order they appeared in the rust
    transcript -- the rust column is the "what we are migrating"
    column, so that ordering matches the contributor's mental model),
    then unpaired core-python entries, then unpaired rust entries.
    """
    corepy_idx: Dict[Tuple[str, str, str, str], TestResult] = {
        (r.surface, r.file_key, r.class_name, r.method_name): r for r in corepy
    }
    rust_idx: Dict[Tuple[str, str, str, str], TestResult] = {
        (r.surface, r.file_key, r.class_name, r.method_name): r for r in rust
    }
    pairs: List[Tuple[Optional[TestResult], Optional[TestResult]]] = []
    used_corepy_keys: set = set()
    for r in rust:
        key = (r.surface, r.file_key, r.class_name, r.method_name)
        cp = corepy_idx.get(key)
        if cp is not None:
            used_corepy_keys.add(key)
        pairs.append((cp, r))
    for cp in corepy:
        key = (cp.surface, cp.file_key, cp.class_name, cp.method_name)
        if key in used_corepy_keys:
            continue
        if key in rust_idx:
            continue  # already represented from the rust loop above
        pairs.append((cp, None))
    return pairs


def verdict_for(cp: Optional[TestResult], rs: Optional[TestResult]) -> str:
    """Apply the verdict grammar (UNPAIRED / MISSING / DIVERGED / PARITY)."""
    if cp is None and rs is None:
        return "UNPAIRED"
    if cp is None:
        return "UNPAIRED (rust only)"
    if rs is None:
        return "UNPAIRED (core-python only)"
    cp_o, rs_o = cp.outcome, rs.outcome
    if cp_o == "PASSED" and rs_o == "PASSED":
        return "FULL PARITY"
    if cp_o == "PASSED" and rs_o == "FAILED":
        return "RUST REGRESSION"
    if cp_o == "FAILED" and rs_o == "PASSED":
        return "RUST FIX"
    if cp_o == "FAILED" and rs_o == "FAILED":
        return "SHARED FAILURE"
    if cp_o == "SKIPPED" and rs_o == "SKIPPED":
        return "BOTH SKIPPED"
    if cp_o == "PASSED" and rs_o == "SKIPPED":
        return "RUST SKIP ONLY"
    if cp_o == "SKIPPED" and rs_o == "PASSED":
        return "CORE-PYTHON SKIP ONLY"
    return f"OTHER ({cp_o} vs {rs_o})"


_VERDICT_SORT_ORDER = {
    "RUST REGRESSION": 0,
    "SHARED FAILURE": 1,
    "OTHER": 2,
    "UNPAIRED (rust only)": 3,
    "UNPAIRED (core-python only)": 4,
    "UNPAIRED": 5,
    "RUST SKIP ONLY": 6,
    "CORE-PYTHON SKIP ONLY": 7,
    "BOTH SKIPPED": 8,
    "RUST FIX": 9,
    "FULL PARITY": 10,
}


def _sort_key(pair: Tuple[Optional[TestResult], Optional[TestResult]]) -> Tuple[int, int, str]:
    v = verdict_for(*pair)
    base = v.split(" (")[0]
    order = _VERDICT_SORT_ORDER.get(v, _VERDICT_SORT_ORDER.get(base, 99))
    # Secondary sort: sync before aio for readability.
    surface_order = 0 if (pair[1] or pair[0]).surface == "sync" else 1
    label = ((pair[1] or pair[0]).class_name + "." + (pair[1] or pair[0]).method_name)
    return (order, surface_order, label)


# -----------------------------------------------------------------------------
# Markdown emission
# -----------------------------------------------------------------------------

def _fmt_outcome(r: Optional[TestResult]) -> str:
    if r is None:
        return "MISSING"
    out = r.outcome
    if r.reason:
        return f"{out} ({r.reason})"
    return out


# Cheap one-liner builder for tests that didn't bother with a
# docstring. Strips the pytest ``test_`` prefix and the optional
# ``_async`` suffix, swaps underscores for spaces, and capitalises
# the first letter. So
#   test_container_read_item_throughput_bucket
#       -> "Container read item throughput bucket"
#   test_container_read_item_none_options_async
#       -> "Container read item none options"
# Not as good as a curated docstring, but better than dumping the
# raw method name into the Description column.
def _humanise_method_name(method_name: str) -> str:
    name = method_name
    if name.startswith("test_"):
        name = name[len("test_"):]
    if name.endswith("_async"):
        name = name[: -len("_async")]
    text = name.replace("_", " ").strip()
    if not text:
        return method_name
    return text[0].upper() + text[1:]


def _description_for(
    cp_blocks: List[CaptureBlock],
    rs_blocks: List[CaptureBlock],
    method_name: str,
) -> str:
    """Resolve the Description-column text for one scoreboard row.

    Preference order:
      1. ``test_doc`` recorded on the rust block (the legacy/ copy
         is the file we own, so its docstring is the canonical
         per-test description).
      2. ``test_doc`` recorded on the core-python block (the
         original file's docstring, if any).
      3. A humanised version of the method name (no-docstring
         fallback).
    """
    for block_list in (rs_blocks, cp_blocks):
        for b in block_list:
            doc = (b.test_doc or "").strip()
            if doc:
                return doc
    return _humanise_method_name(method_name)


def emit_markdown(
    op: str,
    pairs: List[Tuple[Optional[TestResult], Optional[TestResult]]],
    corepy_path: str,
    rust_path: str,
    account_host: str,
    scope_notes: str = "",
    corepy_captures: Optional[Dict[Tuple[str, str, str, str], List[CaptureBlock]]] = None,
    rust_captures: Optional[Dict[Tuple[str, str, str, str], List[CaptureBlock]]] = None,
) -> str:
    corepy_captures = corepy_captures or {}
    rust_captures = rust_captures or {}

    # Resolve the per-row scoreboard verdict once, up front, so
    # sorting and rendering share a single source of truth. The
    # verdict is derived from the actual capture-diff whenever both
    # columns recorded a call -- that's the only way a "FULL PARITY"
    # row really means "same body, same headers". When one or both
    # captures are missing (rare; only happens for tests that didn't
    # run with the plugin active, or for an unpaired test that only
    # exists on one column), we fall back to the pytest-outcome
    # verdict so the row still carries a useful label.
    def _row_verdict(cp: Optional[TestResult], rs: Optional[TestResult]) -> str:
        if cp is None or rs is None:
            return verdict_for(cp, rs)
        cp_key = (cp.surface, cp.file_key, cp.class_name, cp.method_name)
        rs_key = (rs.surface, rs.file_key, rs.class_name, rs.method_name)
        cp_blocks = corepy_captures.get(cp_key, [])
        rs_blocks = rust_captures.get(rs_key, [])
        if not cp_blocks or not rs_blocks:
            return verdict_for(cp, rs)
        # Use the first paired ordinal as the row's representative
        # verdict. Multi-call tests get one PARITY CALL block per
        # ordinal in the per-test section, but the scoreboard
        # condenses to a single label.
        cmp = _build_comparison(cp.class_name, cp.method_name, cp_blocks[0], rs_blocks[0])
        return _short_call_verdict(cmp)

    # Sort by the *new* verdict so worst-first ordering still works
    # with the capture-derived labels.
    def _row_sort_key(pair):
        cp, rs = pair
        v = _row_verdict(cp, rs)
        # Order: most actionable at the top.
        priority = {
            _FUNCTIONAL_DIVERGENCE_LABEL: 0,
            _EXCEPTION_DIVERGENCE_LABEL: 1,
            "RUST REGRESSION": 2,
            "SHARED FAILURE": 3,
            _HEADER_GAP_LABEL: 4,
            "RUST SKIP ONLY": 5,
            "CORE-PYTHON SKIP ONLY": 6,
            "BOTH SKIPPED": 7,
            "RUST FIX": 8,
            _FULL_PARITY_LABEL: 9,
        }
        base = v.split(" (")[0]
        order = priority.get(base, priority.get(v, 99))
        any_r = rs or cp
        surface_order = 0 if any_r.surface == "sync" else 1
        label = f"{any_r.class_name}.{any_r.method_name}"
        return (order, surface_order, label)

    pairs = sorted(pairs, key=_row_sort_key)

    lines: List[str] = []
    lines.append(f"# Parity audit — `{op}` (legacy-folder workflow)")
    lines.append("")
    lines.append(
        f"_Generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by "
        f"`scripts/v5/build_legacy_parity_audit.py`._"
    )
    lines.append("")
    lines.append("## What this report covers")
    lines.append("")
    lines.append(
        f"This audit checks the **`{op}`** operation. Every test below "
        f"was run twice against the live Azure Cosmos account at "
        f"**`{account_host}`** — once on the legacy core-python "
        f"backend and once on the new rust backend — and the two runs "
        f"were diffed call-by-call to see whether the rust path still "
        f"honours the contracts the v4 SDK already shipped."
    )
    lines.append("")
    lines.append("## How to read this report")
    lines.append("")
    lines.append(
        "Each row of the scoreboard below carries one of four verdicts. "
        "The scoreboard shows the headline; the per-test ``PARITY CALL`` "
        "block shows the full evidence (the inputs sent, the response "
        "body and headers each backend returned, and the normalised diff)."
    )
    lines.append("")
    lines.append("**Verdict categories**")
    lines.append("")
    lines.append(
        "* **FULL PARITY** -- the two backends returned the same response body "
        "and the same response headers. Nothing for the rust team to fix and "
        "nothing for the customer to notice."
    )
    lines.append(
        "* **FUNCTIONAL PARITY, HEADER GAP** -- the operation behaved the "
        "same on both backends (same body returned, or same exception raised) "
        "but the response-header surface differs. These are header-only "
        "regressions; the per-test block lists them grouped by the entry in "
        "``docs/V5/RUST_PARITY_PUSHBACKS.md`` that already tracks them, and "
        "flags any header that isn't tracked yet so the next reviewer can "
        "file a new pushback."
    )
    lines.append(
        "* **FUNCTIONAL DIVERGENCE** -- the operation behaved differently: "
        "the response bodies differ, or one backend succeeded while the "
        "other raised. This is a real customer-visible difference and the "
        "rust binding needs work before the operation can ship."
    )
    lines.append(
        "* **EXCEPTION DIVERGENCE** -- both backends raised, but with a "
        "different typed exception or status code. Same severity as "
        "FUNCTIONAL DIVERGENCE: customer error-handling code that switches "
        "on the exception type will behave differently on rust."
    )
    lines.append("")
    lines.append("**Fallback labels (only when a column has no captured call to diff)**")
    lines.append("")
    lines.append(
        "When the capture plugin was not active on one column, or a test on "
        "one side never reached the SDK entry point, the reporter falls back "
        "to a pytest-outcome label so the row is not silently dropped:"
    )
    lines.append("")
    lines.append(
        "* **RUST REGRESSION** -- PASSED on core-python, FAILED on rust. "
        "The contract that worked on legacy is broken on rust."
    )
    lines.append(
        "* **SHARED FAILURE** -- FAILED on both. Not a rust regression."
    )
    lines.append(
        "* **RUST FIX** -- FAILED on core-python, PASSED on rust. Legacy was "
        "broken; rust accidentally fixed it."
    )
    lines.append(
        "* **BOTH SKIPPED** / **RUST SKIP ONLY** / **CORE-PYTHON SKIP ONLY** -- "
        "structured ``@pytest.mark.skip`` on one or both columns."
    )
    lines.append(
        "* **UNPAIRED (rust only)** / **UNPAIRED (core-python only)** -- one "
        "side has no corresponding test (e.g. an async-only method without a "
        "sync twin, or vice versa)."
    )
    lines.append("")
    lines.append("**How response headers are bucketed before the diff**")
    lines.append("")
    lines.append(
        "* **Value-volatile required headers** -- headers Cosmos guarantees on "
        "every response but whose value legitimately changes every call "
        "(``x-ms-request-charge``, ``x-ms-activity-id``, ``etag``, the LSN "
        "family, ``date``, etc.). The diff enforces *presence* on both "
        "backends and skips the value comparison."
    )
    lines.append(
        "* **Wire-nondeterministic headers** -- the Cosmos gateway emits "
        "these unpredictably across calls (the same header appears on one "
        "response and is missing from the next, on the same backend). "
        "Today this is the quorum-acked family (``x-ms-quorum-acked-lsn``, "
        "``x-ms-quorum-acked-llsn``, ``x-ms-cosmos-quorum-acked-llsn``). "
        "Both presence and value are skipped on both sides; otherwise "
        "every audit row would flag a false-positive header gap that "
        "neither backend can fix."
    )
    lines.append(
        "* **Fully ignored headers** -- transport-layer noise that neither "
        "backend's customer surface promises (e.g. ``via``, ``strict-transport-"
        "security``). Skipped on both sides."
    )
    lines.append(
        "* **Everything else** -- both the *presence* and the *value* are "
        "enforced. A mismatch here lands in DIFFS as ``header <name>: "
        "core-python '...' / rust '...'`` and contributes to the verdict."
    )
    lines.append("")
    lines.append("## Scoreboard")
    lines.append("")
    lines.append("| # | Surface | Test (`class::method`) | Description | Verdict |")
    lines.append("|---|---|---|---|---|")
    for i, (cp, rs) in enumerate(pairs, start=1):
        any_r = rs or cp
        assert any_r is not None
        surface = any_r.surface
        label = f"`{any_r.class_name}::{any_r.method_name}`"
        key = (any_r.surface, any_r.file_key, any_r.class_name, any_r.method_name)
        description = _description_for(
            corepy_captures.get(key, []),
            rust_captures.get(key, []),
            any_r.method_name,
        )
        # Escape pipes so the markdown table doesn't get split if a
        # docstring happens to contain a literal "|".
        description_cell = description.replace("|", "\\|")
        verdict = _row_verdict(cp, rs)
        lines.append(
            f"| {i} | {surface} | {label} | {description_cell} | **{verdict}** |"
        )
    lines.append("")
    if scope_notes.strip():
        lines.append("## Scope decisions")
        lines.append("")
        lines.append(scope_notes.rstrip())
        lines.append("")

    n_capture_paired = sum(
        1 for cp, rs in pairs
        if cp is not None and rs is not None
        and (cp.surface, cp.file_key, cp.class_name, cp.method_name) in corepy_captures
        and (rs.surface, rs.file_key, rs.class_name, rs.method_name) in rust_captures
    )

    # -- Per-test PARITY CALL blocks ---------------------------------------
    lines.append("## Per-test PARITY CALL blocks")
    lines.append("")
    if n_capture_paired == 0:
        lines.append(
            "_No paired captures available. The capture plugin "
            "(``tests/common/parity_capture_plugin.py``) was not active "
            "on either column, or no observed call landed on both. "
            "Re-run with ``COSMOS_PARITY_CAPTURE_OP=" + op + "`` set on "
            "both pytest invocations (see ``How to reproduce`` below)._"
        )
        lines.append("")
    else:
        for cp, rs in pairs:
            any_r = rs or cp
            assert any_r is not None
            key = (any_r.surface, any_r.file_key, any_r.class_name, any_r.method_name)
            cp_blocks = corepy_captures.get(key, [])
            rs_blocks = rust_captures.get(key, [])
            if not cp_blocks and not rs_blocks:
                continue  # nothing to render for this row
            lines.append(f"### `{any_r.class_name}::{any_r.method_name}` ({any_r.surface})")
            lines.append("")
            # Pair captures position-for-position by ordinal (the
            # plugin emits ordinal=0 for the first capture in a test,
            # 1 for the second, etc). Most tests issue exactly one
            # call; multi-call tests get one PARITY CALL block per
            # paired ordinal.
            max_n = max(len(cp_blocks), len(rs_blocks))
            for i in range(max_n):
                cp_b = cp_blocks[i] if i < len(cp_blocks) else None
                rs_b = rs_blocks[i] if i < len(rs_blocks) else None
                if max_n > 1:
                    lines.append(f"#### Call #{i + 1}")
                    lines.append("")
                lines.append("```")
                lines.append(render_parity_call_block(
                    any_r.class_name, any_r.method_name, cp_b, rs_b,
                ))
                lines.append("```")
                lines.append("")

    # NOTE: A "How to reproduce" section used to land here, repeating
    # the three pytest + reporter commands. It was removed because
    # duplicating the reproducer in every per-op audit doc made the
    # doc longer without telling the reader anything new. The
    # reporter intentionally emits nothing for this slot now.
    return "\n".join(lines) + "\n"


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--op", required=True, help="Operation name, e.g. read_item")
    ap.add_argument("--corepy", required=True, help="Path to the core-python pytest -v transcript")
    ap.add_argument("--rust", required=True, help="Path to the rust pytest -v transcript")
    ap.add_argument("--out", required=True, help="Path to write the audit markdown")
    ap.add_argument(
        "--account-host",
        default=os.environ.get("ACCOUNT_HOST", "<ACCOUNT_HOST not captured>"),
        help="Live account host to record in the audit (defaults to $ACCOUNT_HOST)",
    )
    ap.add_argument(
        "--scope-notes",
        default=None,
        help=(
            "Optional path to a markdown fragment describing which "
            "candidate tests were considered and which were excluded "
            "from this operation's legacy folder, with the per-test "
            "rationale. Injected verbatim as a 'Scope decisions' "
            "section after the scoreboard."
        ),
    )
    args = ap.parse_args(argv)

    corepy = parse_transcript(args.corepy)
    rust = parse_transcript(args.rust)
    corepy_blocks = parse_captures(args.corepy)
    rust_blocks = parse_captures(args.rust)

    if not corepy:
        print(f"WARNING: no test result lines parsed from {args.corepy}", file=sys.stderr)
    if not rust:
        print(f"WARNING: no test result lines parsed from {args.rust}", file=sys.stderr)
    if not corepy_blocks:
        print(
            f"WARNING: no PARITY-CAPTURE blocks parsed from {args.corepy} "
            f"-- core-python column will render without per-call detail. "
            f"Re-run pytest with COSMOS_PARITY_CAPTURE_OP={args.op} set "
            f"and -s flag enabled.",
            file=sys.stderr,
        )
    if not rust_blocks:
        print(
            f"WARNING: no PARITY-CAPTURE blocks parsed from {args.rust} "
            f"-- rust column will render without per-call detail. Same fix.",
            file=sys.stderr,
        )

    # Plugin-version drift check. Both transcripts should come from
    # the same plugin protocol version; otherwise the JSON schema
    # may have shifted between the two runs and a silent diff can
    # produce misleading verdicts. Warn (don't fail) so a
    # mid-migration regeneration still produces a doc the human can
    # inspect, but make the mismatch loud.
    corepy_versions = {b.plugin_version for b in corepy_blocks if b.plugin_version}
    rust_versions = {b.plugin_version for b in rust_blocks if b.plugin_version}
    if corepy_versions and rust_versions and corepy_versions != rust_versions:
        print(
            f"WARNING: capture-plugin version mismatch between transcripts: "
            f"core-python={sorted(corepy_versions)} rust={sorted(rust_versions)}. "
            f"Re-run both columns with the same plugin version before trusting "
            f"this audit's verdicts.",
            file=sys.stderr,
        )

    scope_notes = ""
    if args.scope_notes:
        with open(args.scope_notes, "r", encoding=_detect_encoding(args.scope_notes)) as fh:
            scope_notes = fh.read()

    pairs = pair_results(corepy, rust)
    md = emit_markdown(
        op=args.op,
        pairs=pairs,
        corepy_path=args.corepy.replace("\\", "/"),
        rust_path=args.rust.replace("\\", "/"),
        account_host=args.account_host,
        scope_notes=scope_notes,
        corepy_captures=index_captures(corepy_blocks),
        rust_captures=index_captures(rust_blocks),
    )

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(md)

    print(f"Wrote {args.out}")
    print(f"  core-python results parsed: {len(corepy)}")
    print(f"  rust results parsed:        {len(rust)}")
    print(f"  core-python captures:       {len(corepy_blocks)}")
    print(f"  rust captures:              {len(rust_blocks)}")
    print(f"  paired:                     {sum(1 for p in pairs if p[0] and p[1])}")
    print(f"  unpaired:                   {sum(1 for p in pairs if not (p[0] and p[1]))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
