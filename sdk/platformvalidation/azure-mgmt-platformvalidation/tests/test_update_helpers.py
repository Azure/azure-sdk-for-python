# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from types import SimpleNamespace as NS
from _execution_testcase import IMAGE_PLACEHOLDER, plan_configuration
from _update_testcase import (
    plan_update,
    replacement_plan,
    response_observation,
    updated_configuration,
)


def test_configuration_update_changes_only_metadata_description():
    original = json.loads(plan_configuration("plan", IMAGE_PLACEHOLDER))
    updated = json.loads(updated_configuration(json.dumps(original)))
    assert updated["metadata"].pop("description") == "Updated SDK recorded plan metadata"
    assert updated == original


def test_patch_omits_configuration_when_updating_description():
    assert plan_update(description="updated").as_dict() == {"properties": {"description": "updated"}}


def test_replacement_preserves_explicit_configuration():
    result = replacement_plan("eastus", {"sdk-test": "plan"}, "description", "{}").as_dict()
    assert result["properties"] == {"description": "description", "planConfigurationJson": "{}"}
    assert result["tags"] == {"sdk-test": "plan"}
    assert result["location"] == "eastus"


def test_observation_discards_credentials_and_payloads():
    result = response_observation(
        NS(
            http_request=NS(method="PATCH", url="https://management.azure.com/resource?sig=secret"),
            http_response=NS(
                status_code=202,
                headers={"x-ms-request-id": "request", "x-ms-operation-identifier": "private"},
            ),
        )
    )
    assert result == {
        "method": "PATCH",
        "path": "/resource",
        "status": 202,
        "request_id": "request",
        "correlation_id": None,
    }
