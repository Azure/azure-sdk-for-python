import asyncio
import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
TOOLS_ROOT = os.path.join(REPO_ROOT, "eng", "tools", "azure-sdk-tools")
if TOOLS_ROOT not in sys.path:
    sys.path.insert(0, TOOLS_ROOT)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from eng.scripts.dispatch_checks import _tee_stream, get_check_dest_dir


def _stream_with(data, limit=16):
    stream = asyncio.StreamReader(limit=limit)
    stream.feed_data(data)
    stream.feed_eof()
    return stream


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


@pytest.mark.asyncio
async def test_tee_stream_suppresses_over_limit_line_and_continues(capsys):
    proc = SimpleNamespace(
        stdout=_stream_with(b"line that is much too long\nnormal output\n"),
        stderr=None,
        wait=AsyncMock(),
    )

    stdout, stderr = await _tee_stream(proc, "package", "samples")

    assert stdout == "log line exceeded\nnormal output\n"
    assert stderr == ""
    assert capsys.readouterr().out == (
        "[package :: samples] log line exceeded\n"
        "[package :: samples] normal output\n"
    )


@pytest.mark.asyncio
async def test_tee_stream_suppresses_over_limit_line_at_eof(capsys):
    proc = SimpleNamespace(
        stdout=_stream_with(b"line that is much too long"),
        stderr=None,
        wait=AsyncMock(),
    )

    stdout, stderr = await _tee_stream(proc, "package", "samples")

    assert stdout == "log line exceeded\n"
    assert stderr == ""
    assert capsys.readouterr().out == "[package :: samples] log line exceeded\n"
