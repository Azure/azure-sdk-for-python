# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline wire contracts for agent endpoint access-boundary authorization."""

import json

import pytest

from azure.ai.projects import models


@pytest.mark.parametrize(
    "responds_to",
    [
        pytest.param([models.ReadAccessResponder.ALLOWLISTED], id="enum"),
        pytest.param(["allowlisted"], id="string"),
        pytest.param([], id="deny-user-messages"),
    ],
)
def test_access_boundary_authorization_serializes_in_endpoint(responds_to):
    endpoint = models.AgentEndpointConfig(
        authorization_schemes=[
            models.AccessBoundaryAuthorizationScheme(read=models.ReadAccessPolicy(responds_to=responds_to))
        ]
    )
    expected = {"authorization_schemes": [{"type": "AccessBoundary", "read": {"responds_to": list(responds_to)}}]}

    assert json.loads(json.dumps(endpoint.as_dict(exclude_readonly=True))) == expected


@pytest.mark.parametrize(
    "responds_to",
    [
        pytest.param(["allowlisted"], id="allowlisted"),
        pytest.param([], id="deny-user-messages"),
        pytest.param(["allowlisted", "future_responder"], id="unknown-response-value"),
    ],
)
def test_access_boundary_authorization_deserializes_in_endpoint(responds_to):
    wire = {"authorization_schemes": [{"type": "AccessBoundary", "read": {"responds_to": responds_to}}]}
    endpoint = models.AgentEndpointConfig(wire)

    assert endpoint.authorization_schemes is not None
    assert len(endpoint.authorization_schemes) == 1
    scheme = endpoint.authorization_schemes[0]
    assert isinstance(scheme, models.AccessBoundaryAuthorizationScheme)
    assert scheme.type == models.AgentEndpointAuthorizationSchemeType.ACCESS_BOUNDARY
    assert isinstance(scheme.read, models.ReadAccessPolicy)
    assert scheme.read.responds_to == responds_to
    assert endpoint.as_dict() == wire
