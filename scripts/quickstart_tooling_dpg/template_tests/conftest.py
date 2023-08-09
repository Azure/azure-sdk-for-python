# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
import pytest

from devtools_testutils import test_proxy, add_general_string_sanitizer

# For more info about add_sanitizers, please refer to https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md#register-sanitizers
@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    subscription_id = os.environ.get("{{ test_prefix | upper }}_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    tenant_id = os.environ.get("{{ test_prefix | upper }}_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    client_id = os.environ.get("{{ test_prefix | upper }}_CLIENT_ID", "00000000-0000-0000-0000-000000000000")
    client_secret = os.environ.get("{{ test_prefix | upper }}_CLIENT_SECRET", "00000000-0000-0000-0000-000000000000")
    add_general_string_sanitizer(target=subscription_id, value="00000000-0000-0000-0000-000000000000")
    add_general_string_sanitizer(target=tenant_id, value="00000000-0000-0000-0000-000000000000")
    add_general_string_sanitizer(target=client_id, value="00000000-0000-0000-0000-000000000000")
    add_general_string_sanitizer(target=client_secret, value="00000000-0000-0000-0000-000000000000")
