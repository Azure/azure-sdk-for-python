from pathlib import Path

import pytest

from azure.ai.ml import Input, MLClient, dsl, load_component
from azure.ai.ml.entities import PipelineJob, ValidationResult

from .._util import _DSL_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


@pytest.mark.usefixtures("enable_pipeline_private_preview_features", "enable_private_preview_schema_features")
@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestDSLPipeline:
    def test_dsl_pipeline_component_with_validation_error(self, mock_machinelearning_client: MLClient) -> None:
        path = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline_no_arg(component_in_path):
            component_func = load_component(source=path)
            component_func(component_in_path=component_in_path, component_in_number=1)

        @dsl.pipeline
        def pipeline_func(job_in_path):
            pipeline_no_arg(job_in_path)

        pipeline_job: PipelineJob = pipeline_func(job_in_path=Input(path="./some/path"))
        # need to figure out how this happens
        pipeline_job.jobs["pipeline_no_arg"]._source_path = __file__

        validation_result: ValidationResult = mock_machinelearning_client.components.validate(
            pipeline_job.jobs["pipeline_no_arg"],
            # skip remote validation for unit test as it requires a valid workspace to fetch the location
            skip_remote_validation=True,
        )
        assert not validation_result.passed
        assert validation_result.error_messages == {
            "inputs.component_in_path": "Parameter type unknown, "
            "please add type annotation or specify input default value.",
        }

        assert mock_machinelearning_client.jobs.validate(pipeline_job).error_messages == {
            "jobs.pipeline_no_arg.inputs.component_in_path": "Parameter type unknown, please add type annotation"
            " or specify input default value.",
            "jobs.pipeline_no_arg.jobs.microsoftsamples_command_component_basic.compute": "Compute not set",
        }
