# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
import tempfile
import os
import asyncio

from unittest.mock import Mock, patch, AsyncMock, MagicMock

from azure.ai.generative.synthetic.simulator import Simulator, _template_dir as template_dir
from azure.ai.generative.synthetic.simulator.templates.simulator_templates import SimulatorTemplates
from azure.ai.generative.synthetic.simulator._conversation.conversation_turn import ConversationTurn
from azure.ai.generative.synthetic.simulator._conversation import ConversationRole
from azure.ai.generative.synthetic.simulator.templates._templates import CONVERSATION

@pytest.fixture()
def mock_config():
    mock_config = Mock()
    mock_config.api_key = "apikey"
    mock_config.deployment_name = "deployment"
    mock_config.api_version = "api-version"
    mock_config.api_base = "api-base"
    mock_config.model_name = "model-name"
    mock_config.model_kwargs = {}
    yield mock_config

@pytest.fixture()
def system_model_completion():
    model = Mock()
    model.get_conversation_completion = AsyncMock()
    response = {
            "samples": ["message content"],
            "finish_reason": ["stop"],
            "id": None,
        }

    model.get_conversation_completion.return_value = {
        "request": {},
        "response": response,
        "time_taken": 0,
        "full_response": response,
    }

    yield model

@pytest.fixture()
def task_parameters():
    yield {
        "name": "Jake",
        "profile": "Jake is a 10 years old boy",
        "tone": "friendly",
        "metadata": {"k1": "v1", "k2": "v2"},
        "task": "this is task description",
        "chatbot_name": "chatbot_name"
    }

@pytest.fixture()
def conv_template():
    st = SimulatorTemplates()

    conv_template = st.get_template(CONVERSATION)
    yield conv_template

@pytest.fixture()
def async_callback():
    async def callback(x):
        return x
    yield callback

@pytest.mark.unittest
class TestSimulator:
    @patch("azure.ai.generative.synthetic.simulator.simulator.simulator.simulate_conversation")
    @patch("azure.ai.generative.synthetic.simulator.simulator.simulator.Simulator._to_openai_chat_completion_model")
    def test_simulator_returns_formatted_conversations(self, _, simulate_conversation_mock, mock_config, task_parameters, conv_template, async_callback):

        ct1 = ConversationTurn(
            role=ConversationRole.USER,
            name="Jake",
            message="<|im_start|>user\nconversation turn 0",
            full_response={"id": "convid", "response1":"k2"},
            request={"messages": [{"content": "some template string"}]}
        )

        ct2 = ConversationTurn(
            role=ConversationRole.USER,
            name="Jake",
            message="<|im_start|>user\nconversation turn 1",
            full_response={"id": "convid", "response2":"k2"},
            request={"messages": [{"content": "some template string"}]}
        )

        conv_history = [ct1, ct2]
        simulate_conversation_mock.return_value = ("conversation_id", conv_history)

        simulator = Simulator(
            simulator_connection=mock_config,
            ai_client=None,
            simulate_callback=async_callback
        )

        st = SimulatorTemplates()
        conv_params = st.get_template_parameters(CONVERSATION)

        assert set(task_parameters.keys()) == set(conv_params.keys())

        conv = simulator.simulate(
            template=conv_template,
            parameters=[task_parameters],
            max_conversation_turns=1)

        expected_keys = set(["messages", "$schema", "template_parameters"])
        assert issubclass(type(conv), list)
        assert len(conv) == 1
        assert set(conv[0]) == expected_keys

    def test_simulator_parse_callback_citations(self, mock_config, async_callback):
        tempalte_parameters = {'name': 'Jane',
            'tone': 'happy',
            'metadata': {'customer_info': '## customer_info      name: Jane Doe    age: 28',
            'callback_citation_key': 'callback_citations',
            'callback_citations': {'turn_0': {'documents': "\n>>> From: cHJvZHVjdF9pbmZvXzIubWQyMg==\n# Information about product item_number: 2"},
                                   'turn_2': {'documents': "\n>>> From: wohdjewodhfjevwdjfywlemfhe==\n# Information about product item_number: 3"}}}
            }
        expected_turn_0_citations = {'citations': [{'id': 'documents',
            'content': "\n>>> From: cHJvZHVjdF9pbmZvXzIubWQyMg==\n# Information about product item_number: 2"}]}
        expected_turn_1_citations = {'citations': [{'id': 'customer_info',
            'content': '## customer_info      name: Jane Doe    age: 28'}]}
        expected_turn_2_citations = {'citations': [{'id': 'documents',
            'content': "\n>>> From: wohdjewodhfjevwdjfywlemfhe==\n# Information about product item_number: 3"}]}
        simulator = Simulator(
            simulator_connection=mock_config,
            simulate_callback=async_callback
        )

        turn_0_citations = simulator._get_citations(tempalte_parameters, context_keys=['metadata'], turn_num = 0)
        turn_1_citations = simulator._get_citations(tempalte_parameters, context_keys=['metadata'], turn_num = 1)
        turn_2_citations = simulator._get_citations(tempalte_parameters, context_keys=['metadata'], turn_num = 2)

        assert turn_0_citations == expected_turn_0_citations, "incorrect turn_0 citations"
        assert turn_1_citations == expected_turn_1_citations, "incorrect turn_1 citations"
        assert turn_2_citations == expected_turn_2_citations, "incorrect turn_2 citations"

    @patch("azure.ai.generative.synthetic.simulator.simulator.simulator.Simulator._to_openai_chat_completion_model")
    def test_simulator_from_openai_callback(self, to_chat_completion_model, mock_config, system_model_completion, task_parameters, conv_template):
        oai_mock = AsyncMock()
        oai_mock.__wrapped__ = Mock()
        oai_mock.__wrapped__.__module__ = "openai.resources.chat.completions"
        oai_mock.__wrapped__.__name__ = "create"

        content = "oai magic mock"
        response = MagicMock()
        response.choices[0].message.role = "user"
        response.choices[0].message.content = content

        oai_mock.return_value = response

        to_chat_completion_model.return_value = system_model_completion

        sim = Simulator.from_fn(
            fn=oai_mock,
            simulator_connection=mock_config)

        conv = sim.simulate(
            template=conv_template,
            parameters=[task_parameters],
            max_conversation_turns=1)

        oai_mock.assert_called_once()
        assert(len(conv) == 1)
        assert(conv[0]["messages"][1]["content"] == "oai magic mock")

    # disabled for now. Azure sdk for python test pipeline import error in promptflow
    #  from opencensus.ext.azure.log_exporter import AzureEventHandler
    # E   ImportError: cannot import name 'AzureEventHandler' from 'opencensus.ext.azure.log_exporter' (D:\a\_work\1\s\sdk\ai\azure-ai-generative\.tox\mindependency\lib\site-packages\opencensus\ext\azure\log_exporter\__init__.py)
    @patch("azure.ai.generative.synthetic.simulator.simulator.simulator.Simulator._to_openai_chat_completion_model")
    @patch("promptflow.load_flow")
    @patch("azure.ai.generative.synthetic.simulator.simulator.simulator.Simulator._wrap_pf")
    def simulator_from_pf(self, wrap_pf, load_flow, to_chat_completion_model, mock_config, system_model_completion, task_parameters, conv_template):
        content = "pf_mock"
        
        async def callback(cm):
            cm["messages"].append(
                {
                    "role": "assistant",
                    "content": content
                }
            )
            return cm
        
        wrap_pf.return_value = callback
        load_flow.return_value = "dontcare"

        to_chat_completion_model.return_value = system_model_completion

        sim = Simulator.from_pf_path(
            pf_path="don't care",
            simulator_connection=mock_config)

        conv = sim.simulate(
            template=conv_template,
            parameters=[task_parameters],
            max_conversation_turns=1)

        assert(len(conv) == 1)
        assert(conv[0]["messages"][1]["content"] == content)

    @patch("azure.ai.generative.synthetic.simulator.simulator.simulator.Simulator._to_openai_chat_completion_model")
    def test_simulator_from_custom_callback(self, to_chat_completion_model, mock_config, system_model_completion, task_parameters, conv_template):
        to_chat_completion_model.return_value = system_model_completion

        content = "async callback"
        async def callback(cm):
            cm["messages"].append(
                {
                    "role": "assistant",
                    "content": content
                }
            )
            return cm
        sim = Simulator.from_fn(
            fn=callback,
            simulator_connection=mock_config)

        conv = sim.simulate(
            template=conv_template,
            parameters=[task_parameters],
            max_conversation_turns=1)

        assert(len(conv) == 1)
        assert(conv[0]["messages"][1]["content"] == content)

    def test_simulator_throws_expected_error_from_incorrect_template_type(self, mock_config, task_parameters, async_callback):
        simulator = Simulator(
            simulator_connection=mock_config,
            ai_client=None,
            simulate_callback=async_callback
        )
        with pytest.raises(ValueError) as exc_info:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(simulator.simulate_async(
                template="wrong template type",
                max_conversation_turns=1,
                parameters=[task_parameters]
                )
            )

        assert(str(exc_info.value).startswith("Please use simulator to construct template"))

    def test_simulator_throws_expected_error_from_sync_callback(self, mock_config):
        with pytest.raises(ValueError) as exc_info:
            simulator = Simulator(
                simulator_connection=mock_config,
                ai_client=None,
                simulate_callback=lambda x:x
            )

        assert(str(exc_info.value).startswith("Callback has to be an async function."))

    def test_simulator_throws_expected_error_from_unset_ai_client_or_connection(self):
        with pytest.raises(ValueError) as all_none_exc_info:
            simulator = Simulator(
                simulator_connection=None,
                ai_client=None,
                simulate_callback=lambda x:x
            )
        with pytest.raises(ValueError) as all_set_exc_info:
            simulator = Simulator(
                simulator_connection="some value",
                ai_client="some value",
                simulate_callback=lambda x:x
            )

        assert(str(all_none_exc_info.value).startswith("One and only one of the parameters [ai_client, simulator_connection]"))
        assert(str(all_set_exc_info.value).startswith("One and only one of the parameters [ai_client, simulator_connection]"))
