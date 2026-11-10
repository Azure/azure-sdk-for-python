# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an evaluation rule that evaluates
    an agent against a fixed set of queries on a recurring schedule, using the
    synchronous AIProjectClient.

    The rule uses a `DatasetEvaluationRuleAction` with the `timerTrigger` event type.
    On each scheduled occurrence, the service sends the queries to the agent and adds
    an evaluation run that scores the agent's responses to the eval. The source can also
    be a JSONL or CSV dataset that already contains responses, or a model target.

    The OpenAI compatible Evals calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

PREREQUISITE:
    Assign the project managed identity the "Foundry User" role:
    1) Open https://portal.azure.com
    2) Search for the AI Foundry project from search bar
    3) Choose "Access control (IAM)" -> "Add"
    4) In "Add role assignment", search for "Foundry User"
    5) Choose "User, group, or service principal" or "Managed Identity", add your AI Foundry project managed identity

USAGE:
    python sample_dataset_evaluation_rule.py

    Before running the sample:

    pip install "azure-ai-projects>=2.11.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model used by the agent and the evaluators, as found
       under the "Name" column in the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the agent to create. If not set, defaults to "MyScheduledAgent".
"""

import os
import time
from dotenv import load_dotenv
from openai.types.evals.create_eval_completions_run_data_source_param import SourceFileContent, SourceFileContentContent
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    TestingCriterionAzureAIEvaluator,
    EvaluationRule,
    DatasetEvaluationRuleAction,
    TargetCompletionEvalRunDataSource,
    AzureAIAgentTargetParam,
    EvaluationRuleEventType,
    RecurrenceTrigger,
    DailyRecurrenceSchedule,
    ScheduleProvisioningStatus,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME") or "MyScheduledAgent"

PENDING_STATUSES = (ScheduleProvisioningStatus.CREATING, ScheduleProvisioningStatus.UPDATING)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # Create the agent to evaluate

    agent = project_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model_deployment_name,
            instructions="You are a helpful assistant that answers general questions",
        ),
    )
    print(f"Agent created (name: {agent.name}, version: {agent.version})")

    # Create an eval that scores the agent's response to each query.
    # `sample.output_text` is the agent's text response.

    data_source_config = {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
        "include_sample_schema": True,
    }
    testing_criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="coherence",
            evaluator_name="builtin.coherence",
            initialization_parameters={"deployment_name": model_deployment_name},
            data_mapping={"query": "{{item.query}}", "response": "{{sample.output_text}}"},
        ),
    ]
    eval_object = openai_client.evals.create(
        name="Scheduled Agent Evaluation",
        data_source_config=data_source_config,  # type: ignore
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    # Create a rule that sends the queries to the agent and scores its responses every day at 9 AM UTC

    agent_queries = TargetCompletionEvalRunDataSource(
        type="azure_ai_target_completions",
        source=SourceFileContent(
            type="file_content",
            content=[
                SourceFileContentContent(item={"query": "What is the capital of France?"}),
                SourceFileContentContent(item={"query": "How many legs does a spider have?"}),
            ],
        ),
        input_messages={
            "type": "template",  # type: ignore
            "template": [
                {"type": "message", "role": "user", "content": {"type": "input_text", "text": "{{item.query}}"}}
            ],
        },
        target=AzureAIAgentTargetParam(type="azure_ai_agent", name=agent.name, version=agent.version),
    )

    dataset_eval_rule = project_client.evaluation_rules.create_or_update(
        id="my-dataset-eval-rule",
        evaluation_rule=EvaluationRule(
            display_name="My Agent Dataset Eval Rule",
            description="An eval rule that evaluates an agent on a fixed set of queries every day",
            action=DatasetEvaluationRuleAction(eval_id=eval_object.id, source=agent_queries),
            event_type=EvaluationRuleEventType.TIMER_TRIGGER,
            schedule=RecurrenceTrigger(interval=1, schedule=DailyRecurrenceSchedule(hours=[9]), time_zone="UTC"),
            enabled=True,
        ),
    )
    print(f"Dataset Evaluation Rule created (id: {dataset_eval_rule.id}, name: {dataset_eval_rule.display_name})")

    # The schedule is provisioned in the background. Wait for it before updating or deleting the rule.

    while dataset_eval_rule.provisioning_status in PENDING_STATUSES:
        time.sleep(5)
        dataset_eval_rule = project_client.evaluation_rules.get(id=dataset_eval_rule.id)
    print(f"Schedule provisioning status: {dataset_eval_rule.provisioning_status}")

    # Disable the rule, without deleting it

    dataset_eval_rule.enabled = False
    dataset_eval_rule = project_client.evaluation_rules.create_or_update(
        id=dataset_eval_rule.id, evaluation_rule=dataset_eval_rule
    )
    while dataset_eval_rule.provisioning_status in PENDING_STATUSES:
        time.sleep(5)
        dataset_eval_rule = project_client.evaluation_rules.get(id=dataset_eval_rule.id)
    print(f"Rule updated (id: {dataset_eval_rule.id}, enabled: {dataset_eval_rule.enabled})")

    # Clean up

    project_client.evaluation_rules.delete(id=dataset_eval_rule.id)
    print("Dataset Evaluation Rule deleted")

    openai_client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")

    project_client.agents.delete(agent_name=agent.name)
    print("Agent deleted")
