# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import sys
import pytest
from devtools_testutils import (
    test_proxy,
    is_live,
    add_remove_header_sanitizer,
    add_general_regex_sanitizer,
    add_oauth_response_sanitizer,
    remove_batch_sanitizers,
)
from azure.storage.blob import BlobServiceClient


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_remove_header_sanitizer(headers="Ocp-Apim-Subscription-Key,Retry-After,Cookie")
    add_general_regex_sanitizer(value="fakeendpoint", regex="(?<=\\/\\/)[a-z-]+(?=\\.cognitiveservices\\.azure\\.com)")
    add_general_regex_sanitizer(
        regex="(?<=\\/\\/)[a-z]+(?=(?:|-secondary)\\.(?:table|blob|queue)\\.core\\.windows\\.net)",
        value="fakeendpoint",
    )
    add_oauth_response_sanitizer()

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3430: $..id
    #  - AZSDK3424: $..to
    remove_batch_sanitizers(["AZSDK3430", "AZSDK3424"])

    # run tests
    yield

    # Dogfood env uses a static storage account so we clean up the blob resources
    # This is unnecessary for AzureCloud where each storage account is deleted at the end of testing
    if is_live() and os.getenv("TRANSLATION_ENVIRONMENT") == "Dogfood":
        client = BlobServiceClient(
            "https://" + os.getenv("TRANSLATION_DOCUMENT_STORAGE_NAME") + ".blob.core.windows.net/",
            os.getenv("TRANSLATION_DOCUMENT_STORAGE_KEY"),
        )
        for container in client.list_containers():
            client.delete_container(container)
