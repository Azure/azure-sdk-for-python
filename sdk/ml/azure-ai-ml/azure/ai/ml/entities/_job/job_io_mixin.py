# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Dict, Union

from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job._input_output_helpers import build_input_output


class JobIOMixin:
    @property
    def inputs(self) -> Dict[str, Union[Input, str, bool, int, float]]:
        return self._inputs

    @inputs.setter
    def inputs(self, value: Dict[str, Union[Input, str, bool, int, float]]) -> None:
        self._inputs: Dict = {}
        if not value:
            return

        for input_name, input_value in value.items():
            self._inputs[input_name] = build_input_output(input_value)

    @property
    def outputs(self) -> Dict[str, Output]:
        return self._outputs

    @outputs.setter
    def outputs(self, value: Dict[str, Output]) -> None:
        self._outputs: Dict = {}
        if not value:
            return

        for output_name, output_value in value.items():
            self._outputs[output_name] = build_input_output(output_value, inputs=False)
