# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import os

import pytest
from devtools_testutils import add_general_regex_sanitizer, add_body_key_sanitizer, add_uri_regex_sanitizer, test_proxy

# Fixture
from testcase import load_registry

# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("*_async.py")


def pytest_configure(config):
    config.addinivalue_line("usefixtures", "load_registry")

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # sanitizes table/cosmos account names in URLs
    add_general_regex_sanitizer(
        value="fakeendpoint",
        regex="(?<=\\/\\/)[a-z]+(?=(?:|-secondary)\\.(?:table|blob|queue)\\.(?:cosmos|core)\\."
              "(?:azure|windows)\\.(?:com|net))",
    )
    # sanitizes random UUIDs that are sent in batch request headers and bodies
    add_general_regex_sanitizer(
        value="00000000-0000-0000-0000-000000000000",
        regex="batch[a-z]*_([0-9a-f]{8}\\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\\b[0-9a-f]{12}\\b)",
        group_for_replace="1",
    )
    # sanitizes access and refresh tokens that are present in single-string request or response bodies
    # we expect tokens to either be at the end of this body string, or followed by "\u0026" and more content
    add_general_regex_sanitizer(value="access_token", regex="(?<=access_token=).*?(?=(?:\\u0026|$))")
    add_general_regex_sanitizer(value="refresh_token", regex="(?<=refresh_token=).*?(?=(?:\\u0026|$))")
    # sanitizes access and refresh tokens in JSON-formatted request or response bodies
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")
    add_body_key_sanitizer(json_path="$..refresh_token", value="refresh_token")
    add_uri_regex_sanitizer(regex="sha256%3A(.*)", value="sha256_encoded_stream")

    client_id = os.environ.get("CONTAINERREGISTRY_CLIENT_ID", "client-id")
    add_general_regex_sanitizer(regex=client_id, value="client-id")
    client_secret = os.environ.get("CONTAINERREGISTRY_CLIENT_SECRET", "client-secret")
    add_general_regex_sanitizer(regex=client_secret, value="client-secret")
