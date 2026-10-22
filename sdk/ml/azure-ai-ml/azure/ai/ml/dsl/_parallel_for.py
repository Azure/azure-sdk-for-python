# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Union

from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._builders.parallel_for import ParallelFor
from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput


def parallel_for(
    *, body: BaseNode, items: Union[List, Dict, str, PipelineInput, NodeOutput], **kwargs: Any
) -> ParallelFor:
    """Build a parallel for loop by specifying the loop body and input items.

    .. note::
        The following example shows how to use parallel for API to create a pipeline with parallel for node.

        .. code-block:: python

            from azure.ai.ml.dsl import pipeline
            from mldesigner.dsl import parallel_for


            @pipeline
            def your_loop_body(input):
                pass


            @pipeline
            def pipeline_with_parallel_for_node():
                # specify fixed inputs and leave loop config inputs unprovided
                loop_body = your_loop_body()

                # link loop body & loop config to loop node
                loop_node = parallel_for(
                    body=loop_body,
                    items=[
                        {"loop_body_input": 1},
                        {"loop_body_input": 2},
                    ],
                )

                # collect aggregated output from loop body
                aggregate_node = collect_aggregated_outputs_from_for_each_node(
                    input=loop_node.outputs.output,
                )

    :keyword body: Node to execute as the loop body.
    :paramtype body: ~azure.ai.ml.entities._builders.BaseNode
    :keyword items: The loop body's input which will bind to the loop node.
    :paramtype items: Union[
        list,
        dict,
        str,
        ~azure.ai.ml.entities._job.pipeline._io.PipelineInput,
        ~azure.ai.ml.entities._job.pipeline._io.NodeOutput]
    :return: The parallel for loop
    :rtype: ~azure.ai.ml.entities._builders.parallel_for.ParallelFor
    """
    parallel_for_node = ParallelFor(
        body=body,  # type: ignore[arg-type]
        items=items,
        _from_component_func=True,
        **kwargs,
    )
    return parallel_for_node
