# pylint: disable=line-too-long,useless-suppression,wrong-import-order,ungrouped-imports,no-else-raise,raise-missing-from
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to assign RBAC permissions,
    create a scheduled agent trace evaluation using `project_client.beta.schedules`,
    list the schedule runs, and delete the schedule when finished.

USAGE:
    python sample_scheduled_agent_traces_evaluation_smart_filter.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv azure-mgmt-authorization azure-mgmt-resource

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) AZURE_SUBSCRIPTION_ID - Required for RBAC assignment. The Azure subscription ID where the project is located.
    3) AZURE_RESOURCE_GROUP_NAME - Required for RBAC assignment. The resource group name where the project is located.
    4) DATASET_NAME - Optional. The name of the Dataset to create and use in this sample.
    5) DATASET_VERSION - Optional. The version of the Dataset to create and use in this sample.
    6) DATA_FOLDER - Optional. The folder path where the data files for upload are located.
    7) FOUNDRY_AGENT_NAME - Required. The name of the Agent to perform red teaming evaluation on.
"""

import argparse
import os

from dotenv import load_dotenv
from pprint import pprint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.resource import ResourceManagementClient
import uuid
from azure.ai.projects.models import (
    TestingCriterionAzureAIEvaluator,
    Schedule,
    RecurrenceTrigger,
    DailyRecurrenceSchedule,
    EvaluationScheduleTask
)
import time


def main() -> None:
    print("Check and assign RBAC permissions...")
    assign_rbac()
    print("Scheduling Dataset based Evaluation...")
    schedule_trace_evaluation()


def assign_rbac():  # pylint: disable=too-many-statements
    """
    Assign the "Foundry User" role to the Microsoft Foundry project's Managed Identity.
    """
    load_dotenv()

    endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "")
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
    resource_group_name = os.environ.get("AZURE_RESOURCE_GROUP_NAME", "")

    if not endpoint or not subscription_id or not resource_group_name:
        print(
            "Error: FOUNDRY_PROJECT_ENDPOINT, AZURE_SUBSCRIPTION_ID, and AZURE_RESOURCE_GROUP_NAME environment variables are required"
        )
        return

    # Parse project information from the endpoint
    # Format: https://<account_name>.services.ai.azure.com/api/projects/<project_name>
    try:
        import re

        pattern = r"https://(.+)\.services\.ai\.azure\.com/api/projects/(.+)"
        match = re.match(pattern, endpoint)
        if not match:
            print("Error: Invalid project endpoint format")
            return
        account_name = match.group(1)
        project_name = match.group(2)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error parsing endpoint: {e}")
        return

    with DefaultAzureCredential() as credential:
        # Initialize clients
        auth_client = AuthorizationManagementClient(credential, subscription_id)
        resource_client = ResourceManagementClient(credential, subscription_id)

        try:
            # Get the Microsoft Foundry project resource
            # Based on resource ID pattern: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/projects/{project}

            # Try to find the resource group and project
            print(
                f"Searching for project: {project_name} under account: {account_name} in resource group: {resource_group_name}"
            )

            # Get the project's managed identity principal ID
            try:
                # Get the AI project resource
                project_resource = resource_client.resources.get(
                    resource_group_name=resource_group_name,
                    resource_provider_namespace="Microsoft.CognitiveServices",
                    parent_resource_path=f"accounts/{account_name}",
                    resource_type="projects",
                    resource_name=project_name,
                    api_version="2025-06-01",
                )

                # Extract the managed identity principal ID
                if project_resource.identity and project_resource.identity.principal_id:
                    principal_id = project_resource.identity.principal_id
                    print(f"Found project managed identity principal ID: {principal_id}")
                else:
                    print("Error: Project does not have a managed identity enabled")
                    return

            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Error retrieving project resource: {e}")
                return

            # Define the Foundry User role definition ID
            # This is the built-in role ID for "Foundry User"
            foundry_user_role_id = "53ca6127-db72-4b80-b1b0-d745d6d5456d"

            # Create the scope (project level)
            scope = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.CognitiveServices/accounts/{account_name}/projects/{project_name}"

            # Create role assignment
            role_assignment_name = str(uuid.uuid4())

            print("Assigning 'Foundry User' role to managed identity...")

            role_assignment = auth_client.role_assignments.create(
                scope=scope,
                role_assignment_name=role_assignment_name,
                parameters={
                    "role_definition_id": f"{scope}/providers/Microsoft.Authorization/roleDefinitions/{foundry_user_role_id}",
                    "principal_id": principal_id,
                    "principal_type": "ServicePrincipal",
                },
            )

            print("Successfully assigned 'Foundry User' role to project managed identity")
            print(f"Role assignment ID: {role_assignment.name}")

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error during role assignment: {e}")

            # Check for specific error types and provide helpful guidance
            error_message = str(e)
            if "AuthorizationFailed" in error_message:
                print("\n🔒 AUTHORIZATION ERROR:")
                print("You don't have sufficient permissions to assign roles at this scope.")
                print("\n📋 REQUIRED PERMISSIONS:")
                print("To assign roles, you need one of the following roles:")
                print("  • Owner - Full access including role assignments")
                print("  • User Access Administrator - Can manage user access to Azure resources")
                print("  • Custom role with 'Microsoft.Authorization/roleAssignments/write' permission")
                print("\n🎯 SCOPE:")
                project_scope = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.CognitiveServices/accounts/{account_name}/projects/{project_name}"
                print(f"  Resource: {project_scope}")
                print("\n💡 SOLUTIONS:")
                print("1. Ask your Azure administrator to grant you 'Owner' or 'User Access Administrator' role")
                print("2. Ask your admin to assign the 'Foundry User' role to the project's managed identity")
                print("3. Run this script with an account that has the required permissions")
                print("4. If you recently got permissions, try refreshing your credentials:")
                print("   - Run 'az logout && az login' in Azure CLI")
                print("   - Or restart this application")
                raise

            elif "RoleAssignmentExists" in error_message:
                print("\n✅ ROLE ASSIGNMENT ALREADY EXISTS:")
                print("The 'Foundry User' role is already assigned to the project's managed identity.")
                print("No action needed - the required permissions are already in place.")

            elif "InvalidResourceTypeNameFormat" in error_message:
                print("\n🔧 RESOURCE FORMAT ERROR:")
                print("The resource path format is incorrect. Please check:")
                print("  • Resource group name is correct")
                print("  • Project endpoint format matches expected pattern")
                print("  • Account and project names are properly extracted")
                raise ValueError("Invalid resource type name format")

            elif "NoRegisteredProviderFound" in error_message:
                print("\n🌐 API VERSION ERROR:")
                print("The API version or resource type is not supported in this region.")
                print("This usually indicates a service availability issue.")

            else:
                print("\n❌ UNEXPECTED ERROR:")
                print("An unexpected error occurred. Please check the error details above.")
                raise

def schedule_trace_evaluation():
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]
    agent_name = os.environ["FOUNDRY_AGENT_NAME"]
    agent_version = os.environ.get("FOUNDRY_AGENT_VERSION", "")

    parser = argparse.ArgumentParser(description="Evaluate agent traces using agent filter.")
    parser.add_argument("--agent-id", default=None, help='Agent ID in "name:version" format')
    parser.add_argument("--max-traces", type=int, default=5, help="Max traces to evaluate (default: 5)")
    parser.add_argument("--lookback-hours", type=int, default=24, help="Hours to look back (default: 24)")
    args = parser.parse_args()

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):
        # Eval group for trace-based evaluations
        data_source_config = {
            "type": "azure_ai_source",
            "scenario": "traces",
        }

        testing_criteria = [
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="task_completion",
                evaluator_name="builtin.task_completion",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                },
            ),
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="conversation_coherence",
                evaluator_name="builtin.coherence",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                },
            ),
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="groundedness",
                evaluator_name="builtin.groundedness",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                },
            ),
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="violence",
                evaluator_name="builtin.violence",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                },
            ),
        ]

        print("Creating trace-based evaluation group")
        eval_object = client.evals.create(
            name="Trace Evaluation (Agent Smart Filter)",
            data_source_config=data_source_config,  # type: ignore
            testing_criteria=testing_criteria,
        )
        print(f"Evaluation created (id: {eval_object.id})")

        # Compute time window in unix seconds
        # Pad end_time by +600s (10 min) to avoid ingestion-delay edge exclusion
        now_unix = int(time.time())
        end_time = now_unix + 600
        start_time = now_unix - (args.lookback_hours * 3600)

        # Build trace_source based on mode
        trace_source: dict = {
            "type": "agent_filter",
            "start_time": start_time,
            "end_time": end_time,
            "max_traces": args.max_traces,
            "filter_strategy": "smart_filtering"
        }

        if args.agent_id:
            trace_source["agent_id"] = args.agent_id
            print(f"Using agent_id filter: {args.agent_id}")
        else:
            trace_source["agent_name"] = agent_name
            if agent_version:
                trace_source["agent_version"] = agent_version
            print(f"Using agent filter: {agent_name} v{agent_version or '(latest)'}")

        data_source = {
            "type": "azure_ai_trace_data_source_preview",
            "trace_source": trace_source,
        }

        eval_run_object = {
            "eval_id": eval_object.id,
            "name": "trace_eval_with_smart_filter",
            "data_source": data_source
        }

        print("Eval Run:")
        pprint(eval_run_object)
        print("Creating Schedule for agent trace evaluation")
        schedule = Schedule(
            display_name="Agent Trace Evaluation Eval Run Schedule",
            enabled=True,
            trigger=RecurrenceTrigger(interval=1, schedule=DailyRecurrenceSchedule(hours=[9])),  # Every day at 9 AM
            task=EvaluationScheduleTask(eval_id=eval_object.id, eval_run=eval_run_object),
        )
        schedule_response = project_client.beta.schedules.create_or_update(
            schedule_id="agent-trace-eval-run-schedule-9am", schedule=schedule
        )

        print(f"Schedule created for agent trace evaluation: {schedule_response.schedule_id}")
        pprint(schedule_response)

        time.sleep(5)  # Wait for schedule to be fully created
        schedule_runs = project_client.beta.schedules.list_runs(schedule_response.schedule_id)
        print(f"Listing schedule runs for schedule id: {schedule_response.schedule_id}")
        for run in schedule_runs:
            pprint(run)

        project_client.beta.schedules.delete(schedule_response.schedule_id)
        print("Agent trace evaluation schedule deleted")

        client.evals.delete(eval_id=eval_object.id)
        print("Evaluation deleted")

if __name__ == "__main__":
    main()
