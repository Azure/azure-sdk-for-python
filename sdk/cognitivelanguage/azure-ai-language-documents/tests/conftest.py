# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest
from devtools_testutils import (
    test_proxy,
    add_remove_header_sanitizer,
    add_oauth_response_sanitizer,
    add_uri_regex_sanitizer,
    add_general_string_sanitizer,
)

ENV_SOURCE_LOCATION = "ANALYZEDOCUMENTS_SOURCE_LOCATION"
ENV_TARGET_LOCATION = "ANALYZEDOCUMENTS_TARGET_LOCATION"

FAKE_SOURCE_LOCATION = "https://fakeaccount.blob.core.windows.net/input/fake.docx"
FAKE_TARGET_LOCATION = "https://fakeaccount.blob.core.windows.net/output"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_remove_header_sanitizer(headers="Ocp-Apim-Subscription-Key,Authorization")
    add_oauth_response_sanitizer()

    add_uri_regex_sanitizer(
        regex=r"https://[^/]+\.(api\.cognitive\.microsoft\.com|cognitiveservices\.azure\.com)",
        value="https://Sanitized.cognitiveservices.azure.com",
    )

    source_location = os.getenv(ENV_SOURCE_LOCATION)
    target_location = os.getenv(ENV_TARGET_LOCATION)

    if source_location:
        add_general_string_sanitizer(target=source_location, value=FAKE_SOURCE_LOCATION)

    if target_location:
        add_general_string_sanitizer(target=target_location, value=FAKE_TARGET_LOCATION)

    return
