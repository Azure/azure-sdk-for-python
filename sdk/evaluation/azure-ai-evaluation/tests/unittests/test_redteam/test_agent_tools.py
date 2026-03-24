# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Unit tests for _agent_tools module (RedTeamToolProvider and get_red_team_tools)."""

import sys
import importlib
import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock

# ---------------------------------------------------------------------------
# Module path constants
# ---------------------------------------------------------------------------
_TOOLS_MODULE_PATH = "azure.ai.evaluation.red_team._agent._agent_tools"
_UTILS_MODULE_PATH = "azure.ai.evaluation.red_team._agent._agent_utils"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_pyrit_shims():
    """Inject any missing pyrit.prompt_converter names so that _agent_utils
    can be imported regardless of the installed pyrit version."""
    _PYRIT_CONVERTER_NAMES = [
        "MathPromptConverter",
        "Base64Converter",
        "FlipConverter",
        "MorseConverter",
        "AnsiAttackConverter",
        "AsciiArtConverter",
        "AsciiSmugglerConverter",
        "AtbashConverter",
        "BinaryConverter",
        "CaesarConverter",
        "CharacterSpaceConverter",
        "CharSwapGenerator",
        "DiacriticConverter",
        "LeetspeakConverter",
        "UrlConverter",
        "UnicodeSubstitutionConverter",
        "UnicodeConfusableConverter",
        "SuffixAppendConverter",
        "StringJoinConverter",
        "ROT13Converter",
    ]
    try:
        import pyrit.prompt_converter as pc
    except ImportError:
        pc = MagicMock()
        sys.modules["pyrit"] = MagicMock()
        sys.modules["pyrit.prompt_converter"] = pc
        return

    for name in _PYRIT_CONVERTER_NAMES:
        if not hasattr(pc, name):
            setattr(pc, name, MagicMock())


_ensure_pyrit_shims()


# ---------------------------------------------------------------------------
# Now we can safely import the modules under test
# ---------------------------------------------------------------------------
# Force-reimport to pick up any shims
sys.modules.pop(_UTILS_MODULE_PATH, None)
sys.modules.pop(_TOOLS_MODULE_PATH, None)

from azure.ai.evaluation.red_team._attack_objective_generator import RiskCategory  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_credential():
    """Return a mock TokenCredential."""
    cred = MagicMock()
    cred.get_token = MagicMock(return_value=MagicMock(token="fake-token"))
    return cred


@pytest.fixture
def mock_token_manager():
    """Return a mock ManagedIdentityAPITokenManager."""
    mgr = MagicMock()
    mgr.get_aad_credential.return_value = "mock-aad-credential"
    return mgr


@pytest.fixture
def mock_rai_client():
    """Return a mock GeneratedRAIClient with async methods."""
    client = MagicMock()
    client.get_attack_objectives = AsyncMock(
        return_value=[
            {"messages": [{"content": "harmful prompt 1", "role": "user"}]},
            {"messages": [{"content": "harmful prompt 2", "role": "user"}]},
        ]
    )
    client.get_jailbreak_prefixes = AsyncMock(
        return_value=[
            "JAILBREAK_PREFIX_A",
            "JAILBREAK_PREFIX_B",
        ]
    )
    return client


@pytest.fixture
def mock_agent_utils():
    """Return a mock AgentUtils."""
    utils = MagicMock()
    utils.get_list_of_supported_converters.return_value = [
        "base64_converter",
        "morse_converter",
        "binary_converter",
        "rot13_converter",
    ]
    utils.convert_text = AsyncMock(return_value="converted_text")
    return utils


@pytest.fixture
def provider(mock_credential, mock_token_manager, mock_rai_client, mock_agent_utils):
    """Create a RedTeamToolProvider with all dependencies mocked."""
    with patch(
        f"{_TOOLS_MODULE_PATH}.ManagedIdentityAPITokenManager",
        return_value=mock_token_manager,
    ), patch(
        f"{_TOOLS_MODULE_PATH}.GeneratedRAIClient",
        return_value=mock_rai_client,
    ), patch(
        f"{_TOOLS_MODULE_PATH}.AgentUtils",
        return_value=mock_agent_utils,
    ):
        from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

        p = RedTeamToolProvider(
            azure_ai_project_endpoint="https://test.services.ai.azure.com/api/projects/test-project",
            credential=mock_credential,
            application_scenario="test scenario",
        )
    # Ensure the mocks are wired up
    p.generated_rai_client = mock_rai_client
    p.converter_utils = mock_agent_utils
    p.token_manager = mock_token_manager
    return p


# ---------------------------------------------------------------------------
# __init__ tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestRedTeamToolProviderInit:
    """Tests for RedTeamToolProvider.__init__."""

    def test_stores_endpoint(self, provider):
        assert provider.azure_ai_project_endpoint == "https://test.services.ai.azure.com/api/projects/test-project"

    def test_stores_credential(self, provider, mock_credential):
        assert provider.credential is mock_credential

    def test_stores_application_scenario(self, provider):
        assert provider.application_scenario == "test scenario"

    def test_empty_cache_on_init(self, provider):
        assert provider._attack_objectives_cache == {}

    def test_empty_fetched_prompts_on_init(self, provider):
        assert provider._fetched_prompts == {}

    def test_token_manager_created(self, provider, mock_token_manager):
        assert provider.token_manager is mock_token_manager

    def test_rai_client_created(self, provider, mock_rai_client):
        assert provider.generated_rai_client is mock_rai_client

    def test_converter_utils_created(self, provider, mock_agent_utils):
        assert provider.converter_utils is mock_agent_utils

    def test_init_without_application_scenario(self, mock_credential):
        """application_scenario defaults to None."""
        with patch(f"{_TOOLS_MODULE_PATH}.ManagedIdentityAPITokenManager", return_value=MagicMock()), patch(
            f"{_TOOLS_MODULE_PATH}.GeneratedRAIClient", return_value=MagicMock()
        ), patch(f"{_TOOLS_MODULE_PATH}.AgentUtils", return_value=MagicMock()):
            from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

            p = RedTeamToolProvider(
                azure_ai_project_endpoint="https://x.ai.azure.com",
                credential=mock_credential,
            )
        assert p.application_scenario is None


# ---------------------------------------------------------------------------
# get_available_strategies tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestGetAvailableStrategies:
    """Tests for get_available_strategies."""

    def test_returns_list(self, provider):
        result = provider.get_available_strategies()
        assert isinstance(result, list)

    def test_delegates_to_converter_utils(self, provider, mock_agent_utils):
        result = provider.get_available_strategies()
        mock_agent_utils.get_list_of_supported_converters.assert_called_once()
        assert result == ["base64_converter", "morse_converter", "binary_converter", "rot13_converter"]


# ---------------------------------------------------------------------------
# apply_strategy_to_prompt tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestApplyStrategyToPrompt:

    @pytest.mark.asyncio
    async def test_delegates_to_convert_text(self, provider, mock_agent_utils):
        result = await provider.apply_strategy_to_prompt("hello", "morse_converter")
        mock_agent_utils.convert_text.assert_awaited_once_with(converter_name="morse_converter", text="hello")
        assert result == "converted_text"

    @pytest.mark.asyncio
    async def test_passes_strategy_and_prompt(self, provider, mock_agent_utils):
        await provider.apply_strategy_to_prompt("test prompt", "base64_converter")
        mock_agent_utils.convert_text.assert_awaited_once_with(converter_name="base64_converter", text="test prompt")


# ---------------------------------------------------------------------------
# _parse_risk_category tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestParseRiskCategory:
    """Tests for the static _parse_risk_category method."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("hate", RiskCategory.HateUnfairness),
            ("unfairness", RiskCategory.HateUnfairness),
            ("hate_unfairness", RiskCategory.HateUnfairness),
            ("bias", RiskCategory.HateUnfairness),
            ("discrimination", RiskCategory.HateUnfairness),
            ("prejudice", RiskCategory.HateUnfairness),
        ],
    )
    def test_hate_unfairness_keywords(self, text, expected):
        from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

        assert RedTeamToolProvider._parse_risk_category(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("violence", RiskCategory.Violence),
            ("harm", RiskCategory.Violence),
            ("physical", RiskCategory.Violence),
            ("weapon", RiskCategory.Violence),
            ("dangerous", RiskCategory.Violence),
        ],
    )
    def test_violence_keywords(self, text, expected):
        from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

        assert RedTeamToolProvider._parse_risk_category(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("sexual", RiskCategory.Sexual),
            ("sex", RiskCategory.Sexual),
            ("adult", RiskCategory.Sexual),
            ("explicit", RiskCategory.Sexual),
        ],
    )
    def test_sexual_keywords(self, text, expected):
        from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

        assert RedTeamToolProvider._parse_risk_category(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("self_harm", RiskCategory.SelfHarm),
            ("selfharm", RiskCategory.SelfHarm),
            ("self-harm", RiskCategory.SelfHarm),
            ("suicide", RiskCategory.SelfHarm),
            ("self-injury", RiskCategory.SelfHarm),
        ],
    )
    def test_self_harm_keywords(self, text, expected):
        from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

        assert RedTeamToolProvider._parse_risk_category(text) == expected

    def test_case_insensitive(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

        assert RedTeamToolProvider._parse_risk_category("HATE") == RiskCategory.HateUnfairness
        assert RedTeamToolProvider._parse_risk_category("Violence") == RiskCategory.Violence
        assert RedTeamToolProvider._parse_risk_category("SEXUAL") == RiskCategory.Sexual

    def test_whitespace_handling(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

        assert RedTeamToolProvider._parse_risk_category("  hate  ") == RiskCategory.HateUnfairness

    def test_unknown_category_returns_none(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

        assert RedTeamToolProvider._parse_risk_category("totally_unknown") is None

    def test_empty_string_returns_none(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

        assert RedTeamToolProvider._parse_risk_category("") is None

    def test_category_value_fallback(self):
        """If no keyword matches, but an exact RiskCategory.value appears in text."""
        from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

        # "protected_material" is not in the keyword_map but is a RiskCategory.value
        result = RedTeamToolProvider._parse_risk_category("protected_material")
        assert result == RiskCategory.ProtectedMaterial

    def test_substring_match_in_longer_text(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

        assert RedTeamToolProvider._parse_risk_category("something about violence here") == RiskCategory.Violence


# ---------------------------------------------------------------------------
# _get_attack_objectives tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestGetAttackObjectives:

    @pytest.mark.asyncio
    async def test_fetches_objectives_baseline(self, provider, mock_rai_client):
        result = await provider._get_attack_objectives(RiskCategory.Violence, strategy="baseline")
        mock_rai_client.get_attack_objectives.assert_awaited_once_with(
            risk_category="violence",
            application_scenario="test scenario",
            strategy=None,
        )
        assert result == ["harmful prompt 1", "harmful prompt 2"]

    @pytest.mark.asyncio
    async def test_fetches_objectives_tense_strategy(self, provider, mock_rai_client):
        await provider._get_attack_objectives(RiskCategory.Violence, strategy="tense")
        mock_rai_client.get_attack_objectives.assert_awaited_once_with(
            risk_category="violence",
            application_scenario="test scenario",
            strategy="tense",
        )

    @pytest.mark.asyncio
    async def test_fetches_objectives_past_tense_strategy(self, provider, mock_rai_client):
        """Strategies containing 'tense' (like 'past_tense') use the tense dataset."""
        await provider._get_attack_objectives(RiskCategory.Violence, strategy="past_tense")
        mock_rai_client.get_attack_objectives.assert_awaited_once_with(
            risk_category="violence",
            application_scenario="test scenario",
            strategy="tense",
        )

    @pytest.mark.asyncio
    async def test_jailbreak_strategy_prepends_prefix(self, provider, mock_rai_client):
        result = await provider._get_attack_objectives(RiskCategory.Violence, strategy="jailbreak")
        # Should have called get_jailbreak_prefixes
        mock_rai_client.get_jailbreak_prefixes.assert_awaited_once()
        # Each prompt should be prefixed with one of the jailbreak prefixes
        for prompt in result:
            assert prompt.startswith("JAILBREAK_PREFIX_A") or prompt.startswith("JAILBREAK_PREFIX_B")

    @pytest.mark.asyncio
    async def test_jailbreak_with_empty_messages(self, provider, mock_rai_client):
        """Objectives with empty messages should not crash during jailbreak prefix application."""
        mock_rai_client.get_attack_objectives.return_value = [
            {"messages": []},
            {"messages": [{"content": "test", "role": "user"}]},
        ]
        result = await provider._get_attack_objectives(RiskCategory.Violence, strategy="jailbreak")
        # Should only return the one with content
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_returns_empty_on_api_error(self, provider, mock_rai_client):
        mock_rai_client.get_attack_objectives.side_effect = Exception("API error")
        result = await provider._get_attack_objectives(RiskCategory.Violence)
        assert result == []

    @pytest.mark.asyncio
    async def test_empty_objectives_response(self, provider, mock_rai_client):
        mock_rai_client.get_attack_objectives.return_value = []
        result = await provider._get_attack_objectives(RiskCategory.Violence)
        assert result == []

    @pytest.mark.asyncio
    async def test_objectives_without_messages_key(self, provider, mock_rai_client):
        """Objectives missing 'messages' key should be skipped."""
        mock_rai_client.get_attack_objectives.return_value = [
            {"no_messages": "here"},
            {"messages": [{"content": "valid", "role": "user"}]},
        ]
        result = await provider._get_attack_objectives(RiskCategory.Violence)
        assert result == ["valid"]

    @pytest.mark.asyncio
    async def test_objectives_with_non_dict_message(self, provider, mock_rai_client):
        """Messages that are not dicts should be skipped."""
        mock_rai_client.get_attack_objectives.return_value = [
            {"messages": ["just a string"]},
            {"messages": [{"content": "valid", "role": "user"}]},
        ]
        result = await provider._get_attack_objectives(RiskCategory.Violence)
        assert result == ["valid"]

    @pytest.mark.asyncio
    async def test_no_application_scenario_sends_empty_string(self, provider, mock_rai_client):
        provider.application_scenario = None
        await provider._get_attack_objectives(RiskCategory.Violence)
        mock_rai_client.get_attack_objectives.assert_awaited_once_with(
            risk_category="violence",
            application_scenario="",
            strategy=None,
        )


# ---------------------------------------------------------------------------
# fetch_harmful_prompt tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestFetchHarmfulPrompt:

    @pytest.mark.asyncio
    async def test_success_baseline(self, provider):
        result = await provider.fetch_harmful_prompt("violence")
        assert result["status"] == "success"
        assert result["risk_category"] == "violence"
        assert result["strategy"] == "baseline"
        assert "prompt" in result
        assert "prompt_id" in result
        assert result["prompt_id"].startswith("prompt_")
        assert "available_strategies" in result

    @pytest.mark.asyncio
    async def test_invalid_risk_category(self, provider):
        result = await provider.fetch_harmful_prompt("totally_invalid_xyz")
        assert result["status"] == "error"
        assert "Could not parse risk category" in result["message"]

    @pytest.mark.asyncio
    async def test_caching_avoids_repeated_api_calls(self, provider, mock_rai_client):
        """Second call with same category+strategy should use cache."""
        await provider.fetch_harmful_prompt("violence", strategy="baseline")
        await provider.fetch_harmful_prompt("violence", strategy="baseline")
        # get_attack_objectives should be called only once (via _get_attack_objectives)
        assert mock_rai_client.get_attack_objectives.await_count == 1

    @pytest.mark.asyncio
    async def test_different_strategies_separate_cache(self, provider, mock_rai_client):
        """Different strategies should not share cache entries."""
        await provider.fetch_harmful_prompt("violence", strategy="baseline")
        await provider.fetch_harmful_prompt("violence", strategy="tense")
        assert mock_rai_client.get_attack_objectives.await_count == 2

    @pytest.mark.asyncio
    async def test_prompt_stored_for_later_conversion(self, provider):
        result = await provider.fetch_harmful_prompt("violence")
        prompt_id = result["prompt_id"]
        assert prompt_id in provider._fetched_prompts
        assert provider._fetched_prompts[prompt_id] == result["prompt"]

    @pytest.mark.asyncio
    async def test_empty_objectives_returns_error(self, provider, mock_rai_client):
        mock_rai_client.get_attack_objectives.return_value = []
        # Clear cache so it re-fetches
        provider._attack_objectives_cache.clear()
        result = await provider.fetch_harmful_prompt("violence")
        assert result["status"] == "error"
        assert "No harmful prompts found" in result["message"]

    @pytest.mark.asyncio
    async def test_with_conversion_strategy(self, provider, mock_agent_utils):
        result = await provider.fetch_harmful_prompt("violence", convert_with_strategy="morse_converter")
        assert result["status"] == "success"
        assert result["conversion_strategy"] == "morse_converter"
        assert result["converted_prompt"] == "converted_text"
        assert "original_prompt" in result

    @pytest.mark.asyncio
    async def test_with_invalid_conversion_strategy(self, provider):
        result = await provider.fetch_harmful_prompt("violence", convert_with_strategy="nonexistent_strategy")
        assert result["status"] == "error"
        assert "Unsupported strategy" in result["message"]

    @pytest.mark.asyncio
    async def test_conversion_error_returns_error(self, provider, mock_agent_utils):
        mock_agent_utils.convert_text.side_effect = Exception("conversion failed")
        result = await provider.fetch_harmful_prompt("violence", convert_with_strategy="morse_converter")
        assert result["status"] == "error"
        assert "Error converting prompt" in result["message"]

    @pytest.mark.asyncio
    async def test_api_error_returns_error(self, provider, mock_rai_client):
        provider._attack_objectives_cache.clear()
        mock_rai_client.get_attack_objectives.side_effect = Exception("service down")
        result = await provider.fetch_harmful_prompt("violence")
        assert result["status"] == "error"
        assert "No harmful prompts found" in result["message"]


# ---------------------------------------------------------------------------
# convert_prompt tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestConvertPrompt:

    @pytest.mark.asyncio
    async def test_convert_raw_prompt(self, provider, mock_agent_utils):
        result = await provider.convert_prompt("hello world", "morse_converter")
        assert result["status"] == "success"
        assert result["strategy"] == "morse_converter"
        assert result["original_prompt"] == "hello world"
        assert result["converted_prompt"] == "converted_text"

    @pytest.mark.asyncio
    async def test_convert_by_prompt_id(self, provider, mock_agent_utils):
        """If prompt_or_id matches a stored prompt ID, use the stored prompt."""
        provider._fetched_prompts["prompt_abc123"] = "stored harmful prompt"
        result = await provider.convert_prompt("prompt_abc123", "base64_converter")
        assert result["status"] == "success"
        assert result["original_prompt"] == "stored harmful prompt"
        mock_agent_utils.convert_text.assert_awaited_once_with(
            converter_name="base64_converter", text="stored harmful prompt"
        )

    @pytest.mark.asyncio
    async def test_unknown_id_treated_as_raw_prompt(self, provider, mock_agent_utils):
        """If prompt_or_id is not a known ID, treat it as the raw prompt text."""
        result = await provider.convert_prompt("prompt_nonexistent", "morse_converter")
        assert result["original_prompt"] == "prompt_nonexistent"

    @pytest.mark.asyncio
    async def test_invalid_strategy(self, provider):
        result = await provider.convert_prompt("hello", "invalid_strategy")
        assert result["status"] == "error"
        assert "Unsupported strategy" in result["message"]
        assert "Available strategies" in result["message"]

    @pytest.mark.asyncio
    async def test_converter_result_with_text_attr(self, provider, mock_agent_utils):
        """Handle ConverterResult objects that have a .text attribute."""
        converter_result = MagicMock()
        converter_result.text = "converted_via_text_attr"
        # Make hasattr(result, "text") return True
        mock_agent_utils.convert_text.return_value = converter_result
        result = await provider.convert_prompt("hello", "morse_converter")
        assert result["converted_prompt"] == "converted_via_text_attr"

    @pytest.mark.asyncio
    async def test_string_result_used_directly(self, provider, mock_agent_utils):
        """Plain string results are used directly."""
        mock_agent_utils.convert_text.return_value = "plain_string_result"
        result = await provider.convert_prompt("hello", "morse_converter")
        assert result["converted_prompt"] == "plain_string_result"

    @pytest.mark.asyncio
    async def test_conversion_exception(self, provider, mock_agent_utils):
        mock_agent_utils.convert_text.side_effect = Exception("boom")
        result = await provider.convert_prompt("hello", "morse_converter")
        assert result["status"] == "error"
        assert "An error occurred" in result["message"]


# ---------------------------------------------------------------------------
# red_team tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestRedTeam:

    @pytest.mark.asyncio
    async def test_success_without_strategy(self, provider):
        result = await provider.red_team("violence")
        assert result["status"] == "success"
        assert result["risk_category"] == "violence"
        assert "prompt" in result
        assert "prompt_id" in result
        assert "available_strategies" in result

    @pytest.mark.asyncio
    async def test_success_with_strategy(self, provider, mock_agent_utils):
        result = await provider.red_team("violence", strategy="morse_converter")
        assert result["status"] == "success"
        assert result["risk_category"] == "violence"
        assert result["strategy"] == "morse_converter"
        assert "converted_prompt" in result
        assert "original_prompt" in result

    @pytest.mark.asyncio
    async def test_invalid_category(self, provider):
        result = await provider.red_team("nonexistent_category_xyz")
        assert result["status"] == "error"
        assert "Could not parse risk category" in result["message"]

    @pytest.mark.asyncio
    async def test_invalid_strategy(self, provider):
        result = await provider.red_team("violence", strategy="nonexistent_strat")
        assert result["status"] == "error"
        assert "Unsupported strategy" in result["message"]

    @pytest.mark.asyncio
    async def test_fetch_failure_propagated(self, provider, mock_rai_client):
        """If fetch_harmful_prompt fails, red_team propagates the error."""
        provider._attack_objectives_cache.clear()
        mock_rai_client.get_attack_objectives.return_value = []
        result = await provider.red_team("violence")
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_conversion_error_returns_error(self, provider, mock_agent_utils):
        mock_agent_utils.convert_text.side_effect = Exception("conversion error")
        result = await provider.red_team("violence", strategy="morse_converter")
        assert result["status"] == "error"
        assert "Error converting prompt" in result["message"]

    @pytest.mark.asyncio
    async def test_uses_baseline_for_fetch(self, provider, mock_rai_client):
        """red_team always uses 'baseline' as the fetch strategy."""
        await provider.red_team("violence", strategy="morse_converter")
        # Check that get_attack_objectives was called with strategy=None (baseline path)
        mock_rai_client.get_attack_objectives.assert_awaited_with(
            risk_category="violence",
            application_scenario="test scenario",
            strategy=None,
        )

    @pytest.mark.asyncio
    async def test_outer_exception_caught(self, provider):
        """An unexpected exception in red_team is caught and returned."""
        with patch.object(provider, "_parse_risk_category", side_effect=RuntimeError("unexpected")):
            result = await provider.red_team("violence")
        assert result["status"] == "error"
        assert "An error occurred" in result["message"]

    @pytest.mark.asyncio
    async def test_none_strategy_returns_prompt_without_conversion(self, provider):
        result = await provider.red_team("hate", strategy=None)
        assert result["status"] == "success"
        assert "converted_prompt" not in result
        assert "prompt" in result


# ---------------------------------------------------------------------------
# get_red_team_tools tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestGetRedTeamTools:

    def test_returns_list(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import get_red_team_tools

        result = get_red_team_tools()
        assert isinstance(result, list)

    def test_contains_three_tools(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import get_red_team_tools

        result = get_red_team_tools()
        assert len(result) == 3

    def test_tool_names(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import get_red_team_tools

        result = get_red_team_tools()
        task_names = [t["task"] for t in result]
        assert "red_team" in task_names
        assert "fetch_harmful_prompt" in task_names
        assert "convert_prompt" in task_names

    def test_each_tool_has_description(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import get_red_team_tools

        for tool in get_red_team_tools():
            assert "description" in tool
            assert isinstance(tool["description"], str)
            assert len(tool["description"]) > 0

    def test_each_tool_has_parameters(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import get_red_team_tools

        for tool in get_red_team_tools():
            assert "parameters" in tool
            assert isinstance(tool["parameters"], dict)

    def test_red_team_tool_parameters(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import get_red_team_tools

        tools = {t["task"]: t for t in get_red_team_tools()}
        rt = tools["red_team"]
        assert "category" in rt["parameters"]
        assert "strategy" in rt["parameters"]
        assert rt["parameters"]["strategy"]["default"] is None

    def test_fetch_harmful_prompt_tool_parameters(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import get_red_team_tools

        tools = {t["task"]: t for t in get_red_team_tools()}
        fhp = tools["fetch_harmful_prompt"]
        assert "risk_category_text" in fhp["parameters"]
        assert "strategy" in fhp["parameters"]
        assert "convert_with_strategy" in fhp["parameters"]
        assert fhp["parameters"]["strategy"]["default"] == "baseline"

    def test_convert_prompt_tool_parameters(self):
        from azure.ai.evaluation.red_team._agent._agent_tools import get_red_team_tools

        tools = {t["task"]: t for t in get_red_team_tools()}
        cp = tools["convert_prompt"]
        assert "prompt_or_id" in cp["parameters"]
        assert "strategy" in cp["parameters"]


# ---------------------------------------------------------------------------
# Additional edge case tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestEdgeCases:

    @pytest.mark.asyncio
    async def test_jailbreak_random_prefix_selection(self, provider, mock_rai_client):
        """Verify jailbreak uses random.choice on the prefixes list."""
        with patch("azure.ai.evaluation.red_team._agent._agent_tools.random") as mock_random:
            mock_random.choice.return_value = "CHOSEN_PREFIX"
            result = await provider._get_attack_objectives(RiskCategory.Violence, strategy="jailbreak")
            # random.choice should have been called for each objective with content
            assert mock_random.choice.call_count >= 1

    @pytest.mark.asyncio
    async def test_fetch_prompt_random_selection(self, provider, mock_rai_client):
        """fetch_harmful_prompt uses random.choice to select an objective."""
        provider._attack_objectives_cache.clear()
        with patch("azure.ai.evaluation.red_team._agent._agent_tools.random") as mock_random:
            mock_random.choice.return_value = "selected_prompt"
            result = await provider.fetch_harmful_prompt("violence")
            mock_random.choice.assert_called()
            assert result["prompt"] == "selected_prompt"

    @pytest.mark.asyncio
    async def test_fetch_prompt_uuid_generation(self, provider):
        """Each fetched prompt gets a unique prompt_id."""
        result1 = await provider.fetch_harmful_prompt("violence")
        result2 = await provider.fetch_harmful_prompt("violence")
        assert result1["prompt_id"] != result2["prompt_id"]
        assert result1["prompt_id"].startswith("prompt_")
        assert result2["prompt_id"].startswith("prompt_")

    @pytest.mark.asyncio
    async def test_multiple_risk_categories_independent_cache(self, provider, mock_rai_client):
        """Different risk categories have separate cache entries."""
        await provider.fetch_harmful_prompt("violence")
        await provider.fetch_harmful_prompt("hate")
        assert ("violence", "baseline") in provider._attack_objectives_cache
        assert ("hate_unfairness", "baseline") in provider._attack_objectives_cache

    def test_parse_risk_category_is_static_method(self):
        """_parse_risk_category can be called without an instance."""
        from azure.ai.evaluation.red_team._agent._agent_tools import RedTeamToolProvider

        result = RedTeamToolProvider._parse_risk_category("violence")
        assert result == RiskCategory.Violence

    @pytest.mark.asyncio
    async def test_objectives_message_missing_content_key(self, provider, mock_rai_client):
        """Messages without 'content' key should be skipped."""
        mock_rai_client.get_attack_objectives.return_value = [
            {"messages": [{"role": "user"}]},  # no content
            {"messages": [{"content": "valid prompt", "role": "user"}]},
        ]
        provider._attack_objectives_cache.clear()
        result = await provider._get_attack_objectives(RiskCategory.Violence)
        assert result == ["valid prompt"]
