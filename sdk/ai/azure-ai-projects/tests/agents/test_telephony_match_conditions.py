import inspect

import pytest
from azure.core import MatchConditions

from azure.ai.projects._utils.utils import prep_if_match, prep_if_none_match
from azure.ai.projects.models import (
    PhoneNumber,
    TelephonyTransferTarget,
    TelephonyTransferTargets,
    UpdateTelephonyBindingRequest,
)
from azure.ai.projects.aio.operations._operations import BetaVoiceAgentsTelephonyOperations as AsyncTelephonyOperations
from azure.ai.projects.operations._operations import (
    BetaVoiceAgentsTelephonyOperations as TelephonyOperations,
    build_beta_voice_agents_telephony_cancel_call_job_request,
    build_beta_voice_agents_telephony_delete_binding_request,
    build_beta_voice_agents_telephony_replace_transfer_targets_request,
    build_beta_voice_agents_telephony_update_binding_request,
)


@pytest.mark.parametrize(
    "etag, match_condition, expected",
    [
        ("etag", MatchConditions.IfNotModified, '"etag"'),
        ('"etag"', MatchConditions.IfNotModified, '"etag"'),
        ('W/"etag"', MatchConditions.IfNotModified, 'W/"etag"'),
        ("etag", MatchConditions.IfPresent, "*"),
        ("etag", MatchConditions.IfModified, None),
    ],
)
def test_prep_if_match(etag, match_condition, expected):
    assert prep_if_match(etag, match_condition) == expected


@pytest.mark.parametrize(
    "etag, match_condition, expected",
    [
        ("etag", MatchConditions.IfModified, '"etag"'),
        ("etag", MatchConditions.IfMissing, "*"),
        ("etag", MatchConditions.IfNotModified, None),
    ],
)
def test_prep_if_none_match(etag, match_condition, expected):
    assert prep_if_none_match(etag, match_condition) == expected


@pytest.mark.parametrize(
    "build_request",
    [
        lambda **kwargs: build_beta_voice_agents_telephony_update_binding_request("agent", "binding", **kwargs),
        lambda **kwargs: build_beta_voice_agents_telephony_delete_binding_request("agent", "binding", **kwargs),
        lambda **kwargs: build_beta_voice_agents_telephony_replace_transfer_targets_request("agent", **kwargs),
        lambda **kwargs: build_beta_voice_agents_telephony_cancel_call_job_request("agent", "job", **kwargs),
    ],
)
def test_telephony_builders_apply_match_condition(build_request):
    assert build_request(etag="etag", match_condition=MatchConditions.IfNotModified).headers["If-Match"] == '"etag"'
    assert build_request(etag="etag", match_condition=MatchConditions.IfPresent).headers["If-Match"] == "*"


@pytest.mark.parametrize("operations_type", [TelephonyOperations, AsyncTelephonyOperations])
@pytest.mark.parametrize(
    "method_name",
    ["update_binding", "delete_binding", "replace_transfer_targets", "cancel_call_job"],
)
def test_telephony_operations_expose_match_condition(operations_type, method_name):
    parameter = inspect.signature(getattr(operations_type, method_name)).parameters["match_condition"]

    assert parameter.annotation is MatchConditions
    assert parameter.default is inspect.Parameter.empty


def test_telephony_transfer_target_phone_number_round_trip():
    targets = TelephonyTransferTargets(
        transfer_targets=[
            TelephonyTransferTarget(
                name="sales_desk",
                description="Transfers to the sales desk for pricing questions.",
                destination=PhoneNumber(value="+14255550123"),
            )
        ]
    )
    payload = targets.as_dict()

    assert payload == {
        "transfer_targets": [
            {
                "name": "sales_desk",
                "description": "Transfers to the sales desk for pricing questions.",
                "destination": {"type": "phone_number", "value": "+14255550123"},
            }
        ]
    }
    restored = TelephonyTransferTargets(payload)
    destination = restored.transfer_targets[0].destination
    assert isinstance(destination, PhoneNumber)
    assert destination.type == "phone_number"
    assert destination.value == "+14255550123"


def test_telephony_binding_update_serializes_label():
    request = UpdateTelephonyBindingRequest(label="Updated test binding")

    assert request.as_dict() == {"label": "Updated test binding"}
