# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Builds fake request-attempt reports for telemetry tests, and the span attributes each one should produce.

After each operation the SDK receives a report that lists every request attempt it
made, with fields such as status code, region and request charge. The SDK turns each
attempt into a ``cosmosdb.request`` tracing span. These helpers let a test set only
the fields it cares about.
"""

# Default values for attempt fields that a test does not set.
REGION = "West US 2"
SERVER = "alpha-bank-westus2.documents.azure.com"
ACTIVITY_ID = "00000000-0000-0000-0000-000000000001"


def _failed(status):
    """A status code counts as failed unless it is 2xx or 304 (not modified)."""
    return not (200 <= status < 300 or status == 304)


def fill_payload_defaults(payload):
    """Adds default values for any report fields the test did not set, and returns the same dict.

    Sets schema_version to 2, the report format the SDK reads. Totals such as the final
    status code, request charge and contacted regions are worked out from the attempt rows.

    :param dict payload: A fake report with an "attempts" list. Each attempt needs at least
        "driver_status_code".
    :return: The same payload.
    :rtype: dict
    """
    payload["schema_version"] = 2
    rows = payload.get("attempts") or []
    for row in rows:
        row.setdefault("sub_status_code", None)
        row.setdefault("failed", _failed(row["driver_status_code"]))
        row.setdefault("request_charge", 1.0)
        row.setdefault("region", REGION)
        row.setdefault("server_address", SERVER)
        row.setdefault("activity_id", ACTIVITY_ID)
        row.setdefault("operation_name", None)
    payload.setdefault("status_code", rows[-1]["driver_status_code"] if rows else None)
    payload.setdefault("sub_status_code", None)
    payload.setdefault("failed", bool(rows) and rows[-1]["failed"])
    payload.setdefault("request_charge", float(sum(row["request_charge"] for row in rows)))
    payload.setdefault("contacted_regions", list(dict.fromkeys(row["region"] for row in rows if row["region"])))
    payload.setdefault("machine_id", None)
    payload.setdefault("hedging_started", False)
    payload.setdefault("hedge_region", None)
    payload.setdefault("hedge_terminal_state", None)
    payload.setdefault("requested_regions", [])
    payload.setdefault("requested_regions_total", 0)
    payload.setdefault("responded_regions", [])
    payload.setdefault("responded_regions_total", 0)
    return payload


def expected_attempt_attributes(row, operation):
    """Returns the attributes the SDK should record on the ``cosmosdb.request`` span for one attempt.

    :param dict row: One attempt row, after fill_payload_defaults.
    :param str operation: Public SDK method name.
    :return: Expected span attributes, not including any the customer adds.
    :rtype: dict
    """
    status = str(row["driver_status_code"])
    expected = {
        "db.system.name": "azure.cosmosdb",
        "db.response.status_code": status,
        "azure.cosmosdb.operation.request_charge": row["request_charge"],
        "azure.cosmosdb.request.execution_context": row["execution_context"],
        "db.operation.name": row["operation_name"] or operation,
    }
    if row["sub_status_code"] is not None:
        expected["azure.cosmosdb.response.sub_status_code"] = row["sub_status_code"]
    if row["region"] is not None:
        expected["azure.cosmosdb.operation.contacted_regions"] = (row["region"],)
    if row["execution_context"] == "hedging":
        expected["azure.cosmosdb.request.hedge"] = True
    if row["server_address"] is not None:
        expected["server.address"] = row["server_address"]
    if row["activity_id"] is not None:
        expected["azure.cosmosdb.request.activity_id"] = row["activity_id"]
    if row["failed"]:
        expected["error.type"] = status
    return expected
