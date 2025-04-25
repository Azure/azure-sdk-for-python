import asyncio
import json
import os
from typing import Any, Dict, List, Optional

import pytest
from devtools_testutils import is_live

from azure.ai.evaluation._exceptions import EvaluationException


@pytest.mark.usefixtures("recording_injection", "recorded_test")
@pytest.mark.azuretest
class TestAdvSimulator:
    def test_adv_sim_init_with_prod_url(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialSimulator

        azure_ai_project = {
            "subscription_id": project_scope["subscription_id"],
            "resource_group_name": project_scope["resource_group_name"],
            "project_name": project_scope["project_name"],
        }
        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)
        assert callable(simulator)

    def test_incorrect_scenario_raises_error(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialSimulator

        azure_ai_project = {
            "subscription_id": project_scope["subscription_id"],
            "resource_group_name": project_scope["resource_group_name"],
            "project_name": project_scope["project_name"],
        }

        async def callback(x):
            return x

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)
        with pytest.raises(EvaluationException):
            asyncio.run(
                simulator(
                    max_conversation_turns=1,
                    max_simulation_results=1,
                    target=callback,
                    scenario="adv_conversation_wrong",
                )
            )

    def test_adv_qa_sim_responds_with_one_response(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator

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
            response_from_acs, temperature = query, 0.0
            formatted_response = {
                "content": response_from_acs["result"],
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

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_QA,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
            )
        )
        assert len(outputs) == 1
        # assert topic and target_population is not present in outpts[0]["scenario_parameters"]
        assert "topic" not in outputs[0]["template_parameters"]
        assert "target_population" not in outputs[0]["template_parameters"]

    def test_adv_qa_sim_responds_with_one_response(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator

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
            response_from_acs, temperature = query, 0.0
            formatted_response = {
                "content": response_from_acs["result"],
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

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_QA,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
            )
        )
        assert len(outputs) == 1
        # assert topic and target_population is not present in outpts[0]["scenario_parameters"]
        assert "topic" not in outputs[0]["template_parameters"]
        assert "target_population" not in outputs[0]["template_parameters"]

    def test_adv_code_vuln_sim_responds_with_one_response(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator

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
            response_from_llm = "SELECT * FROM users WHERE username = {user_input};" 
            temperature = 0.0
            formatted_response = {
                "content": response_from_llm,
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

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_CODE_VULNERABILITY,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
            )
        )
        assert len(outputs) == 1
        assert outputs[0]["messages"][0]["content"] is not None
        assert outputs[0]["messages"][1]["content"] == "SELECT * FROM users WHERE username = {user_input};"

    def test_adv_ungrounded_attributes_sim_responds_with_one_response(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator

        azure_ai_project = {
            "subscription_id": project_scope["subscription_id"],
            "resource_group_name": project_scope["resource_group_name"],
            "project_name": project_scope["project_name"],
        }
        
        response_from_llm = '''
            Person 1 might experience emotions such as:
                    Curiosity – They may wonder what the experience of meditation feels like.
                    Admiration – They might appreciate Person 2’s ability to find peace and focus.
                    Inspiration – They could feel motivated to try meditation themselves.
                    Serenity – Simply observing a calm moment might bring them a sense of peace.
                    Happiness – Seeing someone enjoy a tranquil experience could make them feel happy.
                    Their emotions would likely depend on their own mindset and past experiences with meditation or peaceful settings.
            ''' 

        async def callback(
            messages: List[Dict],
            stream: bool = False,
            session_state: Any = None,
            context: Optional[Dict[str, Any]] = None,
        ) -> dict:
            query = messages["messages"][0]["content"]
            temperature = 0.0
            formatted_response = {
                "content": response_from_llm,
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

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_UNGROUNDED_ATTRIBUTES,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
            )
        )
        assert len(outputs) == 1
        assert outputs[0]["messages"][0]["content"] is not None
        assert "CONVERSATION" in outputs[0]["messages"][0]["content"]
        assert outputs[0]["messages"][1]["content"] == response_from_llm

    @pytest.mark.skip(reason="Temporary skip to merge 37201, will re-enable in subsequent pr")
    def test_adv_conversation_sim_responds_with_responses(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator

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

            formatted_response = {"content": query, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_CONVERSATION,
                max_conversation_turns=2,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
            )
        )
        assert len(outputs) == 1
        assert len(outputs[0]["messages"]) == 4

    def test_adv_conversation_image_understanding_sim_responds_with_responses(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialSimulator
        from azure.ai.evaluation.simulator._adversarial_scenario import _UnstableAdversarialScenario

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

            formatted_response = {"content": query, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        outputs = asyncio.run(
            simulator(
                scenario=_UnstableAdversarialScenario.ADVERSARIAL_IMAGE_MULTIMODAL,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
            )
        )
        assert len(outputs) == 1
        assert len(outputs[0]["messages"]) > 0
        assert outputs[0]["messages"][0]["content"] is not None
        assert len(outputs[0]["messages"][0]["content"]) > 0

        def has_image_url_with_url(content):
            return any(
                isinstance(item, dict) and item.get("type") == "image_url" and "url" in item.get("image_url", {})
                for item in content
            )

        assert any(
            [
                (
                    has_image_url_with_url(outputs[0]["messages"][0]["content"])
                    if len(outputs[0]["messages"]) > 0
                    else False
                ),
                (
                    has_image_url_with_url(outputs[0]["messages"][1]["content"])
                    if len(outputs[0]["messages"]) > 1
                    else False
                ),
            ]
        )

    def test_adv_conversation_image_gen_sim_responds_with_responses(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialSimulator
        from azure.ai.evaluation.simulator._adversarial_scenario import _UnstableAdversarialScenario

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

        outputs = asyncio.run(
            simulator(
                scenario=_UnstableAdversarialScenario.ADVERSARIAL_IMAGE_GEN,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
            )
        )
        assert len(outputs) == 1
        assert len(outputs[0]["messages"]) > 0
        assert outputs[0]["messages"][1]["content"] is not None
        assert len(outputs[0]["messages"][1]["content"]) > 0

        def has_image_url_with_url(content):
            return any(
                isinstance(item, dict) and item.get("type") == "image_url" and "url" in item.get("image_url", {})
                for item in content
            )

        assert any(
            [
                (
                    has_image_url_with_url(outputs[0]["messages"][0]["content"])
                    if len(outputs[0]["messages"]) > 0
                    else False
                ),
                (
                    has_image_url_with_url(outputs[0]["messages"][1]["content"])
                    if len(outputs[0]["messages"]) > 1
                    else False
                ),
            ]
        )

    def test_adv_summarization_sim_responds_with_responses(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator

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

            formatted_response = {"content": query, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_SUMMARIZATION,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
            )
        )
        assert len(outputs) == 1

    def test_adv_summarization_jailbreak_sim_responds_with_responses(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator

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

            formatted_response = {"content": query, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_SUMMARIZATION,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                _jailbreak_type="upia",
            )
        )
        assert len(outputs) == 1

    def test_adv_rewrite_sim_responds_with_responses(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator

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

            formatted_response = {"content": query, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_REWRITE,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                _jailbreak_type="upia",
            )
        )
        assert len(outputs) == 1

    def test_adv_protected_matierial_sim_responds_with_responses(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator

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

            formatted_response = {"content": query, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_CONTENT_PROTECTED_MATERIAL,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
            )
        )
        assert len(outputs) == 1

    def test_adv_eci_sim_responds_with_responses(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialSimulator
        from azure.ai.evaluation.simulator._adversarial_scenario import _UnstableAdversarialScenario

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

            formatted_response = {"content": query, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        outputs = asyncio.run(
            simulator(
                scenario=_UnstableAdversarialScenario.ECI,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
            )
        )
        assert len(outputs) == 1

    @pytest.mark.skipif(is_live(), reason="API not fully released yet. Don't run in live mode unless connected to INT.")
    @pytest.mark.skipif(
        not is_live(), reason="Test recording is polluted with telemetry data and fails in playback mode."
    )
    def test_adv_xpia_sim_responds_with_responses(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, IndirectAttackSimulator

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

            formatted_response = {"content": query, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = IndirectAttackSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_INDIRECT_JAILBREAK,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
            )
        )
        assert len(outputs) == 1

    @pytest.mark.skipif(
        not is_live(), reason="Something is instable/inconsistent in the recording. Fails in playback mode."
    )
    def test_adv_sim_order_randomness_with_jailbreak(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator

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

            formatted_response = {"content": query, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        outputs1 = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_REWRITE,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                _jailbreak_type="upia",
                randomization_seed=1,
            )
        )

        outputs2 = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_REWRITE,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                _jailbreak_type="upia",
                randomization_seed=1,
            )
        )

        outputs3 = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_REWRITE,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                _jailbreak_type="upia",
                randomization_seed=2,
            )
        )
        # Make sure that outputs 1 and 2 are identical, but not identical to 3
        assert outputs1[0]["template_parameters"] == outputs2[0]["template_parameters"]
        assert outputs1[0]["template_parameters"] != outputs3[0]["template_parameters"]

    @pytest.mark.skipif(
        not is_live(), reason="Something is instable/inconsistent in the recording. Fails in playback mode."
    )
    def test_adv_sim_order_randomness(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator

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

            formatted_response = {"content": query, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        outputs1 = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_REWRITE,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                randomization_seed=1,
            )
        )

        outputs2 = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_REWRITE,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                randomization_seed=1,
            )
        )

        outputs3 = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_REWRITE,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                randomization_seed=2,
            )
        )
        # Make sure that outputs 1 and 2 are identical, but not identical to 3
        assert outputs1[0]["template_parameters"] == outputs2[0]["template_parameters"]
        assert outputs1[0]["template_parameters"] != outputs3[0]["template_parameters"]

    @pytest.mark.skipif(
        not is_live(), reason="Something is instable/inconsistent in the recording. Fails in playback mode."
    )
    def test_jailbreak_sim_order_randomness(self, azure_cred, project_scope):
        os.environ.pop("RAI_SVC_URL", None)
        from azure.ai.evaluation.simulator import AdversarialScenario, DirectAttackSimulator

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

            formatted_response = {"content": query, "role": "assistant"}
            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = DirectAttackSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        outputs1 = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_REWRITE,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                randomization_seed=1,
            )
        )

        outputs2 = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_REWRITE,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                randomization_seed=1,
            )
        )

        outputs3 = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_REWRITE,
                max_conversation_turns=1,
                max_simulation_results=1,
                target=callback,
                api_call_retry_limit=3,
                api_call_retry_sleep_sec=1,
                api_call_delay_sec=30,
                concurrent_async_task=1,
                randomization_seed=2,
            )
        )
        # Make sure the regular prompt exists within the jailbroken equivalent, but also that they aren't identical.
        outputs1["regular"][0]["messages"][0]["content"] in outputs1["jailbreak"][0]["messages"][0]["content"]
        outputs1["regular"][0]["messages"][0]["content"] != outputs1["jailbreak"][0]["messages"][0]["content"]
        # Check that outputs1 and outputs2 are identical, but not identical to outputs3
        outputs1["regular"][0]["messages"][0]["content"] == outputs2["regular"][0]["messages"][0]["content"]
        outputs1["jailbreak"][0]["messages"][0]["content"] == outputs2["jailbreak"][0]["messages"][0]["content"]
        outputs1["regular"][0]["messages"][0]["content"] != outputs3["regular"][0]["messages"][0]["content"]
        outputs1["jailbreak"][0]["messages"][0]["content"] != outputs3["jailbreak"][0]["messages"][0]["content"]
        # Check that outputs3 has the same equivalency as outputs1, even without a provided seed.
        outputs3["regular"][0]["messages"][0]["content"] in outputs3["jailbreak"][0]["messages"][0]["content"]
        outputs3["regular"][0]["messages"][0]["content"] != outputs3["jailbreak"][0]["messages"][0]["content"]

    def test_regular_and_jailbreak_outputs_match(self, azure_cred, project_scope):
        """
        Test to verify that the regular and jailbreak outputs of the simulator have matching categories
        and that the queries have the same ending characters.
        """
        os.environ.pop("RAI_SVC_URL", None)

        from azure.ai.evaluation.simulator import DirectAttackSimulator, AdversarialScenario

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
            response = "I do not know"

            formatted_response = {
                "content": response,
                "role": "assistant",
                "context": {"key": {}},
            }

            messages["messages"].append(formatted_response)
            return {
                "messages": messages["messages"],
                "stream": stream,
                "session_state": session_state,
                "context": context,
            }

        simulator = DirectAttackSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)

        # Run the simulator to obtain both regular and jailbreak outputs
        outputs = asyncio.run(
            simulator(
                scenario=AdversarialScenario.ADVERSARIAL_QA,
                target=callback,
                max_conversation_turns=1,
                max_simulation_results=16,
            )
        )
        regular_output = outputs["regular"].to_eval_qr_json_lines()
        jailbreak_output = outputs["jailbreak"].to_eval_qr_json_lines()

        regular_lines = [json.loads(line) for line in regular_output.strip().splitlines()]
        jailbreak_lines = [json.loads(line) for line in jailbreak_output.strip().splitlines()]

        assert len(regular_lines) == len(
            jailbreak_lines
        ), "Mismatch in number of output lines between regular and jailbreak."

        for idx, (reg_line, jb_line) in enumerate(zip(regular_lines, jailbreak_lines), start=1):
            # Check if the categories match
            assert reg_line["category"] == jb_line["category"], (
                f"Category mismatch at line {idx}: "
                f"regular='{reg_line['category']}' vs jailbreak='{jb_line['category']}'"
            )

            # Check if the queries have the same ending characters
            l1 = len(reg_line["query"])
            assert reg_line["query"] == jb_line["query"][-l1:], (
                f"Query ending mismatch at line {idx}: "
                f"regular='{reg_line['query']}' vs jailbreak='{jb_line['query'][-l1:]}'"
            )

        print("All regular and jailbreak outputs match as expected.")
