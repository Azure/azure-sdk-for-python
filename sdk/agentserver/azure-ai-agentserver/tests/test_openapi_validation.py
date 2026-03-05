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
from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator


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
    assert data["error"]["code"] == "invalid_payload"
    assert "details" in data["error"]


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
    assert "details" in data["error"]


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
        details = resp.json()["error"]["details"]
        assert any("tier" in d["message"] for d in details)


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
        details = resp.json()["error"]["details"]
        assert any("city" in d["message"] for d in details)


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
        details = resp.json()["error"]["details"]
        assert any("sku" in d["message"] for d in details)


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
        details = resp.json()["error"]["details"]
        assert any("diamond" in d["message"] for d in details)


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
        details = resp.json()["error"]["details"]
        assert any("FR" in d["message"] for d in details)


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
        details = resp.json()["error"]["details"]
        assert any("surprise_field" in d["message"] for d in details)


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
        assert data["error"]["code"] == "invalid_payload"


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
        details = resp.json()["error"]["details"]
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


# ===================================================================
# OpenAPI nullable support
# ===================================================================

NULLABLE_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "Nullable", "version": "1.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "nickname": {
                                        "type": "string",
                                        "nullable": True,
                                    },
                                    "age": {
                                        "type": "integer",
                                        "nullable": True,
                                    },
                                },
                                "required": ["name", "nickname"],
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "OK"}},
            }
        }
    },
}


@pytest.mark.asyncio
async def test_nullable_accepts_null():
    """A nullable field accepts a JSON null value."""
    agent = _make_echo_agent(NULLABLE_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"name": "Alice", "nickname": None}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_nullable_accepts_value():
    """A nullable field also accepts a normal string value."""
    agent = _make_echo_agent(NULLABLE_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"name": "Alice", "nickname": "Ali"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_nullable_rejects_wrong_type():
    """A nullable string still rejects integers."""
    agent = _make_echo_agent(NULLABLE_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"name": "Alice", "nickname": 42}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_non_nullable_rejects_null():
    """A non-nullable field (name) rejects null."""
    agent = _make_echo_agent(NULLABLE_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"name": None, "nickname": "Ali"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_nullable_integer_accepts_null():
    """A nullable integer accepts null."""
    agent = _make_echo_agent(NULLABLE_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"name": "A", "nickname": "B", "age": None}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


# ===================================================================
# readOnly / writeOnly support
# ===================================================================

READONLY_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "ReadOnly", "version": "1.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "id": {
                                        "type": "string",
                                        "readOnly": True,
                                    },
                                    "password": {
                                        "type": "string",
                                        "writeOnly": True,
                                    },
                                },
                                "required": ["name", "id"],
                            }
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
                                        "name": {"type": "string"},
                                        "id": {
                                            "type": "string",
                                            "readOnly": True,
                                        },
                                        "password": {
                                            "type": "string",
                                            "writeOnly": True,
                                        },
                                    },
                                    "required": ["name", "id"],
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
async def test_readonly_not_required_in_request():
    """readOnly field 'id' is stripped from required in request context."""
    agent = _make_echo_agent(READONLY_SPEC)
    async with await _client_for(agent) as client:
        # Don't send 'id' — it's readOnly, should not be required
        resp = await client.post(
            "/invocations",
            content=json.dumps({"name": "Alice"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_writeonly_allowed_in_request():
    """writeOnly field 'password' is allowed in request."""
    agent = _make_echo_agent(READONLY_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"name": "Alice", "password": "secret"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_readonly_schema_introspection_request():
    """readOnly properties are removed from the preprocessed request schema."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    v = OpenApiValidator(READONLY_SPEC)
    # 'id' should be gone from requestschema properties
    assert "id" not in v._request_schema.get("properties", {})


@pytest.mark.asyncio
async def test_readonly_schema_introspection_response():
    """readOnly properties remain in the preprocessed response schema."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    v = OpenApiValidator(READONLY_SPEC)
    # 'id' should still be in response schema
    assert "id" in v._response_schema.get("properties", {})


@pytest.mark.asyncio
async def test_writeonly_stripped_in_response():
    """writeOnly properties are removed from the preprocessed response schema."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    v = OpenApiValidator(READONLY_SPEC)
    assert "password" not in v._response_schema.get("properties", {})


@pytest.mark.asyncio
async def test_writeonly_present_in_request():
    """writeOnly properties remain in the preprocessed request schema."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    v = OpenApiValidator(READONLY_SPEC)
    assert "password" in v._request_schema.get("properties", {})


# ===================================================================
# requestBody.required: false
# ===================================================================

OPTIONAL_BODY_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "OptionalBody", "version": "1.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "required": False,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"},
                                },
                                "required": ["query"],
                            }
                        }
                    },
                },
                "responses": {"200": {"description": "OK"}},
            }
        }
    },
}

REQUIRED_BODY_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "RequiredBody", "version": "1.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"},
                                },
                                "required": ["query"],
                            }
                        }
                    },
                },
                "responses": {"200": {"description": "OK"}},
            }
        }
    },
}


@pytest.mark.asyncio
async def test_optional_body_empty_accepted():
    """Empty body is accepted when requestBody.required is false."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    v = OpenApiValidator(OPTIONAL_BODY_SPEC)
    errors = v.validate_request(b"", "application/json")
    assert errors == []


@pytest.mark.asyncio
async def test_optional_body_whitespace_accepted():
    """Whitespace-only body is accepted when requestBody.required is false."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    v = OpenApiValidator(OPTIONAL_BODY_SPEC)
    errors = v.validate_request(b"   ", "application/json")
    assert errors == []


@pytest.mark.asyncio
async def test_optional_body_present_still_validated():
    """When body IS present with optional requestBody, it still must be valid."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    v = OpenApiValidator(OPTIONAL_BODY_SPEC)
    errors = v.validate_request(b'{"wrong": 1}', "application/json")
    assert len(errors) > 0


@pytest.mark.asyncio
async def test_required_body_empty_rejected():
    """Empty body is rejected when requestBody.required is true."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    v = OpenApiValidator(REQUIRED_BODY_SPEC)
    errors = v.validate_request(b"", "application/json")
    assert len(errors) > 0  # "Invalid JSON body"


@pytest.mark.asyncio
async def test_default_body_required_behavior():
    """When requestBody.required is omitted, body is required by default."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Default", "version": "1.0"},
        "paths": {
            "/invocations": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "required": ["q"]},
                            }
                        }
                    },
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
    }
    v = OpenApiValidator(spec)
    errors = v.validate_request(b"", "application/json")
    assert len(errors) > 0


# ===================================================================
# OpenAPI keyword stripping
# ===================================================================


@pytest.mark.asyncio
async def test_openapi_keywords_stripped():
    """discriminator, xml, externalDocs, example are stripped from schemas."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    schema = {
        "type": "object",
        "discriminator": {"propertyName": "type"},
        "xml": {"name": "Foo"},
        "externalDocs": {"url": "https://example.com"},
        "example": {"type": "bar"},
        "properties": {"name": {"type": "string"}},
    }
    result = OpenApiValidator._preprocess_schema(schema)
    assert "discriminator" not in result
    assert "xml" not in result
    assert "externalDocs" not in result
    assert "example" not in result
    assert result["properties"]["name"]["type"] == "string"


@pytest.mark.asyncio
async def test_openapi_keywords_stripped_nested():
    """OpenAPI keywords are stripped from nested properties too."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    schema = {
        "type": "object",
        "properties": {
            "child": {
                "type": "object",
                "example": {"key": "value"},
                "xml": {"wrapped": True},
                "properties": {"inner": {"type": "string"}},
            }
        },
    }
    result = OpenApiValidator._preprocess_schema(schema)
    child = result["properties"]["child"]
    assert "example" not in child
    assert "xml" not in child


# ===================================================================
# Format validation (enabled via FormatChecker)
# ===================================================================

FORMAT_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "Format", "version": "1.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {
                                        "type": "string",
                                        "format": "email",
                                    },
                                    "created_at": {
                                        "type": "string",
                                        "format": "date-time",
                                    },
                                },
                                "required": ["email"],
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "OK"}},
            }
        }
    },
}


@pytest.mark.asyncio
async def test_format_email_valid():
    """Valid email passes format validation."""
    agent = _make_echo_agent(FORMAT_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"email": "alice@example.com"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_format_email_invalid():
    """Invalid email fails format validation."""
    agent = _make_echo_agent(FORMAT_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"email": "not-an-email"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_format_datetime_valid():
    """Valid ISO 8601 date-time passes format validation."""
    agent = _make_echo_agent(FORMAT_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(
                {"email": "a@b.com", "created_at": "2025-01-01T00:00:00Z"}
            ).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_format_datetime_invalid():
    """Invalid date-time fails format validation."""
    agent = _make_echo_agent(FORMAT_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(
                {"email": "a@b.com", "created_at": "not-a-date"}
            ).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


# ===================================================================
# allOf / oneOf / anyOf composition
# ===================================================================

COMPOSITION_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "Composition", "version": "1.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "allOf": [
                                    {
                                        "type": "object",
                                        "properties": {"name": {"type": "string"}},
                                        "required": ["name"],
                                    },
                                    {
                                        "type": "object",
                                        "properties": {"age": {"type": "integer"}},
                                        "required": ["age"],
                                    },
                                ]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "OK"}},
            }
        }
    },
}

ONEOF_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "OneOf", "version": "1.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "oneOf": [
                                    {
                                        "type": "object",
                                        "properties": {
                                            "kind": {
                                                "type": "string",
                                                "enum": ["cat"],
                                            },
                                            "purrs": {"type": "boolean"},
                                        },
                                        "required": ["kind", "purrs"],
                                    },
                                    {
                                        "type": "object",
                                        "properties": {
                                            "kind": {
                                                "type": "string",
                                                "enum": ["dog"],
                                            },
                                            "barks": {"type": "boolean"},
                                        },
                                        "required": ["kind", "barks"],
                                    },
                                ]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "OK"}},
            }
        }
    },
}

ANYOF_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "AnyOf", "version": "1.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "anyOf": [
                                    {"type": "string"},
                                    {"type": "integer"},
                                ]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "OK"}},
            }
        }
    },
}


@pytest.mark.asyncio
async def test_allof_valid():
    """allOf: both sub-schemas satisfied → 200."""
    agent = _make_echo_agent(COMPOSITION_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"name": "Alice", "age": 30}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_allof_missing_field():
    """allOf: missing field from second schema → 400."""
    agent = _make_echo_agent(COMPOSITION_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"name": "Alice"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_oneof_first_branch():
    """oneOf: matching first branch (cat) → 200."""
    agent = _make_echo_agent(ONEOF_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"kind": "cat", "purrs": True}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_oneof_second_branch():
    """oneOf: matching second branch (dog) → 200."""
    agent = _make_echo_agent(ONEOF_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"kind": "dog", "barks": True}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_oneof_no_match():
    """oneOf: matching neither branch → 400."""
    agent = _make_echo_agent(ONEOF_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps({"kind": "fish"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_anyof_string():
    """anyOf: string value matches first branch → 200."""
    agent = _make_echo_agent(ANYOF_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps("hello").encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_anyof_integer():
    """anyOf: integer value matches second branch → 200."""
    agent = _make_echo_agent(ANYOF_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(42).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_anyof_wrong_type():
    """anyOf: boolean matches neither string nor integer → 400."""
    agent = _make_echo_agent(ANYOF_SPEC)
    async with await _client_for(agent) as client:
        resp = await client.post(
            "/invocations",
            content=json.dumps(True).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400


# ===================================================================
# nullable + $ref combination
# ===================================================================


@pytest.mark.asyncio
async def test_nullable_ref_accepts_null():
    """A nullable $ref field accepts null after preprocessing."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    spec: dict = {
        "openapi": "3.0.0",
        "info": {"title": "NullRef", "version": "1.0"},
        "components": {
            "schemas": {
                "Address": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                }
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
                                        "addr": {
                                            "$ref": "#/components/schemas/Address",
                                            "nullable": True,
                                        }
                                    },
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
    }
    v = OpenApiValidator(spec)
    errors = v.validate_request(b'{"addr": null}', "application/json")
    assert errors == []


# ===================================================================
# Preprocessing unit tests
# ===================================================================


@pytest.mark.asyncio
async def test_apply_nullable_no_duplicate_null():
    """_apply_nullable does not add 'null' twice if type is already a list with null."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    schema: dict = {"type": ["string", "null"], "nullable": True}
    OpenApiValidator._apply_nullable(schema)
    assert schema["type"] == ["string", "null"]


@pytest.mark.asyncio
async def test_apply_nullable_false():
    """nullable: false is a no-op (just removes the key)."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    schema: dict = {"type": "string", "nullable": False}
    OpenApiValidator._apply_nullable(schema)
    assert schema["type"] == "string"
    assert "nullable" not in schema


@pytest.mark.asyncio
async def test_strip_openapi_keywords_nested_deeply():
    """OpenAPI keywords are stripped from deeply nested schemas."""
    from azure.ai.agentserver.validation._openapi_validator import OpenApiValidator

    schema: dict = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "example": {"deep": True},
                    "properties": {
                        "val": {"type": "string", "xml": {"attr": True}},
                    },
                },
            }
        },
    }
    OpenApiValidator._strip_openapi_keywords(schema)
    items_schema = schema["properties"]["items"]["items"]
    assert "example" not in items_schema
    assert "xml" not in items_schema["properties"]["val"]


# ===================================================================
# Discriminator-aware error collection (ported from C# JsonSchemaValidator)
# ===================================================================

# --- Helper: direct validator call for unit-level assertions ---

def _validate_request(spec: dict, body: dict) -> list[str]:
    """Shortcut: build an OpenApiValidator and return request errors."""
    v = OpenApiValidator(spec)
    return v.validate_request(
        json.dumps(body).encode(),
        "application/json",
    )


# Spec with const-based discriminator (Azure-style polymorphic schema)
CONST_DISCRIMINATOR_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "Disc", "version": "1.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "oneOf": [
                                    {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string", "const": "workflow"},
                                            "steps": {"type": "array", "items": {"type": "string"}},
                                        },
                                        "required": ["type", "steps"],
                                    },
                                    {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string", "const": "prompt"},
                                            "text": {"type": "string"},
                                        },
                                        "required": ["type", "text"],
                                    },
                                    {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string", "const": "tool_call"},
                                            "tool_name": {"type": "string"},
                                            "args": {"type": "object"},
                                        },
                                        "required": ["type", "tool_name"],
                                    },
                                ]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "OK"}},
            }
        }
    },
}


@pytest.mark.asyncio
async def test_discriminator_valid_workflow():
    """const discriminator: valid workflow branch → passes."""
    errors = _validate_request(
        CONST_DISCRIMINATOR_SPEC,
        {"type": "workflow", "steps": ["a", "b"]},
    )
    assert errors == []


@pytest.mark.asyncio
async def test_discriminator_valid_prompt():
    """const discriminator: valid prompt branch → passes."""
    errors = _validate_request(
        CONST_DISCRIMINATOR_SPEC,
        {"type": "prompt", "text": "hello"},
    )
    assert errors == []


@pytest.mark.asyncio
async def test_discriminator_valid_tool_call():
    """const discriminator: valid tool_call branch → passes."""
    errors = _validate_request(
        CONST_DISCRIMINATOR_SPEC,
        {"type": "tool_call", "tool_name": "search"},
    )
    assert errors == []


@pytest.mark.asyncio
async def test_discriminator_reports_matching_branch_errors():
    """const discriminator: correct type but missing required field → reports only that branch."""
    errors = _validate_request(
        CONST_DISCRIMINATOR_SPEC,
        {"type": "workflow"},  # missing "steps"
    )
    assert len(errors) >= 1
    # Should report the missing "steps" field, not errors from prompt/tool_call branches
    assert any("steps" in e for e in errors)
    # Should NOT mention fields from other branches
    assert not any("text" in e for e in errors)
    assert not any("tool_name" in e for e in errors)


@pytest.mark.asyncio
async def test_discriminator_unknown_value_reports_expected():
    """const discriminator: unknown type value → concise 'Expected one of' message."""
    errors = _validate_request(
        CONST_DISCRIMINATOR_SPEC,
        {"type": "unknown_thing", "steps": ["a"]},
    )
    assert len(errors) >= 1
    # Should mention the expected values, not dump all branch errors
    combined = " ".join(errors)
    assert "Expected" in combined or "type" in combined


@pytest.mark.asyncio
async def test_discriminator_wrong_type_value():
    """const discriminator: type field is integer instead of string → type error reported."""
    errors = _validate_request(
        CONST_DISCRIMINATOR_SPEC,
        {"type": 123, "steps": ["a"]},
    )
    assert len(errors) >= 1
    combined = " ".join(errors)
    assert "type" in combined


@pytest.mark.asyncio
async def test_discriminator_missing_type_field():
    """const discriminator: missing discriminator field entirely → error."""
    errors = _validate_request(
        CONST_DISCRIMINATOR_SPEC,
        {"steps": ["a"]},
    )
    assert len(errors) >= 1


# Spec with enum-based discriminator (the existing ONEOF_SPEC pattern)
@pytest.mark.asyncio
async def test_enum_discriminator_matching_branch_errors():
    """enum discriminator: correct kind but missing required field → branch-specific errors."""
    errors = _validate_request(
        ONEOF_SPEC,
        {"kind": "cat"},  # missing "purrs"
    )
    assert len(errors) >= 1
    assert any("purrs" in e for e in errors)
    # Should not mention "barks" from the dog branch
    assert not any("barks" in e for e in errors)


# --- JSON path in error messages ---

@pytest.mark.asyncio
async def test_error_includes_json_path_for_nested_property():
    """Validation errors for nested properties include the JSON path prefix."""
    errors = _validate_request(
        COMPLEX_SPEC,
        {
            "customer_name": "Bob",
            "tier": "gold",
            "shipping_address": {
                "street": "1 Elm",
                # missing "city"
                "zip": "00000",
                "country": "US",
            },
            "items": [{"sku": "ABCD", "quantity": 1, "unit_price": 9.99}],
        },
    )
    assert len(errors) >= 1
    # At least one error should contain a JSON-path-like prefix
    assert any("$." in e or "city" in e for e in errors)


@pytest.mark.asyncio
async def test_error_includes_json_path_for_array_item():
    """Validation errors inside array items include the element index in the path."""
    errors = _validate_request(
        COMPLEX_SPEC,
        {
            "customer_name": "Bob",
            "tier": "gold",
            "shipping_address": {
                "street": "1 Elm",
                "city": "X",
                "zip": "00000",
                "country": "US",
            },
            "items": [{"quantity": 1, "unit_price": 9.99}],  # missing "sku"
        },
    )
    assert len(errors) >= 1
    assert any("items" in e for e in errors)


# --- Spec with nested oneOf inside properties ---

NESTED_ONEOF_SPEC: dict = {
    "openapi": "3.0.0",
    "info": {"title": "NestedOneOf", "version": "1.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "payload": {
                                        "oneOf": [
                                            {
                                                "type": "object",
                                                "properties": {
                                                    "kind": {"type": "string", "const": "text"},
                                                    "content": {"type": "string"},
                                                },
                                                "required": ["kind", "content"],
                                            },
                                            {
                                                "type": "object",
                                                "properties": {
                                                    "kind": {"type": "string", "const": "image"},
                                                    "url": {"type": "string", "format": "uri"},
                                                },
                                                "required": ["kind", "url"],
                                            },
                                        ],
                                    },
                                },
                                "required": ["name", "payload"],
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "OK"}},
            }
        }
    },
}


@pytest.mark.asyncio
async def test_nested_oneof_valid_text():
    """Nested oneOf: valid text payload → passes."""
    errors = _validate_request(
        NESTED_ONEOF_SPEC,
        {"name": "test", "payload": {"kind": "text", "content": "hello"}},
    )
    assert errors == []


@pytest.mark.asyncio
async def test_nested_oneof_valid_image():
    """Nested oneOf: valid image payload → passes."""
    errors = _validate_request(
        NESTED_ONEOF_SPEC,
        {"name": "test", "payload": {"kind": "image", "url": "https://example.com/img.png"}},
    )
    assert errors == []


@pytest.mark.asyncio
async def test_nested_oneof_wrong_discriminator():
    """Nested oneOf: unknown discriminator value → error mentioning payload path."""
    errors = _validate_request(
        NESTED_ONEOF_SPEC,
        {"name": "test", "payload": {"kind": "video", "url": "https://example.com/v.mp4"}},
    )
    assert len(errors) >= 1
    combined = " ".join(errors)
    # Should mention "payload" in the path
    assert "payload" in combined


@pytest.mark.asyncio
async def test_nested_oneof_matching_branch_missing_field():
    """Nested oneOf: correct kind=text but missing content → branch-specific error."""
    errors = _validate_request(
        NESTED_ONEOF_SPEC,
        {"name": "test", "payload": {"kind": "text"}},
    )
    assert len(errors) >= 1
    assert any("content" in e for e in errors)
    # Should NOT mention "url" from the image branch
    assert not any("url" in e for e in errors)


# --- Unit-level tests for helper functions ---

@pytest.mark.asyncio
async def test_format_error_includes_path():
    """_format_error prefixes with JSON path when not root."""
    from azure.ai.agentserver.validation._openapi_validator import _format_error
    import jsonschema

    schema = {"type": "object", "properties": {"age": {"type": "integer"}}, "required": ["age"]}
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors({"age": "not_int"}))
    assert len(errors) == 1
    formatted = _format_error(errors[0])
    assert "$.age" in formatted


@pytest.mark.asyncio
async def test_format_error_root_path_no_prefix():
    """_format_error does not prefix when error is at root ($)."""
    from azure.ai.agentserver.validation._openapi_validator import _format_error
    import jsonschema

    schema = {"type": "object", "required": ["name"]}
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors({}))
    assert len(errors) == 1
    formatted = _format_error(errors[0])
    # Root-level error — should be the message without "$.xxx:" prefix
    assert formatted == errors[0].message


@pytest.mark.asyncio
async def test_collect_errors_flat():
    """_collect_errors for a simple (non-composition) error returns path-prefixed message."""
    from azure.ai.agentserver.validation._openapi_validator import _collect_errors
    import jsonschema

    schema = {"type": "object", "properties": {"x": {"type": "integer"}}}
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors({"x": "abc"}))
    collected = []
    for e in errors:
        collected.extend(_collect_errors(e))
    assert len(collected) == 1
    assert "$.x" in collected[0]
