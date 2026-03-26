import os
import subprocess
from pathlib import Path
import json
import builtins
import io
import base64
import zipfile

import pytest
from azure.core.exceptions import AzureError

from azure.ai.ml.exceptions import JobException, MlException

import azure.ai.ml.operations._local_job_invoker as local_job_invoker
from azure.ai.ml.operations._local_job_invoker import _get_creationflags_and_startupinfo_for_background_process, _log_subprocess, patch_invocation_script_serialization, LOCAL_JOB_FAILURE_MSG, start_run_if_local, AZUREML_RUN_SETUP_DIR, CommonRuntimeHelper


def test_get_creationflags_and_startupinfo_for_background_process_windows(monkeypatch):
    # On non-Windows platforms, subprocess may not expose Windows-specific attributes.
    # Patch them in so that the Windows-specific code path can be exercised.
    if not hasattr(local_job_invoker.subprocess, "STARTUPINFO"):
        class DummyStartupInfo:
            def __init__(self):
                self.dwFlags = 0
                self.wShowWindow = 0

        monkeypatch.setattr(local_job_invoker.subprocess, "STARTUPINFO", DummyStartupInfo, raising=False)

    if not hasattr(local_job_invoker.subprocess, "STARTF_USESHOWWINDOW"):
        monkeypatch.setattr(local_job_invoker.subprocess, "STARTF_USESHOWWINDOW", 1, raising=False)

    if not hasattr(local_job_invoker.subprocess, "SW_HIDE"):
        monkeypatch.setattr(local_job_invoker.subprocess, "SW_HIDE", 0, raising=False)

    result = _get_creationflags_and_startupinfo_for_background_process(os_override="nt")

    assert "creationflags" in result
    assert "startupinfo" in result
    assert "stdin" not in result
    assert "stdout" not in result
    assert "stderr" not in result


def test_get_creationflags_and_startupinfo_for_background_process_non_windows():
    result = _get_creationflags_and_startupinfo_for_background_process(os_override="posix")

    assert result["stdin"] is subprocess.DEVNULL
    assert result["stdout"] is subprocess.DEVNULL
    assert result["stderr"] is subprocess.STDOUT
    # ensure that keys with None values are filtered out
    assert "creationflags" not in result
    assert "startupinfo" not in result


def test_invoke_command_windows_uses_cmd_and_patches_invocation_script(monkeypatch, tmp_path):
    # On non-Windows platforms, subprocess may not expose Windows-specific attributes.
    # Patch them in so that the Windows-specific code path can be exercised when invoke_command
    # calls _get_creationflags_and_startupinfo_for_background_process without an os_override.
    if not hasattr(local_job_invoker.subprocess, "STARTUPINFO"):
        class DummyStartupInfo:
            def __init__(self):
                self.dwFlags = 0
                self.wShowWindow = 0

        monkeypatch.setattr(local_job_invoker.subprocess, "STARTUPINFO", DummyStartupInfo, raising=False)

    if not hasattr(local_job_invoker.subprocess, "STARTF_USESHOWWINDOW"):
        monkeypatch.setattr(local_job_invoker.subprocess, "STARTF_USESHOWWINDOW", 1, raising=False)

    if not hasattr(local_job_invoker.subprocess, "SW_HIDE"):
        monkeypatch.setattr(local_job_invoker.subprocess, "SW_HIDE", 0, raising=False)

    original_os_name = local_job_invoker.os.name
    monkeypatch.setattr(local_job_invoker.os, "name", "nt", raising=False)

    patched_paths = []

    def fake_patch_invocation_script_serialization(invocation_path):
        patched_paths.append(invocation_path)

    monkeypatch.setattr(
        local_job_invoker,
        "patch_invocation_script_serialization",
        fake_patch_invocation_script_serialization,
    )

    popen_calls = []

    class DummyPopen:
        def __init__(self, *args, **kwargs):
            popen_calls.append((args, kwargs))

    monkeypatch.setattr(local_job_invoker.subprocess, "Popen", DummyPopen)

    invocation_dir = tmp_path / local_job_invoker.AZUREML_RUN_SETUP_DIR
    invocation_dir.mkdir(parents=True, exist_ok=True)

    invocation_script_path = invocation_dir / local_job_invoker.INVOCATION_BAT_FILE
    invocation_script_path.write_text("echo test")

    try:
        local_job_invoker.invoke_command(tmp_path)
    finally:
        monkeypatch.setattr(local_job_invoker.os, "name", original_os_name, raising=False)

    assert patched_paths[0] == invocation_script_path
    assert len(popen_calls) == 1
    args, kwargs = popen_calls[0]
    invoked_command = args[0]
    assert invoked_command[0] == "cmd.exe"
    assert invoked_command[1] == "/c"
    assert str(invocation_script_path) in invoked_command[2]
    assert kwargs["cwd"] == tmp_path
    assert "env" in kwargs


def test_get_creationflags_and_startupinfo_for_background_process_windows_extra(monkeypatch):
    # Ensure Windows-specific flags and startupinfo structure are set correctly.
    if not hasattr(local_job_invoker.subprocess, "STARTUPINFO"):
        class DummyStartupInfo:
            def __init__(self):
                self.dwFlags = 0
                self.wShowWindow = 0

        monkeypatch.setattr(local_job_invoker.subprocess, "STARTUPINFO", DummyStartupInfo, raising=False)

    if not hasattr(local_job_invoker.subprocess, "STARTF_USESHOWWINDOW"):
        monkeypatch.setattr(local_job_invoker.subprocess, "STARTF_USESHOWWINDOW", 1, raising=False)

    if not hasattr(local_job_invoker.subprocess, "SW_HIDE"):
        monkeypatch.setattr(local_job_invoker.subprocess, "SW_HIDE", 0, raising=False)

    if not hasattr(local_job_invoker.subprocess, "CREATE_NEW_CONSOLE"):
        monkeypatch.setattr(local_job_invoker.subprocess, "CREATE_NEW_CONSOLE", 0x00000010, raising=False)

    result = local_job_invoker._get_creationflags_and_startupinfo_for_background_process(os_override="nt")

    assert "creationflags" in result
    assert isinstance(result["creationflags"], int)
    assert result["creationflags"] == 0x00000010
    assert "startupinfo" in result
    assert hasattr(result["startupinfo"], "dwFlags")
    assert hasattr(result["startupinfo"], "wShowWindow")
    assert "stdin" not in result
    assert "stdout" not in result
    assert "stderr" not in result
    assert "shell" not in result


def test_get_creationflags_and_startupinfo_for_background_process_non_windows_extra():
    result = local_job_invoker._get_creationflags_and_startupinfo_for_background_process(os_override="posix")

    assert "stdin" in result
    assert "stdout" in result
    assert "stderr" in result
    assert result["stdin"] is subprocess.DEVNULL
    assert result["stdout"] is subprocess.DEVNULL
    assert result["stderr"] is subprocess.STDOUT
    assert "startupinfo" not in result
    assert "creationflags" not in result
    assert "shell" not in result


def test_invoke_command_windows_uses_cmd_and_patches_invocation_script_extra(tmp_path, monkeypatch):
    # Ensure invoke_command uses cmd.exe and patches the invocation script on Windows.
    if not hasattr(local_job_invoker.subprocess, "STARTUPINFO"):
        class DummyStartupInfo:
            def __init__(self):
                self.dwFlags = 0
                self.wShowWindow = 0

        monkeypatch.setattr(local_job_invoker.subprocess, "STARTUPINFO", DummyStartupInfo, raising=False)

    if not hasattr(local_job_invoker.subprocess, "STARTF_USESHOWWINDOW"):
        monkeypatch.setattr(local_job_invoker.subprocess, "STARTF_USESHOWWINDOW", 1, raising=False)

    if not hasattr(local_job_invoker.subprocess, "SW_HIDE"):
        monkeypatch.setattr(local_job_invoker.subprocess, "SW_HIDE", 0, raising=False)

    original_os_name = local_job_invoker.os.name
    monkeypatch.setattr(local_job_invoker.os, "name", "nt", raising=False)

    run_setup_dir = tmp_path / local_job_invoker.AZUREML_RUN_SETUP_DIR
    run_setup_dir.mkdir(parents=True)
    invocation_script = run_setup_dir / local_job_invoker.INVOCATION_BAT_FILE
    invocation_script.write_text("echo test")

    patched_paths = []

    def fake_patch_invocation_script_serialization(path: Path) -> None:
        patched_paths.append(path)

    monkeypatch.setattr(
        local_job_invoker,
        "patch_invocation_script_serialization",
        fake_patch_invocation_script_serialization,
    )

    popen_args = {}

    class FakePopen:
        def __init__(self, cmd, cwd=None, env=None, **kwargs):  # pylint: disable=unused-argument
            popen_args["cmd"] = cmd
            popen_args["cwd"] = cwd
            popen_args["env"] = env

    monkeypatch.setattr(local_job_invoker.subprocess, "Popen", FakePopen)

    try:
        local_job_invoker.invoke_command(tmp_path)
    finally:
        monkeypatch.setattr(local_job_invoker.os, "name", original_os_name, raising=False)

    assert patched_paths[0] == invocation_script
    assert popen_args["cmd"][0] == "cmd.exe"
    assert popen_args["cmd"][1] == "/c"
    assert str(invocation_script) in popen_args["cmd"][2]
    assert popen_args["cwd"] == tmp_path
    assert "AZUREML_TARGET_TYPE" not in popen_args["env"]


def test_invoke_command_non_windows_uses_bash_and_chmod(tmp_path, monkeypatch):
    original_os_name = local_job_invoker.os.name
    monkeypatch.setattr(local_job_invoker.os, "name", "posix", raising=False)

    run_setup_dir = tmp_path / local_job_invoker.AZUREML_RUN_SETUP_DIR
    run_setup_dir.mkdir(parents=True)
    invocation_script = run_setup_dir / local_job_invoker.INVOCATION_BASH_FILE
    invocation_script.write_text("echo test")

    chmod_calls = []

    def fake_check_output(cmd, **kwargs):  # pylint: disable=unused-argument
        chmod_calls.append(cmd)

    monkeypatch.setattr(local_job_invoker.subprocess, "check_output", fake_check_output)

    popen_args = {}

    class FakePopen:
        def __init__(self, cmd, cwd=None, env=None, **kwargs):  # pylint: disable=unused-argument
            popen_args["cmd"] = cmd
            popen_args["cwd"] = cwd
            popen_args["env"] = env

    monkeypatch.setattr(local_job_invoker.subprocess, "Popen", FakePopen)

    env_backup = os.environ.get("AZUREML_TARGET_TYPE")
    os.environ["AZUREML_TARGET_TYPE"] = "some_value"

    try:
        local_job_invoker.invoke_command(tmp_path)
    finally:
        if env_backup is None:
            os.environ.pop("AZUREML_TARGET_TYPE", None)
        else:
            os.environ["AZUREML_TARGET_TYPE"] = env_backup
        monkeypatch.setattr(local_job_invoker.os, "name", original_os_name, raising=False)

    assert chmod_calls[0][0] == "chmod"
    assert chmod_calls[0][1] == "+x"
    assert chmod_calls[0][2] == invocation_script
    assert popen_args["cmd"][0] == "/bin/bash"
    assert popen_args["cmd"][1] == "-c"
    assert str(invocation_script) in popen_args["cmd"][2]
    assert popen_args["cwd"] == tmp_path
    assert "AZUREML_TARGET_TYPE" not in popen_args["env"]


class _FakeLocalService:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint


class _FakeProperties:
    def __init__(self, services):
        self.services = services


class _FakeJobDefinition:
    def __init__(self, endpoint: str = ""):
        services = {"Local": _FakeLocalService(endpoint)} if endpoint is not None else None
        self.properties = _FakeProperties(services)


class _FakeResponse:
    def __init__(self, content: bytes, raise_exc: Exception | None = None):
        self.content = content
        self._raise_exc = raise_exc

    def raise_for_status(self):
        if self._raise_exc is not None:
            raise self._raise_exc


class _FakePipeline:
    def __init__(self, response: _FakeResponse | None = None, error: Exception | None = None):
        self._response = response
        self._error = error

    def post(self, url, json=None, headers=None):  # pylint: disable=unused-argument
        if self._error is not None:
            raise self._error
        return self._response


def _build_endpoint_with_snapshot(snapshot_id: str) -> str:
    body = json.dumps({"SnapshotId": snapshot_id})
    encoded = local_job_invoker.urllib.parse.quote_plus(body)
    return "https://example.com/path?param=value" + local_job_invoker.EXECUTION_SERVICE_URL_KEY + encoded


def test_get_execution_service_response_azure_error_raises_system_exit():
    endpoint = _build_endpoint_with_snapshot("snap-1")
    job_def = _FakeJobDefinition(endpoint=endpoint)

    pipeline = _FakePipeline(error=AzureError("network failure"))

    with pytest.raises(SystemExit) as exc_info:
        local_job_invoker.get_execution_service_response(job_def, "token", pipeline)  # type: ignore[arg-type]

    assert isinstance(exc_info.value, SystemExit)


def test_get_execution_service_response_other_error_raises_jobexception():
    endpoint = _build_endpoint_with_snapshot("snap-2")
    job_def = _FakeJobDefinition(endpoint=endpoint)

    response = _FakeResponse(b"content", raise_exc=Exception("bad status"))
    pipeline = _FakePipeline(response=response)

    with pytest.raises(JobException) as exc_info:
        local_job_invoker.get_execution_service_response(job_def, "token", pipeline)  # type: ignore[arg-type]

    assert "Failed to read in local executable job" in str(exc_info.value)


def test_is_local_run_with_no_services_returns_false():
    job_def = _FakeJobDefinition(endpoint="")
    job_def.properties.services = None

    assert local_job_invoker.is_local_run(job_def) is False  # type: ignore[arg-type]


def test_is_local_run_with_local_endpoint_without_key_returns_false():
    endpoint = "https://example.com/path"
    job_def = _FakeJobDefinition(endpoint=endpoint)

    assert local_job_invoker.is_local_run(job_def) is False  # type: ignore[arg-type]


def test_is_local_run_with_local_endpoint_with_key_returns_true():
    endpoint = _build_endpoint_with_snapshot("snap-3")
    job_def = _FakeJobDefinition(endpoint=endpoint)

    assert local_job_invoker.is_local_run(job_def) is True  # type: ignore[arg-type]


class _FakeToken:
    def __init__(self, token: str):
        self.token = token


class _FakeCredential:
    def __init__(self, token: str = "test-token"):
        self._token = token

    def get_token(self, scope: str):  # pylint: disable=unused-argument
        return _FakeToken(self._token)


def test_start_run_if_local_success_returns_snapshot_id(monkeypatch, tmp_path):
    job_def = _FakeJobDefinition(endpoint=_build_endpoint_with_snapshot("snap-success"))
    credential = _FakeCredential()

    def fake_get_execution_service_response(job_definition, token, requests_pipeline):  # pylint: disable=unused-argument
        return b"zip-content", "snapshot-123"

    def fake_unzip_to_temporary_file(job_definition, zip_content):  # pylint: disable=unused-argument
        return tmp_path

    invoked = {"called": False}

    def fake_invoke_command(project_temp_dir):  # pylint: disable=unused-argument
        invoked["called"] = True

    monkeypatch.setattr(local_job_invoker, "get_execution_service_response", fake_get_execution_service_response)
    monkeypatch.setattr(local_job_invoker, "unzip_to_temporary_file", fake_unzip_to_temporary_file)
    monkeypatch.setattr(local_job_invoker, "invoke_command", fake_invoke_command)

    snapshot_id = local_job_invoker.start_run_if_local(job_def, credential, "https://base", None)  # type: ignore[arg-type]

    assert snapshot_id == "snapshot-123"
    assert invoked["called"] is True


def test_start_run_if_local_failure_wraps_exception_in_mlexception(monkeypatch, tmp_path):
    job_def = _FakeJobDefinition(endpoint=_build_endpoint_with_snapshot("snap-fail"))
    credential = _FakeCredential()

    def fake_get_execution_service_response(job_definition, token, requests_pipeline):  # pylint: disable=unused-argument
        return b"zip-content", "snapshot-err"

    def fake_unzip_to_temporary_file(job_definition, zip_content):  # pylint: disable=unused-argument
        raise RuntimeError("unzip failed")

    monkeypatch.setattr(local_job_invoker, "get_execution_service_response", fake_get_execution_service_response)
    monkeypatch.setattr(local_job_invoker, "unzip_to_temporary_file", fake_unzip_to_temporary_file)

    with pytest.raises(MlException) as exc_info:
        local_job_invoker.start_run_if_local(job_def, credential, "https://base", None)  # type: ignore[arg-type]

    assert "unzip failed" in str(exc_info.value)


class _FakeOutput:
    def __init__(self, lines):
        self._lines = list(lines)
        self._index = 0

    def readline(self):
        if self._index < len(self._lines):
            line = self._lines[self._index]
            self._index += 1
            return line
        return ""


class _FakeFile:
    def __init__(self):
        self.written = []

    def write(self, data):
        self.written.append(data)


def test_log_subprocess_writes_to_file_without_console(monkeypatch):
    created_threads = []

    class _FakeThread:
        def __init__(self, target):
            self._target = target
            self.daemon = False
            self.started = False
            created_threads.append(self)

        def start(self):
            self.started = True
            self._target()

    monkeypatch.setattr(local_job_invoker, "Thread", _FakeThread)

    output = _FakeOutput(["line1\n", "line2\n"])
    file_obj = _FakeFile()

    _log_subprocess(output, file_obj, show_in_console=False)

    assert file_obj.written == ["line1\n", "line2\n"]
    assert len(created_threads) == 1
    assert created_threads[0].daemon is True
    assert created_threads[0].started is True


def test_log_subprocess_writes_to_file_and_console(monkeypatch):
    created_threads = []

    class _FakeThread:
        def __init__(self, target):
            self._target = target
            self.daemon = False
            self.started = False
            created_threads.append(self)

        def start(self):
            self.started = True
            self._target()

    monkeypatch.setattr(local_job_invoker, "Thread", _FakeThread)

    printed = []

    def _fake_print(*args, **kwargs):  # type: ignore[no-untyped-def]
        printed.append((args, kwargs))

    monkeypatch.setattr(builtins, "print", _fake_print)

    output = _FakeOutput(["lineA\n", "lineB\n"])
    file_obj = _FakeFile()

    _log_subprocess(output, file_obj, show_in_console=True)

    assert file_obj.written == ["lineA\n", "lineB\n"]
    assert len(printed) == 2
    assert printed[0][0][0] == "lineA\n"
    assert printed[1][0][0] == "lineB\n"
    assert len(created_threads) == 1
    assert created_threads[0].daemon is True
    assert created_threads[0].started is True


class TestCopyBootstrapperFromContainer:
    def test_copy_bootstrapper_from_container_success(self, tmp_path, monkeypatch):
        original_home = Path.home

        def fake_home():
            return tmp_path

        monkeypatch.setattr(local_job_invoker.Path, "home", staticmethod(fake_home))

        helper = local_job_invoker.CommonRuntimeHelper("test_job")

        written_chunks = []

        class FakeContainer:
            def get_archive(self, path):
                return [b"chunk1", b"chunk2"], None

        class FakeTar:
            def __init__(self, *args, **kwargs):
                self._names = [local_job_invoker.CommonRuntimeHelper.VM_BOOTSTRAPPER_FILE_NAME]
                self.extracted = []

            def getnames(self):
                return self._names

            def extract(self, name, path):
                self.extracted.append((name, path))

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def fake_open_tar(path, mode="r"):
            assert mode == "r"
            return FakeTar()

        def fake_remove(path):
            written_chunks.append(path)

        monkeypatch.setattr(local_job_invoker.tarfile, "open", fake_open_tar)
        monkeypatch.setattr(local_job_invoker.os, "remove", fake_remove)

        container = FakeContainer()

        helper.copy_bootstrapper_from_container(container)

        tar_file_path = helper.vm_bootstrapper_full_path + ".tar"
        assert tar_file_path in written_chunks
        assert os.path.dirname(helper.vm_bootstrapper_full_path) == os.path.dirname(tar_file_path)

        Path.home = original_home

    def test_copy_bootstrapper_from_container_docker_api_error(self, tmp_path, monkeypatch):
        original_home = Path.home

        def fake_home():
            return tmp_path

        monkeypatch.setattr(local_job_invoker.Path, "home", staticmethod(fake_home))

        helper = local_job_invoker.CommonRuntimeHelper("test_job_error")

        class ErrorContainer:
            def get_archive(self, path):
                raise local_job_invoker.docker.errors.APIError("api error", None, "explanation")

        container = ErrorContainer()

        with pytest.raises(MlException) as exc_info:
            helper.copy_bootstrapper_from_container(container)

        assert "Copying vm-bootstrapper from container has failed." in str(exc_info.value)

        Path.home = original_home


class TestCheckBootstrapperProcessStatus:
    def test_check_bootstrapper_process_status_success_returns_code(self, tmp_path, monkeypatch):
        def fake_home():
            return tmp_path

        monkeypatch.setattr(local_job_invoker.Path, "home", staticmethod(fake_home))

        helper = local_job_invoker.CommonRuntimeHelper("job_success")

        class FakeProcess:
            def poll(self):
                return 0

        process = FakeProcess()
        return_code = helper.check_bootstrapper_process_status(process)
        assert return_code == 0

    def test_check_bootstrapper_process_status_failure_raises_runtime_error(self, tmp_path, monkeypatch):
        def fake_home():
            return tmp_path

        monkeypatch.setattr(local_job_invoker.Path, "home", staticmethod(fake_home))

        helper = local_job_invoker.CommonRuntimeHelper("job_failure")
        helper.stderr = io.StringIO("bootstrapper stderr content")

        class FakeProcess:
            def poll(self):
                return 1

        process = FakeProcess()

        with pytest.raises(RuntimeError) as exc_info:
            helper.check_bootstrapper_process_status(process)

        message = str(exc_info.value)
        assert "bootstrapper stderr content" in message
        assert local_job_invoker.CommonRuntimeHelper.BOOTSTRAP_BINARY_FAILURE_MSG.split("{")[0] in message


class TestStartRunIfLocal:
    class _FakeToken:
        def __init__(self, token):
            self.token = token

    class _FakeCredential:
        def get_token(self, scope):
            return TestStartRunIfLocal._FakeToken("fake_token")

    class _FakePipeline:
        def __init__(self):
            self.calls = []

    def test_start_run_if_local_success(self, monkeypatch):
        fake_credential = TestStartRunIfLocal._FakeCredential()
        fake_pipeline = TestStartRunIfLocal._FakePipeline()

        def fake_get_execution_service_response(job_definition, token, requests_pipeline):
            fake_pipeline.calls.append((job_definition, token, requests_pipeline))
            return b"zipcontent", "snapshot-123"

        captured_args = {}

        def fake_unzip_to_temporary_file(job_definition, zip_content):
            captured_args["job_definition"] = job_definition
            captured_args["zip_content"] = zip_content
            return Path("/tmp/fake_dir")

        invoked = {}

        def fake_invoke_command(project_temp_dir):
            invoked["dir"] = project_temp_dir

        monkeypatch.setattr(
            local_job_invoker,
            "get_execution_service_response",
            fake_get_execution_service_response,
        )
        monkeypatch.setattr(local_job_invoker, "unzip_to_temporary_file", fake_unzip_to_temporary_file)
        monkeypatch.setattr(local_job_invoker, "invoke_command", fake_invoke_command)

        job_definition = object()
        snapshot_id = local_job_invoker.start_run_if_local(
            job_definition,
            fake_credential,
            "https://example.com",
            fake_pipeline,
        )

        assert snapshot_id == "snapshot-123"
        assert captured_args["job_definition"] is job_definition
        assert captured_args["zip_content"] == b"zipcontent"
        assert invoked["dir"] == Path("/tmp/fake_dir")

    def test_start_run_if_local_failure_wraps_exception(self, monkeypatch):
        fake_credential = TestStartRunIfLocal._FakeCredential()
        fake_pipeline = TestStartRunIfLocal._FakePipeline()

        def fake_get_execution_service_response(job_definition, token, requests_pipeline):
            return b"zipcontent", "snapshot-456"

        def fake_unzip_to_temporary_file(job_definition, zip_content):
            raise ValueError("unzip failed")

        monkeypatch.setattr(
            local_job_invoker,
            "get_execution_service_response",
            fake_get_execution_service_response,
        )
        monkeypatch.setattr(local_job_invoker, "unzip_to_temporary_file", fake_unzip_to_temporary_file)

        job_definition = object()

        with pytest.raises(MlException) as exc_info:
            local_job_invoker.start_run_if_local(
                job_definition,
                fake_credential,
                "https://example.com",
                fake_pipeline,
            )

        expected_msg = local_job_invoker.LOCAL_JOB_FAILURE_MSG.format(ValueError("unzip failed"))
        assert expected_msg in str(exc_info.value)


def test_get_creationflags_windows(monkeypatch):
    if not hasattr(local_job_invoker.subprocess, "STARTUPINFO"):
        class DummyStartupInfo:
            def __init__(self):
                self.dwFlags = 0
                self.wShowWindow = 0

        monkeypatch.setattr(local_job_invoker.subprocess, "STARTUPINFO", DummyStartupInfo, raising=False)

    if not hasattr(local_job_invoker.subprocess, "STARTF_USESHOWWINDOW"):
        monkeypatch.setattr(local_job_invoker.subprocess, "STARTF_USESHOWWINDOW", 1, raising=False)

    if not hasattr(local_job_invoker.subprocess, "SW_HIDE"):
        monkeypatch.setattr(local_job_invoker.subprocess, "SW_HIDE", 0, raising=False)

    result = local_job_invoker._get_creationflags_and_startupinfo_for_background_process(os_override='nt')
    assert result['creationflags'] == 0x00000010
    startupinfo = result['startupinfo']
    assert (startupinfo.dwFlags & subprocess.STARTF_USESHOWWINDOW) == subprocess.STARTF_USESHOWWINDOW
    assert startupinfo.wShowWindow == subprocess.SW_HIDE
    assert 'shell' not in result
    assert 'stdin' not in result
    assert 'stdout' not in result
    assert 'stderr' not in result


def test_get_creationflags_unix():
    result = local_job_invoker._get_creationflags_and_startupinfo_for_background_process(os_override='posix')
    assert result['stdin'] == subprocess.DEVNULL
    assert result['stdout'] == subprocess.DEVNULL
    assert result['stderr'] == subprocess.STDOUT
    assert 'shell' not in result
    assert 'creationflags' not in result
    assert 'startupinfo' not in result


def test_patch_invocation_script_serialization_transforms_snapshots(tmp_path):
    invocation_script = tmp_path / 'invoke.sh'
    invocation_script.write_text("echo start\n--snapshots '{\"abc\": 123}'\necho end\n")
    patch_invocation_script_serialization(invocation_script)
    updated = invocation_script.read_text()
    assert '--snapshots "{\\"abc\\": 123}"' in updated


def test_patch_invocation_script_serialization_no_match(tmp_path):
    invocation_script = tmp_path / 'invoke.sh'
    invocation_script.write_text("echo start\nno snapshots flag here\n")
    patch_invocation_script_serialization(invocation_script)
    assert invocation_script.read_text() == "echo start\nno snapshots flag here\n"


class _DummyToken:
    def __init__(self, token: str) -> None:
        self.token = token


class _DummyCredential:
    def __init__(self, token: str) -> None:
        self._token = token

    def get_token(self, _: str) -> _DummyToken:
        return _DummyToken(self._token)


class _DummyLocalService:
    def __init__(self) -> None:
        self.endpoint = "dummy"


class _DummyProperties:
    def __init__(self) -> None:
        self.services = {"Local": _DummyLocalService()}


class _DummyJobDefinition:
    def __init__(self) -> None:
        self.name = "test"
        self.properties = _DummyProperties()


def test_start_run_if_local_returns_snapshot(monkeypatch, tmp_path):
    job_definition = _DummyJobDefinition()
    credential = _DummyCredential("token")
    requests_pipeline = object()

    monkeypatch.setattr(
        local_job_invoker,
        "get_execution_service_response",
        lambda jd, token, pipeline: (b"zip", "snapshot-id"),
    )
    monkeypatch.setattr(
        local_job_invoker,
        "unzip_to_temporary_file",
        lambda jd, content: tmp_path,
    )
    invoked = []

    def dummy_invoke(path):
        invoked.append(path)

    monkeypatch.setattr(local_job_invoker, "invoke_command", dummy_invoke)

    result = start_run_if_local(job_definition, credential, "ws", requests_pipeline)

    assert result == "snapshot-id"
    assert invoked == [tmp_path]


def test_start_run_if_local_wraps_unzip_errors(monkeypatch):
    job_definition = _DummyJobDefinition()
    credential = _DummyCredential("token")
    requests_pipeline = object()

    monkeypatch.setattr(
        local_job_invoker,
        "get_execution_service_response",
        lambda jd, token, pipeline: (b"zip", "snapshot"),
    )
    monkeypatch.setattr(
        local_job_invoker,
        "unzip_to_temporary_file",
        lambda jd, content: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    with pytest.raises(MlException) as exc_info:
        start_run_if_local(job_definition, credential, "ws", requests_pipeline)

    expected_message = LOCAL_JOB_FAILURE_MSG.format("boom")
    assert exc_info.value.message == expected_message


def _build_common_runtime_response():
    bootstrapper_info = {"registry": "https://example.com", "value": 1}
    job_spec = "{'job': 'spec'}"
    encoded_bootstrapper_info = base64.b64encode(json.dumps(bootstrapper_info).encode("utf-8"))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_ref:
        zip_ref.writestr(
            f"{AZUREML_RUN_SETUP_DIR}/common_runtime_bootstrapper_info.json",
            encoded_bootstrapper_info,
        )
        zip_ref.writestr(f"{AZUREML_RUN_SETUP_DIR}/common_runtime_job_spec.json", job_spec)
    return buffer.getvalue(), bootstrapper_info, job_spec


def _build_bootstrapper_only_response():
    bootstrapper_info = {"field": "value"}
    encoded_bootstrapper_info = base64.b64encode(json.dumps(bootstrapper_info).encode("utf-8"))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_ref:
        zip_ref.writestr(
            f"{AZUREML_RUN_SETUP_DIR}/common_runtime_bootstrapper_info.json",
            encoded_bootstrapper_info,
        )
    return buffer.getvalue()


def _prepare_helper(monkeypatch, tmp_path, job_suffix):
    monkeypatch.setattr(
        "azure.ai.ml.operations._local_job_invoker.Path.home",
        lambda: tmp_path,
    )
    return CommonRuntimeHelper(f"job-{job_suffix}")


def test_get_common_runtime_info_from_response_success(monkeypatch, tmp_path):
    helper = _prepare_helper(monkeypatch, tmp_path, "success")
    try:
        response, expected_info, expected_spec = _build_common_runtime_response()
        bootstrapper_info, job_spec = helper.get_common_runtime_info_from_response(response)
        assert bootstrapper_info == expected_info
        assert job_spec == expected_spec
    finally:
        helper.stdout.close()
        helper.stderr.close()


def test_get_common_runtime_info_from_response_missing_file(monkeypatch, tmp_path):
    helper = _prepare_helper(monkeypatch, tmp_path, "missing")
    try:
        response = _build_bootstrapper_only_response()
        with pytest.raises(RuntimeError) as error:
            helper.get_common_runtime_info_from_response(response)
        assert "common_runtime_bootstrapper_info.json" in str(error.value)
    finally:
        helper.stdout.close()
        helper.stderr.close()


class _FakeProcess:
    def __init__(self):
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.terminate_called = False
        self.kill_called = False

    def poll(self):
        return None

    def terminate(self):
        self.terminate_called = True

    def kill(self):
        self.kill_called = True


@pytest.mark.usefixtures("monkeypatch", "tmp_path")
def test_execute_bootstrapper_returns_process_when_status_truthy(monkeypatch, tmp_path):
    helper = _prepare_helper(monkeypatch, tmp_path, "success-runner")
    fake_process = _FakeProcess()
    monkeypatch.setattr(
        "azure.ai.ml.operations._local_job_invoker.subprocess.Popen",
        lambda *args, **kwargs: fake_process,
    )
    monkeypatch.setattr(
        "azure.ai.ml.operations._local_job_invoker._log_subprocess",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        CommonRuntimeHelper,
        "check_bootstrapper_process_status",
        lambda self, process: 1,
    )
    try:
        result = helper.execute_bootstrapper("bootstrapper", "job-spec")
        assert result is fake_process
    finally:
        helper.stdout.close()
        helper.stderr.close()


@pytest.mark.usefixtures("monkeypatch", "tmp_path")
def test_execute_bootstrapper_raises_and_disconnects_on_failure(monkeypatch, tmp_path):
    helper = _prepare_helper(monkeypatch, tmp_path, "failure-runner")
    fake_process = _FakeProcess()
    fake_process.stdout.write("")
    fake_process.stderr.write("")
    monkeypatch.setattr(
        "azure.ai.ml.operations._local_job_invoker.subprocess.Popen",
        lambda *args, **kwargs: fake_process,
    )
    monkeypatch.setattr(
        "azure.ai.ml.operations._local_job_invoker._log_subprocess",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        CommonRuntimeHelper,
        "check_bootstrapper_process_status",
        lambda self, process: None,
    )
    helper.stderr.write("failure details")
    helper.stderr.flush()
    helper.stderr.seek(0)
    try:
        with pytest.raises(RuntimeError) as error:
            helper.execute_bootstrapper("bootstrapper", "job-spec")
        assert str(error.value) == LOCAL_JOB_FAILURE_MSG.format("failure details")
        assert fake_process.terminate_called is True
        assert fake_process.kill_called is True
    finally:
        helper.stdout.close()
        helper.stderr.close()


# GENERATED ADDITIONAL TESTS

def test_execute_bootstrapper_returns_process_when_check_returns_truthy(monkeypatch, tmp_path):
    monkeypatch.setattr("azure.ai.ml.operations._local_job_invoker.Path.home", lambda: tmp_path)
    monkeypatch.setattr(
        "azure.ai.ml.operations._local_job_invoker._log_subprocess", lambda *_args, **_kwargs: None
    )
    process_metadata = {}

    class FakeProcess:
        def __init__(self):
            self.stdout = io.StringIO("")
            self.stderr = io.StringIO("")
            self.terminate_called = False
            self.kill_called = False

        def terminate(self):
            self.terminate_called = True

        def kill(self):
            self.kill_called = True

    fake_process = FakeProcess()

    def fake_popen(*args, **kwargs):
        process_metadata["args"] = args
        process_metadata["kwargs"] = kwargs
        return fake_process

    monkeypatch.setattr(
        "azure.ai.ml.operations._local_job_invoker.subprocess.Popen", fake_popen
    )
    monkeypatch.setattr(
        "azure.ai.ml.operations._local_job_invoker.CommonRuntimeHelper.check_bootstrapper_process_status",
        lambda _self, _process: 1,
    )

    helper = CommonRuntimeHelper(job_name="job")
    try:
        result = helper.execute_bootstrapper(str(tmp_path / "bootstrapper"), '{"job": "spec"}')
        assert result is fake_process
        assert helper.common_runtime_temp_folder == process_metadata["kwargs"]["cwd"]
        assert process_metadata["kwargs"]["env"] == helper.LOCAL_JOB_ENV_VARS
        assert not fake_process.terminate_called
        assert not fake_process.kill_called
    finally:
        helper.stdout.close()
        helper.stderr.close()


def test_execute_bootstrapper_raises_when_check_returns_none(monkeypatch, tmp_path):
    monkeypatch.setattr("azure.ai.ml.operations._local_job_invoker.Path.home", lambda: tmp_path)
    monkeypatch.setattr(
        "azure.ai.ml.operations._local_job_invoker._log_subprocess", lambda *_args, **_kwargs: None
    )

    class FakeProcess:
        def __init__(self):
            self.stdout = io.StringIO("")
            self.stderr = io.StringIO("")
            self.terminate_called = False
            self.kill_called = False

        def terminate(self):
            self.terminate_called = True

        def kill(self):
            self.kill_called = True

    fake_process = FakeProcess()

    monkeypatch.setattr(
        "azure.ai.ml.operations._local_job_invoker.subprocess.Popen", lambda *args, **kwargs: fake_process
    )
    monkeypatch.setattr(
        "azure.ai.ml.operations._local_job_invoker.CommonRuntimeHelper.check_bootstrapper_process_status",
        lambda _self, _process: None,
    )

    helper = CommonRuntimeHelper(job_name="job")
    helper.stderr.write("bootstrapper failure")
    helper.stderr.seek(0)
    try:
        with pytest.raises(RuntimeError) as excinfo:
            helper.execute_bootstrapper(str(tmp_path / "bootstrapper"), '{"job": "spec"}')
        assert str(excinfo.value) == LOCAL_JOB_FAILURE_MSG.format("bootstrapper failure")
        assert fake_process.terminate_called
        assert fake_process.kill_called
    finally:
        helper.stdout.close()
        helper.stderr.close()


def test_check_bootstrapper_process_status_raises_for_non_zero_return_code(monkeypatch, tmp_path):
    monkeypatch.setattr("azure.ai.ml.operations._local_job_invoker.Path.home", lambda: tmp_path)

    helper = CommonRuntimeHelper(job_name="job")
    helper.stderr.write("stderr contents")
    helper.stderr.seek(0)

    class DummyProcess:
        @staticmethod
        def poll():
            return 3

    try:
        with pytest.raises(RuntimeError) as excinfo:
            helper.check_bootstrapper_process_status(DummyProcess())
        assert str(excinfo.value) == helper.BOOTSTRAP_BINARY_FAILURE_MSG.format("stderr contents")
    finally:
        helper.stdout.close()
        helper.stderr.close()
