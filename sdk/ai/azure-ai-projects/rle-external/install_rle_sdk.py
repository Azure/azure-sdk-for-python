"""Install an approved RLE SDK wheel without accessing its source repository."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.request import urlopen
import zipfile

PUBLIC_REPOSITORY = "Azure/azure-sdk-for-python"
PUBLIC_BRANCH = "rle-external-releases"
PUBLIC_PATH = "sdk/ai/azure-ai-projects/rle-external"
MANIFEST_URL = (
    f"https://raw.githubusercontent.com/{PUBLIC_REPOSITORY}/"
    f"{PUBLIC_BRANCH}/{PUBLIC_PATH}/registry.json"
)
VERSION_PATTERN = r"[0-9]+\.[0-9]+\.[0-9]+\.dev[0-9]+"


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
        or manifest.get("channel") != "rle-external"
    ):
        raise ValueError("Unsupported SDK manifest schema, package, or channel.")
    selected = manifest.get("latest") if version == "latest" else version
    if not isinstance(selected, str) or not re.fullmatch(VERSION_PATTERN, selected):
        raise ValueError(f"Invalid RLE SDK version: {selected!r}")
    versions = manifest.get("versions")
    if not isinstance(versions, dict) or selected not in versions:
        raise ValueError(f"RLE SDK version {selected!r} is not available.")
    entry = versions[selected]
    if not isinstance(entry, dict):
        raise ValueError(f"Invalid release entry for {selected}.")
    filename = f"azure_ai_projects-{selected}-py3-none-any.whl"
    url = entry.get("url")
    digest = entry.get("sha256")
    if entry.get("filename") != filename:
        raise ValueError(f"Unexpected wheel filename for {selected}.")
    expected_url = (
        rf"https://raw\.githubusercontent\.com/{re.escape(PUBLIC_REPOSITORY)}/"
        rf"[0-9a-f]{{40}}/{re.escape(PUBLIC_PATH)}/wheels/"
        rf"{re.escape(selected)}/{re.escape(filename)}"
    )
    if not isinstance(url, str) or not re.fullmatch(expected_url, url):
        raise ValueError("The wheel URL must reference an immutable public SDK commit.")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("The wheel SHA-256 must contain 64 lowercase hexadecimal digits.")
    return Release(selected, filename, url, digest)


def validate_wheel(path: Path, version: str) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        metadata_paths = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_paths) != 1:
            raise ValueError("Expected exactly one wheel METADATA file.")
        metadata = BytesParser().parsebytes(archive.read(metadata_paths[0]))
        if metadata["Name"] != "azure-ai-projects" or metadata["Version"] != version:
            raise ValueError("Wheel package name or version does not match the manifest.")
        if "rle" not in metadata.get_all("Provides-Extra", []):
            raise ValueError("The wheel does not declare the rle extra.")
        if "azure/ai/projects/rle/environments/__init__.py" not in names:
            raise ValueError("The wheel does not contain RLEnvironment.")
        if archive.testzip() is not None:
            raise ValueError("The wheel contains corrupt entries.")


def download_wheel(release: Release, directory: Path) -> Path:
    target = directory / release.filename
    digest = hashlib.sha256()
    with urlopen(release.url, timeout=120) as response, target.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
            output.write(chunk)
    if digest.hexdigest() != release.sha256:
        target.unlink()
        raise ValueError(f"SHA-256 mismatch for SDK {release.version}; refusing installation.")
    validate_wheel(target, release.version)
    return target


def load_manifest(location: str) -> object:
    if location.startswith("https://"):
        with urlopen(location, timeout=60) as response:
            return json.load(response)
    return json.loads(Path(location).read_text(encoding="utf-8"))


def selected_version(explicit: str | None, version_file: Path | None) -> str:
    if explicit is not None:
        return explicit
    configured = os.environ.get("AZURE_AI_PROJECTS_RLE_VERSION")
    if configured is not None:
        return configured
    if version_file is not None:
        return version_file.read_text(encoding="utf-8").strip()
    return "latest"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=MANIFEST_URL)
    parser.add_argument("--version")
    parser.add_argument("--version-file", type=Path)
    parser.add_argument("--requirements", type=Path)
    parser.add_argument("--index-url", default=os.environ.get("PIP_INDEX_URL"))
    parser.add_argument("--download-only", type=Path)
    args = parser.parse_args()
    release = resolve_release(
        load_manifest(args.manifest), selected_version(args.version, args.version_file)
    )
    print(f"RLE SDK: {release.version} (SHA-256 {release.sha256})", flush=True)
    if args.download_only is not None:
        args.download_only.mkdir(parents=True, exist_ok=True)
        print(download_wheel(release, args.download_only))
        return
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
