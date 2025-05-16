# coding: utf-8
# type: ignore

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    These samples demonstrate usage of various classes and methods used to perform simulation in the azure-ai-evaluation library.
    
USAGE:
    python evaluation_samples_simulate.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_OPENAI_ENDPOINT
    2) AZURE_OPENAI_KEY
    3) AZURE_OPENAI_DEPLOYMENT
    4) AZURE_SUBSCRIPTION_ID
    5) AZURE_RESOURCE_GROUP_NAME
    6) AZURE_PROJECT_NAME
"""


class EvaluationSimulateSamples(object):
    def evaluation_simulate_classes_methods(self):
        # [START adversarial_scenario]
        import os
        import asyncio
        from typing import List, Dict, Any, Optional
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator
        from azure.identity import DefaultAzureCredential

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        async def callback(
            messages: List[Dict],
            stream: bool = False,
            session_state: Any = None,
            context: Optional[Dict[str, Any]] = None,
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

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=DefaultAzureCredential())

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_CONVERSATION,
                max_conversation_turns=2,
                max_simulation_results=2,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                randomization_seed=1,
            )
        )
        # [END adversarial_scenario]

        # [START supported_languages]
        import asyncio
        import os
        from azure.ai.evaluation.simulator import SupportedLanguages
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator
        from azure.identity import DefaultAzureCredential

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        async def callback(
            messages: List[Dict],
            stream: bool = False,
            session_state: Any = None,
            context: Optional[Dict[str, Any]] = None,
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

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=DefaultAzureCredential())

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_CONVERSATION,
                max_conversation_turns=4,
                num_queries=2,
                target=callback,
                language=SupportedLanguages.SimplifiedChinese,
            )
        )
        # [END supported_languages]

        # [START direct_attack_simulator]
        import os
        import asyncio
        from azure.ai.evaluation.simulator import AdversarialScenario, DirectAttackSimulator
        from azure.identity import DefaultAzureCredential

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        async def callback(
            messages: List[Dict],
            stream: bool = False,
            session_state: Any = None,
            context: Optional[Dict[str, Any]] = None,
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

        simulator = DirectAttackSimulator(azure_ai_project=azure_ai_project, credential=DefaultAzureCredential())

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_REWRITE,
                max_conversation_turns=3,
                max_simulation_results=2,
                target=callback,
            )
        )
        # [END direct_attack_simulator]

        # [START indirect_attack_simulator]
        import os
        import asyncio
        from azure.ai.evaluation.simulator import IndirectAttackSimulator
        from azure.identity import DefaultAzureCredential

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        async def callback(
            messages: List[Dict],
            stream: bool = False,
            session_state: Any = None,
            context: Optional[Dict[str, Any]] = None,
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

        simulator = IndirectAttackSimulator(azure_ai_project=azure_ai_project, credential=DefaultAzureCredential())

        outputs = asyncio.run(
            simulator(
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
            )
        )
        # [END indirect_attack_simulator]

        # [START nonadversarial_simulator]
        import os
        import asyncio
        from azure.ai.evaluation.simulator import Simulator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        async def callback(
            messages: List[Dict],
            stream: bool = False,
            session_state: Any = None,
            context: Optional[Dict[str, Any]] = None,
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

        simulator = Simulator(model_config=model_config)

        result = asyncio.run(
            simulator(
                target=callback,
                max_conversation_turns=2,
                text="some text",
                tasks=["tasks"],
                api_call_delay_sec=1,
                num_queries=1,
            )
        )
        # [END nonadversarial_simulator]


if __name__ == "__main__":
    print("Loading samples in evaluation_samples_simulate.py")
    sample = EvaluationSimulateSamples()
    print("Samples loaded successfully!")
    print("Running samples in evaluation_samples_simulate.py")
    sample.evaluation_simulate_classes_methods()
    print("Samples ran successfully!")
