"""Resolve, verify and install an approved RLE SDK wheel from the public registry."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.request import urlopen

PUBLIC_REPOSITORY = "Azure/azure-sdk-for-python"
PUBLIC_BRANCH = "rle-releases"
PUBLIC_PATH = "sdk/ai/azure-ai-projects/rle"
MANIFEST_URL = (
    f"https://raw.githubusercontent.com/{PUBLIC_REPOSITORY}/"
    f"{PUBLIC_BRANCH}/{PUBLIC_PATH}/registry.json"
)


@dataclass(frozen=True)
class Release:
    version: str
    filename: str
    url: str
    sha256: str


def resolve_release(manifest: object, version: str = "latest") -> Release:
    if not isinstance(manifest, dict):
        raise ValueError("The SDK manifest must be a JSON object.")
    if (
        manifest.get("schema_version") != 1
        or manifest.get("package") != "azure-ai-projects"
        or manifest.get("channel") != "rle"
    ):
        raise ValueError("Unsupported SDK manifest schema, package, or channel.")
    selected = manifest.get("latest") if version == "latest" else version
    versions = manifest.get("versions")
    if not isinstance(selected, str) or not selected or not isinstance(versions, dict) or selected not in versions:
        raise ValueError(f"RLE SDK version {selected!r} is not available.")
    entry = versions[selected]
    if not isinstance(entry, dict) or not all(
        isinstance(entry.get(field), str) and entry[field]
        for field in ("filename", "url", "sha256")
    ):
        raise ValueError(f"Invalid release entry for {selected}.")
    filename = entry["filename"]
    if selected in (".", "..") or any(char in selected + filename for char in "/\\:") or not filename.endswith(".whl"):
        raise ValueError("The SDK version and filename must be safe wheel path components.")
    if not entry["url"].startswith("https://"):
        raise ValueError("The SDK wheel URL must use HTTPS.")
    return Release(selected, filename, entry["url"], entry["sha256"])


def verify_checksum(path: Path, release: Release) -> None:
    if hashlib.sha256(path.read_bytes()).hexdigest() != release.sha256:
        raise ValueError(f"SHA-256 mismatch for SDK {release.version}; refusing installation.")


def download_wheel(release: Release, directory: Path) -> Path:
    target = directory / release.filename
    with urlopen(release.url, timeout=120) as response:
        target.write_bytes(response.read())
    try:
        verify_checksum(target, release)
    except ValueError:
        target.unlink()
        raise
    return target


def load_manifest(location: str) -> object:
    if location.startswith("https://"):
        with urlopen(location, timeout=60) as response:
            return json.load(response)
    return json.loads(Path(location).read_text(encoding="utf-8"))


def selected_version(explicit: str | None) -> str:
    if explicit is not None:
        return explicit
    configured = os.environ.get("AZURE_AI_PROJECTS_VERSION")
    if configured is not None:
        return configured
    return "latest"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=MANIFEST_URL)
    parser.add_argument("--version")
    parser.add_argument("--requirements", type=Path)
    parser.add_argument("--index-url", default=os.environ.get("PIP_INDEX_URL"))
    args = parser.parse_args()
    release = resolve_release(
        load_manifest(args.manifest), selected_version(args.version)
    )
    print(f"RLE SDK: {release.version} (SHA-256 {release.sha256})", flush=True)
    with tempfile.TemporaryDirectory(prefix="rle-sdk-") as temporary:
        wheel = download_wheel(release, Path(temporary))
        command = [
            sys.executable, "-m", "pip", "install", "--no-cache-dir",
            "--progress-bar", "off", f"azure-ai-projects[rle] @ {wheel.as_uri()}",
        ]
        if args.index_url:
            command.extend(["--index-url", args.index_url])
        if args.requirements is not None:
            command.extend(["--requirement", str(args.requirements)])
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
