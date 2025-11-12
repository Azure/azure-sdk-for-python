# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to create and run an evaluation for an Azure AI agent response
    using the synchronous AIProjectClient.

    The OpenAI compatible Evals calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

USAGE:
    python sample_agent_response_evaluation_with_function_tool.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import json
import os
import time
from pprint import pprint
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, Tool, FunctionTool
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam

load_dotenv()

model_deployment_name = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

# Define a function tool for the model to use
func_tool = FunctionTool(
    name="get_horoscope",
    parameters={
        "type": "object",
        "properties": {
            "sign": {
                "type": "string",
                "description": "An astrological sign like Taurus or Aquarius",
            },
        },
        "required": ["sign"],
        "additionalProperties": False,
    },
    description="Get today's horoscope for an astrological sign.",
    strict=True,
)

tools: list[Tool] = [func_tool]


def get_horoscope(sign: str) -> str:
    """Generate a horoscope for the given astrological sign."""
    return f"{sign}: Next Tuesday you will befriend a baby otter."

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:

    openai_client = project_client.get_openai_client()

    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=model_deployment_name,
            instructions="You are a helpful assistant that can use function tools.",
            tools=tools,
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # Prompt the model with tools defined
    response = openai_client.responses.create(
        input="What is my horoscope? I am an Aquarius.",
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Response output: {response.output_text}")

    input_list: ResponseInputParam = []
    # Process function calls
    for item in response.output:
        if item.type == "function_call":
            if item.name == "get_horoscope":
                # Execute the function logic for get_horoscope
                horoscope = get_horoscope(**json.loads(item.arguments))

                # Provide function call results to the model
                input_list.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=json.dumps({"horoscope": horoscope}),
                    )
                )

    print("Final input:")
    print(input_list)

    response = openai_client.responses.create(
        input=input_list,
        previous_response_id=response.id,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Response output: {response.output_text} (id: {response.id})")

    data_source_config = {"type": "azure_ai_source", "scenario": "responses"}
    testing_criteria = [
        {"type": "azure_ai_evaluator", "name": "tool_call_accuracy", "evaluator_name": "builtin.tool_call_accuracy", "initialization_parameters": {"deployment_name": f"{model_deployment_name}"}}
    ]
    eval_object = openai_client.evals.create(
        name="Agent Response Evaluation",
        data_source_config=data_source_config, # type: ignore
        testing_criteria=testing_criteria, # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    data_source = {
        "type": "azure_ai_responses",
        "item_generation_params": {
            "type": "response_retrieval",
            "data_mapping": {"response_id": "{{item.resp_id}}"},
            "source": {"type": "file_content", "content": [{"item": {"resp_id": response.id}}]},
        },
    }

    response_eval_run = openai_client.evals.runs.create(
        eval_id=eval_object.id, name=f"Evaluation Run for Agent {agent.name}", data_source=data_source
    )
    print(f"Evaluation run created (id: {response_eval_run.id})")

    while response_eval_run.status not in ["completed", "failed"]:
        response_eval_run = openai_client.evals.runs.retrieve(run_id=response_eval_run.id, eval_id=eval_object.id)
        print(f"Waiting for eval run to complete... current status: {response_eval_run.status}")
        time.sleep(5)

    if response_eval_run.status == "completed":
        print("\n✓ Evaluation run completed successfully!")
        print(f"Result Counts: {response_eval_run.result_counts}")

        output_items = list(
            openai_client.evals.runs.output_items.list(run_id=response_eval_run.id, eval_id=eval_object.id)
        )
        print(f"\nOUTPUT ITEMS (Total: {len(output_items)})")
        print(f"Eval Run Report URL: {response_eval_run.report_url}")

        print(f"{'-'*60}")
        pprint(output_items)
        print(f"{'-'*60}")
    else:
        print(f"Eval Run Report URL: {response_eval_run.report_url}")
        print("\n✗ Evaluation run failed.")

    # openai_client.evals.delete(eval_id=eval_object.id)
    # print("Evaluation deleted")

    project_client.agents.delete(agent_name=agent.name)
    print("Agent deleted")
