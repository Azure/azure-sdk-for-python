# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check source metadata without importing the SDK or requiring build dependencies."""

from pathlib import Path
import re


def _single_value(pattern: str, text: str, source: str) -> str:
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one version in {source}")
    return matches[0]


def validate_version_metadata(package_root: Path = Path(__file__).resolve().parent) -> str:
    """Return the authoritative Python version, rejecting stale release metadata."""
    version = _single_value(
        r"""^VERSION[ \t]*=[ \t]*["']([^"'\r\n]+)["'][ \t]*(?:#.*)?$""",
        (package_root / "azure" / "cosmos" / "_version.py").read_text(encoding="utf-8"),
        "_version.py",
    )
    pyproject = (package_root / "pyproject.toml").read_text(encoding="utf-8")
    project = re.search(r"(?ms)^\[project\][ \t]*\n(.*?)(?=^\[|\Z)", pyproject)
    if project is None:
        raise RuntimeError("Missing [project] table in pyproject.toml")
    declared = {
        "pyproject.toml": _single_value(
            r"""^version[ \t]*=[ \t]*["']([^"'\r\n]+)["'][ \t]*(?:#.*)?$""",
            project.group(1),
            "pyproject.toml [project]",
        ),
        "api.metadata.yml": _single_value(
            r"^packageVersion:[ \t]*([^\s#]+)[ \t]*(?:#.*)?$",
            (package_root / "api.metadata.yml").read_text(encoding="utf-8"),
            "api.metadata.yml",
        ).strip("'\""),
    }
    changelog = re.search(
        r"(?m)^#{2,3}[ \t]+(\d+\.\d+\.\d+\S*)[ \t]+\(",
        (package_root / "CHANGELOG.md").read_text(encoding="utf-8"),
    )
    if changelog is None:
        raise RuntimeError("Missing release heading in CHANGELOG.md")
    declared["CHANGELOG.md"] = changelog.group(1)
    mismatches = [f"{name}={value}" for name, value in declared.items() if value != version]
    if mismatches:
        raise RuntimeError(
            f"Package version mismatch: _version.py={version}; "
            + "; ".join(mismatches)
            + ". Run the repository version updater before building."
        )
    return version
