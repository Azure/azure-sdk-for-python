"""
E2E tests for RedTeam Foundry integration.

These tests verify the Foundry-based execution path which is used when
PyRIT's orchestrator module is not available (new PyRIT versions).

Tests cover:
- Basic Foundry execution with standard attacks
- IndirectJailbreak (XPIA) attacks with context
- Multiple strategies in a single execution
- Context data handling (binary_path storage)
"""

from typing import Any, Dict, List, Optional
import pytest
import asyncio

# This will automatically apply to all test files in this directory
# This avoids having to add the skipif decorator to each test class
pytest.importorskip("pyrit", reason="redteam extra is not installed")

from azure.ai.evaluation.red_team import RedTeam, RiskCategory, AttackStrategy
from azure.ai.evaluation.red_team._red_team_result import RedTeamResult


@pytest.mark.usefixtures("recording_injection", "recorded_test")
@pytest.mark.azuretest
class TestRedTeamFoundry:
    """Test RedTeam Foundry integration features."""

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_basic_execution(self, request, proj_scope, cred):
        """
        Test basic Foundry execution path.

        Verifies that the RedTeam can execute attacks via Foundry when
        the orchestrator module is not available. Uses a simple target
        function with multiple attack strategies to test the Foundry
        strategy mapping and execution.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        def simple_target(query: str) -> str:
            return f"I cannot help with that request: {query}"

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.Violence],
            num_objectives=1,
        )

        result = asyncio.run(
            red_team.scan(
                target=simple_target,
                scan_name="test_foundry_basic",
                attack_strategies=[AttackStrategy.Baseline, AttackStrategy.Base64],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None
        assert len(result.attack_details) > 0

        # Validate attack details structure
        for attack in result.attack_details:
            assert "conversation" in attack
            assert "risk_category" in attack
            assert "attack_technique" in attack
            assert attack["risk_category"] == "violence"

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_indirect_jailbreak(self, request, proj_scope, cred):
        """
        Test IndirectJailbreak (XPIA) attack via Foundry.

        Verifies that indirect/XPIA attacks are properly executed through
        the Foundry path with context injection. Uses a callback function
        that receives context data.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        # Callback that handles context
        async def callback_with_context(
            messages: List[Dict],
            stream: bool = False,
            session_state: Any = None,
            context: Optional[Dict[str, Any]] = None,
        ) -> dict:
            query = messages["messages"][0]["content"]

            # Check if context was provided (for XPIA attacks)
            context_info = ""
            if context and "contexts" in context:
                context_info = f" [with {len(context['contexts'])} context items]"

            formatted_response = {
                "content": f"Response to: {query}{context_info}",
                "role": "assistant"
            }
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
            risk_categories=[RiskCategory.Violence],
            num_objectives=1,
        )

        result = asyncio.run(
            red_team.scan(
                target=callback_with_context,
                scan_name="test_indirect_jailbreak",
                attack_strategies=[AttackStrategy.IndirectJailbreak],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None

        # Verify attack details
        for attack in result.attack_details:
            assert "conversation" in attack
            assert "risk_category" in attack
            # IndirectJailbreak should be mapped to indirect_jailbreak technique
            assert attack["attack_technique"] in ["indirect_jailbreak", "baseline"]

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_multiple_risk_categories(self, request, proj_scope, cred):
        """
        Test Foundry execution with multiple risk categories.

        Verifies that Foundry can handle attacks across multiple risk
        categories in a single scan, mapping objectives correctly to
        each category.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        def simple_target(query: str) -> str:
            return "I cannot help with harmful requests."

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.Violence, RiskCategory.HateUnfairness],
            num_objectives=1,
        )

        # Note: PyRIT requires at least one Foundry strategy - Baseline alone is not sufficient
        result = asyncio.run(
            red_team.scan(
                target=simple_target,
                scan_name="test_multi_risk",
                attack_strategies=[AttackStrategy.Baseline, AttackStrategy.Base64],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None

        # Check that we have results for multiple risk categories
        risk_categories_found = set()
        for attack in result.attack_details:
            risk_categories_found.add(attack["risk_category"])

        # Should have at least one result (categories may vary based on seed generation)
        assert len(risk_categories_found) >= 1

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_with_application_scenario(self, request, proj_scope, cred):
        """
        Test Foundry execution with application scenario context.

        Verifies that providing an application scenario influences
        the generated attack objectives appropriately.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        def simple_target(query: str) -> str:
            return f"Customer service response: {query}"

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.Violence],
            num_objectives=1,
            application_scenario="A customer service chatbot for a retail company",
        )

        # Note: PyRIT requires at least one Foundry strategy - Baseline alone is not sufficient
        result = asyncio.run(
            red_team.scan(
                target=simple_target,
                scan_name="test_app_scenario",
                attack_strategies=[AttackStrategy.Baseline, AttackStrategy.Base64],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None
        assert len(result.attack_details) > 0

        # Validate conversation structure
        for attack in result.attack_details:
            conversation = attack["conversation"]
            assert len(conversation) >= 2
            assert conversation[0]["role"] == "user"
            assert conversation[1]["role"] == "assistant"

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_strategy_combination(self, request, proj_scope, cred):
        """
        Test Foundry execution with multiple converters.

        Verifies that combining Base64 and ROT13 strategies works
        correctly through the Foundry strategy mapping.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        def simple_target(query: str) -> str:
            return "I cannot assist with that."

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.Violence],
            num_objectives=1,
        )

        result = asyncio.run(
            red_team.scan(
                target=simple_target,
                scan_name="test_strategy_combo",
                attack_strategies=[AttackStrategy.Base64, AttackStrategy.ROT13],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None

        # Check that we have results for the strategies
        techniques_found = set()
        for attack in result.attack_details:
            techniques_found.add(attack.get("attack_technique", "unknown"))

        # Should have results from the strategies
        assert len(techniques_found) >= 1
