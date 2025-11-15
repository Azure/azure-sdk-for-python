# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

# import os
import pytest
from test_base import TestBase, servicePreparer, recorded_by_proxy_httpx
from devtools_testutils import is_live_and_not_recording


class TestResponses(TestBase):

    # To run this test:
    # pytest tests\responses\test_responses.py::TestResponses::test_responses -s
    @servicePreparer()
    @recorded_by_proxy_httpx
    def test_responses(self, **kwargs):
        """
        Test creating a responses call (no Agents, no Conversation).

        Routes used in this test:

        Action REST API Route                                OpenAI Client Method
        ------+---------------------------------------------+-----------------------------------
        POST   /openai/responses                             client.responses.create()
        """
        model = self.test_agents_params["model_deployment_name"]

        client = self.create_client(operation_group="agents", **kwargs).get_openai_client()

        response1 = client.responses.create(
            model=model,
            input="How many feet in a mile?",
        )
        print(f"Response id: {response1.id}, output text: {response1.output_text}")
        assert "5280" in response1.output_text or "5,280" in response1.output_text

        response2 = client.responses.create(
            model=model, input="And how many meters?", previous_response_id=response1.id
        )
        print(f"Response id: {response2.id}, output text: {response2.output_text}")
        assert "1609" in response2.output_text or "1,609" in response2.output_text
