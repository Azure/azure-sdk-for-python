# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Recorded account and project cost-control lifecycle tests for the November preview."""

import os
from datetime import datetime, timedelta, timezone

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient, models
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

SANITIZED_RESOURCE_GROUP = "sanitized-resource-group"
SANITIZED_ACCOUNT_NAME = "sanitized-cognitive-account"
SANITIZED_PROJECT_NAME = "sanitized-project"


class TestCostControlsLive(AzureMgmtRecordedTestCase):
    def setup_method(self, method):  # pylint: disable=unused-argument
        self.resource_group_name = _live_value(self, "AZURE_RESOURCE_GROUP", SANITIZED_RESOURCE_GROUP)
        self.account_name = _live_value(self, "AZURE_COGNITIVE_SERVICES_ACCOUNT", SANITIZED_ACCOUNT_NAME)
        self.client = self.create_mgmt_client(
            CognitiveServicesManagementClient,
            api_version="2026-11-15-preview",
        )

    @recorded_by_proxy
    def test_account_cost_control_lifecycle(self, variables=None):
        return self._cost_control_lifecycle("account", variables)

    @recorded_by_proxy
    def test_project_cost_control_lifecycle(self, variables=None):
        return self._cost_control_lifecycle("project", variables)

    def _cost_control_lifecycle(self, scope, variables):
        if self.is_live:
            now = datetime.now(timezone.utc).replace(microsecond=0)
        else:
            if not variables or "budget_reference_time" not in variables:
                pytest.fail("Re-record the Cost Control tests to capture budget_reference_time before playback.")
            now = datetime.fromisoformat(variables["budget_reference_time"])
        cost_control_name = self.get_resource_name("costctrl")[:64]
        session_id = self.get_resource_name("costctrlsession")
        parent_args = (self.resource_group_name, self.account_name)
        resource_type = "Microsoft.CognitiveServices/accounts"
        model_type = models.AccountCostControl
        if scope == "project":
            project_name = _live_value(self, "AZURE_COGNITIVE_SERVICES_PROJECT", SANITIZED_PROJECT_NAME)
            parent_args += (project_name,)
            resource_type += "/projects"
            model_type = models.ProjectCostControl
        operations = getattr(self.client, f"{scope}_cost_controls")
        created = False

        try:
            cost_control = operations.create_or_update(
                *parent_args,
                cost_control_name,
                model_type(properties=_budget_properties(session_id, now)),
                etag="*",
                match_condition=MatchConditions.IfMissing,
            )
            created = True
            assert cost_control.name == cost_control_name
            assert cost_control.type == f"{resource_type}/costControls"
            assert cost_control.properties.category == models.CostControlCategory.COST
            assert cost_control.properties.amount == 25
            assert cost_control.properties.provider_properties.actions["budget-block"].type == "Block"
            assert operations.check_existence(*parent_args, cost_control_name) is True

            fetched, response_headers = operations.get(
                *parent_args,
                cost_control_name,
                cls=lambda _, model, headers: (model, headers),
            )
            etag = fetched.etag or response_headers["ETag"]
            assert etag
            assert fetched.properties.filter.additional_info.values_property == [session_id]

            cost_controls = list(operations.list(*parent_args))
            assert any(item.name == cost_control_name for item in cost_controls)

            updated = operations.update(
                *parent_args,
                cost_control_name,
                models.CostControlPatch(properties=models.CostControlPatchProperties(amount=50)),
                etag=etag,
                match_condition=MatchConditions.IfNotModified,
            )
            assert updated.properties.amount == 50
            assert updated.properties.category == fetched.properties.category
            assert updated.properties.time_period == fetched.properties.time_period
            assert updated.properties.filter.additional_info.values_property == [session_id]
            assert updated.properties.provider_properties.actions["budget-block"].threshold == 100

            fetched, response_headers = operations.get(
                *parent_args,
                cost_control_name,
                cls=lambda _, model, headers: (model, headers),
            )
            etag = fetched.etag or response_headers["ETag"]
            cleared = operations.update(
                *parent_args,
                cost_control_name,
                models.CostControlPatch({"properties": {"providerProperties": None}}),
                etag=etag,
                match_condition=MatchConditions.IfNotModified,
            )
            assert cleared.properties.provider_properties is None or not cleared.properties.provider_properties.actions
            assert cleared.properties.amount == 50
            assert cleared.properties.filter.additional_info.values_property == [session_id]

            fetched, response_headers = operations.get(
                *parent_args,
                cost_control_name,
                cls=lambda _, model, headers: (model, headers),
            )
            etag = fetched.etag or response_headers["ETag"]
            operations.delete(
                *parent_args,
                cost_control_name,
                etag=etag,
                match_condition=MatchConditions.IfNotModified,
            )
            created = False

            with pytest.raises(ResourceNotFoundError):
                operations.get(
                    *parent_args,
                    cost_control_name,
                )
        finally:
            if created:
                try:
                    operations.delete(*parent_args, cost_control_name)
                except ResourceNotFoundError:
                    pass
        return {"budget_reference_time": now.isoformat()}


def _budget_properties(session_id, now):
    return models.CostControlProperties(
        category=models.CostControlCategory.COST,
        amount=25,
        time_grain=models.CostControlTimeGrain.MONTHLY,
        time_period=models.CostControlTimePeriod(start_date=now - timedelta(days=1), end_date=now + timedelta(days=30)),
        filter=models.CostControlFilter(
            additional_info=models.CostControlAdditionalInfoFilter(name="sessionId", values_property=[session_id])
        ),
        provider_properties=models.CostControlProviderProperties(
            actions={
                "budget-block": models.CostControlAction(
                    type="Block",
                    threshold_type=models.CostControlThresholdType.PERCENTAGE,
                    threshold=100,
                    operator="GreaterThanOrEqualTo",
                )
            }
        ),
    )


def _live_value(test_case, name, playback_value):
    if not test_case.is_live:
        return playback_value
    value = os.environ.get(name)
    if not value:
        pytest.fail(f"Set {name} before running the live Cost Control tests.")
    return value
