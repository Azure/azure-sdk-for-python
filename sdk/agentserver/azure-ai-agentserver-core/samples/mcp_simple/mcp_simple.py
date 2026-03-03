# mypy: ignore-errors
"""Custom MCP simple sample.

This sample combines the patterns from:
  - langgraph `mcp_simple` (uses MultiServerMCPClient to discover tools)
  - `custom_mock_agent_test` (implements a custom FoundryCBAgent with streaming events)

Goal: When invoked in stream mode, emit MCP list tools related stream events so a
consumer (UI / CLI) can visualize tool enumeration plus a final assistant
message. In non-stream mode, return a single aggregated response summarizing
the tools.

Run:
  python mcp_simple.py

Then call (example):
  curl -X POST http://localhost:8088/responses -H 'Content-Type: application/json' -d '{
        "agent": {"name": "custom_mcp", "type": "agent_reference"},
        "stream": true,
        "input": "List the tools available"
  }'
"""

import datetime
import json
from typing import AsyncGenerator, List

from langchain_mcp_adapters.client import MultiServerMCPClient

from azure.ai.agentserver.core import AgentRunContext, FoundryCBAgent
from azure.ai.agentserver.core.models import Response as OpenAIResponse
from azure.ai.agentserver.core.models.projects import (
    ItemContentOutputText,
    MCPListToolsItemResource,
    MCPListToolsTool,
    ResponseCompletedEvent,
    ResponseCreatedEvent,
    ResponseMCPListToolsCompletedEvent,
    ResponseMCPListToolsInProgressEvent,
    ResponseOutputItemAddedEvent,
    ResponsesAssistantMessageItemResource,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
)


class MCPToolsAgent(FoundryCBAgent):
    def __init__(self):  # noqa: D401
        super().__init__()
        # Lazy init; created on first request to avoid startup latency if unused
        self._mcp_client = None

    async def _get_client(self) -> MultiServerMCPClient:
        if self._mcp_client is None:
            # Mirror langgraph sample server config
            self._mcp_client = MultiServerMCPClient(
                {
                    "mslearn": {
                        "url": "https://learn.microsoft.com/api/mcp",
                        "transport": "streamable_http",
                    }
                }
            )
        return self._mcp_client

    async def _list_tools(self) -> List[MCPListToolsTool]:
        client = await self._get_client()
        try:
            raw_tools = await client.get_tools()
            tools: List[MCPListToolsTool] = []
            for t in raw_tools:
                # Support either dict-like or attribute-based tool objects
                if isinstance(t, dict):
                    name = t.get("name", "unknown_tool")
                    description = t.get("description")
                    schema = (
                        t.get("input_schema")
                        or t.get("schema")
                        or t.get("parameters")
                        or {}
                    )
                else:  # Fallback to attribute access
                    name = getattr(t, "name", "unknown_tool")
                    description = getattr(t, "description", None)
                    schema = (
                        getattr(t, "input_schema", None)
                        or getattr(t, "schema", None)
                        or getattr(t, "parameters", None)
                        or {}
                    )
                tools.append(
                    MCPListToolsTool(
                        name=name,
                        description=description,
                        input_schema=schema,
                    )
                )
            if not tools:
                raise ValueError("No tools discovered from MCP server")
            return tools
        except Exception:  # noqa: BLE001
            # Provide deterministic fallback so sample always works offline
            return [
                MCPListToolsTool(
                    name="fallback_echo",
                    description="Echo back provided text.",
                    input_schema={
                        "type": "object",
                        "properties": {"text": {"type": "string"}},
                        "required": ["text"],
                    },
                )
            ]

    async def agent_run(self, context: AgentRunContext):  # noqa: D401
        """Implements the FoundryCBAgent contract.

        Streaming path emits MCP list tools events + assistant summary.
        Non-stream path returns aggregated assistant message.
        """

        tools = await self._list_tools()

        if context.stream:

            async def stream() -> AsyncGenerator:  # noqa: D401
                # Initial empty response context (pattern from mock sample)
                yield ResponseCreatedEvent(response=OpenAIResponse(output=[]))

                # Indicate listing in progress
                yield ResponseMCPListToolsInProgressEvent()

                mcp_item = MCPListToolsItemResource(
                    id=context.id_generator.generate("mcp_list"),
                    server_label="mslearn",
                    tools=tools,
                )
                yield ResponseOutputItemAddedEvent(output_index=0, item=mcp_item)
                yield ResponseMCPListToolsCompletedEvent()

                # Assistant streaming summary
                assistant_item = ResponsesAssistantMessageItemResource(
                    id=context.id_generator.generate_message_id(),
                    status="in_progress",
                    content=[ItemContentOutputText(text="", annotations=[])],
                )
                yield ResponseOutputItemAddedEvent(output_index=1, item=assistant_item)

                summary_text = "Discovered MCP tools: " + ", ".join(
                    t.name for t in tools
                )
                assembled = ""
                parts = summary_text.split(" ")
                for i, token in enumerate(parts):
                    piece = token if i == len(parts) - 1 else token + " "  # keep spaces
                    assembled += piece
                    yield ResponseTextDeltaEvent(
                        output_index=1, content_index=0, delta=piece
                    )
                yield ResponseTextDoneEvent(
                    output_index=1, content_index=0, text=assembled
                )

                final_response = OpenAIResponse(
                    metadata={},
                    temperature=0.0,
                    top_p=0.0,
                    user="user",
                    id=context.response_id,
                    created_at=datetime.datetime.now(),
                    output=[
                        mcp_item,
                        ResponsesAssistantMessageItemResource(
                            id=assistant_item.id,
                            status="completed",
                            content=[
                                ItemContentOutputText(text=assembled, annotations=[])
                            ],
                        ),
                    ],
                )
                yield ResponseCompletedEvent(response=final_response)

            return stream()

        # Non-stream path: single assistant message
        # Build a JSON-serializable summary. Avoid dumping complex model/schema objects that
        # can include non-serializable metaclass references (seen in error stacktrace).
        safe_tools = []
        for t in tools:
            schema = t.input_schema
            # Simplify schema to plain dict/str; if not directly serializable, fallback to string.
            if isinstance(schema, (str, int, float, bool)) or schema is None:
                safe_schema = schema
            elif isinstance(schema, dict):
                # Shallow copy ensuring nested values are primitive or stringified
                safe_schema = {}
                for k, v in schema.items():
                    if isinstance(v, (str, int, float, bool, type(None), list, dict)):
                        safe_schema[k] = v
                    else:
                        safe_schema[k] = str(v)
            else:
                safe_schema = str(schema)
            safe_tools.append(
                {
                    "name": t.name,
                    "description": t.description,
                    # Provide only top-level schema keys if dict.
                    "input_schema_keys": list(safe_schema.keys())
                    if isinstance(safe_schema, dict)
                    else safe_schema,
                }
            )
        summary = {
            "server_label": "mslearn",
            "tool_count": len(tools),
            "tools": safe_tools,
        }
        content = [
            ItemContentOutputText(
                text="MCP tool listing completed.\n" + json.dumps(summary, indent=2),
                annotations=[],
            )
        ]
        return OpenAIResponse(
            metadata={},
            temperature=0.0,
            top_p=0.0,
            user="user",
            id="id",
            created_at=datetime.datetime.now(),
            output=[
                ResponsesAssistantMessageItemResource(
                    id=context.id_generator.generate_message_id(),
                    status="completed",
                    content=content,
                )
            ],
        )


my_agent = MCPToolsAgent()

if __name__ == "__main__":
    my_agent.run()
