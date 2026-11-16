# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import argparse
import json
import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

REGISTRY = "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-js/npm/registry/"
FILTER = "@typespec/*,@azure-tools/typespec-python"


def _run(command):
    executable = shutil.which(command[0])
    if not executable:
        raise RuntimeError(f"Required command not found: {command[0]}")
    try:
        return subprocess.run(
            [executable, *command[1:]],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"{command[0]} failed: {error.stderr.strip()}") from error


def check_emitter_package_updates(package_file, registry=REGISTRY):
    manifest = json.loads(Path(package_file).read_text(encoding="utf-8-sig"))
    watched = {
        name
        for section in ("dependencies", "devDependencies", "optionalDependencies")
        for name in manifest.get(section, {})
        if name.startswith("@typespec/") or name == "@azure-tools/typespec-python"
    }
    if not watched:
        raise ValueError(f"No watched emitter dependencies found in {package_file}")

    packages = {}
    for name in sorted(watched):
        try:
            output = _run(
                [
                    "npm",
                    "view",
                    name,
                    "versions",
                    "dist-tags",
                    "--json",
                    "--registry",
                    registry,
                ]
            )
        except RuntimeError as error:
            raise RuntimeError(f"Could not query CFS for {name}: {error}") from error
        metadata = json.loads(output)
        versions = metadata.get("versions")
        tags = metadata.get("dist-tags")
        if (
            not isinstance(versions, list)
            or not versions
            or not all(isinstance(version, str) and version for version in versions)
            or not isinstance(tags, dict)
            or not isinstance(tags.get("latest"), str)
            or tags["latest"] not in versions
        ):
            raise ValueError(f"Invalid CFS metadata for {name}")
        packages[name] = {
            "name": name,
            "versions": {
                version: {"name": name, "version": version} for version in versions
            },
            "dist-tags": tags,
        }

    # ncu's JSON output suppresses registry errors. Serve the validated metadata
    # locally so ncu still applies its own npm version-selection rules.
    requested = set()

    class RegistryHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            name = unquote(urlsplit(self.path).path).lstrip("/")
            if name not in packages:
                self.send_error(404)
                return
            requested.add(name)
            data = json.dumps(packages[name]).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format, *args):
            pass

    with ThreadingHTTPServer(("127.0.0.1", 0), RegistryHandler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            output = _run(
                [
                    "ncu",
                    "--packageFile",
                    str(package_file),
                    "--registry",
                    f"http://127.0.0.1:{server.server_port}/",
                    "--filter",
                    FILTER,
                    "--jsonUpgraded",
                    "--loglevel",
                    "error",
                ]
            )
        finally:
            server.shutdown()
            thread.join()
    unresolved = watched - requested
    if unresolved:
        raise RuntimeError(
            f"Could not resolve CFS versions for: {', '.join(sorted(unresolved))}"
        )
    upgrades = json.loads(output)
    if (
        not isinstance(upgrades, dict)
        or not upgrades.keys() <= watched
        or not all(isinstance(version, str) for version in upgrades.values())
    ):
        raise ValueError("Invalid npm-check-updates output")
    return upgrades


def main():
    parser = argparse.ArgumentParser(
        description="Check CFS for emitter dependency updates"
    )
    parser.add_argument("package_file", type=Path)
    args = parser.parse_args()
    upgrades = check_emitter_package_updates(args.package_file)
    print(
        json.dumps(upgrades, indent=2)
        if upgrades
        else "No eligible watched package updates in CFS."
    )
    print(
        f"##vso[task.setvariable variable=EmitterPackageHasUpdates;isOutput=true]{str(bool(upgrades)).lower()}"
    )


if __name__ == "__main__":
    main()
