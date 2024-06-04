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
from devtools_testutils import (
    add_remove_header_sanitizer,
    add_general_regex_sanitizer,
    add_oauth_response_sanitizer,
    add_body_key_sanitizer,
    test_proxy,
    remove_batch_sanitizers,
)


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_remove_header_sanitizer(headers="Ocp-Apim-Subscription-Key")
    add_general_regex_sanitizer(value="fakeendpoint", regex="(?<=\\/\\/)[a-z-]+(?=\\.cognitiveservices\\.azure\\.com)")
    add_oauth_response_sanitizer()
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
    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3496: "$..resourceLocation"
    remove_batch_sanitizers(["AZSDK3496"])


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
            else:
                raise  # not a flaky test

    return wrapper
