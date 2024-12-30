from typing import List
import pytest
import os
from azure.ai.projects.models import BaseAsyncAgentEventHandler, ThreadRun


event_stream = ""
with open(os.path.join(os.path.dirname(__file__), "event_stream.txt"), "r") as file:
    event_stream = file.read()


class MyAgentEventhHandler(BaseAsyncAgentEventHandler[str]):
    async def _process_event(self, event_data_str: str) -> str:
        return event_data_str


async def break_event_stream(indices: List[int], event_stream: str):
    previous_index = 0
    for index in indices:
        yield event_stream[previous_index:index].encode()
        previous_index = index
    yield event_stream[previous_index:].encode()


async def mock_callable(thread_run: ThreadRun, handler: BaseAsyncAgentEventHandler[str]) -> None:
    pass


@pytest.mark.asyncio
async def test_break_pattern():

    handler = MyAgentEventhHandler()
    handler.initialize(
        break_event_stream([2, 3882, 3954, 3956, 11920, 12470, 13839, 46344], event_stream), mock_callable, None
    )
    count = 0
    all_event_str: List[str] = []
    async for event_str in handler:
        assert event_str.startswith("event:")
        all_event_str.append(event_str)
        count += 1
    assert count == 160
    assert all_event_str[-2].startswith("event: thread.run.completed")
    assert all_event_str[-1].startswith("event: done")
