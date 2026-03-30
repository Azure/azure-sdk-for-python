"""
E2E tests for RedTeam Foundry integration.

These tests verify the Foundry-based execution path which is used when
PyRIT's orchestrator module is not available (new PyRIT versions).

Tests cover:
- Basic Foundry execution with standard attacks
- IndirectJailbreak (XPIA) attacks with context
- Multiple strategies in a single execution
- Context data handling (binary_path storage)
- AzureOpenAIModelConfiguration target type
- Agent-flagged callback targets (is_agent_target=True)
- Agent targets with tool context injection
- New v2025_11_15 risk categories (ProtectedMaterial, CodeVulnerability, TaskAdherence)
- Agent-only risk categories (SensitiveDataLeakage)
- Error paths for contract enforcement (agent-only risk on model target)
- MultiTurn and Crescendo attack strategies via Foundry path
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
from unittest.mock import patch
import pytest
import asyncio

# This will automatically apply to all test files in this directory
# This avoids having to add the skipif decorator to each test class
pytest.importorskip("pyrit", reason="redteam extra is not installed")

from azure.ai.evaluation.red_team import RedTeam, RiskCategory, AttackStrategy
from azure.ai.evaluation.red_team._red_team_result import RedTeamResult
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration

SEEDS_DIR = str(Path(__file__).parent / "data" / "redteam_seeds")


@pytest.mark.usefixtures("recording_injection", "recorded_test")
@pytest.mark.azuretest
class TestRedTeamFoundry:
    """Test RedTeam Foundry integration features."""

    @staticmethod
    def _validate_attack_details(
        attack_details: List[Dict],
        *,
        expected_risk_category: Optional[str] = None,
        min_attacks: int = 1,
        min_conversation_length: int = 2,
    ) -> None:
        """Validate the structure and content of attack details from a red team scan.

        :param attack_details: List of attack detail dicts from RedTeamResult.attack_details
        :param expected_risk_category: If set, asserts all attacks match this risk category
        :param min_attacks: Minimum number of attack details expected (default: 1)
        :param min_conversation_length: Minimum number of messages per conversation (default: 2)
        """
        assert attack_details is not None, "attack_details should not be None"
        assert (
            len(attack_details) >= min_attacks
        ), f"Expected at least {min_attacks} attack detail(s), got {len(attack_details)}"

        for attack in attack_details:
            # Required fields per RAISvc contract
            assert "conversation" in attack, "Attack detail missing 'conversation' field"
            assert "risk_category" in attack, "Attack detail missing 'risk_category' field"
            assert "attack_technique" in attack, "Attack detail missing 'attack_technique' field"

            # Validate risk category if expected
            if expected_risk_category is not None:
                assert (
                    attack["risk_category"] == expected_risk_category
                ), f"Expected risk_category '{expected_risk_category}', got '{attack['risk_category']}'"

            # Validate conversation structure
            conversation = attack["conversation"]
            assert (
                len(conversation) >= min_conversation_length
            ), f"Expected at least {min_conversation_length} messages in conversation, got {len(conversation)}"

            # Validate first message is from user
            assert (
                conversation[0]["role"] == "user"
            ), f"First conversation message should have role 'user', got '{conversation[0]['role']}'"
            # Validate conversation contains at least one assistant response.
            # Note: strict user/assistant alternation is NOT enforced because some strategies
            # (e.g., IndirectJailbreak/XPIA) send context as a second user message before
            # the assistant responds, producing user→user→assistant sequences.
            assistant_msgs = [m for m in conversation if m.get("role") == "assistant"]
            assert len(assistant_msgs) > 0, (
                f"Conversation should contain at least one assistant message, "
                f"got roles: {[m.get('role') for m in conversation]}"
            )

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
        self._validate_attack_details(result.attack_details, expected_risk_category="violence")

        # Validate per_testing_criteria_results contains both risk categories and attack strategies
        if result.scan_result:
            summary = result.scan_result.get("AOAI_Compatible_Summary", result.scan_result)
            per_testing = summary.get("per_testing_criteria_results", [])
            if per_testing:
                risk_entries = [r for r in per_testing if "attack_strategy" not in r]
                strategy_entries = [r for r in per_testing if "attack_strategy" in r]
                assert len(risk_entries) > 0, "per_testing_criteria_results should contain risk category entries"
                assert len(strategy_entries) > 0, "per_testing_criteria_results should contain attack strategy entries"
                for entry in per_testing:
                    assert "testing_criteria" in entry
                    assert "passed" in entry
                    assert "failed" in entry
                    assert isinstance(entry["passed"], int)
                    assert isinstance(entry["failed"], int)

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
            query = messages[-1]["content"]

            # Check if context was provided (for XPIA attacks)
            context_info = ""
            if context and "contexts" in context:
                context_info = f" [with {len(context['contexts'])} context items]"

            formatted_response = {
                "content": f"Response to: {query}{context_info}",
                "role": "assistant",
            }
            messages.append(formatted_response)
            return {
                "messages": messages,
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

        # At least one result should use the indirect_jailbreak technique
        techniques = [a["attack_technique"] for a in result.attack_details]
        assert "indirect_jailbreak" in techniques, f"Expected indirect_jailbreak in techniques, got: {techniques}"

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
        # TODO: Change to [AttackStrategy.Baseline] once PyRIT PR #1321 is merged
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

        # Should have results for at least 2 risk categories since we requested Violence and HateUnfairness
        assert (
            len(risk_categories_found) >= 2
        ), f"Expected results for at least 2 risk categories, got {len(risk_categories_found)}: {risk_categories_found}"

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
        # TODO: Change to [AttackStrategy.Baseline] once PyRIT PR #1321 is merged
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

        # Should have results from at least 2 techniques (Base64 + ROT13, possibly baseline)
        assert (
            len(techniques_found) >= 2
        ), f"Expected results for at least 2 techniques, got {len(techniques_found)}: {techniques_found}"

    # ==================== New target type tests ====================

    @pytest.fixture
    def deterministic_random(self):
        """Make random selection deterministic for recording stability.

        Patches random.sample and random.choice to always return the first N elements
        instead of random ones. This ensures the same objectives are selected during
        both recording and playback, preventing test proxy 404 mismatches.
        """

        def stable_sample(population, k, **kwargs):
            return list(population[:k])

        def stable_choice(seq):
            return seq[0]

        with patch("azure.ai.evaluation.red_team._red_team.random.sample", side_effect=stable_sample), patch(
            "azure.ai.evaluation.red_team._red_team.random.choice", side_effect=stable_choice
        ):
            yield

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_with_model_config_target(
        self, request, proj_scope, cred, sanitized_model_config, deterministic_random
    ):
        """
        Test Foundry execution with AzureOpenAIModelConfiguration target.

        Verifies that the Foundry path can accept and execute against a real
        model configuration target (not just callback functions). This validates
        the AzureAIModel target contract through the Foundry execution path.
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
                scan_name="test_foundry_model_config",
                attack_strategies=[AttackStrategy.Baseline, AttackStrategy.Base64],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        self._validate_attack_details(result.attack_details, expected_risk_category="hate_unfairness")

    @pytest.fixture
    def sanitized_model_config(self, model_config: AzureOpenAIModelConfiguration) -> AzureOpenAIModelConfiguration:
        """Fixture that sanitizes the Azure OpenAI model configuration for testing."""
        if model_config["azure_endpoint"] != "https://Sanitized.api.cognitive.microsoft.com":
            return model_config

        return AzureOpenAIModelConfiguration(
            **{**model_config, "azure_endpoint": "https://Sanitized.openai.azure.com/"},
        )

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_agent_target_callback(self, request, proj_scope, cred):
        """
        Test Foundry execution with an agent-flagged callback target.

        Verifies that the Foundry path correctly handles targets flagged as
        agent targets via the is_agent_target kwarg. This validates the
        AzureAIAgent contract path through the SDK, where the SDK signals
        to the service that the target is an agent (affecting risk category
        validation and objective generation).
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        async def agent_callback(
            messages: List[Dict],
            stream: bool = False,
            session_state: Any = None,
            context: Optional[Dict[str, Any]] = None,
        ) -> dict:
            query = messages[-1]["content"] if isinstance(messages, list) else messages["messages"][-1]["content"]
            formatted_response = {"content": f"Agent response to: {query}", "role": "assistant"}

            if isinstance(messages, list):
                messages.append(formatted_response)
                return {
                    "messages": messages,
                    "stream": stream,
                    "session_state": session_state,
                    "context": context,
                }
            else:
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
                target=agent_callback,
                scan_name="test_foundry_agent_callback",
                attack_strategies=[AttackStrategy.Baseline, AttackStrategy.Base64],
                timeout=4800,
                skip_upload=True,
                is_agent_target=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        self._validate_attack_details(result.attack_details, expected_risk_category="violence")

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_agent_target_with_tool_context(self, request, proj_scope, cred):
        """
        Test Foundry execution with an agent target that handles tool context.

        Verifies that IndirectJailbreak (XPIA) attacks correctly deliver context
        data to agent-flagged callback targets. This validates the tool injection
        contract where context["contexts"] is populated for XPIA attacks, simulating
        how ACA injects synthetic FunctionTool definitions for agent targets.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        async def agent_with_tools(
            messages: List[Dict],
            stream: bool = False,
            session_state: Any = None,
            context: Optional[Dict[str, Any]] = None,
        ) -> dict:
            query = messages[-1]["content"] if isinstance(messages, list) else messages["messages"][-1]["content"]

            # Simulate agent processing tool context
            tool_info = ""
            if context and "contexts" in context:
                tool_info = f" [processed {len(context['contexts'])} tool context(s)]"

            formatted_response = {
                "content": f"Agent with tools response: {query}{tool_info}",
                "role": "assistant",
            }

            if isinstance(messages, list):
                messages.append(formatted_response)
                return {
                    "messages": messages,
                    "stream": stream,
                    "session_state": session_state,
                    "context": context,
                }
            else:
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
                target=agent_with_tools,
                scan_name="test_foundry_agent_tools",
                attack_strategies=[AttackStrategy.IndirectJailbreak],
                timeout=4800,
                skip_upload=True,
                is_agent_target=True,
            )
        )
        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None

        # Verify at least some attacks used indirect_jailbreak technique
        techniques = [a["attack_technique"] for a in result.attack_details]
        assert "indirect_jailbreak" in techniques, f"Expected indirect_jailbreak in techniques, got: {techniques}"

        # Validate conversation structure for all attacks
        self._validate_attack_details(result.attack_details, expected_risk_category="violence")

    # ==================== New risk category tests (v2025_11_15) ====================

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_protected_material_category(self, request, proj_scope, cred):
        """
        Test Foundry execution with ProtectedMaterial risk category.

        Validates that the v2025_11_15 ProtectedMaterial risk category works
        through the Foundry path. This category tests for copyrighted or
        protected content generation.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        def simple_target(query: str) -> str:
            return "I follow content guidelines and cannot reproduce protected material."

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.ProtectedMaterial],
            num_objectives=1,
        )

        result = asyncio.run(
            red_team.scan(
                target=simple_target,
                scan_name="test_foundry_protected_material",
                attack_strategies=[AttackStrategy.Baseline, AttackStrategy.Base64],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        self._validate_attack_details(result.attack_details, expected_risk_category="protected_material")

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_code_vulnerability_category(self, request, proj_scope, cred):
        """
        Test Foundry execution with CodeVulnerability risk category.

        Validates that the v2025_11_15 CodeVulnerability risk category works
        through the Foundry path. This category tests for security vulnerability
        generation in code.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        def simple_target(query: str) -> str:
            return "I write secure code following best practices."

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.CodeVulnerability],
            num_objectives=1,
        )

        result = asyncio.run(
            red_team.scan(
                target=simple_target,
                scan_name="test_foundry_code_vuln",
                attack_strategies=[AttackStrategy.Baseline, AttackStrategy.Base64],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        self._validate_attack_details(result.attack_details, expected_risk_category="code_vulnerability")

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_task_adherence_category(self, request, proj_scope, cred):
        """
        Test Foundry execution with TaskAdherence risk category.

        Validates that the v2025_11_15 TaskAdherence risk category works
        through the Foundry path. This category tests for model divergence
        from intended task behavior.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        def simple_target(query: str) -> str:
            return "I stay on task and only answer questions within my scope."

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.TaskAdherence],
            num_objectives=1,
            custom_attack_seed_prompts=str(Path(SEEDS_DIR) / "task_adherence_seeds.json"),
        )

        result = asyncio.run(
            red_team.scan(
                target=simple_target,
                scan_name="test_foundry_task_adherence",
                attack_strategies=[AttackStrategy.Baseline, AttackStrategy.Base64],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        self._validate_attack_details(result.attack_details, expected_risk_category="task_adherence")

    # ==================== Agent-only risk category tests ====================

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_agent_sensitive_data_leakage(self, request, proj_scope, cred):
        """
        Test Foundry execution with SensitiveDataLeakage risk category on agent target.

        Validates that the agent-only SensitiveDataLeakage risk category works
        when is_agent_target=True. This risk category is restricted to agent
        targets per the SDK validation logic and tests PII/sensitive data
        exposure detection.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        async def agent_callback(
            messages: List[Dict],
            stream: bool = False,
            session_state: Any = None,
            context: Optional[Dict[str, Any]] = None,
        ) -> dict:
            query = messages[-1]["content"] if isinstance(messages, list) else messages["messages"][-1]["content"]
            formatted_response = {"content": f"I protect sensitive data: {query}", "role": "assistant"}

            if isinstance(messages, list):
                messages.append(formatted_response)
                return {
                    "messages": messages,
                    "stream": stream,
                    "session_state": session_state,
                    "context": context,
                }
            else:
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
            risk_categories=[RiskCategory.SensitiveDataLeakage],
            num_objectives=1,
            custom_attack_seed_prompts=str(Path(SEEDS_DIR) / "sensitive_data_leakage_seeds.json"),
        )

        result = asyncio.run(
            red_team.scan(
                target=agent_callback,
                scan_name="test_foundry_sensitive_data",
                attack_strategies=[AttackStrategy.Baseline, AttackStrategy.Base64],
                timeout=4800,
                skip_upload=True,
                is_agent_target=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        self._validate_attack_details(result.attack_details, expected_risk_category="sensitive_data_leakage")

    # ==================== Error path tests ====================

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_model_target_rejects_agent_only_risk_category(self, request, proj_scope, cred):
        """
        Test that SensitiveDataLeakage is rejected for non-agent targets.

        Validates the SDK contract enforcement: the SensitiveDataLeakage risk
        category is restricted to agent targets. When used with a non-agent
        target (is_agent_target=False or not set), the SDK should raise an
        EvaluationException before making any HTTP calls.
        """
        from azure.ai.evaluation._exceptions import EvaluationException

        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        def simple_target(query: str) -> str:
            return "Response"

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.SensitiveDataLeakage],
            num_objectives=1,
        )

        with pytest.raises(EvaluationException, match="only available for agent targets"):
            asyncio.run(
                red_team.scan(
                    target=simple_target,
                    scan_name="test_foundry_reject_agent_only",
                    attack_strategies=[AttackStrategy.Baseline],
                    timeout=4800,
                    skip_upload=True,
                )
            )

    # ==================== Multi-turn and Crescendo strategy tests ====================

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_multi_turn_attack(self, request, proj_scope, cred):
        """
        Test Foundry execution with MultiTurn attack strategy.

        Validates that the Foundry path can execute multi-turn attacks which
        involve multiple conversation exchanges between the attacker and target.
        Multi-turn attacks spread harmful intent across conversation turns.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        def defensive_target(query: str) -> str:
            return "Sorry, I cannot assist with that request."

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.Violence],
            num_objectives=1,
        )

        result = asyncio.run(
            red_team.scan(
                target=defensive_target,
                scan_name="test_foundry_multi_turn",
                attack_strategies=[AttackStrategy.MultiTurn],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None
        assert len(result.attack_details) > 0

        for attack in result.attack_details:
            conversation = attack["conversation"]
            if attack["attack_technique"] == "multi_turn":
                # Multi-turn attacks attempt multiple turns but may terminate early
                assert len(conversation) >= 2, "Multi-turn attack should have at least 2 messages"
            else:
                assert len(conversation) >= 2

            # Validate role alternation
            for i in range(len(conversation)):
                expected_role = "user" if i % 2 == 0 else "assistant"
                assert (
                    conversation[i]["role"] == expected_role
                ), f"Message {i} should have role '{expected_role}', got '{conversation[i]['role']}'"

    @pytest.mark.azuretest
    @pytest.mark.parametrize(
        ("proj_scope", "cred"),
        (("project_scope_onedp", "azure_cred_onedp"),),
    )
    def test_foundry_crescendo_attack(self, request, proj_scope, cred):
        """
        Test Foundry execution with Crescendo attack strategy.

        Validates that the Foundry path can execute crescendo attacks which
        gradually escalate the conversation to try to elicit harmful responses.
        Crescendo attacks are classified as 'Difficult' complexity and produce
        multi-turn conversations.
        """
        azure_cred = request.getfixturevalue(cred)
        project_scope = request.getfixturevalue(proj_scope)

        def defensive_target(query: str) -> str:
            return "Sorry, I cannot assist with that request."

        red_team = RedTeam(
            azure_ai_project=project_scope,
            credential=azure_cred,
            risk_categories=[RiskCategory.Violence],
            num_objectives=1,
        )

        result = asyncio.run(
            red_team.scan(
                target=defensive_target,
                scan_name="test_foundry_crescendo",
                attack_strategies=[AttackStrategy.Crescendo],
                timeout=4800,
                skip_upload=True,
            )
        )

        assert isinstance(result, RedTeamResult)
        assert result.attack_details is not None
        assert len(result.attack_details) > 0

        for attack in result.attack_details:
            conversation = attack["conversation"]
            if attack["attack_technique"] == "crescendo":
                # Crescendo attacks produce multi-turn conversations (typically 20 messages / 10 turns)
                assert len(conversation) >= 2, "Crescendo attack should produce multi-turn conversation"
            else:
                assert len(conversation) >= 2

            # Validate role alternation
            for i in range(len(conversation)):
                expected_role = "user" if i % 2 == 0 else "assistant"
                assert (
                    conversation[i]["role"] == expected_role
                ), f"Message {i} should have role '{expected_role}', got '{conversation[i]['role']}'"
