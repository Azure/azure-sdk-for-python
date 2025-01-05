from typing import AsyncIterator, List
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
fetch_current_datetime_stream_response = read_file("fetch_current_datetime_stream_response")


async def convert_to_byte_iterator(main_stream_response: str) -> AsyncIterator[bytes]:
    yield main_stream_response.encode()


class TestBaseAsyncAgentEventHandler:
    class MyAgentEventhHandler(BaseAsyncAgentEventHandler[str]):
        async def _process_event(self, event_data_str: str) -> str:
            return event_data_str

    async def break_main_stream_response(self, indices: List[int], main_stream_response: str):
        previous_index = 0
        for index in indices:
            yield main_stream_response[previous_index:index].encode()
            previous_index = index
        yield main_stream_response[previous_index:].encode()

    async def mock_callable(self, _: ThreadRun, __: BaseAsyncAgentEventHandler[str]) -> None:
        pass

    @pytest.mark.asyncio
    async def test_event_handler_process_response_when_break_around_indices(self):
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
        handler = self.MyAgentEventhHandler()
        handler.initialize(convert_to_byte_iterator(main_stream_response), self.mock_callable)
        handler.initialize(convert_to_byte_iterator(fetch_current_datetime_stream_response), self.mock_callable)
        count = 0
        all_event_str: List[str] = []
        async for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1

        assert count == main_stream_response.count("event:") + fetch_current_datetime_stream_response.count("event:")
        assert all_event_str[-1].startswith("event: done")

    @pytest.mark.asyncio
    async def test_event_handler_reusable(self):
        handler = self.MyAgentEventhHandler()
        handler.initialize(convert_to_byte_iterator(main_stream_response), self.mock_callable)
        count = 0
        all_event_str: List[str] = []
        async for event_str in handler:
            assert event_str.startswith("event:")

        handler.initialize(convert_to_byte_iterator(fetch_current_datetime_stream_response), self.mock_callable)

        async for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1

        assert fetch_current_datetime_stream_response.count("event:")
        assert all_event_str[-1].startswith("event: done")


class TestAsyncAgentEventHandler:

    class MyAgentEventHandler(AsyncAgentEventHandler[None]):
        pass

    @pytest.mark.asyncio
    @patch("azure.ai.projects.models._patch._parse_event")
    async def test_tool_calls(self, mock_parse_event: AsyncMock):
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


class TestParseEvent:

    def test_parse_event_thread_run_created(self):
        event_data_str = 'event: thread.run.created\ndata: {"id": "123"}'
        event_type, event_obj = _parse_event(event_data_str)
        assert event_type == AgentStreamEvent.THREAD_RUN_CREATED.value
        assert isinstance(event_obj, ThreadRun)
        assert event_obj.id == "123"

    def test_parse_event_thread_run_step_created(self):
        event_data_str = 'event: thread.run.step.created\ndata: {"id": "456"}'
        event_type, event_obj = _parse_event(event_data_str)
        assert event_type == AgentStreamEvent.THREAD_RUN_STEP_CREATED.value
        assert isinstance(event_obj, RunStep)
        assert event_obj.id == "456"

    def test_parse_event_thread_message_created(self):
        event_data_str = 'event: thread.message.created\ndata: {"id": "789"}'
        event_type, event_obj = _parse_event(event_data_str)
        assert event_type == AgentStreamEvent.THREAD_MESSAGE_CREATED.value
        assert isinstance(event_obj, ThreadMessage)
        assert event_obj.id == "789"

    def test_parse_event_thread_message_delta(self):
        event_data_str = 'event: thread.message.delta\ndata: {"id": "101"}'
        event_type, event_obj = _parse_event(event_data_str)
        assert event_type == AgentStreamEvent.THREAD_MESSAGE_DELTA.value
        assert isinstance(event_obj, MessageDeltaChunk)
        assert event_obj.id == "101"

    def test_parse_event_thread_run_step_delta(self):
        event_data_str = 'event: thread.run.step.delta\ndata: {"id": "202"}'
        event_type, event_obj = _parse_event(event_data_str)
        assert event_type == AgentStreamEvent.THREAD_RUN_STEP_DELTA.value
        assert isinstance(event_obj, RunStepDeltaChunk)
        assert event_obj.id == "202"

    def test_parse_event_invalid_event_type(self):
        event_data_str = 'event: invalid.event\ndata: {"id": "303"}'
        event_type, event_obj = _parse_event(event_data_str)
        assert event_type == "invalid.event"
        assert event_obj == "{'id': '303'}"

    def test_parse_event_no_event_type(self):
        event_data_str = 'data: {"id": "404"}'
        with pytest.raises(ValueError):
            _parse_event(event_data_str)

    def test_parse_event_invalid_json(self):
        event_data_str = "event: thread.run.created\ndata: invalid_json"
        event_type, event_obj = _parse_event(event_data_str)
        assert event_type == AgentStreamEvent.THREAD_RUN_CREATED.value
        assert event_obj == "invalid_json"
