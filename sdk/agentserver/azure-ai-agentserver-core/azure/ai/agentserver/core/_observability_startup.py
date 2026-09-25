# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Observability startup mode and effective CPU detection."""

from __future__ import annotations

import logging
import os
import sys

_OBSERVABILITY_STARTUP_ENV = "AGENTSERVER_OBSERVABILITY_STARTUP"
_CPU_LIMIT_ENV = "AGENTSERVER_CPU_LIMIT"
_OBSERVABILITY_STARTUP_MODES = frozenset(("auto", "sync", "concurrent"))

logger = logging.getLogger("azure.ai.agentserver")


def is_free_threaded_runtime() -> bool:
    """Return whether this process can run Python threads without the GIL."""
    is_gil_enabled = getattr(sys, "_is_gil_enabled", None)
    if is_gil_enabled is None or is_gil_enabled():
        return False

    import sysconfig  # pylint: disable=import-outside-toplevel

    return sysconfig.get_config_var("Py_GIL_DISABLED") == 1


def parse_cpuset_count(value: str) -> int | None:
    """Return the number of CPUs represented by a Linux cpuset range."""
    count = 0
    try:
        for group in value.strip().split(","):
            if not group:
                continue
            if "-" in group:
                start, end = group.split("-", 1)
                count += int(end) - int(start) + 1
            else:
                int(group)
                count += 1
    except ValueError:
        return None
    return count or None


def _read_text_file(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read().strip()
    except OSError:
        return None


def _read_cgroup_cpu_quota() -> float | None:
    """Return a Linux cgroup CPU quota expressed as effective CPUs."""
    cpu_max = _read_text_file("/sys/fs/cgroup/cpu.max")
    if cpu_max:
        fields = cpu_max.split()
        if len(fields) == 2 and fields[0] != "max":
            try:
                quota, period = float(fields[0]), float(fields[1])
                if quota > 0 and period > 0:
                    return quota / period
            except ValueError:
                pass

    quota = _read_text_file("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
    period = _read_text_file("/sys/fs/cgroup/cpu/cpu.cfs_period_us")
    if quota and period:
        try:
            quota_value, period_value = float(quota), float(period)
            if quota_value > 0 and period_value > 0:
                return quota_value / period_value
        except ValueError:
            pass
    return None


def effective_cpu_count() -> float:
    """Return the best-effort CPU capacity available to this process."""
    explicit = os.environ.get(_CPU_LIMIT_ENV)
    if explicit:
        try:
            value = float(explicit)
            if value > 0:
                return value
        except ValueError:
            logger.warning("Ignoring invalid %s=%r", _CPU_LIMIT_ENV, explicit)

    candidates: list[float] = []
    process_cpu_count = getattr(os, "process_cpu_count", None)
    process_count = process_cpu_count() if process_cpu_count is not None else os.cpu_count()
    if process_count:
        candidates.append(float(process_count))

    quota_count = _read_cgroup_cpu_quota()
    if quota_count is not None:
        candidates.append(quota_count)

    cpuset = _read_text_file("/sys/fs/cgroup/cpuset.cpus.effective")
    if cpuset is None:
        cpuset = _read_text_file("/sys/fs/cgroup/cpuset/cpuset.cpus")
    cpuset_count = parse_cpuset_count(cpuset) if cpuset else None
    if cpuset_count is not None:
        candidates.append(float(cpuset_count))

    return min(candidates) if candidates else 1.0


def resolve_observability_startup_mode(is_default_callback: bool) -> tuple[str, str]:
    """Resolve synchronous versus concurrent observability initialization."""
    configured = os.environ.get(_OBSERVABILITY_STARTUP_ENV, "auto").strip().lower()
    if configured not in _OBSERVABILITY_STARTUP_MODES:
        logger.warning(
            "Unrecognised %s=%r; falling back to 'auto'.",
            _OBSERVABILITY_STARTUP_ENV,
            configured,
        )
        configured = "auto"

    if not is_default_callback:
        return "sync", "custom callback"
    if configured == "sync":
        return "sync", "forced by configuration"
    if not is_free_threaded_runtime():
        return "sync", "runtime is not free-threaded with the GIL disabled"

    cpu_count = effective_cpu_count()
    if cpu_count < 2:
        return "sync", f"effective CPU capacity is {cpu_count:g}"
    return "concurrent", f"free-threaded runtime with {cpu_count:g} effective CPUs"
