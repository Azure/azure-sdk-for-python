import pytest

from azure.ai.ml.entities._job.pipeline._io import PipelineInput, _resolve_builders_2_data_bindings

from .._util import _DSL_TIMEOUT_SECOND


@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
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
