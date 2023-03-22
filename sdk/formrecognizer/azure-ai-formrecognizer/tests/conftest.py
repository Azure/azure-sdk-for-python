
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import pytest
from functools import wraps
from azure.core.exceptions import HttpResponseError
import sys
from devtools_testutils import (
    add_remove_header_sanitizer,
    add_general_regex_sanitizer,
    add_oauth_response_sanitizer,
    add_body_key_sanitizer,
    test_proxy,
)

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
        json_path="targetResourceId",
        value="/path/to/resource/id",
        regex="^.*",
    )
    add_body_key_sanitizer(
        json_path="targetResourceRegion",
        value="region",
        regex="^.*",
    )
    add_body_key_sanitizer(
        json_path="copyAuthorization.accessToken",
        value="redacted",
        regex="([0-9a-f-]{36})",
    )

def skip_flaky_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HttpResponseError as error:
            logger = logging.getLogger("azure")
            if "Invalid request".casefold() in error.message.casefold():
                pytest.mark.skip("flaky service response: {}".format(error))
                logger.debug("flaky service response: {}".format(error))
            elif "Generic error".casefold() in error.message.casefold():
                pytest.mark.skip("flaky service response: {}".format(error))
                logger.debug("flaky service response: {}".format(error))
            elif "Timeout" in error.message.casefold():
                pytest.mark.skip("flaky service response: {}".format(error))
                logger.debug("flaky service response: {}".format(error))
            elif "InvalidImage" in error.message.casefold():
                pytest.mark.skip("flaky service response: {}".format(error))
                logger.debug("flaky service response: {}".format(error))
            raise  # not a flaky test

    return wrapper
