# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Live Cost Control lifecycle tests.

TODO: Remove ``_PreviewApiVersionPolicy`` when the service accepts
``2026-09-15-preview`` for these operations.
"""

import os
from types import SimpleNamespace

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient, models
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

SANITIZED_RESOURCE_GROUP = "sanitized-resource-group"
SANITIZED_ACCOUNT_NAME = "sanitized-cognitive-account"


class _PreviewApiVersionPolicy(SansIOHTTPPolicy):
    """Temporarily send the working service API version on the wire."""

    def on_request(self, request):
        request.http_request.url = request.http_request.url.replace(
            "api-version=2026-09-15-preview",
            "api-version=2026-07-15-preview",
        )


def test_preview_api_version_policy():
    request = SimpleNamespace(
        http_request=SimpleNamespace(url="https://management.azure.com/resource?api-version=2026-09-15-preview")
    )

    _PreviewApiVersionPolicy().on_request(request)

    assert request.http_request.url.endswith("api-version=2026-07-15-preview")


class TestCostControlsLive(AzureMgmtRecordedTestCase):
    def setup_method(self, method):  # pylint: disable=unused-argument
        self.resource_group_name = _live_value(self, "AZURE_RESOURCE_GROUP", SANITIZED_RESOURCE_GROUP)
        self.account_name = _live_value(self, "AZURE_COGNITIVE_SERVICES_ACCOUNT", SANITIZED_ACCOUNT_NAME)
        self.client = self.create_mgmt_client(
            CognitiveServicesManagementClient,
            api_version="2026-09-15-preview",
            per_call_policies=[_PreviewApiVersionPolicy()],
        )

    @recorded_by_proxy
    def test_cost_control_lifecycle(self):
        cost_control_name = self.get_resource_name("costctrl")[:64]
        created = False
        rule = _cost_control_rule(amount=25, display_action="audit")

        try:
            cost_control = self.client.cost_controls.create_or_update(
                self.resource_group_name,
                self.account_name,
                cost_control_name,
                models.CostControl(
                    properties=models.CostControlProperties(
                        display_name="SDK live test",
                        rules=[rule],
                    )
                ),
                etag="*",
                match_condition=MatchConditions.IfMissing,
            )
            created = True
            assert cost_control.name
            assert cost_control.type == "Microsoft.CognitiveServices/accounts/costControls"
            assert cost_control.properties.rules[0].thresholds[0].action == "audit"

            fetched, response_headers = self.client.cost_controls.get(
                self.resource_group_name,
                self.account_name,
                cost_control_name,
                cls=lambda _, model, headers: (model, headers),
            )
            etag = fetched.etag or response_headers["ETag"]
            assert etag
            assert fetched.properties.rules[0].thresholds[0].value == 0

            cost_controls = list(self.client.cost_controls.list(self.resource_group_name, self.account_name))
            assert any(item.properties.display_name == "SDK live test" for item in cost_controls)

            updated = self.client.cost_controls.update(
                self.resource_group_name,
                self.account_name,
                cost_control_name,
                models.CostControlPatch(
                    properties=models.CostControlPatchProperties(
                        display_name="SDK live test updated",
                        rules=[_cost_control_rule(amount=50, display_action="audit")],
                    )
                ),
                etag=etag,
                match_condition=MatchConditions.IfNotModified,
            )
            assert updated.properties.display_name == "SDK live test updated"
            assert updated.properties.rules[0].amount == 50

            fetched, response_headers = self.client.cost_controls.get(
                self.resource_group_name,
                self.account_name,
                cost_control_name,
                cls=lambda _, model, headers: (model, headers),
            )
            etag = fetched.etag or response_headers["ETag"]
            self.client.cost_controls.delete(
                self.resource_group_name,
                self.account_name,
                cost_control_name,
                etag=etag,
                match_condition=MatchConditions.IfNotModified,
            )
            created = False

            with pytest.raises(ResourceNotFoundError):
                self.client.cost_controls.get(
                    self.resource_group_name,
                    self.account_name,
                    cost_control_name,
                )
        finally:
            if created:
                try:
                    self.client.cost_controls.delete(
                        self.resource_group_name,
                        self.account_name,
                        cost_control_name,
                    )
                except ResourceNotFoundError:
                    pass

    @recorded_by_proxy
    def test_clear_cost_control_connections(self):
        if os.environ.get("AZURE_TEST_COST_CONTROL_CLEAR_CONNECTIONS", "").lower() != "true":
            pytest.skip("Set AZURE_TEST_COST_CONTROL_CLEAR_CONNECTIONS=true to allow account mutation.")

        original = self.client.accounts.get(self.resource_group_name, self.account_name)
        original_connections = original.properties.cost_control_connections
        original_payload = _connection_payload(original_connections)
        temporary_connection_id = os.environ.get("AZURE_COST_CONTROL_APP_INSIGHTS_CONNECTION_ID")

        if original_connections is None and not temporary_connection_id:
            pytest.skip(
                "The account has no costControlConnections. Set "
                "AZURE_COST_CONTROL_APP_INSIGHTS_CONNECTION_ID to test a non-null to null transition."
            )

        try:
            if original_connections is None:
                self.client.accounts.begin_update(
                    self.resource_group_name,
                    self.account_name,
                    {
                        "properties": {
                            "costControlConnections": {
                                "appInsightsConnectionId": temporary_connection_id,
                            }
                        }
                    },
                ).result()

            self.client.accounts.begin_update(
                self.resource_group_name,
                self.account_name,
                {"properties": {"costControlConnections": None}},
            ).result()

            account = self.client.accounts.get(self.resource_group_name, self.account_name)
            assert account.properties.cost_control_connections is None
        finally:
            if original_payload is not None:
                self.client.accounts.begin_update(
                    self.resource_group_name,
                    self.account_name,
                    {"properties": {"costControlConnections": original_payload}},
                ).result()


def _cost_control_rule(amount, display_action):
    return models.CostControlRule(
        name="account-budget",
        counter_key=[models.CostControlDimension(type="account")],
        unit="usd",
        amount=amount,
        period="month",
        recurring=True,
        thresholds=[
            models.CostControlThreshold(
                type="percentage",
                value=0,
                action=display_action,
            )
        ],
    )


def _connection_payload(connections):
    if connections is None:
        return None
    return {
        "appInsightsConnectionId": connections.app_insights_connection_id,
        "eventGridConnectionId": connections.event_grid_connection_id,
    }


def _live_value(test_case, name, playback_value):
    if not test_case.is_live:
        return playback_value
    value = os.environ.get(name)
    if not value:
        pytest.fail(f"Set {name} before running the live Cost Control tests.")
    return value
