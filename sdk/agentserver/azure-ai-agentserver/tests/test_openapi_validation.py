# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for OpenAPI spec validation."""
import json

import httpx
import pytest

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver import AgentServer


# ---------------------------------------------------------------------------
# Helpers – inline agent + client builder
# ---------------------------------------------------------------------------


def _make_echo_agent(spec: dict) -> AgentServer:
    """Create an agent that echoes the parsed JSON body with validation."""

    class _EchoValidated(AgentServer):
        def __init__(self):
            super().__init__(openapi_spec=spec)

        async def invoke(self, request: Request) -> Response:
            data = await request.json()
            return JSONResponse(data)

    return _EchoValidated()


async def _client_for(agent: AgentServer):
    transport = httpx.ASGITransport(app=agent.app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


# ---------------------------------------------------------------------------
# Complex OpenAPI spec with nested objects, arrays, enums, $ref, constraints
# ---------------------------------------------------------------------------

COMPLEX_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "Complex Agent", "version": "2.0"},
    "components": {
        "schemas": {
            "Address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string", "minLength": 1},
                    "city": {"type": "string"},
                    "zip": {"type": "string", "pattern": "^[0-9]{5}$"},
                    "country": {"type": "string", "enum": ["US", "CA", "MX"]},
                },
                "required": ["street", "city", "zip", "country"],
            },
            "OrderItem": {
                "type": "object",
                "properties": {
                    "sku": {"type": "string", "minLength": 3, "maxLength": 12},
                    "quantity": {"type": "integer", "minimum": 1, "maximum": 999},
                    "unit_price": {"type": "number", "exclusiveMinimum": 0},
                },
                "required": ["sku", "quantity", "unit_price"],
            },
        }
    },
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "customer_name": {
                                        "type": "string",
                                        "minLength": 1,
                                        "maxLength": 100,
                                    },
                                    "email": {
                                        "type": "string",
                                        "format": "email",
                                    },
                                    "age": {
                                        "type": "integer",
                                        "minimum": 18,
                                        "maximum": 150,
                                    },
                                    "tier": {
                                        "type": "string",
                                        "enum": ["bronze", "silver", "gold", "platinum"],
                                    },
                                    "shipping_address": {
                                        "$ref": "#/components/schemas/Address"
                                    },
                                    "items": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/OrderItem"
                                        },
                                        "minItems": 1,
                                        "maxItems": 50,
                                    },
                                    "notes": {
                                        "type": "string",
                                    },
                                    "tags": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "uniqueItems": True,
                                    },
                                },
                                "required": [
                                    "customer_name",
                                    "age",
                                    "tier",
                                    "shipping_address",
                                    "items",
                                ],
                                "additionalProperties": False,
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Order accepted",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "order_id": {"type": "string"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        }
    },
}


def _valid_order(**overrides) -> dict:
    """Return a fully valid order payload, with optional field overrides."""
    base = {
        "customer_name": "Alice Smith",
        "age": 30,
        "tier": "gold",
        "shipping_address": {
            "street": "123 Main St",
            "city": "Redmond",
            "zip": "98052",
            "country": "US",
        },
        "items": [{"sku": "ABC123", "quantity": 2, "unit_price": 19.99}],
    }
    base.update(overrides)
    return base


# ===================================================================
# Original tests (kept as-is)
# ===================================================================


@pytest.mark.asyncio
async def test_valid_request_passes(validated_client):
    """Request matching schema returns 200."""
    resp = await validated_client.post(
        "/invocations",
        content=json.dumps({"name": "World"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data["greeting"] == "Hello, World!"


@pytest.mark.asyncio
async def test_invalid_request_returns_400(validated_client):
    """Request missing required field returns 400 with error details."""
    resp = await validated_client.post(
        "/invocations",
        content=json.dumps({"wrong_field": "oops"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "error" in data
    assert "details" in data


@pytest.mark.asyncio
async def test_invalid_request_wrong_type_returns_400(validated_client):
    """Request with wrong field type returns 400."""
    resp = await validated_client.post(
        "/invocations",
        content=json.dumps({"name": 12345}).encode(),
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "details" in data


@pytest.mark.asyncio
async def test_no_spec_skips_validation(no_spec_client):
    """Agent with no spec accepts any request body."""
    resp = await no_spec_client.post(
        "/invocations",
        content=b"this is not json at all",
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_spec_endpoint_returns_spec(validated_client):
    """GET /invocations/docs/openapi.json returns the registered spec."""
    resp = await validated_client.get("/invocations/docs/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert "paths" in data


@pytest.mark.asyncio
async def test_non_json_body_skips_validation(no_spec_client):
    """Non-JSON content type bypasses JSON schema validation."""
    class PlainTextEchoAgent(AgentServer):
        def __init__(self):
            super().__init__(openapi_spec={
                "openapi": "3.0.0",
                "info": {"title": "Test", "version": "1.0"},
                "paths": {
                    "/invocations": {
                        "post": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object", "required": ["name"]}
                                    }
                                }
                            },
                            "responses": {"200": {"description": "OK"}}
                        }
                    }
                }
            })

        async def invoke(self, request: Request) -> Response:
            body = await request.body()
            return Response(content=body, media_type="text/plain")

    agent = PlainTextEchoAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=b"plain text body",
            headers={"Content-Type": "text/plain"},
        )
        assert resp.status_code == 200


# ===================================================================
# Complex spec – valid payloads
# ===================================================================


@pytest.mark.asyncio
async def test_complex_valid_full_payload():
    """A fully-populated valid order is accepted."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        payload = _valid_order(
            email="alice@example.com",
            notes="Leave at the door",
            tags=["priority", "fragile"],
        )
        resp = await client.post(
            "/invocations",
            content=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_complex_valid_minimal_payload():
    """Only required fields are present — should pass."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order()).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_complex_valid_multiple_items():
    """Order with several line items passes."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        items = [
            {"sku": "AAA", "quantity": 1, "unit_price": 5.0},
            {"sku": "BBB", "quantity": 10, "unit_price": 12.50},
            {"sku": "CCC", "quantity": 999, "unit_price": 0.01},
        ]
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(items=items)).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


# ===================================================================
# Complex spec – missing required fields
# ===================================================================


@pytest.mark.asyncio
async def test_complex_missing_top_level_required():
    """Missing top-level required field 'tier' triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        payload = _valid_order()
        del payload["tier"]
        resp = await client.post(
            "/invocations",
            content=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        details = resp.json()["details"]
        assert any("tier" in d for d in details)


@pytest.mark.asyncio
async def test_complex_missing_nested_required():
    """Missing required 'city' in shipping_address triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        payload = _valid_order()
        del payload["shipping_address"]["city"]
        resp = await client.post(
            "/invocations",
            content=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        details = resp.json()["details"]
        assert any("city" in d for d in details)


@pytest.mark.asyncio
async def test_complex_missing_array_item_field():
    """Order item missing required 'sku' field triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        bad_item = {"quantity": 1, "unit_price": 5.0}  # no sku
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(items=[bad_item])).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        details = resp.json()["details"]
        assert any("sku" in d for d in details)


# ===================================================================
# Complex spec – type mismatches
# ===================================================================


@pytest.mark.asyncio
async def test_complex_wrong_type_age_string():
    """'age' must be integer, not string."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(age="thirty")).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_wrong_type_items_not_array():
    """'items' must be an array, not an object."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(
                _valid_order(items={"sku": "X", "quantity": 1, "unit_price": 1.0})
            ).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_wrong_type_quantity_float():
    """'quantity' must be integer, not float."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        bad_item = {"sku": "ABC", "quantity": 2.5, "unit_price": 10.0}
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(items=[bad_item])).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


# ===================================================================
# Complex spec – enum validation
# ===================================================================


@pytest.mark.asyncio
async def test_complex_invalid_tier_enum():
    """'tier' value not in enum list triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(tier="diamond")).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        details = resp.json()["details"]
        assert any("diamond" in d for d in details)


@pytest.mark.asyncio
async def test_complex_invalid_country_enum():
    """'country' outside allowed enum triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        payload = _valid_order()
        payload["shipping_address"]["country"] = "FR"
        resp = await client.post(
            "/invocations",
            content=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        details = resp.json()["details"]
        assert any("FR" in d for d in details)


# ===================================================================
# Complex spec – numeric constraints (minimum / maximum)
# ===================================================================


@pytest.mark.asyncio
async def test_complex_age_below_minimum():
    """'age' below minimum (18) triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(age=10)).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_age_above_maximum():
    """'age' above maximum (150) triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(age=200)).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_quantity_below_minimum():
    """Order item quantity below 1 triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        bad_item = {"sku": "ABC", "quantity": 0, "unit_price": 10.0}
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(items=[bad_item])).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_quantity_above_maximum():
    """Order item quantity above 999 triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        bad_item = {"sku": "ABC", "quantity": 1000, "unit_price": 10.0}
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(items=[bad_item])).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_unit_price_zero_exclusive():
    """unit_price with exclusiveMinimum: 0 rejects exactly 0."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        bad_item = {"sku": "ABC", "quantity": 1, "unit_price": 0}
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(items=[bad_item])).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


# ===================================================================
# Complex spec – string constraints (minLength / maxLength / pattern)
# ===================================================================


@pytest.mark.asyncio
async def test_complex_customer_name_empty():
    """Empty customer_name violates minLength: 1."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(customer_name="")).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_customer_name_too_long():
    """customer_name exceeding maxLength: 100 triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(customer_name="A" * 101)).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_sku_too_short():
    """SKU shorter than minLength: 3 triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        bad_item = {"sku": "AB", "quantity": 1, "unit_price": 5.0}
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(items=[bad_item])).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_sku_too_long():
    """SKU longer than maxLength: 12 triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        bad_item = {"sku": "A" * 13, "quantity": 1, "unit_price": 5.0}
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(items=[bad_item])).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_zip_pattern_invalid():
    """Zip code not matching '^[0-9]{5}$' triggers 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        payload = _valid_order()
        payload["shipping_address"]["zip"] = "ABCDE"
        resp = await client.post(
            "/invocations",
            content=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_zip_pattern_too_short():
    """Zip code with fewer than 5 digits fails pattern."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        payload = _valid_order()
        payload["shipping_address"]["zip"] = "1234"
        resp = await client.post(
            "/invocations",
            content=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


# ===================================================================
# Complex spec – array constraints (minItems / maxItems / uniqueItems)
# ===================================================================


@pytest.mark.asyncio
async def test_complex_empty_items_array():
    """Empty items array violates minItems: 1."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(items=[])).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_duplicate_tags():
    """Duplicate entries in 'tags' violates uniqueItems."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(
                _valid_order(tags=["urgent", "urgent"])
            ).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


# ===================================================================
# Complex spec – additionalProperties: false
# ===================================================================


@pytest.mark.asyncio
async def test_complex_additional_properties_rejected():
    """Extra top-level field rejected by additionalProperties: false."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        payload = _valid_order()
        payload["surprise_field"] = "not allowed"
        resp = await client.post(
            "/invocations",
            content=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        details = resp.json()["details"]
        assert any("surprise_field" in d for d in details)


# ===================================================================
# Complex spec – $ref resolution
# ===================================================================


@pytest.mark.asyncio
async def test_complex_ref_address_validated():
    """$ref to Address schema is resolved and validated."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        payload = _valid_order()
        # Replace structured address with a scalar — violates $ref schema
        payload["shipping_address"] = "123 Main St"
        resp = await client.post(
            "/invocations",
            content=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_complex_ref_order_item_validated():
    """$ref to OrderItem schema is resolved; invalid item caught."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        # unit_price negative — violates exclusiveMinimum
        bad_item = {"sku": "ABC", "quantity": 1, "unit_price": -5.0}
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(items=[bad_item])).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


# ===================================================================
# Complex spec – malformed JSON body
# ===================================================================


@pytest.mark.asyncio
async def test_complex_malformed_json():
    """Malformed JSON body returns 400."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=b"{not json at all",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data


# ===================================================================
# Complex spec – boundary / edge-case valid values
# ===================================================================


@pytest.mark.asyncio
async def test_complex_boundary_age_exactly_minimum():
    """Age exactly at minimum (18) should pass."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(age=18)).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_complex_boundary_age_exactly_maximum():
    """Age exactly at maximum (150) should pass."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(age=150)).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_complex_boundary_sku_exactly_min_length():
    """SKU at exactly minLength: 3 should pass."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        item = {"sku": "XYZ", "quantity": 1, "unit_price": 1.0}
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(items=[item])).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_complex_boundary_sku_exactly_max_length():
    """SKU at exactly maxLength: 12 should pass."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        item = {"sku": "A" * 12, "quantity": 1, "unit_price": 1.0}
        resp = await client.post(
            "/invocations",
            content=json.dumps(_valid_order(items=[item])).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_complex_multiple_errors_reported():
    """Multiple validation errors are all reported in 'details'."""
    agent = _make_echo_agent(COMPLEX_SPEC)
    async with await _client_for(agent) as client:
        # Wrong type for age, invalid enum for tier, empty items array
        payload = {
            "customer_name": "Bob",
            "age": "old",
            "tier": "diamond",
            "shipping_address": {
                "street": "1 Elm",
                "city": "X",
                "zip": "00000",
                "country": "US",
            },
            "items": [],
        }
        resp = await client.post(
            "/invocations",
            content=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        details = resp.json()["details"]
        assert len(details) >= 3  # at least age, tier, items errors


# ---------------------------------------------------------------------------
# Tests: validate_response
# ---------------------------------------------------------------------------

RESPONSE_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "Resp", "version": "1.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"},
                        }
                    }
                },
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "result": {"type": "string"},
                                    },
                                    "required": ["result"],
                                }
                            }
                        }
                    }
                },
            }
        }
    },
}


@pytest.mark.asyncio
async def test_validate_response_valid():
    """Valid response body passes validation."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    v = OpenApiValidator(RESPONSE_SPEC)
    errors = v.validate_response(b'{"result": "ok"}', "application/json")
    assert errors == []


@pytest.mark.asyncio
async def test_validate_response_invalid():
    """Invalid response body returns errors."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    v = OpenApiValidator(RESPONSE_SPEC)
    errors = v.validate_response(b'{"wrong": 42}', "application/json")
    assert len(errors) > 0


@pytest.mark.asyncio
async def test_validate_response_no_schema():
    """When no response schema exists, validation passes (no-op)."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    spec_no_resp = {
        "openapi": "3.0.0",
        "info": {"title": "NoResp", "version": "1.0"},
        "paths": {"/invocations": {"post": {}}},
    }
    v = OpenApiValidator(spec_no_resp)
    errors = v.validate_response(b'{"anything": true}', "application/json")
    assert errors == []


# ---------------------------------------------------------------------------
# Tests: no request body schema
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_request_no_schema():
    """When no request schema exists, validation passes (no-op)."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    spec_no_req = {
        "openapi": "3.0.0",
        "info": {"title": "NoReq", "version": "1.0"},
        "paths": {"/invocations": {"post": {}}},
    }
    v = OpenApiValidator(spec_no_req)
    errors = v.validate_request(b'{"anything": true}', "application/json")
    assert errors == []


# ---------------------------------------------------------------------------
# Tests: response schema from non-200/201 status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_response_schema_fallback_to_first_available():
    """Response schema extraction falls back to first response with JSON."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Fallback", "version": "1.0"},
        "paths": {
            "/invocations": {
                "post": {
                    "responses": {
                        "202": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"status": {"type": "string"}},
                                        "required": ["status"],
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
    }
    v = OpenApiValidator(spec)
    # Valid against the 202 schema
    assert v.validate_response(b'{"status": "accepted"}', "application/json") == []
    # Invalid — missing "status"
    errors = v.validate_response(b'{"other": 1}', "application/json")
    assert len(errors) > 0


# ---------------------------------------------------------------------------
# Tests: $ref edge cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unresolvable_ref():
    """An unresolvable $ref leaves the node as-is (no crash)."""
    from azure.ai.agentserver.validation._openapi_validator import _resolve_ref

    spec: dict = {"components": {"schemas": {}}}
    node = {"$ref": "#/components/schemas/DoesNotExist"}
    result = _resolve_ref(spec, node)
    # Can't resolve — returns the original node
    assert result is node


@pytest.mark.asyncio
async def test_ref_path_hits_non_dict():
    """A $ref path that traverses a non-dict returns the original node."""
    from azure.ai.agentserver.validation._openapi_validator import _resolve_ref

    spec: dict = {"components": {"schemas": "not-a-dict"}}
    node = {"$ref": "#/components/schemas/Foo"}
    result = _resolve_ref(spec, node)
    assert result is node


@pytest.mark.asyncio
async def test_circular_ref_stops_recursion():
    """Circular $ref does not cause infinite recursion."""
    from azure.ai.agentserver.validation._openapi_validator import _resolve_refs_deep

    spec: dict = {
        "components": {
            "schemas": {
                "Node": {
                    "type": "object",
                    "properties": {
                        "child": {"$ref": "#/components/schemas/Node"},
                    },
                }
            }
        }
    }
    node = {"$ref": "#/components/schemas/Node"}
    result = _resolve_refs_deep(spec, node)
    # Should resolve at least the first level, and leave the circular ref as-is
    assert result["type"] == "object"
    child = result["properties"]["child"]
    # The circular reference should be left unresolved
    assert "$ref" in child


@pytest.mark.asyncio
async def test_ref_resolves_to_non_dict():
    """A $ref that resolves to a non-dict value returns the original node."""
    from azure.ai.agentserver.validation._openapi_validator import _resolve_ref

    spec: dict = {"components": {"schemas": {"Bad": 42}}}
    node = {"$ref": "#/components/schemas/Bad"}
    result = _resolve_ref(spec, node)
    assert result is node
