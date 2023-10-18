# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Dict, Optional

from azure.ai.ml.entities._job._input_output_helpers import build_input_output


class JobIOMixin:
    @property
    def inputs(self) -> Optional[Dict]:
        return self._inputs

    @inputs.setter
    def inputs(self, value: Dict) -> None:
        self._inputs = {}
        if not value:
            return

        for input_name, input_value in value.items():
            self._inputs[input_name] = build_input_output(input_value)

    @property
    def outputs(self) -> Optional[Dict]:
        return self._outputs

    @outputs.setter
    def outputs(self, value: Dict) -> None:
        self._outputs = {}
        if not value:
            return

        for output_name, output_value in value.items():
            self._outputs[output_name] = build_input_output(output_value, inputs=False)
