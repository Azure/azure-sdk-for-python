# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Opt-in pytest plugin for sanitized sample log attachments in Azure DevOps JUnit results."""

from __future__ import annotations

from functools import wraps
import hashlib
import os
from pathlib import Path

import pytest

_ATTACHMENTS = pytest.StashKey[list[Path]]()


def sample_log_directory(node_id: str, directory: Path, executor_index: int = 0) -> Path:
    """Keep the executor's own log files isolated per pytest node and executor."""
    target = directory.resolve() / hashlib.sha256(node_id.encode("utf-8")).hexdigest()[:20] / str(executor_index)
    if any(character in str(target) for character in "\r\n|[]"):
        raise ValueError("The attachment directory cannot contain JUnit attachment-marker delimiters.")
    return target


def sample_attachment_paths(executors: list, directory: Path) -> list[Path]:
    """Attach the shared executor's already-sanitized logs without copying or reformatting them."""
    paths = [Path(path) for executor in executors for path in executor.write_capture_logs()]
    root = directory.resolve()
    if any(not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root) for path in paths):
        raise ValueError("Sample log files must remain within this run's attachment directory.")
    return paths


def pytest_addoption(parser):
    parser.getgroup("sample CI attachments").addoption(
        "--sample-attachments-dir", help="Publish sanitized live sample logs under this run's result directory."
    )


@pytest.fixture(autouse=True)
def _capture_sample_attachments(request, monkeypatch):
    directory = request.config.getoption("sample_attachments_dir")
    callspec = getattr(request.node, "callspec", None)
    if (
        not directory
        or os.environ.get("AZURE_TEST_RUN_LIVE") != "true"
        or not callspec
        or "sample_path" not in callspec.params
    ):
        yield
        return

    # Both sync and async executors inherit this constructor and its in-memory capture lists.
    # Patch only for this explicitly opted-in test; ordinary playback/live harness behavior is unchanged.
    from sample_executor import BaseSampleExecutor  # pylint: disable=import-outside-toplevel

    executors = []
    original_init = BaseSampleExecutor.__init__

    @wraps(original_init)
    def tracked_init(executor, *args, **kwargs):
        kwargs["log_directory"] = str(sample_log_directory(request.node.nodeid, Path(directory), len(executors)))
        original_init(executor, *args, **kwargs)
        executors.append(executor)

    monkeypatch.setattr(BaseSampleExecutor, "__init__", tracked_init)
    yield
    try:
        request.node.stash[_ATTACHMENTS] = sample_attachment_paths(executors, Path(directory))
    except Exception:  # pylint: disable=broad-exception-caught
        pytest.fail("Sample attachments could not be created; raw log content was suppressed.", pytrace=False)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if item.config.getoption("sample_attachments_dir"):
        from sample_log import sanitize_log  # pylint: disable=import-outside-toplevel

        # Test output is untrusted: only the paths appended below may become JUnit attachments.
        report.sections = [
            (name, sanitize_log(content).replace("[[ATTACHMENT|", "[[REDACTED-ATTACHMENT|"))
            for name, content in report.sections
        ]
        if report.failed and report.longrepr is not None:
            report.longrepr = sanitize_log(str(report.longrepr))
    if report.when == "teardown":
        paths = item.stash.get(_ATTACHMENTS, [])
        if paths:
            markers = "\n".join(f"[[ATTACHMENT|{path}]]" for path in paths)
            report.sections.append(("Captured stdout teardown", markers))
