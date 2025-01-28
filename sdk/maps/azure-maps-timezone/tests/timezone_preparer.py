# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import EnvironmentVariableLoader

MapsTimeZonePreparer = functools.partial(
    EnvironmentVariableLoader,
    "maps",
    subscription_key="<maps-subscription-key>",
)
