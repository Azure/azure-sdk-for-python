import inspect
import io
import json
import json
from unittest.mock import _Call, _CallList, MagicMock, Mock, AsyncMock

import pytest
from azure.ai.projects._model_base import SdkJSONEncoder
from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.operations import AgentsOperations
from azure.ai.projects.aio.operations import AgentsOperations as AsyncAgentsOperations
from typing import List, Dict
from typing import List, MutableMapping, Any, Union

from requests.structures import CaseInsensitiveDict
from azure.ai.projects.models import ThreadMessageOptions, ToolResources, VectorStore


JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


def dict_to_io_bytes(input: Dict[str, Any]) -> io.BytesIO:
    input_string = json.dumps(input, cls=SdkJSONEncoder, exclude_readonly=True)
    return io.BytesIO(input_string.encode("utf-8"))


class Assertion:
    def __init__(self, calls: _CallList, async_calls: _CallList):
        self.calls = calls
        self.async_calls = async_calls

    def _to_str(self, input: Union[None, str, bytes]) -> str:
        json_string = ""
        if isinstance(input, io.BytesIO):
            json_string = input.getvalue().decode("utf-8")
        elif isinstance(input, str):
            json_string = input
        else:
            json_string = "{}"
        return json.dumps(json.loads(json_string), sort_keys=True)

    def _deep_equal_header_except_content_length(
        self, header1: CaseInsensitiveDict, header2: CaseInsensitiveDict
    ) -> bool:
        """
        Compare two HTTP headers for deep equality, except for the Content-Length header.
        Because it seems only created by HttpRequest class automatically when the type is bytes
        """
        header1 = header1.copy()
        header2 = header2.copy()
        header1.pop("Content-Length", None)
        header2.pop("Content-Length", None)
        return header1 == header2

    def _deep_equal_dict(self, dict1, dict2):
        if dict1.keys() != dict2.keys():
            return False
        for key in dict1:
            if not self._deep_equal(dict1[key], dict2[key]):
                return False
        return True

    def _deep_equal(self, obj1: Any, obj2: Any):
        if isinstance(obj1, dict) and isinstance(obj2, dict):
            return self._deep_equal_dict(obj1, obj2)
        elif isinstance(obj1, list) and isinstance(obj2, list):
            if len(obj1) != len(obj2):
                return False
            for item1, item2 in zip(obj1, obj2):
                if not self._deep_equal(item1, item2):
                    return False
            return True
        else:
            return obj1 == obj2

    def _assert_same_http_request(self, calls: List[_Call], index1: int, index2: int):
        """
        Compare two HTTP request objects for deep equality.
        """

        # Compare method, URL, headers, body, and other relevant attributes
        call1 = calls[index1]
        call2 = calls[index2]
        req1 = call1.args[0]
        req2 = call2.args[0]
        assert (
            req1.method == req2.method
        ), f"call[{index1}] method is {req1.method}, but call[{index2}] method is {req2.method}"
        assert req1.url == req2.url, f"call[{index1}] url is {req1.url}, but call[{index2}] url is {req2.url}"
        assert self._to_str(req1.body) == self._to_str(
            req2.body
        ), f"call[{index1}] body is {self._to_str(req1.body)}, but call[{index2}] body is {self._to_str(req2.body)}"
        assert self._deep_equal_header_except_content_length(
            req1.headers, req2.headers
        ), f"call[{index1}] headers are {req1.headers}, but call[{index2}] headers are {req2.headers}"
        assert self._deep_equal(
            call1.kwargs, call2.kwargs
        ), f"call[{index1}] kwargs are {call1.kwargs}, but call[{index2}] kwargs are {call2.kwargs}"

    def same_http_requests_from(self, *, operation_count: int, api_per_operation_count: int):
        all_calls = self.calls + self.async_calls
        assert len(all_calls) == operation_count * api_per_operation_count

        # Compare first followed by second followed by third call etc of each operations,
        # Assert they have the same http request
        for j in range(api_per_operation_count, operation_count * api_per_operation_count, api_per_operation_count):
            for i in range(api_per_operation_count):
                self._assert_same_http_request(all_calls, i, i + j)


def assert_same_http_requests(test_func):
    """
    Decorator to mock pipeline responses and call the test function with the mock clients and assertion.

    :param test_func: The test function to be decorated.
    :return: The wrapper function.
    """

    def _get_mock_client() -> AIProjectClient:
        """Return the fake project client"""
        client = AIProjectClient(
            endpoint="www.bcac95dd-a1eb-11ef-978f-8c1645fec84b.com",
            subscription_id="00000000-0000-0000-0000-000000000000",
            resource_group_name="non-existing-rg",
            project_name="non-existing-project",
            credential=MagicMock(),
        )
        client.agents.submit_tool_outputs_to_run = MagicMock()
        client.agents.submit_tool_outputs_to_stream = MagicMock()
        return client

    def _get_async_mock_client() -> AsyncAIProjectClient:
        """Return the fake project client"""
        client = AsyncAIProjectClient(
            endpoint="www.bcac95dd-a1eb-11ef-978f-8c1645fec84b.com",
            subscription_id="00000000-0000-0000-0000-000000000000",
            resource_group_name="non-existing-rg",
            project_name="non-existing-project",
            credential=MagicMock(),
        )
        client.agents.submit_tool_outputs_to_run = MagicMock()
        client.agents.submit_tool_outputs_to_stream = MagicMock()
        return client

    async def wrapper(self, *args, **kwargs):
        """
        Wrapper function to set up mocks and call the test function.

        :param self: The test class instance.
        :param args: Positional arguments to pass to the test function.
        :param kwargs: Keyword arguments to pass to the test function.
        """
        if not test_func:
            return

        # Mock the pipeline response
        pipeline_response_mock_return = Mock()
        http_response = Mock()
        http_response_json = Mock()
        iter_bytes = Mock()

        # Set up the mock HTTP response
        http_response_json.return_value = {}
        http_response.status_code = 200
        http_response.json = http_response_json
        http_response.iter_bytes = iter_bytes

        # Set up the pipeline response mock
        pipeline_response_mock = Mock()
        pipeline_response_mock_async = AsyncMock()
        pipeline_response_mock.return_value = pipeline_response_mock_return
        pipeline_response_mock_async.return_value = pipeline_response_mock_return
        pipeline_response_mock_return.http_response = http_response

        # Get the mock clients
        client = _get_mock_client()
        async_client = _get_async_mock_client()

        async with async_client:
            with client:
                # Assign the pipeline mock to the client's agent
                client.agents._client._pipeline.run = pipeline_response_mock
                async_client.agents._client._pipeline.run = pipeline_response_mock_async

                # Create an assertion object with the call arguments list
                assertion = Assertion(
                    pipeline_response_mock.call_args_list, pipeline_response_mock_async.call_args_list
                )

                # Call the test function with the mock clients and assertion
                await test_func(self, client.agents, async_client.agents, assertion, *args, **kwargs)

    return wrapper


def set_mock_and_return(obj: Any, func_name: str, *, return_value: Any):
    # Set a mock to run the original implementation but return the specified value
    func = getattr(obj, func_name)

    def mock_func(*args, **kwargs):
        func(*args, **kwargs)
        return return_value

    async def mock_async_func(*args, **kwargs):
        await func(*args, **kwargs)
        return return_value

    if inspect.iscoroutinefunction(func):
        setattr(obj, func_name, AsyncMock(side_effect=mock_async_func))
    else:
        setattr(obj, func_name, Mock(side_effect=mock_func))


class TestSignatures:

    @pytest.mark.asyncio
    @assert_same_http_requests
    async def test_decorator(self, agent: AgentsOperations, _: AsyncAgentsOperations, assertion: Assertion):
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

    @pytest.mark.asyncio
    @assert_same_http_requests
    async def test_create_agent(
        self, agent: AgentsOperations, async_agent: AsyncAgentsOperations, assertion: Assertion
    ):
        model = "gpt-4-1106-preview"
        name = "first"
        instructions = "You are a helpful assistant"
        body = {"model": model, "name": name, "instructions": instructions}

        agent.create_agent(model=model, name=name, instructions=instructions)
        agent.create_agent(body=body)
        agent.create_agent(body=dict_to_io_bytes(body))

        await async_agent.create_agent(model=model, name=name, instructions=instructions)
        await async_agent.create_agent(body=body)
        await async_agent.create_agent(body=dict_to_io_bytes(body))

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=1)

    @pytest.mark.asyncio
    @assert_same_http_requests
    async def test_create_vector_store_and_poll(
        self, agent: AgentsOperations, async_agent: AsyncAgentsOperations, assertion: Assertion
    ):
        file_ids = ["file_id"]
        body = {"file_ids": file_ids}

        set_mock_and_return(
            agent, "create_vector_store", return_value=VectorStore({"id": "store_1", "status": "in_progress"})
        )
        set_mock_and_return(
            agent, "get_vector_store", return_value=VectorStore({"id": "store_1", "status": "completed"})
        )
        agent.create_vector_store_and_poll(file_ids=file_ids, sleep_interval=0)
        agent.create_vector_store_and_poll(body=body, sleep_interval=0)
        agent.create_vector_store_and_poll(body=dict_to_io_bytes(body), sleep_interval=0)

        set_mock_and_return(
            async_agent, "create_vector_store", return_value=VectorStore({"id": "store_1", "status": "in_progress"})
        )
        set_mock_and_return(
            async_agent, "get_vector_store", return_value=VectorStore({"id": "store_1", "status": "completed"})
        )
        await async_agent.create_vector_store_and_poll(file_ids=file_ids, sleep_interval=0)
        await async_agent.create_vector_store_and_poll(body=body, sleep_interval=0)
        await async_agent.create_vector_store_and_poll(body=dict_to_io_bytes(body), sleep_interval=0)

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=2)

    @pytest.mark.asyncio
    @assert_same_http_requests
    async def test_create_thread(
        self, agent: AgentsOperations, async_agent: AsyncAgentsOperations, assertion: Assertion
    ):
        messages: List[ThreadMessageOptions] = []
        tool_resources: ToolResources = ToolResources()
        metadata: Dict[str, str] = {}
        body = {"messages": messages, "tool_resources": tool_resources, "metadata": metadata}

        agent.create_thread(messages=messages, tool_resources=tool_resources, metadata=metadata)
        agent.create_thread(body=body)
        agent.create_thread(body=dict_to_io_bytes(body))

        await async_agent.create_thread(messages=messages, tool_resources=tool_resources, metadata=metadata)
        await async_agent.create_thread(body=body)
        await async_agent.create_thread(body=dict_to_io_bytes(body))

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=1)

    @pytest.mark.asyncio
    @pytest.mark.skip("Defect: during body as JSON and IO Bytes don't, backend not called with stream=False")
    @assert_same_http_requests
    async def test_create_run(self, agent: AgentsOperations, async_agent: AsyncAgentsOperations, assertion: Assertion):
        thread_id = "thread_id"
        assistant_id = "assistant_id"
        body = {"assistant_id": assistant_id}

        agent.create_run(thread_id, assistant_id=assistant_id)
        agent.create_run(thread_id, body=body)
        agent.create_run(thread_id, body=dict_to_io_bytes(body))

        await async_agent.create_run(thread_id, assistant_id=assistant_id)
        await async_agent.create_run(thread_id, body=body)
        await async_agent.create_run(thread_id, body=dict_to_io_bytes(body))

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=1)

    @pytest.mark.asyncio
    @pytest.mark.skip("Defect: during body as JSON and IO Bytes don't, backend not called with stream=True")
    @assert_same_http_requests
    async def test_create_stream(
        self, agent: AgentsOperations, async_agent: AsyncAgentsOperations, assertion: Assertion
    ):
        thread_id = "thread_id"
        assistant_id = "assistant_id"
        body = {"assistant_id": assistant_id}

        agent.create_stream(thread_id, assistant_id=assistant_id)
        agent.create_stream(thread_id, body=body)
        agent.create_stream(thread_id, body=dict_to_io_bytes(body))

        await async_agent.create_stream(thread_id, assistant_id=assistant_id)
        await async_agent.create_stream(thread_id, body=body)
        await async_agent.create_stream(thread_id, body=dict_to_io_bytes(body))

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=1)
