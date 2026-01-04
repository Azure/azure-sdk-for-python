# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport


class TestResponsesAsync(TestBase):

    # To run this test:
    # pytest tests\responses\test_responses_async.py::TestResponsesAsync::test_responses_async -s
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_responses_async(self, **kwargs):

        model = kwargs.get("azure_ai_model_deployment_name")

        client = self.create_async_client(operation_group="agents", **kwargs).get_openai_client()

        async with client:

            response1 = await client.responses.create(
                model=model,
                input="How many feet in a mile?",
            )
            print(f"Response id: {response1.id}, output text: {response1.output_text}")
            assert "5280" in response1.output_text or "5,280" in response1.output_text

            response2 = await client.responses.create(
                model=model, input="And how many meters?", previous_response_id=response1.id
            )
            print(f"Response id: {response2.id}, output text: {response2.output_text}")
            assert "1609" in response2.output_text or "1,609" in response2.output_text
