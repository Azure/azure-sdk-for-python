import pytest

from test_utilities.utils import _PYTEST_TIMEOUT_METHOD, omit_with_wildcard, assert_job_cancel
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml.dsl._parallel_for import parallel_for
from azure.ai.ml.dsl._do_while import do_while
from azure.ai.ml import MLClient, load_component, Input
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.dsl._condition import condition

from .._util import include_private_preview_nodes_in_pipeline, _DSL_TIMEOUT_SECOND

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
    "enable_environment_id_arm_expansion",
    "enable_pipeline_private_preview_features",
    "mock_code_hash",
    "mock_asset_name",
    "mock_component_hash",
    "recorded_test",
)
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestControlFlowPipeline(AzureRecordedTestCase):
    pass


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
            result = basic_component(str_param="abc", int_param=1)

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
                "inputs": {
                    "int_param": {"job_input_type": "literal", "value": "1"},
                    "str_param": {"job_input_type": "literal", "value": "abc"},
                },
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
            'conditionnode': {'condition': True,
                              'false_block': '${{parent.jobs.node1}}',
                              'true_block': '${{parent.jobs.node2}}',
                              'type': 'if_else'},
            'node1': {'_source': 'REMOTE.WORKSPACE.COMPONENT',
                      'inputs': {'component_in_number': {'job_input_type': 'literal',
                                                         'value': '1'}},
                      'name': 'node1',
                      'type': 'command'},
            'node2': {'_source': 'REMOTE.WORKSPACE.COMPONENT',
                      'inputs': {'component_in_number': {'job_input_type': 'literal',
                                                         'value': '2'}},
                      'name': 'node2',
                      'type': 'command'}
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
            'conditionnode': {'condition': True,
                              'false_block': '${{parent.jobs.node1}}',
                              'type': 'if_else'},
            'node1': {'_source': 'REMOTE.WORKSPACE.COMPONENT',
                      'inputs': {'component_in_number': {'job_input_type': 'literal',
                                                         'value': '1'}},
                      'name': 'node1',
                      'type': 'command'}
        }

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
                str_param=str_param)

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
                paramstr=do_while_body_func.outputs.str_param_output)

            condition(condition=do_while_body_func.outputs.condition, true_block=primitive_output_component_true)

        pipeline_job = test_pipeline(input_data=test_input, int_param=4, bool_param=True, float_param=22.0,
                                     str_param="string_param_no_space")

        with include_private_preview_nodes_in_pipeline():
            rest_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(rest_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            'conditionnode': {'condition': '${{parent.jobs.do_while_body_func.outputs.condition}}',
                              'true_block': '${{parent.jobs.primitive_output_component_true}}',
                              'type': 'if_else'},
            'do_while_body_func': {'_source': 'REMOTE.WORKSPACE.COMPONENT',
                                   'inputs': {'bool_param': {'job_input_type': 'literal',
                                                             'value': '${{parent.inputs.bool_param}}'},
                                              'float_param': {'job_input_type': 'literal',
                                                              'value': '${{parent.inputs.float_param}}'},
                                              'input_1': {'job_input_type': 'literal',
                                                          'value': '${{parent.inputs.input_data}}'},
                                              'input_2': {'job_input_type': 'literal',
                                                          'value': '${{parent.inputs.input_data}}'},
                                              'int_param': {'job_input_type': 'literal',
                                                            'value': '${{parent.inputs.int_param}}'},
                                              'str_param': {'job_input_type': 'literal',
                                                            'value': '${{parent.inputs.str_param}}'}},
                                   'name': 'do_while_body_func',
                                   'type': 'command'},
            'dowhile': {'body': '${{parent.jobs.do_while_body_func}}',
                        'condition': 'condition',
                        'limits': {'max_iteration_count': 3},
                        'mapping': {'bool_param_output': ['bool_param'],
                                    'float_param_output': ['float_param'],
                                    'int_param_output': ['int_param'],
                                    'output_1': ['input_1'],
                                    'output_2': ['input_2'],
                                    'str_param_output': ['str_param']},
                        'type': 'do_while'},
            'primitive_output_component_true': {
                '_source': 'REMOTE.WORKSPACE.COMPONENT',
                'inputs': {'input_data': {'job_input_type': 'literal',
                                          'value': '${{parent.jobs.do_while_body_func.outputs.output_1}}'},
                           'parambool': {'job_input_type': 'literal',
                                         'value': '${{parent.jobs.do_while_body_func.outputs.bool_param_output}}'},
                           'paramfloat': {'job_input_type': 'literal',
                                          'value': '${{parent.jobs.do_while_body_func.outputs.float_param_output}}'},
                           'paramint': {'job_input_type': 'literal',
                                        'value': '${{parent.jobs.do_while_body_func.outputs.int_param_output}}'},
                           'paramstr': {'job_input_type': 'literal',
                                        'value': '${{parent.jobs.do_while_body_func.outputs.str_param_output}}'}},
                'name': 'primitive_output_component_true',
                'type': 'command'}
        }


class TestParallelForPipeline(TestControlFlowPipeline):
    def test_simple_dsl_parallel_for_pipeline(self, client: MLClient):
        hello_world_component = load_component(
            source="./tests/test_configs/components/helloworld_component.yml"
        )

        @pipeline
        def parallel_for_pipeline():
            parallel_body = hello_world_component(component_in_path=test_input)
            parallel_node = parallel_for(
                body=parallel_body,
                items=[
                    {"component_in_number": 1},
                    {"component_in_number": 2},
                ]
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
            'after_node': {
                '_source': 'REMOTE.WORKSPACE.COMPONENT',
                'computeId': 'cpu-cluster',
                'inputs': {'component_in_path': {'job_input_type': 'literal',
                                                 'value': '${{parent.jobs.parallel_node.outputs.component_out_path}}'}},
                'name': 'after_node',
                'type': 'command'},
            'parallel_body': {
                '_source': 'REMOTE.WORKSPACE.COMPONENT',
                'inputs': {'component_in_path': {'job_input_type': 'uri_file',
                                                 'uri': 'https://dprepdata.blob.core.windows.net/demo/Titanic.csv'}},
                'name': 'parallel_body',
                'type': 'command'},
            'parallel_node': {'body': '${{parent.jobs.parallel_body}}',
                              'items': '[{"component_in_number": 1}, '
                                       '{"component_in_number": 2}]',
                              'type': 'parallel_for'}
        }

    def test_dsl_parallel_for_pipeline_unprovided_input(self, client: MLClient):
        hello_world_component = load_component(
            source="./tests/test_configs/components/helloworld_component_alt1.yml"
        )

        @pipeline
        def parallel_for_pipeline():
            parallel_body = hello_world_component(component_in_path=test_input)
            parallel_node = parallel_for(
                body=parallel_body,
                items=[
                    {"component_in_number": 1},
                    {"component_in_number": 2},
                ]
            )
            after_node = hello_world_component(
                component_in_path=parallel_node.outputs.component_out_path,
                component_in_number=1
            )
            after_node.compute = "cpu-cluster"

        pipeline_job = parallel_for_pipeline()
        pipeline_job.settings.default_compute = "cpu-cluster"

        with include_private_preview_nodes_in_pipeline():
            pipeline_job = assert_job_cancel(pipeline_job, client)

        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"] == {
            'after_node': {
                '_source': 'REMOTE.WORKSPACE.COMPONENT',
                'computeId': 'cpu-cluster',
                'inputs': {'component_in_number': {'job_input_type': 'literal',
                                                   'value': '1'},
                           'component_in_path': {'job_input_type': 'literal',
                                                 'value': '${{parent.jobs.parallel_node.outputs.component_out_path}}'}},
                'name': 'after_node',
                'type': 'command'},
            'parallel_body': {
                '_source': 'REMOTE.WORKSPACE.COMPONENT',
                'inputs': {'component_in_path': {'job_input_type': 'uri_file',
                                                 'uri': 'https://dprepdata.blob.core.windows.net/demo/Titanic.csv'}},
                'name': 'parallel_body',
                'type': 'command'},
            'parallel_node': {'body': '${{parent.jobs.parallel_body}}',
                              'items': '[{"component_in_number": 1}, '
                                       '{"component_in_number": 2}]',
                              'type': 'parallel_for'}
        }

    def test_parallel_for_pipeline_with_subgraph(self, client: MLClient):
        hello_world_component = load_component(
            source="./tests/test_configs/components/helloworld_component.yml"
        )

        @pipeline
        def sub_graph(component_in_number: int = 10):
            node = hello_world_component(component_in_path=test_input, component_in_number=component_in_number)
            return {
                "component_out_path": node.outputs.component_out_path
            }

        @pipeline
        def parallel_for_pipeline():
            parallel_body = sub_graph()
            parallel_node = parallel_for(
                body=parallel_body,
                items=[
                    {"component_in_number": 1},
                    {"component_in_number": 2},
                ]
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
            'after_node': {'_source': 'REMOTE.WORKSPACE.COMPONENT',
                           'computeId': 'cpu-cluster',
                           'inputs': {'component_in_path': {
                               'job_input_type': 'literal',
                               'value': '${{parent.jobs.parallel_node.outputs.component_out_path}}'}},
                           'name': 'after_node',
                           'type': 'command'},
            'parallel_body': {'_source': 'REMOTE.WORKSPACE.COMPONENT',
                              'name': 'parallel_body',
                              'type': 'pipeline'},
            'parallel_node': {'body': '${{parent.jobs.parallel_body}}',
                              'items': '[{"component_in_number": 1}, '
                                       '{"component_in_number": 2}]',
                              'type': 'parallel_for'}
        }

    def test_parallel_for_pipeline_subgraph_unprovided_input(self, client: MLClient):
        hello_world_component = load_component(
            source="./tests/test_configs/components/helloworld_component.yml"
        )

        @pipeline
        def sub_graph(component_in_number: int):
            node = hello_world_component(component_in_path=test_input, component_in_number=component_in_number)
            return {
                "component_out_path": node.outputs.component_out_path
            }

        @pipeline
        def parallel_for_pipeline():
            parallel_body = sub_graph()
            parallel_node = parallel_for(
                body=parallel_body,
                items=[
                    {"component_in_number": 1},
                    {"component_in_number": 2},
                ]
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
            'after_node': {'_source': 'REMOTE.WORKSPACE.COMPONENT',
                           'computeId': 'cpu-cluster',
                           'inputs': {'component_in_path': {
                               'job_input_type': 'literal',
                               'value': '${{parent.jobs.parallel_node.outputs.component_out_path}}'}},
                           'name': 'after_node',
                           'type': 'command'},
            'parallel_body': {'_source': 'REMOTE.WORKSPACE.COMPONENT',
                              'name': 'parallel_body',
                              'type': 'pipeline'},
            'parallel_node': {'body': '${{parent.jobs.parallel_body}}',
                              'items': '[{"component_in_number": 1}, '
                                       '{"component_in_number": 2}]',
                              'type': 'parallel_for'}
        }
