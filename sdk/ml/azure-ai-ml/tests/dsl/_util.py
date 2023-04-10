import contextlib
from typing import Union

from azure.ai.ml._schema.pipeline import PipelineJobSchema
from azure.ai.ml._schema.pipeline.pipeline_component import PipelineJobsField
from azure.ai.ml.entities import PipelineJob, PipelineComponent, Pipeline

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
