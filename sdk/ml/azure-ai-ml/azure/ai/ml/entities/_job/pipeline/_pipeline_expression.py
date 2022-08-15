# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import re
from abc import abstractmethod
from typing import List

from azure.ai.ml._utils.utils import get_all_data_binding_expressions
from azure.ai.ml.entities._job.pipeline._exceptions import UserErrorException


class PipelineExpressionOperator:
    ADD = "+"


class PipelineExpressionMixin:
    SUPPORT_PRIMITIVE_TYPES = (str,)

    @abstractmethod
    def __str__(self) -> str:
        pass

    def _validate_binary_operation(self, other, operator: str):
        # only support addition between string, PipelineInput and PipelineExpression (swappable) currently
        err_msg = "Only support addition between string and PipelineInput (swappable) currently."
        if operator != PipelineExpressionOperator.ADD:
            raise UserErrorException(message=err_msg, no_personal_data_message=err_msg)
        from azure.ai.ml.entities._job.pipeline._io import PipelineInput

        if not isinstance(other, self.SUPPORT_PRIMITIVE_TYPES) and not isinstance(
            other, (PipelineInput, PipelineExpression)
        ):
            raise UserErrorException(message=err_msg, no_personal_data_message=err_msg)

    @staticmethod
    def _get_inputs(input1, input2) -> list:
        from azure.ai.ml.entities._job.pipeline._io import PipelineInput

        inputs = []
        for operand in [input1, input2]:
            if isinstance(operand, PipelineInput):
                inputs.append(operand)
            elif isinstance(operand, PipelineExpression):
                inputs.extend(operand.inputs)
        return inputs

    def __add__(self, other) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.ADD)
        return PipelineExpression.resolve(
            expression=str(self) + str(other),
            inputs=self._get_inputs(self, other),
        )

    def __radd__(self, other) -> "PipelineExpression":
        self._validate_binary_operation(other, PipelineExpressionOperator.ADD)
        return PipelineExpression.resolve(
            expression=str(other) + str(self),
            inputs=self._get_inputs(self, other),
        )


class PipelineExpression(PipelineExpressionMixin):
    """Pipeline expression entity.

    Use PipelineExpression to support simple and trivial parameter transformation tasks with constants
    or other parameters. Operations are recorded in this class during executions, and expected result
    will be generated for corresponding scenario.
    """

    PIPELINE_INPUT_PREFIX = ["parent", "inputs"]
    PIPELINE_INPUT_PATTERN = re.compile(pattern=r"parent.inputs.(?P<pipeline_input_name>[^.]+)")
    PIPELINE_INPUT_NAME_GROUP = "pipeline_input_name"

    def __init__(self, expression: str, inputs: dict):
        self._expression = expression
        self._inputs = inputs

    def __repr__(self) -> str:
        return f"PipelineExpression(expression={repr(self._expression)}, inputs={repr(self._inputs)})"

    def __str__(self) -> str:
        return self._expression

    def _data_binding(self) -> str:
        return self._expression

    @property
    def inputs(self) -> list:
        """PipelineInputs in current expression."""
        return list(self._inputs.values())

    @staticmethod
    def resolve(expression: str, inputs: list) -> "PipelineExpression":
        """Resolve PipelineExpression from given data binding expression and nested PipelineInputs.

        :param expression: Data binding expression
        :type expression: str
        :param inputs: PipelineInputs list in given data binding expression
        :type inputs: List[PipelineInput]
        :returns PipelineExpression
        """
        inputs_dict = {pipeline_input._name: pipeline_input for pipeline_input in inputs}
        return PipelineExpression(expression, inputs_dict)

    @staticmethod
    def parse_pipeline_input_names_from_data_binding(data_binding: str) -> List[str]:
        """Parse all PipelineInputs name from data binding expression.

        :param data_binding: Data binding expression
        :type data_binding: str
        :returns List of PipelineInput's name from given data binding expression
        """
        pipeline_input_names = []
        for single_data_binding in get_all_data_binding_expressions(
            value=data_binding,
            binding_prefix=PipelineExpression.PIPELINE_INPUT_PREFIX,
            is_singular=False,
        ):
            m = PipelineExpression.PIPELINE_INPUT_PATTERN.match(single_data_binding)
            # `get_all_data_binding_expressions` should work as pre-filter, so no need to concern `m` is None
            pipeline_input_names.append(m.group(PipelineExpression.PIPELINE_INPUT_NAME_GROUP))
        return pipeline_input_names
