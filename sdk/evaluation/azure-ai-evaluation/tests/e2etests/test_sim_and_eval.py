import asyncio
import json
import os
import pathlib
import time
from typing import Any, Dict, List, Optional
from azure.ai.evaluation._common.math import list_mean_nan_safe

import pandas as pd
import pytest
import requests
from ci_tools.variables import in_ci
from devtools_testutils import is_live

from azure.ai.evaluation import (
    ViolenceEvaluator,
    ContentSafetyMultimodalEvaluator,
    ProtectedMaterialMultimodalEvaluator,
    evaluate,
)
from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator
from azure.identity import DefaultAzureCredential


@pytest.fixture
def data_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data.jsonl")


@pytest.fixture
def questions_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "questions.jsonl")


@pytest.mark.usefixtures("recording_injection", "recorded_test")
@pytest.mark.localtest
class TestSimAndEval:
    @pytest.mark.azuretest
    def test_violence_sim_conv_eval(self, project_scope, azure_cred):
        azure_ai_project = {
            "subscription_id": project_scope["subscription_id"],
            "resource_group_name": project_scope["resource_group_name"],
            "project_name": project_scope["project_name"],
        }

        # Simple First message-only echo callback
        async def callback(
            messages: List[Dict], stream: bool = False, session_state: Any = None, context: Dict[str, Any] = None
        ) -> dict:
            query = messages["messages"][0]["content"]

            formatted_response = {"content": query, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)
        # Run simulator to produce 2 results with 2 conversation turns each (4 messages)
        simulator_output = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_CONVERSATION,
                max_conversation_turns=2,
                max_simulation_results=2,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                randomization_seed=42,
            )
        )

        assert len(simulator_output) == 2
        assert len(simulator_output[0]["messages"]) == 4
        assert simulator_output[0]["messages"][0]["content"] == simulator_output[0]["messages"][1]["content"]
        # message 2 is non-deterministic, don't check it
        assert simulator_output[0]["messages"][0]["content"] == simulator_output[0]["messages"][3]["content"]

        # Write simulator output to file
        file_name = "eval_sim_test.jsonl"
        # Sadly tempfile doesn't play nice with evaluate's data reader
        # Write the output to the file
        with open(file_name, "w") as file:
            file.writelines(
                [
                    json.dumps({"conversation": {"messages": conversation["messages"]}}) + "\n"
                    for conversation in simulator_output
                ]
            )

        # Evaluator simulator output
        violence_eval = ViolenceEvaluator(azure_cred, project_scope)
        # run the evaluation
        eval_output = evaluate(
            data=file_name,
            # evaluation_name="sim_conv_violence_eval",
            # azure_ai_project=project_scope,
            evaluators={"violence": violence_eval},
        )

        # validate the results
        assert eval_output is not None
        assert eval_output["rows"] is not None
        assert len(eval_output["rows"]) == 2
        assert eval_output["rows"][0]["inputs.conversation"]["messages"] == simulator_output[0]["messages"]
        assert eval_output["rows"][1]["inputs.conversation"]["messages"] == simulator_output[1]["messages"]

        assert len(eval_output["rows"][0]["outputs.violence.evaluation_per_turn"]["violence_reason"]) == 2
        assert len(eval_output["rows"][1]["outputs.violence.evaluation_per_turn"]["violence_reason"]) == 2

        row_result_df = pd.DataFrame(eval_output["rows"])
        assert "inputs.conversation" in row_result_df.columns.to_list()
        assert "outputs.violence.violence_score" in row_result_df.columns.to_list()
        assert "outputs.violence.evaluation_per_turn" in row_result_df.columns.to_list()

        assert row_result_df["outputs.violence.violence_score"][0] in [0, 5]
        assert row_result_df["outputs.violence.violence_score"][1] in [0, 5]

        metrics = eval_output["metrics"]
        assert metrics is not None
        assert "violence.violence_defect_rate" in metrics.keys()
        assert metrics["violence.violence_defect_rate"] is not None

        # Cleanup file
        os.remove(file_name)

    @pytest.mark.azuretest
    def test_violence_sim_qna_eval(self, project_scope, azure_cred):
        azure_ai_project = {
            "subscription_id": project_scope["subscription_id"],
            "resource_group_name": project_scope["resource_group_name"],
            "project_name": project_scope["project_name"],
        }

        async def callback(
            messages: List[Dict],
            stream: bool = False,
            session_state: Any = None,
            context: Optional[Dict[str, Any]] = None,
        ) -> dict:
            query = messages["messages"][0]["content"]
            response = f"Response - {query}"
            temperature = 0.0
            formatted_response = {
                "content": response,
                "role": "assistant",
                "context": {
                    "temperature": temperature,
                },
            }
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        simulator_output = asyncio.run(simulator(scenario=AdversarialScenario.ADVERSARIAL_QA, target=callback))

        # Write simulator output to file
        file_name = "eval_sim_test.jsonl"
        # Sadly tempfile doesn't play nice with evaluate's data reader
        # Write the output to the file
        with open(file_name, "w") as file:
            file.writelines(
                [
                    json.dumps({"conversation": {"messages": conversation["messages"]}}) + "\n"
                    for conversation in simulator_output
                ]
            )

        # Evaluator simulator output
        violence_eval = ViolenceEvaluator(azure_cred, project_scope)
        # run the evaluation
        eval_output = evaluate(
            data=file_name,
            # evaluation_name="sim_conv_violence_eval",
            # azure_ai_project=project_scope,
            evaluators={"violence": violence_eval},
        )

        # validate the results
        assert eval_output is not None
        assert eval_output["rows"] is not None
        assert eval_output["metrics"] is not None

        row_result_df = pd.DataFrame(eval_output["rows"])
        metrics = eval_output["metrics"]

        assert "inputs.conversation" in row_result_df.columns.to_list()
        assert "outputs.violence.violence_score" in row_result_df.columns.to_list()

        assert row_result_df["outputs.violence.violence_score"][1] in [0, 5]
        assert "violence.violence_defect_rate" in metrics.keys()

        # Cleanup file
        os.remove(file_name)

    @pytest.mark.azuretest
    def test_protected_material_sim_image_understanding(self, project_scope, azure_cred):
        azure_ai_project = {
            "subscription_id": project_scope["subscription_id"],
            "resource_group_name": project_scope["resource_group_name"],
            "project_name": project_scope["project_name"],
        }

        # Simple First message-only echo callback
        async def callback(
            messages: List[Dict], stream: bool = False, session_state: Any = None, context: Dict[str, Any] = None
        ) -> dict:
            query = messages["messages"][0]["content"]

            formatted_response = {
                "content": "This is what they are teaching our kids in schools these days",
                "role": "assistant",
            }
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        # Run simulator to produce 2 results with 2 conversation turns each (4 messages)
        simulator_output = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_IMAGE_UNDERSTANDING,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
            )
        )
        assert len(simulator_output) == 1

        # Write simulator output to file
        file_name = "eval_sim_test.jsonl"

        # Write the output to the file
        with open(file_name, "w") as file:
            file.writelines(
                [
                    json.dumps({"conversation": {"messages": conversation["messages"]}}) + "\n"
                    for conversation in simulator_output
                ]
            )

        # Evaluator simulator output
        protected_material_eval = ProtectedMaterialMultimodalEvaluator(azure_cred, project_scope)
        # run the evaluation
        eval_output = evaluate(
            data=file_name,
            evaluation_name="sim_image_understanding_protected_material_eval",
            # azure_ai_project=project_scope,
            evaluators={"protected_material": protected_material_eval},
        )

        # validate the results
        assert eval_output is not None
        assert eval_output["rows"] is not None
        assert eval_output["metrics"] is not None

        assert len(eval_output["rows"]) == 1
        assert eval_output["rows"][0]["outputs.protected_material.fictional_characters_reason"] is not None
        assert eval_output["rows"][0]["outputs.protected_material.artwork_reason"] is not None
        assert eval_output["rows"][0]["outputs.protected_material.logos_and_brands_reason"] is not None

        assert eval_output["rows"][0]["outputs.protected_material.fictional_characters_label"] is not None
        assert eval_output["rows"][0]["outputs.protected_material.artwork_label"] is not None
        assert eval_output["rows"][0]["outputs.protected_material.logos_and_brands_label"] is not None

        # Cleanup file
        os.remove(file_name)

    @pytest.mark.azuretest
    def test_protected_material_sim_image_gen(self, project_scope, azure_cred):
        azure_ai_project = {
            "subscription_id": project_scope["subscription_id"],
            "resource_group_name": project_scope["resource_group_name"],
            "project_name": project_scope["project_name"],
        }

        async def callback(
            messages: List[Dict], stream: bool = False, session_state: Any = None, context: Dict[str, Any] = None
        ) -> dict:
            query = messages["messages"][0]["content"]
            content = [
                {
                    "type": "image_url",
                    "image_url": {"url": "http://www.firstaidforfree.com/wp-content/uploads/2017/01/First-Aid-Kit.jpg"},
                }
            ]
            formatted_response = {"content": content, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        # Run simulator to produce 2 results with 2 conversation turns each (4 messages)
        simulator_output = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_IMAGE_GEN,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
            )
        )
        assert len(simulator_output) == 1

        # Write simulator output to file
        file_name = "eval_sim_test.jsonl"

        # Write the output to the file
        with open(file_name, "w") as file:
            file.writelines([json.dumps({"conversation": conversation}) + "\n" for conversation in simulator_output])

        # Evaluator simulator output
        protected_material_eval = ProtectedMaterialMultimodalEvaluator(azure_cred, project_scope)
        # run the evaluation
        eval_output = evaluate(
            data=file_name,
            evaluation_name="sim_image_gen_protected_material_eval",
            # azure_ai_project=project_scope,
            evaluators={"protected_material": protected_material_eval},
        )

        row_result_df = pd.DataFrame(eval_output["rows"])
        metrics = eval_output["metrics"]
        # validate the results
        assert metrics is not None
        assert eval_output is not None
        assert len(eval_output["rows"]) == 1
        assert eval_output["rows"][0]["inputs.conversation"] == simulator_output[0]

        assert eval_output["rows"][0]["outputs.protected_material.fictional_characters_reason"] is not None
        assert eval_output["rows"][0]["outputs.protected_material.artwork_reason"] is not None
        assert eval_output["rows"][0]["outputs.protected_material.logos_and_brands_reason"] is not None

        assert eval_output["rows"][0]["outputs.protected_material.fictional_characters_label"] is not None
        assert eval_output["rows"][0]["outputs.protected_material.artwork_label"] is not None
        assert eval_output["rows"][0]["outputs.protected_material.logos_and_brands_label"] is not None

        # Cleanup file
        os.remove(file_name)

    @pytest.mark.azuretest
    def test_content_safety_sim_image_gen(self, project_scope, azure_cred):
        azure_ai_project = {
            "subscription_id": project_scope["subscription_id"],
            "resource_group_name": project_scope["resource_group_name"],
            "project_name": project_scope["project_name"],
        }

        async def callback(
            messages: List[Dict], stream: bool = False, session_state: Any = None, context: Dict[str, Any] = None
        ) -> dict:
            query = messages["messages"][0]["content"]
            content = [
                {
                    "type": "image_url",
                    "image_url": {"url": "http://www.firstaidforfree.com/wp-content/uploads/2017/01/First-Aid-Kit.jpg"},
                }
            ]
            formatted_response = {"content": content, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        simulator_output = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_IMAGE_GEN,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
            )
        )
        assert len(simulator_output) == 1

        # Write simulator output to file
        file_name = "eval_sim_test.jsonl"

        # Write the output to the file
        with open(file_name, "w") as file:
            file.writelines([json.dumps({"conversation": conversation}) + "\n" for conversation in simulator_output])

        # Evaluator simulator output
        content_safety_val = ContentSafetyMultimodalEvaluator(azure_cred, project_scope)
        # run the evaluation
        result = evaluate(
            data=file_name,
            evaluation_name="sim_image_gen_content_safety_eval",
            azure_ai_project=project_scope,
            evaluators={"content_safety": content_safety_val},
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]

        assert result is not None
        assert result["rows"] is not None

        assert "outputs.content_safety.sexual" in row_result_df.columns.to_list()
        assert "outputs.content_safety.violence" in row_result_df.columns.to_list()
        assert "outputs.content_safety.self_harm" in row_result_df.columns.to_list()
        assert "outputs.content_safety.hate_unfairness" in row_result_df.columns.to_list()

        assert "content_safety.sexual_defect_rate" in metrics.keys()
        assert "content_safety.violence_defect_rate" in metrics.keys()
        assert "content_safety.self_harm_defect_rate" in metrics.keys()
        assert "content_safety.hate_unfairness_defect_rate" in metrics.keys()

        assert 0 <= metrics.get("content_safety.sexual_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.violence_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.self_harm_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.hate_unfairness_defect_rate") <= 1

        # Cleanup file
        os.remove(file_name)
