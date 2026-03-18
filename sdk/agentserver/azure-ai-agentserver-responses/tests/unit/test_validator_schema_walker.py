"""Tests for OpenAPI schema walker behavior used by validator generation."""

from __future__ import annotations

from scripts.validator_schema_walker import SchemaWalker, discover_post_request_roots, resolve_ref


def test_resolve_ref_extracts_schema_name() -> None:
    assert resolve_ref("#/components/schemas/CreateResponse") == "CreateResponse"


def test_schema_walker_collects_reachable_from_root_schema() -> None:
    schemas = {
        "CreateResponse": {
            "type": "object",
            "properties": {
                "metadata": {"$ref": "#/components/schemas/Metadata"},
            },
        },
        "Metadata": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
        },
    }

    walker = SchemaWalker(schemas)
    walker.walk("CreateResponse")

    assert "CreateResponse" in walker.reachable
    assert "Metadata" in walker.reachable


def test_schema_walker_discovers_inline_post_request_schema() -> None:
    spec = {
        "paths": {
            "/responses": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/CreateResponse",
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    assert discover_post_request_roots(spec) == ["CreateResponse"]


def test_schema_walker_handles_oneof_anyof_ref_branches() -> None:
    schemas = {
        "CreateResponse": {
            "type": "object",
            "properties": {
                "input": {
                    "oneOf": [
                        {"$ref": "#/components/schemas/InputText"},
                        {"$ref": "#/components/schemas/InputImage"},
                    ]
                },
                "tool_choice": {
                    "anyOf": [
                        {"type": "string"},
                        {"$ref": "#/components/schemas/ToolChoiceParam"},
                    ]
                },
            },
        },
        "InputText": {"type": "string"},
        "InputImage": {"type": "object", "properties": {"url": {"type": "string"}}},
        "ToolChoiceParam": {"type": "object", "properties": {"type": {"type": "string"}}},
    }

    walker = SchemaWalker(schemas)
    walker.walk("CreateResponse")

    assert "InputText" in walker.reachable
    assert "InputImage" in walker.reachable
    assert "ToolChoiceParam" in walker.reachable
