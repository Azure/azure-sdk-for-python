"""Helpers for loading the pinned versions of the third-party tools that the
``azpysdk`` checks install at runtime (mypy, pylint, pyright, sphinx, ...).

The pins live in ``eng/tool_requirements/<name>.txt`` so they are a single,
machine-scannable source of truth. Keeping them out of the Python modules lets
the daily CFS warm-up (``eng/scripts/warm_cfs_feed.py``) discover the tools and
pre-cache their full transitive dependency closures in the CFS feed, which is
what prevents unauthenticated PR pipelines from failing when an unpinned
transitive dependency releases a new version.

Each requirements file is an ordinary pip requirements file: one requirement per
line, ``#`` comments and blank lines allowed.
"""

import os
from typing import List

from ci_tools.variables import discover_repo_root

REPO_ROOT = discover_repo_root()

# Folder that holds the pinned tool requirement files.
TOOL_REQUIREMENTS_DIR = os.path.join(REPO_ROOT, "eng", "tool_requirements")


def requirements_path(name: str) -> str:
    """Return the absolute path to ``eng/tool_requirements/<name>.txt``.

    :param str name: The requirements file stem (e.g. ``"mypy"`` or ``"pylint_next"``).
    :rtype: str
    """
    return os.path.join(TOOL_REQUIREMENTS_DIR, f"{name}.txt")


def load_requirements(name: str) -> List[str]:
    """Load the requirement specifiers from ``eng/tool_requirements/<name>.txt``.

    Comments (``#``) and blank lines are stripped. The returned list is suitable
    for passing directly to :func:`ci_tools.functions.install_into_venv`.

    :param str name: The requirements file stem (e.g. ``"mypy"`` or ``"pylint_next"``).
    :return: The list of requirement specifiers, in file order.
    :rtype: List[str]
    """
    path = requirements_path(name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"No tool requirements file found at {path}")

    specifiers: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.split("#", 1)[0].strip()
            if stripped:
                specifiers.append(stripped)
    return specifiers


def _requirement_name(specifier: str) -> str:
    """Return the lowercased distribution name from a requirement specifier."""
    from packaging.requirements import Requirement

    return Requirement(specifier).name.lower()


def pin(name: str, package: str) -> str:
    """Return the single requirement specifier for ``package`` from ``<name>.txt``.

    Useful when a check installs the packages from one file across multiple pip
    invocations (e.g. pylint installs ``azure-pylint-guidelines-checker`` before
    building the target package and ``pylint`` itself afterwards).

    :param str name: The requirements file stem (e.g. ``"pylint"``).
    :param str package: The distribution name to look up (e.g. ``"pylint"``).
    :return: The full requirement specifier (e.g. ``"pylint==4.0.4"``).
    :rtype: str
    """
    target = package.lower()
    for specifier in load_requirements(name):
        if _requirement_name(specifier) == target:
            return specifier
    raise KeyError(f"'{package}' is not listed in tool requirements file '{name}.txt'")


def pinned_version(name: str, package: str) -> str:
    """Return just the pinned version string for ``package`` from ``<name>.txt``.

    :param str name: The requirements file stem (e.g. ``"mypy"``).
    :param str package: The distribution name to look up (e.g. ``"mypy"``).
    :return: The pinned version (e.g. ``"1.19.1"``), or empty string if unpinned.
    :rtype: str
    """
    from packaging.requirements import Requirement

    requirement = Requirement(pin(name, package))
    specifiers = list(requirement.specifier)
    return specifiers[0].version if specifiers else ""
