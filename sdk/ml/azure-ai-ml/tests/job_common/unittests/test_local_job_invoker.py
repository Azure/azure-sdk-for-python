import io
import os
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from azure.ai.ml.operations._local_job_invoker import (
    _get_creationflags_and_startupinfo_for_background_process,
    _safe_tar_extractall,
    patch_invocation_script_serialization,
    unzip_to_temporary_file,
)


@pytest.mark.unittest
@pytest.mark.training_experiences_test
class TestLocalJobInvoker:
    def test_serialize_patch(self):
        in_text = """unread strings
        everythng before are ignored
        continue to ignore --snapshots '"""
        in_text += '[{"Id": "abc-123"}]'
        in_text += """' Everything after is ignored"""

        expected_out = (
            """unread strings
        everythng before are ignored
        continue to ignore --snapshots"""
            + ' "[{\\"Id\\": \\"abc-123\\"}]" '
            + """Everything after is ignored"""
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with tempfile.NamedTemporaryFile(mode="w", delete=False, dir=temp_dir) as f:
                f.write(in_text)
                f.flush()
                patch_invocation_script_serialization(Path(f.name).resolve())
            assert Path(f.name).read_text() == expected_out

    def test_serialize_patch_no_op(self):
        # Validate that the previously escaped string does not modify if funciton is run
        dummy_file = Path("./dummy_file2.txt").resolve()
        expected_out = (
            """unread strings
        everythng before are ignored
        continue to ignore --snapshots"""
            + ' "[{\\"Id\\": \\"abc-123\\"}]" '
            + """Everything after is ignored"""
        )
        dummy_file.write_text(expected_out)
        # Should change nothing if correctly serialized
        patch_invocation_script_serialization(dummy_file)

        assert dummy_file.read_text() == expected_out
        dummy_file.unlink()

    def test_creation_flags(self):
        flags = _get_creationflags_and_startupinfo_for_background_process()
        if os.name == "nt":
            assert flags["creationflags"] == 16
            assert flags["startupinfo"] is not None
            # After validating Windows flags, rerun with override os set.
            flags = _get_creationflags_and_startupinfo_for_background_process("linux")

        assert flags == {"stderr": -2, "stdin": -3, "stdout": -3}


def _make_job_definition(name="test-run"):
    job_def = MagicMock()
    job_def.name = name
    return job_def


@pytest.mark.unittest
@pytest.mark.training_experiences_test
class TestUnzipPathTraversalPrevention:
    """Tests for ZIP path traversal prevention in unzip_to_temporary_file."""

    def test_normal_zip_extracts_successfully(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("azureml-setup/invocation.sh", "#!/bin/bash\necho hello\n")
            zf.writestr("azureml-setup/config.json", '{"key": "value"}')
        zip_bytes = buf.getvalue()

        job_def = _make_job_definition("safe-run")
        result = unzip_to_temporary_file(job_def, zip_bytes)

        try:
            assert result.exists()
            assert (result / "azureml-setup" / "invocation.sh").exists()
            assert (result / "azureml-setup" / "config.json").exists()
        finally:
            if result.exists():
                shutil.rmtree(result, ignore_errors=True)

    def test_zip_with_path_traversal_is_rejected(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("azureml-setup/invocation.sh", "#!/bin/bash\necho hello\n")
            zf.writestr("../../etc/evil.sh", "#!/bin/bash\necho pwned\n")
        zip_bytes = buf.getvalue()

        job_def = _make_job_definition("traversal-run")
        with pytest.raises(ValueError, match="path traversal"):
            unzip_to_temporary_file(job_def, zip_bytes)

    def test_zip_with_absolute_path_is_rejected(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            if os.name == "nt":
                zf.writestr("C:/Windows/Temp/evil.sh", "#!/bin/bash\necho pwned\n")
            else:
                zf.writestr("/tmp/evil.sh", "#!/bin/bash\necho pwned\n")
        zip_bytes = buf.getvalue()

        job_def = _make_job_definition("absolute-path-run")
        with pytest.raises(ValueError, match="path traversal"):
            unzip_to_temporary_file(job_def, zip_bytes)


@pytest.mark.unittest
@pytest.mark.training_experiences_test
class TestSafeTarExtract:
    """Tests for tar path traversal prevention in _safe_tar_extractall."""

    def test_normal_tar_extracts_successfully(self):
        with tempfile.TemporaryDirectory() as dest:
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode="w") as tar:
                data = b"normal content"
                info = tarfile.TarInfo(name="vm-bootstrapper")
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
            buf.seek(0)

            with tarfile.open(fileobj=buf, mode="r") as tar:
                _safe_tar_extractall(tar, dest)

            assert os.path.exists(os.path.join(dest, "vm-bootstrapper"))

    def test_tar_with_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as dest:
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode="w") as tar:
                data = b"evil content"
                info = tarfile.TarInfo(name="../../evil_script.sh")
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
            buf.seek(0)

            with tarfile.open(fileobj=buf, mode="r") as tar:
                with pytest.raises(ValueError):
                    _safe_tar_extractall(tar, dest)

    def test_tar_with_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as dest:
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode="w") as tar:
                info = tarfile.TarInfo(name="evil_link")
                info.type = tarfile.SYMTYPE
                info.linkname = "/etc/passwd"
                tar.addfile(info)
            buf.seek(0)

            with tarfile.open(fileobj=buf, mode="r") as tar:
                with pytest.raises(ValueError):
                    _safe_tar_extractall(tar, dest)

    def test_tar_with_hardlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as dest:
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode="w") as tar:
                info = tarfile.TarInfo(name="evil_hardlink")
                info.type = tarfile.LNKTYPE
                info.linkname = "/etc/shadow"
                tar.addfile(info)
            buf.seek(0)

            with tarfile.open(fileobj=buf, mode="r") as tar:
                with pytest.raises(ValueError):
                    _safe_tar_extractall(tar, dest)
