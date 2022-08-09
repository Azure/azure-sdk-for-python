from typing import List

import pytest

from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpression

from .._util import _PIPELINE_JOB_TIMEOUT_SECOND


@pytest.mark.timeout(_PIPELINE_JOB_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestPipelineExpression:
    @pytest.mark.parametrize(
        "data_binding,expected_pipeline_input_names",
        [
            ("${{parent.inputs.input_param}}", ["input_param"]),
            ("${{parent.inputs.input_param}} literal string", ["input_param"]),
            ("${{parent.inputs.input_param}} ${{parent.inputs.another_param}}", ["input_param", "another_param"]),
        ],
    )
    def test_parsing_pipeline_inputs_from_data_binding_expression(
        self,
        data_binding: str,
        expected_pipeline_input_names: List[str],
    ) -> None:
        actual_pipeline_input_names = PipelineExpression.parse_pipeline_input_names_from_data_binding(data_binding)
        assert actual_pipeline_input_names == expected_pipeline_input_names
