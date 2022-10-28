import contextlib
import pytest

from azure.ai.ml._schema.pipeline import PipelineJobSchema
from .._util import _DSL_TIMEOUT_SECOND
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD, omit_with_wildcard
from azure.ai.ml._schema.pipeline.pipeline_component import PipelineJobsField
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_component
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.dsl._condition import condition


@contextlib.contextmanager
def include_private_preview_nodes_in_pipeline():
    original_jobs = PipelineJobSchema._declared_fields["jobs"]
    PipelineJobSchema._declared_fields["jobs"] = PipelineJobsField()

    try:
        yield
    finally:
        PipelineJobSchema._declared_fields["jobs"] = original_jobs


@pytest.mark.usefixtures(
    "enable_environment_id_arm_expansion",
    "enable_pipeline_private_preview_features",
    "mock_code_hash",
    "mock_component_hash",
    "recorded_test",
)
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestDynamicPipeline(AzureRecordedTestCase):
    def test_dsl_condition_pipeline(self, client: MLClient):
        # update jobs field to include private preview nodes

        hello_world_component_no_paths = load_component(
            source="./tests/test_configs/components/helloworld_component_no_paths.yml"
        )
        basic_component = load_component(
            source="./tests/test_configs/components/component_with_conditional_output/spec.yaml"
        )

        @pipeline(
            name="test_mldesigner_component_with_conditional_output",
            compute="cpu-cluster",
        )
        def condition_pipeline():
            result = basic_component(str_param="abc", int_param=1)

            node1 = hello_world_component_no_paths(component_in_number=1)
            node2 = hello_world_component_no_paths(component_in_number=2)
            condition(condition=result.outputs.output, false_block=node1, true_block=node2)

        pipeline_job = condition_pipeline()

        # include private preview nodes
        with include_private_preview_nodes_in_pipeline():
            pipeline_job = client.jobs.create_or_update(pipeline_job)

        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.*.componentId",
            "properties.settings",
        ]
        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            "conditionnode": {
                "condition": "${{parent.jobs.result.outputs.output}}",
                "false_block": "${{parent.jobs.node1}}",
                "true_block": "${{parent.jobs.node2}}",
                "type": "if_else",
            },
            "node1": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "computeId": None,
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "1"}},
                "limits": None,
                "name": "node1",
                "outputs": {},
                "resources": None,
                "tags": {},
                "type": "command",
                "properties": {},
            },
            "node2": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "computeId": None,
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "2"}},
                "limits": None,
                "name": "node2",
                "outputs": {},
                "resources": None,
                "tags": {},
                "type": "command",
                "properties": {},
            },
            "result": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "computeId": None,
                "display_name": None,
                "distribution": None,
                "environment_variables": {},
                "inputs": {
                    "int_param": {"job_input_type": "literal", "value": "1"},
                    "str_param": {"job_input_type": "literal", "value": "abc"},
                },
                "limits": None,
                "name": "result",
                "outputs": {},
                "resources": None,
                "tags": {},
                "type": "command",
                "properties": {},
            },
        }

    @pytest.mark.skip(reason="TODO(2027778): Verify after primitive condition is supported.")
    def test_dsl_condition_pipeline_with_primitive_input(self, client: MLClient):
        hello_world_component_no_paths = load_component(
            source="./tests/test_configs/components/helloworld_component_no_paths.yml"
        )

        @pipeline(
            name="test_mldesigner_component_with_conditional_output",
            compute="cpu-cluster",
        )
        def condition_pipeline():
            node1 = hello_world_component_no_paths(component_in_number=1)
            node2 = hello_world_component_no_paths(component_in_number=2)
            condition(condition=True, false_block=node1, true_block=node2)

        pipeline_job = condition_pipeline()
        client.jobs.create_or_update(pipeline_job)
