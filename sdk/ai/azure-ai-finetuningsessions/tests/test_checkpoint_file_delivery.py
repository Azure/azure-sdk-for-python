# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cspell:ignore IHHHHHH
"""Public download delivery through normal pipelines and offline raw streams."""

import asyncio
import os
import struct
from contextlib import asynccontextmanager

import pytest
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
    ServiceRequestError,
    ServiceResponseError,
)

from azure.ai.finetuningsessions import MalformedResponseError, _checkpoint_files

from .test_raw_request_polling import (
    DOWNLOAD_URL,
    AsyncResponse,
    Reply,
    Script,
    client_for,
    close_client,
    download_file,
    file_reply,
)


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def asynchronous(request):
    return request.param


@asynccontextmanager
async def delivery(asynchronous, *replies, files=None, **options):
    script = Script(
        Reply({"status": "Succeeded", "files": [download_file(size_bytes=3)] if files is None else files}),
        *replies,
    )
    instance = client_for(script, asynchronous, retry_total=5, **options)
    try:
        yield instance, script
    finally:
        await close_client(instance, asynchronous)
        assert all(response.is_closed for response in script.responses)


async def download(client, asynchronous, output, session="session_test", checkpoint="checkpoint_test"):
    result = client.checkpoints.download_weights(session, checkpoint, output)
    if asynchronous:
        result = await result
    assert result is None


def target(root):
    return root / "session_test" / "checkpoint_test"


def after_receive(monkeypatch, script, callback):
    receive = script.receive

    def wrapped(request, options):
        reply = receive(request, options)
        callback(request)
        return reply

    monkeypatch.setattr(script, "receive", wrapped)


@pytest.mark.parametrize("existing", [False, True], ids=["absent", "empty"])
async def test_complete_nested_tree_zero_bytes_and_unrelated_ancestors(asynchronous, tmp_path, existing):
    output = tmp_path / "output" / "deep"
    session = output / "model_test"
    session.mkdir(parents=True)
    (output / "unrelated.txt").write_bytes(b"keep-root")
    (session / "old").mkdir()
    (session / "old" / "weights.bin").write_bytes(b"keep-checkpoint")
    destination = session / "checkpoint_test"
    if existing:
        destination.mkdir()
    block = bytes(range(256)) * 16
    files = [
        download_file(filename="nested/weights%2f-1.bin", size_bytes=len(block) * 257),
        download_file("b" * 64, filename="nested/deeper/empty.bin", size_bytes=0, etag='""'),
        download_file("c" * 64, filename="config.json", size_bytes=3),
    ]
    async with delivery(
        asynchronous,
        Reply(
            b"",
            headers={"Content-Length": str(len(block) * 257), "ETag": '"file-v1"'},
            chunks=(block,) * 257,
        ),
        Reply(b"", headers={"Content-Length": "0", "ETag": '""'}, chunks=()),
        file_reply(b"cfg"),
        files=files,
    ) as (client, script):
        await download(client, asynchronous, output, session="model_test")
        assert {path.relative_to(destination).as_posix() for path in destination.rglob("*") if path.is_file()} == {
            "nested/weights%2f-1.bin",
            "nested/deeper/empty.bin",
            "config.json",
        }
        assert (destination / "nested" / "weights%2f-1.bin").read_bytes() == block * 257
        assert (destination / "nested" / "deeper" / "empty.bin").read_bytes() == b""
        assert (destination / "config.json").read_bytes() == b"cfg"
        assert (output / "unrelated.txt").read_bytes() == b"keep-root"
        assert (session / "old" / "weights.bin").read_bytes() == b"keep-checkpoint"
        assert [request["method"] for request in script.requests] == ["POST", "GET", "GET", "GET"]
        for request, file in zip(script.requests[1:], files):
            assert request["url"] == (DOWNLOAD_URL.partition("?")[0] + "/files/" + file["file_id"] + "?api-version=v1")
            assert request["headers"]["If-Match"] == file["etag"]
            assert request["headers"]["Accept"] == "application/octet-stream"
            assert request["headers"]["Accept-Encoding"] == "identity"
            assert request["options"]["stream"] is True
        assert not script.replies
        assert not script.delays


async def test_absent_root_is_created_only_after_valid_manifest(asynchronous, tmp_path):
    output = tmp_path / "missing" / "output"
    async with delivery(asynchronous, file_reply(b"abc")) as (client, _):
        await download(client, asynchronous, output)
    assert (target(output) / "nested" / "weights.bin").read_bytes() == b"abc"


@pytest.mark.parametrize("replace_at", [None, "POST", "GET"], ids=["stable", "during-preparation", "during-delivery"])
async def test_output_root_symlink_binding_is_preserved(asynchronous, tmp_path, monkeypatch, replace_at):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.bin").write_bytes(b"keep")
    link = tmp_path / "link"
    try:
        link.symlink_to(root, target_is_directory=True)
    except OSError as error:
        if getattr(error, "winerror", None) == 1314:
            pytest.skip("Windows symlink privilege is unavailable")
        raise
    async with delivery(asynchronous, file_reply(b"abc")) as (client, script):

        def replace_root(request):
            if request.method == replace_at:
                link.unlink()
                link.symlink_to(outside, target_is_directory=True)

        after_receive(monkeypatch, script, replace_root)
        if replace_at is None:
            await download(client, asynchronous, link)
            assert (target(root) / "nested" / "weights.bin").read_bytes() == b"abc"
        else:
            with pytest.raises(ValueError, match="output root changed"):
                await download(client, asynchronous, link)
            assert not (target(root) / "nested" / "weights.bin").exists()
        assert (outside / "keep.bin").read_bytes() == b"keep"
        assert list(outside.iterdir()) == [outside / "keep.bin"]


@pytest.mark.parametrize(
    "headers",
    [
        {"Content-Length": "3"},
        {"Content-Length": "3", "ETag": '"other"'},
        {"ETag": '"file-v1"'},
        {"Content-Length": "2", "ETag": '"file-v1"'},
        {"Content-Length": "-3", "ETag": '"file-v1"'},
        {"Content-Length": "3, 3", "ETag": '"file-v1"'},
        {"Content-Length": "3", "ETag": '"file-v1"', "Content-Encoding": "gzip"},
        {"Content-Length": "3", "ETag": '"file-v1"', "Content-Range": "bytes 0-2/3"},
    ],
)
async def test_file_identity_headers_fail_before_file_creation(asynchronous, tmp_path, headers):
    async with delivery(asynchronous, Reply(b"", headers=headers, chunks=(b"abc",))) as (client, script):
        with pytest.raises(MalformedResponseError, match="identity or headers"):
            await download(client, asynchronous, tmp_path)
        assert list(target(tmp_path).iterdir()) == []
        assert len(script.requests) == 2
        assert not script.delays


async def test_successful_file_response_cannot_change_url(asynchronous, tmp_path, monkeypatch):
    async with delivery(asynchronous, file_reply(b"abc")) as (client, script):
        after_receive(
            monkeypatch,
            script,
            lambda request: (
                setattr(request, "url", request.url.replace("unit.invalid", "other.invalid"))
                if request.method == "GET"
                else None
            ),
        )
        with pytest.raises(MalformedResponseError, match="identity or headers"):
            await download(client, asynchronous, tmp_path)
        assert list(target(tmp_path).iterdir()) == []


@pytest.mark.parametrize(
    "status,error",
    [
        (401, ClientAuthenticationError),
        (403, HttpResponseError),
        (404, ResourceNotFoundError),
        (412, HttpResponseError),
        (503, HttpResponseError),
        (206, HttpResponseError),
        (307, HttpResponseError),
    ],
)
async def test_non_success_is_not_buffered_retried_or_redirected(asynchronous, tmp_path, status, error):
    reply = Reply(
        b"",
        status=status,
        headers={"Location": "https://evil.invalid/weights", "Retry-After": "1000"},
        chunks=(AssertionError("Error body must not be consumed"),),
    )
    async with delivery(asynchronous, reply) as (client, script):
        with pytest.raises(error) as raised:
            await download(client, asynchronous, tmp_path)
        assert raised.value.status_code == status
        assert list(target(tmp_path).iterdir()) == []
        assert len(script.requests) == 2
        assert not script.delays


@pytest.mark.parametrize(
    "chunks,error,expected",
    [
        ((b"ab",), MalformedResponseError, b"ab"),
        ((b"ab", b"cd"), MalformedResponseError, b"ab"),
        ((b"ab", ServiceResponseError("offline interrupted stream")), ServiceResponseError, b"ab"),
    ],
)
async def test_incomplete_streams_retain_partial_output_and_do_not_resume(
    asynchronous, tmp_path, chunks, error, expected
):
    reply = Reply(b"", headers={"Content-Length": "3", "ETag": '"file-v1"'}, chunks=chunks)
    async with delivery(asynchronous, reply) as (client, script):
        with pytest.raises(error):
            await download(client, asynchronous, tmp_path)
        partial = target(tmp_path) / "nested" / "weights.bin"
        assert partial.read_bytes() == expected
        with pytest.raises(ValueError, match="must be empty"):
            await download(client, asynchronous, tmp_path)
        assert partial.read_bytes() == expected
        assert len(script.requests) == 2
        assert not script.delays
    # Windows would reject this rename if any directory/file handle leaked.
    target(tmp_path).rename(tmp_path / "retained")


async def test_partial_checkpoint_failure_preserves_completed_files(asynchronous, tmp_path):
    files = [download_file(filename="first.bin", size_bytes=3), download_file("b" * 64, size_bytes=3)]
    async with delivery(asynchronous, file_reply(b"abc"), Reply({}, status=412), files=files) as (client, script):
        with pytest.raises(HttpResponseError):
            await download(client, asynchronous, tmp_path)
        assert (target(tmp_path) / "first.bin").read_bytes() == b"abc"
        assert not (target(tmp_path) / "nested").exists()
        assert len(script.requests) == 3


async def test_get_transport_error_is_explicit_without_retries(asynchronous, tmp_path, monkeypatch):
    async with delivery(asynchronous, file_reply(b"abc")) as (client, script):

        def fail(request):
            if request.method == "GET":
                raise ServiceRequestError("offline connect failure")

        after_receive(monkeypatch, script, fail)
        with pytest.raises(ServiceRequestError, match="offline connect failure"):
            await download(client, asynchronous, tmp_path)
        assert len(script.requests) == 2
        assert not script.delays
        assert list(target(tmp_path).iterdir()) == []


async def test_destination_rechecked_after_preparation(asynchronous, tmp_path, monkeypatch):
    async with delivery(asynchronous) as (client, script):

        def add_user_file(_):
            target(tmp_path).mkdir(parents=True)
            (target(tmp_path) / "user.bin").write_bytes(b"keep")

        after_receive(monkeypatch, script, add_user_file)
        with pytest.raises(ValueError, match="must be empty"):
            await download(client, asynchronous, tmp_path)
        assert len(script.requests) == 1
        assert (target(tmp_path) / "user.bin").read_bytes() == b"keep"


@pytest.mark.parametrize("entry", ["file", "directory", "symlink"])
async def test_racing_entries_are_never_overwritten_or_adopted(asynchronous, tmp_path, monkeypatch, entry):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.bin").write_bytes(b"keep")
    filename = "nested/weights.bin" if entry != "file" else "weights.bin"
    async with delivery(asynchronous, file_reply(b"abc"), files=[download_file(filename=filename, size_bytes=3)]) as (
        client,
        script,
    ):

        def create_entry(request):
            if request.method != "GET":
                return
            destination = target(tmp_path) / ("weights.bin" if entry == "file" else "nested")
            if entry == "file":
                destination.write_bytes(b"keep")
            elif entry == "directory":
                destination.mkdir()
                (destination / "keep.bin").write_bytes(b"keep")
            else:
                try:
                    destination.symlink_to(outside, target_is_directory=True)
                except OSError as error:
                    if getattr(error, "winerror", None) == 1314:
                        pytest.skip("Windows symlink privilege is unavailable")
                    raise

        after_receive(monkeypatch, script, create_entry)
        with pytest.raises(FileExistsError):
            await download(client, asynchronous, tmp_path)
        assert (outside / "keep.bin").read_bytes() == b"keep"
        assert not (outside / "weights.bin").exists()
        if entry == "file":
            assert (target(tmp_path) / "weights.bin").read_bytes() == b"keep"
        elif entry == "directory":
            assert (target(tmp_path) / "nested" / "keep.bin").read_bytes() == b"keep"


async def test_final_inventory_does_not_silently_accept_external_files(asynchronous, tmp_path, monkeypatch):
    complete = _checkpoint_files._CheckpointOutput.complete

    def add_external(self):
        (self.path / "user.txt").write_bytes(b"keep")
        complete(self)

    monkeypatch.setattr(_checkpoint_files._CheckpointOutput, "complete", add_external)
    async with delivery(asynchronous, file_reply(b"abc")) as (client, _):
        with pytest.raises(ValueError, match="directory changed"):
            await download(client, asynchronous, tmp_path)
    assert (target(tmp_path) / "user.txt").read_bytes() == b"keep"
    assert (target(tmp_path) / "nested" / "weights.bin").read_bytes() == b"abc"


async def test_replaced_file_is_preserved_instead_of_deleted(asynchronous, tmp_path, monkeypatch):
    complete = _checkpoint_files._CheckpointOutput.complete

    def replace_file(self):
        replacement = tmp_path / "replacement"
        replacement.write_bytes(b"new")
        os.replace(replacement, self.path / "nested" / "weights.bin")
        complete(self)

    monkeypatch.setattr(_checkpoint_files._CheckpointOutput, "complete", replace_file)
    async with delivery(asynchronous, file_reply(b"abc")) as (client, _):
        with pytest.raises(ValueError, match="file changed"):
            await download(client, asynchronous, tmp_path)
    assert (target(tmp_path) / "nested" / "weights.bin").read_bytes() == b"new"


async def test_directory_replacement_cannot_redirect_writes(asynchronous, tmp_path, monkeypatch):
    original = _checkpoint_files._Directory.open_file
    moved = tmp_path / "moved"

    def race(self, name):
        if os.name == "nt":
            with pytest.raises(PermissionError):
                target(tmp_path).rename(moved)
        else:
            target(tmp_path).rename(moved)
            target(tmp_path).mkdir()
        return original(self, name)

    monkeypatch.setattr(_checkpoint_files._Directory, "open_file", race)
    async with delivery(asynchronous, file_reply(b"abc")) as (client, _):
        if os.name == "nt":
            await download(client, asynchronous, tmp_path)
            assert (target(tmp_path) / "nested" / "weights.bin").read_bytes() == b"abc"
        else:
            with pytest.raises(ValueError, match="directory changed"):
                await download(client, asynchronous, tmp_path)
            assert not list(target(tmp_path).iterdir())
    target(tmp_path).rename(tmp_path / "released")


def set_windows_junction(path, destination):
    import ctypes
    from ctypes import wintypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    create.restype = wintypes.HANDLE
    close = kernel.CloseHandle
    close.argtypes = [wintypes.HANDLE]
    close.restype = wintypes.BOOL
    ioctl = kernel.DeviceIoControl
    ioctl.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        wintypes.LPVOID,
    ]
    ioctl.restype = wintypes.BOOL
    handle = create(str(path), 0x40000000, 0x7, None, 3, 0x02200000, None)
    if handle == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        substitute = ("\\??\\" + str(destination)).encode("utf-16-le")
        printable = str(destination).encode("utf-16-le")
        names = substitute + b"\0\0" + printable + b"\0\0"
        data = (
            struct.pack(
                "<IHHHHHH", 0xA0000003, len(names) + 8, 0, 0, len(substitute), len(substitute) + 2, len(printable)
            )
            + names
        )
        buffer = ctypes.create_string_buffer(data)
        returned = wintypes.DWORD()
        if not ioctl(handle, 0x900A4, buffer, len(data), None, 0, ctypes.byref(returned), None):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        close(handle)


@pytest.mark.skipif(os.name != "nt", reason="Windows in-place junction race")
@pytest.mark.parametrize("creation", ["file", "directory"])
async def test_in_place_junction_cannot_redirect_creation(asynchronous, tmp_path, monkeypatch, creation):
    output = tmp_path / "output"
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.bin").write_bytes(b"keep")
    nested = target(output) / "nested"
    installed = False
    method = "open_file" if creation == "file" else "child"
    create = getattr(_checkpoint_files._Directory, method)

    def race(self, *args, **kwargs):
        if self.path != nested:
            return create(self, *args, **kwargs)
        verify = self.verify

        def reparse_after_verification():
            nonlocal installed
            verify()
            set_windows_junction(nested, outside)
            installed = True

        with monkeypatch.context() as context:
            context.setattr(self, "verify", reparse_after_verification)
            return create(self, *args, **kwargs)

    monkeypatch.setattr(_checkpoint_files._Directory, method, race)
    filename = "nested/weights.bin" if creation == "file" else "nested/deeper/weights.bin"
    try:
        async with delivery(
            asynchronous, file_reply(b"abc"), files=[download_file(filename=filename, size_bytes=3)]
        ) as (client, script):
            with pytest.raises((OSError, ValueError)):
                await download(client, asynchronous, output)
            assert installed
            assert len(script.requests) == 2
        assert list(outside.iterdir()) == [outside / "keep.bin"]
        assert (outside / "keep.bin").read_bytes() == b"keep"
    finally:
        if installed:
            nested.rmdir()
    target(output).rename(tmp_path / "released")


async def test_short_local_write_is_explicit_and_handles_close(asynchronous, tmp_path, monkeypatch):
    original = _checkpoint_files._Directory.open_file

    class ShortWrite:
        def __init__(self, stream):
            self.stream = stream

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.stream.close()

        def fileno(self):
            return self.stream.fileno()

        def write(self, data):
            return self.stream.write(data[:1])

    monkeypatch.setattr(_checkpoint_files._Directory, "open_file", lambda self, name: ShortWrite(original(self, name)))
    async with delivery(asynchronous, file_reply(b"abc")) as (client, _):
        with pytest.raises(OSError, match="Incomplete checkpoint file write"):
            await download(client, asynchronous, tmp_path)
    assert (target(tmp_path) / "nested" / "weights.bin").read_bytes() == b"a"
    target(tmp_path).rename(tmp_path / "released")


async def test_async_cancellation_closes_response_and_files_retaining_partial_output(tmp_path, monkeypatch):
    started = asyncio.Event()

    async def stream(self, **_):
        yield b"a"
        started.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(AsyncResponse, "iter_raw", stream)
    async with delivery(True, file_reply(b"abc")) as (client, script):
        task = asyncio.create_task(download(client, True, tmp_path))
        await asyncio.wait_for(started.wait(), timeout=5)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert script.responses[-1].is_closed
        assert (target(tmp_path) / "nested" / "weights.bin").read_bytes() == b"a"
        assert len(script.requests) == 2
    target(tmp_path).rename(tmp_path / "released")
