from typing import Any, Dict, List, Optional
import pytest
import os
import asyncio
import tempfile
import json
from pathlib import Path

# This will automatically apply to all test files in this directory
# This avoids having to add the skipif decorator to each test class
pytest.importorskip("pyrit", reason="redteam extra is not installed")

from azure.ai.evaluation.red_team import RedTeam, RiskCategory, AttackStrategy
from azure.ai.evaluation.red_team._red_team_result import RedTeamResult
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration


@pytest.mark.usefixtures("recording_injection", "recorded_test")
@pytest.mark.azuretest
class TestRedTeam:
    @pytest.fixture
    def sanitized_model_config(self, model_config: AzureOpenAIModelConfiguration) -> AzureOpenAIModelConfiguration:
        """
        Fixture that sanitizes the Azure OpenAI model configuration for testing.

        Returns a sanitized version of the model configuration with updated endpoint
        if the original endpoint matches the sanitized test endpoint.

        Args:
            model_config: The original Azure OpenAI model configuration

        Returns:
            AzureOpenAIModelConfiguration: Sanitized model configuration for testing
        """
        if model_config["azure_endpoint"] != "https://Sanitized.api.cognitive.microsoft.com":
            return model_config

        return AzureOpenAIModelConfiguration(
            **{**model_config, "azure_endpoint": "https://Sanitized.openai.azure.com/"},
        )

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (
            # ("project_scope", "azure_cred"),
            ("project_scope_onedp", "azure_cred_onedp"),
        ),
    )
    def test_red_team_basic_scan(self, request, proj_scope, cred):
        """
        Test basic red team scan functionality with minimal configuration.

        Verifies that the RedTeam can successfully perform a scan with:
        - A simple string-based target function
        - Single risk category (Violence)
        - Base64 attack strategy
        - Single objective

        Validates that the scan results contain properly structured attack details
        with required fields like conversation, risk_category, and attack_technique.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        # Setup a simple target function
        def simple_target(query: str) -> str:
            return f"Response to: {query}"

        # Initialize RedTeam with minimal config
        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.Violence],
            num_objectives=1,
        )

        # Run scan
        result = asyncio.run(
            red_team.scan(
                target=simple_target,
                scan_name="test_basic_scan",
                attack_strategies=[AttackStrategy.Base64],
                timeout=4800,
                skip_upload=True,
            )
        )

        # Validate results
        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None
        assert len(result.attack_details) > 0

        # Validate scan structure
        for attack in result.attack_details:
            assert "conversation" in attack
            assert "risk_category" in attack
            assert "attack_technique" in attack
            assert attack["risk_category"] == "violence"

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"), (("project_scope", "azure_cred"), ("project_scope_onedp", "azure_cred_onedp"))
    )
    def test_red_team_with_azure_openai_target(self, request, proj_scope, cred, sanitized_model_config):
        """
        Test red team scan using Azure OpenAI model as the target.

        Validates that the RedTeam can successfully scan an Azure OpenAI model configuration
        target with HateUnfairness risk category. Verifies proper conversation structure
        with user and assistant roles in the attack details.

        Uses skip_upload=True to avoid uploading results during testing.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.HateUnfairness],
            num_objectives=1,
        )

        result = asyncio.run(
            red_team.scan(
                target=sanitized_model_config,
                scan_name="test_azure_openai_target",
                attack_strategies=[AttackStrategy.Base64],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None

        # Validate conversation structure
        for attack in result.attack_details:
            conversation = attack["conversation"]
            assert len(conversation) >= 2
            assert conversation[0]["role"] == "user"
            assert conversation[1]["role"] == "assistant"

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"), (("project_scope", "azure_cred"), ("project_scope_onedp", "azure_cred_onedp"))
    )
    def test_red_team_with_callback_target(self, request, proj_scope, cred):
        """
        Test red team scan using an async callback function as the target.

        Validates that the RedTeam can successfully scan an async callback function
        that follows the expected message-based interface. The callback function
        receives messages and returns a properly formatted response with messages,
        stream, session_state, and context fields.

        Verifies proper conversation structure in the results.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        # Setup a simple callback function
        async def callback_function(
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

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.HateUnfairness],
            num_objectives=1,
        )

        result = asyncio.run(
            red_team.scan(
                target=callback_function,
                scan_name="test_callback_target",
                attack_strategies=[AttackStrategy.Base64],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None

        # Validate conversation structure
        for attack in result.attack_details:
            conversation = attack["conversation"]
            assert len(conversation) >= 2
            assert conversation[0]["role"] == "user"
            assert conversation[1]["role"] == "assistant"

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"), (("project_scope", "azure_cred"), ("project_scope_onedp", "azure_cred_onedp"))
    )
    def test_red_team_multi_turn_attack(self, request, proj_scope, cred):
        """
        Test red team scan using MultiTurn attack strategy.

        Validates that the RedTeam can successfully execute multi-turn attacks
        which involve multiple conversation exchanges between the attacker and target.
        Verifies that multi-turn attacks produce conversations with more than 2 messages
        and that the conversation alternates between user and assistant roles properly.

        Uses a defensive target that responds with refusal messages.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        # Setup a simple target function
        def simple_target(query: str) -> str:
            return "Sorry I cannot assist with that."

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.Violence],
            num_objectives=1,
        )

        result = asyncio.run(
            red_team.scan(
                target=simple_target,
                scan_name="test_multi_turn_attack",
                attack_strategies=[
                    AttackStrategy.MultiTurn,
                ],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None

        # Validate conversation structure
        for attack in result.attack_details:
            conversation = attack["conversation"]
            if attack["attack_technique"] == "multi_turn":
                assert len(conversation) > 2
            else:
                assert len(conversation) == 2
            for i in range(len(conversation)):
                assert conversation[i]["role"] == "user" if i % 2 == 0 else "assistant"

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"), (("project_scope", "azure_cred"), ("project_scope_onedp", "azure_cred_onedp"))
    )
    def test_red_team_crescendo_attack(self, request, proj_scope, cred):
        """
        Test red team scan using Crescendo attack strategy.

        Validates that the RedTeam can successfully execute crescendo attacks
        which gradually escalate the conversation to try to elicit harmful responses.
        Verifies that crescendo attacks produce conversations with exactly 20 messages
        (10 turns) and that the conversation alternates between user and assistant roles.

        Uses a defensive target that responds with refusal messages.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        # Setup a simple target function
        def simple_target(query: str) -> str:
            return "Sorry I cannot assist with that."

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.Violence],
            num_objectives=1,
        )

        result = asyncio.run(
            red_team.scan(
                target=simple_target,
                scan_name="test_crescendo_attack",
                attack_strategies=[
                    AttackStrategy.Crescendo,
                ],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None

        # Validate conversation structure
        for attack in result.attack_details:
            conversation = attack["conversation"]
            if attack["attack_technique"] == "crescendo":
                assert len(conversation) == 20
            else:
                assert len(conversation) == 2
            for i in range(len(conversation)):
                assert conversation[i]["role"] == "user" if i % 2 == 0 else "assistant"

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"), (("project_scope", "azure_cred"), ("project_scope_onedp", "azure_cred_onedp"))
    )
    def test_red_team_ungrounded_attributes(self, request, proj_scope, cred):
        """
        Test red team scan for UngroundedAttributes risk category.

        Validates that the RedTeam can successfully scan for ungrounded attributes,
        which involve testing the target's tendency to generate factually incorrect
        or unsupported claims. Uses a callback function target that echoes the input
        and validates the conversation structure.

        Uses Baseline attack strategy which represents standard attack techniques
        without special encoding or multi-turn approaches.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        # Setup a simple callback function
        async def callback_function(
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

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.UngroundedAttributes],
            num_objectives=1,
        )

        result = asyncio.run(
            red_team.scan(
                target=callback_function,
                scan_name="test_ungrounded_attributes",
                attack_strategies=[
                    AttackStrategy.Baseline,
                ],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None

        # Validate conversation structure
        for attack in result.attack_details:
            conversation = attack["conversation"]
            assert len(conversation) >= 2
            assert conversation[0]["role"] == "user"
            assert conversation[1]["role"] == "assistant"
