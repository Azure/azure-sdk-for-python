from pathlib import Path

import pytest

from azure.ai.ml import Input, dsl, load_component

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestPersistentLocals:
    def test_simple(self):
        component_yaml = components_dir / "helloworld_component_optional_input.yml"
        component_func = load_component(component_yaml)

        @dsl.pipeline
        def pipeline_func(required_input: int, optional_input: int = 2):
            named_step = component_func(required_input=required_input, optional_input=optional_input)

        pipeline_job = pipeline_func(1, 2)
        assert 'named_step' in pipeline_job.jobs

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
        assert 'named_step' in pipeline_job.jobs
        assert 'self' in pipeline_job.inputs
        assert pipeline_job.inputs['self'].path == "./some/path"
