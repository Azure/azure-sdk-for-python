# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from urllib.parse import quote

import pytest
from dotenv import load_dotenv

from devtools_testutils import (
    add_body_key_sanitizer,
    add_general_regex_sanitizer,
    add_general_string_sanitizer,
    add_remove_header_sanitizer,
    remove_batch_sanitizers,
)

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def configure_test_proxy(test_proxy, patch_sleep, patch_async_sleep) -> None:
    # Preserve resource identity assertions and LRO polling URLs, not credentials.
    remove_batch_sanitizers(["AZSDK3430", "AZSDK3493", "AZSDK2003"])
    for variable in (
        "AZURE_SUBSCRIPTION_ID",
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
        "PLATFORMVALIDATION_TENANT_ID",
        "PLATFORMVALIDATION_CLIENT_ID",
        "PLATFORMVALIDATION_CLIENT_SECRET",
    ):
        value = os.environ.get(variable)
        if value:
            for target in {value, quote(value, safe="")}:
                add_general_string_sanitizer(target=target, value="00000000-0000-0000-0000-000000000000")
    # A replacement Set-Cookie can introduce a cookie that was never sent live.
    add_remove_header_sanitizer(headers="Set-Cookie,Cookie,x-ms-resource-provider-hint,x-ms-providerhub-traffic")
    # ARM polling URLs carry signed parameters in both headers and request URIs.
    add_general_regex_sanitizer(
        regex=r"""(?i)([?&](?:c|h|s|t)=)([^&\s"<>\\]+)""",
        group_for_replace="2",
        value="Sanitized",
    )
    add_body_key_sanitizer(json_path="$..access_token", value="Sanitized")
    add_body_key_sanitizer(json_path="$..systemData.createdBy", value="Sanitized")
    add_body_key_sanitizer(json_path="$..systemData.lastModifiedBy", value="Sanitized")
