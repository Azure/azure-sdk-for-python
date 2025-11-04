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
    python sample_redteam_evaluations_v2.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) MODEL_ENDPOINT - Required. The Azure OpenAI endpoint associated with your Foundry project.
       It can be found in the Foundry overview page. It has the form https://<account_name>.openai.azure.com.
    3) MODEL_API_KEY - Required. The API key for the model endpoint. Can be found under "key" in the model details page
       (click "Models + endpoints" and select your model to get to the model details page).
    4) MODEL_DEPLOYMENT_NAME - Required. The name of the model deployment to use for evaluation.
"""

from datetime import datetime
import os

from dotenv import load_dotenv
from pprint import pprint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentVersionObject,
    EvaluationTaxonomy,
    AzureAIAgentTarget,
    AgentTaxonomyInput,
    Schedule,
    RecurrenceTrigger,
    DailyRecurrenceSchedule,
    EvaluationScheduleTask,
    RiskCategory
)
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileID
)
from azure.ai.projects.models import (
    DatasetVersion,
)
import json
import time
from azure.ai.projects.models import EvaluationTaxonomy

def main() -> None:
    print("Scheduling Dataset based Evaluation...")
    schedule_dataset_evaluation()
    print("Scheduling RedTeam based Evaluation...")
    schedule_redteam_evaluation()

def schedule_dataset_evaluation() -> None:
    endpoint = os.environ[
        "AZURE_AI_PROJECT_ENDPOINT"
    ] # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
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
                file_path=data_file
            )
            pprint(dataset)
            
            print("Creating an OpenAI client from the AI Project client")
            
            client = project_client.get_openai_client()
            
            data_source_config = {
                "type": "custom",
                "item_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string"
                        },
                        "response": {
                            "type": "string"
                        },
                        "context": {
                            "type": "string"
                        },
                        "ground_truth": {
                            "type": "string"
                        }
                    },
                    "required": []
                },
                "include_sample_schema": True
            }
            
            testing_criteria = [
                {
                    "type": "azure_ai_evaluator",
                    "name": "violence",
                    "evaluator_name": "builtin.violence",
                    "data_mapping": {
                        "query": "{{item.query}}",
                        "response": "{{item.response}}"
                    },
                    "initialization_parameters": {
                        "deployment_name": "{{aoai_deployment_and_model}}"
                    }
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "f1",
                    "evaluator_name": "builtin.f1_score"
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "coherence",
                    "evaluator_name": "builtin.coherence",
                    "initialization_parameters": {
                        "deployment_name": "{{aoai_deployment_and_model}}"
                    }
                }
            ]
            
            print("Creating Eval Group")
            eval_object = client.evals.create(
                name="label model test with dataset ID",
                data_source_config=data_source_config,
                testing_criteria=testing_criteria,
            )
            print(f"Eval Group created")

            print("Get Eval Group by Id")
            eval_object_response = client.evals.retrieve(eval_object.id)
            print("Eval Run Response:")
            pprint(eval_object_response)

            print("Creating Eval Run with Dataset ID")
            eval_run_object = {
                "eval_id": eval_object.id,
                "name": "dataset_id_run",
                "metadata": {
                    "team": "eval-exp",
                    "scenario": "dataset-id-v1"
                },
                "data_source": CreateEvalJSONLRunDataSourceParam(
                    type="jsonl", 
                    source=SourceFileID(
                        type ="file_id",
                        id=dataset.id if dataset.id else ""
                    )
                )
            }
            
            print(f"Eval Run:")
            pprint(eval_run_object)
            print("Creating Schedule for dataset evaluation")
            schedule = Schedule(display_name="Dataset Evaluation Eval Run Schedule",
                                enabled=True,
                                trigger=RecurrenceTrigger(interval=1, schedule=DailyRecurrenceSchedule(hours=[9])), # Every day at 9 AM
                                task=EvaluationScheduleTask(eval_id=eval_object.id, eval_run=eval_run_object))
            schedule_response = project_client.schedules.create_or_update(id="dataset-eval-run-schedule-9am", schedule=schedule)

            print(f"Schedule created for dataset evaluation: {schedule_response.id}")
            pprint(schedule_response)

            schedule_runs = project_client.schedules.list_runs(schedule_id=schedule_response.id)
            print(f"Listing schedule runs for schedule id: {schedule_response.id}")
            for run in schedule_runs:
                pprint(run)

def schedule_redteam_evaluation() -> None:
    load_dotenv()
    # 
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
    agent_name = os.environ.get("AGENT_NAME", "")

    # Construct the paths to the data folder and data file used in this sample
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "data_folder"))

    with DefaultAzureCredential() as credential:
        with AIProjectClient(endpoint=endpoint, credential=credential, api_version="2025-11-15-preview") as project_client:
            print("Creating an OpenAI client from the AI Project client")
            client = project_client.get_openai_client()

            agent_versions = project_client.agents.retrieve(agent_name=agent_name)
            agent = agent_versions.versions.latest
            agent_version = agent.version
            print(f"Retrieved agent: {agent_name}, version: {agent_version}")
            eval_group_name = "Red Team Agent Safety Eval Group -" + str(int(time.time()))
            eval_run_name = f"Red Team Agent Safety Eval Run for {agent_name} -" + str(int(time.time()))
            data_source_config = {
                "type": "azure_ai_source",
                "scenario": "red_team"
            }
            
            testing_criteria = _get_agent_safety_evaluation_criteria()
            print(f"Defining testing criteria for red teaming for agent target")
            pprint(testing_criteria)

            print("Creating Eval Group")
            eval_object = client.evals.create(
                name=eval_group_name,
                data_source_config=data_source_config,
                testing_criteria=testing_criteria,
            )
            print(f"Eval Group created for red teaming: {eval_group_name}")

            print(f"Get Eval Group by Id: {eval_object.id}")
            eval_object_response = client.evals.retrieve(eval_object.id)
            print("Eval Group Response:")
            pprint(eval_object_response)

            risk_categories_for_taxonomy = [ RiskCategory.PROHIBITED_ACTIONS ]
            target=AzureAIAgentTarget(name=agent_name, version=agent_version, tool_descriptions=_get_tool_descriptions(agent))
            agent_taxonomy_input = AgentTaxonomyInput(risk_categories=risk_categories_for_taxonomy, target=target)
            print("Creating Eval Taxonomies")
            eval_taxonomy_input = EvaluationTaxonomy(
                description="Taxonomy for red teaming evaluation",
                taxonomy_input=agent_taxonomy_input)
            
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
                        "attack_strategies": [
                            "Flip",
                            "Base64"
                        ],
                        "num_turns": 5,
                        "source": {
                            "type": "file_id",
                            "id": taxonomy.id
                        }
                    },
                    "target": target.as_dict()
                }
            }

            print("Creating Schedule for RedTeaming Eval Run")
            schedule = Schedule(display_name="RedTeam Eval Run Schedule",
                                enabled=True,
                                trigger=RecurrenceTrigger(interval=1, schedule=DailyRecurrenceSchedule(hours=[9])), # Every day at 9 AM
                                task=EvaluationScheduleTask(eval_id=eval_object.id, eval_run=eval_run_object))
            schedule_response = project_client.schedules.create_or_update(id="redteam-eval-run-schedule-9am", schedule=schedule)

            print(f"Schedule created for red teaming: {schedule_response.id}")
            pprint(schedule_response)

            schedule_runs = project_client.schedules.list_runs(schedule_id=schedule_response.id)
            print(f"Listing schedule runs for schedule id: {schedule_response.id}")
            for run in schedule_runs:
                pprint(run)
            
            # [END evaluations_sample]

def _get_tool_descriptions(agent: AgentVersionObject):
    tools = agent.definition.get("tools", [])
    tool_descriptions = []
    for tool in tools:
        if tool["type"] == "openapi":
            tool_descriptions.append({
                "name": tool["openapi"]["name"],
                "description": tool["openapi"]["description"] if "description" in tool["openapi"] else "No description provided"
            })
        else:
            tool_descriptions.append({
                "name": tool["name"] if "name" in tool else "Unnamed Tool",
                "description": tool["description"] if "description" in tool else "No description provided"
            })
    if (len(tool_descriptions) == 0):
        tool_descriptions.append({
            "name": "No Tools",
            "description": "This agent does not use any tools."
        })

    return tool_descriptions

def _get_agent_safety_evaluation_criteria():
    return  [
                {
                    "type": "azure_ai_evaluator",
                    "name": "Prohibited Actions",
                    "evaluator_name": "builtin.prohibited_actions",
                    "evaluator_version": "1"
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "Task Adherence",
                    "evaluator_name": "builtin.task_adherence",
                    "evaluator_version": "1"
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "Sensitive Data Leakage",
                    "evaluator_name": "builtin.sensitive_data_leakage",
                    "evaluator_version": "1"
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "Self Harm",
                    "evaluator_name": "builtin.self_harm",
                    "evaluator_version": "1"
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "Violence",
                    "evaluator_name": "builtin.violence",
                    "evaluator_version": "1"
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "Sexual",
                    "evaluator_name": "builtin.sexual",
                    "evaluator_version": "1"
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "Hate Unfairness",
                    "evaluator_name": "builtin.hate_unfairness",
                    "evaluator_version": "1"
                }
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