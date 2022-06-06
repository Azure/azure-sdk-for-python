import os
from pathlib import Path
import pytest

from azure.ai.ml._operations.local_job_invoker import (
    _get_creationflags_and_startupinfo_for_background_process,
    patch_invocation_script_serialization,
)


@pytest.mark.unittest
class TestLocalJobInvoker:
    def test_serialize_patch(self):
        dummy_file = Path("./dummy_file1.txt").resolve()
        dummy_file.write_text(
            """unread strings
        everythng before are ignored
        continue to ignore --snapshots '"""
            + '[{"Id": "abc-123"}]'
            + """' Everything after is ignored"""
        )

        patch_invocation_script_serialization(dummy_file)
        expected_out = (
            """unread strings
        everythng before are ignored
        continue to ignore --snapshots"""
            + ' "[{\\"Id\\": \\"abc-123\\"}]" '
            + """Everything after is ignored"""
        )
        assert dummy_file.read_text() == expected_out
        dummy_file.unlink()

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
