# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml.entities._builders.do_while import DoWhile
from azure.ai.ml.exceptions import UserErrorException


def do_while(body, mapping, max_iteration_count: int, condition=True):
    """Build a do_while node by specifying the loop body, output-input mapping and termination condition.

    .. remarks::
        The following example shows how to use do_while function to create a pipeline with do_while node.

        .. code-block:: python

            from azure.ai.ml.dsl import pipeline
            from mldesigner.dsl import do_while

            @pipeline()
            def your_do_while_body():
                pass

            @pipeline()
            def pipeline_with_do_while_node():
                do_while_body = your_do_while_body()
                do_while_node = do_while(
                    body=do_while_body,
                    condition=do_while_body.outputs.condition_output,
                    mapping={
                        do_while_body.outputs.output1: do_while_body_inputs.input1,
                        do_while_body.outputs.output2: [do_while_body_inputs.input2, do_while_body_inputs.input3]
                    }
                )
                # Connect to the do_while_node outputs
                component = component_func(
                    input1=do_while_body.outputs.output1,
                    input2=do_while_body.outputs.output2
                )

    :param body: Pipeline job for the do-while loop body.
    :type body: Pipeline
    :param mapping: Output-Input mapping for reach round of the do-while loop.
                    Key is the last round output of the body. Value is the input port for current body.
    :type mapping: Dict[Union[str, Output], Union[str, Input, List]]
    :param max_iteration_count: limits in running the do-while node.
    :type max_iteration_count: int
    :param condition: Either name of boolean output of body or simply True as do-while loop condition.
                      Default value is True.
    :type condition: Union[Output, bool]
    """
    # while False is meaningless, ban this behaviour.
    if isinstance(condition, bool) and condition is False:
        error_message = f"Invalid condition value, only {True!r} is acceptable."
        raise UserErrorException(message=error_message, no_personal_data_message=error_message)

    do_while_node = DoWhile(
        body=body,
        condition=condition,
        mapping=mapping,
        _from_component_func=True,
    )
    do_while_node.set_limits(max_iteration_count=max_iteration_count)
    return do_while_node
