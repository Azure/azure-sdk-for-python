from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from typing import Optional

BASE_VERSION = "1.0.0"


def _from_buildinfo() -> tuple[Optional[str], Optional[str]]:
    try:
        from . import _buildinfo  # type: ignore import-not-found
    except Exception:  # pragma: no cover - best effort fallback
        return None, None

    commit = getattr(_buildinfo, "commit", None)
    build_time = getattr(_buildinfo, "build_time", None)
    return commit or None, build_time or None


def _git_output(args: list[str]) -> Optional[str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:  # pragma: no cover - git may be unavailable
        return None

    output = completed.stdout.strip()
    return output or None


def _coerce_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None

    try:
        # Accept ISO formatted timestamps with or without trailing Z
        if date_str.endswith("Z"):
            date_str = date_str[:-1] + "+00:00"
        dt = datetime.fromisoformat(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None

    return dt.strftime("%y%m%d")


def _git_commit() -> Optional[str]:
    return _git_output(["rev-parse", "--short=7", "HEAD"])


def _current_date_code() -> str:
    return datetime.now(timezone.utc).strftime("%y%m%d")


def _format_version(base: str, commit: Optional[str], date: Optional[str]) -> str:
    suffix_parts: list[str] = []

    if commit:
        suffix_parts.append(f"g{commit[:7]}")

    if date:
        suffix_parts.append(f"d{date}")

    if suffix_parts:
        return f"{base}+{'.'.join(suffix_parts)}"

    return base


def _resolve_version() -> str:
    build_commit, build_time = _from_buildinfo()
    git_commit = _git_commit()
    commit = git_commit or build_commit

    date = _coerce_date(build_time)
    if date is None:
        date = _current_date_code()

    return _format_version(BASE_VERSION, commit, date)


VERSION = _resolve_version()

__all__ = ["VERSION"]
