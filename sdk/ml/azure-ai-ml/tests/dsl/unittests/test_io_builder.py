from pathlib import Path

import pytest
from test_utilities.utils import omit_with_wildcard

from azure.ai.ml import Input, load_component
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities._job.pipeline._io import PipelineInput
from azure.ai.ml.entities._job.pipeline._io.base import _resolve_builders_2_data_bindings
from azure.ai.ml.exceptions import UserErrorException

from .._util import _DSL_TIMEOUT_SECOND, expand_pipeline_nodes

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"
common_omit_fields = [
    "jobs.*.componentId",
    "jobs.*._source",
    "jobs.*.properties",
]


def assert_node_owners_expected(pipeline_job, expected_owners: dict):
    nodes = expand_pipeline_nodes(pipeline_job)

    actual_owners = {}
    for node in nodes:
        owner = node.inputs.component_in_path._get_data_owner()
        if owner:
            owner = owner.name
        actual_owners[node.name] = owner
    assert actual_owners == expected_owners


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestInputOutputBuilder:
    def test_nested_input_output_builder(self):
        input1 = PipelineInput(name="input1", owner="pipeline", meta=None)
        input2 = PipelineInput(name="input2", owner="pipeline", meta=None)
        input3 = PipelineInput(name="input3", owner="pipeline", meta=None)
        test_data = {
            "data1": input1,
            "data2": {
                "1": input2,
            },
            "data3": [input3],
            "data4": [{"1": input1}, input2, [input3]],
            "data5": {"1": [input1], "2": {"1": input2}, "3": input3},
        }
        assert _resolve_builders_2_data_bindings(test_data) == {
            "data1": "${{parent.inputs.input1}}",
            "data2": {"1": "${{parent.inputs.input2}}"},
            "data3": ["${{parent.inputs.input3}}"],
            "data4": [{"1": "${{parent.inputs.input1}}"}, "${{parent.inputs.input2}}", ["${{parent.inputs.input3}}"]],
            "data5": {
                "1": ["${{parent.inputs.input1}}"],
                "2": {"1": "${{parent.inputs.input2}}"},
                "3": "${{parent.inputs.input3}}",
            },
        }

    def test_pipeline_input_result(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func = load_component(source=component_yaml)

        @pipeline
        def my_pipeline(job_in_number, job_in_path):
            assert isinstance(job_in_number, PipelineInput)
            assert isinstance(job_in_path, PipelineInput)
            assert isinstance(job_in_number.result(), int)
            assert isinstance(job_in_path.result(), Input)
            node1 = component_func(component_in_number=job_in_number, component_in_path=job_in_path)
            # calling result() will convert pipeline input to actual value
            node2 = component_func(component_in_number=job_in_number.result(), component_in_path=job_in_path.result())
            return {"output1": node1.outputs.component_out_path, "output2": node2.outputs.component_out_path}

        pipeline_job1 = my_pipeline(job_in_number=1, job_in_path=Input(path="fake_path1"))

        rest_pipeline_job = omit_with_wildcard(
            pipeline_job1._to_rest_object().properties.as_dict(), *common_omit_fields
        )
        expected_pipeline_job1 = {
            "node1": {
                "inputs": {
                    "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_number}}"},
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                },
                "name": "node1",
                "outputs": {"component_out_path": {"type": "literal", "value": "${{parent.outputs.output1}}"}},
                "type": "command",
            },
            "node2": {
                "inputs": {
                    "component_in_number": {"job_input_type": "literal", "value": "1"},
                    "component_in_path": {"job_input_type": "uri_folder", "uri": "fake_path1"},
                },
                "name": "node2",
                "outputs": {"component_out_path": {"type": "literal", "value": "${{parent.outputs.output2}}"}},
                "type": "command",
            },
        }
        assert rest_pipeline_job["jobs"] == expected_pipeline_job1

        pipeline_job2 = my_pipeline(job_in_number=2, job_in_path=Input(path="fake_path2"))

        rest_pipeline_job = omit_with_wildcard(
            pipeline_job2._to_rest_object().properties.as_dict(), *common_omit_fields
        )

        expected_pipeline_job2 = {
            "node1": {
                "inputs": {
                    "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_number}}"},
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                },
                "name": "node1",
                "outputs": {"component_out_path": {"type": "literal", "value": "${{parent.outputs.output1}}"}},
                "type": "command",
            },
            "node2": {
                "inputs": {
                    "component_in_number": {"job_input_type": "literal", "value": "2"},
                    "component_in_path": {"job_input_type": "uri_folder", "uri": "fake_path2"},
                },
                "name": "node2",
                "outputs": {"component_out_path": {"type": "literal", "value": "${{parent.outputs.output2}}"}},
                "type": "command",
            },
        }
        assert rest_pipeline_job["jobs"] == expected_pipeline_job2

        # calling pipeline func again won't affect existing pipeline job
        pipeline_job1.jobs["node2"].inputs["component_in_number"] == 1
        pipeline_job1.jobs["node2"].inputs["component_in_path"].path == "fake_path1"

        rest_pipeline_job = omit_with_wildcard(
            pipeline_job1._to_rest_object().properties.as_dict(), *common_omit_fields
        )
        assert rest_pipeline_job["jobs"] == expected_pipeline_job1

    def test_pipeline_input_result_multiple_levle(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func = load_component(source=component_yaml)

        @pipeline
        def my_pipeline_level_1(job_in_number, job_in_path):
            assert isinstance(job_in_number, PipelineInput)
            assert isinstance(job_in_path, PipelineInput)
            # Note: call result will get actual value
            assert isinstance(job_in_number.result(), int)
            assert isinstance(job_in_path.result(), Input)
            component_func(component_in_number=job_in_number, component_in_path=job_in_path)

        @pipeline
        def my_pipeline_level_2(job_in_number, job_in_path):
            assert isinstance(job_in_number, PipelineInput)
            assert isinstance(job_in_path, PipelineInput)
            assert isinstance(job_in_number.result(), int)
            assert isinstance(job_in_path.result(), Input)
            my_pipeline_level_1(job_in_number=job_in_number, job_in_path=job_in_path)
            component_func(component_in_number=job_in_number, component_in_path=job_in_path)

        pipeline_job2 = my_pipeline_level_2(job_in_number=2, job_in_path=Input(path="fake_path2"))

        rest_pipeline_job = omit_with_wildcard(
            pipeline_job2._to_rest_object().properties.as_dict(), *common_omit_fields
        )

        expected_pipeline_job = {
            "microsoftsamples_command_component_basic": {
                "inputs": {
                    "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_number}}"},
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                },
                "name": "microsoftsamples_command_component_basic",
                "type": "command",
            },
            "my_pipeline_level_1": {
                "inputs": {
                    "job_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_number}}"},
                    "job_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                },
                "name": "my_pipeline_level_1",
                "type": "pipeline",
            },
        }
        assert rest_pipeline_job["jobs"] == expected_pipeline_job

    def test_pipeline_expression_bool_test(self) -> None:
        # non-pipeline scenario, bool test will return True
        input1 = PipelineInput(name="input1", owner="pipeline", meta=None)
        if input1:
            pass
        else:
            assert False, "bool test for PipelineInput in non-pipeline scenario should always return True."

        # pipeline scenario, should raise UserErrorException
        @pipeline
        def pipeline_func(int_param: int):
            if int_param:
                print("should not enter this line.")

        with pytest.raises(UserErrorException) as e:
            pipeline_func(int_param=1)
        assert str(e.value) == (
            "Type <class 'azure.ai.ml.entities._job.pipeline._io.base.PipelineInput'> "
            "is not supported for operation bool()."
        )

    def test_input_get_data_owner(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml)

        @pipeline
        def sub_pipeline(component_in_path: Input):
            # node input from pipeline input
            inner_node = component_func1(component_in_path=component_in_path)
            return inner_node.outputs

        @pipeline
        def my_pipeline():
            # node input literal value
            node1 = component_func1(component_in_number=1, component_in_path=Input(path="test_path"))
            # node input from another node's output
            node2 = sub_pipeline(component_in_path=node1.outputs.component_out_path)
            # node input from another (pipeline) node's output
            node3 = component_func1(component_in_path=node2.outputs.component_out_path)
            return node3.outputs

        my_pipeline = my_pipeline()

        assert_node_owners_expected(
            pipeline_job=my_pipeline, expected_owners={"node1": None, "inner_node": "node1", "node3": "node2"}
        )
