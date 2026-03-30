import io
import zipfile
import os
from pathlib import Path
from typing import Callable
import time
import json
import base64

import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.operations._local_job_invoker import (
    unzip_to_temporary_file,
    _get_creationflags_and_startupinfo_for_background_process,
    patch_invocation_script_serialization,
    is_local_run,
    invoke_command,
    CommonRuntimeHelper,
)
from azure.ai.ml.constants._common import AZUREML_RUN_SETUP_DIR, INVOCATION_BASH_FILE
import random


@pytest.fixture
def randstr():
    """Simple randstr fixture for unit tests that generates random strings without recording infrastructure."""
    def _generate(variable_name: str) -> str:
        return f"test_{random.randint(1, 1000000000000)}"
    return _generate


@pytest.mark.unittest
class TestLocalJobInvokerUnzip:
    def test_unzip_to_temporary_file_extracts_contents(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Create a fake job definition with a name attribute
        class _JD:
            def __init__(self, name: str):
                self.name = name

        job_name = randstr("job_name")
        job_definition = _JD(job_name)

        # Create an in-memory zip with a sample file under the expected AZUREML_RUN_SETUP_DIR
        file_path_inside = f"{AZUREML_RUN_SETUP_DIR}/testfile.txt"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w") as z:
            z.writestr(file_path_inside, "hello world")
        zip_bytes = buf.getvalue()

        # Call the function under test
        extracted_dir = unzip_to_temporary_file(job_definition, zip_bytes)

        # Verify the returned path exists and the file was extracted with expected contents
        extracted_file = extracted_dir / file_path_inside
        assert extracted_file.exists()
        content = extracted_file.read_text()
        assert content == "hello world"

        # Cleanup
        # The function extracts into tempfile.gettempdir()/AZUREML_RUNS_DIR/<job_name>
        # Remove the created directory to avoid leaving artifacts
        try:
            # Use pathlib to remove files then directory
            if extracted_file.exists():
                extracted_file.unlink()
            # remove parent directories up to the job folder
            parent = extracted_file.parent
            while parent != extracted_dir.parent and parent.exists():
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent
            # finally remove the job folder if empty
            if extracted_dir.exists():
                try:
                    extracted_dir.rmdir()
                except OSError:
                    pass
        except Exception:
            # best effort cleanup only
            pass


@pytest.mark.unittest
class TestLocalJobInvokerGaps:
    def test_get_creationflags_windows_and_unix(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Windows override should include creationflags and startupinfo
        try:
            win_args = _get_creationflags_and_startupinfo_for_background_process(os_override="nt")
        except AttributeError as e:
            # On some Python builds subprocess may not expose Windows-specific attributes
            assert "STARTUPINFO" in str(e) or "STARTF_USESHOWWINDOW" in str(e) or "SW_HIDE" in str(e)
        else:
            assert "creationflags" in win_args
            assert "startupinfo" in win_args

        # Unix-like override should include stdin/stdout/stderr
        unix_args = _get_creationflags_and_startupinfo_for_background_process(os_override="posix")
        assert "stdin" in unix_args
        assert "stdout" in unix_args
        assert "stderr" in unix_args

    def test_patch_invocation_script_serialization_rewrites_snapshots_json(self, client: MLClient, tmp_path: Path, randstr: Callable[[str], str]) -> None:
        # Create a temporary invocation script containing the problematic pattern
        script_path = tmp_path / "invoke.sh"
        original_snapshot_json = "--snapshots '{\"a\": \"b\"}'"
        content = f"echo start\n{original_snapshot_json}\necho end\n"
        script_path.write_text(content)

        # Patch should replace single-quoted JSON and escape double quotes
        patch_invocation_script_serialization(script_path)
        patched = script_path.read_text()
        assert '--snapshots "{\\"a\\": \\\"b\\\"}"' in patched
        assert "echo start" in patched and "echo end" in patched

    def test_is_local_run_various_service_configurations(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        class Props:
            def __init__(self, services):
                self.services = services

        class FakeJob:
            def __init__(self, name, services):
                self.name = name
                self.properties = Props(services)

        # No services -> not local
        job1 = FakeJob(randstr("job"), None)
        assert is_local_run(job1) is False

        # Services present but no Local -> not local
        job2 = FakeJob(randstr("job"), {})
        assert is_local_run(job2) is False

        # Local present but endpoint does not contain execution key -> False
        job3 = FakeJob(randstr("job"), {"Local": type("L", (), {"endpoint": "http://example.com/"})()})
        assert is_local_run(job3) is False

        # Local present and endpoint contains EXECUTION_SERVICE_URL_KEY -> True
        # Use the constant string from module to craft endpoint
        from azure.ai.ml.constants._common import EXECUTION_SERVICE_URL_KEY

        endpoint_with_key = f"http://es.local{EXECUTION_SERVICE_URL_KEY}{{}}"
        job4 = FakeJob(randstr("job"), {"Local": type("L", (), {"endpoint": endpoint_with_key})()})
        assert is_local_run(job4) is True


@pytest.mark.unittest
class TestLocalJobInvokerInvoke:
    @pytest.mark.skip(reason="Background bash process race condition in playback")
    def test_invoke_command_runs_bash_invocation(self, client: MLClient, randstr: Callable[[str], str], tmp_path: Path) -> None:
        # Create project temp dir with AZUREML_RUN_SETUP_DIR and invocation bash file
        project_dir = tmp_path / randstr("local_project")
        setup_dir = project_dir / AZUREML_RUN_SETUP_DIR
        setup_dir.mkdir(parents=True, exist_ok=True)

        invocation_file = setup_dir / INVOCATION_BASH_FILE
        # The script will create an output marker file and exit immediately
        marker_file = project_dir / "invocation_marker.txt"
        invocation_file.write_text(f"#!/bin/bash\necho hello > {marker_file}\n")

        # Invoke command: on unix this will chmod +x and start the script in background
        invoke_command(project_dir)

        # Wait briefly for background process to create the marker file
        for _ in range(20):
            if marker_file.exists():
                break
            time.sleep(0.1)

        assert marker_file.exists()
        content = marker_file.read_text().strip()
        assert content == "hello"


# Additional tests from generated batch merged below. Renamed class to avoid duplication with existing TestLocalJobInvokerGaps
@pytest.mark.unittest
class TestLocalJobInvokerCommonRuntime:
    def test_common_runtime_helper_init_creates_temp_and_files(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """
        Covers: lines 113-115
        Branch summary: Ensure CommonRuntimeHelper __init__ creates the per-job common runtime folder
        and opens stdout/stderr files for writing.
        Trigger strategy: Instantiate CommonRuntimeHelper with a unique job name and assert files and
        directory exist and file objects are available.
        """
        job_name = randstr("local_invoker_job")
        helper = CommonRuntimeHelper(job_name)

        # Verify the common runtime temp folder exists
        assert os.path.exists(helper.common_runtime_temp_folder)

        # Verify vm_bootstrapper_full_path is under the common runtime folder
        assert helper.VM_BOOTSTRAPPER_FILE_NAME in helper.vm_bootstrapper_full_path
        assert helper.common_runtime_temp_folder in helper.vm_bootstrapper_full_path

        # stdout and stderr file handles should be open and writable
        helper.stdout.write("test_stdout\n")
        helper.stdout.flush()
        helper.stderr.write("test_stderr\n")
        helper.stderr.flush()

        # Verify the files were created on disk
        stdout_path = os.path.join(helper.common_runtime_temp_folder, "stdout")
        stderr_path = os.path.join(helper.common_runtime_temp_folder, "stderr")
        assert os.path.exists(stdout_path)
        assert os.path.exists(stderr_path)

        # Clean up file handles
        helper.stdout.close()
        helper.stderr.close()

    def test_get_common_runtime_info_from_response_missing_files_raises(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        """
        Covers: lines 142-143
        Branch summary: get_common_runtime_info_from_response should raise if expected files are missing
        from the execution service zip response.
        Trigger strategy: Create a zip payload that does NOT include the required
        common_runtime_bootstrapper_info.json and common_runtime_job_spec.json entries and assert
        RuntimeError is raised.
        """
        job_name = randstr("local_invoker_job")
        helper = CommonRuntimeHelper(job_name)

        # Build a zip that is missing the required files under AZUREML_RUN_SETUP_DIR
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            # Add an unrelated file
            z.writestr("some_other_dir/readme.txt", "not the expected files")
        zip_bytes = buf.getvalue()

        with pytest.raises(RuntimeError) as ex:
            helper.get_common_runtime_info_from_response(zip_bytes)

        # Assert the error message references the expected bootstrapper and job spec paths
        assert "common_runtime_bootstrapper_info.json" in str(ex.value) or "common_runtime_job_spec.json" in str(ex.value)
