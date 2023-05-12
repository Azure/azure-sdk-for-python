# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import openai
from devtools_testutils import AzureRecordedTestCase


class TestCompletions(AzureRecordedTestCase):

    def test_completion(self, azure_openai_creds):
        deployment = azure_openai_creds["completions_name"]

        completion = openai.Completion.create(prompt="hello world", deployment_id=deployment)
        assert completion
