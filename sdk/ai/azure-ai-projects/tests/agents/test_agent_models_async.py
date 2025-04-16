# pylint: disable=line-too-long,useless-suppression
from typing import Any, AsyncIterator, List
from unittest.mock import AsyncMock, patch
import pytest
import os
from azure.ai.projects.models import (
    AsyncAgentEventHandler,
    BaseAsyncAgentEventHandler,
    SubmitToolOutputsAction,
    ThreadRun,
)
from azure.ai.projects.models._patch import _parse_event
from azure.ai.projects.models import AgentStreamEvent
from azure.ai.projects.models import ThreadRun, RunStep, ThreadMessage, MessageDeltaChunk, RunStepDeltaChunk


def read_file(file_name: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), "assets", f"{file_name}.txt"), "r") as file:
        return file.read()


main_stream_response = read_file("main_stream_response")
fetch_current_datetime_and_weather_stream_response = read_file("fetch_current_datetime_and_weather_stream_response")
send_email_stream_response = read_file("send_email_stream_response")


async def convert_to_byte_iterator(input: str) -> AsyncIterator[bytes]:
    yield input.encode()


async def async_bytes_iter(iterable: List[bytes]) -> AsyncIterator[bytes]:
    for item in iterable:
        yield item


class TestBaseAsyncAgentEventHandler:
    class MyAgentEventhHandler(BaseAsyncAgentEventHandler[str]):
        async def _process_event(self, event_data_str: str) -> str:
            return event_data_str

    async def break_main_stream_response(self, indices: List[int], response: str):
        previous_index = 0
        for index in indices:
            yield response[previous_index:index].encode()
            previous_index = index
        yield response[previous_index:].encode()

    async def mock_callable(self, _: ThreadRun, __: BaseAsyncAgentEventHandler[str]) -> None:
        pass

    @pytest.mark.asyncio
    async def test_event_handler_process_response_when_break_around_event_separators(self):
        # events are split into multiple chunks.
        # Each chunk might contains more than one or incomplete response.
        # Test the chunks are borken around the event separators which are "\n\n"
        handler = self.MyAgentEventhHandler()
        new_line_indices = [i for i in range(len(main_stream_response)) if main_stream_response.startswith("\n\n", i)]

        indices_around_new_lines = [i + offset for i, offset in zip(new_line_indices, [0, -1, 1, 2, 3, 4, 5])]
        handler.initialize(
            self.break_main_stream_response(indices_around_new_lines, main_stream_response), self.mock_callable
        )
        count = 0
        all_event_str: List[str] = []
        async for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1
        assert count == main_stream_response.count("event:")
        assert all_event_str[-1].startswith("event: done")

    @pytest.mark.asyncio
    async def test_event_handler_process_response_when_break_at_the_start(self):
        handler = self.MyAgentEventhHandler()

        handler.initialize(
            # the numbers of the index around the new line characters, middle of the event, or at the end
            self.break_main_stream_response([2], main_stream_response),
            self.mock_callable,
        )
        count = 0
        all_event_str: List[str] = []
        async for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1
        assert count == main_stream_response.count("event:")
        assert all_event_str[-1].startswith("event: done")

    @pytest.mark.asyncio
    async def test_event_handler_process_response_when_break_at_the_end(self):
        handler = self.MyAgentEventhHandler()

        response_len = len(main_stream_response)
        indices_around_new_lines = list(range(response_len - 5, response_len + 1))

        handler.initialize(
            # the numbers of the index around the new line characters, middle of the event, or at the end
            self.break_main_stream_response(indices_around_new_lines, main_stream_response),
            self.mock_callable,
        )
        count = 0
        all_event_str: List[str] = []
        async for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1
        assert count == main_stream_response.count("event:")
        assert all_event_str[-1].startswith("event: done")

    @pytest.mark.asyncio
    async def test_event_handler_chain_responses(self):
        # Test if the event handler can have the second stream followed by the first one.
        handler = self.MyAgentEventhHandler()
        handler.initialize(convert_to_byte_iterator(main_stream_response), self.mock_callable)
        handler.initialize(
            convert_to_byte_iterator(fetch_current_datetime_and_weather_stream_response), self.mock_callable
        )
        count = 0
        all_event_str: List[str] = []
        async for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1

        assert count == main_stream_response.count("event:") + fetch_current_datetime_and_weather_stream_response.count(
            "event:"
        )
        assert all_event_str[-1].startswith("event: done")

    @pytest.mark.asyncio
    async def test_event_handler_reusable(self):
        # Test if the event handler can be reused after a stream is done.
        handler = self.MyAgentEventhHandler()
        handler.initialize(convert_to_byte_iterator(main_stream_response), self.mock_callable)
        count = 0
        all_event_str: List[str] = []
        async for event_str in handler:
            assert event_str.startswith("event:")

        handler.initialize(
            convert_to_byte_iterator(fetch_current_datetime_and_weather_stream_response), self.mock_callable
        )

        async for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1

        assert fetch_current_datetime_and_weather_stream_response.count("event:")
        assert all_event_str[-1].startswith("event: done")

    @pytest.mark.asyncio
    async def test_event_handler_with_split_chinese_char(self):
        response_bytes_split_chinese_char: List[bytes] = [
            b'event: thread.message.delta\ndata: data: {"id":"msg_01","object":"thread.message.delta","delta":{"content":[{"index":0,"type":"text","text":{"value":"\xe5',
            b"\xa4",
            b'\xa9"}}]}}\n\n',
            b'event: thread.message.delta\ndata: data: {"id":"msg_02","object":"thread.message.delta","delta":{"content":[{"index":0,"type":"text","text":{"value":"."}}]}}}\n\nevent: done\ndata: [DONE]\n\n',
        ]

        handler = self.MyAgentEventhHandler()

        handler.initialize(
            # the numbers of the index around the new line characters, middle of the event, or at the end
            async_bytes_iter(response_bytes_split_chinese_char),
            self.mock_callable,
        )
        count = 0
        all_event_str: List[str] = []
        async for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1
        assert count == 3
        assert all_event_str[-1].startswith("event: done")


class TestAsyncAgentEventHandler:

    deserializable_events = [
        AgentStreamEvent.THREAD_CREATED.value,
        AgentStreamEvent.ERROR.value,
        AgentStreamEvent.DONE.value,
    ]

    class MyAgentEventHandler(AsyncAgentEventHandler[None]):
        pass

    @pytest.mark.asyncio
    @patch("azure.ai.projects.models._patch._parse_event")
    async def test_tool_calls(self, mock_parse_event: AsyncMock):
        # Test if the event type and status are met, submit function calls.
        submit_tool_outputs = AsyncMock()
        handler = self.MyAgentEventHandler()

        handler.initialize(convert_to_byte_iterator("event\n\n"), submit_tool_outputs)

        event_obj = ThreadRun({})
        event_obj.status = "requires_action"
        event_obj.required_action = SubmitToolOutputsAction({})
        mock_parse_event.return_value = ("", event_obj)

        async for _ in handler:
            await handler.until_done()

        assert mock_parse_event.call_count == 1
        assert mock_parse_event.call_args[0][0] == "event"
        assert submit_tool_outputs.call_count == 1
        assert submit_tool_outputs.call_args[0] == (event_obj, handler)

    @pytest.mark.asyncio
    @patch("azure.ai.projects.models._patch.AsyncAgentEventHandler.on_unhandled_event")
    @pytest.mark.parametrize("event_type", [e.value for e in AgentStreamEvent])
    async def test_parse_event(self, mock_on_unhandled_event: AsyncMock, event_type: str):
        # Make sure all the event types defined in AgentStreamEvent are deserializable except Created, Done, and Error
        # And ensure handle_event is never raised.

        handler = self.MyAgentEventHandler()
        event_data_str = f"event: {event_type}\ndata: {{}}"
        _, event_obj, _ = await handler._process_event(event_data_str)

        if event_type in self.deserializable_events:
            assert isinstance(event_obj, str)
        else:
            assert not isinstance(event_obj, str)

        # The only event we are not handling today is CREATED which is never sent by backend.
        if event_type == AgentStreamEvent.THREAD_CREATED.value:
            assert mock_on_unhandled_event.call_count == 1
        else:
            assert mock_on_unhandled_event.call_count == 0
