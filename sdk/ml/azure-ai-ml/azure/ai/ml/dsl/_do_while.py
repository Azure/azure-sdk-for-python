# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml.entities._builders.do_while import DoWhile
from azure.ai.ml.entities._job.pipeline._io import NodeOutput


def do_while(body, mapping, max_iteration_count: int, condition=None):
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

    :param body: Pipeline job or command node for the do-while loop body.
    :type body: Union[Pipeline, Command]
    :param mapping: Output-Input mapping for reach round of the do-while loop.
                    Key is the last round output of the body. Value is the input port for current body.
    :type mapping: Dict[Union[str, Output], Union[str, Input, List]]
    :param max_iteration_count: limits in running the do-while node.
    :type max_iteration_count: int
    :param condition: Name of a boolean output of body, do-while loop stops if its value is evaluated to be negative;
                      If not specified, handle as while true.
    :type condition: Output
    """
    do_while_node = DoWhile(
        body=body,
        condition=condition,
        mapping=mapping,
        _from_component_func=True,
    )
    do_while_node.set_limits(max_iteration_count=max_iteration_count)

    def _infer_and_update_body_input_from_mapping():
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
                body.component.inputs[input_name]._is_inferred_optional = True
                body.component.inputs[input_name].type = inferred_type

    # when mapping is a dictionary, infer and update for dynamic input
    if isinstance(mapping, dict):
        _infer_and_update_body_input_from_mapping()

    return do_while_node
