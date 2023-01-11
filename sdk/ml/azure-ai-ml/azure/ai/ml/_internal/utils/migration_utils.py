# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Union, NoReturn

from azure.ai.ml.entities import PipelineJob, Pipeline, PipelineComponent
from azure.ai.ml.entities._job.pipeline._io import PipelineOutput


def _get_pipeline_component(node) -> Optional[PipelineComponent]:
    if isinstance(node, PipelineJob):
        return node.component
    if isinstance(node, Pipeline):
        component = node.component
        if isinstance(component, PipelineComponent):
            return component

    return None


def update_mode_for_promoted_outputs_in_pipeline(
    _pipeline: Union[PipelineJob, Pipeline],
    mode: Optional[str] = None
) -> NoReturn:
    """Update the promoted outputs in the pipeline job. Promoted outputs in sub-graphs will also be updated.
    Will infer the mode from the output being promoted if mode is not specified.

    :param _pipeline: The pipeline job or pipeline to update.
    :type _pipeline: Union[PipelineJob, Pipeline]
    :param mode: The mode to update the promoted outputs to.
    If not specified, will infer the mode from the output being promoted.
    :type mode: Optional[str]
    """
    node_queue, qt = [_pipeline], 0
    while qt < len(node_queue):
        node = node_queue[qt]
        qt += 1

        component = _get_pipeline_component(node)
        if component:
            node_queue.extend(filter(lambda x: isinstance(x, Pipeline), component.jobs.values()))

    for owner in reversed(node_queue):
        for sub_node in owner.component.jobs.values():
            for output in sub_node.outputs.values():
                if isinstance(output._data, PipelineOutput):  # pylint: disable=protected-access
                    # this output has been promoted
                    promoted_output = owner.outputs[output._name]  # pylint: disable=protected-access
                    # update only if mode of promoted output is not set
                    if promoted_output.mode is None:
                        promoted_output.mode = mode or output.mode
