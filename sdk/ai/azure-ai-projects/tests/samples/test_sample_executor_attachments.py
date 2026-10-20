# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import logging

from sample_executor import BaseSampleExecutor


def test_writes_separate_api_and_print_attachments_once(tmp_path, monkeypatch, capsys):
    sample_path = tmp_path / "sample_attachment.py"
    sample_path.write_text("# attachment fixture\n", encoding="utf-8")
    executor = BaseSampleExecutor(None, str(sample_path))

    monkeypatch.setenv("AZURE_TEST_RUN_LIVE", "true")
    monkeypatch.setenv("AZURE_TEST_ATTACH_SAMPLE_LOGS", "true")
    monkeypatch.setattr("sample_executor.tempfile.gettempdir", lambda: str(tmp_path))

    with executor._capture_debug_logs():
        logging.getLogger("azure.attachment_test").debug("Authorization: Bearer sample-token")
        executor._capture_print("sample print content")

    api_log_path, print_log_path = executor._write_attachment_logs()
    executor._write_attachment_logs()

    assert api_log_path is not None
    assert print_log_path is not None
    api_log = tmp_path.joinpath(api_log_path).read_text(encoding="utf-8")
    print_log = tmp_path.joinpath(print_log_path).read_text(encoding="utf-8")
    assert "Bearer <REDACTED>" in api_log
    assert "sample print content" not in api_log
    assert "sample print content" in print_log
    assert "Bearer <REDACTED>" not in print_log

    attachment_markers = [line for line in capsys.readouterr().out.splitlines() if line.startswith("[[ATTACHMENT|")]
    assert attachment_markers == [
        f"[[ATTACHMENT|{api_log_path}]]",
        f"[[ATTACHMENT|{print_log_path}]]",
    ]


def test_does_not_emit_attachment_markers_without_pipeline_flag(tmp_path, monkeypatch, capsys):
    sample_path = tmp_path / "sample_local.py"
    sample_path.write_text("# local fixture\n", encoding="utf-8")
    executor = BaseSampleExecutor(None, str(sample_path))

    monkeypatch.setenv("AZURE_TEST_RUN_LIVE", "true")
    monkeypatch.delenv("AZURE_TEST_ATTACH_SAMPLE_LOGS", raising=False)
    monkeypatch.setattr("sample_executor.tempfile.gettempdir", lambda: str(tmp_path))

    api_log_path, print_log_path = executor._write_attachment_logs()

    assert api_log_path is not None
    assert print_log_path is not None
    assert "[[ATTACHMENT|" not in capsys.readouterr().out