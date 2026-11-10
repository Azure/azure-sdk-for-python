# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an evaluation rule that evaluates
    a dataset on a recurring schedule, using the synchronous AIProjectClient.

    The rule uses a `DatasetEvaluationRuleAction` with the `timerTrigger` event type.
    On each scheduled occurrence, the service adds an evaluation run over the given
    dataset to the eval. This sample uses inline JSONL content; a file ID, a CSV file,
    or a source that generates responses from a model or agent target also work.

    The OpenAI compatible Evals calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

PREREQUISITE:
    Assign the project managed identity the "Azure AI User" role:
    1) Open https://portal.azure.com
    2) Search for the AI Foundry project from search bar
    3) Choose "Access control (IAM)" -> "Add"
    4) In "Add role assignment", search for "Azure AI User"
    5) Choose "User, group, or service principal" or "Managed Identity", add your AI Foundry project managed identity

USAGE:
    python sample_dataset_evaluation_rule.py

    Before running the sample:

    pip install "azure-ai-projects>=2.11.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model used by the evaluators, as found under
       the "Name" column in the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    TestingCriterionAzureAIEvaluator,
    EvaluationRule,
    DatasetEvaluationRuleAction,
    CreateEvalJsonlRunDataSource,
    EvalJsonlFileContentSource,
    EvalJsonlFileContentSourceContent,
    EvaluationRuleEventType,
    RecurrenceTrigger,
    DailyRecurrenceSchedule,
    ScheduleProvisioningStatus,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]

PENDING_STATUSES = (ScheduleProvisioningStatus.CREATING, ScheduleProvisioningStatus.UPDATING)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # Create an eval for query/response pairs

    data_source_config = {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "response": {"type": "string"}},
            "required": ["query", "response"],
        },
        "include_sample_schema": False,
    }
    testing_criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="coherence",
            evaluator_name="builtin.coherence",
            initialization_parameters={"deployment_name": model_deployment_name},
            data_mapping={"query": "{{item.query}}", "response": "{{item.response}}"},
        ),
    ]
    eval_object = openai_client.evals.create(
        name="Scheduled Dataset Evaluation",
        data_source_config=data_source_config,  # type: ignore
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    # Create a rule that evaluates the dataset every day at 9 AM UTC

    dataset = CreateEvalJsonlRunDataSource(
        source=EvalJsonlFileContentSource(
            content=[
                EvalJsonlFileContentSourceContent(
                    item={"query": "What is the capital of France?", "response": "Paris is the capital of France."}
                ),
                EvalJsonlFileContentSourceContent(
                    item={"query": "How many legs does a spider have?", "response": "A spider has eight legs."}
                ),
            ]
        )
    )

    dataset_eval_rule = project_client.evaluation_rules.create_or_update(
        id="my-dataset-eval-rule",
        evaluation_rule=EvaluationRule(
            display_name="My Dataset Eval Rule",
            description="An eval rule that evaluates a dataset every day",
            action=DatasetEvaluationRuleAction(eval_id=eval_object.id, source=dataset),
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
