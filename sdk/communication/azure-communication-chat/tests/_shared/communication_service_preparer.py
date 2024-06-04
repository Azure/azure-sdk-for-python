# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from devtools_testutils import PowerShellPreparer

CommunicationPreparer = functools.partial(
    PowerShellPreparer,
    "communication",
    communication_livetest_dynamic_connection_string="endpoint=https://sanitized.communication.azure.com/;accesskey=fake===",
)
