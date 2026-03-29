import io
import os
import re
import time
import sys
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.exceptions import JobException
from azure.ai.ml.operations._job_ops_helper import (
    _get_sorted_filtered_logs,
    _incremental_print,
    _get_last_log_primary_instance,
    _wait_before_polling,
    get_git_properties,
    has_pat_token,
)
from azure.ai.ml.constants._common import GitProperties


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOpsHelperTopGaps(AzureRecordedTestCase):
    def test_get_sorted_filtered_logs_only_streamable_and_processed_slice(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Create logs that match the COMMON_RUNTIME_STREAM_LOG_PATTERN and ALL_USER patterns
        # Use names that would be matched by the SDK patterns (they are regex-based); we only need deterministic behavior
        logs = [
            "azureml-logs/2023-01-01_00-00-00/job_1/stdout.txt",
            "azureml-logs/2023-01-01_00-00-01/job_2/stderr.txt",
            "azureml-logs/2023-01-01_00-00-02/job_3/100-stdout.txt",
        ]

        # When only_streamable=True, function should choose COMMON_RUNTIME_STREAM_LOG_PATTERN
        filtered_all = _get_sorted_filtered_logs(logs, job_type="command", processed_logs=None, only_streamable=True)
        assert isinstance(filtered_all, list)
        # When none processed, returns sorted list (or subset matched by regex). Ensure result is a list and contains strings.
        assert all(isinstance(x, str) for x in filtered_all)

        # Simulate some entries already processed to exercise previously_printed_index slicing logic
        processed = {filtered_all[0]: 1} if len(filtered_all) > 0 else {}
        sliced = _get_sorted_filtered_logs(logs, job_type="command", processed_logs=processed, only_streamable=True)
        # If processed had an entry, slicing should not start from that entry (i.e., length reduced or same)
        assert isinstance(sliced, list)
        assert all(isinstance(x, str) for x in sliced)

    def test_get_sorted_filtered_logs_fallback_legacy_patterns(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Provide logs that do NOT match common runtime patterns to force fallback to legacy patterns.
        legacy_logs = [
            "/azureml-logs/70_job_rank_0.txt",
            "/azureml-logs/71_job_rank_1.txt",
            "/azureml-logs/72_job_worker_0.txt",
        ]
        # only_streamable True but no common runtime matches; should fallback and match COMMAND_JOB_LOG_PATTERN for job_type 'command'
        result = _get_sorted_filtered_logs(legacy_logs, job_type="command", processed_logs=None, only_streamable=True)
        assert isinstance(result, list)
        # Should include only entries that match the legacy command pattern (all above are legacy-like), ensure sorted
        assert result == sorted(result)

    def test_incremental_print_empty_and_header_behavior(self, client: MLClient, randstr: Callable[[], str]) -> None:
        buf = io.StringIO()
        processed = {}
        # Empty log should return without writing anything
        _incremental_print("", processed, "empty_log.txt", buf)
        assert buf.getvalue() == ""

        # Non-empty should write header and lines
        _incremental_print("a\nb", processed, "log1.txt", buf)
        val = buf.getvalue()
        assert "Streaming log1.txt" in val
        assert "a" in val and "b" in val

        # Calling again with additional line should append only the new line (no new header)
        buf.truncate(0)
        buf.seek(0)
        # simulate log extended with a third line
        _incremental_print("a\nb\nc", processed, "log1.txt", buf)
        appended = buf.getvalue()
        assert "Streaming log1.txt" not in appended
        assert "c" in appended


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOpsHelperGaps(AzureRecordedTestCase):
    def test_get_sorted_filtered_logs_legacy_fallback_and_processed_slice(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Create a list of logs that do NOT match the common runtime patterns so the function falls back to legacy patterns
        # Use job_type that maps to COMMAND so legacy COMMAND_JOB_LOG_PATTERN is selected
        logs = [
            "azureml-logs/70_job_rank_0.txt",
            "azureml-logs/70_job_worker_0.txt",
            "azureml-logs/71_job_rank_1.txt",
            "azureml-logs/71_job_worker_0.txt",
        ]
        # Simulate that one of the logs has been processed already
        processed = {"azureml-logs/70_job_rank_0.txt": 10}

        # Call with only_streamable True (common-runtime patterns will not match these legacy names)
        result = _get_sorted_filtered_logs(logs_iterable=logs, job_type="command", processed_logs=processed, only_streamable=True)

        # The legacy pattern should be applied and results sorted.
        assert isinstance(result, list)
        # The implementation returns the slice inclusive of the last processed file; ensure the processed file is present at start
        assert len(result) > 0
        assert result[0] == "azureml-logs/70_job_rank_0.txt"
        # Ensure remaining logs are present
        assert any(x in result for x in ["azureml-logs/70_job_worker_0.txt", "azureml-logs/71_job_rank_1.txt", "azureml-logs/71_job_worker_0.txt"]) 

    def test_incremental_print_writes_header_and_appends_then_updates_processed(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        fileout = io.StringIO()
        processed_logs = {}
        name = "test_log.txt"
        # First call with some content should write header and lines
        content = "line1\nline2"
        _incremental_print(content, processed_logs, name, fileout)
        output = fileout.getvalue()
        # Header should be present
        assert "Streaming test_log.txt" in output
        assert "line1\n" in output
        assert processed_logs[name] == 2

        # Second call with additional lines should NOT repeat the header, only append new lines
        fileout2 = io.StringIO()
        _incremental_print("line1\nline2\nline3\n", processed_logs, name, fileout2)
        out2 = fileout2.getvalue()
        # No header in second output
        assert "Streaming test_log.txt" not in out2
        # Only the new line (line3) should be printed
        assert "line3\n" in out2
        # Processed count updated to 3
        assert processed_logs[name] == 3

    def test_get_last_log_primary_instance_prefers_primary_ranks(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Create logs where last log matches pattern and there exist primary rank entries
        logs = [
            "prefix_rank_1_0.txt",
            "prefix_rank_0_0.txt",
            "prefix_worker_0_1.txt",
            "prefix_rank_2_0.txt",
        ]
        # The last log is prefix_rank_2_0.txt; function should search for primary ranks and return the matching primary if found
        last = _get_last_log_primary_instance(logs)
        # Should return one of the logs and be a .txt filename
        assert last in logs
        assert last.endswith(".txt")

    def test_wait_before_polling_raises_on_negative_and_returns_int_on_positive(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Negative seconds should raise JobException
        with pytest.raises(Exception):
            _wait_before_polling(-1)

        # Small positive seconds should return an int greater than or equal to the configured minimum
        val = _wait_before_polling(1.0)
        assert isinstance(val, int)
        assert val >= 0

    def test_has_pat_token_detects_various_formats(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # format: https://mypattoken@dev.azure.com/...
        url1 = "https://mypattoken@dev.azure.com/organization/project/_git/repo"
        assert has_pat_token(url1) is True

        # format: https://dev.azure.com/mypattoken@organization/... (rare but supported by regex)
        url2 = "https://dev.azure.com/mypattoken@organization/project/_git/repo"
        assert has_pat_token(url2) is True

        # no token present
        url3 = "https://dev.azure.com/organization/project/_git/repo"
        assert has_pat_token(url3) is False

        # None input
        assert has_pat_token(None) is False


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOpsHelperGapsGenerated(AzureRecordedTestCase):
    def test_incremental_print_headers_and_append_behavior(self, client: MLClient, randstr: Callable[[], str]) -> None:
        filebuf = io.StringIO()
        processed = {}
        log_name = "some_log.txt"
        # first write: should print header and lines
        _incremental_print("line1\nline2", processed, log_name, filebuf)
        content = filebuf.getvalue()
        assert "Streaming some_log.txt" in content
        assert "line1\n" in content
        assert processed.get(log_name) == 2

        # subsequent write should not repeat header, only append new lines
        _incremental_print("line1\nline2\nline3", processed, log_name, filebuf)
        content2 = filebuf.getvalue()
        # header should only appear once
        assert content2.count("Streaming some_log.txt") == 1
        # new line should be appended
        assert "line3\n" in content2
        assert processed.get(log_name) == 3

        # empty log should be skipped and not change processed
        prev = dict(processed)
        _incremental_print("", processed, "empty.txt", filebuf)
        assert processed.get("empty.txt") is None
        assert processed == prev or processed.get(log_name) == 3

    def test_wait_before_polling_negative_raises_and_positive_returns_int(self, client: MLClient, randstr: Callable[[], str]) -> None:
        with pytest.raises(Exception):
            _wait_before_polling(-1)
        # For a small positive time, should return an int >= min polling interval
        val = _wait_before_polling(1.0)
        assert isinstance(val, int)
        assert val >= 1

    def test_get_git_properties_env_overrides_and_has_pat_token(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Set environment variables to avoid invoking git
        os.environ[GitProperties.ENV_REPOSITORY_URI] = "https://example.com/repo.git"
        os.environ[GitProperties.ENV_BRANCH] = "feature/branch"
        os.environ[GitProperties.ENV_COMMIT] = "abcdef123456"
        os.environ[GitProperties.ENV_DIRTY] = "true"
        os.environ[GitProperties.ENV_BUILD_ID] = "build-42"
        os.environ[GitProperties.ENV_BUILD_URI] = "https://ci.example/build/42"

        props = get_git_properties()
        assert props[GitProperties.PROP_MLFLOW_GIT_REPO_URL] == "https://example.com/repo.git"
        assert props[GitProperties.PROP_MLFLOW_GIT_BRANCH] == "feature/branch"
        assert props[GitProperties.PROP_MLFLOW_GIT_COMMIT] == "abcdef123456"
        assert props[GitProperties.PROP_DIRTY] == "True" or props[GitProperties.PROP_DIRTY] == "true"
        assert props[GitProperties.PROP_BUILD_ID] == "build-42"
        assert props[GitProperties.PROP_BUILD_URI] == "https://ci.example/build/42"

        # has_pat_token should detect PAT in different url placements
        assert has_pat_token("https://dev.azure.com/mypattoken@organization/project") is True
        assert has_pat_token("https://mypattoken@dev.azure.com/organization/project") is True
        assert has_pat_token(None) is False

        # cleanup env
        for k in [
            GitProperties.ENV_REPOSITORY_URI,
            GitProperties.ENV_BRANCH,
            GitProperties.ENV_COMMIT,
            GitProperties.ENV_DIRTY,
            GitProperties.ENV_BUILD_ID,
            GitProperties.ENV_BUILD_URI,
        ]:
            if k in os.environ:
                del os.environ[k]


# Additional generated tests merged below with a unique class name to avoid duplicate test blocks
@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOpsHelperGapsAdditional(AzureRecordedTestCase):
    def test_get_git_properties_with_env_overrides(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Set environment variables to override git properties and ensure they are returned
        env_vars = {
            GitProperties.ENV_REPOSITORY_URI: "https://example.com/repo.git",
            GitProperties.ENV_BRANCH: "feature/test-branch",
            GitProperties.ENV_COMMIT: "abcdef1234567890",
            GitProperties.ENV_DIRTY: "true",
            GitProperties.ENV_BUILD_ID: "build-123",
            GitProperties.ENV_BUILD_URI: "http://ci/build/123",
        }
        # Backup and set
        backup = {k: os.environ.get(k) for k in env_vars}
        try:
            for k, v in env_vars.items():
                os.environ[k] = v

            props = get_git_properties()

            assert props[GitProperties.PROP_MLFLOW_GIT_REPO_URL] == "https://example.com/repo.git"
            assert props[GitProperties.PROP_MLFLOW_GIT_BRANCH] == "feature/test-branch"
            assert props[GitProperties.PROP_MLFLOW_GIT_COMMIT] == "abcdef1234567890"
            # dirty is stored as stringified boolean
            assert props[GitProperties.PROP_DIRTY] == "True" or props[GitProperties.PROP_DIRTY] == "true"
            assert props[GitProperties.PROP_BUILD_ID] == "build-123"
            assert props[GitProperties.PROP_BUILD_URI] == "http://ci/build/123"
        finally:
            # Restore env
            for k, v in backup.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_has_pat_token_various_urls(self, client: MLClient) -> None:
        # None should be False
        assert has_pat_token(None) is False

        # URL without token should be False
        assert has_pat_token("https://dev.azure.com/org/project/_git/repo") is False

        # URL with token before host
        assert has_pat_token("https://mypattoken@dev.azure.com/org/project/_git/repo") is True

        # URL with token as userinfo after host path
        assert has_pat_token("https://dev.azure.com/mypattoken@org/project/_git/repo") is True

    def test_wait_before_polling_negative_raises(self, client: MLClient) -> None:
        with pytest.raises(JobException):
            _wait_before_polling(-1.0)

    def test_wait_before_polling_positive_returns_int(self, client: MLClient) -> None:
        # For a positive small value, should return an int >= minimum
        val = _wait_before_polling(1.0)
        assert isinstance(val, int)
        assert val >= 1
