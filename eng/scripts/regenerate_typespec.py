# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Regenerate existing TypeSpec clients and retain reviewable changes and logs."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess

import yaml


def discover_clients(repo: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", "sdk/**/tsp-location.yaml"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    locations = sorted(repo / name.decode("utf-8") for name in result.stdout.split(b"\0") if name)
    clients = []
    for location in locations:
        try:
            config = yaml.safe_load(location.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            # Let tsp-client report invalid configurations as individual failures
            # rather than preventing regeneration of every other client.
            config = None
        if (
            isinstance(config, dict)
            and set(config) == {"batch"}
            and isinstance(config["batch"], list)
            and config["batch"]
        ):
            children = config["batch"]
            if all(
                isinstance(child, str) and (location.parent / child / "tsp-location.yaml").resolve() in locations
                for child in children
            ):
                # Run each tracked child independently so a failed batch member
                # cannot prevent the remaining members from being attempted.
                continue
        clients.append(location.parent)
    return clients


def regenerate(repo: Path, output: Path, shard_index: int = 0, shard_count: int = 1) -> int:
    if shard_count < 1 or not 0 <= shard_index < shard_count:
        raise ValueError("Require shard-count > 0 and 0 <= shard-index < shard-count")
    repo = repo.resolve()
    output = output.resolve()
    if output == repo or repo in output.parents:
        raise ValueError("The output directory must be outside the checkout")
    status = subprocess.run(["git", "status", "--porcelain"], cwd=repo, check=True, capture_output=True, text=True)
    if status.stdout.strip():
        raise ValueError("Regeneration requires a clean checkout, including untracked files")

    clients = discover_clients(repo)
    if not clients:
        raise ValueError("No TypeSpec clients were found under sdk")
    clients = clients[shard_index::shard_count]
    node = shutil.which("node")
    if node is None:
        raise FileNotFoundError("Node.js is required for TypeSpec regeneration")
    cli = repo / "eng" / "common" / "tsp-client" / "node_modules" / "@azure-tools"
    cli = cli / "typespec-client-generator-cli" / "cmd" / "tsp-client.js"
    if not cli.is_file():
        raise FileNotFoundError("Install the pinned CLI with: npm ci --prefix eng/common/tsp-client")
    command = [node, str(cli), "update", "--skip-install", "--debug"]
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for index, client in enumerate(clients):
        relative = client.relative_to(repo).as_posix()
        log_name = f"{index:04d}.log"
        print(f"Regenerating {relative}", flush=True)
        with (output / log_name).open("wb") as log:
            result = subprocess.run(command, cwd=client, stdout=log, stderr=subprocess.STDOUT, check=False)
        results.append({"directory": relative, "exit_code": result.returncode, "log": log_name})
        if result.returncode:
            print(f"Generation failed for {relative}: exit {result.returncode}; see {log_name}", flush=True)
        (output / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    # Include new generated files without creating commits. The clean checkout
    # requirement ensures this cannot stage a developer's existing work.
    subprocess.run(["git", "add", "--intent-to-add", "--", "sdk"], cwd=repo, check=True)
    with (output / "changes.patch").open("wb") as patch:
        subprocess.run(["git", "diff", "--binary", "HEAD", "--", "sdk"], cwd=repo, stdout=patch, check=True)
    with (output / "changes.txt").open("wb") as summary:
        subprocess.run(["git", "diff", "--stat", "HEAD", "--", "sdk"], cwd=repo, stdout=summary, check=True)
    (output / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return int(any(result["exit_code"] for result in results))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True, help="Artifact directory outside the checkout")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    args = parser.parse_args()
    return regenerate(args.repo, args.output, args.shard_index, args.shard_count)


if __name__ == "__main__":
    raise SystemExit(main())
