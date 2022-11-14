import pytest

from azure.ai.ml import load_component, Input
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.dsl._parallel_for import parallel_for
from azure.ai.ml.exceptions import ValidationException
from .._util import _DSL_TIMEOUT_SECOND, include_private_preview_nodes_in_pipeline


@pytest.mark.usefixtures(
    "enable_pipeline_private_preview_features",
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
        # items unsupported

        basic_component = load_component(
            source="./tests/test_configs/components/component_with_conditional_output/spec.yaml"
        )

        @pipeline
        def invalid_pipeline():
            body = basic_component()
            parallel_for(
                body=body,
                items=1,
            )

        invalid_pipeline()

        # invalid items

        # item inputs not exist in body
        pass

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
