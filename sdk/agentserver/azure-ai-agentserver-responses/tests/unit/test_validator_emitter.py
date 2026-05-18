# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for validator emitter behavior."""

from __future__ import annotations

import re
from types import ModuleType

from scripts.validator_emitter import build_validator_module


def _load_module(code: str) -> ModuleType:
    module = ModuleType("generated_validators")
    exec(code, module.__dict__)
    return module


def test_emitter_generates_required_property_check() -> None:
    schemas = {
        "CreateResponse": {
            "type": "object",
            "required": ["model"],
            "properties": {"model": {"type": "string"}},
        }
    }
    module = _load_module(build_validator_module(schemas, ["CreateResponse"]))
    errors = module.validate_CreateResponse({})
    assert any(e["path"] == "$.model" and "missing" in e["message"].lower() for e in errors)


def test_emitter_generates_class_without_schema_definition() -> None:
    schemas = {
        "CreateResponse": {
            "type": "object",
            "required": ["model"],
            "properties": {"model": {"type": "string"}},
        }
    }
    code = build_validator_module(schemas, ["CreateResponse"])
    assert "class CreateResponseValidator" in code
    assert "\nSCHEMAS =" not in code


def test_emitter_uses_generated_enum_values_when_available() -> None:
    schemas = {
        "OpenAI.ToolType": {
            "anyOf": [
                {"type": "string"},
                {"type": "string", "enum": ["function", "file_search"]},
            ]
        }
    }
    code = build_validator_module(schemas, ["OpenAI.ToolType"])
    assert "_enum_values('ToolType')" in code


def test_emitter_deduplicates_string_union_error_message() -> None:
    schemas = {
        "OpenAI.InputItemType": {
            "anyOf": [
                {"type": "string"},
                {"type": "string", "enum": ["message", "item_reference"]},
            ]
        }
    }

    module = _load_module(build_validator_module(schemas, ["OpenAI.InputItemType"]))
    errors = module.validate_OpenAI_InputItemType(123)
    assert errors
    assert errors[0]["path"] == "$"
    assert "InputItemType" in errors[0]["message"]
    assert "got integer" in errors[0]["message"].lower()
    assert "string, string" not in errors[0]["message"]


def test_emitter_generates_nullable_handling() -> None:
    schemas = {
        "CreateResponse": {
            "type": "object",
            "properties": {"instructions": {"type": "string", "nullable": True}},
        }
    }
    module = _load_module(build_validator_module(schemas, ["CreateResponse"]))
    assert module.validate_CreateResponse({"instructions": None}) == []


def test_emitter_generates_primitive_type_checks_and_enum_literal() -> None:
    schemas = {
        "CreateResponse": {
            "type": "object",
            "properties": {
                "model": {"type": "string", "enum": ["gpt-4o", "gpt-4.1"]},
                "temperature": {"type": "number"},
                "stream": {"type": "boolean"},
            },
        }
    }
    module = _load_module(build_validator_module(schemas, ["CreateResponse"]))
    errors = module.validate_CreateResponse({"model": "bad", "temperature": "hot", "stream": "yes"})
    assert any(e["path"] == "$.model" and "allowed" in e["message"].lower() for e in errors)
    assert any(e["path"] == "$.temperature" and "number" in e["message"].lower() for e in errors)
    assert any(e["path"] == "$.stream" and "boolean" in e["message"].lower() for e in errors)


def test_emitter_generates_nested_delegate_calls() -> None:
    schemas = {
        "CreateResponse": {
            "type": "object",
            "properties": {"metadata": {"$ref": "#/components/schemas/Metadata"}},
        },
        "Metadata": {
            "type": "object",
            "required": ["id"],
            "properties": {"id": {"type": "string"}},
        },
    }
    module = _load_module(build_validator_module(schemas, ["CreateResponse"]))
    errors = module.validate_CreateResponse({"metadata": {}})
    assert any(e["path"] == "$.metadata.id" for e in errors)


def test_emitter_generates_union_kind_check_for_oneof_anyof() -> None:
    schemas = {
        "CreateResponse": {
            "type": "object",
            "properties": {
                "tool_choice": {
                    "anyOf": [
                        {"type": "string"},
                        {"$ref": "#/components/schemas/ToolChoiceParam"},
                    ]
                }
            },
        },
        "ToolChoiceParam": {
            "type": "object",
            "required": ["type"],
            "properties": {"type": {"type": "string"}},
        },
    }
    module = _load_module(build_validator_module(schemas, ["CreateResponse"]))
    errors = module.validate_CreateResponse({"tool_choice": 123})
    assert any(e["path"] == "$.tool_choice" and "expected one of" in e["message"].lower() for e in errors)


def test_emitter_validates_create_response_input_property() -> None:
    schemas = {
        "CreateResponse": {
            "type": "object",
            "properties": {
                "input": {
                    "anyOf": [
                        {"type": "string"},
                        {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/InputItem"},
                        },
                    ]
                }
            },
        },
        "InputItem": {
            "type": "object",
            "required": ["type"],
            "properties": {"type": {"type": "string"}},
        },
    }

    module = _load_module(build_validator_module(schemas, ["CreateResponse"]))

    # Invalid input kind should fail the CreateResponse.input union check.
    invalid_errors = module.validate_CreateResponse({"input": 123})
    assert any(e["path"] == "$.input" and "expected one of" in e["message"].lower() for e in invalid_errors)

    # Supported input kinds should pass.
    assert module.validate_CreateResponse({"input": "hello"}) == []
    assert module.validate_CreateResponse({"input": [{"type": "message"}]}) == []


def test_emitter_generates_discriminator_dispatch() -> None:
    schemas = {
        "Tool": {
            "type": "object",
            "discriminator": {
                "propertyName": "type",
                "mapping": {
                    "function": "#/components/schemas/FunctionTool",
                },
            },
            "properties": {"type": {"type": "string"}},
        },
        "FunctionTool": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "type": {"type": "string"},
                "name": {"type": "string"},
            },
        },
    }
    module = _load_module(build_validator_module(schemas, ["Tool"]))
    errors = module.validate_Tool({"type": "function"})
    assert any(e["path"] == "$.name" and "missing" in e["message"].lower() for e in errors)


def test_emitter_generates_default_discriminator_fallback() -> None:
    """When defaultValue is set on a discriminator, absent 'type' uses the default."""
    schemas = {
        "Item": {
            "type": "object",
            "required": ["type"],
            "discriminator": {
                "propertyName": "type",
                "defaultValue": "message",
                "mapping": {
                    "message": "#/components/schemas/ItemMessage",
                    "function_call": "#/components/schemas/ItemFunctionCall",
                },
            },
            "properties": {"type": {"type": "string"}},
        },
        "ItemMessage": {
            "type": "object",
            "required": ["role"],
            "properties": {
                "type": {"type": "string"},
                "role": {"type": "string"},
            },
        },
        "ItemFunctionCall": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "type": {"type": "string"},
                "name": {"type": "string"},
            },
        },
    }
    module = _load_module(build_validator_module(schemas, ["Item"]))

    # No type → defaults to "message", validates against ItemMessage
    errors = module.validate_Item({"role": "user"})
    # Should NOT get "Required discriminator 'type' is missing" or "Required property 'type' is missing"
    assert not any("type" in e.get("path", "") and "missing" in e.get("message", "").lower() for e in errors)
    # Should validate as message — role present, so no errors
    assert errors == []

    # No type, missing required "role" → defaults to "message" but fails message validation
    errors_no_role = module.validate_Item({"content": "hi"})
    assert not any("type" in e.get("path", "") and "missing" in e.get("message", "").lower() for e in errors_no_role)
    assert any(e["path"] == "$.role" and "missing" in e["message"].lower() for e in errors_no_role)

    # Explicit type still works
    errors_fc = module.validate_Item({"type": "function_call"})
    assert any(e["path"] == "$.name" and "missing" in e["message"].lower() for e in errors_fc)


def test_emitter_generates_array_and_map_checks() -> None:
    schemas = {
        "CreateResponse": {
            "type": "object",
            "properties": {
                "tools": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/Tool"},
                },
                "metadata": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
            },
        },
        "Tool": {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        },
    }
    module = _load_module(build_validator_module(schemas, ["CreateResponse"]))
    errors = module.validate_CreateResponse({"tools": [{}], "metadata": {"a": 1}})
    assert any(e["path"] == "$.tools[0].name" for e in errors)
    assert any(e["path"] == "$.metadata.a" for e in errors)


def test_emitter_uses_descriptive_helper_function_names() -> None:
    schemas = {
        "CreateResponse": {
            "type": "object",
            "properties": {
                "model": {"type": "string"},
                "metadata": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
            },
        }
    }

    code = build_validator_module(schemas, ["CreateResponse"])
    assert "_validate_CreateResponse_model" in code
    assert "_validate_CreateResponse_metadata" in code
    assert re.search(r"_validate_branch_\d+", code) is None
