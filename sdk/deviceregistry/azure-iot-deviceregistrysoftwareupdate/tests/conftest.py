# coding: utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import os
import re

import pytest
from devtools_testutils import add_general_regex_sanitizer, remove_batch_sanitizers, test_proxy
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    remove_batch_sanitizers(["AZSDK2003", "AZSDK3496"])

    endpoint = os.environ.get(
        "DEVICEREGISTRYSOFTWAREUPDATE_ENDPOINT",
        "fake.api.dev.adu.microsoft.com",
    )
    add_general_regex_sanitizer(regex=endpoint, value="fake.api.dev.adu.microsoft.com")

    secret_urls = {
        "DEVICEREGISTRYSOFTWAREUPDATE_MANIFEST_URL": "https://fake.blob.core.windows.net/container/manifest.json?sanitized",
        "DEVICEREGISTRYSOFTWAREUPDATE_FILE_URL": "https://fake.blob.core.windows.net/container/README.md?sanitized",
    }
    for variable, replacement in secret_urls.items():
        value = os.environ.get(variable)
        if value:
            add_general_regex_sanitizer(regex=re.escape(value), value=replacement)
