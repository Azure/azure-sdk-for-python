# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list evaluation and and eval runs.

USAGE:
    python sample_redteam_evaluations.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) DATA_FOLDER - Optional. The folder path where the data files for upload are located.
    3) AZURE_AI_AGENT_NAME - Required. The name of the Agent to perform red teaming evaluation on.
"""

import os

from dotenv import load_dotenv
from pprint import pprint
from azure.ai.projects.models._models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentVersionDetails,
    EvaluationTaxonomy,
    AzureAIAgentTarget,
    AgentTaxonomyInput,
    RiskCategory,
)
import json
import time
from azure.ai.projects.models import EvaluationTaxonomy
from typing import Union


def main() -> None:
    load_dotenv()
    #
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
    agent_name = os.environ.get("AZURE_AI_AGENT_NAME", "")

    # Construct the paths to the data folder and data file used in this sample
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "data_folder"))

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):
        agent_version = project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                instructions="You are a helpful assistant that answers general questions",
            ),
        )
        print(f"Agent created (id: {agent_version.id}, name: {agent_version.name}, version: {agent_version.version})")

        eval_group_name = "Red Team Agent Safety Evaluation -" + str(int(time.time()))
        eval_run_name = f"Red Team Agent Safety Eval Run for {agent_name} -" + str(int(time.time()))
        data_source_config = {"type": "azure_ai_source", "scenario": "red_team"}

        testing_criteria = _get_agent_safety_evaluation_criteria()
        print(f"Defining testing criteria for red teaming for agent target")
        pprint(testing_criteria)

        print("Creating red teaming evaluation")
        eval_object = client.evals.create(
            name=eval_group_name,
            data_source_config=data_source_config,  # type: ignore
            testing_criteria=testing_criteria,  # type: ignore
        )
        print(f"Evaluation created for red teaming: {eval_group_name}")

        print(f"Get evaluation by Id: {eval_object.id}")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Evaluation Response:")
        pprint(eval_object_response)

        risk_categories_for_taxonomy: list[Union[str, RiskCategory]] = [RiskCategory.PROHIBITED_ACTIONS]
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
        print(f"Red teaming Taxonomy created for agent: {agent_name}. Taxonomy written to {taxonomy_path}")

        print("Creating red teaming Eval Run")
        eval_run_object = client.evals.runs.create(
            eval_id=eval_object.id,
            name=eval_run_name,
            data_source={  # type: ignore
                "type": "azure_ai_red_team",
                "item_generation_params": {
                    "type": "red_team_taxonomy",
                    "attack_strategies": ["Flip", "Base64"],
                    "num_turns": 5,
                    "source": {"type": "file_id", "id": taxonomy.id},
                },
                "target": target.as_dict(),
            },
        )

        print(f"Eval Run created for red teaming: {eval_run_name}")
        pprint(eval_run_object)

        print(f"Get Eval Run by Id: {eval_run_object.id}")
        eval_run_response = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
        print("Eval Run Response:")
        pprint(eval_run_response)

        while True:
            run = client.evals.runs.retrieve(run_id=eval_run_response.id, eval_id=eval_object.id)
            if run.status == "completed" or run.status == "failed":
                output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
                output_items_path = os.path.join(data_folder, f"redteam_eval_output_items_{agent_name}.json")
                # Create the data folder if it doesn't exist
                os.makedirs(data_folder, exist_ok=True)
                with open(output_items_path, "w") as f:
                    f.write(json.dumps(_to_json_primitive(output_items), indent=2))
                print(
                    f"RedTeam Eval Run completed with status: {run.status}. Output items written to {output_items_path}"
                )
                break
            time.sleep(5)
            print(f"Waiting for eval run to complete... {run.status}")

        client.evals.delete(eval_id=eval_object.id)
        print("Evaluation deleted")

        project_client.agents.delete(agent_name=agent_name)
        print("Agent deleted")


def _get_tool_descriptions(agent: AgentVersionDetails):
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
