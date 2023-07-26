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
import platform
import pytest
import sys

from dotenv import load_dotenv

from devtools_testutils import test_proxy, add_general_regex_sanitizer, add_body_key_sanitizer, add_header_regex_sanitizer

# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5) or platform.python_implementation() == "PyPy":
    collect_ignore_glob.append("*_async.py")

load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    subscription_id = os.environ.get("PURVIEWSHARING_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    tenant_id = os.environ.get("PURVIEWSHARING_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    client_id = os.environ.get("PURVIEWSHARING_CLIENT_ID", "00000000-0000-0000-0000-000000000000")
    client_secret = os.environ.get("PURVIEWSHARING_CLIENT_SECRET", "00000000-0000-0000-0000-000000000000")
    resource_group_name = os.environ.get("PURVIEWSHARING_RESOURCEGROUP", "fakeResourceGroup")
    storage_account_provider = os.environ.get("PURVIEWSHARING_STORAGEACCOUNT_PROVIDER", "fakeStorageAccount")
    storage_account_receiver = os.environ.get("PURVIEWSHARING_STORAGEACCOUNT_RECEIVER", "fakeStorageAccountR")
    add_general_regex_sanitizer(regex=subscription_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=tenant_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=client_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=client_secret, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=resource_group_name, value="fakeResourceGroup")
    add_general_regex_sanitizer(regex=storage_account_provider, value="fakeStorageAccount")
    add_general_regex_sanitizer(regex=storage_account_receiver, value="fakeStorageAccountR")
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    add_header_regex_sanitizer(key="Cookie", value="cookie;")
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")
    add_body_key_sanitizer(json_path="$..atlasKafkaPrimaryEndpoint", value="000")
    add_body_key_sanitizer(json_path="$..atlasKafkaSecondaryEndpoint", value="000")
    add_body_key_sanitizer(json_path="$..systemData.createdBy", value="000")
