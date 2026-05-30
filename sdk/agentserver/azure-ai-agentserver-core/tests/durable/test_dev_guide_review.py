# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Developer-guide review meta-test (Spec 015 FR-024 / FR-025).

This test guards the consolidated end-user-developer guide at
``azure-ai-agentserver-core/docs/durable-task-guide.md``. It is the
quality gate that prevents the guide from silently drifting from the
public API surface or from accumulating stale, contradictory, or
ambiguous content.

The checks (per FR-024) — each is a separate top-level test for clear
diagnostics:

1. **Symbol coverage** — every name in ``durable/__init__.py.__all__``
   MUST be referenced by the consolidated guide.
2. **Removed-name absence** — names retired by Phase 3 (``run_attempt``,
   ``lease_generation``, ``previous_input``, ``store_input``,
   ``TaskSuspended``, ``max_pending``, ``_framework.``,
   ``_FilteredMetadata``, ``lease_duration_seconds``) MUST NOT appear.
3. **Required sections** — the 8-section learning arc (Why → Mental model →
   Hello world → Concepts → Reference → Patterns → Operational/testing →
   What this is NOT) MUST be present, in order.
4. **Cross-guide canonical statements** — a small JSON file of "canonical
   sentences" (load-bearing statements that the responses-side
   ``handler-implementation-guide.md`` and the
   ``durability-contract.md`` glossary both rely on) MUST appear
   verbatim in the consolidated guide.
5. **Internal-contradiction detection** — the guide MUST NOT pair an
   "always X" claim with a paragraph that says "never X" (small
   invariants list). This is a heuristic check.
6. **PR-blocking failure mode (FR-025)** — when a new public symbol is
   added to ``__all__`` without a corresponding doc entry, the
   relevant test (symbol coverage) MUST exit non-zero. This is verified
   by ``test_pr_blocking_failure_mode_for_undocumented_symbol`` which
   injects a synthetic symbol and asserts the coverage check raises.

Per FR-030, this file is committed RED at Phase 7 and turns GREEN once
the consolidated guide ships.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Iterable

import pytest

# --------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------- #

_DURABLE_TESTS_DIR = Path(__file__).parent
_PACKAGE_ROOT = _DURABLE_TESTS_DIR.parent.parent
_DURABLE_INIT = (
    _PACKAGE_ROOT
    / "azure"
    / "ai"
    / "agentserver"
    / "core"
    / "durable"
    / "__init__.py"
)
_CONSOLIDATED_GUIDE = _PACKAGE_ROOT / "docs" / "durable-task-guide.md"

# --------------------------------------------------------------------- #
# Loaders
# --------------------------------------------------------------------- #


def _load_all_from_init() -> frozenset[str]:
    """Parse ``__all__`` from ``durable/__init__.py`` without importing it."""

    tree = ast.parse(_DURABLE_INIT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                        return frozenset(
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant)
                            and isinstance(elt.value, str)
                        )
    return frozenset()


def _load_guide_text() -> str:
    if not _CONSOLIDATED_GUIDE.exists():
        pytest.fail(
            f"Consolidated developer guide not found at {_CONSOLIDATED_GUIDE}. "
            "Per FR-023, Phase 7 MUST consolidate the two existing guides into a "
            "single end-user-developer document at this path."
        )
    return _CONSOLIDATED_GUIDE.read_text(encoding="utf-8")


# --------------------------------------------------------------------- #
# 1. Symbol coverage
# --------------------------------------------------------------------- #


def _undocumented_symbols(symbols: Iterable[str], guide: str) -> list[str]:
    """Return public symbols not referenced anywhere in the guide.

    The coverage rule is intentionally loose: a bare symbol name in code
    fences, prose, or headings all count. We just need evidence the
    developer reading the guide could *find* the symbol.
    """

    missing: list[str] = []
    for name in symbols:
        pattern = r"\b" + re.escape(name) + r"\b"
        if not re.search(pattern, guide):
            missing.append(name)
    return sorted(missing)


def test_every_public_symbol_is_referenced_in_guide() -> None:
    """FR-024 (1): every name in ``__all__`` MUST appear in the guide."""

    symbols = _load_all_from_init()
    guide = _load_guide_text()
    missing = _undocumented_symbols(symbols, guide)
    assert not missing, (
        f"{len(missing)} public symbol(s) from durable/__init__.py.__all__ are "
        f"not referenced in {_CONSOLIDATED_GUIDE.name}: {missing}. "
        "Either add them to the guide or remove them from __all__ (consult "
        "spec 015 FR-006/FR-007 first)."
    )


def test_pr_blocking_failure_mode_for_undocumented_symbol() -> None:
    """FR-025: the coverage check MUST bite when a new symbol is undocumented.

    Inject a synthetic symbol that the guide cannot possibly contain
    and assert the coverage detector flags it. This proves the gate is
    actually exercised (the suite is allowed to be PR-blocking by being
    PR-blocking only when the failure mode is wired correctly).
    """

    real_symbols = _load_all_from_init()
    guide = _load_guide_text()
    synthetic = "__SyntheticUndocumentedSymbol_xZyA__"
    missing = _undocumented_symbols(real_symbols | {synthetic}, guide)
    assert synthetic in missing, (
        "Coverage check did not flag the injected synthetic symbol — the "
        "PR-blocking failure mode is not wired. FR-025 requires "
        "test_every_public_symbol_is_referenced_in_guide to fail when a new "
        "public symbol exists in __all__ without a doc entry."
    )


# --------------------------------------------------------------------- #
# 2. Removed-name absence
# --------------------------------------------------------------------- #

_REMOVED_NAMES: tuple[str, ...] = (
    # Phase-3 / Phase-4 renames (old names)
    "run_attempt",
    "lease_generation",
    # Phase-3 drops
    "previous_input",
    "store_input",
    "TaskSuspended",
    "lease_duration_seconds",
    "max_pending",
    # Phase-5 namespace cleanup
    "_framework.",
    "_framework[",
    # Responses-layer helper deleted in Phase 6
    "_FilteredMetadata",
    # Phase 11 closeout — internal abstractions that leaked into the
    # end-user-developer guide and must stay out of the guide body
    # (per user feedback 2026-05-30: developers don't deal with etags,
    # provider classes, env vars, or the SDK's own test harness).
    "LocalFileTaskProvider",
    "AGENTSERVER_DURABLE_TASKS_PATH",
    "_crash_harness",
    "EtagConflict",
)


def _strip_rename_map(guide: str) -> str:
    """Return the guide text with the rename-map appendix removed.

    FR-007 explicitly requires a rename map appendix that mentions the
    old names. That appendix is the *only* place those names are
    allowed to appear, so we exclude it before scanning for retired-name
    occurrences. Match is heuristic: any H2 whose title contains
    "rename map" (case-insensitive) starts the excluded region;
    excluded region runs to end-of-document (the appendix is expected
    to be the final section).
    """

    import re as _re

    m = _re.search(r"^##\s+.*rename map.*$", guide, flags=_re.IGNORECASE | _re.MULTILINE)
    if m is None:
        return guide
    return guide[: m.start()]


def test_removed_names_absent_from_guide() -> None:
    """FR-024 (2): no retired names appear in the guide outside the rename map."""

    guide = _strip_rename_map(_load_guide_text())
    offenders: list[tuple[str, int]] = []
    for name in _REMOVED_NAMES:
        # Use literal substring search — these strings should never appear,
        # regardless of context (prose, code fence, comment), outside the
        # FR-007 rename-map appendix.
        count = guide.count(name)
        if count:
            offenders.append((name, count))
    assert not offenders, (
        f"Retired name(s) still present in {_CONSOLIDATED_GUIDE.name} "
        f"outside the rename map appendix: {offenders}. Phase 3-6 of "
        "spec 015 deleted these — remove them from the guide body (the "
        "rename map appendix is the only allowed mention)."
    )


# --------------------------------------------------------------------- #
# 3. Required sections (8-section learning arc)
# --------------------------------------------------------------------- #

# Top-level headings expected, in this exact order. Match is by canonical
# keyword(s) so wording flex is permitted around the canonical noun(s).
_REQUIRED_SECTIONS: tuple[tuple[str, str], ...] = (
    ("why", r"^##\s+(?:1\.\s+)?Why\b"),
    ("mental_model", r"^##\s+(?:2\.\s+)?Mental Model\b"),
    ("hello_world", r"^##\s+(?:3\.\s+)?Hello\b"),
    ("concepts", r"^##\s+(?:4\.\s+)?Concepts\b"),
    ("reference", r"^##\s+(?:5\.\s+)?Reference\b"),
    ("patterns", r"^##\s+(?:6\.\s+)?Patterns\b"),
    ("operational", r"^##\s+(?:7\.\s+)?Operational\b"),
    ("what_not", r"^##\s+(?:8\.\s+)?What This Is NOT\b"),
)


def test_required_sections_present_in_order() -> None:
    """FR-024 (3): 8 sections of the learning arc appear in order."""

    guide = _load_guide_text()
    positions: list[tuple[str, int]] = []
    for key, pattern in _REQUIRED_SECTIONS:
        m = re.search(pattern, guide, flags=re.MULTILINE | re.IGNORECASE)
        assert m, (
            f"Required section '{key}' not found in {_CONSOLIDATED_GUIDE.name}. "
            f"Expected an H2 heading matching {pattern!r}."
        )
        positions.append((key, m.start()))
    sorted_positions = sorted(positions, key=lambda p: p[1])
    assert positions == sorted_positions, (
        "Required sections appear out of order in the guide. "
        f"Expected order: {[k for k, _ in _REQUIRED_SECTIONS]}; "
        f"actual order: {[k for k, _ in sorted_positions]}."
    )


# --------------------------------------------------------------------- #
# 4. Cross-guide canonical statements
# --------------------------------------------------------------------- #

# Statements that the responses-side handler-implementation-guide.md
# and the durability-contract.md glossary depend on. Drift in these
# statements would silently break the cross-document mental model.
_CANONICAL_STATEMENTS: tuple[str, ...] = (
    # retry semantics
    "retry_attempt",
    "crash recovery does NOT consume",
    # metadata facility
    "callable namespace facade",
    # _* convention
    "reserved",
    # explicit flush
    "flush()",
)


def test_canonical_statements_present() -> None:
    """FR-024 (4): cross-guide canonical statements appear in the guide."""

    guide = _load_guide_text()
    missing = [s for s in _CANONICAL_STATEMENTS if s not in guide]
    assert not missing, (
        f"Canonical statements missing from {_CONSOLIDATED_GUIDE.name}: "
        f"{missing}. These statements are also referenced by "
        "azure-ai-agentserver-responses/docs/handler-implementation-guide.md "
        "and specs/durability-contract.md — keeping them in sync prevents "
        "split-brain documentation drift."
    )


# --------------------------------------------------------------------- #
# 5. Internal-contradiction detection (heuristic)
# --------------------------------------------------------------------- #

# Pairs of (claim, counter-claim) that MUST NOT both appear. Each pair
# represents a known historic ambiguity that the consolidation deletes.
_INVARIANT_PAIRS: tuple[tuple[str, str], ...] = (
    # auto-flush is gone; if the guide still says "auto-flush" it
    # contradicts the new explicit-flush model.
    ("auto-flush", "explicit flush"),
    # retry counter is durable; can't say "per-process retry"
    ("per-process retry", "cross-lifetime"),
)


def test_no_internal_contradictions() -> None:
    """FR-024 (5): heuristic check for paired claim/counter-claim."""

    guide_lower = _load_guide_text().lower()
    contradictions: list[tuple[str, str]] = []
    for claim, counter in _INVARIANT_PAIRS:
        if claim.lower() in guide_lower and counter.lower() in guide_lower:
            contradictions.append((claim, counter))
    assert not contradictions, (
        f"Internal contradictions detected in {_CONSOLIDATED_GUIDE.name}: "
        f"{contradictions}. Each pair represents a removed concept paired "
        "with its replacement — pick one. Update the invariants list in "
        "test_dev_guide_review.py if a new pair becomes legitimate."
    )


# --------------------------------------------------------------------- #
# 6. Pre-consolidation regression sub-test (T058)
# --------------------------------------------------------------------- #


def test_pre_consolidation_state_would_have_failed() -> None:
    """T058 (FR-024 regression): the meta-test MUST bite on bad input.

    Run the most load-bearing check (symbol coverage + removed-name
    absence + required sections) against a synthetic "pre-consolidation"
    string that approximates the old two-file state, and assert each
    layer of the check flags the problem.
    """

    # A short synthetic "guide" that fails in multiple categories at
    # once. It is intentionally NOT the real pre-consolidation text;
    # the goal is to prove the checks bite when they should.
    bad = (
        "# Old durable-task overview\n\n"
        "## What We're Solving\n\n"
        "Use `run_attempt` to detect retries. Set `store_input=True`. "
        "Set `max_pending=10` for steerable mode. Keys with `_framework.` "
        "prefix are reserved. Catch `TaskSuspended` on suspend.\n"
    )

    # 1. removed-name check would flag at least one offender.
    offenders = [name for name in _REMOVED_NAMES if name in bad]
    assert offenders, (
        "Regression check broken: the synthetic bad guide does not contain "
        "any retired names; the removed-name detector would not have flagged "
        "the pre-consolidation state."
    )

    # 2. required-section check would fail (synthetic has none of the 8).
    for key, pattern in _REQUIRED_SECTIONS:
        m = re.search(pattern, bad, flags=re.MULTILINE | re.IGNORECASE)
        assert m is None, (
            f"Regression check broken: synthetic bad guide matched required "
            f"section '{key}' unexpectedly."
        )

    # 3. symbol coverage on a small subset would flag missing entries.
    sample_real_symbols = frozenset({"task", "TaskContext", "RetryPolicy"})
    missing = _undocumented_symbols(sample_real_symbols, bad)
    assert "task" in missing or "TaskContext" in missing or "RetryPolicy" in missing, (
        "Regression check broken: coverage detector did not flag a missing "
        "real symbol on the synthetic bad guide."
    )
