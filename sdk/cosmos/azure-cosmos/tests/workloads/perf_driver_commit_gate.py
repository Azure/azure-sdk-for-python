# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Shared check that every Rust result row names one known driver build.

Every headline number must be tied to ONE known azure-sdk-for-rust driver build.
A rust result set is trustworthy only if every rust row carries the same,
non-empty ``driver_commit``:

  * a MISSING commit means the build was never stamped (we cannot say which
    driver produced the number), and
  * MORE THAN ONE commit means the run mixed driver builds, so the comparison is
    not like-for-like.

Either case invalidates a cross-build comparison, so in strict mode (the default)
the gate FAILS -- the caller exits non-zero -- instead of only printing a warning
as the tools used to. core-python rows legitimately have no rust driver, so the
gate is scoped to rust rows only (``config_backend``/``runtime_backend`` contains
'rust'; 'AsyncRustBackend' matches).

"Missing" covers placeholders as well as blanks. ``perf_config`` stamps the
literal string ``"unknown"`` when it cannot read a git SHA, so treating that as a
real commit would let a completely unstamped run report "single rust driver build
across all rows (OK)" -- the exact claim the gate exists to refuse. Any value in
``UNSTAMPED_COMMIT_VALUES`` therefore counts as no commit at all.

Reading a historical run that predates driver stamping is still possible: pass
``--allow-missing-driver-commit`` (or set ``PERF_ALLOW_MISSING_DRIVER_COMMIT=1``) to
downgrade the gate back to a warning.
"""
import os

HEADER = "### Rust driver commit (azure-sdk-for-rust) ###"

# Values that name no build. ``perf_config._get_git_sha`` returns "unknown" when
# git is unavailable; the rest are the usual stand-ins for an absent field. All
# are compared case-insensitively after stripping.
UNSTAMPED_COMMIT_VALUES = frozenset({"", "unknown", "none", "null", "n/a", "na", "-"})


def is_rust(row):
    """True when a results row was produced by the Rust backend."""
    b = row.get("config_backend") or row.get("runtime_backend") or ""
    return "rust" in str(b).lower()


def _clean(v):
    return str(v).strip() if v is not None else ""


def is_stamped_commit(value):
    """True when ``value`` actually names a driver build.

    A blank field and a placeholder such as ``"unknown"`` mean the same thing --
    nobody recorded which driver produced the number -- so both are unstamped.
    """
    return _clean(value).lower() not in UNSTAMPED_COMMIT_VALUES


def collect(rows):
    """Return (sorted_commits, missing_count, rust_row_count) over rust rows."""
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

    ``commits`` is the sorted list of distinct non-empty rust driver commits,
    ``missing`` the count of rust rows with no commit, ``rust_rows`` the total
    rust-row count. Returns (ok, lines). In non-strict mode problems are reported
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
