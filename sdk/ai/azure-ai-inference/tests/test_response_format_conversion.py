# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Unit tests for _get_internal_response_format dict handling (issue #44201)."""

import pytest
from azure.ai.inference._patch import _get_internal_response_format
from azure.ai.inference import models as _models
from azure.ai.inference.models import _models as _internal_models


class TestGetInternalResponseFormatDict:
    """Tests for OpenAI-style dict response_format support."""

    def test_dict_text_format(self):
        """Dict with type='text' should produce ChatCompletionsResponseFormatText."""
        result = _get_internal_response_format({"type": "text"})
        assert isinstance(result, _internal_models.ChatCompletionsResponseFormatText)

    def test_dict_json_object_format(self):
        """Dict with type='json_object' should produce ChatCompletionsResponseFormatJsonObject."""
        result = _get_internal_response_format({"type": "json_object"})
        assert isinstance(
            result, _internal_models.ChatCompletionsResponseFormatJsonObject
        )

    def test_dict_json_schema_format(self):
        """Dict with type='json_schema' should produce ChatCompletionsResponseFormatJsonSchema."""
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "ContactInfo",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                    },
                    "required": ["name", "email"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }
        result = _get_internal_response_format(response_format)
        assert isinstance(
            result, _internal_models.ChatCompletionsResponseFormatJsonSchema
        )
        assert result.json_schema.name == "ContactInfo"
        assert result.json_schema.schema["type"] == "object"
        assert result.json_schema.strict is True

    def test_dict_json_schema_with_description(self):
        """Dict with json_schema including description should preserve it."""
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "PersonInfo",
                "description": "Information about a person",
                "schema": {"type": "object", "properties": {}},
            },
        }
        result = _get_internal_response_format(response_format)
        assert isinstance(
            result, _internal_models.ChatCompletionsResponseFormatJsonSchema
        )
        assert result.json_schema.name == "PersonInfo"
        assert result.json_schema.description == "Information about a person"

    def test_dict_unsupported_type_raises(self):
        """Dict with unknown type should raise ValueError."""
        with pytest.raises(
            ValueError, match="Unsupported `response_format` type in dict"
        ):
            _get_internal_response_format({"type": "xml"})

    def test_dict_missing_type_raises(self):
        """Dict without type key should raise ValueError."""
        with pytest.raises(
            ValueError, match="Unsupported `response_format` type in dict"
        ):
            _get_internal_response_format({"foo": "bar"})


class TestGetInternalResponseFormatExisting:
    """Verify existing behavior is preserved."""

    def test_string_text(self):
        result = _get_internal_response_format("text")
        assert isinstance(result, _internal_models.ChatCompletionsResponseFormatText)

    def test_string_json_object(self):
        result = _get_internal_response_format("json_object")
        assert isinstance(
            result, _internal_models.ChatCompletionsResponseFormatJsonObject
        )

    def test_json_schema_format_object(self):
        schema = _models.JsonSchemaFormat(
            name="TestSchema",
            schema={"type": "object", "properties": {}},
        )
        result = _get_internal_response_format(schema)
        assert isinstance(
            result, _internal_models.ChatCompletionsResponseFormatJsonSchema
        )
        assert result.json_schema.name == "TestSchema"

    def test_none_returns_none(self):
        result = _get_internal_response_format(None)
        assert result is None

    def test_unsupported_type_raises(self):
        with pytest.raises(ValueError, match="Unsupported `response_format`"):
            _get_internal_response_format(12345)
