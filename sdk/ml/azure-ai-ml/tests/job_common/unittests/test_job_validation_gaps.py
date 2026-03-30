from typing import Callable

import pytest

from azure.ai.ml import MLClient
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.exceptions import UserErrorException, ValidationException

from azure.ai.ml.entities._builders import Command
from azure.ai.ml.operations._job_operations import _get_job_compute_id


@pytest.mark.unittest
class TestJobOperationsGapsAdditional:
    def test_get_invalid_name_raises_user_error(self, client: MLClient) -> None:
        """
        Covers the branch in get() that raises UserErrorException when name is not a string.
        """
        with pytest.raises(UserErrorException):
            client.jobs.get(123)  # type: ignore[arg-type]

    def test_try_get_compute_arm_id_adf_returns_same(self, client: MLClient) -> None:
        """
        Covers the DataFactory 'clusterless' compute special-case in _try_get_compute_arm_id.
        Passing ComputeType.ADF should return the same value.
        """
        result = client.jobs._try_get_compute_arm_id(ComputeType.ADF)
        assert result == ComputeType.ADF

    def test_resolve_job_input_empty_path_raises_validation(self, client: MLClient) -> None:
        """
        Covers the validation branch in _resolve_job_input where Input.path is empty and should raise ValidationException.
        """
        inp = Input(path=None)
        with pytest.raises(ValidationException):
            client.jobs._resolve_job_input(inp, base_path=".")


@pytest.mark.unittest
class TestJobOperationsGaps:
    def test_get_job_compute_id_resolver_applies(self, client: MLClient) -> None:
        """Verify that _get_job_compute_id uses the provided resolver to set job.compute."""
        # Command requires a component argument
        cmd = Command(component="")
        # ensure Command exposes compute attribute
        cmd.compute = "my-compute"

        def resolver(value, **kwargs):
            return "resolved-compute-id"

        _get_job_compute_id(cmd, resolver)
        assert cmd.compute == "resolved-compute-id"
