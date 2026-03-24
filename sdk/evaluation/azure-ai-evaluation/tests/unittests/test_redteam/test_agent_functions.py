"""
Unit tests for _agent_functions module.

The source module does ``from azure.ai.evaluation.red_team._agent import
RedTeamToolProvider``, which fails at import time because the ``_agent``
package's ``__init__.py`` is empty and the transitive import chain
(pyrit converters, etc.) may be broken.

Strategy: we populate the ``_agent`` package entry in ``sys.modules``
with the *real* package object (so ``__path__`` is correct for submodule
resolution) but patch in a ``RedTeamToolProvider`` attribute before
importing the target module.
"""

import os
import sys
import types
import importlib
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# ---------------------------------------------------------------------------
# Pre-import shimming
# ---------------------------------------------------------------------------

_AGENT_PKG = "azure.ai.evaluation.red_team._agent"
_MODULE_PATH = "azure.ai.evaluation.red_team._agent._agent_functions"

# Physical path to the _agent package directory — needed for __path__
_AGENT_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        os.pardir,
        os.pardir,  # up from tests/unittests/test_redteam
        "azure",
        "ai",
        "evaluation",
        "red_team",
        "_agent",
    )
)


def _ensure_importable():
    """Ensure the target module can be imported by guaranteeing that the
    ``_agent`` package has a ``RedTeamToolProvider`` name and correct
    ``__path__`` for submodule resolution."""

    # Build or update the _agent package entry
    if _AGENT_PKG in sys.modules:
        pkg = sys.modules[_AGENT_PKG]
    else:
        pkg = types.ModuleType(_AGENT_PKG)
        pkg.__package__ = _AGENT_PKG
        pkg.__path__ = [_AGENT_DIR]
        pkg.__file__ = os.path.join(_AGENT_DIR, "__init__.py")
        sys.modules[_AGENT_PKG] = pkg

    # Ensure __path__ is set (real package may have it already)
    if not getattr(pkg, "__path__", None):
        pkg.__path__ = [_AGENT_DIR]

    # Inject the mock class so ``from ... import RedTeamToolProvider`` works
    if not hasattr(pkg, "RedTeamToolProvider"):
        pkg.RedTeamToolProvider = MagicMock

    # Drop any cached copy of the target module
    sys.modules.pop(_MODULE_PATH, None)


_ensure_importable()

af_module = importlib.import_module(_MODULE_PATH)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CONN_STR = "https://host.example.com;sub-id-123;rg-name;project-name"


def _make_mock_provider():
    """Return a MagicMock that mimics RedTeamToolProvider with async helpers."""
    provider = MagicMock()
    provider.fetch_harmful_prompt = AsyncMock()
    provider.convert_prompt = AsyncMock()
    provider.red_team = AsyncMock()
    provider.get_available_strategies = MagicMock(
        return_value=["morse_converter", "binary_converter", "base64_converter"]
    )
    provider._fetched_prompts = {}
    return provider


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unittest
class TestAgentFunctions:
    """Tests for every public function in _agent_functions.py."""

    # -- state isolation ----------------------------------------------------

    def setup_method(self):
        """Save module globals before each test."""
        self._saved = {
            "credential": af_module.credential,
            "tool_provider": af_module.tool_provider,
            "azure_ai_project": af_module.azure_ai_project,
            "target_function": af_module.target_function,
            "fetched_prompts": af_module.fetched_prompts.copy(),
        }

    def teardown_method(self):
        """Restore module globals after each test."""
        af_module.credential = self._saved["credential"]
        af_module.tool_provider = self._saved["tool_provider"]
        af_module.azure_ai_project = self._saved["azure_ai_project"]
        af_module.target_function = self._saved["target_function"]
        af_module.fetched_prompts.clear()
        af_module.fetched_prompts.update(self._saved["fetched_prompts"])

    # ======================================================================
    # initialize_tool_provider
    # ======================================================================

    @patch.object(af_module, "DefaultAzureCredential")
    @patch.object(af_module, "RedTeamToolProvider")
    def test_initialize_parses_connection_string(self, mock_provider_cls, mock_cred_cls):
        """Connection string is split into azure_ai_project dict."""
        af_module.credential = None
        af_module.tool_provider = None

        result = af_module.initialize_tool_provider(_CONN_STR)

        assert af_module.azure_ai_project == {
            "subscription_id": "sub-id-123",
            "resource_group_name": "rg-name",
            "project_name": "project-name",
        }
        mock_cred_cls.assert_called_once()
        mock_provider_cls.assert_called_once_with(
            azure_ai_project=af_module.azure_ai_project,
            credential=mock_cred_cls.return_value,
        )
        assert result is af_module.user_functions

    @patch.object(af_module, "DefaultAzureCredential")
    @patch.object(af_module, "RedTeamToolProvider")
    def test_initialize_sets_target_function(self, mock_provider_cls, mock_cred_cls):
        af_module.credential = None
        my_target = MagicMock()

        af_module.initialize_tool_provider(_CONN_STR, target_func=my_target)

        assert af_module.target_function is my_target

    @patch.object(af_module, "DefaultAzureCredential")
    @patch.object(af_module, "RedTeamToolProvider")
    def test_initialize_no_target_func_leaves_none(self, mock_provider_cls, mock_cred_cls):
        af_module.credential = None
        af_module.target_function = None

        af_module.initialize_tool_provider(_CONN_STR)

        assert af_module.target_function is None

    @patch.object(af_module, "DefaultAzureCredential")
    @patch.object(af_module, "RedTeamToolProvider")
    def test_initialize_reuses_existing_credential(self, mock_provider_cls, mock_cred_cls):
        existing_cred = MagicMock()
        af_module.credential = existing_cred

        af_module.initialize_tool_provider(_CONN_STR)

        mock_cred_cls.assert_not_called()
        assert af_module.credential is existing_cred

    # ======================================================================
    # _get_tool_provider (lazy init)
    # ======================================================================

    @patch.object(af_module, "DefaultAzureCredential")
    @patch.object(af_module, "RedTeamToolProvider")
    def test_get_tool_provider_creates_on_first_call(self, mock_provider_cls, mock_cred_cls):
        af_module.tool_provider = None
        af_module.credential = None
        af_module.azure_ai_project = {
            "subscription_id": "s",
            "resource_group_name": "r",
            "project_name": "p",
        }

        result = af_module._get_tool_provider()

        mock_cred_cls.assert_called_once()
        mock_provider_cls.assert_called_once()
        assert result is mock_provider_cls.return_value

    def test_get_tool_provider_returns_existing(self):
        existing = MagicMock()
        af_module.tool_provider = existing

        assert af_module._get_tool_provider() is existing

    # ======================================================================
    # red_team_fetch_harmful_prompt
    # ======================================================================

    @patch.object(af_module, "_get_tool_provider")
    @patch.object(af_module, "asyncio")
    def test_fetch_harmful_prompt_success(self, mock_asyncio, mock_get_provider):
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider
        mock_asyncio.run.return_value = {
            "status": "success",
            "prompt_id": "pid-1",
            "prompt": "test harmful prompt",
        }

        result = json.loads(af_module.red_team_fetch_harmful_prompt("violence"))

        assert result["status"] == "success"
        assert af_module.fetched_prompts["pid-1"] == "test harmful prompt"
        mock_asyncio.run.assert_called_once()

    @patch.object(af_module, "_get_tool_provider")
    @patch.object(af_module, "asyncio")
    def test_fetch_harmful_prompt_with_strategy(self, mock_asyncio, mock_get_provider):
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider
        mock_asyncio.run.return_value = {
            "status": "success",
            "prompt_id": "pid-2",
            "prompt": "converted",
        }

        af_module.red_team_fetch_harmful_prompt(
            "hate_unfairness",
            strategy="jailbreak",
            convert_with_strategy="base64_converter",
        )

        call_args = provider.fetch_harmful_prompt.call_args
        assert call_args.kwargs["risk_category_text"] == "hate_unfairness"
        assert call_args.kwargs["strategy"] == "jailbreak"
        assert call_args.kwargs["convert_with_strategy"] == "base64_converter"

    @patch.object(af_module, "_get_tool_provider")
    @patch.object(af_module, "asyncio")
    def test_fetch_harmful_prompt_failure_not_cached(self, mock_asyncio, mock_get_provider):
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider
        mock_asyncio.run.return_value = {"status": "error", "message": "something broke"}

        af_module.red_team_fetch_harmful_prompt("violence")

        assert af_module.fetched_prompts == {}

    @patch.object(af_module, "_get_tool_provider")
    @patch.object(af_module, "asyncio")
    def test_fetch_harmful_prompt_no_prompt_key(self, mock_asyncio, mock_get_provider):
        """Success with prompt_id but missing 'prompt' key does not cache."""
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider
        mock_asyncio.run.return_value = {"status": "success", "prompt_id": "pid-3"}

        af_module.red_team_fetch_harmful_prompt("self_harm")

        assert "pid-3" not in af_module.fetched_prompts

    @patch.object(af_module, "_get_tool_provider")
    @patch.object(af_module, "asyncio")
    def test_fetch_harmful_prompt_no_prompt_id(self, mock_asyncio, mock_get_provider):
        """Success without prompt_id does not crash or cache."""
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider
        mock_asyncio.run.return_value = {"status": "success", "prompt": "some text"}

        result = json.loads(af_module.red_team_fetch_harmful_prompt("violence"))

        assert result["status"] == "success"
        assert af_module.fetched_prompts == {}

    # ======================================================================
    # red_team_convert_prompt
    # ======================================================================

    @patch.object(af_module, "_get_tool_provider")
    @patch.object(af_module, "asyncio")
    def test_convert_prompt_with_cached_id(self, mock_asyncio, mock_get_provider):
        """Cached prompt is pushed into the provider's internal cache."""
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider
        af_module.fetched_prompts["pid-1"] = "cached prompt text"
        mock_asyncio.run.return_value = {
            "original": "cached prompt text",
            "converted": "... --- ...",
        }

        result = json.loads(af_module.red_team_convert_prompt("pid-1", "morse_converter"))

        assert provider._fetched_prompts["pid-1"] == "cached prompt text"
        assert result["converted"] == "... --- ..."

    @patch.object(af_module, "_get_tool_provider")
    @patch.object(af_module, "asyncio")
    def test_convert_prompt_with_raw_text(self, mock_asyncio, mock_get_provider):
        """Raw text (not in cache) does not touch provider's cache."""
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider
        mock_asyncio.run.return_value = {"original": "hello", "converted": "01101000"}

        result = json.loads(af_module.red_team_convert_prompt("hello", "binary_converter"))

        assert "hello" not in provider._fetched_prompts
        assert result["converted"] == "01101000"

    # ======================================================================
    # red_team_unified
    # ======================================================================

    @patch.object(af_module, "_get_tool_provider")
    @patch.object(af_module, "asyncio")
    def test_unified_success_caches_prompt(self, mock_asyncio, mock_get_provider):
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider
        mock_asyncio.run.return_value = {
            "status": "success",
            "prompt_id": "uid-1",
            "prompt": "unified prompt",
        }

        result = json.loads(af_module.red_team_unified("violence", strategy="morse_converter"))

        assert result["status"] == "success"
        assert af_module.fetched_prompts["uid-1"] == "unified prompt"
        call_args = provider.red_team.call_args
        assert call_args.kwargs["category"] == "violence"
        assert call_args.kwargs["strategy"] == "morse_converter"

    @patch.object(af_module, "_get_tool_provider")
    @patch.object(af_module, "asyncio")
    def test_unified_success_no_prompt_key(self, mock_asyncio, mock_get_provider):
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider
        mock_asyncio.run.return_value = {"status": "success", "prompt_id": "uid-2"}

        af_module.red_team_unified("sexual")

        assert "uid-2" not in af_module.fetched_prompts

    @patch.object(af_module, "_get_tool_provider")
    @patch.object(af_module, "asyncio")
    def test_unified_success_no_prompt_id(self, mock_asyncio, mock_get_provider):
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider
        mock_asyncio.run.return_value = {"status": "success", "prompt": "text only"}

        af_module.red_team_unified("violence")

        assert af_module.fetched_prompts == {}

    @patch.object(af_module, "_get_tool_provider")
    @patch.object(af_module, "asyncio")
    def test_unified_failure_not_cached(self, mock_asyncio, mock_get_provider):
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider
        mock_asyncio.run.return_value = {"status": "error", "message": "fail"}

        af_module.red_team_unified("violence")

        assert af_module.fetched_prompts == {}

    @patch.object(af_module, "_get_tool_provider")
    @patch.object(af_module, "asyncio")
    def test_unified_no_strategy(self, mock_asyncio, mock_get_provider):
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider
        mock_asyncio.run.return_value = {"status": "success"}

        af_module.red_team_unified("hate_unfairness")

        assert provider.red_team.call_args.kwargs["strategy"] is None

    # ======================================================================
    # red_team_get_available_strategies
    # ======================================================================

    @patch.object(af_module, "_get_tool_provider")
    def test_get_available_strategies(self, mock_get_provider):
        provider = _make_mock_provider()
        mock_get_provider.return_value = provider

        result = json.loads(af_module.red_team_get_available_strategies())

        assert result["status"] == "success"
        assert "morse_converter" in result["available_strategies"]
        assert len(result["available_strategies"]) == 3

    # ======================================================================
    # red_team_explain_purpose
    # ======================================================================

    def test_explain_purpose_returns_valid_json(self):
        result = json.loads(af_module.red_team_explain_purpose())

        assert "purpose" in result
        assert "responsible_use" in result
        assert isinstance(result["responsible_use"], list)
        assert "risk_categories" in result
        assert "violence" in result["risk_categories"]
        assert "conversion_strategies" in result

    def test_explain_purpose_has_all_risk_categories(self):
        result = json.loads(af_module.red_team_explain_purpose())
        for cat in ("violence", "hate_unfairness", "sexual", "self_harm"):
            assert cat in result["risk_categories"]

    def test_explain_purpose_responsible_use_not_empty(self):
        result = json.loads(af_module.red_team_explain_purpose())
        assert len(result["responsible_use"]) >= 1

    # ======================================================================
    # red_team_send_to_target
    # ======================================================================

    def test_send_to_target_no_target_function(self):
        af_module.target_function = None

        result = json.loads(af_module.red_team_send_to_target("hello"))

        assert result["status"] == "error"
        assert "not initialized" in result["message"]

    def test_send_to_target_success(self):
        my_target = MagicMock(return_value="target response text")
        af_module.target_function = my_target

        result = json.loads(af_module.red_team_send_to_target("test prompt"))

        assert result["status"] == "success"
        assert result["prompt"] == "test prompt"
        assert result["response"] == "target response text"
        my_target.assert_called_once_with("test prompt")

    def test_send_to_target_exception(self):
        def bad_target(p):
            raise RuntimeError("boom")

        af_module.target_function = bad_target

        result = json.loads(af_module.red_team_send_to_target("trigger"))

        assert result["status"] == "error"
        assert "boom" in result["message"]
        assert result["prompt"] == "trigger"

    def test_send_to_target_exception_type_preserved(self):
        def val_err_target(p):
            raise ValueError("bad input value")

        af_module.target_function = val_err_target

        result = json.loads(af_module.red_team_send_to_target("x"))

        assert "bad input value" in result["message"]

    # ======================================================================
    # user_functions set
    # ======================================================================

    def test_user_functions_contains_all_public_functions(self):
        expected = {
            af_module.red_team_fetch_harmful_prompt,
            af_module.red_team_convert_prompt,
            af_module.red_team_unified,
            af_module.red_team_get_available_strategies,
            af_module.red_team_explain_purpose,
            af_module.red_team_send_to_target,
        }
        assert af_module.user_functions == expected

    def test_user_functions_has_correct_count(self):
        assert len(af_module.user_functions) == 6

    # ======================================================================
    # Global state isolation smoke tests
    # ======================================================================

    @patch.object(af_module, "DefaultAzureCredential")
    @patch.object(af_module, "RedTeamToolProvider")
    def test_initialize_then_lazy_get_reuses_provider(self, mock_provider_cls, mock_cred_cls):
        af_module.credential = None
        af_module.tool_provider = None

        af_module.initialize_tool_provider(_CONN_STR)
        provider = af_module._get_tool_provider()

        assert mock_provider_cls.call_count == 1
        assert provider is af_module.tool_provider

    def test_fetched_prompts_is_dict(self):
        assert isinstance(af_module.fetched_prompts, dict)
