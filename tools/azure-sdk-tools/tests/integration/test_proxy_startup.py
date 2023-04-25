# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from urllib3 import PoolManager, Retry
import os
from devtools_testutils.proxy_startup import PROXY_CHECK_URL

if os.getenv("REQUESTS_CA_BUNDLE"):
    http_client = PoolManager(
        retries=Retry(total=3, raise_on_status=False),
        cert_reqs="CERT_REQUIRED",
        ca_certs=os.getenv("REQUESTS_CA_BUNDLE"),
    )
else:
    http_client = PoolManager(retries=Retry(total=1, raise_on_status=False))


class TestProxyIntegration:
    # These tests are checking spinup of the proxy, not automatic redirect.
    # Therefore we are not using recorded_by_proxy decorator or recorded_test fixture
    def test_tool_spinup_http(self):
        result = http_client.request("GET", PROXY_CHECK_URL)
        assert(result.status == 200)
