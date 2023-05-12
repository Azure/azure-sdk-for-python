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
        deployment = azure_openai_creds["completions_name"]

        completion = await openai.Completion.acreate(prompt="hello world", deployment_id=deployment)
        assert completion
