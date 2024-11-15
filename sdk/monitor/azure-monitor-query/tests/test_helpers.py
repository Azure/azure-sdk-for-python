# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime, timedelta
import pytest

from azure.monitor.query._helpers import get_subscription_id_from_resource, get_timespan_iso8601_endpoints


def test_get_subscription_id_from_resource():
    assert (
        get_subscription_id_from_resource(
            "/subscriptions/00000000-1111-2222-3333-000000000000/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm"
        )
        == "00000000-1111-2222-3333-000000000000"
    )

    # Test witout preceding slash
    assert (
        get_subscription_id_from_resource(
            "subscriptions/00000000-1111-2222-3333-000000000000/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm"
        )
        == "00000000-1111-2222-3333-000000000000"
    )

    with pytest.raises(ValueError):
        get_subscription_id_from_resource("/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm")

    with pytest.raises(ValueError):
        get_subscription_id_from_resource("")


def test_get_timespan_iso6801_endpoints():
    start, end = datetime(2020, 1, 1), datetime(2020, 1, 2)
    iso_start, iso_end = get_timespan_iso8601_endpoints((start, end))
    assert iso_start == "2020-01-01T00:00:00.000Z"
    assert iso_end == "2020-01-02T00:00:00.000Z"

    start, delta = datetime(2020, 1, 1), timedelta(days=3)
    iso_start, iso_end = get_timespan_iso8601_endpoints((start, delta))
    assert iso_start == "2020-01-01T00:00:00.000Z"
    assert iso_end == "2020-01-04T00:00:00.000Z"

    start, delta = datetime(2020, 1, 4), timedelta(days=-3)
    iso_start, iso_end = get_timespan_iso8601_endpoints((start, delta))
    assert iso_start == "2020-01-01T00:00:00.000Z"
    assert iso_end == "2020-01-04T00:00:00.000Z"
