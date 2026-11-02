# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import get_type_hints

import pytest

from azure.ai.projects import operations
from azure.ai.projects.aio import operations as async_operations
from azure.ai.projects.models import (
    PhoneNumber,
    SipAddress,
    TeamsAddress,
    TelephonyTransferTarget,
    UpdateTelephonyBindingRequest,
)


@pytest.mark.parametrize(
    "address_model,address_type,value",
    [
        (PhoneNumber, "phone_number", "+15555550123"),
        (SipAddress, "sip", "sip:support@example.com"),
        (TeamsAddress, "teams", "00000000-0000-0000-0000-000000000001"),
    ],
)
def test_telephony_transfer_address_round_trip(address_model, address_type, value):
    target = TelephonyTransferTarget(
        name="support",
        description="Transfer to support.",
        destination=address_model(value=value),
    )
    payload = {
        "name": "support",
        "description": "Transfer to support.",
        "destination": {"type": address_type, "value": value},
    }
    assert target.as_dict() == payload

    restored = TelephonyTransferTarget(payload)
    assert isinstance(restored.destination, address_model)
    assert restored.destination.type == address_type
    assert restored.destination.value == value


@pytest.mark.parametrize("update", [{"label": "updated-binding"}, {"label": None}, {"allowed_calling_numbers": []}])
def test_telephony_binding_update_preserves_explicit_values(update):
    request = UpdateTelephonyBindingRequest(update)
    assert request.as_dict() == update


@pytest.mark.parametrize("operation_module", [operations, async_operations])
def test_voice_agent_nested_operation_types_are_public(operation_module):
    annotations = get_type_hints(operation_module.BetaVoiceAgentsOperations)
    assert annotations["campaigns"] is operation_module.BetaVoiceAgentsCampaignsOperations
    assert annotations["live_conversations"] is operation_module.BetaVoiceAgentsLiveConversationsOperations
    assert "BetaVoiceAgentsCampaignsOperations" in operation_module.__all__
    assert "BetaVoiceAgentsLiveConversationsOperations" in operation_module.__all__
