# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Compare client-side upload preparation across two azure-search-documents packages."""

from __future__ import annotations

import argparse
import json
import math
from importlib.metadata import version
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch
import venv

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def _python_executable(environment: Path) -> Path:
    scripts = "Scripts" if sys.platform == "win32" else "bin"
    executable = "python.exe" if sys.platform == "win32" else "python"
    return environment / scripts / executable


def _package_spec(value: str) -> str:
    path = Path(value).expanduser()
    return str(path.resolve()) if path.exists() else value


def _run_worker(python: Path, arguments: argparse.Namespace) -> dict[str, object]:
    command = [
        str(python),
        str(Path(__file__).resolve()),
        "--worker",
        "--repeats",
        str(arguments.repeats),
        "--warmups",
        str(arguments.warmups),
        "--num-documents",
        str(arguments.num_documents),
        "--vector-dimensions",
        str(arguments.vector_dimensions),
        "--text-length",
        str(arguments.text_length),
    ]
    output = subprocess.run(command, check=True, capture_output=True, text=True).stdout
    return json.loads(output)


def _install_and_run(root: Path, label: str, package: str, arguments: argparse.Namespace) -> dict[str, object]:
    environment = root / label
    print(f"Creating {label} environment", file=sys.stderr)
    venv.EnvBuilder(with_pip=True).create(environment)
    python = _python_executable(environment)
    package = _package_spec(package)
    print(f"Installing {package}", file=sys.stderr)
    subprocess.run([str(python), "-m", "pip", "install", "--quiet", package], check=True)
    return _run_worker(python, arguments)


def _print_result(label: str, result: dict[str, object]) -> None:
    print(
        f"{label:<10} {result['version']:<14} "
        f"median={result['median_ms']:>10.3f} ms  "
        f"min={result['min_ms']:>10.3f} ms  "
        f"p95={result['p95_ms']:>10.3f} ms"
    )


def _controller(arguments: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory(prefix="azure-search-upload-perf-") as directory:
        root = Path(directory)
        baseline = _install_and_run(root, "baseline", arguments.baseline, arguments)
        candidate = _install_and_run(root, "candidate", arguments.candidate, arguments)

    print(
        f"Payload: {arguments.num_documents} documents, "
        f"{arguments.vector_dimensions} vector dimensions, "
        f"{arguments.text_length} text characters"
    )
    _print_result("Baseline", baseline)
    _print_result("Candidate", candidate)
    ratio = float(candidate["median_ms"]) / float(baseline["median_ms"])
    print(f"Candidate/baseline median ratio: {ratio:.2f}x")

    if arguments.output_json:
        Path(arguments.output_json).write_text(
            json.dumps(
                {
                    "payload": {
                        "num_documents": arguments.num_documents,
                        "vector_dimensions": arguments.vector_dimensions,
                        "text_length": arguments.text_length,
                    },
                    "baseline": baseline,
                    "candidate": candidate,
                    "median_ratio": ratio,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    return 0


def _worker(arguments: argparse.Namespace) -> int:
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    vector = [float(index % 10) / 10 for index in range(arguments.vector_dimensions)]
    content = "x" * arguments.text_length
    documents = [
        {
            "id": str(index),
            "content": content,
            "content_vector": vector,
            "category": "performance",
            "source": "synthetic",
        }
        for index in range(arguments.num_documents)
    ]
    client = SearchClient("https://localhost", "perf-index", AzureKeyCredential("perf-test-key"))

    with patch.object(SearchClient, "index_documents", return_value=[]):
        for _ in range(arguments.warmups):
            client.upload_documents(documents)

        timings = []
        for _ in range(arguments.repeats):
            start = time.perf_counter()
            client.upload_documents(documents)
            timings.append(time.perf_counter() - start)

    client.close()
    ordered = sorted(timings)
    p95_index = min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1)
    print(
        json.dumps(
            {
                "version": version("azure-search-documents"),
                "median_ms": statistics.median(timings) * 1000,
                "min_ms": min(timings) * 1000,
                "max_ms": max(timings) * 1000,
                "p95_ms": ordered[p95_index] * 1000,
                "repeats": arguments.repeats,
            }
        )
    )
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        default="azure-search-documents==11.6.0",
        help="Baseline pip requirement or package path.",
    )
    parser.add_argument(
        "--candidate",
        default=str(PACKAGE_ROOT),
        help="Candidate pip requirement or package path. Defaults to the current package checkout.",
    )
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--num-documents", type=int, default=100)
    parser.add_argument("--vector-dimensions", type=int, default=3072)
    parser.add_argument("--text-length", type=int, default=4000)
    parser.add_argument("--output-json", help="Optional path for machine-readable results.")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    if arguments.repeats < 1:
        parser.error("--repeats must be at least 1")
    if arguments.warmups < 0:
        parser.error("--warmups cannot be negative")
    if arguments.num_documents < 1:
        parser.error("--num-documents must be at least 1")
    if arguments.vector_dimensions < 0 or arguments.text_length < 0:
        parser.error("--vector-dimensions and --text-length cannot be negative")
    return arguments


if __name__ == "__main__":
    args = _parse_args()
    raise SystemExit(_worker(args) if args.worker else _controller(args))
