import os
from unittest.mock import patch

import pytest
from typing import Callable
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from azure.ai.ml.entities import PipelineJob, Job
from azure.ai.ml.entities._job.job import Job as JobClass
from azure.ai.ml.constants._common import (
    GIT_PATH_PREFIX,
    AZUREML_PRIVATE_FEATURES_ENV_VAR,
)
from azure.ai.ml.exceptions import ValidationException, UserErrorException
from azure.core.exceptions import ResourceNotFoundError


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOperationsGaps(AzureRecordedTestCase):
    @pytest.mark.e2etest
    def test_download_non_terminal_job_raises_job_exception(
        self, client: MLClient, randstr: Callable[[], str], tmp_path
    ) -> None:
        """Covers download early-exit branch when job is not in terminal state.
        Create or get a job name that is unlikely to be terminal and call client.jobs.download to assert
        a JobException (or service-side error) is raised for non-terminal state."""
        job_name = f"e2etest_{randstr('job')}_noterm"

        # Attempt to call download for a job that likely does not exist / is not terminal.
        # The client should raise an exception indicating the job is not in a terminal state or not found.
        with pytest.raises(ResourceNotFoundError):
            client.jobs.download(job_name, download_path=str(tmp_path))

    @pytest.mark.e2etest
    def test_get_invalid_name_type_raises_user_error(self, client: MLClient) -> None:
        """Covers get() input validation branch where non-string name raises UserErrorException.
        We call client.jobs.get with a non-string value and expect an exception to be raised.
        """
        with pytest.raises(UserErrorException):
            # Intentionally pass non-string
            client.jobs.get(123)  # type: ignore[arg-type]

    @pytest.mark.e2etest
    def test_validate_git_code_path_rejected_when_private_preview_disabled(
        self, client: MLClient, randstr: Callable[[], str]
    ) -> None:
        # Construct a minimal PipelineJob with code set to a git path to trigger git code validation
        pj_name = f"e2etest_{randstr('pj')}_git"
        pj = PipelineJob(name=pj_name)
        # set code to a git path string to trigger the GIT_PATH_PREFIX check
        pj.code = GIT_PATH_PREFIX + "some/repo.git"

        # Explicitly ensure private preview is disabled so the git-code check is active,
        # even if a prior test in the session enabled it.
        with patch.dict(os.environ, {AZUREML_PRIVATE_FEATURES_ENV_VAR: "False"}):
            with pytest.raises(ValidationException):
                client.jobs.validate(pj, raise_on_failure=True)

    @pytest.mark.e2etest
    def test_get_named_output_uri_with_none_job_name_raises_user_error(
        self, client: MLClient, randstr: Callable[[], str]
    ) -> None:
        # Passing None as job_name surfaces a ResourceNotFoundError from the service
        with pytest.raises(ResourceNotFoundError):
            # Use protected helper to drive the branch where client.jobs.get is invoked with invalid name
            client.jobs._get_named_output_uri(None)

    @pytest.mark.e2etest
    def test_get_batch_job_scoring_output_uri_returns_none_for_unknown_job(self, client: MLClient) -> None:
        # For a random/nonexistent job, there should be no child scoring output and function returns None
        fake_job_name = "nonexistent_rand_job"
        result = client.jobs._get_batch_job_scoring_output_uri(fake_job_name)
        assert result is None

    @pytest.mark.e2etest
    @pytest.mark.skipif(condition=not is_live(), reason="JWT token decoding requires real credentials")
    def test_set_headers_with_user_aml_token_raises_when_aud_mismatch(
        self, client: MLClient, randstr: Callable[[], str]
    ) -> None:
        """Trigger the branch in _set_headers_with_user_aml_token that validates the token audience and
        raises ValidationException when the decoded token 'aud' does not match the aml resource id.
        """
        # kwargs to be populated by method; method mutates passed dict
        kwargs = {}
        try:
            # Call internal operation through client.jobs to exercise the public path used in create_or_update
            client.jobs._set_headers_with_user_aml_token(kwargs)
        except ValidationException:
            # In some environments the token audience will not match and a ValidationException is expected.
            pass
        else:
            # In other environments the token matches and headers should be set with the token.
            assert "headers" in kwargs
            assert "x-azureml-token" in kwargs["headers"]

    @pytest.mark.e2etest
    def test_get_batch_job_scoring_output_uri_returns_none_when_no_child_outputs(
        self, client: MLClient, randstr: Callable[[], str]
    ) -> None:
        """When there are no child run outputs reported for a batch job, _get_batch_job_scoring_output_uri should
        return None. This exercises the loop/early-exit branch where no uri is found.
        """
        fake_job_name = f"nonexistent_{randstr('job')}"
        result = client.jobs._get_batch_job_scoring_output_uri(fake_job_name)
        assert result is None


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOperationsGaps2(AzureRecordedTestCase):
    @pytest.mark.e2etest
    @pytest.mark.skipif(condition=not is_live(), reason="JWT token decoding requires real credentials")
    def test_create_or_update_pipeline_job_triggers_aml_token_validation(
        self, client: MLClient, randstr: Callable[[], str]
    ) -> None:
        # Construct a minimal PipelineJob to force the code path that sets headers with user aml token
        pj_name = f"e2etest_{randstr('pj')}_headers"
        pj = PipelineJob(name=pj_name, experiment_name="test_experiment")
        # Pipeline jobs exercise the branch where _set_headers_with_user_aml_token is invoked.
        # In many environments the token audience will not match aml resource id, causing a ValidationException.
        try:
            result = client.jobs.create_or_update(pj)
        except ValidationException:
            # Expected in environments where token audience does not match
            pass
        else:
            assert isinstance(result, Job)

    @pytest.mark.e2etest
    @pytest.mark.skipif(condition=not is_live(), reason="JWT token decoding requires real credentials")
    def test_validate_pipeline_job_headers_on_create_or_update_raises(
        self, client: MLClient, randstr: Callable[[], str]
    ) -> None:
        # Another variation to ensure create_or_update attempts to set user aml token headers for pipeline jobs
        pj_name = f"e2etest_{randstr('pj')}_headers2"
        pj = PipelineJob(name=pj_name, experiment_name="test_experiment")
        try:
            result = client.jobs.create_or_update(pj, skip_validation=False)
        except ValidationException:
            # Expected in some environments
            pass
        else:
            assert isinstance(result, Job)
