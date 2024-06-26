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
from urllib.parse import urlparse
from devtools_testutils import (
    add_general_string_sanitizer,
    test_proxy,
    add_body_key_sanitizer,
    add_header_regex_sanitizer,
    add_oauth_response_sanitizer,
    add_body_regex_sanitizer,
)
from devtools_testutils.sanitizers import (
    add_remove_header_sanitizer,
    add_general_regex_sanitizer,
    set_custom_default_matcher,
)


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
    set_custom_default_matcher(
        compare_bodies=False,
        excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id",
    )
    add_remove_header_sanitizer(headers="aeg-sas-key, aeg-sas-token, aeg-channel-name")
    add_general_regex_sanitizer(
        value="fakeresource", regex="(?<=\\/\\/)[a-z-]+(?=\\.eastus-1\\.eventgrid\\.azure\\.net/api/events)"
    )

    add_oauth_response_sanitizer()
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    add_header_regex_sanitizer(key="Cookie", value="cookie;")

    add_body_key_sanitizer(json_path="$..id", value="id")

    client_id = os.getenv("AZURE_CLIENT_ID", "sanitized")
    client_secret = os.getenv("AZURE_CLIENT_SECRET", "sanitized")
    eventgrid_client_id = os.getenv("EVENTGRID_CLIENT_ID", "sanitized")
    eventgrid_client_secret = os.getenv("EVENTGRID_CLIENT_SECRET", "sanitized")
    tenant_id = os.getenv("AZURE_TENANT_ID", "sanitized")
    eventgrid_topic_endpoint = os.getenv("EVENTGRID_TOPIC_ENDPOINT", "sanitized")

    eventgrid_endpoint = os.getenv("EVENTGRID_ENDPOINT", "sanitized")
    eventgrid_key = os.getenv("EVENTGRID_KEY", "sanitized")
    eventgrid_topic_name = os.getenv("EVENTGRID_TOPIC_NAME", "sanitized")
    eventgrid_event_subscription_name = os.getenv("EVENTGRID_EVENT_SUBSCRIPTION_NAME", "sanitized")

    eventgrid_cloud_event_topic_key = os.getenv("EVENTGRID_CLOUD_EVENT_TOPIC_KEY", "sanitized")
    eventgrid_cloud_event_topic_endpoint = os.getenv("EVENTGRID_CLOUD_EVENT_TOPIC_ENDPOINT", "sanitized")

    eventgrid_topic_key = os.getenv("EVENTGRID_TOPIC_KEY", "sanitized")
    eventgrid_topic_endpoint = os.getenv("EVENTGRID_TOPIC_ENDPOINT", "sanitized")

    eventgrid_partner_channel_name = os.getenv("EVENTGRID_PARTNER_CHANNEL_NAME", "sanitized")
    eventgrid_partner_namespace_topic_endpoint = os.getenv("EVENTGRID_PARTNER_NAMESPACE_TOPIC_ENDPOINT", "sanitized")
    eventgrid_partner_namespace_topic_key = os.getenv("EVENTGRID_PARTNER_NAMESPACE_TOPIC_KEY", "sanitized")

    # Need to santize namespace for eventgrid_topic:
    try:
        eventgrid_hostname = urlparse(eventgrid_topic_endpoint).hostname
        add_general_string_sanitizer(target=eventgrid_hostname.upper(), value="sanitized.eastus-1.eventgrid.azure.net")
    except:
        pass
    add_general_string_sanitizer(target=client_id, value="00000000-0000-0000-0000-000000000000")
    add_general_string_sanitizer(target=client_secret, value="sanitized")
    add_general_string_sanitizer(target=eventgrid_client_id, value="00000000-0000-0000-0000-000000000000")
    add_general_string_sanitizer(target=eventgrid_client_secret, value="sanitized")
    add_general_string_sanitizer(target=tenant_id, value="00000000-0000-0000-0000-000000000000")
