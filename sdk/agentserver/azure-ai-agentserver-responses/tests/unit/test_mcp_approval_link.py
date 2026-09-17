# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""MCP approval identity survives streamed and terminal representations."""

import pytest

from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from azure.ai.agentserver.responses.aio.streaming._event_stream import ResponseEventStream as AsyncResponseEventStream


@pytest.mark.parametrize("failed", [False, True])
@pytest.mark.parametrize("stream_type", [ResponseEventStream, AsyncResponseEventStream])
def test_mcp_approval_link_survives_output_and_response(failed: bool, stream_type: type[ResponseEventStream]) -> None:
    stream = stream_type(response_id="resp_link")
    stream.emit_created()
    call = stream.add_output_item_mcp_call("weather", "lookup", approval_request_id="approval_123")
    added = call.emit_added()
    call.emit_arguments_done("{}")
    if failed:
        call.emit_failed()
    else:
        call.emit_completed()
    done = call.emit_done(output="result")
    terminal = stream.emit_completed()
    for item in [added["item"], done["item"], terminal["response"]["output"][0]]:
        assert item["approval_request_id"] == "approval_123"
    assert done["item"]["status"] == ("failed" if failed else "completed")


@pytest.mark.parametrize("stream_type", [ResponseEventStream, AsyncResponseEventStream])
def test_unapproved_mcp_call_has_no_invented_link(stream_type: type[ResponseEventStream]) -> None:
    stream = stream_type(response_id="resp_unlinked")
    stream.emit_created()
    call = stream.add_output_item_mcp_call("weather", "lookup")
    assert "approval_request_id" not in call.emit_added()["item"]
    assert "approval_request_id" not in call.emit_done(output="result")["item"]


@pytest.mark.parametrize("value", ["", "   "])
@pytest.mark.parametrize("stream_type", [ResponseEventStream, AsyncResponseEventStream])
def test_mcp_approval_link_rejects_empty_identity(value: str, stream_type: type[ResponseEventStream]) -> None:
    stream = stream_type(response_id="resp_invalid")
    with pytest.raises(ValueError):
        stream.add_output_item_mcp_call("weather", "lookup", approval_request_id=value)
