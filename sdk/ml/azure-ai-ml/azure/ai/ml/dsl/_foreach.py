# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


def foreach(body, input):
    """Build a foreach node by specifying the loop body and input mapping

    .. remarks::
        The following example shows how to use foreach API to create a pipeline with foreach node.

        .. code-block:: python

            from azure.ai.ml.dsl import pipeline
            from mldesigner.dsl import foreach

            @pipeline()
            def your_foreach_body(input):
                pass

            @pipeline()
            def pipeline_with_foreach_node(input):
                # specify aggregated input in foreach body
                foreach_body = your_foreach_body(input=input)

                # link foreach body input to foreach node input
                # each iteration of foreach body's output will be automatically aggregated to foreach node's output
                foreach_node = foreach(
                    body=foreach_body,
                    input=foreach_body.inputs.input
                )

                # collect aggregated output from foreach body
                aggregate_node = collect_aggregated_outputs_from_for_each_node(
                    input=foreach_node.outputs.output,
                )

    :param body: Pipeline job for the foreach loop body.
    :type body: Pipeline
    :param input: The foreach loop body's input which will bind to the foreach node
    :type input: NodeInput
    """
    pass
