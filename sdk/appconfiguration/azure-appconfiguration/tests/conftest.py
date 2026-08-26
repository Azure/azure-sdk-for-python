# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import logging
import os
import time

import pytest
from azure.appconfiguration import AzureAppConfigurationClient
from azure.core.exceptions import HttpResponseError
from devtools_testutils import (
    add_general_regex_sanitizer,
    get_credential,
    is_live,
    remove_batch_sanitizers,
    set_bodiless_matcher,
    test_proxy,
)


_LOGGER = logging.getLogger(__name__)
_RBAC_PROPAGATION_TIMEOUT = 15 * 60
_MAX_RETRY_DELAY = 30


def _wait_for_data_plane_access(client, timeout=_RBAC_PROPAGATION_TIMEOUT):
    deadline = time.monotonic() + timeout
    retry_delay = 1

    while True:
        try:
            next(client.list_configuration_settings(key_filter="__rbac_readiness_probe__"), None)
            return
        except HttpResponseError as error:
            if error.status_code != 403:
                raise

            remaining_time = deadline - time.monotonic()
            if remaining_time <= 0:
                raise TimeoutError("App Configuration data-plane role assignment did not propagate in time.") from error

            sleep_time = min(retry_delay, remaining_time)
            _LOGGER.info(
                "Waiting %.0f seconds for the App Configuration data-plane role assignment to propagate.",
                sleep_time,
            )
            time.sleep(sleep_time)
            retry_delay = min(retry_delay * 2, _MAX_RETRY_DELAY)


@pytest.fixture(scope="session", autouse=True)
def wait_for_data_plane_access():
    if not is_live():
        return

    endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
    if not endpoint:
        pytest.fail("APPCONFIGURATION_ENDPOINT_STRING must be set when running live tests.")

    client = AzureAppConfigurationClient(endpoint, get_credential())
    try:
        _wait_for_data_plane_access(client)
    finally:
        client.close()


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, patch_sleep, patch_async_sleep):
    set_bodiless_matcher()

    client_id = os.environ.get("APPCONFIGURATION_CLIENT_ID", "client-id")
    add_general_regex_sanitizer(regex=client_id, value="client-id")
    client_secret = os.environ.get("APPCONFIGURATION_CLIENT_SECRET", "client-secret")
    add_general_regex_sanitizer(regex=client_secret, value="client-secret")
    tenant_id = os.environ.get("APPCONFIGURATION_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(value="00000000-0000-0000-0000-000000000000", regex=tenant_id)

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3447: $.key
    #  - AZSDK3490: $..etag
    #  - AZSDK3493: $..name
    #  - AZSDK4001: host name -> Sanitized
    remove_batch_sanitizers(["AZSDK3447", "AZSDK3490", "AZSDK3493", "AZSDK4001"])
