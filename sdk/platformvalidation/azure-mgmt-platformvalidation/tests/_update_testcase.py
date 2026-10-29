# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from urllib.parse import urlsplit

from azure.mgmt.platformvalidation.models import (
    ValidationExecutionPlan,
    ValidationExecutionPlanProperties,
    ValidationExecutionPlanUpdate,
    ValidationExecutionPlanUpdateProperties,
)


def replacement_plan(location, tags, description, configuration):
    return ValidationExecutionPlan(
        location=location,
        tags=tags,
        properties=ValidationExecutionPlanProperties(description=description, plan_configuration_json=configuration),
    )


def plan_update(*, tags=None, **properties):
    return ValidationExecutionPlanUpdate(
        **({"tags": tags} if tags is not None else {}),
        properties=ValidationExecutionPlanUpdateProperties(**properties),
    )


def updated_configuration(configuration):
    document = json.loads(configuration)
    document["metadata"]["description"] = "Updated SDK recorded plan metadata"
    return json.dumps(document, separators=(",", ":"))


def response_observation(response):
    """Retain correlation evidence, never signed queries or response documents."""
    headers = response.http_response.headers
    return {
        "method": response.http_request.method,
        "path": urlsplit(response.http_request.url).path,
        "status": response.http_response.status_code,
        "request_id": headers.get("x-ms-request-id"),
        "correlation_id": headers.get("x-ms-correlation-request-id"),
    }
