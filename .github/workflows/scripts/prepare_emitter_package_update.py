# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Validate untrusted generator output before publishing an emitter update PR."""

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
from urllib.parse import unquote, urlsplit

FILES = ("emitter-package.json", "emitter-package-lock.json")
SECTIONS = ("dependencies", "devDependencies", "optionalDependencies")
CFS_REGISTRY = "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-js/npm/registry/"
VERSION = re.compile(
    r"[~^]?[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?"
)
MAX_JSON_BYTES = 20 * 1024 * 1024


def read_json(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError("Update inputs must be bounded, regular JSON files")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def metadata(value):
    return {key: item for key, item in value.items() if key not in SECTIONS}


def prepare_update(artifact, repository):
    if (
        artifact.is_symlink()
        or not artifact.is_dir()
        or {entry.name for entry in artifact.iterdir()} != set(FILES)
    ):
        raise ValueError("Artifact must contain exactly the two emitter JSON files")
    manifest, lock = [read_json(artifact / name) for name in FILES]
    original, original_lock = [read_json(repository / "eng" / name) for name in FILES]

    if manifest.keys() != original.keys() or metadata(manifest) != metadata(original):
        raise ValueError("Only dependency versions may change in the manifest")
    changed = False
    for section in SECTIONS:
        before, after = original.get(section, {}), manifest.get(section, {})
        if not isinstance(after, dict) or before.keys() != after.keys():
            raise ValueError("Dependency names and sections must remain unchanged")
        for name, version in after.items():
            if not isinstance(version, str) or VERSION.fullmatch(version) is None:
                raise ValueError(
                    "Dependency versions must be npm semantic versions, not URLs or paths"
                )
            changed |= version != before[name]

    if {key: value for key, value in lock.items() if key != "packages"} != {
        key: value for key, value in original_lock.items() if key != "packages"
    }:
        raise ValueError("Unexpected lockfile metadata changes")
    packages = lock.get("packages")
    if not isinstance(packages, dict) or not isinstance(packages.get(""), dict):
        raise ValueError("Lockfile must contain a root package")
    root = packages[""]
    if metadata(root) != metadata(original_lock["packages"][""]):
        raise ValueError("Unexpected root package metadata changes")
    if any(root.get(section, {}) != manifest.get(section, {}) for section in SECTIONS):
        raise ValueError("Lockfile root dependencies must match the manifest")
    for name, package in packages.items():
        if not isinstance(package, dict):
            raise ValueError("Lockfile package entries must be objects")
        if name == "":
            continue
        if (
            not name.startswith("node_modules/")
            or "\\" in name
            or ":" in name
            or ".." in PurePosixPath(name).parts
            or str(PurePosixPath(name)) != name
            or package.get("link")
        ):
            raise ValueError(
                "Lockfile packages must not reference local paths or links"
            )
        version = package.get("version")
        if (
            not isinstance(version, str)
            or VERSION.fullmatch(version) is None
            or version.startswith(("^", "~"))
        ):
            raise ValueError("Locked package versions must be exact semantic versions")
        resolved = package.get("resolved")
        if not isinstance(resolved, str) or not resolved.startswith(CFS_REGISTRY):
            raise ValueError("Lockfile packages must resolve through the CFS npm feed")
        url = urlsplit(resolved)
        decoded_path = unquote(url.path)
        if (
            url.query
            or url.fragment
            or "\\" in decoded_path
            or any(part in (".", "..") for part in decoded_path.split("/"))
        ):
            raise ValueError("Invalid CFS package URL")

    if changed:
        # Re-serialize data, never copy executable files or generator-controlled paths.
        for name, value in zip(FILES, (manifest, lock)):
            (repository / "eng" / name).write_text(
                json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8"
            )
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    available = prepare_update(args.artifact, Path.cwd())
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write(f"available={str(available).lower()}\n")


if __name__ == "__main__":
    main()
