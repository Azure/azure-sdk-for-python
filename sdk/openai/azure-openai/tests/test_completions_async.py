# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import openai
from devtools_testutils import AzureRecordedTestCase


class TestCompletionsAsync(AzureRecordedTestCase):

    @pytest.mark.asyncio
    async def test_completion(self, azure_openai_creds):
        openai.api_base = azure_openai_creds["endpoint"]
        openai.api_type = "azure"
        openai.api_key = azure_openai_creds["key"]
        openai.api_version = azure_openai_creds["api_version"]
        deployment = azure_openai_creds["completions_name"]

        completion = await openai.Completion.acreate(prompt="hello world", deployment_id=deployment)
        assert completion
