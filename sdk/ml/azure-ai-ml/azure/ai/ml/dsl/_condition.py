# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List, Optional, Union

from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._builders.condition_node import ConditionNode
from azure.ai.ml.entities._job.pipeline._io import InputOutputBase
from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpression
from azure.ai.ml.exceptions import UserErrorException

# pylint: disable=redefined-outer-name


def condition(
    condition: Union[str, bool, InputOutputBase, BaseNode, PipelineExpression],
    *,
    true_block: Optional[Union[BaseNode, List[BaseNode]]] = None,
    false_block: Optional[Union[BaseNode, List[BaseNode]]] = None,
) -> ConditionNode:
    """Create a condition node to provide runtime condition graph experience.

    Below is an example of using an expression result to control which step is executed.
    If the pipeline parameter 'int_param1' is greater than 'int_param2', then 'true_step' will be executed,
    otherwise, the 'false_step' will be executed.

    .. code-block:: python

        @dsl.pipeline
        def pipeline_func(int_param1: int, int_param2: int):
            true_step = component_func()
            false_step = another_component_func()
            dsl.condition(
                int_param1 > int_param2,
                true_block=true_step,
                false_block=false_step
            )

    :param condition: The condition of the execution flow.
        The value could be a boolean type control output, a node with exactly one boolean type output,
        or a pipeline expression.
    :type condition: Union[
        str,
        bool,
        ~azure.ai.ml.entities._job.pipeline._io.InputOutputBase,
        ~azure.ai.ml.entities._builders.BaseNode,
        ~azure.ai.ml.entities._job.pipeline._pipeline_expression.PipelineExpression]
    :keyword true_block: The block to be executed if the condition resolves to True.
    :paramtype true_block: Union[
        ~azure.ai.ml.entities._builders.BaseNode,
        List[~azure.ai.ml.entities._builders.BaseNode]]
    :keyword false_block: The block to be executed if the condition resolves to False.
    :paramtype false_block: Union[
        ~azure.ai.ml.entities._builders.BaseNode,
        List[~azure.ai.ml.entities._builders.BaseNode]]
    :return: The condition node.
    :rtype: ConditionNode
    :raises UserErrorException: Raised if the condition node has an incorrect number of outputs.
    """
    # resolve expression as command component
    if isinstance(condition, PipelineExpression):
        condition = condition.resolve()
    if isinstance(condition, BaseNode):
        if len(condition.outputs) != 1:
            error_message = (
                f"Exactly one output is expected for condition node, {len(condition.outputs)} outputs found."
            )
            raise UserErrorException(message=error_message, no_personal_data_message=error_message)
        condition = list(condition.outputs.values())[0]
    return ConditionNode(
        condition=condition,
        true_block=true_block,  # type: ignore[arg-type]
        false_block=false_block,  # type: ignore[arg-type]
        _from_component_func=True,
    )
