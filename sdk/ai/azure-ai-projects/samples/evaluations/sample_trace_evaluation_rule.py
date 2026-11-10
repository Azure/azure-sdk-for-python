# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an evaluation rule that evaluates
    an agent's traces on a recurring schedule, using the synchronous AIProjectClient.

    The rule uses a `TraceEvaluationRuleAction` with the `timerTrigger` event type.
    On each scheduled occurrence, the service reads the agent's recent traces from
    Application Insights and adds an evaluation run to the given eval.

    The OpenAI compatible Evals calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

PREREQUISITE:
    1) The Foundry project must have an Application Insights resource connected, and the agent
       must have produced traces.
    2) Assign the project managed identity the "Azure AI User" role:
       a) Open https://portal.azure.com
       b) Search for the AI Foundry project from search bar
       c) Choose "Access control (IAM)" -> "Add"
       d) In "Add role assignment", search for "Azure AI User"
       e) Choose "User, group, or service principal" or "Managed Identity", add your AI Foundry project managed identity

USAGE:
    python sample_trace_evaluation_rule.py

    Before running the sample:

    pip install "azure-ai-projects>=2.11.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model used by the evaluators, as found under
       the "Name" column in the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - The name of an existing agent whose traces should be evaluated.
"""

import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureAIDataSourceConfig,
    TestingCriterionAzureAIEvaluator,
    EvaluationRule,
    TraceEvaluationRuleAction,
    TracesEvalRunDataSource,
    EvaluationRuleEventType,
    RecurrenceTrigger,
    HourlyRecurrenceSchedule,
    ScheduleProvisioningStatus,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ["FOUNDRY_AGENT_NAME"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # Create an eval that scores agent traces

    data_source_config = AzureAIDataSourceConfig(type="azure_ai_source", scenario="traces")
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
        name="Scheduled Trace Evaluation",
        data_source_config=data_source_config,  # type: ignore
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    # Create a rule that evaluates up to 10 of the agent's traces every hour.
    # The trace lookback window is inferred from the recurrence interval.

    trace_eval_rule = project_client.evaluation_rules.create_or_update(
        id="my-trace-eval-rule",
        evaluation_rule=EvaluationRule(
            display_name="My Trace Eval Rule",
            description="An eval rule that evaluates agent traces every hour",
            action=TraceEvaluationRuleAction(
                eval_id=eval_object.id,
                source=TracesEvalRunDataSource(agent_name=agent_name, max_traces=10),
            ),
            event_type=EvaluationRuleEventType.TIMER_TRIGGER,
            schedule=RecurrenceTrigger(interval=1, schedule=HourlyRecurrenceSchedule()),
            enabled=True,
        ),
    )
    print(f"Trace Evaluation Rule created (id: {trace_eval_rule.id}, name: {trace_eval_rule.display_name})")

    # The schedule is provisioned in the background. Wait for it before updating or deleting the rule.

    while trace_eval_rule.provisioning_status in (
        ScheduleProvisioningStatus.CREATING,
        ScheduleProvisioningStatus.UPDATING,
    ):
        time.sleep(5)
        trace_eval_rule = project_client.evaluation_rules.get(id=trace_eval_rule.id)
    print(f"Schedule provisioning status: {trace_eval_rule.provisioning_status}")

    # Clean up

    project_client.evaluation_rules.delete(id=trace_eval_rule.id)
    print("Trace Evaluation Rule deleted")

    openai_client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")
