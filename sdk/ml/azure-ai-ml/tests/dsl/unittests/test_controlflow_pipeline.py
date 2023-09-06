from pathlib import Path

import pytest
from marshmallow import ValidationError
from test_utilities.utils import omit_with_wildcard

from azure.ai.ml import Input, load_component
from azure.ai.ml.constants._component import ComponentSource
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.dsl._condition import condition
from azure.ai.ml.dsl._do_while import do_while
from azure.ai.ml.dsl._group_decorator import group
from azure.ai.ml.dsl._parallel_for import parallel_for
from azure.ai.ml.entities._builders.parallel_for import ParallelFor
from azure.ai.ml.entities._job.pipeline._io import InputOutputBase, PipelineInput
from azure.ai.ml.exceptions import ValidationException

from .._util import _DSL_TIMEOUT_SECOND


@pytest.mark.usefixtures(
    "enable_pipeline_private_preview_features",
    "enable_private_preview_schema_features",
    "enable_private_preview_pipeline_node_types",
)
@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestControlFlowPipelineUT:
    pass


class CustomizedObject:
    pass


class TestIfElseUT(TestControlFlowPipelineUT):
    def test_multiblock_if_else(self):
        hello_world_component_no_paths = load_component(
            source="./tests/test_configs/components/helloworld_component_no_paths.yml"
        )
        basic_component = load_component(
            source="./tests/test_configs/components/component_with_conditional_output/spec.yaml"
        )

        @pipeline()
        def condition_pipeline():
            result = basic_component()
            node1 = hello_world_component_no_paths(component_in_number=1)
            node2 = hello_world_component_no_paths(component_in_number=2)
            condition(condition=result.outputs.output, false_block=[node1, node2])

        pipeline_job = condition_pipeline()
        rest_pipeline_job = pipeline_job._to_rest_object().as_dict()
        assert rest_pipeline_job["properties"]["jobs"]["conditionnode"] == {
            "_source": "DSL",
            "condition": "${{parent.jobs.result.outputs.output}}",
            "false_block": ["${{parent.jobs.node1}}", "${{parent.jobs.node2}}"],
            "type": "if_else",
        }

    def test_if_else_validate(self):
        hello_world_component_no_paths = load_component(
            source="./tests/test_configs/components/helloworld_component_no_paths.yml"
        )
        basic_component = load_component(
            source="./tests/test_configs/components/component_with_conditional_output/spec.yaml"
        )

        @pipeline(compute="cpu-cluster")
        def condition_pipeline():
            result = basic_component()
            node1 = hello_world_component_no_paths(component_in_number=1)
            node2 = hello_world_component_no_paths(component_in_number=2)
            # true block and false block has intersection
            condition(condition=result.outputs.output, false_block=[node1, node2], true_block=[node1])

        with pytest.raises(ValidationError) as e:
            pipeline_job = condition_pipeline()
            pipeline_job._validate(raise_error=True)
        assert "True block and false block cannot contain same nodes: {'${{parent.jobs.node1}}'" in str(e.value)

        @pipeline(compute="cpu-cluster")
        def condition_pipeline():
            result = basic_component()
            node1 = hello_world_component_no_paths()
            node2 = hello_world_component_no_paths()
            # true block and false block has intersection
            condition(condition=result.outputs.output, false_block=[node1], true_block=[node2])

        # no error raise
        pipeline_job = condition_pipeline()
        pipeline_job._validate(raise_error=True)

    def test_create_dsl_condition_illegal_cases(self):
        basic_component = load_component(
            source="./tests/test_configs/components/component_with_conditional_output/spec.yaml"
        )
        basic_node = basic_component()

        with pytest.raises(ValidationException) as e:
            node = condition(condition=1, true_block=basic_node)
            node._validate(raise_error=True)

        assert f"must be an instance of {str}, {bool} or {InputOutputBase}" in str(e.value)

        node = condition(condition=basic_node.outputs.output3, true_block=basic_node)
        node._validate(raise_error=True)

        with pytest.raises(ValidationError) as e:
            node = condition(condition="${{parent.jobs.xxx.outputs.output}}")
            node._validate(raise_error=True)

        assert "True block and false block cannot be empty at the same time." in str(e.value)

        with pytest.raises(ValidationError) as e:
            node = condition(
                condition="${{parent.jobs.xxx.outputs.output}}", true_block=basic_node, false_block=basic_node
            )
            node._validate(raise_error=True)

        assert "True block and false block cannot contain same nodes" in str(e.value)

        with pytest.raises(ValidationException) as e:
            node = condition(condition="xxx", true_block=basic_node)
            node._validate(raise_error=True)

        assert "condition has invalid binding expression: xxx" in str(e.value)

    def test_condition_node(self):
        hello_world_component_no_paths = load_component(
            source="./tests/test_configs/components/helloworld_component_no_paths.yml"
        )
        node1 = hello_world_component_no_paths()
        node1.name = "node1"
        node2 = hello_world_component_no_paths()
        node2.name = "node2"
        control_node = condition(
            condition="${{parent.jobs.condition_predicate.outputs.output}}", false_block=node1, true_block=node2
        )
        assert control_node._to_rest_object() == {
            "_source": "DSL",
            "condition": "${{parent.jobs.condition_predicate.outputs.output}}",
            "false_block": "${{parent.jobs.node1}}",
            "true_block": "${{parent.jobs.node2}}",
            "type": "if_else",
        }

        # test boolean type condition
        control_node = condition(condition=True, false_block=node1, true_block=node2)
        assert control_node._to_rest_object() == {
            "_source": "DSL",
            "condition": True,
            "false_block": "${{parent.jobs.node1}}",
            "true_block": "${{parent.jobs.node2}}",
            "type": "if_else",
        }

    def test_condition_pipeline(self):
        basic_component = load_component(
            source="./tests/test_configs/components/component_with_conditional_output/spec.yaml"
        )

        hello_world_component_no_paths = load_component(
            source="./tests/test_configs/components/helloworld_component_no_paths.yml"
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
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.*.componentId",
            "properties.settings",
        ]
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
                "_source": "YAML.COMPONENT",
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "1"}},
                "name": "node1",
                "type": "command",
            },
            "node2": {
                "_source": "YAML.COMPONENT",
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "2"}},
                "name": "node2",
                "type": "command",
            },
            "result": {"_source": "YAML.COMPONENT", "name": "result", "type": "command"},
        }

    def test_condition_with_group_input(self):
        hello_world_component_no_paths = load_component(
            source=r"./tests/test_configs/components/helloworld_component_no_paths.yml"
        )

        @group
        class SubGroup:
            num: int

        @group
        class ParentGroup:
            input_group: SubGroup

        @pipeline(
            compute="cpu-cluster",
        )
        def condition_pipeline(group_input: ParentGroup):
            node1 = hello_world_component_no_paths(component_in_number=1)
            condition(condition=group_input.input_group.num < 100, true_block=node1)

        pipeline_job = condition_pipeline(group_input=ParentGroup(input_group=SubGroup(num=10)))
        omit_fields = [
            "name",
            "properties.display_name",
            "properties.jobs.*.componentId",
            "properties.settings",
        ]
        dsl_pipeline_job_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict(), *omit_fields)
        assert dsl_pipeline_job_dict["properties"]["jobs"]["expression_component"] == {
            "environment_variables": {"AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED": "true"},
            "name": "expression_component",
            "type": "command",
            "inputs": {"num": {"job_input_type": "literal", "value": "${{parent.inputs.group_input.input_group.num}}"}},
            "_source": "YAML.COMPONENT",
        }


class TestDoWhilePipelineUT(TestControlFlowPipelineUT):
    def test_invalid_do_while_pipeline(self):
        basic_component_func = load_component(
            "./tests/test_configs/dsl_pipeline/do_while/basic_component/component.yml"
        )

        @pipeline
        def do_while_body_pipeline_component(
            component_in_number: Input(type="integer", optional=True),
            component_in_number_1: Input(type="integer", optional=True),
            component_in_path: Input(type="uri_folder"),
        ):
            """E2E dummy train-score-eval pipeline with components defined via yaml."""
            # Call component obj as function: apply given inputs & parameters to create a node in pipeline
            train_with_sample_data = basic_component_func(
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
            # Create two training pipeline component with different learning rate
            do_while_body_pipeline_1 = do_while_body_pipeline_component(
                component_in_number=component_in_number,
                component_in_number_1=component_in_number,
                component_in_path=component_in_path,
            )
            empty_mapping = do_while(  # noqa: F841
                body=do_while_body_pipeline_1,
                condition=do_while_body_pipeline_1.outputs.is_number_larger_than_zero,
                mapping=None,
                max_iteration_count=5,
            )

            do_while_body_pipeline_2 = do_while_body_pipeline_component(  # noqa: F841
                component_in_number=component_in_number,
                component_in_number_1=component_in_number,
                component_in_path=component_in_path,
            )
            out_of_max_iteration_count_range = do_while(  # noqa: F841
                body=do_while_body_pipeline_2,
                condition=do_while_body_pipeline_2.outputs.is_number_larger_than_zero,
                mapping={
                    do_while_body_pipeline_2.outputs.output_in_number: [
                        do_while_body_pipeline_2.inputs.component_in_number,
                        do_while_body_pipeline_2.inputs.component_in_number_1,
                    ],
                    do_while_body_pipeline_2.outputs.output_in_path: do_while_body_pipeline_2.inputs.component_in_path,
                },
                max_iteration_count=1001,
            )

            body_in_other_loop = do_while(  # noqa: F841
                body=do_while_body_pipeline_1,
                condition=do_while_body_pipeline_1.outputs.is_number_larger_than_zero,
                mapping={
                    do_while_body_pipeline_1.outputs.output_in_number: [
                        do_while_body_pipeline_1.inputs.component_in_number,
                        do_while_body_pipeline_1.inputs.component_in_number_1,
                    ],
                    do_while_body_pipeline_1.outputs.output_in_path: do_while_body_pipeline_1.inputs.component_in_path,
                },
                max_iteration_count=5,
            )

            do_while_body_pipeline_3 = do_while_body_pipeline_component(
                component_in_number=component_in_number,
                component_in_number_1=component_in_number,
                component_in_path=component_in_path,
            )
            invalid_mapping = do_while(  # noqa: F841
                body=do_while_body_pipeline_3,
                condition=do_while_body_pipeline_1.outputs.is_number_larger_than_zero,
                mapping={
                    do_while_body_pipeline_3.outputs.output_in_number: [
                        do_while_body_pipeline_3.inputs.component_in_number,
                        do_while_body_pipeline_1.inputs.component_in_number_1,
                    ],
                    do_while_body_pipeline_1.outputs.output_in_path: do_while_body_pipeline_1.outputs.output_in_path,
                },
                max_iteration_count=5,
            )

            do_while_body_pipeline_4 = do_while_body_pipeline_component(
                component_in_number=component_in_number,
                component_in_number_1=component_in_number,
                component_in_path=component_in_path,
            )
            invalid_condition = do_while(  # noqa: F841
                body=do_while_body_pipeline_4,
                condition=do_while_body_pipeline_4.outputs.output_in_path,
                mapping={
                    do_while_body_pipeline_4.outputs.output_in_number: [
                        do_while_body_pipeline_4.inputs.component_in_number,
                        do_while_body_pipeline_4.inputs.component_in_number_1,
                    ]
                },
                max_iteration_count=5,
            )

        pipeline_job = pipeline_with_do_while(
            component_in_number=2,
            component_in_path=Input(type="uri_folder", path=str(Path(__file__).parent)),
        )
        # set pipeline level compute
        pipeline_job.settings.default_compute = "cpu-cluster"
        result = pipeline_job._customized_validate()
        validate_errors = result._to_dict()["errors"]

        def validate_error_message(expect_errors, validate_errors):
            for path, msg in expect_errors.items():
                acture_errors = list(filter(lambda error: error["path"] == path, validate_errors))
                assert acture_errors, f"Cannot find the error of {path} in validation results."
                for acture_error in acture_errors:
                    assert acture_error["message"] in msg

        expect_errors = {
            "jobs.empty_mapping.mapping": ["Missing data for required field."],
            "jobs.out_of_max_iteration_count_range.limit.max_iteration_count": [
                "The max iteration count cannot be less than 0 or larger than 1000."
            ],
            "jobs.body_in_other_loop.body": ["The body of loop node cannot be promoted as another loop again."],
            "jobs.invalid_mapping.condition": [
                "is_number_larger_than_zero is the output of do_while_body_pipeline_1, dowhile only accept output of the body: do_while_body_pipeline_3."
            ],
            "jobs.invalid_mapping.mapping": [
                "component_in_number_1 is the input of do_while_body_pipeline_1, dowhile only accept input of the body: do_while_body_pipeline_3.",
                "output_in_path is the output of do_while_body_pipeline_1, dowhile only accept output of the body: do_while_body_pipeline_3.",
            ],
            "jobs.invalid_condition.condition": [
                "output_in_path is not a control output and is not primitive type. The condition of dowhile must be the control output or primitive type of the body."
            ],
        }
        validate_error_message(expect_errors, validate_errors)

    def test_infer_dynamic_input_type_from_mapping(self):
        # Pass None to dynamic input in do-while loop body, and provide it in mapping for next iteration,
        # which is a valid case in federated learning.
        from test_configs.dsl_pipeline.dynamic_input_do_while.pipeline import pipeline_job

        assert pipeline_job._customized_validate().passed
        # assert input type of loop body, should both have type now
        assert pipeline_job.jobs["loop_body"].inputs.required_input.type == "uri_folder"
        assert pipeline_job.jobs["loop_body"].inputs.optional_input.type == "uri_folder"


class TestParallelForPipelineUT(TestControlFlowPipelineUT):
    # Need to disable internal components or internal nodes will be in allowed node types
    @pytest.mark.usefixtures("disable_internal_components")
    def test_dsl_parallel_for_pipeline_illegal_cases(self):
        # body unsupported
        parallel_component = load_component(
            source="./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/score.yml"
        )

        basic_component = load_component(
            source="./tests/test_configs/components/component_with_conditional_output/spec.yaml"
        )

        @pipeline
        def invalid_pipeline(test_path1, test_path2):
            body = parallel_component()
            parallel_for(
                body=body,
                items=[{"job_data_path": test_path1}, {"job_data_path": test_path2}],
            )

        with pytest.raises(ValidationException) as e:
            invalid_pipeline(test_path1=Input(path="test_path1"), test_path2=Input(path="test_path2"))
        assert (
            "Expecting (<class 'azure.ai.ml.entities._builders.command.Command'>, "
            "<class 'azure.ai.ml.entities._builders.pipeline.Pipeline'>) for body" in str(e.value)
        )

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
                "Items is an empty list/dict",
            ),
            (
                # item meta not match
                [{"component_in_path": "test_path1"}, {"component_in_path": "test_path2", "component_in_number": 1}],
                "Items should have same keys with body inputs, but got ",
            ),
            (
                # item inputs not exist in body
                [
                    {"job_data_path": "test_path1"},
                ],
                "Item {'job_data_path': 'test_path1'} got unmatched inputs ",
            ),
            (
                # invalid JSON string items
                '[{"component_in_number": 1}, {}]',
                "Items should have same keys with body inputs",
            ),
            (
                # unsupported item value type
                [
                    {"component_in_number": CustomizedObject()},
                ],
                "Unsupported type",
            ),
            (
                # local file input
                [{"component_in_path": Input(path="./tests/test_configs/components/helloworld_component.yml")}],
                "Local file input",
            ),
            (
                # empty path
                [{"component_in_path": Input(path=None)}],
                "Input path not provided",
            ),
            (
                # dict Input
                [{"component_in_path": {"job_input_path": "azureml://path/to/file"}}],
                "Unsupported type",
            ),
        ],
    )
    def test_dsl_parallel_for_pipeline_illegal_items_content(self, items, error_message):
        basic_component = load_component(source="./tests/test_configs/components/helloworld_component.yml")

        @pipeline
        def invalid_pipeline():
            body = basic_component()
            parallel_for(
                body=body,
                items=items,
            )

        with pytest.raises(ValidationException) as e:
            pipeline_job = invalid_pipeline()
            pipeline_job._validate(raise_error=True)
        assert error_message in str(e.value)

    @pytest.mark.parametrize(
        "items",
        (
            # items with empty dict as content
            [{}],
        ),
    )
    def test_dsl_parallel_for_pipeline_legal_items_content(self, items):
        basic_component = load_component(source="./tests/test_configs/components/helloworld_component.yml")

        @pipeline
        def valid_pipeline():
            body = basic_component()
            parallel_for(
                body=body,
                items=items,
            )

        valid_pipeline()

    def test_dsl_parallel_for_pipeline_items(self):
        # TODO: submit those pipelines

        basic_component = load_component(source="./tests/test_configs/components/helloworld_component.yml")
        complex_component = load_component(source="./tests/test_configs/components/input_types_component.yml")

        # binding in items

        @pipeline
        def my_pipeline(test_path1, test_path2):
            body = basic_component()
            parallel_for(
                body=body,
                items=[{"component_in_path": test_path1}, {"component_in_path": test_path2}],
            )

        my_job = my_pipeline(test_path1=Input(path="test_path1"), test_path2=Input(path="test_path2"))
        rest_job = my_job._to_rest_object().as_dict()
        rest_items = rest_job["properties"]["jobs"]["parallelfor"]["items"]
        assert (
            rest_items == '[{"component_in_path": "${{parent.inputs.test_path1}}"}, '
            '{"component_in_path": "${{parent.inputs.test_path2}}"}]'
        )

        # dict items
        @pipeline
        def my_pipeline():
            body = basic_component(component_in_path=Input(path="test_path1"))
            parallel_for(body=body, items={"iter1": {"component_in_number": 1}, "iter2": {"component_in_number": 2}})

        my_job = my_pipeline()
        rest_job = my_job._to_rest_object().as_dict()
        rest_items = rest_job["properties"]["jobs"]["parallelfor"]["items"]
        assert rest_items == '{"iter1": {"component_in_number": 1}, "iter2": {"component_in_number": 2}}'

        # binding items
        @pipeline
        def my_pipeline(pipeline_input: str):
            body = basic_component(component_in_path=Input(path="test_path1"))
            parallel_for(body=body, items=pipeline_input)

        my_job = my_pipeline(pipeline_input='[{"component_in_number": 1}, {"component_in_number": 2}]')
        rest_job = my_job._to_rest_object().as_dict()
        rest_items = rest_job["properties"]["jobs"]["parallelfor"]["items"]
        assert rest_items == "${{parent.inputs.pipeline_input}}"

        # serialized string as items
        @pipeline
        def my_pipeline():
            body = basic_component(component_in_path=Input(path="test_path1"))
            parallel_for(body=body, items='[{"component_in_number": 1}, {"component_in_number": 2}]')

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
                        component_in_ranged_number=5.5,
                    ),
                ],
            )

        my_job = my_pipeline()
        rest_job = my_job._to_rest_object().as_dict()
        rest_items = rest_job["properties"]["jobs"]["parallelfor"]["items"]
        assert (
            rest_items == '[{"component_in_string": "component_in_string", '
            '"component_in_ranged_integer": 10, "component_in_enum": "world", '
            '"component_in_boolean": true, "component_in_ranged_number": 5.5}]'
        )

        # JSON string items
        @pipeline
        def my_pipeline():
            body = basic_component(component_in_path=Input(path="test_path1"))
            parallel_for(body=body, items='[{"component_in_number": 1}, {"component_in_number": 2}]')

        my_job = my_pipeline()
        rest_job = my_job._to_rest_object().as_dict()
        rest_items = rest_job["properties"]["jobs"]["parallelfor"]["items"]
        assert rest_items == '[{"component_in_number": 1}, {"component_in_number": 2}]'

    @pytest.mark.parametrize(
        "output_dict, pipeline_out_dict, component_out_dict, check_pipeline_job",
        [
            ({"type": "uri_file"}, {"job_output_type": "mltable"}, {"type": "mltable"}, True),
            ({"type": "uri_folder"}, {"job_output_type": "mltable"}, {"type": "mltable"}, True),
            ({"type": "mltable"}, {"job_output_type": "mltable"}, {"type": "mltable"}, True),
            ({"type": "mlflow_model"}, {"job_output_type": "mltable"}, {"type": "mltable"}, True),
            ({"type": "triton_model"}, {"job_output_type": "mltable"}, {"type": "mltable"}, True),
            ({"type": "custom_model"}, {"job_output_type": "mltable"}, {"type": "mltable"}, True),
            ({"type": "path"}, {"job_output_type": "mltable"}, {"type": "mltable"}, True),
            ({"type": "number"}, {}, {"type": "string"}, False),
            ({"type": "string"}, {}, {"type": "string"}, False),
            ({"type": "boolean"}, {}, {"type": "string"}, False),
            ({"type": "integer"}, {}, {"type": "string"}, False),
        ],
    )
    def test_parallel_for_outputs(self, output_dict, pipeline_out_dict, component_out_dict, check_pipeline_job):
        basic_component = load_component(
            source="./tests/test_configs/components/helloworld_component.yml",
            params_override=[{"outputs.component_out_path": output_dict}],
        )

        @pipeline
        def my_pipeline():
            body = basic_component(component_in_path=Input(path="test_path1"))

            foreach_node = parallel_for(
                body=body, items={"iter1": {"component_in_number": 1}, "iter2": {"component_in_number": 2}}
            )
            return {"output": foreach_node.outputs.component_out_path}

        my_job = my_pipeline()

        if check_pipeline_job:
            rest_job = my_job._to_rest_object().as_dict()
            rest_outputs = rest_job["properties"]["outputs"]
            assert rest_outputs == {"output": pipeline_out_dict}

        pipeline_component = my_job.component
        rest_component = pipeline_component._to_rest_object().as_dict()
        assert rest_component["properties"]["component_spec"]["outputs"] == {"output": component_out_dict}

    def test_parallel_for_source(self):
        basic_component = load_component(
            source="./tests/test_configs/components/helloworld_component.yml",
        )

        @pipeline
        def my_pipeline():
            body = basic_component(component_in_path=Input(path="test_path1"))

            foreach_node = parallel_for(
                body=body, items={"iter1": {"component_in_number": 1}, "iter2": {"component_in_number": 2}}
            )

        my_job = my_pipeline()
        assert my_job.jobs["foreach_node"]._source == ComponentSource.DSL

    @pytest.mark.parametrize(
        "items, rest_input_str",
        [
            (
                # asset input with path on datastore
                {
                    "silo1": {"uri_file_input": Input(path="path/on/datastore")},
                },
                '{"silo1": {"uri_file_input": {"uri": "path/on/datastore", "job_input_type": "uri_folder"}}}',
            ),
            (
                # asset input with name + version
                {
                    "silo1": {"name_version": Input(path="test-data:1")},
                },
                '{"silo1": {"name_version": {"uri": "test-data:1", "job_input_type": "uri_folder"}}}',
            ),
            (
                # asset input with uri
                {
                    "silo1": {"uri": Input(path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv")},
                },
                '{"silo1": {"uri": {"uri": "https://dprepdata.blob.core.windows.net/demo/Titanic.csv", '
                '"job_input_type": "uri_folder"}}}',
            ),
            (
                # asset input binding
                {
                    "silo1": {"binding": PipelineInput(name="input1", owner="pipeline", meta=None)},
                },
                '{"silo1": {"binding": "${{parent.inputs.input1}}"}}',
            ),
            (
                # primitive type input
                {
                    "silo1": dict(
                        component_in_string="component_in_string",
                        component_in_ranged_integer=10,
                        component_in_enum="world",
                        component_in_boolean=True,
                        component_in_ranged_number=5.5,
                    ),
                },
                '{"silo1": {"component_in_string": "component_in_string", '
                '"component_in_ranged_integer": 10, "component_in_enum": "world", '
                '"component_in_boolean": true, "component_in_ranged_number": 5.5}}',
            ),
        ],
    )
    def test_to_rest_items(self, items, rest_input_str):
        assert ParallelFor._to_rest_items(items) == rest_input_str

    @pytest.mark.parametrize(
        "items, error_message",
        [
            (
                # unsupported item value type
                [
                    {"component_in_number": CustomizedObject()},
                ],
                "Unsupported type",
            ),
            (
                # local file input
                [{"component_in_path": Input(path="./tests/test_configs/components/helloworld_component.yml")}],
                "Local file input",
            ),
            (
                # empty path
                [{"component_in_path": Input(path=None)}],
                "Input path not provided",
            ),
            (
                # dict Input
                [{"component_in_path": {"job_input_path": "azureml://path/to/file"}}],
                "Unsupported type",
            ),
        ],
    )
    def test_to_rest_items_unsupported(self, items, error_message):
        with pytest.raises(ValidationException) as e:
            ParallelFor._to_rest_items(items)
        assert error_message in str(e.value)
