import pytest

from azure.ai.ml import Input, load_component
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.dsl._parallel_for import parallel_for
from azure.ai.ml.entities import Command
from azure.ai.ml.exceptions import UserErrorException, ValidationException

from .._util import _DSL_TIMEOUT_SECOND, include_private_preview_nodes_in_pipeline


@pytest.mark.usefixtures(
    "enable_pipeline_private_preview_features",
    "enable_private_preview_schema_features"
)
@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestControlFlowPipelineUT:
    pass


class TestParallelForPipelineUT(TestControlFlowPipelineUT):
    def test_dsl_parallel_for_pipeline_illegal_cases(self):
        # body unsupported
        parallel_component = load_component(
            source="./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/score.yml")

        basic_component = load_component(
            source="./tests/test_configs/components/component_with_conditional_output/spec.yaml"
        )

        @pipeline
        def invalid_pipeline(test_path1, test_path2):
            body = parallel_component()
            parallel_for(
                body=body,
                items=[
                    {"job_data_path": test_path1},
                    {"job_data_path": test_path2}
                ],
            )

        with pytest.raises(ValidationException) as e:
            invalid_pipeline(
                test_path1=Input(path="test_path1"),
                test_path2=Input(path="test_path2")
            )
        assert "Expecting (<class 'azure.ai.ml.entities._builders.command.Command'>, " \
               "<class 'azure.ai.ml.entities._builders.pipeline.Pipeline'>) for body" in str(e.value)

        # items with invalid type

        @pipeline
        def invalid_pipeline():
            body = basic_component()
            parallel_for(
                body=body,
                items=1,
            )

        with pytest.raises(ValidationException) as e:
            invalid_pipeline()

        assert "got <class 'int'> instead." in str(e.value)

    @pytest.mark.parametrize(
        "items, error_message",
        [
            (
                    # items with invalid content type
                    {"a": 1},
                    "but got <class 'int'> for 1.",
            ),
            (
                    # items with empty dict as content
                    [],
                    "Items is an empty list/dict"

            ),
            (
                    # items with empty dict as content
                    [{}],
                    "but got <class \'dict\'> for {}"
            ),
            (
                    # item meta not match
                    [
                        {"component_in_path": "test_path1"},
                        {"component_in_path": "test_path2", "component_in_number": 1}
                    ],
                    "Items should to have same keys with body inputs, but got "
            ),
            (
                    # item inputs not exist in body
                    [
                        {"job_data_path": "test_path1"},
                    ],
                    "Item {\'job_data_path\': \'test_path1\'} got unmatched inputs "
            ),
            (
                    # invalid JSON string items

                    '[{"component_in_number": 1}, {}]',
                    "Items has to be list/dict of non-empty dict as value"
            )
        ],
    )
    def test_dsl_parallel_for_pipeline_illegal_items_content(self, items, error_message):
        basic_component = load_component(
            source="./tests/test_configs/components/helloworld_component.yml"
        )

        @pipeline
        def invalid_pipeline():
            body = basic_component()
            parallel_for(
                body=body,
                items=items,
            )

        with pytest.raises(ValidationException) as e:
            invalid_pipeline()
        assert error_message in str(e.value)

    def test_dsl_parallel_for_pipeline_items(self):
        # TODO: submit those pipelines

        basic_component = load_component(
            source="./tests/test_configs/components/helloworld_component.yml"
        )
        complex_component = load_component(
            source="./tests/test_configs/components/input_types_component.yml"
        )

        # binding in items

        @pipeline
        def my_pipeline(test_path1, test_path2):
            body = basic_component()
            parallel_for(
                body=body,
                items=[
                    {"component_in_path": test_path1},
                    {"component_in_path": test_path2}
                ],
            )

        my_job = my_pipeline(
            test_path1=Input(path="test_path1"),
            test_path2=Input(path="test_path2")
        )
        rest_job = my_job._to_rest_object().as_dict()
        rest_items = rest_job["properties"]["jobs"]["parallelfor"]["items"]
        assert rest_items == '[{"component_in_path": "${{parent.inputs.test_path1}}"}, ' \
                             '{"component_in_path": "${{parent.inputs.test_path2}}"}]'

        # dict items
        @pipeline
        def my_pipeline():
            body = basic_component(component_in_path=Input(path="test_path1"))
            parallel_for(
                body=body,
                items={
                    "iter1": {"component_in_number": 1},
                    "iter2": {"component_in_number": 2}
                }
            )

        my_job = my_pipeline()
        rest_job = my_job._to_rest_object().as_dict()
        rest_items = rest_job["properties"]["jobs"]["parallelfor"]["items"]
        assert rest_items == '{"iter1": {"component_in_number": 1}, "iter2": {"component_in_number": 2}}'

        # binding items
        @pipeline
        def my_pipeline(pipeline_input: str):
            body = basic_component(component_in_path=Input(path="test_path1"))
            parallel_for(
                body=body,
                items=pipeline_input
            )

        my_job = my_pipeline(pipeline_input='[{"component_in_number": 1}, {"component_in_number": 2}]')
        rest_job = my_job._to_rest_object().as_dict()
        rest_items = rest_job["properties"]["jobs"]["parallelfor"]["items"]
        assert rest_items == "${{parent.inputs.pipeline_input}}"

        # serialized string as items
        @pipeline
        def my_pipeline():
            body = basic_component(component_in_path=Input(path="test_path1"))
            parallel_for(
                body=body,
                items='[{"component_in_number": 1}, {"component_in_number": 2}]'
            )

        my_job = my_pipeline()
        rest_job = my_job._to_rest_object().as_dict()
        rest_items = rest_job["properties"]["jobs"]["parallelfor"]["items"]
        assert rest_items == '[{"component_in_number": 1}, {"component_in_number": 2}]'

        # complicated input types as items
        @pipeline
        def my_pipeline():
            body = complex_component()
            parallel_for(
                body=body,
                items=[
                    dict(
                        component_in_string="component_in_string",
                        component_in_ranged_integer=10,
                        component_in_enum="world",
                        component_in_boolean=True,
                        component_in_ranged_number=5.5),
                ]
            )

        my_job = my_pipeline()
        rest_job = my_job._to_rest_object().as_dict()
        rest_items = rest_job["properties"]["jobs"]["parallelfor"]["items"]
        assert rest_items == '[{"component_in_string": "component_in_string", ' \
                             '"component_in_ranged_integer": 10, "component_in_enum": "world", ' \
                             '"component_in_boolean": true, "component_in_ranged_number": 5.5}]'

        # JSON string items
        @pipeline
        def my_pipeline():
            body = basic_component(component_in_path=Input(path="test_path1"))
            parallel_for(
                body=body,
                items='[{"component_in_number": 1}, {"component_in_number": 2}]'
            )

        my_job = my_pipeline()
        rest_job = my_job._to_rest_object().as_dict()
        rest_items = rest_job["properties"]["jobs"]["parallelfor"]["items"]
        assert rest_items == '[{"component_in_number": 1}, {"component_in_number": 2}]'

    @pytest.mark.parametrize(
        "output_dict, pipeline_out_dict, component_out_dict, check_pipeline_job",
        [
            ({"type": "uri_file"}, {'job_output_type': 'mltable'}, {'type': 'mltable'}, True),
            ({"type": "uri_folder"}, {'job_output_type': 'mltable'}, {'type': 'mltable'}, True),
            ({"type": "mltable"}, {'job_output_type': 'mltable'}, {'type': 'mltable'}, True),
            ({"type": "number"}, {}, {'type': 'string'}, False),
            ({"type": "string", "is_control": True}, {}, {'type': 'string', "is_control": True}, False),
            ({"type": "boolean", "is_control": True}, {}, {'type': 'string', "is_control": True}, False),
            ({"type": "integer"}, {}, {'type': 'string'}, False),
        ]
    )
    def test_parallel_for_outputs(self, output_dict, pipeline_out_dict, component_out_dict, check_pipeline_job):
        basic_component = load_component(
            source="./tests/test_configs/components/helloworld_component.yml",
            params_override=[
                {"outputs.component_out_path": output_dict}
            ]
        )

        @pipeline
        def my_pipeline():
            body = basic_component(component_in_path=Input(path="test_path1"))

            foreach_node = parallel_for(
                body=body,
                items={
                    "iter1": {"component_in_number": 1},
                    "iter2": {"component_in_number": 2}
                }
            )
            return {
                "output": foreach_node.outputs.component_out_path
            }

        my_job = my_pipeline()

        if check_pipeline_job:
            rest_job = my_job._to_rest_object().as_dict()
            rest_outputs = rest_job["properties"]["outputs"]
            assert rest_outputs == {'output': pipeline_out_dict}

        pipeline_component = my_job.component
        rest_component = pipeline_component._to_rest_object().as_dict()
        assert rest_component["properties"]["component_spec"]["outputs"] == {'output': component_out_dict}

    @pytest.mark.parametrize(
        "out_type", ["mlflow_model", "triton_model", "custom_model"]
    )
    def test_parallel_for_output_unsupported_case(self, out_type):
        basic_component = load_component(
            source="./tests/test_configs/components/helloworld_component.yml",
            params_override=[
                {"outputs.component_out_path": {"type": out_type}}
            ]
        )

        @pipeline
        def my_pipeline():
            body = basic_component(component_in_path=Input(path="test_path1"))

            parallel_for(
                body=body,
                items={
                    "iter1": {"component_in_number": 1},
                    "iter2": {"component_in_number": 2}
                }
            )

        with pytest.raises(UserErrorException) as e:
            my_pipeline()
        assert f"Referencing output with type {out_type} is not supported" in str(e.value)
