# pylint: disable=line-too-long,useless-suppression
from typing import Iterator, List
from unittest.mock import MagicMock, Mock, patch
import pytest
import os
from azure.ai.agents.models import (
    AgentEventHandler,
    AgentStreamEvent,
    BaseAgentEventHandler,
    MessageDeltaChunk,
    RunStep,
    RunStepDeltaChunk,
    SubmitToolOutputsAction,
    ThreadMessage,
    ThreadRun,
)
from azure.ai.agents.models._patch import _parse_event


def read_file(file_name: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), "assets", f"{file_name}.txt"), "r") as file:
        return file.read()


main_stream_response = read_file("main_stream_response")
fetch_current_datetime_and_weather_stream_response = read_file("fetch_current_datetime_and_weather_stream_response")


def convert_to_byte_iterator(input: str) -> Iterator[bytes]:
    yield input.encode()


class TestBaseAgentEventHandler:
    class MyAgentEventhHandler(BaseAgentEventHandler[str]):
        def _process_event(self, event_data_str: str) -> str:
            return event_data_str

    def break_main_stream_response(self, indices: List[int], response: str):
        previous_index = 0
        for index in indices:
            yield response[previous_index:index].encode()
            previous_index = index
        yield response[previous_index:].encode()

    def mock_callable(self, _: ThreadRun, __: BaseAgentEventHandler[str]) -> None:
        pass

    def test_event_handler_process_response_when_break_around_event_separators(self):
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
        for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1
        assert count == main_stream_response.count("event:")
        assert all_event_str[-1].startswith("event: done")

    def test_event_handler_process_response_when_break_at_the_start(self):
        handler = self.MyAgentEventhHandler()

        handler.initialize(
            # the numbers of the index around the new line characters, middle of the event, or at the end
            self.break_main_stream_response([2], main_stream_response),
            self.mock_callable,
        )
        count = 0
        all_event_str: List[str] = []
        for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1
        assert count == main_stream_response.count("event:")
        assert all_event_str[-1].startswith("event: done")

    def test_event_handler_process_response_when_break_at_the_end(self):
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
        for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1
        assert count == main_stream_response.count("event:")
        assert all_event_str[-1].startswith("event: done")

    def test_event_handler_chain_responses(self):
        # Test if the event handler can have the second stream followed by the first one.
        handler = self.MyAgentEventhHandler()
        handler.initialize(convert_to_byte_iterator(main_stream_response), self.mock_callable)
        handler.initialize(
            convert_to_byte_iterator(fetch_current_datetime_and_weather_stream_response), self.mock_callable
        )
        count = 0
        all_event_str: List[str] = []
        for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1

        assert count == main_stream_response.count("event:") + fetch_current_datetime_and_weather_stream_response.count(
            "event:"
        )
        assert all_event_str[-1].startswith("event: done")

    def test_event_handler_reusable(self):
        # Test if the event handler can be reused after a stream is done.
        handler = self.MyAgentEventhHandler()
        handler.initialize(convert_to_byte_iterator(main_stream_response), self.mock_callable)
        count = 0
        all_event_str: List[str] = []
        for event_str in handler:
            assert event_str.startswith("event:")

        handler.initialize(
            convert_to_byte_iterator(fetch_current_datetime_and_weather_stream_response), self.mock_callable
        )

        for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1

        assert fetch_current_datetime_and_weather_stream_response.count("event:")
        assert all_event_str[-1].startswith("event: done")

    def test_event_handler_with_split_chinese_char(self):
        response_bytes_split_chinese_char: List[bytes] = [
            b'event: thread.message.delta\ndata: data: {"id":"msg_01","object":"thread.message.delta","delta":{"content":[{"index":0,"type":"text","text":{"value":"\xe5',
            b"\xa4",
            b'\xa9"}}]}}\n\n',
            b'event: thread.message.delta\ndata: data: {"id":"msg_02","object":"thread.message.delta","delta":{"content":[{"index":0,"type":"text","text":{"value":"."}}]}}}\n\nevent: done\ndata: [DONE]\n\n',
        ]

        handler = self.MyAgentEventhHandler()

        handler.initialize(
            # the numbers of the index around the new line characters, middle of the event, or at the end
            iter(response_bytes_split_chinese_char),
            self.mock_callable,
        )
        count = 0
        all_event_str: List[str] = []
        for event_str in handler:
            assert event_str.startswith("event:")
            all_event_str.append(event_str)
            count += 1
        assert count == 3
        assert all_event_str[-1].startswith("event: done")


class TestAgentEventHandler:

    deserializable_events = [
        AgentStreamEvent.THREAD_CREATED.value,
        AgentStreamEvent.ERROR.value,
        AgentStreamEvent.DONE.value,
    ]

    class MyAgentEventHandler(AgentEventHandler[None]):
        pass

    @patch("azure.ai.agents.models._patch._parse_event")
    def test_tool_calls(self, mock_parse_event: Mock):
        # Test if the event type and status are met, submit function calls.
        submit_tool_outputs = MagicMock(return_value=[{"all": "good"}])
        handler = self.MyAgentEventHandler()

        handler.initialize(convert_to_byte_iterator("event\n\n"), submit_tool_outputs)

        event_obj = ThreadRun({})
        event_obj.status = "requires_action"
        event_obj.required_action = SubmitToolOutputsAction({})
        mock_parse_event.return_value = ("", event_obj)

        for _ in handler:
            handler.until_done()

        assert mock_parse_event.call_count == 1
        assert mock_parse_event.call_args[0][0] == "event"
        assert submit_tool_outputs.call_count == 1
        assert submit_tool_outputs.call_args[0] == (event_obj, handler, True)

    @patch("azure.ai.agents.models._patch.AgentEventHandler.on_unhandled_event")
    @pytest.mark.parametrize("event_type", [e.value for e in AgentStreamEvent])
    def test_parse_event(self, mock_on_unhandled_event: Mock, event_type: str):
        # Make sure all the event types defined in AgentStreamEvent are deserializable except Created, Done, and Error
        # And ensure handle_event is never raised.

        handler = self.MyAgentEventHandler()
        event_data_str = f"event: {event_type}\ndata: {{}}"
        _, event_obj, _ = handler._process_event(event_data_str)

        if event_type in self.deserializable_events:
            assert isinstance(event_obj, str)
        else:
            assert not isinstance(event_obj, str)

        # The only event we are not handling today is CREATED which is never sent by backend.
        if event_type == AgentStreamEvent.THREAD_CREATED.value:
            assert mock_on_unhandled_event.call_count == 1
        else:
            assert mock_on_unhandled_event.call_count == 0


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
