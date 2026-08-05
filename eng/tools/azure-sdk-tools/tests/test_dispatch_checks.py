import asyncio
from io import StringIO
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
TOOLS_ROOT = os.path.join(REPO_ROOT, "eng", "tools", "azure-sdk-tools")
if TOOLS_ROOT not in sys.path:
    sys.path.insert(0, TOOLS_ROOT)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from eng.scripts.dispatch_checks import _tee_stream, get_check_dest_dir


def test_apistub_dest_dir_uses_package_subdirectory():
    package_dir = os.path.join(REPO_ROOT, "sdk", "core", "azure-core")
    artifact_dir = os.path.join(REPO_ROOT, "artifacts")

    with patch(
        "eng.scripts.dispatch_checks.ParsedSetup.from_path",
        return_value=SimpleNamespace(name="azure-core"),
    ):
        result = get_check_dest_dir(package_dir, "apistub", artifact_dir)

    assert result == os.path.join(artifact_dir, "azure-core")


def test_non_apistub_dest_dir_is_unchanged():
    package_dir = os.path.join(REPO_ROOT, "sdk", "core", "azure-core")
    artifact_dir = os.path.join(REPO_ROOT, "artifacts")

    with patch("eng.scripts.dispatch_checks.ParsedSetup.from_path") as parsed_setup:
        result = get_check_dest_dir(package_dir, "pylint", artifact_dir)

    assert result == artifact_dir
    parsed_setup.assert_not_called()


def test_empty_dest_dir_is_unchanged():
    package_dir = os.path.join(REPO_ROOT, "sdk", "core", "azure-core")

    with patch("eng.scripts.dispatch_checks.ParsedSetup.from_path") as parsed_setup:
        result = get_check_dest_dir(package_dir, "apistub", None)

    assert result is None
    parsed_setup.assert_not_called()


def test_tee_stream_suppresses_oversized_line():
    class Stream:
        def __init__(self):
            self.lines = [asyncio.LimitOverrunError("line is too long", 0), b"next line\n", b""]

        async def readline(self):
            line = self.lines.pop(0)
            if isinstance(line, Exception):
                raise line
            return line

    class Process:
        def __init__(self):
            self.stdout = Stream()
            self.stderr = Stream()

        async def wait(self):
            pass

    stdout_sink = StringIO()
    stderr_sink = StringIO()
    with patch("eng.scripts.dispatch_checks.sys.stdout", stdout_sink), patch(
        "eng.scripts.dispatch_checks.sys.stderr", stderr_sink
    ):
        stdout, stderr = asyncio.run(_tee_stream(Process(), "/tmp/package", "check"))

    assert stdout == "next line\n"
    assert stderr == "next line\n"
    assert stdout_sink.getvalue() == "[package :: check] [suppressed oversized log line]\n[package :: check] next line\n"
    assert stderr_sink.getvalue() == "[package :: check] [suppressed oversized log line]\n[package :: check] next line\n"
