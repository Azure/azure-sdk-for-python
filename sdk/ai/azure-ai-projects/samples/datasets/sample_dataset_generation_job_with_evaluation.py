# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end scenario combining `.beta.datasets` data generation with an
    evaluation run. The sample:

      1. Creates a `DataGenerationJob` (scenario=EVALUATION, type=simple_qna) that
         synthesizes question/answer pairs from an inline prompt and writes them
         to a new versioned Dataset.
      2. Polls the job to completion and resolves the resulting `DatasetVersion`.
      3. Creates an OpenAI evaluation (`client.evals.create`) with builtin
         Azure AI evaluators.
      4. Runs the evaluation against the generated dataset by passing the
         dataset's id as the run's `file_id`.
      5. Cleans up the evaluation and the data generation job.

USAGE:
    python sample_dataset_generation_job_with_evaluation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of an LLM model deployment used both
       to generate the QnA samples and as the judge model for builtin evaluators
       (e.g. `gpt-4o`, `gpt-5`).
    3) DATASET_NAME - Optional. Name to assign to the generated output dataset.
       Defaults to `dataset-generation-eval-sample`.
    4) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between status
       polls for both the data generation job and the evaluation run. Defaults to 10.
"""

import os
import time

from dotenv import load_dotenv
from openai.types.eval_create_params import DataSourceConfigCustom
from openai.types.evals.create_eval_completions_run_data_source_param import (
    CreateEvalCompletionsRunDataSourceParam,
    InputMessagesTemplate,
    InputMessagesTemplateTemplateEvalItem,
    SourceFileID,
)
from openai.types.responses.response_input_text_param import ResponseInputTextParam

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DataGenerationJob,
    DataGenerationJobInputs,
    DataGenerationJobOutputOptions,
    DataGenerationJobScenario,
    DataGenerationModelOptions,
    DatasetDataGenerationJobOutput,
    DatasetVersion,
    JobStatus,
    PromptDataGenerationJobSource,
    SimpleQnADataGenerationJobOptions,
    TestingCriterionAzureAIEvaluator,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
dataset_name = os.environ.get("DATASET_NAME", "dataset-generation-eval-sample")
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # ------------------------------------------------------------------
    # 1. Generate a QnA evaluation dataset from an inline prompt.
    # ------------------------------------------------------------------
    print("Create a data generation job.")
    job = DataGenerationJob(
        inputs=DataGenerationJobInputs(
            name="qna-from-policy-prompt",
            scenario=DataGenerationJobScenario.EVALUATION,
            sources=[
                PromptDataGenerationJobSource(
                    description="Contoso refund policy",
                    prompt=(
                        "Contoso offers a full refund within 30 days of purchase for any product "
                        "returned in its original condition. After 30 days, store credit may be "
                        "issued at the discretion of customer support. Digital goods are "
                        "non-refundable once downloaded."
                    ),
                ),
            ],
            options=SimpleQnADataGenerationJobOptions(
                # Service requires max_samples to be between 15 and 1000.
                max_samples=15,
                model_options=DataGenerationModelOptions(model=model_name),
            ),
            output_options=DataGenerationJobOutputOptions(
                name=dataset_name,
                description="QnA pairs generated from the Contoso refund policy prompt.",
                tags={"sample": "dataset-generation-with-evaluation"},
            ),
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

    # Resolve the DatasetVersion so we can use its id as the eval run's file_id.
    dataset: DatasetVersion = project_client.datasets.get(name=output_name, version=output_version)
    print(f"Generated dataset: name=`{dataset.name}` version=`{dataset.version}` id=`{dataset.id}`")

    # ------------------------------------------------------------------
    # 2. Create an evaluation that scores the model's answers to the
    #    generated questions.
    # ------------------------------------------------------------------
    # The `simple_qna` generator produces records with `query` and `ground_truth`
    # fields. The evaluation run below sends each `query` through a model target
    # to produce a response, and the evaluators score that response.
    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "ground_truth": {"type": "string"},
            },
            "required": ["query"],
        },
        include_sample_schema=True,
    )

    testing_criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="coherence",
            evaluator_name="builtin.coherence",
            initialization_parameters={"deployment_name": model_name},
            data_mapping={"query": "{{item.query}}", "response": "{{sample.output_text}}"},
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="fluency",
            evaluator_name="builtin.fluency",
            initialization_parameters={"deployment_name": model_name},
            data_mapping={"response": "{{sample.output_text}}"},
        ),
    ]

    print("Create the evaluation.")
    eval_object = openai_client.evals.create(
        name="generated-qna-evaluation",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created (id: {eval_object.id}).")

    # ------------------------------------------------------------------
    # 3. Run the evaluation against the generated dataset.
    # ------------------------------------------------------------------
    # `completions` data source: for each item in the dataset, render the
    # input_messages template, send to `model`, and feed the response into
    # the testing criteria as `sample.output_text`.
    print(f"Create an evaluation run that consumes dataset `{dataset.id}`.")
    input_message = InputMessagesTemplate(
        type="template",
        template=[
            InputMessagesTemplateTemplateEvalItem(
                type="message",
                role="developer",
                content=ResponseInputTextParam(
                    type="input_text",
                    text=(
                        "You are a Contoso customer-support assistant. Answer the user's "
                        "question about the Contoso refund policy clearly and concisely."
                    ),
                ),
            ),
            InputMessagesTemplateTemplateEvalItem(
                type="message",
                role="user",
                content=ResponseInputTextParam(
                    type="input_text",
                    text="{{item.query}}",
                ),
            ),
        ],
    )
    data_source = CreateEvalCompletionsRunDataSourceParam(
        type="completions",
        source=SourceFileID(type="file_id", id=dataset.id or ""),
        input_messages=input_message,
        model=model_name,
    )
    eval_run = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name="generated-qna-evaluation-run",
        data_source=data_source,
    )
    print(f"Evaluation run created (id: {eval_run.id}).")

    while eval_run.status not in ("completed", "failed"):
        time.sleep(poll_interval_seconds)
        eval_run = openai_client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_object.id)
    print(f"Final eval run status: `{eval_run.status}`.")

    if eval_run.status == "completed":
        print(f"Result counts: {eval_run.result_counts}")
        print(f"Eval run report URL: {eval_run.report_url}")
        output_items = list(openai_client.evals.runs.output_items.list(run_id=eval_run.id, eval_id=eval_object.id))
        print(f"Output items (total: {len(output_items)}):")
        # Print a per-item summary (avoid pprint on the full payload to keep the
        # output ASCII-safe on Windows consoles and easy to scan).
        for idx, item in enumerate(output_items, start=1):
            results = getattr(item, "results", None) or []
            scores = ", ".join(
                f"{r.get('name', '?')}={r.get('score', 'n/a')} ({r.get('passed', 'n/a')})"
                for r in results
                if isinstance(r, dict)
            )
            print(f"  item {idx}: status={item.status} | {scores}")
    else:
        print("Evaluation run did not complete successfully.")

    # ------------------------------------------------------------------
    # 4. Clean up.
    # ------------------------------------------------------------------
    print(f"Delete evaluation `{eval_object.id}`.")
    openai_client.evals.delete(eval_id=eval_object.id)

    print(f"Delete the data generation job `{job.id}`.")
    project_client.beta.datasets.delete_generation_job(job_id=job.id)
