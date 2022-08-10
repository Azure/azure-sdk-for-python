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
    def inputs(self, value: Dict[str, Union[Input, str, bool, int, float]]):
        self._inputs = {}
        if not value:
            return

        for key, value in value.items():
            self._inputs[key] = build_input_output(value)

    @property
    def outputs(self) -> Dict[str, Output]:
        return self._outputs

    @outputs.setter
    def outputs(self, value: Dict[str, Output]):
        self._outputs = {}
        if not value:
            return

        for key, value in value.items():
            self._outputs[key] = build_input_output(value, inputs=False)
