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

    agent = project_client.agents.create_version(
        agent_name=os.environ["AZURE_AI_AGENT_NAME"],
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant that answers general questions",
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

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

    continuous_eval_rule = project_client.evaluation_rules.delete(id=continuous_eval_rule.id)
    print("Continuous Evaluation Rule deleted")

    openai_client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")

    project_client.agents.delete(agent_name=agent.name)
    print("Agent deleted")
