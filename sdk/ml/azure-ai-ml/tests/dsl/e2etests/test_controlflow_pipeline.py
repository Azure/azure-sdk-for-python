from pathlib import Path

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD, assert_job_cancel, omit_with_wildcard

from azure.ai.ml import Input, MLClient, Output, load_component
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.dsl._condition import condition
from azure.ai.ml.dsl._do_while import do_while
from azure.ai.ml.dsl._group_decorator import group
from azure.ai.ml.dsl._parallel_for import parallel_for

from .._util import _DSL_TIMEOUT_SECOND, include_private_preview_nodes_in_pipeline

test_input = Input(
    type="uri_file",
    path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
)

omit_fields = [
    "name",
    "properties.display_name",
    "properties.jobs.*.componentId",
    "properties.settings",
]


@pytest.mark.usefixtures(
    "enable_private_preview_schema_features",
    "enable_environment_id_arm_expansion",
    "enable_pipeline_private_preview_features",
    "mock_code_hash",
    "mock_asset_name",
    "mock_component_hash",
    "mock_set_headers_with_user_aml_token",
    "recorded_test",
    "use_python_amlignore_during_upload",
)
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestControlFlowPipeline(AzureRecordedTestCase):
    pass


@pytest.mark.usefixtures("mock_anon_component_version")
class TestIfElse(TestControlFlowPipeline):
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
            result = basic_component()

            node1 = hello_world_component_no_paths(component_in_number=1)
            node2 = hello_world_component_no_paths(component_in_number=2)
            condition(condition=result.outputs.output, false_block=node1, true_block=node2)

        pipeline_job = condition_pipeline()

        # include private preview nodes
        with include_private_preview_nodes_in_pipeline():
            pipeline_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            "conditionnode": {
                "_source": "DSL",
                "condition": "${{parent.jobs.result.outputs.output}}",
                "false_block": "${{parent.jobs.node1}}",
                "true_block": "${{parent.jobs.node2}}",
                "type": "if_else",
            },
            "node1": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "1"}},
                "name": "node1",
                "type": "command",
            },
            "node2": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "2"}},
                "name": "node2",
                "type": "command",
            },
            "result": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "name": "result",
                "type": "command",
            },
        }

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
        with include_private_preview_nodes_in_pipeline():
            rest_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(rest_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            "conditionnode": {
                "_source": "DSL",
                "condition": True,
                "false_block": "${{parent.jobs.node1}}",
                "true_block": "${{parent.jobs.node2}}",
                "type": "if_else",
            },
            "node1": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "1"}},
                "name": "node1",
                "type": "command",
            },
            "node2": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "2"}},
                "name": "node2",
                "type": "command",
            },
        }

    def test_dsl_condition_pipeline_with_one_branch(self, client: MLClient):
        hello_world_component_no_paths = load_component(
            source="./tests/test_configs/components/helloworld_component_no_paths.yml"
        )

        @pipeline(
            compute="cpu-cluster",
        )
        def condition_pipeline():
            node1 = hello_world_component_no_paths(component_in_number=1)
            condition(condition=True, false_block=node1)

        pipeline_job = condition_pipeline()
        with include_private_preview_nodes_in_pipeline():
            rest_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(rest_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            "conditionnode": {
                "_source": "DSL",
                "condition": True,
                "false_block": "${{parent.jobs.node1}}",
                "type": "if_else",
            },
            "node1": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "1"}},
                "name": "node1",
                "type": "command",
            },
        }

    def test_registered_component_is_control(self, client: MLClient):
        primitive_component_with_normal_input_output_v2 = load_component(
            source="./tests/test_configs/components/do_while_test/primitive_component_with_normal_input_output_v2.yaml"
        )
        primitive_component_with_normal_input_output_v2.outputs["bool_param_output"].early_available = True
        registered_component = client.components.create_or_update(primitive_component_with_normal_input_output_v2)
        rest_dict = registered_component._to_dict()
        # Assert is_control with correct bool type
        expected_dict = {
            "output_data": {"type": "uri_folder"},
            "bool_param_output": {"type": "boolean", "is_control": True, "early_available": True},
            "int_param_output": {"type": "integer", "is_control": True},
            "float_param_output": {"type": "number", "is_control": True},
            "str_param_output": {"type": "string", "is_control": True},
        }
        assert rest_dict["outputs"] == expected_dict

        # Assert on pipeline component
        @group
        class ControlOutputGroup:
            output_data: Output(type="uri_folder")
            float_param_output: Output(type="number", is_control=True)
            int_param_output: Output(type="integer", is_control=True)
            bool_param_output: Output(type="boolean", is_control=True)
            str_param_output: Output(type="string", is_control=True)

        @pipeline()
        def test_pipeline_component_control_output() -> ControlOutputGroup:
            node = primitive_component_with_normal_input_output_v2(
                input_data=test_input, parambool=True, paramint=2, paramfloat=2.2, paramstr="test"
            )
            return node.outputs

        registered_pipeline_component = client.components.create_or_update(test_pipeline_component_control_output)
        rest_dict = registered_pipeline_component._to_dict()
        assert rest_dict["outputs"] == expected_dict

    def test_do_while_combined_if_else(self, client: MLClient):
        do_while_body_component = load_component(
            source="./tests/test_configs/components/do_while_test/do_while_body_component.yaml"
        )
        primitive_component_with_normal_input_output_v2 = load_component(
            source="./tests/test_configs/components/do_while_test/primitive_component_with_normal_input_output_v2.yaml"
        )

        @pipeline(default_compute_target="cpu-cluster", continue_on_step_failure=True)
        def test_pipeline(input_data, int_param, bool_param, float_param, str_param):
            do_while_body_func = do_while_body_component(
                input_1=input_data,
                input_2=input_data,
                int_param=int_param,
                bool_param=bool_param,
                float_param=float_param,
                str_param=str_param,
            )

            do_while(
                body=do_while_body_func,
                condition=do_while_body_func.outputs.condition,
                mapping={
                    do_while_body_func.outputs.output_1: do_while_body_func.inputs.input_1,
                    do_while_body_func.outputs.output_2: do_while_body_func.inputs.input_2,
                    do_while_body_func.outputs.int_param_output: do_while_body_func.inputs.int_param,
                    do_while_body_func.outputs.bool_param_output: do_while_body_func.inputs.bool_param,
                    do_while_body_func.outputs.float_param_output: do_while_body_func.inputs.float_param,
                    do_while_body_func.outputs.str_param_output: do_while_body_func.inputs.str_param,
                },
                max_iteration_count=3,
            )

            primitive_output_component_true = primitive_component_with_normal_input_output_v2(
                input_data=do_while_body_func.outputs.output_1,
                parambool=do_while_body_func.outputs.bool_param_output,
                paramint=do_while_body_func.outputs.int_param_output,
                paramfloat=do_while_body_func.outputs.float_param_output,
                paramstr=do_while_body_func.outputs.str_param_output,
            )

            condition(condition=do_while_body_func.outputs.condition, true_block=primitive_output_component_true)

        pipeline_job = test_pipeline(
            input_data=test_input, int_param=4, bool_param=True, float_param=22.0, str_param="string_param_no_space"
        )

        with include_private_preview_nodes_in_pipeline():
            rest_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(rest_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            "conditionnode": {
                "_source": "DSL",
                "condition": "${{parent.jobs.do_while_body_func.outputs.condition}}",
                "true_block": "${{parent.jobs.primitive_output_component_true}}",
                "type": "if_else",
            },
            "do_while_body_func": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "inputs": {
                    "bool_param": {"job_input_type": "literal", "value": "${{parent.inputs.bool_param}}"},
                    "float_param": {"job_input_type": "literal", "value": "${{parent.inputs.float_param}}"},
                    "input_1": {"job_input_type": "literal", "value": "${{parent.inputs.input_data}}"},
                    "input_2": {"job_input_type": "literal", "value": "${{parent.inputs.input_data}}"},
                    "int_param": {"job_input_type": "literal", "value": "${{parent.inputs.int_param}}"},
                    "str_param": {"job_input_type": "literal", "value": "${{parent.inputs.str_param}}"},
                },
                "name": "do_while_body_func",
                "type": "command",
            },
            "dowhile": {
                "_source": "DSL",
                "body": "${{parent.jobs.do_while_body_func}}",
                "condition": "condition",
                "limits": {"max_iteration_count": 3},
                "mapping": {
                    "bool_param_output": ["bool_param"],
                    "float_param_output": ["float_param"],
                    "int_param_output": ["int_param"],
                    "output_1": ["input_1"],
                    "output_2": ["input_2"],
                    "str_param_output": ["str_param"],
                },
                "type": "do_while",
            },
            "primitive_output_component_true": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "inputs": {
                    "input_data": {
                        "job_input_type": "literal",
                        "value": "${{parent.jobs.do_while_body_func.outputs.output_1}}",
                    },
                    "parambool": {
                        "job_input_type": "literal",
                        "value": "${{parent.jobs.do_while_body_func.outputs.bool_param_output}}",
                    },
                    "paramfloat": {
                        "job_input_type": "literal",
                        "value": "${{parent.jobs.do_while_body_func.outputs.float_param_output}}",
                    },
                    "paramint": {
                        "job_input_type": "literal",
                        "value": "${{parent.jobs.do_while_body_func.outputs.int_param_output}}",
                    },
                    "paramstr": {
                        "job_input_type": "literal",
                        "value": "${{parent.jobs.do_while_body_func.outputs.str_param_output}}",
                    },
                },
                "name": "primitive_output_component_true",
                "type": "command",
            },
        }

    def test_if_else_multiple_blocks(self, client: MLClient):
        hello_world_component_no_paths = load_component(
            source="./tests/test_configs/components/helloworld_component_no_paths.yml"
        )
        hello_world_component = load_component(source="./tests/test_configs/components/helloworld_component.yml")
        basic_component = load_component(
            source="./tests/test_configs/components/component_with_conditional_output/spec.yaml"
        )

        @pipeline(
            compute="cpu-cluster",
        )
        def condition_pipeline():
            result = basic_component()

            node1 = hello_world_component_no_paths(component_in_number=1)

            node2 = hello_world_component_no_paths(component_in_number=2)
            node3 = hello_world_component(component_in_number=3, component_in_path=test_input)
            node4 = hello_world_component(component_in_number=4, component_in_path=test_input)
            condition(condition=result.outputs.output, false_block=[node1, node3], true_block=[node2, node4])

        pipeline_job = condition_pipeline()
        with include_private_preview_nodes_in_pipeline():
            pipeline_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"]["conditionnode"] == {
            "_source": "DSL",
            "condition": "${{parent.jobs.result.outputs.output}}",
            "false_block": ["${{parent.jobs.node1}}", "${{parent.jobs.node3}}"],
            "true_block": ["${{parent.jobs.node2}}", "${{parent.jobs.node4}}"],
            "type": "if_else",
        }

    @pytest.mark.skipif(condition=not is_live(), reason="TODO(2177353): check why recorded tests failure.")
    def test_if_else_multiple_blocks_subgraph(self, client: MLClient):
        hello_world_component_no_paths = load_component(
            source="./tests/test_configs/components/helloworld_component_no_paths.yml"
        )
        basic_component = load_component(
            source="./tests/test_configs/components/component_with_conditional_output/spec.yaml"
        )

        @pipeline()
        def subgraph():
            hello_world_component_no_paths(component_in_number=2)

        @pipeline(
            compute="cpu-cluster",
        )
        def condition_pipeline():
            result = basic_component()

            node1 = hello_world_component_no_paths(component_in_number=1)

            node2 = subgraph()

            condition(condition=result.outputs.output, true_block=[node1, node2])

        pipeline_job = condition_pipeline()
        with include_private_preview_nodes_in_pipeline():
            pipeline_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"]["conditionnode"] == {
            "_source": "DSL",
            "condition": "${{parent.jobs.result.outputs.output}}",
            "true_block": ["${{parent.jobs.node1}}", "${{parent.jobs.node2}}"],
            "type": "if_else",
        }


@pytest.mark.usefixtures("mock_anon_component_version")
class TestDoWhilePipeline(TestControlFlowPipeline):
    @property
    def _basic_component_func(self):
        return load_component("./tests/test_configs/dsl_pipeline/do_while/basic_component/component.yml")

    @pytest.mark.skipif(
        condition=not is_live(),
        reason="TODO (2374610): hash sanitizer is being applied unnecessarily and forcing playback failures",
    )
    @pytest.mark.usefixtures("mock_anon_component_version")
    def test_do_while_pipeline(self, client: MLClient):
        @pipeline
        def do_while_body_pipeline_component(
            component_in_number: Input(type="integer", optional=True),
            component_in_path: Input(type="uri_folder"),
        ):
            # Call component obj as function: apply given inputs & parameters to create a node in pipeline
            basic_component = self._basic_component_func(
                component_in_number=component_in_number,
                component_in_path=component_in_path,
            )
            return basic_component.outputs

        @pipeline
        def pipeline_with_do_while(
            component_in_number: Input(type="integer"),
            component_in_path: Input(type="uri_folder"),
        ):
            # Do while node with pipeline component
            do_while_body_pipeline = do_while_body_pipeline_component(
                component_in_number=component_in_number,
                component_in_path=component_in_path,
            )
            do_while_with_pipeline = do_while(  # noqa: F841
                body=do_while_body_pipeline,
                condition=do_while_body_pipeline.outputs.is_number_larger_than_zero,
                mapping={
                    do_while_body_pipeline.outputs.output_in_path: do_while_body_pipeline.inputs.component_in_path,
                },
                max_iteration_count=5,
            )

            command_component = self._basic_component_func(
                component_in_number=component_in_number,
                component_in_path=component_in_path,
            )
            do_while_with_command_component = do_while(  # noqa: F841
                body=command_component,
                condition=command_component.outputs.is_number_larger_than_zero,
                mapping={
                    "output_in_number": command_component.inputs.component_in_number,
                    command_component.outputs.output_in_path: command_component.inputs.component_in_path,
                },
                max_iteration_count=5,
            )

            # Use the outputs of do_while node
            basic_component = do_while_body_pipeline_component(
                component_in_number=None,
                component_in_path=command_component.outputs.output_in_path,
            )
            return {"output_in_path": basic_component.outputs.output_in_path}

        pipeline_job = pipeline_with_do_while(
            component_in_number=2,
            component_in_path=Input(type="uri_folder", path=str(Path(__file__).parent)),
        )
        # set pipeline level compute
        pipeline_job.settings.default_compute = "cpu-cluster"

        assert_job_cancel(pipeline_job, client)

    def test_do_while_pipeline_with_primitive_inputs(self, client: MLClient):
        @pipeline
        def do_while_body_pipeline_component(
            component_in_number: Input(type="integer"),
            component_in_number_1: Input(type="integer"),
            component_in_path: Input(type="uri_folder"),
        ):
            """E2E dummy train-score-eval pipeline with components defined via yaml."""
            # Call component obj as function: apply given inputs & parameters to create a node in pipeline
            train_with_sample_data = self._basic_component_func(
                component_in_number=component_in_number,
                component_in_number_1=component_in_number_1,
                component_in_path=component_in_path,
            )
            return train_with_sample_data.outputs

        @pipeline
        def pipeline_with_do_while(
            component_in_number: Input(type="integer"),
            component_in_path: Input(type="uri_folder"),
        ):
            # Do while node with pipeline component
            do_while_body_pipeline = do_while_body_pipeline_component(
                component_in_number=component_in_number,
                component_in_number_1=component_in_number,
                component_in_path=component_in_path,
            )
            do_while_with_pipeline = do_while(  # noqa: F841
                body=do_while_body_pipeline,
                condition=do_while_body_pipeline.outputs.is_number_larger_than_zero,
                mapping={
                    do_while_body_pipeline.outputs.output_in_number: [
                        do_while_body_pipeline.inputs.component_in_number,
                        do_while_body_pipeline.inputs.component_in_number_1,
                    ],
                    "output_in_path": do_while_body_pipeline.inputs.component_in_path,
                },
                max_iteration_count=5,
            )

            command_component = self._basic_component_func(
                component_in_number=component_in_number,
                component_in_number_1=component_in_number,
                component_in_path=component_in_path,
            )
            do_while_with_command_component = do_while(  # noqa: F841
                body=command_component,
                condition=command_component.outputs.is_number_larger_than_zero,
                mapping={
                    "output_in_number": [
                        command_component.inputs.component_in_number,
                        command_component.inputs.component_in_number_1,
                    ],
                    "output_in_path": command_component.inputs.component_in_path,
                },
                max_iteration_count=5,
            )

            # Use the outputs of do_while node
            basic_component = do_while_body_pipeline_component(
                component_in_number=do_while_body_pipeline.outputs.output_in_number,
                component_in_number_1=command_component.outputs.output_in_number,
                component_in_path=do_while_body_pipeline.outputs.output_in_path,
            )
            return {"output_in_path": basic_component.outputs.output_in_path}

        pipeline_job = pipeline_with_do_while(
            component_in_number=2,
            component_in_path=Input(type="uri_folder", path=str(Path(__file__).parent)),
        )
        # set pipeline level compute
        pipeline_job.settings.default_compute = "cpu-cluster"

        assert_job_cancel(pipeline_job, client)


@pytest.mark.skipif(
    condition=is_live(),
    # TODO: reopen live test when parallel_for deployed to canary
    reason="parallel_for is not available in canary.",
)
class TestParallelForPipeline(TestControlFlowPipeline):
    def test_simple_dsl_parallel_for_pipeline(self, client: MLClient):
        hello_world_component = load_component(source="./tests/test_configs/components/helloworld_component.yml")

        @pipeline
        def parallel_for_pipeline():
            parallel_body = hello_world_component(component_in_path=test_input)
            parallel_node = parallel_for(
                body=parallel_body,
                items=[
                    {"component_in_number": 1},
                    {"component_in_number": 2},
                ],
            )
            after_node = hello_world_component(
                component_in_path=parallel_node.outputs.component_out_path,
            )
            after_node.compute = "cpu-cluster"

        pipeline_job = parallel_for_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"

        with include_private_preview_nodes_in_pipeline():
            pipeline_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            "after_node": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "computeId": "cpu-cluster",
                "inputs": {
                    "component_in_path": {
                        "job_input_type": "literal",
                        "value": "${{parent.jobs.parallel_node.outputs.component_out_path}}",
                    }
                },
                "name": "after_node",
                "type": "command",
            },
            "parallel_body": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "inputs": {
                    "component_in_path": {
                        "job_input_type": "uri_file",
                        "uri": "https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
                    }
                },
                "name": "parallel_body",
                "type": "command",
            },
            "parallel_node": {
                "_source": "DSL",
                "body": "${{parent.jobs.parallel_body}}",
                "items": '[{"component_in_number": 1}, ' '{"component_in_number": 2}]',
                "type": "parallel_for",
            },
        }

    def test_dsl_parallel_for_pipeline_unprovided_input(self, client: MLClient):
        hello_world_component = load_component(source="./tests/test_configs/components/helloworld_component_alt1.yml")

        @pipeline
        def parallel_for_pipeline():
            parallel_body = hello_world_component(component_in_path=test_input)
            parallel_node = parallel_for(
                body=parallel_body,
                items=[
                    {"component_in_number": 1},
                    {"component_in_number": 2},
                ],
            )
            after_node = hello_world_component(
                component_in_path=parallel_node.outputs.component_out_path, component_in_number=1
            )
            after_node.compute = "cpu-cluster"

        pipeline_job = parallel_for_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"

        with include_private_preview_nodes_in_pipeline():
            pipeline_job = assert_job_cancel(pipeline_job, client)
        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            "after_node": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "computeId": "cpu-cluster",
                "inputs": {
                    "component_in_number": {"job_input_type": "literal", "value": "1"},
                    "component_in_path": {
                        "job_input_type": "literal",
                        "value": "${{parent.jobs.parallel_node.outputs.component_out_path}}",
                    },
                },
                "name": "after_node",
                "type": "command",
            },
            "parallel_body": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "inputs": {
                    "component_in_path": {
                        "job_input_type": "uri_file",
                        "uri": "https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
                    }
                },
                "name": "parallel_body",
                "type": "command",
            },
            "parallel_node": {
                "_source": "DSL",
                "body": "${{parent.jobs.parallel_body}}",
                "items": '[{"component_in_number": 1}, ' '{"component_in_number": 2}]',
                "type": "parallel_for",
            },
        }

    def test_parallel_for_pipeline_with_subgraph(self, client: MLClient):
        hello_world_component = load_component(source="./tests/test_configs/components/helloworld_component.yml")

        @pipeline
        def sub_graph(component_in_number: int = 10):
            node = hello_world_component(component_in_path=test_input, component_in_number=component_in_number)
            return {"component_out_path": node.outputs.component_out_path}

        @pipeline
        def parallel_for_pipeline():
            parallel_body = sub_graph()
            parallel_node = parallel_for(
                body=parallel_body,
                items=[
                    {"component_in_number": 1},
                    {"component_in_number": 2},
                ],
            )
            after_node = hello_world_component(
                component_in_path=parallel_node.outputs.component_out_path,
            )
            after_node.compute = "cpu-cluster"

        pipeline_job = parallel_for_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"

        with include_private_preview_nodes_in_pipeline():
            pipeline_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            "after_node": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "computeId": "cpu-cluster",
                "inputs": {
                    "component_in_path": {
                        "job_input_type": "literal",
                        "value": "${{parent.jobs.parallel_node.outputs.component_out_path}}",
                    }
                },
                "name": "after_node",
                "type": "command",
            },
            "parallel_body": {"_source": "REMOTE.WORKSPACE.COMPONENT", "name": "parallel_body", "type": "pipeline"},
            "parallel_node": {
                "_source": "DSL",
                "body": "${{parent.jobs.parallel_body}}",
                "items": '[{"component_in_number": 1}, ' '{"component_in_number": 2}]',
                "type": "parallel_for",
            },
        }

    def test_parallel_for_pipeline_subgraph_unprovided_input(self, client: MLClient):
        hello_world_component = load_component(source="./tests/test_configs/components/helloworld_component.yml")

        @pipeline
        def sub_graph(component_in_number: int):
            node = hello_world_component(component_in_path=test_input, component_in_number=component_in_number)
            return {"component_out_path": node.outputs.component_out_path}

        @pipeline
        def parallel_for_pipeline():
            parallel_body = sub_graph()
            parallel_node = parallel_for(
                body=parallel_body,
                items=[
                    {"component_in_number": 1},
                    {"component_in_number": 2},
                ],
            )
            after_node = hello_world_component(
                component_in_path=parallel_node.outputs.component_out_path,
            )
            after_node.compute = "cpu-cluster"

        pipeline_job = parallel_for_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"

        with include_private_preview_nodes_in_pipeline():
            pipeline_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            "after_node": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "computeId": "cpu-cluster",
                "inputs": {
                    "component_in_path": {
                        "job_input_type": "literal",
                        "value": "${{parent.jobs.parallel_node.outputs.component_out_path}}",
                    }
                },
                "name": "after_node",
                "type": "command",
            },
            "parallel_body": {"_source": "REMOTE.WORKSPACE.COMPONENT", "name": "parallel_body", "type": "pipeline"},
            "parallel_node": {
                "_source": "DSL",
                "body": "${{parent.jobs.parallel_body}}",
                "items": '[{"component_in_number": 1}, ' '{"component_in_number": 2}]',
                "type": "parallel_for",
            },
        }

    def test_parallel_for_pipeline_with_port_outputs(self, client: MLClient):
        hello_world_component = load_component(
            source="./tests/test_configs/components/helloworld_component.yml",
            params_override=[
                {
                    "outputs": {
                        "component_out_path": {"type": "uri_folder"},
                        "component_out_file": {"type": "uri_file"},
                        "component_out_table": {"type": "mltable"},
                    }
                }
            ],
        )

        @pipeline
        def parallel_for_pipeline():
            parallel_body = hello_world_component(component_in_path=test_input)
            parallel_node = parallel_for(
                body=parallel_body,
                items=[
                    {"component_in_number": 3},
                    {"component_in_number": 4},
                ],
            )
            return {
                "component_out_path": parallel_node.outputs.component_out_path,
                "component_out_file": parallel_node.outputs.component_out_file,
                "component_out_table": parallel_node.outputs.component_out_table,
            }

        pipeline_job = parallel_for_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"

        with include_private_preview_nodes_in_pipeline():
            pipeline_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            "parallel_body": {
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "inputs": {
                    "component_in_path": {
                        "job_input_type": "uri_file",
                        "uri": "https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
                    }
                },
                "name": "parallel_body",
                "type": "command",
            },
            "parallel_node": {
                "_source": "DSL",
                "body": "${{parent.jobs.parallel_body}}",
                "items": '[{"component_in_number": 3}, ' '{"component_in_number": 4}]',
                "type": "parallel_for",
                "outputs": {
                    "component_out_file": {"type": "literal", "value": "${{parent.outputs.component_out_file}}"},
                    "component_out_path": {"type": "literal", "value": "${{parent.outputs.component_out_path}}"},
                    "component_out_table": {"type": "literal", "value": "${{parent.outputs.component_out_table}}"},
                },
            },
        }
        assert dsl_pipeline_job_dict["properties"]["outputs"] == {
            "component_out_file": {"job_output_type": "mltable", "mode": "ReadWriteMount"},
            "component_out_path": {"job_output_type": "mltable", "mode": "ReadWriteMount"},
            "component_out_table": {"job_output_type": "mltable", "mode": "ReadWriteMount"},
        }

        # parallel for pipeline component is correctly generated
        @pipeline
        def parent_pipeline():
            parallel_for_pipeline()

        pipeline_job = parent_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"

        rest_pipeline_component = pipeline_job.jobs["parallel_for_pipeline"].component._to_rest_object().as_dict()
        assert rest_pipeline_component["properties"]["component_spec"]["outputs"] == {
            "component_out_file": {"type": "mltable"},
            "component_out_path": {"type": "mltable"},
            "component_out_table": {"type": "mltable"},
        }
        assert rest_pipeline_component["properties"]["component_spec"]["jobs"]["parallel_node"] == {
            "body": "${{parent.jobs.parallel_body}}",
            "items": '[{"component_in_number": 3}, {"component_in_number": 4}]',
            "outputs": {
                "component_out_file": {"type": "literal", "value": "${{parent.outputs.component_out_file}}"},
                "component_out_path": {"type": "literal", "value": "${{parent.outputs.component_out_path}}"},
                "component_out_table": {"type": "literal", "value": "${{parent.outputs.component_out_table}}"},
            },
            "type": "parallel_for",
            "_source": "DSL",
        }

        with include_private_preview_nodes_in_pipeline():
            assert_job_cancel(pipeline_job, client)

    def test_parallel_for_pipeline_with_primitive_outputs(self, client: MLClient):
        hello_world_component = load_component(
            source="./tests/test_configs/components/helloworld_component.yml",
            params_override=[
                {
                    "outputs": {
                        "component_out_path": {"type": "uri_folder"},
                        "component_out_number": {"type": "number"},
                        "component_out_boolean": {"type": "boolean", "is_control": True},
                    }
                }
            ],
        )

        @pipeline
        def parallel_for_pipeline():
            parallel_body = hello_world_component(component_in_path=test_input)
            parallel_node = parallel_for(
                body=parallel_body,
                items=[
                    {"component_in_number": 1},
                    {"component_in_number": 2},
                ],
            )
            return {
                "component_out_path": parallel_node.outputs.component_out_path,
                "component_out_number": parallel_node.outputs.component_out_number,
                "component_out_boolean": parallel_node.outputs.component_out_boolean,
            }

        @pipeline
        def parent_pipeline():
            parallel_for_pipeline()

        pipeline_job = parent_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"

        rest_pipeline_component = pipeline_job.jobs["parallel_for_pipeline"].component._to_rest_object().as_dict()
        assert rest_pipeline_component["properties"]["component_spec"]["outputs"] == {
            "component_out_boolean": {"is_control": True, "type": "string"},
            "component_out_number": {"type": "string"},
            "component_out_path": {"type": "mltable"},
        }

        assert rest_pipeline_component["properties"]["component_spec"]["jobs"]["parallel_node"] == {
            "body": "${{parent.jobs.parallel_body}}",
            "items": '[{"component_in_number": 1}, {"component_in_number": 2}]',
            "outputs": {
                "component_out_boolean": {"type": "literal", "value": "${{parent.outputs.component_out_boolean}}"},
                "component_out_number": {"type": "literal", "value": "${{parent.outputs.component_out_number}}"},
                "component_out_path": {"type": "literal", "value": "${{parent.outputs.component_out_path}}"},
            },
            "type": "parallel_for",
            "_source": "DSL",
        }

        # parallel for pipeline component is correctly generated
        with include_private_preview_nodes_in_pipeline():
            assert_job_cancel(pipeline_job, client)

    def test_parallel_for_pipeline_with_empty_inputs(self, client: MLClient):
        hello_world_component = load_component(
            source="./tests/test_configs/components/helloworld_component_no_inputs.yml",
        )

        @pipeline
        def parallel_for_pipeline():
            parallel_body = hello_world_component()
            foreach_config = {}
            for i in range(10):
                foreach_config[f"silo_{i}"] = {}
            parallel_node = parallel_for(body=parallel_body, items=foreach_config)
            return {
                "component_out_path": parallel_node.outputs.component_out_path,
            }

        pipeline_job = parallel_for_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"

        with include_private_preview_nodes_in_pipeline():
            assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            "parallel_body": {"_source": "YAML.COMPONENT", "name": "parallel_body", "type": "command"},
            "parallel_node": {
                "_source": "DSL",
                "body": "${{parent.jobs.parallel_body}}",
                "items": '{"silo_0": {}, "silo_1": {}, "silo_2": {}, '
                '"silo_3": {}, "silo_4": {}, "silo_5": {}, '
                '"silo_6": {}, "silo_7": {}, "silo_8": {}, '
                '"silo_9": {}}',
                "outputs": {
                    "component_out_path": {"type": "literal", "value": "${{parent.outputs.component_out_path}}"}
                },
                "type": "parallel_for",
            },
        }

    def test_parallel_for_pipeline_with_asset_items(self, client: MLClient):
        hello_world_component = load_component(source="./tests/test_configs/components/helloworld_component.yml")

        @pipeline
        def parallel_for_pipeline():
            parallel_body = hello_world_component()
            parallel_node = parallel_for(
                body=parallel_body,
                items=[
                    {"component_in_number": 1, "component_in_path": test_input},
                    {"component_in_number": 2, "component_in_path": test_input},
                ],
            )
            after_node = hello_world_component(
                component_in_path=parallel_node.outputs.component_out_path,
            )

        pipeline_job = parallel_for_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"

        with include_private_preview_nodes_in_pipeline():
            pipeline_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"]["parallel_node"] == {
            "body": "${{parent.jobs.parallel_body}}",
            "items": '[{"component_in_path": {"uri": '
            '"https://dprepdata.blob.core.windows.net/demo/Titanic.csv", '
            '"job_input_type": "uri_file"}, '
            '"component_in_number": 1}, {"component_in_path": '
            '{"uri": '
            '"https://dprepdata.blob.core.windows.net/demo/Titanic.csv", '
            '"job_input_type": "uri_file"}, '
            '"component_in_number": 2}]',
            "type": "parallel_for",
            "_source": "DSL",
        }
