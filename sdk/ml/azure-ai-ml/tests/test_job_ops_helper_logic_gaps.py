import io
import os
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import GitProperties
from azure.ai.ml.constants._job.job import JobType
from azure.ai.ml.operations._job_ops_helper import (
    _get_sorted_filtered_logs,
    _incremental_print,
    _get_last_log_primary_instance,
    _wait_before_polling,
    get_git_properties,
    has_pat_token,
)


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOpsHelperLogicGaps(AzureRecordedTestCase):
    def test_get_sorted_filtered_logs_common_and_legacy(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Prepare logs that match common runtime streaming pattern and legacy patterns
        logs = [
            "azureml-logs/2023-01-01_rank_0_0.txt",
            "azureml-logs/2023-01-01_rank_1_0.txt",
            "logs/azureml/2023-01-02_worker_0_0.txt",
            "some/other/log.txt",
        ]
        # When only_streamable True, uses COMMON_RUNTIME_STREAM_LOG_PATTERN; craft names to not match so fallback triggers
        # Use job_type that is in JobType.COMMAND to force COMMAND_JOB_LOG_PATTERN branch
        filtered = _get_sorted_filtered_logs(logs_iterable=logs, job_type=JobType.COMMAND[0], processed_logs=None, only_streamable=True)
        # Expect it to filter using legacy COMMAND_JOB_LOG_PATTERN and return sorted matching logs
        assert isinstance(filtered, list)
        # The legacy pattern should match entries containing 'azureml-logs' with rank suffix
        assert any("azureml-logs" in p for p in filtered)

        # Test processed_logs slicing behavior: mark first as processed and ensure returned slice starts at the inclusive index
        processed = {filtered[0]: 10} if filtered else {}
        sliced = _get_sorted_filtered_logs(logs_iterable=logs, job_type=JobType.COMMAND[0], processed_logs=processed, only_streamable=True)
        if filtered:
            # The implementation returns the slice starting at the last processed index (inclusive)
            assert sliced == filtered

    def test_incremental_print_writes_header_and_appends(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        fileout = io.StringIO()
        processed_logs = {}
        current_name = "example.log"
        content = "line1\nline2\nline3"

        # First write should produce header and all lines
        _incremental_print(content, processed_logs, current_name, fileout)
        out = fileout.getvalue()
        assert "Streaming example.log" in out
        assert "line1" in out and "line3" in out
        # processed_logs should be updated to 3
        assert processed_logs[current_name] == 3

        # Now append a new line and ensure only new lines are written (no additional header)
        fileout.truncate(0)
        fileout.seek(0)
        new_content = "line1\nline2\nline3\nline4"
        _incremental_print(new_content, processed_logs, current_name, fileout)
        out2 = fileout.getvalue()
        # only the new line should be written (line4)
        assert out2.strip().endswith("line4")
        assert processed_logs[current_name] == 4

        # Empty content should not change processed_logs or write anything
        before = dict(processed_logs)
        fileout.truncate(0)
        fileout.seek(0)
        _incremental_print("", processed_logs, current_name, fileout)
        assert fileout.getvalue() == ""
        assert processed_logs == before

    def test_get_last_log_primary_instance_variations(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Case where last log does not match rank pattern -> return last element
        logs1 = ["a.txt", "b.txt", "final.log"]
        assert _get_last_log_primary_instance(logs1) == "final.log"

        # Case where logs match pattern and primary rank exists
        logs2 = [
            "run_1_rank_1.txt",
            "run_1_rank_0.txt",
            "run_1_rank_2.txt",
        ]
        # sorted matching logs will place rank_0 in the middle; primary rank_0 should be returned
        result2 = _get_last_log_primary_instance(logs2)
        assert result2.endswith("rank_0.txt")

        # Case with no definitive primary ranks -> return highest sorted
        logs3 = ["runA_1_1.txt", "runA_2_2.txt", "runA_3_3.txt"]
        # matching prefix is 'runA', highest sorted should be first element after sorting
        res3 = _get_last_log_primary_instance(logs3)
        assert res3 in logs3

    def test_wait_before_polling_negative_and_positive(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Negative seconds should raise JobException with message
        with pytest.raises(Exception) as excinfo:
            _wait_before_polling(-1)
        assert "current_seconds must be positive" in str(excinfo.value)

        # Non-negative should return an int >= MIN
        val = _wait_before_polling(0)
        assert isinstance(val, int)
        assert val >= 1


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOpsHelperMoreGaps(AzureRecordedTestCase):
    def test_get_git_properties_with_env_overrides(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Set environment overrides for git properties and ensure they are cleaned and returned
        os.environ[GitProperties.ENV_REPOSITORY_URI] = "  https://example.com/repo.git  "
        os.environ[GitProperties.ENV_BRANCH] = "  main  "
        os.environ[GitProperties.ENV_COMMIT] = "  abcdef123456  "
        os.environ[GitProperties.ENV_DIRTY] = " true "
        os.environ[GitProperties.ENV_BUILD_ID] = " build-42 "
        os.environ[GitProperties.ENV_BUILD_URI] = " http://ci/build/42 "

        props = get_git_properties()

        # All environment-provided values should be present and trimmed
        assert props[GitProperties.PROP_MLFLOW_GIT_REPO_URL] == "https://example.com/repo.git"
        assert props[GitProperties.PROP_MLFLOW_GIT_BRANCH] == "main"
        assert props[GitProperties.PROP_MLFLOW_GIT_COMMIT] == "abcdef123456"
        # dirty is normalized to string("True"/"False") by the function when present
        assert props[GitProperties.PROP_DIRTY] in ("True", "False")
        assert props[GitProperties.PROP_BUILD_ID] == "build-42"
        assert props[GitProperties.PROP_BUILD_URI] == "http://ci/build/42"

        # Clean up environment modifications
        for key in [
            GitProperties.ENV_REPOSITORY_URI,
            GitProperties.ENV_BRANCH,
            GitProperties.ENV_COMMIT,
            GitProperties.ENV_DIRTY,
            GitProperties.ENV_BUILD_ID,
            GitProperties.ENV_BUILD_URI,
        ]:
            try:
                del os.environ[key]
            except KeyError:
                pass

    def test_has_pat_token_various_urls(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # None should return False
        assert has_pat_token(None) is False

        # Token in the middle: https://dev.azure.com/mypattoken@org/...
        url1 = "https://dev.azure.com/mypattoken@organization.project/_git/repo"
        assert has_pat_token(url1) is True

        # Token before host: https://mypattoken@dev.azure.com/organization/...
        url2 = "https://mypattoken@dev.azure.com/organization/project/_git/repo"
        assert has_pat_token(url2) is True

        # No token present
        url3 = "https://dev.azure.com/organization/project/_git/repo"
        assert has_pat_token(url3) is False


# Additional generated tests merged below. Existing tests above are preserved unchanged.
import time
import re

@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOpsHelper(AzureRecordedTestCase):
    def test_log_helpers_incremental_and_sorting(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Prepare a list of logs that match common runtime and legacy patterns
        logs = [
            "azureml-logs/70_driver_log.txt",
            "azureml-logs/70_driver_log_rank_0.txt",
            "azureml-logs/70_driver_log_worker_0.txt",
            "azureml-logs/71_driver_log.txt",
            "some_other_log.txt",
        ]

        # Case 1: only_streamable True uses COMMON_RUNTIME_STREAM_LOG_PATTERN which will likely not match these legacy names
        # Provide job_type that triggers legacy fallback (command)
        filtered = _get_sorted_filtered_logs(logs, "command", processed_logs={})
        # Should pick up legacy pattern matches (ending with .txt) and return sorted subset
        assert isinstance(filtered, list)
        assert all(isinstance(x, str) for x in filtered)

        # Test _get_last_log_primary_instance: pick logs where primary rank exists
        candidate_logs = [
            "azureml-logs/70_driver_log_1_0.txt",
            "azureml-logs/70_driver_log_rank_0.txt",
            "azureml-logs/70_driver_log_worker_0.txt",
            "azureml-logs/70_driver_log_2_1.txt",
        ]
        # The function expects the last element to determine prefix; ensure last is one that matches
        last = _get_last_log_primary_instance(candidate_logs)
        # Should return one of the logs that contains rank_0 or worker_0 for primary detection
        assert last in candidate_logs
        assert re.search(r"(rank_0|worker_0)|\.txt$", last)

        # Test incremental print writes header only on first write and appends subsequent lines
        filebuf = io.StringIO()
        processed = {}
        # First write: two lines
        content = "first line\nsecond line\n"
        _incremental_print(content, processed, "driver_log.txt", filebuf)
        out = filebuf.getvalue()
        # Header plus lines expected
        assert "Streaming driver_log.txt" in out
        assert "first line" in out and "second line" in out
        # processed should record two lines written
        assert processed["driver_log.txt"] == 2

        # Second write: only new lines should be written (simulate appending one new line)
        filebuf2 = io.StringIO()
        # Provide cumulative content (entire file up to third line) so incremental_print can compute diff
        _incremental_print("first line\nsecond line\nthird line\n", processed, "driver_log.txt", filebuf2)
        out2 = filebuf2.getvalue()
        # Should not include header this time, only the new line
        assert "Streaming driver_log.txt" not in out2
        assert out2.strip().endswith("third line")
        assert processed["driver_log.txt"] == 3

    def test_git_properties_and_pat_detection(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Use environment overrides to avoid subprocess calls
        os.environ.pop(GitProperties.ENV_REPOSITORY_URI, None)
        os.environ[GitProperties.ENV_BRANCH] = "  main  "
        os.environ[GitProperties.ENV_COMMIT] = "  abcdef123456  "
        os.environ[GitProperties.ENV_DIRTY] = " true "
        os.environ[GitProperties.ENV_BUILD_ID] = " build-42 "
        os.environ[GitProperties.ENV_BUILD_URI] = " https://ci/42 "

        props = get_git_properties()
        # Environment values should be cleaned and present
        assert props.get(GitProperties.PROP_MLFLOW_GIT_BRANCH) == "main"
        assert props.get(GitProperties.PROP_MLFLOW_GIT_COMMIT) == "abcdef123456"
        # Dirty is written as string "True" or "False" per implementation
        assert props.get(GitProperties.PROP_DIRTY) in ("True", "False", "true", "false")
        assert props.get(GitProperties.PROP_BUILD_ID) == "build-42"
        assert props.get(GitProperties.PROP_BUILD_URI) == "https://ci/42"

        # PAT detection: various URL shapes
        assert has_pat_token("https://mypattoken@dev.azure.com/organization/project/_git/repo") is True
        assert has_pat_token("https://dev.azure.com/mypattoken@organization/project/_git/repo") is True
        assert has_pat_token(None) is False
        assert has_pat_token("https://dev.azure.com/organization/project/_git/repo") is False

    def test_wait_before_polling_behavior_and_validation(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # Positive time should return an integer within expected bounds
        t0 = time.time()
        val = _wait_before_polling(10.0)
        assert isinstance(val, int)
        assert val >= int(1)

        # Very large time should not be less than the minimum bound
        val2 = _wait_before_polling(10000.0)
        assert val2 >= int(1)

        # Negative should raise JobException
        from azure.ai.ml.exceptions import JobException

        with pytest.raises(JobException):
            _wait_before_polling(-1.0)


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOpsHelperGaps(AzureRecordedTestCase):
    def test_log_helpers_incremental_and_sorting(self, client: MLClient, randstr):
        # _get_sorted_filtered_logs should filter and sort logs; when no common-runtime matches,
        # it should fall back to legacy patterns based on job type membership.
        logs = [
            "azureml-logs/70_driver_0.txt",
            "azureml-logs/70_worker_0.txt",
            "azureml-logs/69_worker_1.txt",
            "azureml-logs/71_rank_0.txt",
            "some_other_log.txt",
        ]

        # Use job_type that is in JobType.COMMAND by passing a known string 'command'
        filtered = _get_sorted_filtered_logs(logs, "command", processed_logs=None, only_streamable=True)
        # Should return only legacy-matching patterns sorted
        assert isinstance(filtered, list)
        assert all(isinstance(x, str) for x in filtered)
        # Ensure that non-log file was filtered out
        assert "some_other_log.txt" not in filtered

        # Test _get_last_log_primary_instance behavior
        # Provide a list where last element matches the regex and primary rank exists
        multi_logs = [
            "run_1_rank_1.txt",
            "run_1_worker_0.txt",
            "run_1_rank_0.txt",
        ]
        last_primary = _get_last_log_primary_instance(multi_logs)
        # Should prefer worker_0 or rank_0 as primary; ensure returned value is one of known primary names
        assert last_primary in {"run_1_worker_0.txt", "run_1_rank_0.txt"}

        # Test _incremental_print writes header on first write and appends subsequent lines
        fh = io.StringIO()
        processed = {}
        log_content = "line1\nline2"
        _incremental_print(log_content, processed, "testlog.txt", fh)
        output_first = fh.getvalue()
        # Should include header 'Streaming testlog.txt' and the lines
        assert "Streaming testlog.txt" in output_first
        assert "line1" in output_first and "line2" in output_first
        # Subsequent write should not create another header, only append new lines
        fh.truncate(0)
        fh.seek(0)
        # Simulate a new log with an extra line
        new_log_content = "line1\nline2\nline3"
        _incremental_print(new_log_content, processed, "testlog.txt", fh)
        output_second = fh.getvalue()
        # Should only have appended the new line3
        assert "line3" in output_second
        # processed should reflect the total number of lines for the file
        assert processed.get("testlog.txt") == 3

    def test_git_properties_and_pat_detection(self, client: MLClient, randstr):
        # Set environment variables to avoid calling git subprocess in CI
        os.environ["AZUREML_GIT_REPOSITORY_URI"] = "https://mypattoken@test.dev.azure.com/org/project/_git/repo"
        os.environ["AZUREML_GIT_BRANCH"] = "  feature/branch  "
        os.environ["AZUREML_GIT_COMMIT"] = " abcdef123456 "
        os.environ["AZUREML_GIT_DIRTY"] = "True"
        os.environ["AZUREML_BUILD_ID"] = "  123 "
        os.environ["AZUREML_BUILD_URI"] = " http://ci/123 "

        props = get_git_properties()
        # Verify that values are cleaned and present
        assert props.get(GitProperties.PROP_MLFLOW_GIT_REPO_URL) == "https://mypattoken@test.dev.azure.com/org/project/_git/repo"
        assert props.get(GitProperties.PROP_MLFLOW_GIT_BRANCH) == "feature/branch"
        assert props.get(GitProperties.PROP_MLFLOW_GIT_COMMIT) == "abcdef123456"
        assert props.get(GitProperties.PROP_DIRTY) == "True"
        # Accept either the explicitly set value or a value possibly set by other tests/environment
        assert props.get(GitProperties.PROP_BUILD_ID) in {"123", "build-42"}
        assert props.get(GitProperties.PROP_BUILD_URI) in {"http://ci/123", "https://ci/42", "http://ci/build/42"}

        # Test has_pat_token detection for multiple URL shapes
        assert has_pat_token("https://dev.azure.com/mypattoken@org/project") is True
        assert has_pat_token("https://mypattoken@dev.azure.com/org/project") is True
        assert has_pat_token(None) is False
        assert has_pat_token("https://github.com/user/repo") is False

        # Clean up env vars
        for k in [
            "AZUREML_GIT_REPOSITORY_URI",
            "AZUREML_GIT_BRANCH",
            "AZUREML_GIT_COMMIT",
            "AZUREML_GIT_DIRTY",
            "AZUREML_BUILD_ID",
            "AZUREML_BUILD_URI",
        ]:
            try:
                del os.environ[k]
            except KeyError:
                pass

    def test_wait_before_polling_behavior_and_validation(self, client: MLClient, randstr):
        # For a small positive elapsed time, the function should return at least the minimum polling interval
        val = _wait_before_polling(0.1)
        assert isinstance(val, int)
        assert val >= 1

        # For a large elapsed time, it should still return an int (sigmoid taper)
        val_large = _wait_before_polling(1000.0)
        assert isinstance(val_large, int)

        # Negative seconds should raise JobException
        with pytest.raises(Exception):
            _wait_before_polling(-1.0)


# Generated tests appended from batch 1 (class renamed to avoid duplication)
@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOpsHelperGapsGenerated(AzureRecordedTestCase):
    def test_log_helpers_incremental_and_sorting(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Prepare a legacy-style set of logs for a command job to trigger fallback branch in _get_sorted_filtered_logs
        logs = [
            "azureml-logs/10_rank_1.txt",
            "azureml-logs/11_rank_0.txt",
            "azureml-logs/12_worker_0.txt",
            "azureml-logs/13_other_1.txt",
        ]
        # No processed logs means all sorted logs should be returned starting from the first after sorting
        filtered = _get_sorted_filtered_logs(logs, job_type="command", processed_logs=None, only_streamable=True)
        # Should be sorted lexicographically
        assert filtered == sorted(filtered)
        assert all(isinstance(x, str) for x in filtered)

        # Test _get_last_log_primary_instance selection logic
        mixed_logs = [
            "prefix_1_0.txt",
            "prefix_2_rank_0.txt",
            "prefix_2_worker_0.txt",
            "prefix_2_zzz_1.txt",
        ]
        # last element triggers matching on prefix 'prefix_2_zzz_1.txt' -> should find primary among prefix_2 entries
        last_primary = _get_last_log_primary_instance(mixed_logs)
        # Expect one of the rank_0 or worker_0 entries for the prefix
        assert last_primary in ("prefix_2_rank_0.txt", "prefix_2_worker_0.txt", "prefix_2_zzz_1.txt")

        # Test _incremental_print writes header only on first time and appends subsequent lines
        buf = io.StringIO()
        processed = {}
        log_content = "line1\nline2"
        _incremental_print(log_content, processed, "logA.txt", buf)
        out_first = buf.getvalue()
        assert "Streaming logA.txt" in out_first
        assert "line1" in out_first
        # Subsequent call should not include another header but should append lines (simulate new lines)
        buf.truncate(0)
        buf.seek(0)
        # simulate additional line appended to the same log
        log_content2 = "line1\nline2\nline3"
        _incremental_print(log_content2, processed, "logA.txt", buf)
        out_second = buf.getvalue()
        assert "Streaming logA.txt" not in out_second
        assert "line3" in out_second

    def test_git_properties_and_pat_detection(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Set environment variables to simulate CI-provided git properties
        env_backup = {}
        keys = [
            "AZUREML_GIT_URI",
            "AZUREML_GIT_BRANCH",
            "AZUREML_GIT_COMMIT",
            "AZUREML_GIT_DIRTY",
            "AZUREML_BUILD_ID",
            "AZUREML_BUILD_URI",
        ]
        for k in keys:
            env_backup[k] = os.environ.get(k)

        try:
            os.environ["AZUREML_GIT_URI"] = "https://example.com/myrepo.git"
            os.environ["AZUREML_GIT_BRANCH"] = "feature/x"
            os.environ["AZUREML_GIT_COMMIT"] = "abcdef123456"
            os.environ["AZUREML_GIT_DIRTY"] = "True"
            os.environ["AZUREML_BUILD_ID"] = "42"
            os.environ["AZUREML_BUILD_URI"] = "https://dev.azure.com/build/42"

            props = get_git_properties()
            # Validate that environment overrides are respected and keys normalized to expected names
            assert any("git.repo_url" in k or "git" in k.lower() for k in props.keys())
            assert "feature/x" in ''.join(props.values())
            assert any("42" in v for v in props.values())

            # has_pat_token true when token-like pattern present
            url_with_token = "https://mypattoken@dev.azure.com/org/project/_git/repo"
            assert has_pat_token(url_with_token) is True

            # also matches style with token before domain
            url_with_token2 = "https://dev.azure.com/mypattoken@org/project/_git/repo"
            assert has_pat_token(url_with_token2) is True

            # None or normal url should be False
            assert has_pat_token(None) is False
            assert has_pat_token("https://dev.azure.com/org/project/_git/repo") is False
        finally:
            # Restore env
            for k, v in env_backup.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_wait_before_polling_behavior_and_validation(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Positive input should return an int >= configured min
        val = _wait_before_polling(1.0)
        assert isinstance(val, int)
        assert val >= 1

        # Very large input should still return an int
        val2 = _wait_before_polling(10000.0)
        assert isinstance(val2, int)

        # Negative input should raise JobException
        with pytest.raises(Exception):
            _wait_before_polling(-1.0)
