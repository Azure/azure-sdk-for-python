# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
import re

import pytest
from dotenv import load_dotenv
from devtools_testutils import add_general_regex_sanitizer, set_custom_default_matcher, test_proxy


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)


@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    set_custom_default_matcher(ignore_query_ordering=True)
    connection_string = os.environ.get("WPS_CHAT_CONNECTION_STRING", "")
    access_key_match = re.search(r"(?:^|;)AccessKey=([^;]+)", connection_string, re.IGNORECASE)
    if access_key_match:
        add_general_regex_sanitizer(
            regex=re.escape(access_key_match.group(1)),
            value="Kg==",
        )
