# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Check consistency and presence of declared driver-commit labels on Rust rows.

Missing/placeholder labels and multiple distinct labels fail strict mode.
Rows are classified using their backend labels, not measured execution.
Non-placeholder strings are accepted without verifying a Git revision or
the extension's build provenance, so a passing gate is not build attestation.

--allow-missing-driver-commit or PERF_ALLOW_MISSING_DRIVER_COMMIT downgrades
label problems to warnings for historical or intentionally unstamped runs.
"""
import os

HEADER = "### Rust driver commit (azure-sdk-for-rust) ###"

# Values that name no build. ``perf_config._get_git_sha`` returns "unknown" when
# git is unavailable; the rest are the usual stand-ins for an absent field. All
# are compared case-insensitively after stripping.
UNSTAMPED_COMMIT_VALUES = frozenset({"", "unknown", "none", "null", "n/a", "na", "-"})


def is_rust(row):
    """Classify a row as Rust from its configured/runtime backend labels."""
    b = row.get("config_backend") or row.get("runtime_backend") or ""
    return "rust" in str(b).lower()


def _clean(v):
    return str(v).strip() if v is not None else ""


def is_stamped_commit(value):
    """Check that a value is nonblank and not a known placeholder.

    This does not verify that it names a commit or the loaded driver build.
    """
    return _clean(value).lower() not in UNSTAMPED_COMMIT_VALUES


def collect(rows):
    """Return (sorted_commits, missing_count, rust_row_count) over Rust rows."""
    commits, missing, n = set(), 0, 0
    for r in rows:
        if not is_rust(r):
            continue
        n += 1
        c = _clean(r.get("driver_commit"))
        if is_stamped_commit(c):
            commits.add(c)
        else:
            missing += 1
    return sorted(commits), missing, n


def decide(commits, missing, rust_rows, strict=True):
    """Pure decision + human-readable lines from pre-aggregated commit facts.

    ``commits`` is the sorted list of distinct non-empty Rust driver commits,
    ``missing`` the count of Rust rows with no commit, ``rust_rows`` the total
    Rust-row count. Returns (ok, lines). In non-strict mode problems are reported
    but ok stays True.
    """
    lines = [HEADER]
    if rust_rows == 0:
        lines.append("  no rust rows in this set -- no driver commit to check.")
        return True, lines
    ok = True
    if missing:
        lines.append(
            f"  {missing} rust row(s) carry NO driver_commit (absent or a placeholder "
            "such as 'unknown') -- the driver build is unknown. "
            "Stamp the build (PERF_DRIVER_COMMIT / rebuild) and re-run."
        )
        if strict:
            ok = False
    if len(commits) > 1:
        lines.append(
            f"  !! MIXED rust driver builds in one result set: {commits}. "
            "Re-run so every rust row shares a single build."
        )
        if strict:
            ok = False
    if len(commits) == 1 and not missing:
        lines.append(
            f"  commit {commits[0]} -- single rust driver build across all "
            f"{rust_rows} rust row(s) (OK)."
        )
    elif len(commits) == 1 and missing:
        lines.append(f"  present build {commits[0]}, but some rust rows are unstamped (above).")
    elif not commits:
        lines.append("  no driver_commit present on any rust row.")
    return ok, lines


def evaluate(rows, strict=True):
    """Convenience for tools that hold the raw rows: collect + decide."""
    commits, missing, n = collect(rows)
    return decide(commits, missing, n, strict=strict)


def add_cli_flag(ap):
    """Register the standard override flag on an argparse parser."""
    ap.add_argument(
        "--allow-missing-driver-commit",
        action="store_true",
        help="downgrade the rust driver-commit check from FAIL to a warning "
        "(use only to read historical runs that predate driver stamping).",
    )


def strict_from(args):
    """Strict unless the override flag or PERF_ALLOW_MISSING_DRIVER_COMMIT is set."""
    env = os.environ.get("PERF_ALLOW_MISSING_DRIVER_COMMIT", "").strip().lower()
    if env in ("1", "true", "yes"):
        return False
    return not getattr(args, "allow_missing_driver_commit", False)
