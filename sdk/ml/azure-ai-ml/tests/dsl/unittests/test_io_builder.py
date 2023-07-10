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


def assert_node_owners_expected(pipeline_job, expected_owners: dict, input_name: str):
    nodes = expand_pipeline_nodes(pipeline_job)

    actual_owners = {}
    for node in nodes:
        owner = node.inputs[input_name]._get_data_owner()
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

        # case1: node input from another node's output
        @pipeline
        def another_nodes_output():
            node1 = component_func1(component_in_number=1, component_in_path=Input(path="test_path"))
            node1.name = "node1"
            node2 = component_func1(component_in_number=2, component_in_path=node1.outputs.component_out_path)
            node2.name = "node2"
            assert node2.inputs.component_in_path._get_data_owner().name == "node1"

        assert_node_owners_expected(
            pipeline_job=another_nodes_output(),
            expected_owners={"node1": None, "node2": "node1"},
            input_name="component_in_path",
        )

        # case2.1: node input from pipeline input, which has literal value
        @pipeline
        def literal_pipeline_val(component_in_path: Input):
            node2 = component_func1(component_in_number=2, component_in_path=component_in_path)
            node2.name = "node2"
            assert node2.inputs.component_in_path._get_data_owner() == None

        assert_node_owners_expected(
            pipeline_job=literal_pipeline_val(component_in_path=Input(path="test_path")),
            expected_owners={"node2": None},
            input_name="component_in_path",
        )

        # case2.2: node input from pipeline input, which is from another node's output
        @pipeline
        def sub_pipeline(component_in_path: Input):
            node2 = component_func1(component_in_number=2, component_in_path=component_in_path)
            node2.name = "node2"
            assert node2.inputs.component_in_path._get_data_owner().name == "node1"

        @pipeline
        def parent_pipeline():
            node1 = component_func1(component_in_number=1, component_in_path=Input(path="test_path"))
            node1.name = "node1"
            sub_pipeline(component_in_path=node1.outputs.component_out_path)

        assert_node_owners_expected(
            pipeline_job=parent_pipeline(),
            expected_owners={"node1": None, "node2": "node1"},
            input_name="component_in_path",
        )

        # case2.3: node input from pipeline input, which is from subgraph's output
        @pipeline
        def sub_pipeline1(component_in_path: Input):
            node1 = component_func1(component_in_number=2, component_in_path=component_in_path)
            return node1.outputs

        @pipeline
        def sub_pipeline2(component_in_path: Input):
            node2 = component_func1(component_in_number=2, component_in_path=component_in_path)
            assert node2.inputs.component_in_path._get_data_owner().name == "node1"

        @pipeline
        def parent_pipeline():
            src = component_func1(component_in_number=1, component_in_path=Input(path="test_path"))
            sub1 = sub_pipeline1(component_in_path=src)
            sub_pipeline2(component_in_path=sub1.outputs.component_out_path)

        assert_node_owners_expected(
            pipeline_job=parent_pipeline(),
            expected_owners={"src": None, "node1": "src", "node2": "node1"},
            input_name="component_in_path",
        )

        # case3.1: node input from subgraph's output, which is from a normal node
        @pipeline
        def sub_pipeline(component_in_path: Input):
            sub_node = component_func1(component_in_number=2, component_in_path=component_in_path)
            return sub_node.outputs

        @pipeline
        def parent_pipeline():
            node1 = sub_pipeline(component_in_path=Input(path="test_path"))
            node3 = component_func1(component_in_number=3, component_in_path=node1.outputs.component_out_path)
            assert node3.inputs.component_in_path._get_data_owner().name == "sub_node"
            return node3

        assert_node_owners_expected(
            pipeline_job=parent_pipeline(),
            expected_owners={"sub_node": None, "node3": "sub_node"},
            input_name="component_in_path",
        )

        # case3.2: node input from subgraph's output, which is from another subgraph
        @pipeline
        def sub_pipeline_1(component_in_path: Input):
            sub_node_1 = component_func1(component_in_number=2, component_in_path=component_in_path)
            return sub_node_1.outputs

        @pipeline
        def sub_pipeline_2(component_in_path: Input):
            sub_node_2 = sub_pipeline_1(component_in_path=component_in_path)
            return sub_node_2.outputs

        @pipeline
        def parent_pipeline():
            node1 = sub_pipeline_2(component_in_path=Input(path="test_path"))
            node3 = component_func1(component_in_number=3, component_in_path=node1.outputs.component_out_path)
            assert node3.inputs.component_in_path._get_data_owner().name == "sub_node_1"
            return node3

        assert_node_owners_expected(
            pipeline_job=parent_pipeline(),
            expected_owners={"sub_node_1": None, "node3": "sub_node_1"},
            input_name="component_in_path",
        )

    def test_input_get_data_owner_multiple_subgraph(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml)

        @pipeline
        def sub_pipeline(component_in_path: Input):
            inner_node = component_func1(component_in_number=2, component_in_path=component_in_path)
            return inner_node.outputs

        @pipeline
        def parent_pipeline():
            node1 = component_func1(component_in_number=1, component_in_path=Input(path="test_path1"))
            node1.name = "node1"
            sub1 = sub_pipeline(component_in_path=node1.outputs.component_out_path)
            after1 = component_func1(component_in_path=sub1.outputs.component_out_path)
            source_of_branch_1 = after1.inputs.component_in_path._get_data_owner()
            assert source_of_branch_1.name == "inner_node"

            node2 = component_func1(component_in_number=3, component_in_path=Input(path="test_path2"))
            node2.name = "node2"
            sub2 = sub_pipeline(component_in_path=node2.outputs.component_out_path)
            after2 = component_func1(component_in_path=sub2.outputs.component_out_path)
            source_of_branch_2 = after2.inputs.component_in_path._get_data_owner()
            assert source_of_branch_2.name == "inner_node"

            # subgraph called twice, source for each branch should not be the same
            assert source_of_branch_1._instance_id != source_of_branch_2._instance_id
            # one is from node1, the other is from node2
            assert source_of_branch_1.inputs.component_in_path._get_data_owner().name == "node1"
            assert source_of_branch_2.inputs.component_in_path._get_data_owner().name == "node2"

        parent_pipeline()

    def test_input_get_data_owner_multiple_level_pipeline(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml)

        # case1: multi-level pipeline input
        @pipeline
        def pipeline_level1(component_in_path: Input):
            node1 = component_func1(component_in_path=component_in_path)
            assert node1.inputs.component_in_path._get_data_owner().name == "src"
            return node1.outputs

        @pipeline
        def pipeline_level2(component_in_path: Input):
            node2 = pipeline_level1(component_in_path=component_in_path)
            return node2.outputs

        @pipeline
        def pipeline_level3():
            src = component_func1(component_in_path=Input(path="test_path"))
            src.name = "src"
            node3 = pipeline_level2(component_in_path=src)
            return node3.outputs

        assert_node_owners_expected(
            pipeline_job=pipeline_level3(),
            expected_owners={"src": None, "node1": "src"},
            input_name="component_in_path",
        )

        # case2: multi-level pipeline output
        @pipeline
        def pipeline_level1():
            node1 = component_func1(component_in_path=Input(path="test_path"))
            node1.name = "node1"
            return node1.outputs

        @pipeline
        def pipeline_level2():
            node2 = pipeline_level1()
            return node2.outputs

        @pipeline
        def pipeline_level3():
            node3 = pipeline_level2()
            node3.name = "node3"
            dst = component_func1(component_in_path=node3.outputs.component_out_path)
            assert dst.inputs.component_in_path._get_data_owner().name == "node1"
            return dst.outputs

        assert_node_owners_expected(
            pipeline_job=pipeline_level3(),
            expected_owners={"node1": None, "dst": "node1"},
            input_name="component_in_path",
        )

    def test_input_get_data_owner_complex_case(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func1 = load_component(source=component_yaml)

        @pipeline
        def sub_pipeline(component_in_path: Input):
            inner_node = component_func1(component_in_path=component_in_path)
            # node input from pipeline input and it's actual value is from another node's output
            assert inner_node.inputs.component_in_path._get_data_owner().name == "node1"
            # node input left empty, owner should be None
            assert inner_node.inputs.component_in_number._get_data_owner() is None
            return inner_node.outputs

        @pipeline
        def my_pipeline():
            node1 = component_func1(component_in_number=1, component_in_path=Input(path="test_path"))
            node1.name = "node1"
            # node input literal value, don't have owner
            assert node1.inputs.component_in_number._get_data_owner() is None
            assert node1.inputs.component_in_path._get_data_owner() is None

            node2 = sub_pipeline(component_in_path=node1.outputs.component_out_path)
            node2.name = "node2"
            # node input from another node's output
            assert node2.inputs.component_in_path._get_data_owner().name == "node1"

            node3 = component_func1(component_in_path=node2.outputs.component_out_path)
            node3.name = "node3"
            # node input from another (pipeline) node's output
            assert node3.inputs.component_in_path._get_data_owner().name == "inner_node"
            return node3.outputs

        my_pipeline = my_pipeline()

        assert_node_owners_expected(
            pipeline_job=my_pipeline,
            expected_owners={"node1": None, "inner_node": "node1", "node3": "inner_node"},
            input_name="component_in_path",
        )
