# pylint: disable=line-too-long,useless-suppression
import io
import json
import unittest
from typing import Any, Dict, IO, Union
from unittest.mock import Mock, MagicMock, AsyncMock
from requests.structures import CaseInsensitiveDict
import inspect
from azure.ai.agents import AgentsClient
from azure.ai.agents.aio import AgentsClient as AsyncAgentsClient
from azure.ai.agents._utils.model_base import SdkJSONEncoder


def dict_to_io_bytes(input: Dict[str, Any]) -> io.BytesIO:
    input_string = json.dumps(input, cls=SdkJSONEncoder, exclude_readonly=True)
    return io.BytesIO(input_string.encode("utf-8"))


class OverloadAssertion:
    def __init__(self, mock: Mock, async_mock: AsyncMock, **args):
        self.mock = mock
        self.async_mock = async_mock

    def _to_dict(self, input: Union[None, str, IO[bytes]]) -> Dict[str, Any]:
        json_string = ""
        if isinstance(input, io.BytesIO):
            json_string = input.getvalue().decode("utf-8")
        elif isinstance(input, str):
            json_string = input
        else:
            json_string = "{}"
        return json.loads(json_string)

    def assert_deep_equal_header_except_content_length(
        self, header1: CaseInsensitiveDict, header2: CaseInsensitiveDict, msg: str
    ):
        """
        Compare two HTTP headers for deep equality, except for the Content-Length header.
        Because it seems only created by HttpRequest class automatically when the type is bytes
        """
        header1 = header1.copy()
        header2 = header2.copy()
        header1.pop("Content-Length", None)
        header2.pop("Content-Length", None)
        unittest.TestCase().assertDictEqual(dict(header1), dict(header2), msg)

    def _assert_same_http_request(self, call1: Any, call2: Any, index1: int, index2: int):
        """
        Compare two HTTP request objects for deep equality.
        """

        # Compare method, URL, headers, body, and other relevant attributes
        req1 = call1.args[0]
        req2 = call2.args[0]
        req1_body = self._to_dict(req1.body)
        req2_body = self._to_dict(req2.body)
        unittest.TestCase().assertEqual(
            req1.method,
            req2.method,
            f"call[{index1}] method is {req1.method}, but call[{index2}] method is {req2.method}",
        )
        unittest.TestCase().assertEqual(
            req1.url, req2.url, f"call[{index1}] url is {req1.url}, but call[{index2}] url is {req2.url}"
        )
        unittest.TestCase().assertDictEqual(
            req1_body,
            req2_body,
            f"call[{index1}] body is {json.dumps(req1_body, sort_keys=True)}, but call[{index2}] body is {json.dumps(req2_body, sort_keys=True)}",
        )
        self.assert_deep_equal_header_except_content_length(
            req1.headers,
            req2.headers,
            f"call[{index1}] headers are {req1.headers}, but call[{index2}] headers are {req2.headers}",
        )
        unittest.TestCase().assertDictEqual(
            call1.kwargs,
            call2.kwargs,
            f"call[{index1}] kwargs are {call1.kwargs}, but call[{index2}] kwargs are {call2.kwargs}",
        )

    def same_http_requests_from(self, *, operation_count: int, api_per_operation_count: int):
        all_calls = self.mock.call_args_list + self.async_mock.call_args_list
        assert len(all_calls) == operation_count * api_per_operation_count

        # Compare first followed by second followed by third call etc of each operations,
        # Assert they have the same http request
        template = all_calls[:api_per_operation_count]
        for j in range(api_per_operation_count, len(all_calls), api_per_operation_count):
            for i, (api_one, api_other) in enumerate(zip(template, all_calls[j : j + api_per_operation_count])):
                self._assert_same_http_request(api_one, api_other, i, i + j)


def assert_same_http_requests(test_func):
    """
    Decorator to mock pipeline responses and call the test function with the mock clients and assertion.

    :param test_func: The test function to be decorated.
    :return: The wrapper function.
    """

    def _get_mock_client() -> AgentsClient:
        """Return the fake project client"""
        client = AgentsClient(
            endpoint="www.bcac95dd-a1eb-11ef-978f-8c1645fec84b.com",
            credential=MagicMock(),
        )
        client.submit_tool_outputs_to_run = MagicMock()
        client.submit_tool_outputs_to_stream = MagicMock()
        return client

    def _get_async_mock_client() -> AsyncAgentsClient:
        """Return the fake project client"""
        client = AsyncAgentsClient(
            endpoint="www.bcac95dd-a1eb-11ef-978f-8c1645fec84b.com",
            subscription_id="00000000-0000-0000-0000-000000000000",
            resource_group_name="non-existing-rg",
            project_name="non-existing-project",
            credential=AsyncMock(),
        )
        client.submit_tool_outputs_to_run = AsyncMock()
        client.submit_tool_outputs_to_stream = AsyncMock()
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
                # Assign the pipeline mock to the client
                client._client._pipeline.run = pipeline_response_mock
                async_client._client._pipeline.run = pipeline_response_mock_async

                # Create an assertion object with the call arguments list
                assertion = OverloadAssertion(pipeline_response_mock, pipeline_response_mock_async)

                # Call the test function with the mock clients and assertion
                await test_func(self, client, async_client, assertion, *args, **kwargs)

    return wrapper


def get_mock_fn(fn, return_val):
    def mock_func(*args, **kwargs):
        fn(*args, **kwargs)
        return return_val

    async def mock_func_async(*args, **kwargs):
        await fn(*args, **kwargs)
        return return_val

    if inspect.iscoroutinefunction(fn):
        return mock_func_async
    return mock_func
