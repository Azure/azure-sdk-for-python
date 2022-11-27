import contextlib

from azure.ai.ml._schema.pipeline import PipelineJobSchema
from azure.ai.ml._schema.pipeline.pipeline_component import PipelineJobsField

_DSL_TIMEOUT_SECOND = 20 * 60  # timeout for dsl's tests, unit in second.


@contextlib.contextmanager
def include_private_preview_nodes_in_pipeline():
    original_jobs = PipelineJobSchema._declared_fields["jobs"]
    PipelineJobSchema._declared_fields["jobs"] = PipelineJobsField()

    try:
        yield
    finally:
        PipelineJobSchema._declared_fields["jobs"] = original_jobs
