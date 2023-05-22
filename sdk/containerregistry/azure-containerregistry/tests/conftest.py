# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
from devtools_testutils import (
    add_general_regex_sanitizer,
    add_body_key_sanitizer,
    add_uri_regex_sanitizer,
    test_proxy,
    is_live,
)
from testcase import get_authority, import_image

@pytest.fixture(scope="session", autouse=True)
def load_registry():
    if not is_live():
        return
    authority = get_authority(os.environ.get("CONTAINERREGISTRY_ENDPOINT"))
    authority_anon = get_authority(os.environ.get("CONTAINERREGISTRY_ANONREGISTRY_ENDPOINT"))
    repo = "library/hello-world"
    tags = [
        "library/hello-world:latest",
        "library/hello-world:v1"
    ]
    try:
        import_image(authority, repo, tags)
        import_image(authority_anon, repo, tags, is_anonymous=True)
    except Exception as e:
        print(e)

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
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
