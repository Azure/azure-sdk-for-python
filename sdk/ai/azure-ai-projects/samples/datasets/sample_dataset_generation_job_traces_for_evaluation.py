# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates an evaluation dataset from an agent's conversation traces.
    The sample is fully self-contained:

      1. Wires up Azure Monitor + AIProjectInstrumentor so agent calls emit
         semantic GenAI spans (with content) to Application Insights.
      2. Creates a temporary agent and seeds spans with sample conversations.
      3. Waits for ingestion, then submits a `DataGenerationJob`
         (scenario=EVALUATION, source=traces) that synthesizes Q/A pairs.
      4. Polls the job and fetches the resulting `DatasetVersion`.
      5. Cleans up the dataset, job, seeded conversations, and agent.

    To adapt for an existing agent with recent traces, replace step 2 with
    your agent's name and skip the ingestion wait.

USAGE:
    python sample_dataset_generation_job_traces_for_evaluation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv \\
        azure-monitor-opentelemetry azure-core-tracing-opentelemetry

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as
       found in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The Azure OpenAI deployment name used
       to drive the temporary agent during trace seeding.
    3) DATASET_NAME - Optional. Output dataset name. Defaults to
       `traces-eval-sample`. Service caps the rendered name at 50 chars
       (the sample appends a unique run-id suffix).
    4) POLL_INTERVAL_SECONDS - Optional. Sleep between job status polls.
       Defaults to 10.
    5) TRACE_INGESTION_WAIT_SECONDS - Optional. Wait after seeding for
       Application Insights ingestion. Defaults to 180.
"""

import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DataGenerationJob,
    DataGenerationJobInputs,
    DataGenerationJobOutputOptions,
    DataGenerationJobScenario,
    DatasetDataGenerationJobOutput,
    DatasetVersion,
    JobStatus,
    PromptAgentDefinition,
    TracesDataGenerationJobOptions,
    TracesDataGenerationJobSource,
)
from azure.ai.projects.telemetry import AIProjectInstrumentor
from azure.monitor.opentelemetry import configure_azure_monitor

load_dotenv()


# Minimal persona + prompt; one seeded turn is enough for the job to succeed
# (max_samples is the cap on generated samples, not a floor on input traces).
AGENT_INSTRUCTIONS = (
    "Widgets & Gizmos support agent. Be concise. "
    "Refunds: unopened 30 days; defective 90 days; 5-7 business days to process."
)
SEED_PROMPT = "What is your refund policy?"


endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment = os.environ["FOUNDRY_MODEL_NAME"]
dataset_name = os.environ.get("DATASET_NAME", "traces-eval-sample")
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))
trace_ingestion_wait_seconds = int(os.environ.get("TRACE_INGESTION_WAIT_SECONDS", "180"))

# Per-run id keeps repeated runs from colliding; output names are capped at 50 chars.
run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
output_dataset_name = f"{dataset_name}-{run_id}"
if len(output_dataset_name) > 50:
    raise ValueError(
        f"Output dataset name `{output_dataset_name}` exceeds the 50-character service limit. "
        f"Shorten DATASET_NAME (currently `{dataset_name}`) so that `<name>-<run id>` fits within 50 characters."
    )

agent_name = f"traces-eval-sample-{run_id}"

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    created_agent = None
    created_conversation_id: Optional[str] = None
    submitted_job_id: Optional[str] = None
    created_dataset: Optional[DatasetVersion] = None

    try:
        # 1. Configure Azure Monitor + GenAI instrumentation to emit spans with content.
        # AIProjectInstrumentor gates on this env var at instrument() time; without it
        # instrument() returns early and no spans flow.
        os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = "true"

        print("Configure Azure Monitor exporter from the project's Application Insights connection.")
        connection_string = project_client.telemetry.get_application_insights_connection_string()
        configure_azure_monitor(connection_string=connection_string)
        AIProjectInstrumentor().instrument(enable_content_recording=True)

        # 2. Create a temporary agent and seed traces.
        print(f"Create temporary agent `{agent_name}` (model: `{model_deployment}`).")
        created_agent = project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(model=model_deployment, instructions=AGENT_INSTRUCTIONS),
        )
        print(f"Agent created (id: {created_agent.id}, version: {created_agent.version}).")

        seed_start = datetime.now(tz=timezone.utc)
        print(f"Seed one conversation against the agent (prompt: {SEED_PROMPT!r}).")
        with project_client.get_openai_client() as openai_client:
            conversation = openai_client.conversations.create()
            created_conversation_id = conversation.id
            print(f"  - conversation id: {conversation.id}")
            openai_client.responses.create(
                conversation=conversation.id,
                input=SEED_PROMPT,
                extra_body={
                    "agent_reference": {
                        "name": created_agent.name,
                        "id": created_agent.id,
                        "type": "agent_reference",
                    }
                },
            )

        print(
            f"Wait {trace_ingestion_wait_seconds}s for Application Insights to ingest the emitted spans. "
            f"Override with TRACE_INGESTION_WAIT_SECONDS.",
            flush=True,
        )
        time.sleep(trace_ingestion_wait_seconds)

        # 3. Submit a data generation job that reads the agent's traces.
        # Small backoff so the seeded spans fall inside the queried window.
        start_time = seed_start - timedelta(minutes=5)
        end_time = datetime.now(tz=timezone.utc)

        print(
            f"Create a data generation job from traces for agent `{agent_name}` "
            f"(window: {start_time.isoformat()} .. {end_time.isoformat()})."
        )
        job = project_client.beta.datasets.create_generation_job(
            job=DataGenerationJob(
                inputs=DataGenerationJobInputs(
                    name=f"traces-eval-{run_id}",
                    scenario=DataGenerationJobScenario.EVALUATION,
                    sources=[
                        TracesDataGenerationJobSource(
                            description="Application Insights conversation traces for the temporary agent.",
                            agent_name=agent_name,
                            start_time=start_time,
                            end_time=end_time,
                        ),
                    ],
                    # Service requires max_samples in [15, 1000]. It's a cap on
                    # generated samples - one seeded trace turn is enough.
                    options=TracesDataGenerationJobOptions(max_samples=15),
                    output_options=DataGenerationJobOutputOptions(name=output_dataset_name),
                ),
            ),
        )
        submitted_job_id = job.id
        print(f"Created data generation job `{job.id}` (status: `{job.status}`).")

        print(f"Poll job `{job.id}` until it reaches a terminal state.", end="", flush=True)
        while job.status not in TERMINAL_STATUSES:
            time.sleep(poll_interval_seconds)
            print(".", end="", flush=True)
            job = project_client.beta.datasets.get_generation_job(job_id=job.id)
        print()
        print(f"Final job status: `{job.status}`.")

        if job.status != JobStatus.SUCCEEDED:
            message = job.error.message if job.error is not None else "<no error message>"
            raise RuntimeError(f"Job `{job.id}` ended with status `{job.status}`: {message}")

        # 4. Resolve the generated dataset.
        outputs = (job.result.outputs if job.result is not None else None) or []
        dataset_output = next(
            (o for o in outputs if isinstance(o, DatasetDataGenerationJobOutput)), None
        )
        if dataset_output is None or not dataset_output.name or not dataset_output.version:
            raise RuntimeError(f"Job `{job.id}` did not produce a dataset output.")

        created_dataset = project_client.datasets.get(
            name=dataset_output.name, version=dataset_output.version
        )
        print(
            f"Generated dataset: name=`{created_dataset.name}` "
            f"version=`{created_dataset.version}` id=`{created_dataset.id}`"
        )
        if job.result is not None and job.result.generated_samples is not None:
            print(f"Generated samples: {job.result.generated_samples}")

    finally:
        # Best-effort cleanup, outputs -> producers (dataset, job, conversations, agent).
        if created_dataset is not None:
            try:
                project_client.datasets.delete(
                    name=created_dataset.name or "",
                    version=created_dataset.version or "",
                )
                print(f"Deleted dataset `{created_dataset.name}` v{created_dataset.version}.")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"  (warning) could not delete dataset: {exc}")

        if submitted_job_id is not None:
            try:
                project_client.beta.datasets.delete_generation_job(job_id=submitted_job_id)
                print(f"Deleted data generation job `{submitted_job_id}`.")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"  (warning) could not delete job: {exc}")

        if created_conversation_id is not None:
            try:
                with project_client.get_openai_client() as openai_client:
                    openai_client.conversations.delete(conversation_id=created_conversation_id)
                    print(f"Deleted seeded conversation `{created_conversation_id}`.")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"  (warning) could not delete conversation: {exc}")

        if created_agent is not None:
            try:
                project_client.agents.delete_version(
                    agent_name=created_agent.name,
                    agent_version=created_agent.version,
                )
                print(f"Deleted temporary agent `{created_agent.name}` v{created_agent.version}.")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"  (warning) could not delete agent: {exc}")
