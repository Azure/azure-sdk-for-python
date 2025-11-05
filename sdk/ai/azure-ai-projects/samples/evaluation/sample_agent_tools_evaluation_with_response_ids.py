# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to create and run an evaluation for an Azure AI 
    response with function tools using the synchronous AIProjectClient, and evaluate 
    using response ID. The model automatically executes the function tool in a single response.

USAGE:
    python sample_agent_function_tool_evaluation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
import time
import json
from pprint import pprint
from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

# 1. Define a function tool for the agent
tools = [
    {
        "type": "function",
        "strict": True,
        "name": "get_horoscope",
        "description": "Get today's horoscope for an astrological sign.",
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "sign": {
                    "type": "string",
                    "description": "An astrological sign like Taurus or Aquarius",
                },
            },
            "required": ["sign"],
        },
    },
]


def get_horoscope(sign):
    return f"{sign}: Next Tuesday you will befriend a baby otter."


# Create input message
input_message = "What is my horoscope? I am an Aquarius."

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=AzureCliCredential(),
    api_version="2025-11-15-preview"
)

with project_client:

    # [START agent_function_tool_evaluation]
    openai_client = project_client.get_openai_client()
    
    # Explicitly set the API version on the client to ensure it's used for all requests
    openai_client._custom_query = {"api-version": "2025-11-15-preview"}

    # 2. Create response with tools - model will automatically call functions as needed
    response = openai_client.responses.create(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        input=input_message,
        tools=tools,
        instructions="Use the get_horoscope function to provide the user's horoscope.",
    )
    
    print(f"Response output: {response.output_text}")
    print(f"Response ID: {response.id}")
    print(f"\nResponse output items:")
    for item in response.output:
        print(f"  - Type: {item.type}")
        if hasattr(item, 'name'):
            print(f"    Name: {item.name}")
        if hasattr(item, 'content'):
            print(f"    Content: {item.content}")

    # 3. Create evaluation using the response ID
    data_source_config = {
        "type": "azure_ai_source",
        "scenario": "responses"
    }
    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "tool_call_accuracy",
            "evaluator_name": "builtin.tool_call_accuracy"
        }
    ]
    eval_object = openai_client.evals.create(
        name="Function Tool Response Evaluation",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"\nEvaluation created (id: {eval_object.id}, name: {eval_object.name})")

    # 4. Create eval run with the response ID
    data_source = {
        "type": "azure_ai_responses",
        "item_generation_params": {
            "type": "response_retrieval",
            "data_mapping": {
                "response_id": "{{item.resp_id}}"
            },
            "source": {
                "type": "file_content",
                "content": [
                    { "item": { "resp_id": response.id } }
                ]
            }
        }
    }

    response_eval_run = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name=f"Evaluation Run for Horoscope Response",
        data_source=data_source
    )
    print(f"Evaluation run created (id: {response_eval_run.id})")

    # 5. Wait for evaluation to complete
    while response_eval_run.status not in ["completed", "failed"]:
        response_eval_run = openai_client.evals.runs.retrieve(run_id=response_eval_run.id, eval_id=eval_object.id)
        print(f"Waiting for eval run to complete... current status: {response_eval_run.status}")
        time.sleep(5)

    # 6. Display evaluation results
    if response_eval_run.status == "completed":
        print("\n✓ Evaluation run completed successfully!")
        print(f"Result Counts: {response_eval_run.result_counts}")
        
        output_items = list(openai_client.evals.runs.output_items.list(
            run_id=response_eval_run.id,
            eval_id=eval_object.id
        ))        
        print(f"\nOUTPUT ITEMS (Total: {len(output_items)})")
        print(f"{'-'*60}")
        pprint(output_items)
        print(f"{'-'*60}")
    else:
        print("\n✗ Evaluation run failed.")
        
    # Cleanup (commented out to keep evaluation for inspection)
    openai_client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")

    # [END agent_function_tool_evaluation]