from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD

from azure.ai.ml import MLClient, load_job
from azure.ai.ml._schema.pipeline import pipeline_job
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.entities._builders import Command, Pipeline
from azure.ai.ml.entities._builders.do_while import DoWhile
from azure.ai.ml.entities._builders.parallel_for import ParallelFor

from .._util import _PIPELINE_JOB_TIMEOUT_SECOND
from .test_pipeline_job import assert_job_cancel


@pytest.fixture()
def update_pipeline_schema():
    # Update the job type that the pipeline is supported.
    schema = pipeline_job.PipelineJobSchema
    original_jobs = schema._declared_fields["jobs"]
    schema._declared_fields["jobs"] = pipeline_job.PipelineJobsField()

    try:
        yield
    finally:
        schema._declared_fields["jobs"] = original_jobs


@pytest.mark.usefixtures(
    "recorded_test",
    "mock_code_hash",
    "enable_pipeline_private_preview_features",
    "enable_private_preview_schema_features",
    "update_pipeline_schema",
    "mock_asset_name",
    "mock_component_hash",
)
@pytest.mark.timeout(timeout=_PIPELINE_JOB_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestConditionalNodeInPipeline(AzureRecordedTestCase):
    pass


class TestDoWhile(TestConditionalNodeInPipeline):
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


def assert_foreach(client: MLClient, job_name, source, expected_node):
    params_override = [{"name": job_name}]
    pipeline_job = load_job(
        source,
        params_override=params_override,
    )

    created_pipeline_job = assert_job_cancel(pipeline_job, client)
    assert isinstance(created_pipeline_job.jobs["parallel_node"], ParallelFor)
    rest_job_dict = pipeline_job._to_rest_object().as_dict()
    assert rest_job_dict["properties"]["jobs"]["parallel_node"] == expected_node


@pytest.mark.skipif(
    condition=is_live(),
    # TODO: reopen live test when parallel_for deployed to canary
    reason="parallel_for is not available in canary."
)
class TestParallelFor(TestConditionalNodeInPipeline):
    def test_simple_foreach_string_item(self, client: MLClient, randstr: Callable):
        source = "./tests/test_configs/pipeline_jobs/helloworld_parallel_for_pipeline_job.yaml"
        expected_node = {
            'body': '${{parent.jobs.parallel_body}}',
            'items': '[{"component_in_number": 1}, {"component_in_number": 2}]',
            'type': 'parallel_for'
        }

        assert_foreach(client, randstr("job_name"), source, expected_node)

    def test_simple_foreach_list_item(self, client: MLClient, randstr: Callable):
        source = "./tests/test_configs/pipeline_jobs/helloworld_parallel_for_pipeline_job_list_input.yaml"
        expected_node = {
            'body': '${{parent.jobs.parallel_body}}',
            'items': '[{"component_in_number": 1}, {"component_in_number": 2}]',
            'type': 'parallel_for'
        }
        assert_foreach(client, randstr("job_name"), source, expected_node)

    def test_simple_foreach_dict_item(self, client: MLClient, randstr: Callable):
        source = "./tests/test_configs/pipeline_jobs/helloworld_parallel_for_pipeline_job_dict_input.yaml"
        expected_node = {
            'body': '${{parent.jobs.parallel_body}}',
            'items': '{"branch1": {"component_in_number": 1}, "branch2": '
                     '{"component_in_number": 2}}',
            'type': 'parallel_for'
        }
        assert_foreach(client, randstr("job_name"), source, expected_node)

    def test_output_binding_foreach_node(self, client: MLClient, randstr: Callable):
        source = "./tests/test_configs/pipeline_jobs/helloworld_parallel_for_pipeline_job_output_binding.yaml"
        expected_node = {
            'body': '${{parent.jobs.parallel_body}}',
            'items': '[{"component_in_number": 1}, {"component_in_number": 2}]',
            'outputs': {'component_out_path': {'type': 'literal',
                                               'value': '${{parent.outputs.component_out_path}}'}},
            'type': 'parallel_for'
        }
        assert_foreach(client, randstr("job_name"), source, expected_node)
