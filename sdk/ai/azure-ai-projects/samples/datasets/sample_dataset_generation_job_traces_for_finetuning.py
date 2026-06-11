# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates a supervised fine-tuning dataset from an agent's conversation traces.

      1. Creates an agent and seeds multiple short conversations against it.
      2. Waits for ingestion, then submits a `DataGenerationJob`
         (scenario=SUPERVISED_FINETUNING, source=traces) that extracts and
         formats the trace data into training/validation JSONL files.
      3. Polls the job and inspects the resulting Azure OpenAI file outputs.
      4. Cleans up the generated files, job, seeded conversations, and agent.

    Prerequisite: the project must have an Application Insights resource
    connected so the agent emits server-side traces. The Foundry project's
    managed identity must have the `Reader` role on that Application Insights
    resource so the data generation job can query the traces.

    To adapt for an existing agent with recent traces, replace step 1 with
    your agent's name and skip the ingestion wait.

USAGE:
    python sample_dataset_generation_job_traces_for_finetuning.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as
       found in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The Azure OpenAI deployment name used
       to drive the agent during trace seeding.
"""

import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import List

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DataGenerationJob,
    DataGenerationJobInputs,
    DataGenerationJobOutputOptions,
    DataGenerationJobScenario,
    FileDataGenerationJobOutput,
    JobStatus,
    PromptAgentDefinition,
    TracesDataGenerationJobOptions,
    TracesDataGenerationJobSource,
)

load_dotenv()


AGENT_INSTRUCTIONS = (
    "Widgets & Gizmos support agent. Be concise. "
    "Refunds: unopened 30 days; defective 90 days; 5-7 business days to process."
)
# Multiple seeded conversations give the SFT job enough trace material to
# extract and format into training/validation samples.
SEED_PROMPTS = [
    "What is your refund policy?",
    "I bought a widget last week and it's defective. What can I do?",
    "How long does it take to process a refund?",
    "Can I return an unopened gizmo after 45 days?",
    "Do you offer exchanges, or only refunds?",
    "What's the warranty period on a sprocket?",
    "I lost my receipt. Can you still process a return?",
    "Are shipping fees refundable?",
]


endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment = os.environ["FOUNDRY_MODEL_NAME"]
DATASET_NAME = "traces-ft-sample"
POLL_INTERVAL_SECONDS = 10
INITIAL_INGEST_WAIT_SECONDS = 60
MAX_JOB_ATTEMPTS = 5
RETRY_WAIT_SECONDS = 60

# Per-run id suffixed on the agent, output file, and job-input names so
# repeated runs don't collide. Kept short (timestamp + 4 hex) to stay under
# the 50-char service limit on output names.
run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
output_name = f"{DATASET_NAME}-{run_id}"
agent_name = f"{DATASET_NAME}-{run_id}"

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    created_agent = None
    created_conversation_ids: List[str] = []
    submitted_job_ids: List[str] = []
    created_file_ids: List[str] = []

    try:
        # 1. Create an agent and seed traces.
        print(f"Create agent `{agent_name}` (model: `{model_deployment}`).")
        created_agent = project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(model=model_deployment, instructions=AGENT_INSTRUCTIONS),
        )
        print(f"Agent created (id: {created_agent.id}, version: {created_agent.version}).")

        seed_start = datetime.now(tz=timezone.utc)
        print(f"Seed {len(SEED_PROMPTS)} conversation(s) against the agent.")
        for prompt in SEED_PROMPTS:
            conversation = openai_client.conversations.create()
            created_conversation_ids.append(conversation.id)
            print(f"  - conversation id: {conversation.id}  (prompt: {prompt!r})")
            openai_client.responses.create(
                conversation=conversation.id,
                input=prompt,
                extra_body={"agent_reference": {"name": created_agent.name, "type": "agent_reference"}},
            )

        print(f"Wait {INITIAL_INGEST_WAIT_SECONDS}s for Application Insights to ingest the spans.", flush=True)
        time.sleep(INITIAL_INGEST_WAIT_SECONDS)

        # 2. Submit a fine-tuning data generation job that reads the agent's
        # traces (retry in case ingestion is still in flight). Small backoff so
        # the seeded spans fall inside the queried window.
        start_time = seed_start - timedelta(minutes=5)

        job = None
        for attempt in range(1, MAX_JOB_ATTEMPTS + 1):
            end_time = datetime.now(tz=timezone.utc)
            print(
                f"Create fine-tuning data generation job from traces for agent `{agent_name}` "
                f"(attempt {attempt}/{MAX_JOB_ATTEMPTS}, "
                f"window: {start_time.isoformat()} .. {end_time.isoformat()})."
            )
            job = project_client.beta.datasets.create_generation_job(
                job=DataGenerationJob(
                    inputs=DataGenerationJobInputs(
                        name=f"traces-ft-{run_id}-a{attempt}",
                        scenario=DataGenerationJobScenario.SUPERVISED_FINETUNING,
                        sources=[
                            TracesDataGenerationJobSource(
                                description="Application Insights conversation traces for the agent.",
                                agent_name=agent_name,
                                start_time=start_time,
                                end_time=end_time,
                            ),
                        ],
                        # max_samples must be in [15, 1000]; caps output dataset size.
                        # train_split=0.8 splits generated samples into a training
                        # and a validation Azure OpenAI file.
                        options=TracesDataGenerationJobOptions(max_samples=15, train_split=0.8),
                        output_options=DataGenerationJobOutputOptions(name=output_name),
                    ),
                ),
            )
            submitted_job_ids.append(job.id)
            print(f"Created data generation job `{job.id}` (status: `{job.status}`).")

            print(f"Poll job `{job.id}` until it reaches a terminal state.", end="", flush=True)
            while job.status not in TERMINAL_STATUSES:
                time.sleep(POLL_INTERVAL_SECONDS)
                print(".", end="", flush=True)
                job = project_client.beta.datasets.get_generation_job(job_id=job.id)
            print()
            print(f"Final job status: `{job.status}`.")

            if job.status == JobStatus.SUCCEEDED:
                break

            message = job.error.message if job.error is not None else "<no error message>"
            if attempt == MAX_JOB_ATTEMPTS:
                raise RuntimeError(f"Job `{job.id}` failed after {MAX_JOB_ATTEMPTS} attempts: {message}")
            print(f"  Attempt {attempt} failed ({message}); wait {RETRY_WAIT_SECONDS}s and retry.")
            time.sleep(RETRY_WAIT_SECONDS)

        assert job is not None  # for type-checker; loop guarantees success path sets job

        # 3. Resolve generated fine-tuning files.
        outputs = (job.result.outputs if job.result is not None else None) or []
        file_outputs = [o for o in outputs if isinstance(o, FileDataGenerationJobOutput)]
        if not file_outputs:
            raise RuntimeError(f"Job `{job.id}` did not produce any file outputs.")

        print(f"Generated {len(file_outputs)} fine-tuning file(s):")
        for output in file_outputs:
            if not output.id:
                raise RuntimeError(f"Job `{job.id}` returned a file output without an id.")
            created_file_ids.append(output.id)
            file_info = openai_client.files.retrieve(file_id=output.id)
            print(f"  - filename=`{file_info.filename}` id=`{output.id}` bytes={file_info.bytes}")
        if job.result is not None and job.result.generated_samples is not None:
            print(f"Generated samples: {job.result.generated_samples}")

    finally:
        # Best-effort cleanup, outputs -> producers (files, job, conversations, agent).
        if created_file_ids:
            for fid in created_file_ids:
                try:
                    openai_client.files.delete(file_id=fid)
                    print(f"Deleted Azure OpenAI file `{fid}`.")
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    print(f"  (warning) could not delete file `{fid}`: {exc}")

        for jid in submitted_job_ids:
            try:
                project_client.beta.datasets.delete_generation_job(job_id=jid)
                print(f"Deleted data generation job `{jid}`.")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"  (warning) could not delete job `{jid}`: {exc}")

        if created_conversation_ids:
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
                print(f"Deleted agent `{created_agent.name}` v{created_agent.version}.")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"  (warning) could not delete agent: {exc}")
