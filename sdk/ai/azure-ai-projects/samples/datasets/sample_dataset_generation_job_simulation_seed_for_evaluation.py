# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates simulation seeds for multi-turn agent evaluation from a
    description of an agent's purpose. The sample:

      1. Submits an `EvaluationDataGenerationJobInputs` job (scenario `evaluation`,
         generation type `simulation_seed`) whose `Prompt` source describes what
         the agent under test is for. The service uses the configured LLM to
         synthesize test cases for multi-turn conversations and writes them to a
         new versioned Dataset.
      2. Polls the job to completion and resolves the resulting `DatasetVersion`.
      3. Downloads the dataset content and prints the first few rows. Each row
         includes fields such as `id`, `category`, `test_case_description`, and
         `desired_num_turns`.
      4. Cleans up the generated dataset.

    `SimulationSeedDataGenerationJobOptions` can be used with prompt, file, or
    agent sources. The service requires `max_samples` (1-1000) for this generation
    type; because the options class does not expose it as a keyword argument, the
    sample sets it through the model's mapping interface.

USAGE:
    python sample_dataset_generation_job_simulation_seed_for_evaluation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.8.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of an Azure OpenAI model
       deployment used to synthesize the simulation seeds. The deployed model must
       support the Azure OpenAI Responses API. See the supported-model list:
       https://learn.microsoft.com/azure/foundry/openai/how-to/responses?tabs=python-key#model-support
    3) DATASET_NAME - Optional. Name to assign to the generated output dataset.
       Defaults to `simulation-seed-sample`. The service caps the rendered output
       name at 50 characters, so keep custom values short — the sample appends a
       unique run id suffix.
    4) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between status
       polls for the data generation job. Defaults to 10.
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DataGenerationModelOptions,
    DatasetDataGenerationJobOutput,
    DatasetVersion,
    EvaluationDataGenerationJobInputs,
    EvaluationDataGenerationJobOutputTarget,
    PromptDataGenerationJobSource,
    SimulationSeedDataGenerationJobOptions,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
dataset_name = os.environ.get("DATASET_NAME", "simulation-seed-sample")
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

MAX_ROWS_TO_PRINT = 5

# Unique per-run names so repeated runs do not collide.
# Output names are capped at 50 characters by the service.
run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
output_dataset_name = f"{dataset_name}-{run_id}"
if len(output_dataset_name) > 50:
    raise ValueError(
        f"Output dataset name `{output_dataset_name}` exceeds the 50-character service limit. "
        f"Lower DATASET_NAME (currently `{dataset_name}`) so that `<DATASET_NAME>-<run id>` fits within 50 characters."
    )

# Describes the purpose of the agent under test. The service synthesizes
# multi-turn test cases (simulation seeds) that exercise this purpose.
AGENT_PURPOSE = """The agent is a customer support assistant for Acme's "Widgets & Gizmos" online store.
It answers questions about products (Widget, Gizmo, Sprocket), order status, shipping,
returns (accepted within 30 days if unopened), warranty claims (require the product serial number),
and bulk orders (50+ units get an extended 90-day return window). It must politely decline
requests outside this scope and never share other customers' order details.
"""


def read_dataset_rows(project_client: AIProjectClient, dataset: DatasetVersion, max_rows: int) -> List[Dict[str, Any]]:
    """Download the dataset's JSON Lines content via a SAS credential and return up to `max_rows` rows."""
    dataset_credential = project_client.datasets.get_credentials(name=dataset.name, version=dataset.version)
    sas_uri = dataset_credential.blob_reference.credential.sas_uri
    # Blobs belonging to this dataset version are addressed relative to the SAS container.
    container_path = urlsplit(sas_uri).path.rstrip("/")
    data_path = urlsplit(dataset.data_uri).path
    blob_prefix = data_path[len(container_path) :].lstrip("/") if data_path.startswith(container_path) else ""

    rows: List[Dict[str, Any]] = []
    with ContainerClient.from_container_url(container_url=sas_uri) as container_client:
        for blob_name in container_client.list_blob_names(name_starts_with=blob_prefix or None):
            content = container_client.download_blob(blob_name).readall().decode("utf-8")
            for line in content.splitlines():
                if line.strip():
                    rows.append(json.loads(line))
                if len(rows) >= max_rows:
                    return rows
    return rows


def main() -> None:
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        dataset: Optional[DatasetVersion] = None

        try:
            # ------------------------------------------------------------------
            # 1. Submit a simulation seed data generation job.
            # ------------------------------------------------------------------
            generation_configuration = SimulationSeedDataGenerationJobOptions(
                model_options=DataGenerationModelOptions(model=model_name),
            )
            # The service currently requires `max_samples` (1-1000) for `simulation_seed`
            # jobs, but `SimulationSeedDataGenerationJobOptions` does not expose it as a
            # keyword argument, so set it through the model's mapping interface.
            generation_configuration["max_samples"] = 15

            job = EvaluationDataGenerationJobInputs(
                name=f"simulation-seed-{run_id}",
                sources=[
                    PromptDataGenerationJobSource(
                        description="Purpose of the customer support agent under test.",
                        prompt=AGENT_PURPOSE,
                    ),
                ],
                generation_configuration=generation_configuration,
                output_configuration=EvaluationDataGenerationJobOutputTarget(
                    name=output_dataset_name,
                    description="Simulation seeds for multi-turn evaluation of the Widgets & Gizmos support agent.",
                    tags={"sample": "dataset-generation-simulation-seed"},
                ),
            )

            print("Begin creating a dataset generation job.")
            poller = project_client.datasets.begin_create_generation_job(
                job=job,
                polling_interval=poll_interval_seconds,
            )

            # Optional: While SDK is polling, periodically print the job status until the job is complete
            print("Periodically check job status:")
            while not poller.done():
                print(f"\tstatus=`{poller.status()}`")
                time.sleep(poll_interval_seconds)

            # Since done() is true, result() returns the final deserialized job result without
            # waiting further. It also propagates any LRO polling exception.
            job_result = poller.result()
            print(f"Final LRO status: `{poller.status()}`.")
            print(f"Data generation result: {job_result}")

            # ------------------------------------------------------------------
            # 2. Resolve the generated dataset.
            # ------------------------------------------------------------------
            dataset_output = next(
                (o for o in job_result.outputs or [] if isinstance(o, DatasetDataGenerationJobOutput)),
                None,
            )
            if dataset_output is None or not dataset_output.name or not dataset_output.version:
                raise RuntimeError("The data generation job did not produce a dataset output.")

            dataset = project_client.datasets.get(name=dataset_output.name, version=dataset_output.version)
            print(f"Generated dataset: name=`{dataset.name}` version=`{dataset.version}` id=`{dataset.id}`")
            if job_result.generated_samples is not None:
                print(f"Generated samples: {job_result.generated_samples}")

            # ------------------------------------------------------------------
            # 3. Print the first few simulation seeds.
            # ------------------------------------------------------------------
            rows = read_dataset_rows(project_client, dataset, MAX_ROWS_TO_PRINT)
            print(f"First {len(rows)} simulation seed(s):")
            for row in rows:
                print(
                    f"  - id=`{row.get('id')}` category=`{row.get('category')}` "
                    f"desired_num_turns={row.get('desired_num_turns')}\n"
                    f"    test_case_description: {row.get('test_case_description')}"
                )

        finally:
            # ------------------------------------------------------------------
            # 4. Clean up (best effort, so partial failures do not leak resources).
            # ------------------------------------------------------------------
            # Delete the generated dataset.
            if dataset is not None:
                print(f"Delete the generated dataset `{dataset.name}` v{dataset.version}.")
                try:
                    project_client.datasets.delete(name=dataset.name or "", version=dataset.version or "")
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    print(f"  (warning) could not delete dataset: {exc}")


if __name__ == "__main__":
    main()
