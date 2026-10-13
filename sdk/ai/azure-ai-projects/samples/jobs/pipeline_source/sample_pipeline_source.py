# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Submit a two-component PipelineJob that snapshots local helper modules.

The image must include the same azure-ai-projects version used for authoring.
Running this file uploads one Code folder and submits a live pipeline job.
"""

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.dsl import pipeline
from azure.identity import AzureCliCredential
from steps.source_pipeline_components import consume, produce


@pipeline(
    compute_id=os.environ["JOB_COMPUTE_ID"],
    environment_image_reference=os.environ["JOB_ENVIRONMENT_IMAGE"],
    user_assigned_identity_id=os.environ["JOB_NODE_UAI_RESOURCE_ID"],
    instance_type=os.environ["JOB_INSTANCE_TYPE"],
)
def workflow(text: str):
    first = produce(text=text)
    second = consume(message=first.outputs.message)
    return {"receipt": second.outputs.receipt}


def main() -> None:
    job = workflow(text="world")
    with (
        AzureCliCredential() as credential,
        AIProjectClient(
            endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            credential=credential,
            allow_preview=True,
            retry_total=0,
        ) as client,
    ):
        created = client.beta.jobs.create_or_update(
            job, experiment_name="pipeline_samples", headers={"x-ms-foundry-job-route": "execution"}
        )
        print(f"Submitted {created.name}: {created.id} (status: {created.status})")


if __name__ == "__main__":
    main()
