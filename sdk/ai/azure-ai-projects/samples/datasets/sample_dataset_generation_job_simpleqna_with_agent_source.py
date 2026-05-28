# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates an evaluation dataset from a prompt agent's definition using the
    `simple_qna` recipe. The sample is fully self-contained — it creates a
    short-lived `PromptAgentDefinition` whose `instructions` give the service
    enough material to synthesize QnA pairs, then uses that agent as the
    source for the data generation job. The sample:

      1. Creates a `PromptAgentDefinition` agent with domain-specific
         instructions (a small Widgets & Gizmos customer-support persona).
      2. Creates a `DataGenerationJob` (scenario=EVALUATION, type=simple_qna)
         whose source is an `Agent` reference pointing at the new agent. The
         service fetches the agent's instructions / prompt and uses the
         configured LLM to synthesize question / answer pairs from them.
      3. Polls the job to completion and resolves the resulting `DatasetVersion`.
      4. Cleans up the data generation job, the generated dataset, and the agent version.

    `simple_qna` REQUIRES `model_options`. For `simple_qna` evaluation jobs the
    deployed model must support the Azure OpenAI Responses API. See the
    supported-model list:
    https://learn.microsoft.com/azure/foundry/openai/how-to/responses?tabs=python-key#model-support

    If you want to synthesize QnA from an agent's recorded conversation traces
    instead of its definition, see
    `sample_dataset_generation_job_traces_for_evaluation.py` (traces recipe).

USAGE:
    python sample_dataset_generation_job_simpleqna_with_agent_source.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of an Azure OpenAI model
       deployment used both as the prompt agent's backing model and to synthesize
       the QnA samples. For `simple_qna` evaluation, choose a Responses-API
       capable model (see the link in the description).
    3) DATASET_NAME - Optional. Name to assign to the generated output dataset.
       Defaults to `simpleqna-agent-source-sample`. The service caps the
       rendered output name at 50 characters, so keep custom values short —
       the sample appends a unique run id suffix.
    4) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between status
       polls for the data generation job. Defaults to 10.
"""

import os
import time
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentDataGenerationJobSource,
    DataGenerationJob,
    DataGenerationJobInputs,
    DataGenerationJobOutputOptions,
    DataGenerationJobScenario,
    DataGenerationModelOptions,
    DatasetDataGenerationJobOutput,
    DatasetVersion,
    JobStatus,
    PromptAgentDefinition,
    SimpleQnADataGenerationJobOptions,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
dataset_name = os.environ.get("DATASET_NAME", "simpleqna-agent-source-sample")
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Unique per-run names so repeated runs do not collide.
# Output names are capped at 50 characters by the service.
run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
output_dataset_name = f"{dataset_name}-{run_id}"
if len(output_dataset_name) > 50:
    raise ValueError(
        f"Output dataset name `{output_dataset_name}` exceeds the 50-character service limit. "
        f"Lower DATASET_NAME (currently `{dataset_name}`) so that `<DATASET_NAME>-<run id>` fits within 50 characters."
    )

# The prompt agent's instructions seed the QnA generation. Make them concrete
# and domain-specific so the service has enough material to synthesize from.
AGENT_INSTRUCTIONS = """You are a customer support assistant for Acme's "Widgets & Gizmos" product line.

Product catalog you can answer about:
- Widget: blue, manufactured at Factory 7 in Acme, carbon-fiber, rated to 80 C, sold in packs of 4, 250 g each, USD 24.99 per pack.
- Gizmo: red, manufactured at Factory 12 in Bedrock, carbon-fiber, rated to 80 C, sold individually, 1.2 kg each, USD 49.99.
- Sprocket: green, manufactured at Factory 3 in Acme, stainless steel, rated to 200 C, sold individually, 500 g each, USD 14.99.

Operational policy:
- Factory operates weekdays 0700-1900 local time and is closed on public holidays except the annual maintenance run on December 27.
- Warranty claims must include the serial number printed on the underside of the product, emailed to support@example.com.
- Returns are accepted within 30 days if unopened; opened items are eligible for repair only.
- Bulk orders of 50 or more units use the sales@example.com channel and get an extended 90-day return window.
- Standard support responds within one business day; priority support responds within four hours.
- Free shipping on orders over USD 75.

When asked about anything outside this catalog and policy, politely say you do not have that information.
"""

agent_name = f"widgets-gizmos-support-{run_id}"

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    # ------------------------------------------------------------------
    # 1. Create a short-lived prompt agent to act as the source.
    # ------------------------------------------------------------------
    print(f"Create prompt agent `{agent_name}`.")
    agent = project_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model_name,
            instructions=AGENT_INSTRUCTIONS,
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version}).")

    try:
        # ------------------------------------------------------------------
        # 2. Submit a SimpleQnA data generation job sourced from the agent.
        # ------------------------------------------------------------------
        # The service fetches the agent's instructions / prompt and uses
        # `model_options.model` to synthesize QnA pairs from them.
        print(f"Create a SimpleQnA evaluation job sourced from agent `{agent.name}` (version {agent.version}).")
        job = DataGenerationJob(
            inputs=DataGenerationJobInputs(
                name=f"simpleqna-agent-{run_id}",
                scenario=DataGenerationJobScenario.EVALUATION,
                sources=[
                    AgentDataGenerationJobSource(
                        description="Agent definition (instructions / prompt) used to seed QnA generation.",
                        agent_name=agent.name,
                        agent_version=agent.version,
                    ),
                ],
                options=SimpleQnADataGenerationJobOptions(
                    # Service requires max_samples to be between 15 and 1000.
                    max_samples=15,
                    # `simple_qna` REQUIRES model_options.
                    model_options=DataGenerationModelOptions(model=model_name),
                ),
                output_options=DataGenerationJobOutputOptions(name=output_dataset_name),
            ),
        )
        job = project_client.beta.datasets.create_generation_job(job=job)
        print(f"Created data generation job `{job.id}` (status: `{job.status}`).")

        print(f"Poll job `{job.id}` until it reaches a terminal state.", end="", flush=True)
        while True:
            job = project_client.beta.datasets.get_generation_job(job_id=job.id)
            if job.status in TERMINAL_STATUSES:
                break
            time.sleep(poll_interval_seconds)
            print(".", end="", flush=True)
        print()
        print(f"Final job status: `{job.status}`.")

        if job.status != JobStatus.SUCCEEDED:
            message = job.error.message if job.error is not None else "<no error message>"
            raise RuntimeError(f"Job `{job.id}` ended with status `{job.status}`: {message}")

        # Locate the Dataset output produced by the job.
        output_name: str = ""
        output_version: str = ""
        for output in (job.result.outputs if job.result is not None else None) or []:
            if isinstance(output, DatasetDataGenerationJobOutput):
                output_name = output.name or ""
                output_version = output.version or ""
                break
        if not output_name or not output_version:
            raise RuntimeError(f"Job `{job.id}` did not produce a dataset output.")

        dataset: DatasetVersion = project_client.datasets.get(name=output_name, version=output_version)
        print(f"Generated dataset: name=`{dataset.name}` version=`{dataset.version}` id=`{dataset.id}`")
        if job.result is not None and job.result.generated_samples is not None:
            print(f"Generated samples: {job.result.generated_samples}")

        # ------------------------------------------------------------------
        # 3. Clean up the generated dataset and the data generation job
        #    (the agent is deleted in the `finally` block below).
        # ------------------------------------------------------------------
        print(f"Delete the generated dataset `{dataset.name}` v{dataset.version}.")
        project_client.datasets.delete(name=dataset.name or "", version=dataset.version or "")

        print(f"Delete the data generation job `{job.id}`.")
        project_client.beta.datasets.delete_generation_job(job_id=job.id)
    finally:
        # The agent is short-lived — always delete it, even if the job failed.
        print(f"Delete the prompt agent `{agent.name}` (version {agent.version}).")
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
