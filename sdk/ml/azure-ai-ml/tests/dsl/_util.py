import contextlib
from typing import Union, List

from azure.ai.ml._schema.pipeline import PipelineJobSchema
from azure.ai.ml._schema.pipeline.pipeline_component import PipelineJobsField
from azure.ai.ml.entities import PipelineJob, PipelineComponent, Pipeline
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._job.pipeline._io import NodeInput

_DSL_TIMEOUT_SECOND = 20 * 60  # timeout for dsl's tests, unit in second.


@contextlib.contextmanager
def include_private_preview_nodes_in_pipeline():
    original_jobs = PipelineJobSchema._declared_fields["jobs"]
    PipelineJobSchema._declared_fields["jobs"] = PipelineJobsField()

    try:
        yield
    finally:
        PipelineJobSchema._declared_fields["jobs"] = original_jobs


def expand_pipeline_nodes(pipeline: Union[PipelineJob, PipelineComponent]):
    """Expand pipeline nodes to a list of nodes. All sub-graphs will be expanded."""
    nodes = []
    for node in pipeline.jobs.values():
        if isinstance(node, Pipeline):
            pipeline_component = node.component
            if not isinstance(pipeline_component, PipelineComponent):
                raise RuntimeError(
                    "Pipeline component must be a PipelineComponent object, but got {}".format(type(pipeline_component))
                )
            nodes.extend(expand_pipeline_nodes(pipeline_component))
        else:
            nodes.append(node)
    return nodes


def get_predecessors(node) -> List[BaseNode]:
    """Return list of predecessors for current node.

    Note: Only non-control flow nodes in @pipeline are supported.
    Node: For sub-graph node, we will trace back to inner node and return.
    Example:
        @pipeline
        def sub_pipeline():
            inner_node = component_func()
            return inner_node.outputs
        @pipeline
        def root_pipeline():
            pipeline_node = sub_pipeline()
            node1 = component_func(input1=pipeline_node.outputs.output1)
            node2 = component_func(
                input1=pipeline_node.outputs.output1
                input2=node1.outputs.output1
            )
            # pipeline_node.get_predecessors() will return []
            # node1.get_predecessors() will return [inner_node]
            # node2.get_predecessors() will return [inner_node, node1]
    """

    # use {id: instance} dict to avoid nodes with component and parameters being duplicated
    predecessors = {}
    for _, input_value in node.inputs.items():
        if not isinstance(input_value, NodeInput):
            continue
        owner = input_value._get_data_owner()
        if owner is not None:
            predecessors[owner._instance_id] = owner
    return list(predecessors.values())
