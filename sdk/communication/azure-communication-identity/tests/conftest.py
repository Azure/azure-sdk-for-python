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
import pytest
import os
from devtools_testutils import test_proxy, add_general_regex_sanitizer, add_header_regex_sanitizer, \
    set_default_session_settings, add_uri_regex_sanitizer, add_body_key_sanitizer, add_oauth_response_sanitizer
from azure.communication.identity._shared.utils import parse_connection_str

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    set_default_session_settings()

    connection_str = os.getenv('COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING') or \
                          os.getenv('COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING')
    if connection_str is not None:
        endpoint, _ = parse_connection_str(connection_str)
        resource_name = endpoint.split(".")[0]
        add_general_regex_sanitizer(regex=resource_name, value="sanitized")

    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=subscription_id, value="00000000-0000-0000-0000-000000000000")

    m365_client_id = os.environ.get("COMMUNICATION_M365_APP_ID", "sanitized")
    add_general_regex_sanitizer(regex=m365_client_id, value="sanitized")

    msal_username = os.environ.get("COMMUNICATION_MSAL_USERNAME", "sanitized")
    add_general_regex_sanitizer(regex=msal_username, value="sanitized")

    msal_password = os.environ.get("COMMUNICATION_MSAL_PASSWORD", "sanitized")
    add_general_regex_sanitizer(regex=msal_password, value="sanitized")

    expired_teams_token = os.environ.get("COMMUNICATION_EXPIRED_TEAMS_TOKEN", "sanitized")
    add_general_regex_sanitizer(regex=expired_teams_token, value="sanitized")

    azure_tenant_id = os.environ.get("AZURE_TENANT_ID", "sanitized")
    add_general_regex_sanitizer(regex=azure_tenant_id, value="sanitized")

    azure_client_secret = os.environ.get("AZURE_CLIENT_SECRET", "sanitized")
    add_general_regex_sanitizer(regex=azure_client_secret, value="sanitized")

    azure_client_id = os.environ.get("AZURE_CLIENT_ID", "sanitized")
    add_general_regex_sanitizer(regex=azure_client_id, value="sanitized")

    add_body_key_sanitizer(json_path="*.id", value="sanitized")
    add_body_key_sanitizer(json_path="*.token", value="sanitized")
    add_body_key_sanitizer(json_path="token", value="sanitized")
    add_body_key_sanitizer(json_path="*.userId", value="sanitized")
    add_body_key_sanitizer(json_path="userId", value="sanitized")
    add_body_key_sanitizer(json_path="*.domain_name", value="sanitized")

    add_general_regex_sanitizer(regex='/identities/([^/?]+)', value='/identities/sanitized')
    add_general_regex_sanitizer(regex='common/userrealm/([^/.]+)', value='common/userrealm/sanitized@test')

    add_header_regex_sanitizer(key="P3P", value="sanitized")
    add_header_regex_sanitizer(key="Set-Cookie", value="sanitized")
    add_header_regex_sanitizer(key="Date", value="sanitized")
    add_header_regex_sanitizer(key="Cookie", value="sanitized")
    add_header_regex_sanitizer(key="client-request-id", value="sanitized")
    add_header_regex_sanitizer(key="MS-CV", value="sanitized")
    add_header_regex_sanitizer(key="X-Azure-Ref", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-content-sha256", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-client-request-id", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-date", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-ests-server", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-request-id", value="sanitized")
    add_header_regex_sanitizer(key="Content-Security-Policy-Report-Only", value="sanitized")

