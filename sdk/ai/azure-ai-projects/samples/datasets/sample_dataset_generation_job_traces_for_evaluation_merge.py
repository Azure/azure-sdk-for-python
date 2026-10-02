# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Grows an evaluation dataset from an agent's conversation traces over time,
    using the `merge` write mode. The sample:

      1. Creates an agent and seeds a first batch of conversations against it.
      2. Waits for trace ingestion, then submits an `EvaluationDataGenerationJobInputs`
         job (scenario `evaluation`, generation type `traces`) with
         `write_mode=DataGenerationJobOutputWriteMode.OVERWRITE`. This creates the
         first version of the output dataset.
      3. Seeds a second batch of conversations and submits a second job with the
         same output dataset name and `write_mode=DataGenerationJobOutputWriteMode.MERGE`.
         The service creates the next dataset version by merging the newly
         generated rows with the latest existing dataset version and de-duplicating
         trace rows. The second job's time window covers both batches, so rows from
         the first batch are de-duplicated rather than added twice.
      4. Prints both dataset versions, then cleans up both dataset versions,
         the seeded conversations, and the agent.

    Private content in the traces is redacted by default
    (`TracesDataGenerationJobConfiguration.redact_private_content=True`).

    Prerequisite: the project must have an Application Insights resource
    connected so the agent emits server-side traces. The Foundry project's
    managed identity must have the `Reader` role on that Application Insights
    resource so the data generation job can query the traces.

USAGE:
    python sample_dataset_generation_job_traces_for_evaluation_merge.py

    Before running the sample:

    pip install "azure-ai-projects>=2.8.0" azure-identity openai python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as
       found in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The Azure OpenAI deployment name used
       to drive the agent during trace seeding.
    3) TRACE_IDS - Optional. Comma-separated list of trace IDs. When set, both
       jobs only use these traces (within the time window) instead of all of the
       agent's traces.
"""

import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DataGenerationJobOutputWriteMode,
    DataGenerationJobResult,
    DatasetDataGenerationJobOutput,
    DatasetVersion,
    EvaluationDataGenerationJobInputs,
    EvaluationDataGenerationJobOutputConfiguration,
    PromptAgentDefinition,
    TracesDataGenerationJobConfiguration,
    TracesDataGenerationJobSource,
)

load_dotenv()


AGENT_INSTRUCTIONS = (
    "Widgets & Gizmos support agent. Be concise. "
    "Refunds: unopened 30 days; defective 90 days; 5-7 business days to process."
)
FIRST_BATCH_PROMPTS = [
    "What is your refund policy?",
    "I bought a widget last week and it's defective. What can I do?",
    "How long does it take to process a refund?",
]
SECOND_BATCH_PROMPTS = [
    "Can I return an unopened gizmo after 45 days?",
    "Do you offer exchanges, or only refunds?",
    "Are shipping fees refundable?",
]

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment = os.environ["FOUNDRY_MODEL_NAME"]
trace_ids = [
    trace_id.strip()
    for trace_id in os.environ.get("TRACE_IDS", "").split(",")
    if trace_id.strip()
]
DATASET_NAME = "traces-eval-merge"
POLL_INTERVAL_SECONDS = 10
INGEST_WAIT_SECONDS = 60
MAX_JOB_ATTEMPTS = 5
RETRY_WAIT_SECONDS = 60

# Per-run id suffixed on the agent, output dataset, and job-input names so
# repeated runs don't collide. Kept short (timestamp + 4 hex) to stay under
# the 50-char service limit on output names.
run_id = (
    f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
)
output_dataset_name = f"{DATASET_NAME}-{run_id}"
agent_name = f"{DATASET_NAME}-{run_id}"
if len(output_dataset_name) > 50:
    raise ValueError(
        f"Output dataset name `{output_dataset_name}` exceeds the 50-character service limit."
    )


def seed_conversations(
    openai_client: Any, prompts: List[str], conversation_ids: List[str]
) -> None:
    """Run one short conversation per prompt against the agent, recording the conversation IDs."""
    for prompt in prompts:
        conversation = openai_client.conversations.create()
        conversation_ids.append(conversation.id)
        print(f"  - conversation id: {conversation.id}  (prompt: {prompt!r})")
        openai_client.responses.create(
            conversation=conversation.id,
            input=prompt,
            extra_body={
                "agent_reference": {"name": agent_name, "type": "agent_reference"}
            },
        )


def run_traces_job(
    project_client: AIProjectClient,
    job_name: str,
    start_time: datetime,
    write_mode: DataGenerationJobOutputWriteMode,
) -> DataGenerationJobResult:
    """Run a traces -> evaluation dataset job, retrying while recent traces are still being ingested."""
    for attempt in range(1, MAX_JOB_ATTEMPTS + 1):
        end_time = datetime.now(tz=timezone.utc)
        print(
            f"Create `{write_mode.value}` data generation job `{job_name}` (attempt {attempt}/{MAX_JOB_ATTEMPTS}, "
            f"window: {start_time.isoformat()} .. {end_time.isoformat()})."
        )
        try:
            poller = project_client.datasets.begin_create_generation_job(
                job=EvaluationDataGenerationJobInputs(
                    name=f"{job_name}-a{attempt}",
                    sources=[
                        TracesDataGenerationJobSource(
                            description="Application Insights conversation traces for the agent.",
                            agent_name=agent_name,
                            start_time=start_time,
                            end_time=end_time,
                            trace_ids=trace_ids or None,
                        ),
                    ],
                    # max_samples is omitted, so sampling is turned off and every matching trace is used.
                    generation_configuration=TracesDataGenerationJobConfiguration(
                        redact_private_content=True
                    ),
                    output_configuration=EvaluationDataGenerationJobOutputConfiguration(
                        name=output_dataset_name,
                        write_mode=write_mode,
                    ),
                ),
                polling_interval=POLL_INTERVAL_SECONDS,
            )
            job_result = poller.result()
            print(f"Job succeeded (final LRO status: `{poller.status()}`).")
            return job_result
        except Exception as e:  # pylint: disable=broad-exception-caught
            if attempt == MAX_JOB_ATTEMPTS:
                raise RuntimeError(
                    f"Job `{job_name}` failed after {MAX_JOB_ATTEMPTS} attempts: {e}"
                ) from e
            print(
                f"  Attempt {attempt} failed ({e}); wait {RETRY_WAIT_SECONDS}s and retry."
            )
            time.sleep(RETRY_WAIT_SECONDS)
    raise RuntimeError(f"Job `{job_name}` did not run.")


def get_output_dataset(
    project_client: AIProjectClient, job_result: DataGenerationJobResult
) -> DatasetVersion:
    """Resolve the dataset version produced by a data generation job."""
    dataset_output = next(
        (
            o
            for o in job_result.outputs or []
            if isinstance(o, DatasetDataGenerationJobOutput)
        ),
        None,
    )
    if dataset_output is None or not dataset_output.name or not dataset_output.version:
        raise RuntimeError("The data generation job did not produce a dataset output.")
    dataset = project_client.datasets.get(
        name=dataset_output.name, version=dataset_output.version
    )
    print(
        f"Dataset: name=`{dataset.name}` version=`{dataset.version}` id=`{dataset.id}` "
        f"(generated samples in this job: {job_result.generated_samples})"
    )
    return dataset


def main() -> None:
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):

        created_agent = None
        created_conversation_ids: List[str] = []
        created_datasets: List[DatasetVersion] = []

        try:
            # 1. Create an agent and seed the first batch of traces.
            print(f"Create agent `{agent_name}` (model: `{model_deployment}`).")
            created_agent = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model_deployment, instructions=AGENT_INSTRUCTIONS
                ),
            )
            print(
                f"Agent created (id: {created_agent.id}, version: {created_agent.version})."
            )

            start_time = datetime.now(tz=timezone.utc) - timedelta(minutes=5)
            print(
                f"Seed the first batch of {len(FIRST_BATCH_PROMPTS)} conversation(s)."
            )
            seed_conversations(
                openai_client, FIRST_BATCH_PROMPTS, created_conversation_ids
            )
            print(
                f"Wait {INGEST_WAIT_SECONDS}s for Application Insights to ingest the spans.",
                flush=True,
            )
            time.sleep(INGEST_WAIT_SECONDS)

            # 2. Create the first dataset version (overwrite is the default write mode).
            first_result = run_traces_job(
                project_client,
                f"traces-merge-{run_id}-1",
                start_time,
                DataGenerationJobOutputWriteMode.OVERWRITE,
            )
            first_dataset = get_output_dataset(project_client, first_result)
            created_datasets.append(first_dataset)

            # 3. Seed more traces, then merge them into the next dataset version.
            print(
                f"Seed the second batch of {len(SECOND_BATCH_PROMPTS)} conversation(s)."
            )
            seed_conversations(
                openai_client, SECOND_BATCH_PROMPTS, created_conversation_ids
            )
            print(
                f"Wait {INGEST_WAIT_SECONDS}s for Application Insights to ingest the spans.",
                flush=True,
            )
            time.sleep(INGEST_WAIT_SECONDS)

            # The window still starts before the first batch: trace rows already present in
            # the latest dataset version are de-duplicated by the merge.
            second_result = run_traces_job(
                project_client,
                f"traces-merge-{run_id}-2",
                start_time,
                DataGenerationJobOutputWriteMode.MERGE,
            )
            second_dataset = get_output_dataset(project_client, second_result)
            created_datasets.append(second_dataset)

            # 4. Show both dataset versions.
            print(f"Versions of dataset `{output_dataset_name}`:")
            for dataset in created_datasets:
                print(f"  - version=`{dataset.version}` id=`{dataset.id}`")

        finally:
            # Best-effort cleanup, outputs -> producers (datasets, conversations, agent).
            for dataset in created_datasets:
                try:
                    project_client.datasets.delete(
                        name=dataset.name or "", version=dataset.version or ""
                    )
                    print(f"Deleted dataset `{dataset.name}` v{dataset.version}.")
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    print(
                        f"  (warning) could not delete dataset `{dataset.name}` v{dataset.version}: {exc}"
                    )

            for cid in created_conversation_ids:
                try:
                    openai_client.conversations.delete(conversation_id=cid)
                    print(f"Deleted seeded conversation `{cid}`.")
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    print(f"  (warning) could not delete conversation `{cid}`: {exc}")

            if created_agent is not None:
                try:
                    project_client.agents.delete_version(
                        agent_name=created_agent.name,
                        agent_version=created_agent.version,
                    )
                    print(
                        f"Deleted agent `{created_agent.name}` v{created_agent.version}."
                    )
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    print(f"  (warning) could not delete agent: {exc}")


if __name__ == "__main__":
    main()
