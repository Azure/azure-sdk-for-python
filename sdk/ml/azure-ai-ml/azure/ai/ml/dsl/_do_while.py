# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Optional, Union

from azure.ai.ml.entities._builders import Command
from azure.ai.ml.entities._builders.do_while import DoWhile
from azure.ai.ml.entities._builders.pipeline import Pipeline
from azure.ai.ml.entities._inputs_outputs import Output
from azure.ai.ml.entities._job.pipeline._io import NodeOutput


def do_while(
    body: Union[Pipeline, Command], mapping: Dict, max_iteration_count: int, condition: Optional[Output] = None
) -> DoWhile:
    """Build a do_while node by specifying the loop body, output-input mapping, and termination condition.

    .. note::
        The following example shows how to use the `do_while` function to create a pipeline with a `do_while` node.

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
                        do_while_body.outputs.output2: [
                            do_while_body_inputs.input2,
                            do_while_body_inputs.input3,
                        ],
                    },
                )
                # Connect to the do_while_node outputs
                component = component_func(
                    input1=do_while_body.outputs.output1, input2=do_while_body.outputs.output2
                )

    :param body: The pipeline job or command node for the do-while loop body.
    :type body: Union[~azure.ai.ml.entities._builders.pipeline.Pipeline, ~azure.ai.ml.entities._builders.Command]
    :param mapping: The output-input mapping for each round of the do-while loop.
        The key is the last round's output of the body, and the value is the input port for the current body.
    :type mapping: Dict[
        Union[str,  ~azure.ai.ml.entities.Output],
        Union[str, ~azure.ai.ml.entities.Input, List]]
    :param max_iteration_count: The limit on running the do-while node.
    :type max_iteration_count: int
    :param condition: The name of a boolean output of the body.
        The do-while loop stops if its value is evaluated to be negative.
        If not specified, it handles as a while-true loop.
    :type condition:  ~azure.ai.ml.entities.Output
    :return: The do-while node.
    :rtype: ~azure.ai.ml.entities._builders.do_while.DoWhile
    """
    do_while_node = DoWhile(
        body=body,
        condition=condition,  # type: ignore[arg-type]
        mapping=mapping,
        _from_component_func=True,
    )
    do_while_node.set_limits(max_iteration_count=max_iteration_count)

    def _infer_and_update_body_input_from_mapping() -> None:
        # pylint: disable=protected-access
        for source_output, body_input in mapping.items():
            # handle case that mapping key is a NodeOutput
            output_name = source_output._port_name if isinstance(source_output, NodeOutput) else source_output
            # if loop body output type is not specified, skip as we have no place to infer
            if body.outputs[output_name].type is None:
                continue
            # body input can be a list of inputs, normalize as a list to process
            if not isinstance(body_input, list):
                body_input = [body_input]
            for single_input in body_input:
                # if input type is specified, no need to infer and skip
                if single_input.type is not None:
                    continue
                inferred_type = body.outputs[output_name].type
                # update node input
                single_input._meta._is_inferred_optional = True
                single_input.type = inferred_type
                # update node corresponding component input
                input_name = single_input._meta.name
                body.component.inputs[input_name]._is_inferred_optional = True  # type: ignore[union-attr]
                body.component.inputs[input_name].type = inferred_type  # type: ignore[union-attr]

    # when mapping is a dictionary, infer and update for dynamic input
    if isinstance(mapping, dict):
        _infer_and_update_body_input_from_mapping()

    return do_while_node
