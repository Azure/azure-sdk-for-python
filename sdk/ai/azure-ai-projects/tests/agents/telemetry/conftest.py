# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from devtools_testutils import add_body_key_sanitizer, set_custom_default_matcher


@pytest.fixture(scope="session", autouse=True)
def configure_playback_matcher(test_proxy, add_sanitizers):  # pylint: disable=unused-argument
    add_body_key_sanitizer(json_path="$..image_url", value="SANITIZED_IMAGE_DATA")
    set_custom_default_matcher(
        excluded_headers="Authorization,x-ms-client-request-id,x-ms-request-id",
        ignored_query_parameters="api-version",
        compare_bodies=True,
    )
