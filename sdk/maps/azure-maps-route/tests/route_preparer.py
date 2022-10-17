# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import EnvironmentVariableLoader

MapsRoutePreparer = functools.partial(
    EnvironmentVariableLoader, "maps",
    subscription_key="<maps-subscription-key>",
    maps_client_id="fake_client_id",
    maps_client_secret="fake_secret",
    maps_tenant_id="fake_tenant_id",
)