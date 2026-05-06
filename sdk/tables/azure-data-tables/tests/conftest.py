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
import os

import pytest
from devtools_testutils import (
    add_general_regex_sanitizer,
    add_body_key_sanitizer,
    add_remove_header_sanitizer,
    test_proxy,
    add_oauth_response_sanitizer,
    remove_batch_sanitizers,
)


# Workaround: devtools_testutils.get_credential() doesn't forward AZURE_TENANT_ID
# to AzureDeveloperCliCredential. Without this, AZD auth uses the default tenant
# which may differ from the tenant where test resources are deployed.
# See: https://github.com/Azure/azure-sdk-for-python/issues/XXXXX
def _patch_get_credential_for_azd_tenant():
    import devtools_testutils.azure_recorded_testcase as _arc
    import devtools_testutils as _dt
    import _shared.testcase as _tc

    _original = _arc.get_credential

    def _patched(**kwargs):
        cred = _original(**kwargs)
        tenant_id = os.environ.get("AZURE_TENANT_ID")
        if tenant_id and type(cred).__name__ == "AzureDeveloperCliCredential":
            from azure.identity import AzureDeveloperCliCredential

            if kwargs.get("is_async", False):
                from azure.identity.aio import AzureDeveloperCliCredential

            return AzureDeveloperCliCredential(tenant_id=tenant_id)
        return cred

    _arc.get_credential = _patched
    _dt.get_credential = _patched
    _tc.get_credential = _patched


_patch_get_credential_for_azd_tenant()

# fixture needs to be visible from conftest


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # sanitizes table/cosmos account names in URLs
    add_general_regex_sanitizer(
        value="fakeendpoint",
        regex="(?<=\\/\\/)[a-z]+(?=(?:|-secondary)\\.(?:table|blob|queue)\\.(?:cosmos|core)\\."
        "(?:azure|windows)\\.(?:com|net))",
    )
    # sanitizes tenant IDs from environment to prevent leaking into recordings
    for env_var in ("AZURE_TENANT_ID", "TABLES_TENANT_ID", "CHALLENGE_TABLES_TENANT_ID"):
        tid = os.environ.get(env_var, "")
        if tid and tid != "00000000-0000-0000-0000-000000000000":
            add_general_regex_sanitizer(value="00000000-0000-0000-0000-000000000000", regex=tid)
    # sanitizes access tokens in response bodies
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")
    add_oauth_response_sanitizer()
    # Remove the Server header from recordings — the test proxy replays multi-value
    # Server headers as duplicates, which aiohttp rejects with BadHttpMessage.
    add_remove_header_sanitizer(headers="Server")
    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3490: $..etag
    remove_batch_sanitizers(["AZSDK3490"])
