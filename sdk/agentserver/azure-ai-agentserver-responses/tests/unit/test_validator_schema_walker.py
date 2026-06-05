# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
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


def test_schema_walker_follows_discriminator_mapping_refs() -> None:
    """Discriminator mapping targets must be walked so overlay can be applied to them."""
    schemas = {
        "Item": {
            "type": "object",
            "discriminator": {
                "propertyName": "type",
                "mapping": {
                    "message": "#/components/schemas/ItemMessage",
                    "tool_call": "#/components/schemas/ToolCall",
                },
            },
        },
        "ItemMessage": {
            "type": "object",
            "required": ["type", "role", "content"],
            "properties": {
                "type": {"type": "string"},
                "role": {"type": "string"},
                "content": {"type": "string"},
            },
        },
        "ToolCall": {
            "type": "object",
            "required": ["type", "name"],
            "properties": {
                "type": {"type": "string"},
                "name": {"type": "string"},
            },
        },
    }

    walker = SchemaWalker(schemas)
    walker.walk("Item")

    assert "ItemMessage" in walker.reachable
    assert "ToolCall" in walker.reachable


def test_schema_walker_applies_overlay_required_replacement() -> None:
    """overlay required: [] removes all required fields from a schema."""
    schemas = {
        "CreateResponse": {
            "type": "object",
            "required": ["model"],
            "properties": {"model": {"type": "string"}},
        }
    }
    overlay = {"schemas": {"CreateResponse": {"required": []}}}

    walker = SchemaWalker(schemas, overlay=overlay)
    walker.walk("CreateResponse")

    assert walker.reachable["CreateResponse"].get("required") == []


def test_schema_walker_applies_overlay_not_required() -> None:
    """overlay not_required removes a field from required and marks it nullable."""
    schemas = {
        "ItemMessage": {
            "type": "object",
            "required": ["type", "role", "content"],
            "properties": {
                "type": {"type": "string"},
                "role": {"type": "string"},
                "content": {"type": "string"},
            },
        }
    }
    overlay = {"schemas": {"ItemMessage": {"not_required": ["type"]}}}

    walker = SchemaWalker(schemas, overlay=overlay)
    walker.walk("ItemMessage")

    schema = walker.reachable["ItemMessage"]
    assert "type" not in schema["required"]
    assert schema["properties"]["type"].get("nullable") is True
    # role and content remain required
    assert "role" in schema["required"]
    assert "content" in schema["required"]


def test_schema_walker_applies_overlay_property_constraints() -> None:
    """overlay properties: merges per-property constraint overrides."""
    schemas = {
        "Config": {
            "type": "object",
            "properties": {"temperature": {"type": "number"}},
        }
    }
    overlay = {"schemas": {"Config": {"properties": {"temperature": {"minimum": 0, "maximum": 2}}}}}

    walker = SchemaWalker(schemas, overlay=overlay)
    walker.walk("Config")

    prop = walker.reachable["Config"]["properties"]["temperature"]
    assert prop["minimum"] == 0
    assert prop["maximum"] == 2


def test_schema_walker_overlay_matches_vendor_prefixed_schema_by_bare_name() -> None:
    """Overlay keys like 'ItemMessage' must match 'OpenAI.ItemMessage' in the spec."""
    schemas = {
        "OpenAI.ItemMessage": {
            "type": "object",
            "required": ["type", "role"],
            "properties": {
                "type": {"type": "string"},
                "role": {"type": "string"},
            },
        }
    }
    overlay = {"schemas": {"ItemMessage": {"not_required": ["type"]}}}

    walker = SchemaWalker(schemas, overlay=overlay)
    walker.walk("OpenAI.ItemMessage")

    schema = walker.reachable["OpenAI.ItemMessage"]
    assert "type" not in schema["required"]
    assert schema["properties"]["type"].get("nullable") is True


def test_schema_walker_applies_overlay_default_discriminator() -> None:
    """Overlay default_discriminator injects defaultValue into the discriminator dict."""
    schemas = {
        "OpenAI.Item": {
            "type": "object",
            "required": ["type"],
            "discriminator": {
                "propertyName": "type",
                "mapping": {"message": "#/components/schemas/ItemMessage"},
            },
            "properties": {"type": {"type": "string"}},
        }
    }
    overlay = {"schemas": {"Item": {"default_discriminator": "message"}}}

    walker = SchemaWalker(schemas, overlay=overlay)
    walker.walk("OpenAI.Item")

    disc = walker.reachable["OpenAI.Item"]["discriminator"]
    assert disc["defaultValue"] == "message"
