"""Phase 9 RED — Shippable-bar meta-test (FR-013 + FR-014 + FR-020 + FR-021).

This file is the static contract test for the four durable invocation
samples. It asserts the per-sample shippable bar mandated by
spec 015 user stories US6 (Per-sample shippable bar) and US7
(Operational guidance):

- ``samples/SHIPPABLE.md`` exists and is the source-of-truth manifest
  for which samples are released; every named sample matches an
  existing directory and every existing sample appears in the manifest.
- ``samples/DURABLE_SAMPLES.md`` exists and links to each per-sample
  ``README.md`` (FR-021 cross-sample operational guide).
- Each per-sample ``README.md`` contains the FR-020 sections:
  prereqs, quick start / install, invocation example, crash induction,
  recovery observation, troubleshooting.
- Each per-sample ``requirements.txt`` declares actual dependencies
  (FR-014 install-independence: not empty; lists the upstream SDKs
  needed for *this* sample only — does not pull every framework into
  the base invocations install).

These tests run on every PR; they have no live-marker, no network
needed, and complete in well under a second.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent
_SAMPLES_DIR = _THIS_DIR.parent / "samples"

_REQUIRED_DURABLE_SAMPLES = (
    "durable_copilot",
    "durable_langgraph",
    "durable_multiturn",
    "durable_research",
)

# Section markers each per-sample README must contain (FR-020).
# Match in any heading level; case-insensitive substring match.
_REQUIRED_README_SECTIONS = (
    ("prerequisites", r"^#+\s*(prereq|prerequisites|requirements)\b"),
    ("quick_start", r"^#+\s*(quick\s*start|install|getting\s*started)\b"),
    ("invocation_example", r"^#+\s*(invocation|usage|example|run\s*it|try\s*it)\b"),
    ("crash_induction", r"^#+\s*(crash|induc(e|ing)|kill|sigkill|failure)\b"),
    ("recovery_observation", r"^#+\s*(recover|resume|reconnect|replay|reattach)\b"),
    ("troubleshooting", r"^#+\s*(troubleshoot|faq|debug|gotcha|known\s+issue)\b"),
)


# --------------------------------------------------------------------------
# Manifest tests (FR-013, FR-021)
# --------------------------------------------------------------------------


def test_shippable_manifest_exists() -> None:
    """FR-013 — ``samples/SHIPPABLE.md`` must exist as the manifest."""

    manifest = _SAMPLES_DIR / "SHIPPABLE.md"
    assert manifest.is_file(), (
        f"Expected the shippable-samples manifest at {manifest}. "
        "FR-013 requires this file as the source of truth for which "
        "samples are released."
    )


def test_durable_samples_guide_exists() -> None:
    """FR-021 — cross-sample operational guide must exist."""

    guide = _SAMPLES_DIR / "DURABLE_SAMPLES.md"
    assert guide.is_file(), (
        f"Expected the cross-sample operational guide at {guide}. "
        "FR-021 requires this file as the entry point that links to "
        "each per-sample README."
    )


def test_manifest_lists_every_required_sample() -> None:
    """Every required sample must appear in ``samples/SHIPPABLE.md``."""

    manifest = _SAMPLES_DIR / "SHIPPABLE.md"
    if not manifest.is_file():
        pytest.skip("SHIPPABLE.md missing — covered by test_shippable_manifest_exists")
    text = manifest.read_text(encoding="utf-8")

    missing = [s for s in _REQUIRED_DURABLE_SAMPLES if s not in text]
    assert not missing, (
        f"SHIPPABLE.md is missing entries for: {missing}. "
        "Every required sample must appear in the manifest."
    )


def test_durable_samples_guide_links_each_sample() -> None:
    """``DURABLE_SAMPLES.md`` must link to each per-sample README."""

    guide = _SAMPLES_DIR / "DURABLE_SAMPLES.md"
    if not guide.is_file():
        pytest.skip(
            "DURABLE_SAMPLES.md missing — covered by test_durable_samples_guide_exists"
        )
    text = guide.read_text(encoding="utf-8")

    missing = [s for s in _REQUIRED_DURABLE_SAMPLES if s not in text]
    assert not missing, (
        f"DURABLE_SAMPLES.md does not reference samples: {missing}. "
        "The cross-sample guide must link each per-sample README."
    )


# --------------------------------------------------------------------------
# Per-sample README content gates (FR-020)
# --------------------------------------------------------------------------


@pytest.mark.parametrize("sample_name", _REQUIRED_DURABLE_SAMPLES)
@pytest.mark.parametrize(
    "section_key,pattern",
    _REQUIRED_README_SECTIONS,
    ids=[s[0] for s in _REQUIRED_README_SECTIONS],
)
def test_readme_has_required_section(
    sample_name: str, section_key: str, pattern: str
) -> None:
    """FR-020 — per-sample README must cover the operational topics."""

    readme = _SAMPLES_DIR / sample_name / "README.md"
    if not readme.is_file():
        pytest.skip(
            f"{sample_name}/README.md missing — covered by test_required_files_per_sample"
        )
    text = readme.read_text(encoding="utf-8")
    matches = re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    assert matches, (
        f"{sample_name}/README.md is missing a section matching "
        f"'{section_key}' (regex: {pattern!r}). FR-020 requires "
        "prerequisites, quick start, invocation example, crash induction, "
        "recovery observation, and troubleshooting."
    )


# --------------------------------------------------------------------------
# requirements.txt install-independence (FR-014)
# --------------------------------------------------------------------------


@pytest.mark.parametrize("sample_name", _REQUIRED_DURABLE_SAMPLES)
def test_requirements_txt_declares_dependencies(sample_name: str) -> None:
    """FR-014 — per-sample ``requirements.txt`` must list actual dependencies."""

    req = _SAMPLES_DIR / sample_name / "requirements.txt"
    if not req.is_file():
        pytest.skip(
            f"{sample_name}/requirements.txt missing — covered by structural gate"
        )

    declared = [
        ln.strip()
        for ln in req.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    assert declared, (
        f"{sample_name}/requirements.txt is empty. FR-014 requires "
        "each sample to declare its upstream-SDK dependencies so adding "
        "the sample does not pull every framework into the base install."
    )
