# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from dotenv import load_dotenv, find_dotenv

if not load_dotenv(find_dotenv(filename="azure_ai_projects_tests.filled.env"), override=True):
    print("Failed to apply environment variables for azure-ai-projects tests. This is expected if running in ADO pipeline.")

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return