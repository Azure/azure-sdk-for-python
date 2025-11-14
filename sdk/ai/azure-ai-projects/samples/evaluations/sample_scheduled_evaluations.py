# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list eval group and and eval runs.

USAGE:
    python sample_scheduled_evaluations.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv azure-mgmt-authorization azure-mgmt-resource

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) AZURE_SUBSCRIPTION_ID - Required for RBAC assignment. The Azure subscription ID where the project is located.
    3) AZURE_RESOURCE_GROUP_NAME - Required for RBAC assignment. The resource group name where the project is located.
    4) DATASET_NAME - Optional. The name of the Dataset to create and use in this sample.
    5) DATASET_VERSION - Optional. The version of the Dataset to create and use in this sample.
    6) DATA_FOLDER - Optional. The folder path where the data files for upload are located.
    7) AZURE_AI_AGENT_NAME - Required. The name of the Agent to perform red teaming evaluation on.
"""

from datetime import datetime
import os

from dotenv import load_dotenv
from pprint import pprint
from azure.ai.projects.models._models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.resource import ResourceManagementClient
import uuid
from azure.ai.projects.models import (
    AgentVersionObject,
    EvaluationTaxonomy,
    AzureAIAgentTarget,
    AgentTaxonomyInput,
    Schedule,
    RecurrenceTrigger,
    DailyRecurrenceSchedule,
    EvaluationScheduleTask,
    RiskCategory,
)
from openai.types.evals.create_eval_jsonl_run_data_source_param import CreateEvalJSONLRunDataSourceParam, SourceFileID
from azure.ai.projects.models import (
    DatasetVersion,
)
import json
import time
from azure.ai.projects.models import EvaluationTaxonomy


def main() -> None:
    print("Assigning RBAC permissions...")
    assign_rbac()
    print("Scheduling Dataset based Evaluation...")
    schedule_dataset_evaluation()
    print("Scheduling RedTeam based Evaluation...")
    schedule_redteam_evaluation()


def assign_rbac():
    """
    Assign the "Azure AI User" role to the Microsoft Foundry project's Managed Identity.
    """
    load_dotenv()

    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
    resource_group_name = os.environ.get("AZURE_RESOURCE_GROUP_NAME", "")

    if not endpoint or not subscription_id or not resource_group_name:
        print(
            "Error: AZURE_AI_PROJECT_ENDPOINT, AZURE_SUBSCRIPTION_ID, and AZURE_RESOURCE_GROUP_NAME environment variables are required"
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
    except Exception as e:
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

            except Exception as e:
                print(f"Error retrieving project resource: {e}")
                return

            # Define the Azure AI User role definition ID
            # This is the built-in role ID for "Azure AI User"
            azure_ai_user_role_id = "64702f94-c441-49e6-a78b-ef80e0188fee"

            # Create the scope (project level)
            scope = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.CognitiveServices/accounts/{account_name}/projects/{project_name}"

            # Create role assignment
            role_assignment_name = str(uuid.uuid4())

            print(f"Assigning 'Azure AI User' role to managed identity...")

            role_assignment = auth_client.role_assignments.create(
                scope=scope,
                role_assignment_name=role_assignment_name,
                parameters={
                    "role_definition_id": f"{scope}/providers/Microsoft.Authorization/roleDefinitions/{azure_ai_user_role_id}",
                    "principal_id": principal_id,
                    "principal_type": "ServicePrincipal",
                },
            )

            print(f"Successfully assigned 'Azure AI User' role to project managed identity")
            print(f"Role assignment ID: {role_assignment.name}")

        except Exception as e:
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
                print("2. Ask your admin to assign the 'Azure AI User' role to the project's managed identity")
                print("3. Run this script with an account that has the required permissions")
                print("4. If you recently got permissions, try refreshing your credentials:")
                print("   - Run 'az logout && az login' in Azure CLI")
                print("   - Or restart this application")
                raise

            elif "RoleAssignmentExists" in error_message:
                print("\n✅ ROLE ASSIGNMENT ALREADY EXISTS:")
                print("The 'Azure AI User' role is already assigned to the project's managed identity.")
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
                print(f"\n❌ UNEXPECTED ERROR:")
                print("An unexpected error occurred. Please check the error details above.")
                raise


def schedule_dataset_evaluation() -> None:
    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    dataset_name = os.environ.get("DATASET_NAME", "")
    dataset_version = os.environ.get("DATASET_VERSION", "1")
    # Construct the paths to the data folder and data file used in this sample
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "data_folder"))
    data_file = os.path.join(data_folder, "sample_data_evaluation.jsonl")
    with DefaultAzureCredential() as credential:
        with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

            print("Upload a single file and create a new Dataset to reference the file.")
            dataset: DatasetVersion = project_client.datasets.upload_file(
                name=dataset_name or f"eval-data-{datetime.utcnow().strftime('%Y-%m-%d_%H%M%S_UTC')}",
                version=dataset_version,
                file_path=data_file,
            )
            pprint(dataset)

            print("Creating an OpenAI client from the AI Project client")

            client = project_client.get_openai_client()

            data_source_config = {
                "type": "custom",
                "item_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "response": {"type": "string"},
                        "context": {"type": "string"},
                        "ground_truth": {"type": "string"},
                    },
                    "required": [],
                },
                "include_sample_schema": True,
            }

            testing_criteria = [
                {
                    "type": "azure_ai_evaluator",
                    "name": "violence",
                    "evaluator_name": "builtin.violence",
                    "data_mapping": {"query": "{{item.query}}", "response": "{{item.response}}"},
                    "initialization_parameters": {"deployment_name": "{{aoai_deployment_and_model}}"},
                },
                {"type": "azure_ai_evaluator", "name": "f1", "evaluator_name": "builtin.f1_score"},
                {
                    "type": "azure_ai_evaluator",
                    "name": "coherence",
                    "evaluator_name": "builtin.coherence",
                    "initialization_parameters": {"deployment_name": "{{aoai_deployment_and_model}}"},
                },
            ]

            print("Creating evaluation")
            eval_object = client.evals.create(
                name="label model test with dataset ID",
                data_source_config=data_source_config,  # type: ignore
                testing_criteria=testing_criteria,  # type: ignore
            )
            print(f"Evaluation created")

            print("Get Evaluation by Id")
            eval_object_response = client.evals.retrieve(eval_object.id)
            print("Eval Run Response:")
            pprint(eval_object_response)

            print("Creating Eval Run with Dataset ID")
            eval_run_object = {
                "eval_id": eval_object.id,
                "name": "dataset_id_run",
                "metadata": {"team": "eval-exp", "scenario": "dataset-id-v1"},
                "data_source": CreateEvalJSONLRunDataSourceParam(
                    type="jsonl", source=SourceFileID(type="file_id", id=dataset.id if dataset.id else "")
                ),
            }

            print(f"Eval Run:")
            pprint(eval_run_object)
            print("Creating Schedule for dataset evaluation")
            schedule = Schedule(
                display_name="Dataset Evaluation Eval Run Schedule",
                enabled=True,
                trigger=RecurrenceTrigger(interval=1, schedule=DailyRecurrenceSchedule(hours=[9])),  # Every day at 9 AM
                task=EvaluationScheduleTask(eval_id=eval_object.id, eval_run=eval_run_object),
            )
            schedule_response = project_client.schedules.create_or_update(
                id="dataset-eval-run-schedule-9am", schedule=schedule
            )

            print(f"Schedule created for dataset evaluation: {schedule_response.id}")
            pprint(schedule_response)

            schedule_runs = project_client.schedules.list_runs(schedule_response.id)
            print(f"Listing schedule runs for schedule id: {schedule_response.id}")
            for run in schedule_runs:
                pprint(run)

            project_client.schedules.delete(schedule_response.id)
            print("Schedule deleted")

            client.evals.delete(eval_id=eval_object.id)
            print("Evaluation deleted")

            project_client.datasets.delete(name=dataset.name, version=dataset.version)
            print("Dataset deleted")


def schedule_redteam_evaluation() -> None:
    load_dotenv()
    #
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
    agent_name = os.environ.get("AGENT_NAME", "")

    # Construct the paths to the data folder and data file used in this sample
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "data_folder"))

    with DefaultAzureCredential() as credential:
        with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:
            print("Creating an OpenAI client from the AI Project client")
            client = project_client.get_openai_client()

            agent_version = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                    instructions="You are a helpful assistant that answers general questions",
                ),
            )
            print(
                f"Agent created (id: {agent_version.id}, name: {agent_version.name}, version: {agent_version.version})"
            )

            eval_group_name = "Red Team Agent Safety Eval Group -" + str(int(time.time()))
            eval_run_name = f"Red Team Agent Safety Eval Run for {agent_name} -" + str(int(time.time()))
            data_source_config = {"type": "azure_ai_source", "scenario": "red_team"}

            testing_criteria = _get_agent_safety_evaluation_criteria()
            print(f"Defining testing criteria for red teaming for agent target")
            pprint(testing_criteria)

            print("Creating Eval Group")
            eval_object = client.evals.create(
                name=eval_group_name,
                data_source_config=data_source_config,  # type: ignore
                testing_criteria=testing_criteria,  # type: ignore # type: ignore
            )
            print(f"Eval Group created for red teaming: {eval_group_name}")

            print(f"Get Eval Group by Id: {eval_object.id}")
            eval_object_response = client.evals.retrieve(eval_object.id)
            print("Eval Group Response:")
            pprint(eval_object_response)

            risk_categories_for_taxonomy = [RiskCategory.PROHIBITED_ACTIONS]
            target = AzureAIAgentTarget(
                name=agent_name, version=agent_version.version, tool_descriptions=_get_tool_descriptions(agent_version)
            )
            agent_taxonomy_input = AgentTaxonomyInput(risk_categories=risk_categories_for_taxonomy, target=target)  # type: ignore
            print("Creating Eval Taxonomies")
            eval_taxonomy_input = EvaluationTaxonomy(
                description="Taxonomy for red teaming evaluation", taxonomy_input=agent_taxonomy_input
            )

            taxonomy = project_client.evaluation_taxonomies.create(name=agent_name, body=eval_taxonomy_input)
            taxonomy_path = os.path.join(data_folder, f"taxonomy_{agent_name}.json")
            # Create the data folder if it doesn't exist
            os.makedirs(data_folder, exist_ok=True)
            with open(taxonomy_path, "w") as f:
                f.write(json.dumps(_to_json_primitive(taxonomy), indent=2))
            print(f"RedTeaming Taxonomy created for agent: {agent_name}. Taxonomy written to {taxonomy_path}")
            eval_run_object = {
                "eval_id": eval_object.id,
                "name": eval_run_name,
                "data_source": {
                    "type": "azure_ai_red_team",
                    "item_generation_params": {
                        "type": "red_team_taxonomy",
                        "attack_strategies": ["Flip", "Base64"],
                        "num_turns": 5,
                        "source": {"type": "file_id", "id": taxonomy.id},
                    },
                    "target": target.as_dict(),
                },
            }

            print("Creating Schedule for RedTeaming Eval Run")
            schedule = Schedule(
                display_name="RedTeam Eval Run Schedule",
                enabled=True,
                trigger=RecurrenceTrigger(interval=1, schedule=DailyRecurrenceSchedule(hours=[9])),  # Every day at 9 AM
                task=EvaluationScheduleTask(eval_id=eval_object.id, eval_run=eval_run_object),
            )
            schedule_response = project_client.schedules.create_or_update(
                id="redteam-eval-run-schedule-9am", schedule=schedule
            )

            print(f"Schedule created for red teaming: {schedule_response.id}")
            pprint(schedule_response)

            schedule_runs = project_client.schedules.list_runs(schedule_response.id)
            print(f"Listing schedule runs for schedule id: {schedule_response.id}")
            for run in schedule_runs:
                pprint(run)

            project_client.schedules.delete(schedule_response.id)
            print("Schedule deleted")

            client.evals.delete(eval_id=eval_object.id)
            print("Evaluation deleted")

            project_client.evaluation_taxonomies.delete(name=taxonomy.name, version=taxonomy.version)
            print("Taxonomy deleted")


def _get_tool_descriptions(agent: AgentVersionObject):
    tools = agent.definition.get("tools", [])
    tool_descriptions = []
    for tool in tools:
        if tool["type"] == "openapi":
            tool_descriptions.append(
                {
                    "name": tool["openapi"]["name"],
                    "description": (
                        tool["openapi"]["description"]
                        if "description" in tool["openapi"]
                        else "No description provided"
                    ),
                }
            )
        else:
            tool_descriptions.append(
                {
                    "name": tool["name"] if "name" in tool else "Unnamed Tool",
                    "description": tool["description"] if "description" in tool else "No description provided",
                }
            )
    if len(tool_descriptions) == 0:
        tool_descriptions.append({"name": "No Tools", "description": "This agent does not use any tools."})

    return tool_descriptions


def _get_agent_safety_evaluation_criteria():
    return [
        {
            "type": "azure_ai_evaluator",
            "name": "Prohibited Actions",
            "evaluator_name": "builtin.prohibited_actions",
            "evaluator_version": "1",
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Task Adherence",
            "evaluator_name": "builtin.task_adherence",
            "evaluator_version": "1",
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Sensitive Data Leakage",
            "evaluator_name": "builtin.sensitive_data_leakage",
            "evaluator_version": "1",
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Self Harm",
            "evaluator_name": "builtin.self_harm",
            "evaluator_version": "1",
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Violence",
            "evaluator_name": "builtin.violence",
            "evaluator_version": "1",
        },
        {"type": "azure_ai_evaluator", "name": "Sexual", "evaluator_name": "builtin.sexual", "evaluator_version": "1"},
        {
            "type": "azure_ai_evaluator",
            "name": "Hate Unfairness",
            "evaluator_name": "builtin.hate_unfairness",
            "evaluator_version": "1",
        },
    ]


def _to_json_primitive(obj):
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_to_json_primitive(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _to_json_primitive(v) for k, v in obj.items()}
    for method in ("to_dict", "as_dict", "dict", "serialize"):
        if hasattr(obj, method):
            try:
                return _to_json_primitive(getattr(obj, method)())
            except Exception:
                pass
    if hasattr(obj, "__dict__"):
        return _to_json_primitive({k: v for k, v in vars(obj).items() if not k.startswith("_")})
    return str(obj)


if __name__ == "__main__":
    main()
