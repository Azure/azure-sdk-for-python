# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Evaluate single-turn and multi-turn agent output using builtin.output_quality.
    Single-turn data uses query and response; the multi-turn conversation keeps
    all messages in one row. The composite evaluator scores
    fluency, coherence, intent resolution, task adherence, groundedness, and
    task completion in a single call.

USAGE:
    python sample_output_quality.py

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT - The Foundry project endpoint.
    2) FOUNDRY_MODEL_NAME - The model deployment used by the evaluator.
"""

import os
import time
from pprint import pprint

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import TestingCriterionAzureAIEvaluator
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from openai.types.eval_create_params import DataSourceConfigCustom
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)

load_dotenv()


def main() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]

    # single-turn example
    query = "What is the capital of France?"
    response = "The capital of France is Paris."

    # multi-turn example
    messages = [
        {"role": "user", "content": [{"type": "text", "text": "What is the return period for this item?"}]},
        {"role": "assistant", "content": [{"type": "text", "text": "The return period is 30 days."}]},
        {"role": "user", "content": [{"type": "text", "text": "I bought it 10 days ago. Can I still return it?"}]},
        {
            "role": "assistant",
            "content": [{"type": "text", "text": "Yes. Your purchase is within the 30-day return period."}],
        },
    ]

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):
        for evaluation_level, item in (
            ("turn", {"query": query, "response": response}),
            ("conversation", {"messages": messages}),
        ):
            if evaluation_level == "turn":
                properties = {"query": {"type": "string"}, "response": {"type": "string"}}
                data_mapping = {"query": "{{item.query}}", "response": "{{item.response}}"}
            else:
                properties = {"messages": {"type": "array", "items": {"type": "object"}}}
                data_mapping = {"messages": "{{item.messages}}"}

            evaluation = client.evals.create(
                name=f"Output Quality - {evaluation_level}",
                data_source_config=DataSourceConfigCustom(
                    type="custom",
                    item_schema={
                        "type": "object",
                        "properties": properties,
                        "required": list(properties),
                    },
                    include_sample_schema=evaluation_level == "turn",
                ),
                testing_criteria=[
                    TestingCriterionAzureAIEvaluator(
                        type="azure_ai_evaluator",
                        name="output_quality",
                        evaluator_name="builtin.output_quality",
                        initialization_parameters={
                            "deployment_name": model_deployment_name,
                            "evaluation_level": evaluation_level,
                        },
                        data_mapping=data_mapping,
                    )
                ],
            )
            try:
                run = client.evals.runs.create(
                    eval_id=evaluation.id,
                    name=f"{evaluation_level}_inline_run",
                    extra_body={"evaluation_level": evaluation_level},
                    data_source=CreateEvalJSONLRunDataSourceParam(
                        type="jsonl",
                        source=SourceFileContent(
                            type="file_content",
                            content=[SourceFileContentContent(item=item)],
                        ),
                    ),
                )
                while run.status not in ("completed", "failed", "cancelled"):
                    time.sleep(5)
                    run = client.evals.runs.retrieve(run_id=run.id, eval_id=evaluation.id)
                if run.status != "completed":
                    raise RuntimeError(f"{evaluation_level} output quality evaluation {run.status}: {run.error}")
                print(f"{evaluation_level} output quality results:")
                pprint(list(client.evals.runs.output_items.list(run_id=run.id, eval_id=evaluation.id)))
            finally:
                client.evals.delete(eval_id=evaluation.id)


if __name__ == "__main__":
    main()
