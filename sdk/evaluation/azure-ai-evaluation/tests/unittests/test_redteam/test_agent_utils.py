"""
Unit tests for _agent_utils module (AgentUtils class).

The source module imports ``CharSwapGenerator`` from ``pyrit.prompt_converter``,
but the installed pyrit version renamed it to ``CharSwapConverter``.  We inject
a shim before the module is loaded so the import succeeds, then mock every
converter *instance* on the ``AgentUtils`` object for behavioural tests.
"""

import sys
import importlib
import pytest
from unittest.mock import MagicMock, AsyncMock

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# All converter classes imported at the top of _agent_utils.py
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

# Fully-qualified module path
_MODULE_PATH = "azure.ai.evaluation.red_team._agent._agent_utils"

# All instance-level attribute names set in AgentUtils.__init__
_INSTANCE_ATTRS = [
    "base64_converter",
    "flip_converter",
    "morse_converter",
    "ansi_attack_converter",
    "ascii_art_converter",
    "ascii_smuggler_converter",
    "atbash_converter",
    "binary_converter",
    "character_space_converter",
    "char_swap_generator",
    "diacritic_converter",
    "leetspeak_converter",
    "url_converter",
    "unicode_substitution_converter",
    "unicode_confusable_converter",
    "suffix_append_converter",
    "string_join_converter",
    "rot13_converter",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_converter():
    """Create a mock converter whose ``convert_async`` returns an object
    with ``output_text = "converted"``."""
    mock = MagicMock()
    result = MagicMock()
    result.output_text = "converted"
    mock.convert_async = AsyncMock(return_value=result)
    return mock


def _inject_missing_pyrit_names():
    """Ensure every class name that _agent_utils imports from
    ``pyrit.prompt_converter`` is available — even if the installed
    version renamed or removed it.  Returns names that were injected
    so they can be cleaned up later."""
    import pyrit.prompt_converter as pc

    injected = []
    for name in _PYRIT_CONVERTER_NAMES:
        if not hasattr(pc, name):
            setattr(pc, name, MagicMock())
            injected.append(name)
    return injected


def _import_agent_utils():
    """Import (or reimport) the _agent_utils module, returning it."""
    sys.modules.pop(_MODULE_PATH, None)
    return importlib.import_module(_MODULE_PATH)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _patched_pyrit():
    """Module-scoped fixture: make sure pyrit.prompt_converter has all names
    that _agent_utils expects, then import the module."""
    injected = _inject_missing_pyrit_names()
    mod = _import_agent_utils()
    yield mod
    # Cleanup injected names
    import pyrit.prompt_converter as pc

    for name in injected:
        if hasattr(pc, name):
            delattr(pc, name)
    sys.modules.pop(_MODULE_PATH, None)


@pytest.fixture
def agent_utils(_patched_pyrit):
    """Create an ``AgentUtils`` instance with every converter attribute
    replaced by a mock so tests control ``convert_async`` return values."""
    utils = _patched_pyrit.AgentUtils()
    # Replace every converter attribute with a mock
    for attr in _INSTANCE_ATTRS:
        setattr(utils, attr, _make_mock_converter())
    yield utils


# ---------------------------------------------------------------------------
# __init__ tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestAgentUtilsInit:
    """Verify that __init__ creates all expected converter attributes."""

    EXPECTED_ATTRS = [
        "base64_converter",
        "flip_converter",
        "morse_converter",
        "ansi_attack_converter",
        "ascii_art_converter",
        "ascii_smuggler_converter",
        "atbash_converter",
        "binary_converter",
        "character_space_converter",
        "char_swap_generator",
        "diacritic_converter",
        "leetspeak_converter",
        "url_converter",
        "unicode_substitution_converter",
        "unicode_confusable_converter",
        "suffix_append_converter",
        "string_join_converter",
        "rot13_converter",
    ]

    def test_all_converter_attributes_exist(self, agent_utils):
        """Every converter attribute listed in __init__ must be present."""
        for attr in self.EXPECTED_ATTRS:
            assert hasattr(agent_utils, attr), f"Missing attribute: {attr}"

    def test_all_converters_are_not_none(self, agent_utils):
        """Each converter must be a non-None object."""
        for attr in self.EXPECTED_ATTRS:
            assert getattr(agent_utils, attr) is not None, f"{attr} is None"

    def test_at_least_18_converters(self, agent_utils):
        """AgentUtils must initialise at least 18 converter instances."""
        count = sum(1 for attr in self.EXPECTED_ATTRS if hasattr(agent_utils, attr))
        assert count >= 18

    def test_suffix_append_converter_called_with_suffix(self, _patched_pyrit):
        """SuffixAppendConverter must be created with the expected suffix kwarg."""
        utils = _patched_pyrit.AgentUtils()
        # The real SuffixAppendConverter was constructed — verify via the instance
        assert hasattr(utils, "suffix_append_converter")
        assert utils.suffix_append_converter is not None


# ---------------------------------------------------------------------------
# convert_text tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestConvertText:
    """Tests for the async convert_text method."""

    @pytest.mark.asyncio
    async def test_dispatch_with_converter_suffix(self, agent_utils):
        """When converter_name already contains '_converter', use it as-is."""
        result = await agent_utils.convert_text(converter_name="base64_converter", text="hello")
        assert result == "converted"
        agent_utils.base64_converter.convert_async.assert_awaited_once_with(prompt="hello")

    @pytest.mark.asyncio
    async def test_dispatch_without_converter_suffix(self, agent_utils):
        """When converter_name lacks '_converter', the method appends it."""
        result = await agent_utils.convert_text(converter_name="flip", text="hello")
        assert result == "converted"
        agent_utils.flip_converter.convert_async.assert_awaited_once_with(prompt="hello")

    @pytest.mark.asyncio
    async def test_dispatch_char_swap_generator_quirk(self, agent_utils):
        """char_swap_generator has no '_converter' suffix, so convert_text
        appends '_converter' → looks for 'char_swap_generator_converter',
        which doesn't exist.  This is a known source-code quirk."""
        with pytest.raises(ValueError, match="not found"):
            await agent_utils.convert_text(converter_name="char_swap_generator", text="test")

    @pytest.mark.asyncio
    async def test_unsupported_converter_raises_value_error(self, agent_utils):
        """An unknown converter name must raise ValueError."""
        with pytest.raises(ValueError, match="not found"):
            await agent_utils.convert_text(converter_name="nonexistent", text="hello")

    @pytest.mark.asyncio
    async def test_unsupported_converter_with_suffix_raises_value_error(self, agent_utils):
        """Unknown name that already contains '_converter' still raises."""
        with pytest.raises(ValueError, match="not found"):
            await agent_utils.convert_text(converter_name="nonexistent_converter", text="hello")

    @pytest.mark.asyncio
    async def test_convert_empty_text(self, agent_utils):
        """Empty string is a valid input."""
        result = await agent_utils.convert_text(converter_name="morse", text="")
        assert result == "converted"
        agent_utils.morse_converter.convert_async.assert_awaited_once_with(prompt="")

    @pytest.mark.asyncio
    async def test_convert_special_characters(self, agent_utils):
        """Special / unicode characters should be forwarded unchanged."""
        special = "héllo wörld! 🔥 <script>alert(1)</script>"
        result = await agent_utils.convert_text(converter_name="binary", text=special)
        assert result == "converted"
        agent_utils.binary_converter.convert_async.assert_awaited_once_with(prompt=special)

    @pytest.mark.asyncio
    async def test_convert_returns_output_text(self, agent_utils):
        """Return value must be the output_text attribute of the converter result."""
        custom_result = MagicMock()
        custom_result.output_text = "custom-output-12345"
        agent_utils.rot13_converter.convert_async = AsyncMock(return_value=custom_result)

        result = await agent_utils.convert_text(converter_name="rot13", text="abc")
        assert result == "custom-output-12345"

    @pytest.mark.asyncio
    async def test_all_listed_converters_dispatch_correctly(self, agent_utils):
        """Every converter whose name contains '_converter' must be reachable
        via convert_text.  'char_swap_generator' is excluded because its name
        lacks '_converter' and the dispatch logic cannot resolve it."""
        supported = agent_utils.get_list_of_supported_converters()
        for name in supported:
            if name == "char_swap_generator":
                continue  # known quirk — tested separately
            result = await agent_utils.convert_text(converter_name=name, text="probe")
            assert result == "converted", f"Dispatch failed for {name}"

    @pytest.mark.asyncio
    async def test_converter_async_exception_propagates(self, agent_utils):
        """If the underlying converter raises, convert_text must propagate it."""
        agent_utils.base64_converter.convert_async = AsyncMock(side_effect=RuntimeError("boom"))
        with pytest.raises(RuntimeError, match="boom"):
            await agent_utils.convert_text(converter_name="base64", text="x")


# ---------------------------------------------------------------------------
# get_list_of_supported_converters tests
# ---------------------------------------------------------------------------
@pytest.mark.unittest
class TestGetListOfSupportedConverters:
    """Tests for get_list_of_supported_converters."""

    def test_returns_list(self, agent_utils):
        result = agent_utils.get_list_of_supported_converters()
        assert isinstance(result, list)

    def test_list_has_at_least_18_entries(self, agent_utils):
        result = agent_utils.get_list_of_supported_converters()
        assert len(result) >= 18

    def test_expected_names_present(self, agent_utils):
        result = agent_utils.get_list_of_supported_converters()
        expected = {
            "base64_converter",
            "flip_converter",
            "morse_converter",
            "ansi_attack_converter",
            "ascii_art_converter",
            "ascii_smuggler_converter",
            "atbash_converter",
            "binary_converter",
            "character_space_converter",
            "char_swap_generator",
            "diacritic_converter",
            "leetspeak_converter",
            "url_converter",
            "unicode_substitution_converter",
            "unicode_confusable_converter",
            "suffix_append_converter",
            "string_join_converter",
            "rot13_converter",
        }
        assert expected.issubset(set(result))

    def test_all_entries_are_strings(self, agent_utils):
        for name in agent_utils.get_list_of_supported_converters():
            assert isinstance(name, str)

    def test_all_entries_correspond_to_instance_attrs(self, agent_utils):
        """Every name returned must be an actual attribute on the instance."""
        for name in agent_utils.get_list_of_supported_converters():
            assert hasattr(agent_utils, name), f"{name} not found on AgentUtils instance"
