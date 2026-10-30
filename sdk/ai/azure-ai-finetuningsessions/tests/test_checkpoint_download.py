# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Destination and private manifest validation, without network or file delivery."""

from __future__ import annotations

import hashlib
import inspect
import json
import runpy
from dataclasses import FrozenInstanceError
from pathlib import Path
from urllib.parse import urlencode
from unittest.mock import AsyncMock, Mock, patch

import pytest
from azure.core.rest import HttpRequest

from azure.ai.finetuningsessions import MalformedResponseError
from azure.ai.finetuningsessions._checkpoint_download import (
    _CheckpointDownloadFile,
    _checkpoint_download_result,
    _parse_checkpoint_download_manifest,
    _prepare_checkpoint_download,
    _prepare_checkpoint_download_async,
)
from azure.ai.finetuningsessions.aio.operations import (
    CheckpointsOperations as AsyncCheckpointsOperations,
)
from azure.ai.finetuningsessions.operations import CheckpointsOperations

from .test_raw_request_polling import (
    DOWNLOAD_URL,
    ENDPOINT,
    Reply,
    Script,
    SyncResponse,
    client_for,
    close_client,
    download_file,
)


@pytest.fixture(params=[False, True], ids=["sync", "async"])
async def client(request, monkeypatch):
    module = (
        "azure.ai.finetuningsessions.aio.operations._patch"
        if request.param
        else "azure.ai.finetuningsessions.operations._patch"
    )
    prepare = "_prepare_checkpoint_download_async" if request.param else "_prepare_checkpoint_download"
    monkeypatch.setattr(
        f"{module}.{prepare}", AsyncMock(return_value=None) if request.param else Mock(return_value=None)
    )
    script = Script()
    instance = client_for(script, request.param)
    try:
        yield instance
    finally:
        await close_client(instance, request.param)
        assert script.requests == []


async def _download(client, output_path, session_id="session_test", checkpoint_id="checkpoint-1"):
    result = client.checkpoints.download_weights(session_id, checkpoint_id, output_path)
    if inspect.isawaitable(result):
        result = await result
    assert result is None


async def test_absent_output_root_is_not_created(client, tmp_path):
    output = tmp_path / "absent" / "output"
    await _download(client, str(output))
    assert list(tmp_path.iterdir()) == []


async def test_only_target_checkpoint_must_be_empty(client, tmp_path, monkeypatch):
    (tmp_path / "unrelated.txt").write_text("keep")
    session = tmp_path / "session_test"
    session.mkdir()
    (session / "unrelated.txt").write_text("keep")
    (session / "checkpoint-previous").mkdir()
    (session / "checkpoint-previous" / "weights.bin").write_bytes(b"keep")
    (session / "checkpoint-1").mkdir()
    (tmp_path / "other-session").mkdir()
    (tmp_path / "other-session" / "checkpoint-1").mkdir()
    (tmp_path / "other-session" / "checkpoint-1" / "weights.bin").write_bytes(b"other")

    def snapshot():
        return {p.relative_to(tmp_path): p.read_bytes() if p.is_file() else None for p in tmp_path.rglob("*")}

    before = snapshot()
    monkeypatch.chdir(tmp_path)
    await _download(client, Path("."))
    await _download(client, tmp_path, checkpoint_id="checkpoint-2")
    await _download(client, tmp_path, session_id="session_other")
    assert snapshot() == before


@pytest.mark.parametrize("session_id", ["model_legacy", "bare-id"])
async def test_session_identifier_is_not_normalized(client, tmp_path, session_id):
    checkpoint = tmp_path / session_id / "checkpoint-1"
    checkpoint.mkdir(parents=True)
    (checkpoint / "weights.bin").write_bytes(b"keep")
    with pytest.raises(ValueError, match="Checkpoint directory must be empty"):
        await _download(client, tmp_path, session_id=session_id)


@pytest.mark.parametrize("entry", ["file", "directory"])
async def test_nonempty_checkpoint_is_rejected(client, tmp_path, entry):
    checkpoint = tmp_path / "session_test" / "checkpoint-1"
    checkpoint.mkdir(parents=True)
    if entry == "file":
        (checkpoint / ".hidden").touch()
    else:
        (checkpoint / "nested").mkdir()
    with pytest.raises(ValueError, match="Checkpoint directory must be empty"):
        await _download(client, tmp_path)


@pytest.mark.parametrize("level", ["ancestor", "root", "session", "checkpoint"])
async def test_file_in_place_of_directory_is_rejected(client, tmp_path, level):
    output = tmp_path / "output"
    file = {
        "ancestor": output,
        "root": output,
        "session": output / "session_test",
        "checkpoint": output / "session_test" / "checkpoint-1",
    }[level]
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_bytes(b"keep")
    with pytest.raises(NotADirectoryError):
        await _download(client, output / "nested" if level == "ancestor" else output)
    assert file.read_bytes() == b"keep"


@pytest.mark.parametrize("name", ["session_id", "checkpoint_id"])
async def test_unsafe_identifier_is_rejected(client, tmp_path, name):
    for value in (
        "",
        ".",
        "..",
        "../escape",
        r"..\escape",
        "/absolute",
        r"C:\absolute",
        "C:relative",
        r"\\server\share",
        "CON.txt",
        "CONIN$",
        "COM\u00b9",
        "LPT1",
        "trailing.",
        "trailing ",
        "a\0b",
        "a\nb",
        "a*b",
    ):
        with pytest.raises(ValueError, match=f"{name} must be a single portable directory name"):
            await _download(client, tmp_path, **{name: value})
    for value in (None, 42):
        with pytest.raises(TypeError, match=f"{name} must be a string"):
            await _download(client, tmp_path, **{name: value})
    assert list(tmp_path.iterdir()) == []


async def test_invalid_output_type_is_rejected(client):
    with pytest.raises(TypeError):
        await _download(client, None)


@pytest.mark.parametrize("level", ["session", "checkpoint"])
async def test_symlink_cannot_escape_output_root(client, tmp_path, level):
    output = tmp_path / "output"
    output.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    link = output / "session_test"
    if level == "checkpoint":
        link.mkdir()
        link = link / "checkpoint-1"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as error:
        if getattr(error, "winerror", None) == 1314:
            pytest.skip("Windows symlink privilege is unavailable")
        raise
    with pytest.raises(ValueError, match="must remain within output_path"):
        await _download(client, output)
    assert list(outside.iterdir()) == []


async def test_filesystem_errors_propagate(client, tmp_path):
    error = PermissionError("fixture permission denied")
    with patch.object(Path, "stat", side_effect=error), pytest.raises(PermissionError) as raised:
        await _download(client, tmp_path)
    assert raised.value is error


def test_sync_async_public_shape_matches():
    sync = CheckpointsOperations.download_weights
    asynchronous = AsyncCheckpointsOperations.download_weights
    assert inspect.signature(sync) == inspect.signature(asynchronous)
    assert list(inspect.signature(sync).parameters) == ["self", "session_id", "checkpoint_id", "output_path"]
    assert inspect.signature(sync).return_annotation is None
    assert not inspect.iscoroutinefunction(sync)
    assert inspect.iscoroutinefunction(asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "endpoint,version",
    [
        (ENDPOINT + "%20name", "preview+v1&test/?:# %\u00e9"),
        (
            "https://unit.invalid:443/subscriptions/sub/resourceGroups/rg/providers/"
            "Microsoft.CognitiveServices/accounts/account",
            "v1",
        ),
        (
            "https://unit.invalid/loom/v1.0/subscriptions/sub/resourceGroups/rg/providers/"
            "Microsoft.MachineLearningServices/workspaces/account@project@AML",
            "",
        ),
    ],
)
async def test_preparation_returns_complete_immutable_private_manifest(asynchronous, endpoint, version):
    files = [
        download_file(filename="nested/weights%2f-1.bin", api_version=version, size_bytes=2**80),
        download_file("b" * 64, filename="nested/deeper/\u00e9-2.bin", api_version=version, size_bytes=0, etag='""'),
        download_file("c" * 64, filename="config.json", api_version=version, etag='"\x80\xff"'),
    ]
    script = Script(
        Reply({"status": "Pending", "files": [{}]}, status=202),
        Reply({"status": "Succeeded", "files": files}),
    )
    instance = client_for(script, asynchronous, endpoint=endpoint, api_version=version)
    try:
        with (
            patch.object(Path, "mkdir", side_effect=AssertionError("mkdir")),
            patch.object(Path, "open", side_effect=AssertionError("open")),
        ):
            manifest = (
                await _prepare_checkpoint_download_async(instance.checkpoints, "model_test", "checkpoint_test")
                if asynchronous
                else _prepare_checkpoint_download(instance.checkpoints, "model_test", "checkpoint_test")
            )
        file_prefix = endpoint + "/fine_tuning_sessions/session_test/checkpoints/checkpoint_test/download/files/"
        version_query = "?" + urlencode({"api-version": version})
        assert manifest == tuple(
            _CheckpointDownloadFile(
                file["file_id"],
                file["filename"],
                file["size_bytes"],
                file["etag"],
                file_prefix + file["file_id"] + version_query,
            )
            for file in files
        )
        assert isinstance(manifest, tuple)
        with pytest.raises(FrozenInstanceError):
            manifest[0].filename = "changed"
        assert [request["method"] for request in script.requests] == ["POST", "POST"]
        assert all(request["body"] is None for request in script.requests)
        assert not script.replies
    finally:
        await close_client(instance, asynchronous)


_INVALID_FILE_FIELDS = [
    *[("file_id", value) for value in (None, 42, "a" * 63, "A" * 64, "../file")],
    *[
        ("filename", value)
        for value in (
            None,
            "",
            "/absolute",
            "C:relative",
            "a//b",
            "a/../b",
            r"a\b",
            "a/CON.txt",
            "a/x:y",
            "a/x.",
            "a/x ",
            "a/\nb",
            "a/\x7fb",
            "a/\ud800",
        )
    ],
    *[("size_bytes", value) for value in (None, True, -1, 1.0, "1")],
    *[("etag", value) for value in (None, "*", 'W/"v1"', "v1", '"v1", "v2"', '"x\ny"', '"\u0100"')],
]


@pytest.mark.parametrize("field,value", _INVALID_FILE_FIELDS)
def test_malformed_file_metadata_is_rejected(field, value):
    _assert_invalid_manifest([download_file(**{field: value})])


@pytest.mark.parametrize("field", ["file_id", "filename", "size_bytes", "etag", "download_url"])
def test_missing_metadata_field_is_not_skipped(field):
    file = download_file()
    del file[field]
    _assert_invalid_manifest([file])


@pytest.mark.parametrize("files", [None, [], {}, [None]])
def test_success_requires_a_nonempty_list_of_file_objects(files):
    _assert_invalid_manifest(files)


@pytest.mark.parametrize(
    "filenames",
    [
        ("weights.bin", "weights.bin"),
        ("Weights.bin", "weights.BIN"),
        ("\u00e9.bin", "e\u0301.bin"),
        ("I.bin", "\u0131.bin"),
        ("ss.bin", "\u00df.bin"),
        ("nested", "nested/weights.bin"),
        ("nested/weights.bin", "nested"),
        ("Nested/a.bin", "nested/b.bin"),
        ("\u00e9/a.bin", "e\u0301/b.bin"),
    ],
)
def test_local_aliases_duplicates_and_file_directory_conflicts_fail(filenames):
    _assert_invalid_manifest([download_file(filename=filenames[0]), download_file("b" * 64, filename=filenames[1])])


def test_duplicate_opaque_id_cannot_be_renamed_into_another_file():
    _assert_invalid_manifest([download_file(filename="first.bin"), download_file(filename="second.bin")])


_FILE_LOCATOR = "download/files/" + "a" * 64
_INVALID_LOCATORS = [
    None,
    _FILE_LOCATOR,
    _FILE_LOCATOR + "?api-version=v2",
    _FILE_LOCATOR + "?api-version=v1&sig=secret",
    _FILE_LOCATOR + "?api-version=v1&api-version=v1",
    _FILE_LOCATOR + "?api-version=v1#fragment",
    "../" + _FILE_LOCATOR + "?api-version=v1",
    "download/files/" + "b" * 64 + "?api-version=v1",
    DOWNLOAD_URL.replace("/download?", "/download/files/" + "a" * 64 + "?"),
    "//evil.invalid/path",
    "http://unit.invalid/path",
    "https://evil.invalid/path",
    "file:///weights",
    "download/files/%2e%2e?api-version=v1",
    "download%2ffiles/" + "a" * 64 + "?api-version=v1",
    "download/files/%61" + "a" * 63 + "?api-version=v1",
    "/fine_tuning_sessions/session_other/checkpoints/checkpoint_test/" + _FILE_LOCATOR + "?api-version=v1",
    "/fine_tuning_sessions/session_test/checkpoints/other/" + _FILE_LOCATOR + "?api-version=v1",
]


@pytest.mark.parametrize("locator", _INVALID_LOCATORS)
def test_only_current_api_request_relative_locators_are_accepted(locator):
    _assert_invalid_manifest([download_file(download_url=locator)])


def _assert_invalid_manifest(files):
    with pytest.raises(ValueError):
        _parse_checkpoint_download_manifest(files, DOWNLOAD_URL)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_invalid_last_file_fails_the_whole_public_download_without_writes(asynchronous, tmp_path):
    files = [download_file(filename="valid.bin"), download_file("b" * 64, filename="../escape")]
    script = Script(Reply({"status": "Succeeded", "files": files}))
    instance = client_for(script, asynchronous)
    try:
        with pytest.raises(MalformedResponseError, match="Invalid checkpoint download manifest:") as raised:
            with (
                patch.object(Path, "mkdir", side_effect=AssertionError("mkdir")),
                patch.object(Path, "open", side_effect=AssertionError("open")),
            ):
                await _download(instance, tmp_path, checkpoint_id="checkpoint_test")
        assert raised.value.response.status_code == 200
        assert raised.value.response.request.url == DOWNLOAD_URL
        assert [request["method"] for request in script.requests] == ["POST"]
        assert not script.replies
        assert not script.delays
        assert list(tmp_path.iterdir()) == []
    finally:
        await close_client(instance, asynchronous)


@pytest.mark.parametrize(
    "changed_url",
    [
        DOWNLOAD_URL.replace("unit.invalid", "backend.invalid"),
        DOWNLOAD_URL.replace("/api/projects/p", "/api/projects/other"),
    ],
)
def test_manifest_cannot_adopt_a_different_successful_request_location(changed_url):
    response = SyncResponse(
        HttpRequest("POST", changed_url), Reply({"status": "Succeeded", "files": [download_file()]})
    )
    with pytest.raises(MalformedResponseError, match="successful preparation URL changed") as raised:
        _checkpoint_download_result(response, "session_test", DOWNLOAD_URL)
    assert raised.value.response is response


def test_maintained_download_runtime_matches_provenance():
    package = Path(__file__).resolve().parents[1]
    verifier = runpy.run_path(str(package / "scripts" / "verify_generation.py"))
    for module in ("_checkpoint_download.py", "_text_only.py", "models/_text_only.py"):
        assert module in verifier["HANDWRITTEN_MODULES"]
        assert module in verifier["MAINTAINED_MODULES"]
        assert all(not name.endswith(f"/{module}") for name in verifier["generated_files"](package))
    assembly = json.loads((package / "eng" / "generation" / "provenance.json").read_text(encoding="utf-8"))["assembly"]
    runtime = verifier["package_hashes"](package)
    assert assembly["runtime_files"] == len(runtime)
    assert assembly["runtime_python_modules"] == sum(name.endswith(".py") for name in runtime)
    fingerprint = hashlib.sha256(json.dumps(runtime, sort_keys=True).encode()).hexdigest()
    assert assembly["runtime_fingerprint_sha256"] == fingerprint
    assert set(assembly["maintained_modules"]) == verifier["MAINTAINED_MODULES"]
