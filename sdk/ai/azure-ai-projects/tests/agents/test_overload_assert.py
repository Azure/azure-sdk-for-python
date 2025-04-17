# pylint: disable=line-too-long,useless-suppression
import unittest
import pytest
from azure.ai.projects.operations import AgentsOperations
from azure.ai.projects.aio.operations import AgentsOperations as AsyncAgentsOperations
from overload_assert_utils import OverloadAssertion, assert_same_http_requests


class TestDeclarator(unittest.TestCase):

    @pytest.mark.asyncio
    @assert_same_http_requests
    async def test_assert_errors(self, agent: AgentsOperations, _: AsyncAgentsOperations, assertion: OverloadAssertion):
        # This is a special test case tested verified the decorator assert name field presents in one call but not another
        model = "gpt-4-1106-preview"
        name = "first"
        instructions = "You are a helpful assistant"
        body = {"model": model, "name": name, "instructions": instructions}

        agent.create_agent(model=model, instructions=instructions)
        agent.create_agent(body=body)

        # Expect failure because the name field is missing in the second call
        # If it doesn't assert, it means the decorator is not working and the test is failing here
        with pytest.raises(AssertionError):
            assertion.same_http_requests_from(operation_count=2, api_per_operation_count=1)
