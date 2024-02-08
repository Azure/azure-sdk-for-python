# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from azure.ai.generative.synthetic.simulator import Simulator, _template_dir as template_dir, SimulatorTemplates
from azure.ai.generative.synthetic.simulator._conversation.conversation_turn import ConversationTurn
from azure.ai.generative.synthetic.simulator._conversation import ConversationRole
from azure.ai.generative.synthetic.simulator.templates._templates import CONVERSATION

@pytest.mark.unittest
class TestSimulator:
    @patch("azure.ai.generative.synthetic.simulator.simulator.simulator.simulate_conversation")
    @patch("azure.ai.generative.synthetic.simulator.simulator.simulator.Simulator._to_openai_chat_completion_model")
    def test_simulator_returns_formatted_conversations(self, _, simulate_conversation_mock):

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
        simulator = Simulator(None, None)

        st = SimulatorTemplates()

        task_parameters = {
            "name": "Jake",
            "profile": "Jake is a 10 years old boy",
            "tone": "friendly",
            "metadata": {"k1": "v1", "k2": "v2"},
            "task": "this is task description",
            "chatbot_name": "chatbot_name"
        }

        conv_template = st.get_template(CONVERSATION)
        conv_params = st.get_template_parameters(CONVERSATION)

        assert set(task_parameters.keys()) == set(conv_params.keys())

        conv = simulator.simulate(conv_template, task_parameters, 2)

        expected_keys = set(["messages", "$schema"])
        assert type(conv) == dict
        assert set(conv) == expected_keys

    def test_simulator_parse_callback_citations(self, ):

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
        simulator = Simulator(None, None)

        turn_0_citations = simulator._get_citations(tempalte_parameters, context_keys=['metadata'], turn_num = 0)
        turn_1_citations = simulator._get_citations(tempalte_parameters, context_keys=['metadata'], turn_num = 1)
        turn_2_citations = simulator._get_citations(tempalte_parameters, context_keys=['metadata'], turn_num = 2)

        assert turn_0_citations == expected_turn_0_citations, "incorrect turn_0 citations"
        assert turn_1_citations == expected_turn_1_citations, "incorrect turn_1 citations"
        assert turn_2_citations == expected_turn_2_citations, "incorrect turn_2 citations"