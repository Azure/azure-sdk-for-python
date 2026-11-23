# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from copy import deepcopy
from pathlib import Path
import re
from typing import Optional

try:
    import tomllib as toml
except ImportError:
    import tomli as toml

from packaging.version import InvalidVersion, Version

_NUMBER = r"(?:0|[1-9][0-9]*)"
_PRERELEASE = r"(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
_SEMVER = re.compile(
    rf"{_NUMBER}\.{_NUMBER}\.{_NUMBER}"
    rf"(?:-{_PRERELEASE}(?:\.{_PRERELEASE})*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)
_MAX_CARGO_COMPONENT = 2**64 - 1
_TABLE_HEADER = re.compile(r"(?m)^[ \t]*\[{1,2}[^\r\n\]]+\]{1,2}[ \t]*(?:#[^\r\n]*)?\r?$")
_PACKAGE_HEADER = re.compile(r"""^[ \t]*\[[ \t]*(?:package|"package"|'package')[ \t]*\]""")
_LOCK_PACKAGE_HEADER = re.compile(r"^[ \t]*\[\[[ \t]*package[ \t]*\]\]")
_VERSION_FIELD = re.compile(
    r"""(?m)^[ \t]*(?:version|"version"|'version')[ \t]*=[ \t]*(?P<quote>["'])"""
    r"""(?P<value>[^"'\r\n]*)(?P=quote)[ \t]*(?:#[^\r\n]*)?\r?$"""
)


def _load_toml(path: Path) -> dict:
    try:
        with path.open("rb") as stream:
            return toml.load(stream)
    except (FileNotFoundError, toml.TOMLDecodeError) as exc:
        raise ValueError(f"Unable to read valid TOML from {path}: {exc}") from exc


def get_maturin_cargo_manifest(pyproject_path, config: Optional[dict] = None) -> Optional[Path]:
    """Find the Cargo version source only when maturin supplies a dynamic project version."""
    pyproject_path = Path(pyproject_path)
    if pyproject_path.name != "pyproject.toml" or not pyproject_path.is_file():
        return None

    config = config if config is not None else _load_toml(pyproject_path)
    project = config.get("project", {})
    if (
        config.get("build-system", {}).get("build-backend") != "maturin"
        or "version" in project
        or "version" not in project.get("dynamic", [])
    ):
        return None

    manifest = config.get("tool", {}).get("maturin", {}).get("manifest-path", "Cargo.toml")
    if not isinstance(manifest, str) or not manifest:
        raise ValueError(f"Invalid maturin manifest-path in {pyproject_path}")
    return pyproject_path.parent / manifest


def _manifest_version(config: dict, manifest: Path) -> tuple[str, str]:
    package = config.get("package", {})
    version = package.get("version") if isinstance(package, dict) else None
    if not isinstance(version, str) or not _SEMVER.fullmatch(version):
        raise ValueError(f"{manifest} must declare a direct [package].version using Cargo SemVer")
    try:
        parsed = Version(version)
    except InvalidVersion as exc:
        raise ValueError(f"Version {version!r} in {manifest} is not valid Python package metadata") from exc
    if any(part > _MAX_CARGO_COMPONENT for part in parsed.release):
        raise ValueError(f"Version {version!r} in {manifest} exceeds Cargo's numeric limit")
    return version, str(parsed)


def get_cargo_version(manifest: Path) -> str:
    """Return the PEP 440 version maturin derives from a Cargo manifest."""
    return _manifest_version(_load_toml(manifest), manifest)[1]


def _cargo_version_from_python(version: str) -> str:
    try:
        parsed = Version(version)
    except InvalidVersion as exc:
        raise ValueError(f"Invalid Python package version: {version!r}") from exc

    if (
        parsed.epoch
        or len(parsed.release) != 3
        or any(part > _MAX_CARGO_COMPONENT for part in parsed.release)
        or parsed.post is not None
        or (parsed.pre is not None and parsed.dev is not None)
    ):
        raise ValueError(f"Python version {version!r} cannot be represented safely as a Cargo version")

    result = ".".join(str(part) for part in parsed.release)
    if parsed.pre is not None:
        label = {"a": "alpha", "b": "beta", "rc": "rc"}[parsed.pre[0]]
        result += f"-{label}.{parsed.pre[1]}"
    elif parsed.dev is not None:
        result += f"-dev.{parsed.dev}"
    if parsed.local:
        result += f"+{parsed.local}"
    return result


def _read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return stream.read()


def _replace_version_field(contents: str, start: int, end: int, version: str, path: Path) -> str:
    matches = list(_VERSION_FIELD.finditer(contents, start, end))
    if len(matches) != 1:
        raise ValueError(f"Unable to safely locate a single version field in {path}")
    match = matches[0]
    return contents[: match.start("value")] + version + contents[match.end("value") :]


def _replace_manifest_version(contents: str, config: dict, version: str, manifest: Path) -> str:
    headers = list(_TABLE_HEADER.finditer(contents))
    matching = [index for index, header in enumerate(headers) if _PACKAGE_HEADER.match(header.group())]
    if len(matching) != 1:
        raise ValueError(f"Unable to safely locate the [package] table in {manifest}")
    index = matching[0]
    end = headers[index + 1].start() if index + 1 < len(headers) else len(contents)
    updated = _replace_version_field(contents, headers[index].end(), end, version, manifest)
    expected = deepcopy(config)
    expected["package"]["version"] = version
    if toml.loads(updated) != expected:
        raise ValueError(f"Updating {manifest} would change fields other than [package].version")
    return updated


def _replace_lock_version(contents: str, config: dict, name: str, old: str, new: str, lock: Path) -> str:
    packages = config.get("package", [])
    if not isinstance(packages, list) or any(not isinstance(package, dict) for package in packages):
        raise ValueError(f"Invalid package entries in {lock}")
    matches = [
        index
        for index, package in enumerate(packages)
        if package.get("name") == name and package.get("version") == old and "source" not in package
    ]
    if len(matches) != 1:
        raise ValueError(f"{lock} does not contain exactly one local {name} package at version {old}")
    if any(
        not isinstance(package.get("dependencies", []), list)
        or any(not isinstance(dependency, str) for dependency in package.get("dependencies", []))
        for package in packages
    ):
        raise ValueError(f"Invalid dependency entries in {lock}")
    if old != new and any(
        dependency.split(" ", 1)[0] == name for package in packages for dependency in package.get("dependencies", [])
    ):
        raise ValueError(f"{lock} contains dependencies on {name}; update this workspace with Cargo")

    headers = list(_TABLE_HEADER.finditer(contents))
    package_headers = [index for index, header in enumerate(headers) if _LOCK_PACKAGE_HEADER.match(header.group())]
    if len(package_headers) != len(packages):
        raise ValueError(f"Unable to safely locate package entries in {lock}")
    header_index = package_headers[matches[0]]
    end = headers[header_index + 1].start() if header_index + 1 < len(headers) else len(contents)
    updated = _replace_version_field(contents, headers[header_index].end(), end, new, lock)
    expected = deepcopy(config)
    expected["package"][matches[0]]["version"] = new
    if toml.loads(updated) != expected:
        raise ValueError(f"Updating {lock} would change fields other than the local package version")
    return updated


def set_cargo_version(manifest: Path, version: str) -> None:
    """Update a maturin package's Cargo version and its existing local lock entry."""
    manifest = manifest.resolve()
    config = _load_toml(manifest)
    old_version, _ = _manifest_version(config, manifest)
    new_version = _cargo_version_from_python(version)
    contents = _replace_manifest_version(_read_text(manifest), config, new_version, manifest)

    if "workspace" in config or config["package"].get("workspace"):
        raise ValueError(f"Cargo workspace version updates are not supported for {manifest}")
    for ancestor in manifest.parent.parents:
        parent_manifest = ancestor / "Cargo.toml"
        if parent_manifest.is_file() and "workspace" in _load_toml(parent_manifest):
            raise ValueError(f"Cargo workspace version updates are not supported for {manifest}")
        if (ancestor / ".git").exists():
            break

    lock = manifest.parent / "Cargo.lock"
    lock_contents = None
    if lock.exists():
        name = config["package"].get("name")
        if not isinstance(name, str) or not name:
            raise ValueError(f"{manifest} must declare [package].name to update {lock}")
        lock_contents = _replace_lock_version(_read_text(lock), _load_toml(lock), name, old_version, new_version, lock)

    with manifest.open("w", encoding="utf-8", newline="") as stream:
        stream.write(contents)
    if lock_contents is not None:
        with lock.open("w", encoding="utf-8", newline="") as stream:
            stream.write(lock_contents)
