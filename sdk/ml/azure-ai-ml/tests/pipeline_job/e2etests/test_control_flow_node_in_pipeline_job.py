import pytest
from typing import Callable
from devtools_testutils import AzureRecordedTestCase
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD

from azure.ai.ml import MLClient, load_job
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml._schema.pipeline import pipeline_job
from azure.ai.ml.entities._builders import Command, Pipeline
from azure.ai.ml.entities._builders.do_while import DoWhile

from .._util import _PIPELINE_JOB_TIMEOUT_SECOND
from .test_pipeline_job import assert_job_cancel


@pytest.fixture()
def update_pipeline_schema():
    # Update the job type that the pipeline is supported.
    schema = pipeline_job.PipelineJobSchema
    schema._declared_fields['jobs'] = pipeline_job.PipelineJobsField()


@pytest.mark.usefixtures(
    "recorded_test",
    "mock_code_hash",
    "enable_pipeline_private_preview_features",
    "update_pipeline_schema",
    "mock_asset_name",
    "mock_component_hash",
)
@pytest.mark.timeout(timeout=_PIPELINE_JOB_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestConditionalNodeInPipeline(AzureRecordedTestCase):
    def test_pipeline_with_do_while_node(self, client: MLClient, randstr: Callable[[], str]) -> None:
        params_override = [{"name": randstr('name')}]
        pipeline_job = load_job(
            "./tests/test_configs/dsl_pipeline/pipeline_with_do_while/pipeline.yml",
            params_override=params_override,
        )
        created_pipeline = assert_job_cancel(pipeline_job, client)
        assert len(created_pipeline.jobs) == 5
        assert isinstance(created_pipeline.jobs["pipeline_body_node"], Pipeline)
        assert isinstance(created_pipeline.jobs["do_while_job_with_pipeline_job"], DoWhile)
        assert isinstance(created_pipeline.jobs["do_while_job_with_command_component"], DoWhile)
        assert isinstance(created_pipeline.jobs["command_component_body_node"], Command)
        assert isinstance(created_pipeline.jobs["get_do_while_result"], Command)

    def test_do_while_pipeline_with_primitive_inputs(self, client: MLClient, randstr: Callable[[], str]) -> None:
        params_override = [{"name": randstr('name')}]
        pipeline_job = load_job(
            "./tests/test_configs/dsl_pipeline/pipeline_with_do_while/pipeline_with_primitive_inputs.yml",
            params_override=params_override,
        )
        created_pipeline = assert_job_cancel(pipeline_job, client)
        assert len(created_pipeline.jobs) == 5
        assert isinstance(created_pipeline.jobs["pipeline_body_node"], Pipeline)
        assert isinstance(created_pipeline.jobs["do_while_job_with_pipeline_job"], DoWhile)
        assert isinstance(created_pipeline.jobs["do_while_job_with_command_component"], DoWhile)
        assert isinstance(created_pipeline.jobs["command_component_body_node"], Command)
        assert isinstance(created_pipeline.jobs["get_do_while_result"], Command)
