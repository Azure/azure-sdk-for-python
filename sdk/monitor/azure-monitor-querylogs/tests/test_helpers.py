# pylint: disable=line-too-long,useless-suppression
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime, timedelta
import pytest

from azure.monitor.querylogs._helpers import get_subscription_id_from_resource


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
