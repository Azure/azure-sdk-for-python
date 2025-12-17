# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create and manage evaluation rules
    using the synchronous AIProjectClient.

    The OpenAI compatible Evals calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

PREQUISITE:
    To enable continuous evaluation, plase assign project managed identity with the following steps:
    1) Open https://portal.azure.com
    2) Search for the AI Foundry project from search bar
    3) Choose "Access control (IAM)" -> "Add"
    4) In "Add role assignment", search for "Azure AI User"
    5) Choose "User, group, or service principal" or "Managed Identity", add your AI Foundry project managed identity

USAGE:
    python sample_continuous_evaluation_rule.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_AGENT_NAME - The name of the AI agent to use for evaluation.
    3) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    EvaluationRule,
    ContinuousEvaluationRuleAction,
    EvaluationRuleFilter,
    EvaluationRuleEventType,
)

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # Create agent

    agent = project_client.agents.create_version(
        agent_name=os.environ["AZURE_AI_AGENT_NAME"],
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant that answers general questions",
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # Setup agent continuous evaluation

    data_source_config = {"type": "azure_ai_source", "scenario": "responses"}
    testing_criteria = [
        {"type": "azure_ai_evaluator", "name": "violence_detection", "evaluator_name": "builtin.violence"}
    ]
    eval_object = openai_client.evals.create(
        name="Continuous Evaluation",
        data_source_config=data_source_config,  # type: ignore
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    continuous_eval_rule = project_client.evaluation_rules.create_or_update(
        id="my-continuous-eval-rule",
        evaluation_rule=EvaluationRule(
            display_name="My Continuous Eval Rule",
            description="An eval rule that runs on agent response completions",
            action=ContinuousEvaluationRuleAction(eval_id=eval_object.id, max_hourly_runs=100),
            event_type=EvaluationRuleEventType.RESPONSE_COMPLETED,
            filter=EvaluationRuleFilter(agent_name=agent.name),
            enabled=True,
        ),
    )
    print(
        f"Continuous Evaluation Rule created (id: {continuous_eval_rule.id}, name: {continuous_eval_rule.display_name})"
    )

    # Run agent

    conversation = openai_client.conversations.create(
        items=[{"type": "message", "role": "user", "content": "What is the size of France in square miles?"}],
    )
    print(f"Created conversation with initial user message (id: {conversation.id})")

    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        input="",
    )
    print(f"Response output: {response.output_text}")

    # Loop for 5 questions

    MAX_QUESTIONS = 10
    for i in range(0, MAX_QUESTIONS):
        openai_client.conversations.items.create(
            conversation_id=conversation.id,
            items=[{"type": "message", "role": "user", "content": f"Question {i}: What is the capital city?"}],
        )
        print(f"Added a user message to the conversation")

        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            input="",
        )
        print(f"Response output: {response.output_text}")

        # Wait for 10 seconds for evaluation, and then retrieve eval results

        time.sleep(10)
        eval_run_list = openai_client.evals.runs.list(
            eval_id=eval_object.id,
            order="desc",
            limit=10,
        )

        if len(eval_run_list.data) > 0:
            eval_run_ids = [eval_run.id for eval_run in eval_run_list.data]
            print(f"Finished evals: {' '.join(eval_run_ids)}")

    # Get the report_url

    print("Agent runs finished")

    MAX_LOOP = 20
    for _ in range(0, MAX_LOOP):
        print(f"Waiting for eval run to complete...")

        eval_run_list = openai_client.evals.runs.list(
            eval_id=eval_object.id,
            order="desc",
            limit=10,
        )

        if len(eval_run_list.data) > 0 and eval_run_list.data[0].report_url:
            run_report_url = eval_run_list.data[0].report_url
            # Remove the last 2 URL path segments (run/continuousevalrun_xxx)
            report_url = '/'.join(run_report_url.split('/')[:-2])
            print(f"To check evaluation runs, please open {report_url} from the browser")
            break

        time.sleep(10)
