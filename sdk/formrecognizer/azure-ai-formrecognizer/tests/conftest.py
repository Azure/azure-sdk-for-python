
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import sys
from devtools_testutils import add_remove_header_sanitizer, add_general_regex_sanitizer, add_oauth_response_sanitizer, add_body_key_sanitizer, test_proxy

# Ignore async tests for Python < 3.6
collect_ignore_glob = []
if sys.version_info < (3, 6):
    collect_ignore_glob.append("*_async.py")

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_remove_header_sanitizer(headers="Ocp-Apim-Subscription-Key")
    add_general_regex_sanitizer(
        value="fakeendpoint",
        regex="(?<=\\/\\/)[a-z-]+(?=\\.cognitiveservices\\.azure\\.com)"
    )
    add_oauth_response_sanitizer()
    add_body_key_sanitizer(
        json_path="urlSource",
        value="blob_sas_url",
        regex="(?<=\\/\\/)[a-z-]+(?=\\.blob\\.core\\.windows\\.net)(.*)$",
    )
    add_body_key_sanitizer(
        json_path="azureBlobSource.containerUrl",
        value="blob_sas_url",
        regex="(?<=\\/\\/)[a-z-]+(?=\\.blob\\.core\\.windows\\.net)(.*)$",
    )
    add_body_key_sanitizer(
        json_path="source",
        value="blob_sas_url",
        regex="(?<=\\/\\/)[a-z-]+(?=\\.blob\\.core\\.windows\\.net)(.*)$",
    )
    add_body_key_sanitizer(
        json_path="accessToken",
        value="redacted",
        regex="([0-9a-f-]{36})",
    )
    
    add_body_key_sanitizer(
        json_path="copyAuthorization.accessToken",
        value="redacted",
        regex="([0-9a-f-]{36})",
    )
