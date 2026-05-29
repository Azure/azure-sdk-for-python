#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Generate API.md for an Azure SDK package.

Usage:
    python scripts/generate_api_text.py azure-ai-projects
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile


REPO_ROOT = os.environ.get("AZSDK_REPO_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APIVIEW_REQS = os.path.join(REPO_ROOT, "eng", "apiview_reqs.txt")
AZURE_SDK_INDEX = "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/"
EXPORT_SCRIPT = os.environ.get("AZSDK_EXPORT_SCRIPT") or os.path.join(
    REPO_ROOT, "eng", "common", "scripts", "Export-APIViewMarkdown.ps1"
)


def find_package_dir(package_name: str) -> str:
    """Find the package directory under sdk/*/{package_name}/."""
    pattern = os.path.join(REPO_ROOT, "sdk", "*", package_name)
    matches = glob.glob(pattern)
    # Filter to directories that contain a pyproject.toml or setup.py
    valid = [
        m
        for m in matches
        if os.path.isdir(m)
        and (os.path.exists(os.path.join(m, "pyproject.toml")) or os.path.exists(os.path.join(m, "setup.py")))
    ]
    if not valid:
        raise FileNotFoundError(f"Package '{package_name}' not found under sdk/*/")
    if len(valid) > 1:
        raise ValueError(f"Multiple matches for '{package_name}': {valid}")
    return valid[0]


def get_installed_version(package: str) -> str | None:
    """Get the currently installed version of a package, or None."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
    except subprocess.CalledProcessError:
        pass
    return None


def get_latest_version(package: str) -> str | None:
    """Query the Azure SDK feed for the latest version of a package."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", package, "--index-url", AZURE_SDK_INDEX],
            capture_output=True,
            text=True,
            check=True,
        )
        # Output format: "apiview-stub-generator (0.3.28)"
        for line in result.stdout.splitlines():
            if package in line and "(" in line:
                version = line.split("(")[1].split(")")[0].strip()
                return version
    except subprocess.CalledProcessError:
        pass
    return None


def ensure_latest_apiview_stub_generator():
    """Ensure the latest apiview-stub-generator is installed from the Azure SDK feed.

    If we cannot determine the latest version (e.g. the feed query fails),
    fail fast rather than proceeding with an unknown potentially stale version.
    """
    installed = get_installed_version("apiview-stub-generator")
    latest = get_latest_version("apiview-stub-generator")

    print(f"apiview-stub-generator: installed={installed}, latest={latest}")

    if installed and latest and installed == latest:
        print("Already at latest version.")
        return

    if not latest:
        raise RuntimeError(
            "Could not determine the latest apiview-stub-generator from the "
            "Azure SDK feed. Failing to avoid using an unknown local version."
        )

    # Install from apiview_reqs.txt first (gets dependencies right)
    print("Installing apiview_reqs.txt...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", APIVIEW_REQS, f"--index-url={AZURE_SDK_INDEX}"],
        check=True,
    )

    # Override with latest version (not the pinned one)
    print("Upgrading apiview-stub-generator to latest...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "apiview-stub-generator",
            f"--index-url={AZURE_SDK_INDEX}",
        ],
        check=True,
    )

    new_version = get_installed_version("apiview-stub-generator")
    print(f"apiview-stub-generator now at version {new_version}")


def build_wheel(package_dir: str, output_dir: str) -> str:
    """Build a wheel for the package and return the path to the .whl file."""
    subprocess.run(
        [sys.executable, "-m", "pip", "wheel", package_dir, "--no-deps", "-w", output_dir],
        check=True,
    )
    whls = glob.glob(os.path.join(output_dir, "*.whl"))
    if not whls:
        raise FileNotFoundError(f"No .whl file found in {output_dir}")
    return whls[0]


def run_apistub(whl_path: str, out_path: str):
    """Run apiview-stub-generator on the wheel."""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "apistub",
            "--pkg-path",
            whl_path,
            "--out-path",
            out_path,
            "--skip-pylint",
        ],
        check=True,
    )


def export_api_markdown(token_json_path: str, output_path: str):
    """Run the Export-APIViewMarkdown.ps1 script to convert token JSON to API.md."""
    try:
        subprocess.run(
            ["pwsh", EXPORT_SCRIPT, "-TokenJsonPath", token_json_path, "-OutputPath", output_path],
            check=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "PowerShell 7 (pwsh) is required to export API markdown but was not found on PATH. "
            "Install PowerShell from "
            "https://learn.microsoft.com/powershell/scripting/install/installing-powershell "
            "and restart your terminal/IDE."
        ) from exc


def main():
    parser = argparse.ArgumentParser(description="Generate API.md for an Azure SDK package.")
    parser.add_argument("package", help="Package name (e.g. azure-ai-projects)")
    args = parser.parse_args()

    package_name = args.package
    print(f"Generating API.md for {package_name}...")

    # Find the package
    package_dir = find_package_dir(package_name)
    print(f"Found package at: {package_dir}")

    # Ensure latest apiview-stub-generator
    ensure_latest_apiview_stub_generator()

    # Build wheel in a temp directory
    tmp_dir = tempfile.mkdtemp(prefix="apistub_")
    try:
        print("Building wheel...")
        whl_path = build_wheel(package_dir, tmp_dir)
        print(f"Built: {os.path.basename(whl_path)}")

        # Run apiview-stub-generator
        print("Running apiview-stub-generator...")
        run_apistub(whl_path, tmp_dir)

        # Find the generated token JSON
        token_json = os.path.join(tmp_dir, f"{package_name}_python.json")
        if not os.path.exists(token_json):
            # Try with underscores (package name normalization)
            normalized = package_name.replace("-", "_")
            token_json = os.path.join(tmp_dir, f"{normalized}_python.json")
        if not os.path.exists(token_json):
            # Find any json file
            jsons = glob.glob(os.path.join(tmp_dir, "*_python.json"))
            if jsons:
                token_json = jsons[0]
            else:
                raise FileNotFoundError(f"No token JSON found in {tmp_dir}")

        # Export to API.md
        api_md_path = os.path.join(package_dir, "API.md")
        print("Exporting API.md...")
        export_api_markdown(token_json, api_md_path)
        print(f"Generated: {api_md_path}")

    finally:
        # Clean up temp directory (wheel + token json)
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
