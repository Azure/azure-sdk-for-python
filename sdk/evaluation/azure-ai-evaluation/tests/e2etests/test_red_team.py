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

        if model_config["azure_endpoint"] != "https://Sanitized.api.cognitive.microsoft.com":
            return model_config

        return AzureOpenAIModelConfiguration(
            **{**model_config, "azure_endpoint": "https://Sanitized.openai.azure.com/"},
        )

    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (
            ("project_scope", "azure_cred"),
            ("project_scope_onedp", "azure_cred_onedp"),
        ),
    )
    def test_red_team_basic_scan(self, request, proj_scope, cred):
        """Test basic red team scan with minimal configuration."""
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
            num_objectives=1
        )
        
        # Run scan
        result = asyncio.run(red_team.scan(
            target=simple_target,
            scan_name="test_basic_scan",
            attack_strategies=[AttackStrategy.Base64],
            timeout=4800,
        ))
        
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
        ("proj_scope", "cred"), 
        (("project_scope", "azure_cred"), ("project_scope_onedp", "azure_cred_onedp"))
    )
    def test_red_team_with_azure_openai_target(self, request, proj_scope, cred, sanitized_model_config):
        """Test red team scan with Azure OpenAI model as target."""
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)
        
        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.HateUnfairness],
            num_objectives=1
        )
        
        result = asyncio.run(red_team.scan(
            target=sanitized_model_config,
            scan_name="test_azure_openai_target",
            attack_strategies=[AttackStrategy.Base64],
            timeout=4800,
            skip_upload=True
        ))
        
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
        ("proj_scope", "cred"), 
        (("project_scope", "azure_cred"), ("project_scope_onedp", "azure_cred_onedp"))
    )
    def test_red_team_with_callback_target(self, request, proj_scope, cred):
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
            num_objectives=1
        )

        result = asyncio.run(red_team.scan(
            target=callback_function,
            scan_name="test_callback_target",
            attack_strategies=[AttackStrategy.Base64],
            timeout=4800,
            skip_upload=True
        ))

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
        ("proj_scope", "cred"), 
        (("project_scope", "azure_cred"), ("project_scope_onedp", "azure_cred_onedp"))
    )
    def test_red_team_multi_turn_attack(self, request, proj_scope, cred):
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        # Setup a simple target function
        def simple_target(query: str) -> str:
            return "Sorry I cannot assist with that."

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.Violence],
            num_objectives=1
        )

        result = asyncio.run(red_team.scan(
            target=simple_target,
            scan_name="test_multi_turn_attack",
            attack_strategies=[
                AttackStrategy.MultiTurn,
            ],
            timeout=4800,
            skip_upload=True
        ))

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
        ("proj_scope", "cred"), 
        (("project_scope", "azure_cred"), ("project_scope_onedp", "azure_cred_onedp"))
    )
    def test_red_team_crescendo_attack(self, request, proj_scope, cred):
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        # Setup a simple target function
        def simple_target(query: str) -> str:
            return "Sorry I cannot assist with that."

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.Violence],
            num_objectives=1
        )

        result = asyncio.run(red_team.scan(
            target=simple_target,
            scan_name="test_crescendo_attack",
            attack_strategies=[
                AttackStrategy.Crescendo,
            ],
            timeout=4800,
            skip_upload=True
        ))

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
        ("proj_scope", "cred"), 
        (("project_scope", "azure_cred"), ("project_scope_onedp", "azure_cred_onedp"))
    )
    def test_red_team_ungrounded_attributes(self, request, proj_scope, cred):
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
            num_objectives=1
        )

        result = asyncio.run(red_team.scan(
            target=callback_function,
            scan_name="test_ungrounded_attributes",
            attack_strategies=[
                AttackStrategy.Baseline,
            ],
            timeout=4800,
            skip_upload=True
        ))

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None

        # Validate conversation structure
        for attack in result.attack_details:
            conversation = attack["conversation"]
            assert len(conversation) >= 2
            assert conversation[0]["role"] == "user"
            assert conversation[1]["role"] == "assistant"
