from pathlib import Path

import pytest

from azure.ai.ml import Input, dsl, load_component

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestPipelineBuilder:
    def test_simple(self):
        component_yaml = components_dir / "helloworld_component_optional_input.yml"
        component_func = load_component(component_yaml)

        @dsl.pipeline
        def pipeline_func(required_input: int, optional_input: int = 2):
            named_step = component_func(required_input=required_input, optional_input=optional_input)

        pipeline_job = pipeline_func(1, 2)
        assert "named_step" in pipeline_job.jobs

    def test_raise_exception(self):
        @dsl.pipeline
        def mock_error_exception():
            mock_local_variable = 1
            return mock_local_variable / 0

        with pytest.raises(ZeroDivisionError):
            mock_error_exception()

    def test_instance_func(self):
        component_yaml = components_dir / "helloworld_component_optional_input.yml"
        component_func = load_component(component_yaml)

        class MockClass(Input):
            def __init__(self, mock_path):
                super(MockClass, self).__init__(path=mock_path)

            @dsl.pipeline
            def pipeline_func(self, required_input: int, optional_input: int = 2):
                named_step = component_func(required_input=required_input, optional_input=optional_input)

        mock_obj = MockClass("./some/path")
        pipeline_job = mock_obj.pipeline_func(1, 2)
        assert "named_step" in pipeline_job.jobs
        assert "self" in pipeline_job.inputs
        assert pipeline_job.inputs["self"].path == "./some/path"

    def test_node_as_input_output(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func = load_component(component_yaml)

        @dsl.pipeline
        def base_pipeline_func(input_path: Input, input_number: float = 0.5):
            node1 = component_func(component_in_path=input_path, component_in_number=input_number)
            node2 = component_func(
                component_in_path=node1.outputs["component_out_path"],
                component_in_number=input_number,
            )
            # return {
            #     'component_out_path': node2.outputs['component_out_path'],
            # }

        @dsl.pipeline
        def pipeline_func(input_path: Input, input_number: float = 0.5):
            node1 = component_func(component_in_path=input_path, component_in_number=input_number)
            # single output node as node input
            node2 = component_func(
                component_in_path=node1,
                component_in_number=input_number,
            )
            # single output node as pipeline output
            # return node2

        base_pipeline_job = base_pipeline_func(Input(path="./tests/test_configs/data"), 0.5)
        pipeline_job = pipeline_func(Input(path="./tests/test_configs/data"), 0.5)
        pipeline_job.display_name = base_pipeline_job.display_name
        assert (
            pipeline_job._to_rest_object().properties.as_dict()
            == base_pipeline_job._to_rest_object().properties.as_dict()
        )

    def test_node_as_sub_pipeline_input(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func = load_component(component_yaml)

        @dsl.pipeline
        def sub_pipeline_func(input_path: Input, input_number: float = 0.5):
            node1 = component_func(component_in_path=input_path, component_in_number=input_number)
            node2 = component_func(
                component_in_path=node1.outputs["component_out_path"],
                component_in_number=input_number,
            )
            return {
                "component_out_path": node2.outputs["component_out_path"],
            }

        @dsl.pipeline
        def base_pipeline_func(input_path: Input, input_number: float = 0.5):
            node1 = component_func(component_in_path=input_path, component_in_number=input_number)
            node2 = sub_pipeline_func(
                input_path=node1.outputs["component_out_path"],
                input_number=input_number,
            )
            # return {
            #     'component_out_path': node2.outputs['component_out_path'],
            # }

        @dsl.pipeline
        def pipeline_func(input_path: Input, input_number: float = 0.5):
            node1 = component_func(component_in_path=input_path, component_in_number=input_number)
            # single output node as node input
            node2 = sub_pipeline_func(
                input_path=node1,
                input_number=input_number,
            )
            # single output node as pipeline output
            # return node2

        base_pipeline_job = base_pipeline_func(Input(path="./tests/test_configs/data"), 0.5)
        pipeline_job = pipeline_func(Input(path="./tests/test_configs/data"), 0.5)
        pipeline_job.display_name = base_pipeline_job.display_name
        assert (
            pipeline_job._to_rest_object().properties.as_dict()
            == base_pipeline_job._to_rest_object().properties.as_dict()
        )

    def test_node_as_sub_pipeline_input_error(self):
        single_output_component_func = load_component(components_dir / "helloworld_component.yml")
        multi_output_component_func = load_component(components_dir / "helloworld_component_multi_outputs.yml")

        @dsl.pipeline
        def sub_pipeline_func(input_path: Input, input_number: float = 0.5):
            node1 = single_output_component_func(component_in_path=input_path, component_in_number=input_number)
            node2 = single_output_component_func(
                component_in_path=node1.outputs["component_out_path"],
                component_in_number=input_number,
            )
            return {
                "component_out_path": node2.outputs["component_out_path"],
            }

        @dsl.pipeline
        def pipeline_func(input_path: Input, input_number: float = 0.5):
            node1 = multi_output_component_func(component_in_path=input_path, component_in_number=input_number)
            # single output node as node input
            node2 = sub_pipeline_func(
                input_path=node1,
                input_number=input_number,
            )
            # single output node as pipeline output
            # return node2

        with pytest.raises(
            ValueError, match="Provided input input_path is not a single output node, cannot be used as a node input."
        ):
            pipeline_func(Input(path="./tests/test_configs/data"), 0.5)

    def test_with_global_condition(self):
        single_output_component_func = load_component(components_dir / "helloworld_component.yml")

        is_true = True

        @dsl.pipeline
        def sub_components(input_path: Input):
            if is_true:
                node = single_output_component_func(component_in_path=input_path, component_in_number=0.2)
                return {"component_out_path": node.outputs["component_out_path"]}
            else:
                node = single_output_component_func(component_in_path=input_path, component_in_number=0.7)
                return {"component_out_path": node.outputs["component_out_path"]}

        @dsl.pipeline
        def pipeline_func(input_path: Input):
            sub_components(input_path=input_path)

        pipeline_job = pipeline_func(Input(path="./tests/test_configs/data"))
        assert len(pipeline_job.jobs) == 1
        assert pipeline_job.jobs["sub_components"].component.jobs["node"].inputs["component_in_number"]._data == 0.2

        is_true = False
        pipeline_job = pipeline_func(Input(path="./tests/test_configs/data"))
        assert len(pipeline_job.jobs) == 1
        assert pipeline_job.jobs["sub_components"].component.jobs["node"].inputs["component_in_number"]._data == 0.7
