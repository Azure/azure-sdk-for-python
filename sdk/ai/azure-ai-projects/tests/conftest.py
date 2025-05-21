# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from dotenv import load_dotenv, find_dotenv

if not load_dotenv(find_dotenv(filename="azure_ai_projects_tests.filled.env"), override=True):
    print("Failed to apply environment variables for azure-ai-projects tests. This is expected if running in ADO pipeline.")

import pytest

# From: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#start-the-test-proxy-server
# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
# test_proxy auto-starts the test proxy
# patch_sleep and patch_async_sleep streamline tests by disabling wait times during LRO polling
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy, patch_sleep, patch_async_sleep):
    return