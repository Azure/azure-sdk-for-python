# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import test_proxy, add_body_key_sanitizer
import pytest

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    add_body_key_sanitizer(json_path="$..id_token", value="Sanitized")
    add_body_key_sanitizer(json_path="$..client_info", value="Sanitized")
    return