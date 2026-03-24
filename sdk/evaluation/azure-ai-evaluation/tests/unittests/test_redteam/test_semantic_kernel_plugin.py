"""
Unit tests for _semantic_kernel_plugin module (RedTeamPlugin class).

The source module imports ``kernel_function`` from ``semantic_kernel.functions``
and ``RedTeamToolProvider`` from the agent tools module.  Both are shimmed at the
sys.modules level *before* importing the plugin so we avoid the heavy transitive
import chain (pyrit converters, numpy, etc.) that would otherwise hang or fail.
"""

import sys
import json
import importlib
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MODULE_PATH = "azure.ai.evaluation.red_team._agent._semantic_kernel_plugin"
_AGENT_TOOLS_MODULE = "azure.ai.evaluation.red_team._agent._agent_tools"


# ---------------------------------------------------------------------------
# Helpers — shim heavy dependencies before import
# ---------------------------------------------------------------------------

_injected_modules = []


def _inject_shims():
    """Inject shims for ``semantic_kernel`` and the agent-tools module so
    the plugin can be imported without pulling in pyrit/numpy.
    Returns list of module keys that were injected."""
    injected = []

    # 1. semantic_kernel shim
    if "semantic_kernel" not in sys.modules:
        sk_mod = MagicMock()
        sk_mod.functions.kernel_function = lambda **kwargs: (lambda fn: fn)
        sys.modules["semantic_kernel"] = sk_mod
        sys.modules["semantic_kernel.functions"] = sk_mod.functions
        injected.extend(["semantic_kernel", "semantic_kernel.functions"])

    # 2. Agent-tools module shim (avoids pyrit import chain)
    if _AGENT_TOOLS_MODULE not in sys.modules:
        tools_mod = MagicMock()
        # Provide a real class-like mock for RedTeamToolProvider so that
        # isinstance checks and attribute access work.
        tools_mod.RedTeamToolProvider = MagicMock
        sys.modules[_AGENT_TOOLS_MODULE] = tools_mod
        injected.append(_AGENT_TOOLS_MODULE)

    return injected


def _import_plugin_module():
    """Import (or reimport) the _semantic_kernel_plugin module."""
    sys.modules.pop(_MODULE_PATH, None)
    return importlib.import_module(_MODULE_PATH)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _patched_sk():
    """Module-scoped: shim dependencies and load the plugin module."""
    injected = _inject_shims()
    mod = _import_plugin_module()
    yield mod
    for key in injected:
        sys.modules.pop(key, None)
    sys.modules.pop(_MODULE_PATH, None)


@pytest.fixture
def mock_tool_provider():
    """Create a mock RedTeamToolProvider with all async methods stubbed."""
    provider = MagicMock()
    provider._fetched_prompts = {}

    provider.fetch_harmful_prompt = AsyncMock(
        return_value={
            "status": "success",
            "prompt_id": "prompt-001",
            "prompt": "test harmful prompt",
            "risk_category": "violence",
        }
    )
    provider.convert_prompt = AsyncMock(
        return_value={
            "status": "success",
            "original_prompt": "test harmful prompt",
            "converted_prompt": "converted prompt text",
        }
    )
    provider.red_team = AsyncMock(
        return_value={
            "status": "success",
            "prompt_id": "prompt-002",
            "prompt": "unified prompt text",
            "risk_category": "hate_unfairness",
        }
    )
    provider.get_available_strategies = MagicMock(return_value=["baseline", "jailbreak", "base64", "rot13"])
    return provider


@pytest.fixture
def plugin(_patched_sk, mock_tool_provider):
    """Create a RedTeamPlugin with mocked credential and tool provider."""
    with patch.object(_patched_sk, "DefaultAzureCredential", return_value=MagicMock()), patch.object(
        _patched_sk, "RedTeamToolProvider", return_value=mock_tool_provider
    ):
        p = _patched_sk.RedTeamPlugin(
            azure_ai_project_endpoint="https://test.services.ai.azure.com/api/projects/test-project",
            target_func=lambda x: f"response to: {x}",
            application_scenario="test scenario",
        )
    # Ensure the mock provider is used
    p.tool_provider = mock_tool_provider
    return p


@pytest.fixture
def plugin_no_target(_patched_sk, mock_tool_provider):
    """Create a RedTeamPlugin with no target function."""
    with patch.object(_patched_sk, "DefaultAzureCredential", return_value=MagicMock()), patch.object(
        _patched_sk, "RedTeamToolProvider", return_value=mock_tool_provider
    ):
        p = _patched_sk.RedTeamPlugin(
            azure_ai_project_endpoint="https://test.services.ai.azure.com/api/projects/test-project",
        )
    p.tool_provider = mock_tool_provider
    return p


# ---------------------------------------------------------------------------
# __init__ tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestRedTeamPluginInit:
    """Verify RedTeamPlugin.__init__ behaviour."""

    def test_init_creates_credential(self, _patched_sk):
        """Init should create a DefaultAzureCredential."""
        mock_cred = MagicMock()
        with patch.object(_patched_sk, "DefaultAzureCredential", return_value=mock_cred) as cred_cls, patch.object(
            _patched_sk, "RedTeamToolProvider", return_value=MagicMock()
        ):
            p = _patched_sk.RedTeamPlugin(
                azure_ai_project_endpoint="https://test.ai.azure.com/api/projects/p",
            )
            cred_cls.assert_called_once()
            assert p.credential is mock_cred

    def test_init_creates_tool_provider_with_correct_args(self, _patched_sk):
        """Init should pass endpoint, credential, and scenario to RedTeamToolProvider."""
        mock_cred = MagicMock()
        with patch.object(_patched_sk, "DefaultAzureCredential", return_value=mock_cred), patch.object(
            _patched_sk, "RedTeamToolProvider", return_value=MagicMock()
        ) as provider_cls:
            _patched_sk.RedTeamPlugin(
                azure_ai_project_endpoint="https://endpoint.test",
                application_scenario="my scenario",
            )
            provider_cls.assert_called_once_with(
                azure_ai_project_endpoint="https://endpoint.test",
                credential=mock_cred,
                application_scenario="my scenario",
            )

    def test_init_stores_target_function(self, plugin):
        """target_func should be stored as target_function attribute."""
        assert plugin.target_function is not None
        assert callable(plugin.target_function)

    def test_init_no_target_function(self, plugin_no_target):
        """Without target_func, target_function should be None."""
        assert plugin_no_target.target_function is None

    def test_init_empty_fetched_prompts(self, plugin):
        """fetched_prompts should start as an empty dict."""
        assert plugin.fetched_prompts == {}

    def test_init_default_application_scenario(self, _patched_sk):
        """Default application_scenario is empty string."""
        with patch.object(_patched_sk, "DefaultAzureCredential", return_value=MagicMock()), patch.object(
            _patched_sk, "RedTeamToolProvider", return_value=MagicMock()
        ) as provider_cls:
            _patched_sk.RedTeamPlugin(
                azure_ai_project_endpoint="https://endpoint.test",
            )
            provider_cls.assert_called_once_with(
                azure_ai_project_endpoint="https://endpoint.test",
                credential=provider_cls.call_args.kwargs.get("credential", provider_cls.call_args[1]["credential"]),
                application_scenario="",
            )


# ---------------------------------------------------------------------------
# fetch_harmful_prompt tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestFetchHarmfulPrompt:
    """Tests for the fetch_harmful_prompt method."""

    @pytest.mark.asyncio
    async def test_fetch_returns_json_string(self, plugin, mock_tool_provider):
        """Result should be a valid JSON string."""
        result = await plugin.fetch_harmful_prompt(risk_category="violence")
        parsed = json.loads(result)
        assert parsed["status"] == "success"

    @pytest.mark.asyncio
    async def test_fetch_calls_provider_with_correct_params(self, plugin, mock_tool_provider):
        """Should delegate to tool_provider.fetch_harmful_prompt with correct args."""
        await plugin.fetch_harmful_prompt(
            risk_category="hate_unfairness",
            strategy="jailbreak",
            convert_with_strategy="base64",
        )
        mock_tool_provider.fetch_harmful_prompt.assert_awaited_once_with(
            risk_category_text="hate_unfairness",
            strategy="jailbreak",
            convert_with_strategy="base64",
        )

    @pytest.mark.asyncio
    async def test_fetch_empty_convert_strategy_becomes_none(self, plugin, mock_tool_provider):
        """Empty string convert_with_strategy should be converted to None."""
        await plugin.fetch_harmful_prompt(
            risk_category="sexual",
            strategy="baseline",
            convert_with_strategy="",
        )
        mock_tool_provider.fetch_harmful_prompt.assert_awaited_once_with(
            risk_category_text="sexual",
            strategy="baseline",
            convert_with_strategy=None,
        )

    @pytest.mark.asyncio
    async def test_fetch_default_convert_strategy_is_none(self, plugin, mock_tool_provider):
        """Default convert_with_strategy (empty string) should become None."""
        await plugin.fetch_harmful_prompt(risk_category="self_harm")
        call_kwargs = mock_tool_provider.fetch_harmful_prompt.call_args.kwargs
        assert call_kwargs["convert_with_strategy"] is None

    @pytest.mark.asyncio
    async def test_fetch_caches_prompt_on_success(self, plugin, mock_tool_provider):
        """Successful fetch should store prompt in fetched_prompts dict."""
        await plugin.fetch_harmful_prompt(risk_category="violence")
        assert "prompt-001" in plugin.fetched_prompts
        assert plugin.fetched_prompts["prompt-001"] == "test harmful prompt"

    @pytest.mark.asyncio
    async def test_fetch_updates_provider_cache(self, plugin, mock_tool_provider):
        """Successful fetch should also update the provider's _fetched_prompts."""
        await plugin.fetch_harmful_prompt(risk_category="violence")
        assert mock_tool_provider._fetched_prompts["prompt-001"] == "test harmful prompt"

    @pytest.mark.asyncio
    async def test_fetch_no_cache_on_failure(self, plugin, mock_tool_provider):
        """Failed fetch should not update caches."""
        mock_tool_provider.fetch_harmful_prompt = AsyncMock(
            return_value={"status": "error", "message": "something went wrong"}
        )
        await plugin.fetch_harmful_prompt(risk_category="violence")
        assert "prompt-001" not in plugin.fetched_prompts

    @pytest.mark.asyncio
    async def test_fetch_no_cache_when_no_prompt_id(self, plugin, mock_tool_provider):
        """Success without prompt_id should not update caches."""
        mock_tool_provider.fetch_harmful_prompt = AsyncMock(return_value={"status": "success", "prompt": "some prompt"})
        await plugin.fetch_harmful_prompt(risk_category="violence")
        assert len(plugin.fetched_prompts) == 0

    @pytest.mark.asyncio
    async def test_fetch_no_cache_when_no_prompt_text(self, plugin, mock_tool_provider):
        """Success with prompt_id but no 'prompt' key should not cache."""
        mock_tool_provider.fetch_harmful_prompt = AsyncMock(return_value={"status": "success", "prompt_id": "id-99"})
        await plugin.fetch_harmful_prompt(risk_category="violence")
        assert "id-99" not in plugin.fetched_prompts

    @pytest.mark.asyncio
    async def test_fetch_returns_all_result_fields(self, plugin, mock_tool_provider):
        """All fields from provider result should appear in the JSON output."""
        result = await plugin.fetch_harmful_prompt(risk_category="violence")
        parsed = json.loads(result)
        assert parsed["prompt_id"] == "prompt-001"
        assert parsed["prompt"] == "test harmful prompt"
        assert parsed["risk_category"] == "violence"


# ---------------------------------------------------------------------------
# convert_prompt tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestConvertPrompt:
    """Tests for the convert_prompt method."""

    @pytest.mark.asyncio
    async def test_convert_returns_json_string(self, plugin, mock_tool_provider):
        """Result should be a valid JSON string."""
        result = await plugin.convert_prompt(prompt_or_id="hello", strategy="base64")
        parsed = json.loads(result)
        assert parsed["status"] == "success"

    @pytest.mark.asyncio
    async def test_convert_calls_provider(self, plugin, mock_tool_provider):
        """Should delegate to tool_provider.convert_prompt."""
        await plugin.convert_prompt(prompt_or_id="some text", strategy="rot13")
        mock_tool_provider.convert_prompt.assert_awaited_once_with(prompt_or_id="some text", strategy="rot13")

    @pytest.mark.asyncio
    async def test_convert_with_cached_prompt_id(self, plugin, mock_tool_provider):
        """When prompt_or_id matches a cached prompt, provider cache is updated."""
        plugin.fetched_prompts["cached-id"] = "cached prompt text"
        await plugin.convert_prompt(prompt_or_id="cached-id", strategy="base64")
        assert mock_tool_provider._fetched_prompts["cached-id"] == "cached prompt text"
        mock_tool_provider.convert_prompt.assert_awaited_once_with(prompt_or_id="cached-id", strategy="base64")

    @pytest.mark.asyncio
    async def test_convert_without_cached_id_no_provider_update(self, plugin, mock_tool_provider):
        """When prompt_or_id is raw text (not cached), provider cache is not pre-populated."""
        mock_tool_provider._fetched_prompts = {}
        await plugin.convert_prompt(prompt_or_id="raw text", strategy="jailbreak")
        assert "raw text" not in mock_tool_provider._fetched_prompts

    @pytest.mark.asyncio
    async def test_convert_result_contains_original_and_converted(self, plugin, mock_tool_provider):
        """JSON result should contain both original and converted prompts."""
        result = await plugin.convert_prompt(prompt_or_id="test", strategy="base64")
        parsed = json.loads(result)
        assert "original_prompt" in parsed
        assert "converted_prompt" in parsed


# ---------------------------------------------------------------------------
# red_team_unified tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestRedTeamUnified:
    """Tests for the red_team_unified method."""

    @pytest.mark.asyncio
    async def test_unified_returns_json_string(self, plugin, mock_tool_provider):
        """Result should be a valid JSON string."""
        result = await plugin.red_team_unified(category="violence")
        parsed = json.loads(result)
        assert parsed["status"] == "success"

    @pytest.mark.asyncio
    async def test_unified_calls_provider_red_team(self, plugin, mock_tool_provider):
        """Should delegate to tool_provider.red_team."""
        await plugin.red_team_unified(category="hate_unfairness", strategy="jailbreak")
        mock_tool_provider.red_team.assert_awaited_once_with(category="hate_unfairness", strategy="jailbreak")

    @pytest.mark.asyncio
    async def test_unified_empty_strategy_becomes_none(self, plugin, mock_tool_provider):
        """Empty string strategy should be converted to None."""
        await plugin.red_team_unified(category="sexual", strategy="")
        mock_tool_provider.red_team.assert_awaited_once_with(category="sexual", strategy=None)

    @pytest.mark.asyncio
    async def test_unified_default_strategy_is_none(self, plugin, mock_tool_provider):
        """Default strategy (empty string) should become None."""
        await plugin.red_team_unified(category="self_harm")
        call_kwargs = mock_tool_provider.red_team.call_args.kwargs
        assert call_kwargs["strategy"] is None

    @pytest.mark.asyncio
    async def test_unified_caches_on_success(self, plugin, mock_tool_provider):
        """Successful call should cache prompt in fetched_prompts and provider."""
        await plugin.red_team_unified(category="violence")
        assert "prompt-002" in plugin.fetched_prompts
        assert plugin.fetched_prompts["prompt-002"] == "unified prompt text"
        assert mock_tool_provider._fetched_prompts["prompt-002"] == "unified prompt text"

    @pytest.mark.asyncio
    async def test_unified_no_cache_on_failure(self, plugin, mock_tool_provider):
        """Failed call should not update caches."""
        mock_tool_provider.red_team = AsyncMock(return_value={"status": "error", "message": "fail"})
        await plugin.red_team_unified(category="violence")
        assert len(plugin.fetched_prompts) == 0

    @pytest.mark.asyncio
    async def test_unified_no_cache_when_missing_prompt_id(self, plugin, mock_tool_provider):
        """Success without prompt_id should not cache."""
        mock_tool_provider.red_team = AsyncMock(return_value={"status": "success", "prompt": "some text"})
        await plugin.red_team_unified(category="violence")
        assert len(plugin.fetched_prompts) == 0

    @pytest.mark.asyncio
    async def test_unified_no_cache_when_missing_prompt_text(self, plugin, mock_tool_provider):
        """Success with prompt_id but no 'prompt' should not cache."""
        mock_tool_provider.red_team = AsyncMock(return_value={"status": "success", "prompt_id": "id-77"})
        await plugin.red_team_unified(category="violence")
        assert "id-77" not in plugin.fetched_prompts

    @pytest.mark.asyncio
    async def test_unified_with_non_empty_strategy(self, plugin, mock_tool_provider):
        """Non-empty strategy should be passed through as-is."""
        await plugin.red_team_unified(category="violence", strategy="base64")
        mock_tool_provider.red_team.assert_awaited_once_with(category="violence", strategy="base64")


# ---------------------------------------------------------------------------
# get_available_strategies tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestGetAvailableStrategies:
    """Tests for get_available_strategies method."""

    @pytest.mark.asyncio
    async def test_returns_json_string(self, plugin, mock_tool_provider):
        """Result should be valid JSON."""
        result = await plugin.get_available_strategies()
        parsed = json.loads(result)
        assert parsed["status"] == "success"

    @pytest.mark.asyncio
    async def test_contains_strategies_list(self, plugin, mock_tool_provider):
        """JSON should contain available_strategies list."""
        result = await plugin.get_available_strategies()
        parsed = json.loads(result)
        assert "available_strategies" in parsed
        assert isinstance(parsed["available_strategies"], list)

    @pytest.mark.asyncio
    async def test_strategies_from_provider(self, plugin, mock_tool_provider):
        """Strategies should match what the provider returns."""
        result = await plugin.get_available_strategies()
        parsed = json.loads(result)
        assert parsed["available_strategies"] == ["baseline", "jailbreak", "base64", "rot13"]

    @pytest.mark.asyncio
    async def test_delegates_to_provider(self, plugin, mock_tool_provider):
        """Should call provider's get_available_strategies."""
        await plugin.get_available_strategies()
        mock_tool_provider.get_available_strategies.assert_called_once()


# ---------------------------------------------------------------------------
# explain_purpose tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestExplainPurpose:
    """Tests for explain_purpose method."""

    @pytest.mark.asyncio
    async def test_returns_json_string(self, plugin):
        """Result should be valid JSON."""
        result = await plugin.explain_purpose()
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    @pytest.mark.asyncio
    async def test_contains_purpose(self, plugin):
        """JSON should contain 'purpose' key."""
        result = await plugin.explain_purpose()
        parsed = json.loads(result)
        assert "purpose" in parsed
        assert "red teaming" in parsed["purpose"].lower()

    @pytest.mark.asyncio
    async def test_contains_responsible_use(self, plugin):
        """JSON should contain 'responsible_use' list."""
        result = await plugin.explain_purpose()
        parsed = json.loads(result)
        assert "responsible_use" in parsed
        assert isinstance(parsed["responsible_use"], list)
        assert len(parsed["responsible_use"]) == 3

    @pytest.mark.asyncio
    async def test_contains_risk_categories(self, plugin):
        """JSON should contain 'risk_categories' dict with expected keys."""
        result = await plugin.explain_purpose()
        parsed = json.loads(result)
        assert "risk_categories" in parsed
        expected_keys = {"violence", "hate_unfairness", "sexual", "self_harm"}
        assert expected_keys == set(parsed["risk_categories"].keys())

    @pytest.mark.asyncio
    async def test_contains_conversion_strategies(self, plugin):
        """JSON should contain 'conversion_strategies' key."""
        result = await plugin.explain_purpose()
        parsed = json.loads(result)
        assert "conversion_strategies" in parsed

    @pytest.mark.asyncio
    async def test_static_output_consistency(self, plugin):
        """Multiple calls should return identical output (static data)."""
        result1 = await plugin.explain_purpose()
        result2 = await plugin.explain_purpose()
        assert result1 == result2


# ---------------------------------------------------------------------------
# send_to_target tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestSendToTarget:
    """Tests for send_to_target method."""

    @pytest.mark.asyncio
    async def test_send_returns_json_string(self, plugin):
        """Result should be valid JSON."""
        result = await plugin.send_to_target(prompt="hello")
        parsed = json.loads(result)
        assert parsed["status"] == "success"

    @pytest.mark.asyncio
    async def test_send_calls_target_function(self, plugin):
        """Should invoke the target_function with the prompt."""
        result = await plugin.send_to_target(prompt="test input")
        parsed = json.loads(result)
        assert parsed["prompt"] == "test input"
        assert parsed["response"] == "response to: test input"

    @pytest.mark.asyncio
    async def test_send_no_target_returns_error(self, plugin_no_target):
        """Without target function, should return error JSON."""
        result = await plugin_no_target.send_to_target(prompt="hello")
        parsed = json.loads(result)
        assert parsed["status"] == "error"
        assert "not initialized" in parsed["message"].lower()

    @pytest.mark.asyncio
    async def test_send_target_exception_returns_error(self, plugin):
        """Target function exception should be caught and returned as error."""
        plugin.target_function = MagicMock(side_effect=RuntimeError("target exploded"))
        result = await plugin.send_to_target(prompt="boom")
        parsed = json.loads(result)
        assert parsed["status"] == "error"
        assert "target exploded" in parsed["message"]
        assert parsed["prompt"] == "boom"

    @pytest.mark.asyncio
    async def test_send_includes_prompt_in_success_response(self, plugin):
        """Success response should echo back the prompt."""
        result = await plugin.send_to_target(prompt="echo test")
        parsed = json.loads(result)
        assert parsed["prompt"] == "echo test"

    @pytest.mark.asyncio
    async def test_send_empty_prompt(self, plugin):
        """Empty string prompt should work fine."""
        result = await plugin.send_to_target(prompt="")
        parsed = json.loads(result)
        assert parsed["status"] == "success"
        assert parsed["prompt"] == ""

    @pytest.mark.asyncio
    async def test_send_target_returns_none(self, plugin):
        """If target function returns None, it should still serialize."""
        plugin.target_function = lambda x: None
        result = await plugin.send_to_target(prompt="test")
        parsed = json.loads(result)
        assert parsed["status"] == "success"
        assert parsed["response"] is None

    @pytest.mark.asyncio
    async def test_send_target_returns_dict(self, plugin):
        """Target function returning a dict should serialize correctly."""
        plugin.target_function = lambda x: {"answer": "42", "input": x}
        result = await plugin.send_to_target(prompt="question")
        parsed = json.loads(result)
        assert parsed["status"] == "success"
        assert parsed["response"]["answer"] == "42"

    @pytest.mark.asyncio
    async def test_send_special_characters_in_prompt(self, plugin):
        """Special characters in prompt should be handled correctly."""
        special = 'test "quotes" & <tags> \\ newline\n tab\t'
        result = await plugin.send_to_target(prompt=special)
        parsed = json.loads(result)
        assert parsed["status"] == "success"
        assert parsed["prompt"] == special


# ---------------------------------------------------------------------------
# Integration-style tests (multiple method interactions)
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestPluginWorkflow:
    """Tests verifying multi-method workflows and state management."""

    @pytest.mark.asyncio
    async def test_fetch_then_convert_uses_cache(self, plugin, mock_tool_provider):
        """Fetch a prompt, then convert it by ID — cache should be populated."""
        await plugin.fetch_harmful_prompt(risk_category="violence")
        assert "prompt-001" in plugin.fetched_prompts

        await plugin.convert_prompt(prompt_or_id="prompt-001", strategy="base64")
        assert mock_tool_provider._fetched_prompts["prompt-001"] == "test harmful prompt"

    @pytest.mark.asyncio
    async def test_unified_then_convert_uses_cache(self, plugin, mock_tool_provider):
        """Unified fetch, then convert by the returned prompt_id."""
        await plugin.red_team_unified(category="hate_unfairness")
        assert "prompt-002" in plugin.fetched_prompts

        await plugin.convert_prompt(prompt_or_id="prompt-002", strategy="rot13")
        assert mock_tool_provider._fetched_prompts["prompt-002"] == "unified prompt text"

    @pytest.mark.asyncio
    async def test_multiple_fetches_accumulate(self, plugin, mock_tool_provider):
        """Multiple fetches should accumulate in the cache."""
        # First fetch
        await plugin.fetch_harmful_prompt(risk_category="violence")

        # Second fetch with different result
        mock_tool_provider.fetch_harmful_prompt = AsyncMock(
            return_value={
                "status": "success",
                "prompt_id": "prompt-003",
                "prompt": "another prompt",
            }
        )
        await plugin.fetch_harmful_prompt(risk_category="sexual")

        assert len(plugin.fetched_prompts) == 2
        assert "prompt-001" in plugin.fetched_prompts
        assert "prompt-003" in plugin.fetched_prompts
