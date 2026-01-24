import importlib
import inspect
from types import SimpleNamespace
from unittest.mock import AsyncMock

from typing import Any

import pytest
from agent_framework import AIFunction, ChatOptions
from pydantic import Field, create_model

# Import schema models directly from client._models to avoid heavy azure.identity import
# chain triggered by azure.ai.agentserver.core.__init__.py
from azure.ai.agentserver.core.tools.client._models import (
	FoundryHostedMcpTool,
	FoundryToolDetails,
	ResolvedFoundryTool,
	SchemaDefinition,
	SchemaProperty,
	SchemaType,
)

# Load _foundry_tools module directly without triggering parent __init__ which has heavy deps
import importlib.util
import sys
from pathlib import Path

foundry_tools_path = Path(__file__).parent.parent.parent / "azure" / "ai" / "agentserver" / "agentframework" / "_foundry_tools.py"
spec = importlib.util.spec_from_file_location("_foundry_tools", foundry_tools_path)
foundry_tools_module = importlib.util.module_from_spec(spec)
sys.modules["_foundry_tools"] = foundry_tools_module
spec.loader.exec_module(foundry_tools_module)

FoundryToolClient = foundry_tools_module.FoundryToolClient
FoundryToolsChatMiddleware = foundry_tools_module.FoundryToolsChatMiddleware
_attach_signature_from_pydantic_model = foundry_tools_module._attach_signature_from_pydantic_model


@pytest.mark.unit
def test_attach_signature_from_pydantic_model_required_and_optional() -> None:
	InputModel = create_model(
		"InputModel",
		required_int=(int, Field(description="required")),
		optional_str=(str | None, Field(default=None, description="optional")),
	)

	async def tool_func(**kwargs):
		return kwargs

	_attach_signature_from_pydantic_model(tool_func, InputModel)

	sig = inspect.signature(tool_func)
	assert list(sig.parameters.keys()) == ["required_int", "optional_str"]
	assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in sig.parameters.values())
	assert sig.parameters["required_int"].default is inspect._empty
	assert sig.parameters["optional_str"].default is None

	# Ensure annotations are also attached.
	assert tool_func.__annotations__["required_int"] is int
	assert tool_func.__annotations__["return"] is Any


def _make_resolved_tool(*, name: str = "my_tool", description: str = "desc") -> ResolvedFoundryTool:
	schema = SchemaDefinition(
		properties={
			"a": SchemaProperty(type=SchemaType.STRING, description="field a"),
			"b": SchemaProperty(type=SchemaType.INTEGER, description="field b"),
		},
		required={"a"},
	)
	definition = FoundryHostedMcpTool(name=name)
	details = FoundryToolDetails(name=name, description=description, input_schema=schema)
	return ResolvedFoundryTool(definition=definition, details=details)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_to_aifunction_builds_pydantic_model_and_invokes(monkeypatch: pytest.MonkeyPatch) -> None:
	resolved_tool = _make_resolved_tool(name="echo", description="Echo tool")

	invoke = AsyncMock(return_value={"ok": True})
	server_context = SimpleNamespace(
		tools=SimpleNamespace(
			invoke=invoke,
			catalog=SimpleNamespace(list=AsyncMock()),
		)
	)
	monkeypatch.setattr(
		foundry_tools_module.AgentServerContext,
		"get",
		classmethod(lambda cls: server_context),
	)

	client = FoundryToolClient(tools=[])
	ai_func = client._to_aifunction(resolved_tool)
	assert isinstance(ai_func, AIFunction)
	assert ai_func.name == "echo"
	assert ai_func.description == "Echo tool"

	# Signature should be attached from schema (a required, b optional)
	sig = inspect.signature(ai_func.func)
	assert list(sig.parameters.keys()) == ["a", "b"]
	assert sig.parameters["a"].default is inspect._empty
	assert sig.parameters["b"].default is None

	result = await ai_func.func(a="hi", b=123)
	assert result == {"ok": True}
	invoke.assert_awaited_once_with(resolved_tool, {"a": "hi", "b": 123})


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_tools_uses_catalog_and_converts(monkeypatch: pytest.MonkeyPatch) -> None:
	allowed = [FoundryHostedMcpTool(name="allowed_tool")]
	resolved = [_make_resolved_tool(name="allowed_tool", description="Allowed")]

	catalog_list = AsyncMock(return_value=resolved)
	server_context = SimpleNamespace(
		tools=SimpleNamespace(
			catalog=SimpleNamespace(list=catalog_list),
			invoke=AsyncMock(),
		)
	)
	monkeypatch.setattr(
		foundry_tools_module.AgentServerContext,
		"get",
		classmethod(lambda cls: server_context),
	)

	client = FoundryToolClient(tools=allowed)
	funcs = await client.list_tools()

	catalog_list.assert_awaited_once()
	args, _kwargs = catalog_list.await_args
	assert args[0] == list(allowed)

	assert len(funcs) == 1
	assert isinstance(funcs[0], AIFunction)
	assert funcs[0].name == "allowed_tool"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_middleware_process_creates_chat_options_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
	middleware = FoundryToolsChatMiddleware(tools=[])

	async def dummy_tool(**kwargs):
		return kwargs

	DummyInput = create_model("DummyInput")
	injected = [AIFunction(name="t", description="d", func=dummy_tool, input_model=DummyInput)]
	monkeypatch.setattr(middleware._foundry_tool_client, "list_tools", AsyncMock(return_value=injected))

	context = SimpleNamespace(chat_options=None)
	next_fn = AsyncMock()

	await middleware.process(context, next_fn)

	assert isinstance(context.chat_options, ChatOptions)
	assert context.chat_options.tools == injected
	next_fn.assert_awaited_once_with(context)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_middleware_process_appends_to_existing_chat_options(monkeypatch: pytest.MonkeyPatch) -> None:
	middleware = FoundryToolsChatMiddleware(tools=[])

	async def dummy_tool(**kwargs):
		return kwargs

	DummyInput = create_model("DummyInput")
	injected = [AIFunction(name="t2", description="d2", func=dummy_tool, input_model=DummyInput)]
	monkeypatch.setattr(middleware._foundry_tool_client, "list_tools", AsyncMock(return_value=injected))

	# Existing ChatOptions with no tools should become injected
	context = SimpleNamespace(chat_options=ChatOptions())
	next_fn = AsyncMock()
	await middleware.process(context, next_fn)
	assert context.chat_options.tools == injected

	# Existing ChatOptions with tools should be appended
	existing = [AIFunction(name="t1", description="d1", func=dummy_tool, input_model=DummyInput)]
	context = SimpleNamespace(chat_options=ChatOptions(tools=existing))
	next_fn = AsyncMock()
	await middleware.process(context, next_fn)
	assert context.chat_options.tools == existing + injected
	assert next_fn.await_count == 1
