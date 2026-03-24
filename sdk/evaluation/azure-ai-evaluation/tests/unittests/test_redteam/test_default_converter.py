"""
Unit tests for _default_converter module.
"""

import pytest

from azure.ai.evaluation.red_team._default_converter import _DefaultConverter


@pytest.mark.unittest
class TestDefaultConverter:
    """Test the _DefaultConverter class."""

    def test_supported_type_constants(self):
        """Test that SUPPORTED_INPUT_TYPES and SUPPORTED_OUTPUT_TYPES are correct."""
        assert _DefaultConverter.SUPPORTED_INPUT_TYPES == ("text",)
        assert _DefaultConverter.SUPPORTED_OUTPUT_TYPES == ("text",)

    def test_input_supported_text(self):
        """Test input_supported returns True for 'text'."""
        converter = _DefaultConverter()
        assert converter.input_supported("text") is True

    def test_input_supported_unsupported(self):
        """Test input_supported returns False for non-text types."""
        converter = _DefaultConverter()
        assert converter.input_supported("image") is False
        assert converter.input_supported("audio") is False
        assert converter.input_supported("") is False

    def test_output_supported_text(self):
        """Test output_supported returns True for 'text'."""
        converter = _DefaultConverter()
        assert converter.output_supported("text") is True

    def test_output_supported_unsupported(self):
        """Test output_supported returns False for non-text types."""
        converter = _DefaultConverter()
        assert converter.output_supported("image") is False
        assert converter.output_supported("audio") is False
        assert converter.output_supported("") is False

    @pytest.mark.asyncio
    async def test_convert_async_passthrough(self):
        """Test that convert_async returns the prompt unchanged."""
        converter = _DefaultConverter()
        result = await converter.convert_async(prompt="hello world", input_type="text")
        assert result.output_text == "hello world"
        assert result.output_type == "text"

    @pytest.mark.asyncio
    async def test_convert_async_empty_string(self):
        """Test convert_async with an empty prompt string."""
        converter = _DefaultConverter()
        result = await converter.convert_async(prompt="", input_type="text")
        assert result.output_text == ""
        assert result.output_type == "text"

    @pytest.mark.asyncio
    async def test_convert_async_special_characters(self):
        """Test convert_async preserves special characters."""
        prompt = "Hello! @#$%^&*() 日本語 émojis 🎉"
        converter = _DefaultConverter()
        result = await converter.convert_async(prompt=prompt, input_type="text")
        assert result.output_text == prompt
        assert result.output_type == "text"

    @pytest.mark.asyncio
    async def test_convert_async_default_input_type(self):
        """Test that convert_async defaults input_type to 'text'."""
        converter = _DefaultConverter()
        result = await converter.convert_async(prompt="test prompt")
        assert result.output_text == "test prompt"
        assert result.output_type == "text"

    @pytest.mark.asyncio
    async def test_convert_async_unsupported_input_type(self):
        """Test that convert_async raises ValueError for unsupported input types."""
        converter = _DefaultConverter()
        with pytest.raises(ValueError, match="Input type not supported"):
            await converter.convert_async(prompt="test", input_type="image")

    @pytest.mark.asyncio
    async def test_convert_async_multiline_prompt(self):
        """Test convert_async with multiline text."""
        prompt = "line one\nline two\nline three"
        converter = _DefaultConverter()
        result = await converter.convert_async(prompt=prompt, input_type="text")
        assert result.output_text == prompt

    def test_is_instance_of_prompt_converter(self):
        """Test that _DefaultConverter is a subclass of PromptConverter."""
        from pyrit.prompt_converter import PromptConverter

        converter = _DefaultConverter()
        assert isinstance(converter, PromptConverter)
