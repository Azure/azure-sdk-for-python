# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Resolve wildcard queries against the actual sync/async pytest sample collection."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import sys


@dataclass(frozen=True)
class SampleTest:
    node_id: str
    sample_path: str
    test_id: str


def normalize(value: str) -> str:
    """Use package-relative, forward-slash paths on Windows and Linux."""
    value = value.replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    prefix = "sdk/ai/azure-ai-projects/"
    if value.startswith(prefix):
        value = value[len(prefix) :]
    return value


def matches(value: str, pattern: str) -> bool:
    """Only * and ? are special; pytest parameter brackets remain literal."""
    expression = re.escape(normalize(pattern)).replace(r"\*", ".*").replace(r"\?", ".")
    return re.fullmatch(expression, normalize(value), flags=re.IGNORECASE) is not None


def select_tests(tests: list[SampleTest], selection_kind: str, query: str) -> list[SampleTest]:
    if selection_kind not in {"sample-path", "test-id"}:
        raise ValueError("Selection kind must be sample-path or test-id.")
    patterns = [pattern.strip() for pattern in re.split(r"[;\r\n]+", query) if pattern.strip()]
    if not patterns:
        raise ValueError("Supply a sample path or test ID wildcard; an empty query never selects all tests.")

    selected = {}
    for test in tests:
        candidates = [test.sample_path] if selection_kind == "sample-path" else [test.node_id, test.test_id]
        if any(matches(candidate, pattern) for candidate in candidates for pattern in patterns):
            selected[test.node_id] = test
    if not selected:
        raise ValueError(
            f"No collected sample tests match {selection_kind} query {query!r}. "
            "Use * or ? wildcards, not pytest -k expressions. Samples excluded by the harness are not selected."
        )
    return sorted(selected.values(), key=lambda test: test.node_id)


def partition_tests(tests: list[SampleTest], queue_count: int) -> dict[str, list[SampleTest]]:
    """Assign each selected case once, preserving manifest order within each queue."""
    if type(queue_count) is not int or not 1 <= queue_count <= 4:
        raise ValueError("Request one to four test queues.")
    if not tests or len({test.node_id for test in tests}) != len(tests):
        raise ValueError("Queue assignment requires a nonempty selection of unique test nodes.")
    active = min(queue_count, len(tests))
    return {f"q{index + 1}": tests[index::active] for index in range(active)}


class SampleCollector:
    def __init__(self, package_root: Path):
        self.package_root = package_root.resolve()
        self.tests: list[SampleTest] = []

    def pytest_collection_finish(self, session):
        for item in session.items:
            callspec = getattr(item, "callspec", None)
            sample_path = callspec.params.get("sample_path") if callspec is not None else None
            if not isinstance(sample_path, (str, os.PathLike)):
                continue
            path = Path(sample_path).resolve()
            try:
                relative_path = path.relative_to(self.package_root / "samples")
            except ValueError:
                continue
            self.tests.append(
                SampleTest(
                    node_id=normalize(item.nodeid),
                    sample_path=f"samples/{relative_path.as_posix()}",
                    test_id=str(callspec.id),
                )
            )


def collect_tests(package_root: Path) -> list[SampleTest]:
    # Collection must never inherit a developer's .env or execute a sample.
    os.environ["PYTHON_DOTENV_DISABLED"] = "true"
    import pytest  # pylint: disable=import-outside-toplevel

    collector = SampleCollector(package_root)
    arguments = [
        "--collect-only",
        "-q",
        f"--rootdir={package_root}",
        "--azure-test-run-live=false",
        "--azure-skip-live-recording=true",
        str(package_root / "tests/samples/test_samples.py"),
        str(package_root / "tests/samples/test_samples_async.py"),
    ]
    original_directory = Path.cwd()
    try:
        os.chdir(package_root)
        sys.path.insert(0, str(package_root))
        result = pytest.main(arguments, plugins=[collector])
    finally:
        os.chdir(original_directory)
    if result != pytest.ExitCode.OK:
        raise ValueError(
            f"Sample test collection failed (pytest exit code {int(result)}); no resources were provisioned."
        )
    return collector.tests


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection-kind", choices=["sample-path", "test-id"], required=True)
    parser.add_argument("--selection", required=True, help="* and ? wildcards; separate OR patterns with semicolons.")
    parser.add_argument("--package-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--queue-count", type=int, choices=range(1, 5), default=1)
    arguments = parser.parse_args()
    if arguments.output.exists() or any((arguments.output.parent / f"q{number}").exists() for number in range(1, 5)):
        parser.error("Use a fresh output directory; previous queue plans must not be reused or overwritten.")
    try:
        selected = select_tests(collect_tests(arguments.package_root), arguments.selection_kind, arguments.selection)
        queues = partition_tests(selected, arguments.queue_count)
    except ValueError as error:
        parser.error(str(error))

    manifest = {
        "schemaVersion": 1,
        "selectionKind": arguments.selection_kind,
        "selection": arguments.selection,
        "tests": [asdict(test) for test in selected],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    matrix = {}
    for queue, tests in queues.items():
        directory = arguments.output.parent / queue
        directory.mkdir()
        shard = {**manifest, "tests": [asdict(test) for test in tests]}
        (directory / "selected-tests.json").write_text(json.dumps(shard, indent=2) + "\n", encoding="utf-8")
        matrix[queue] = {"QueueName": queue}
        print(f"{queue}: {len(tests)} assigned sample test(s).")
    (arguments.output.parent / "queue-matrix.json").write_text(json.dumps(matrix) + "\n", encoding="utf-8")
    print(f"\nSelected {len(selected)} sample test(s):")
    for test in selected:
        print(f"  {test.sample_path}\n    {test.node_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
