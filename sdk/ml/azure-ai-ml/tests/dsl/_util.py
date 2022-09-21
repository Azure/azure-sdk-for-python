from azure.ai.ml import MLClient
from azure.core.exceptions import HttpResponseError


def cancel_pipeline_job(pipeline, client: MLClient):
    job = client.jobs.create_or_update(pipeline)
    try:
        client.jobs.cancel(job.name)
    except HttpResponseError:
        pass
    return job


_DSL_TIMEOUT_SECOND = 20 * 60  # timeout for dsl's tests, unit in second.
