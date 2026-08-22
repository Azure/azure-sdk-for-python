#!/usr/bin/env python
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Generate extension-owned shared OpenAI/Foundry model contracts."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from finalize_projects_generation import finalize as finalize_projects
from finalize_responses_generation import finalize as finalize_responses


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class GenerationTarget:
    name: str
    type_spec_dir: Path
    temp_dir: Path
    entrypoint: str
    namespace: str
    generated_root: Path


TARGETS = {
    "responses": GenerationTarget(
        name="responses",
        type_spec_dir=PACKAGE_ROOT / "type_spec" / "responses",
        temp_dir=PACKAGE_ROOT / "type_spec" / "responses" / "TempTypeSpecFiles",
        entrypoint="sdk-service-agentserver-contracts/client.tsp",
        namespace="azure.ai.extensions.openai.responses._generated.sdk.models",
        generated_root=PACKAGE_ROOT / "azure" / "ai" / "extensions" / "openai" / "responses" / "_generated" / "sdk" / "models",
    ),
    "projects": GenerationTarget(
        name="projects",
        type_spec_dir=PACKAGE_ROOT / "type_spec" / "projects",
        temp_dir=PACKAGE_ROOT / "type_spec" / "projects" / "TempTypeSpecFiles",
        entrypoint="sdk-python-js-azure-ai-projects/client.tsp",
        namespace="azure.ai.extensions.openai.projects._generated",
        generated_root=PACKAGE_ROOT / "azure" / "ai" / "extensions" / "openai" / "projects" / "_generated",
    ),
}


def _run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def generate(target: GenerationTarget) -> None:
    if shutil.which("tsp-client") is None:
        raise RuntimeError("tsp-client is not installed.")
    if shutil.which("npm") is None:
        raise RuntimeError("npm is required. Install Node.js (v18+) from https://nodejs.org/")

    _run(["tsp-client", "sync"], cwd=target.type_spec_dir)
    _run(["npm", "install", "--silent"], cwd=target.temp_dir)
    shutil.rmtree(target.generated_root, ignore_errors=True)
    _run(
        [
            "npx",
            "tsp",
            "compile",
            target.entrypoint,
            "--emit",
            "@azure-tools/typespec-python",
            "--option",
            f"@azure-tools/typespec-python.emitter-output-dir={PACKAGE_ROOT}",
            "--option",
            f"@azure-tools/typespec-python.namespace={target.namespace}",
            "--option",
            "@azure-tools/typespec-python.package-name=azure-ai-extensions-openai",
            "--option",
            "@azure-tools/typespec-python.models-mode=typeddict",
            "--option",
            "@azure-tools/typespec-python.generate-packaging-files=false",
        ],
        cwd=target.temp_dir,
    )
    if target.name == "responses":
        finalize_responses(target.generated_root)
    else:
        finalize_projects(target.generated_root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=sorted(TARGETS))
    args = parser.parse_args()
    generate(TARGETS[args.target])


if __name__ == "__main__":
    main()
