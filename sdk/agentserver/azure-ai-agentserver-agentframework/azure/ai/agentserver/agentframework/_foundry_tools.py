# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

import asyncio
import inspect
from typing import Any, AsyncIterable, Callable, Dict, List, Optional, Sequence

from agent_framework import AIFunction, BaseChatClient, ChatOptions, Context, ContextProvider
from pydantic import BaseModel, Field, create_model

from azure.ai.agentserver.core import AgentServerContext
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.tools import FoundryToolLike, ResolvedFoundryTool

logger = get_logger()


def _attach_signature_from_pydantic_model(func, input_model) -> None:
    params = []
    annotations: Dict[str, Any] = {}

    for name, field in input_model.model_fields.items():
        ann = field.annotation or Any
        annotations[name] = ann

        default = inspect._empty if field.is_required() else field.default
        params.append(
            inspect.Parameter(
                name=name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=default,
                annotation=ann,
            )
        )

    func.__signature__ = inspect.Signature(parameters=params, return_annotation=Any)
    func.__annotations__ = {**annotations, "return": Any}

class FoundryToolClient:

    def __init__(
        self,
        tools: Sequence[FoundryToolLike],
    ) -> None:
        self._allowed_tools: List[FoundryToolLike] = list(tools)

    async def list_tools(self) -> List[AIFunction]:
        server_context = AgentServerContext.get()
        foundry_tool_catalog = server_context.tools.catalog
        resolved_tools = await foundry_tool_catalog.list(self._allowed_tools)
        return [self._to_aifunction(tool) for tool in resolved_tools]
    
    def _to_aifunction(self, foundry_tool: "ResolvedFoundryTool") -> AIFunction:
        """Convert an FoundryTool to an Agent Framework AI Function

        :param foundry_tool: The FoundryTool to convert.
        :type foundry_tool: ~azure.ai.agentserver.core.client.tools.aio.FoundryTool
        :return: An AI Function Tool.
        :rtype: AIFunction
        """
        # Get the input schema from the tool descriptor
        input_schema = foundry_tool.input_schema or {}

        # Create a Pydantic model from the input schema
        properties = input_schema.properties or {}
        required_fields = set(input_schema.required or [])

        # Build field definitions for the Pydantic model
        field_definitions: Dict[str, Any] = {}
        for field_name, field_info in properties.items():
            field_type = self._json_schema_type_to_python(field_info.type or "string")
            field_description = field_info.description or ""
            is_required = field_name in required_fields

            if is_required:
                field_definitions[field_name] = (field_type, Field(description=field_description))
            else:
                field_definitions[field_name] = (Optional[field_type],
                                                 Field(default=None, description=field_description))

        # Create the Pydantic model dynamically
        input_model = create_model(
            f"{foundry_tool.name}_input",
            **field_definitions
        )

        # Create a wrapper function that calls the Azure tool
        async def tool_func(**kwargs: Any) -> Any:
            """Dynamically generated function to invoke the Azure AI tool.

            :return: The result from the tool invocation.
            :rtype: Any
            """
            server_context = AgentServerContext.get()
            invoker = await server_context.tools.invocation.resolve(foundry_tool)

            logger.debug("Invoking tool: %s with input: %s", foundry_tool.name, kwargs)
            return await invoker.invoke(kwargs)
        _attach_signature_from_pydantic_model(tool_func, input_model)

        # Create and return the AIFunction
        return AIFunction(
            name=foundry_tool.name,
            description=foundry_tool.description or "No description available",
            func=tool_func,
            input_model=input_model
        )

    def _json_schema_type_to_python(self, json_type: str) -> type:
        """Convert JSON schema type to Python type.

        :param json_type: The JSON schema type string.
        :type json_type: str
        :return: The corresponding Python type.
        :rtype: type
        """
        type_map = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        return type_map.get(json_type, str)


class ChatClientWithFoundryTools(BaseChatClient):
    """Wrap a BaseChatClient and inject Foundry tools into ChatOptions on each call.

    Callers only provide:
    - `inner`: the BaseChatClient to delegate to
    - `tools`: a list of FoundryToolLike descriptors (facades or FoundryTool objects)
    """

    def __init__(
            self,
            *,
            inner: BaseChatClient, 
            tools: Sequence[FoundryToolLike]) -> None:
        if not isinstance(inner, BaseChatClient):
            raise TypeError(
                "inner must be an instance of agent_framework.BaseChatClient"
            )

        super().__init__(middleware=getattr(inner, "middleware", None))

        self._inner = inner
        self._tools: List[FoundryToolLike] = list(tools)

        self._foundry_tool_client = FoundryToolClient(tools=self._tools)

    async def _inject_chat_options(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        tools = await self._foundry_tool_client.list_tools()
        base: Optional[ChatOptions] = kwargs.pop("chat_options", None)
        kwargs["chat_options"] = (base or ChatOptions()) & ChatOptions(tools=tools)
        return kwargs

    async def get_response(self, messages: Any, **kwargs: Any) -> Any:
        kwargs = await self._inject_chat_options(kwargs)
        return await self._inner.get_response(messages=messages, **kwargs)

    async def get_streaming_response(self, messages: Any, **kwargs: Any) -> AsyncIterable[Any]:
        kwargs = await self._inject_chat_options(kwargs)
        async for update in self._inner.get_streaming_response(messages=messages, **kwargs):
            yield update

    async def _inner_get_response(self, *, messages: Any, chat_options: ChatOptions, **kwargs: Any) -> Any:
        return await self._inner._inner_get_response(messages=messages, chat_options=chat_options, **kwargs)

    async def _inner_get_streaming_response(
        self, *, messages: Any, chat_options: ChatOptions, **kwargs: Any
    ) -> AsyncIterable[Any]:
        async for update in self._inner._inner_get_streaming_response(
            messages=messages, chat_options=chat_options, **kwargs
        ):
            yield update

    def create_agent(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        instructions: str | None = None,
        chat_message_store_factory: Callable[[], Any] | None = None,
        context_providers: Any = None,
        middleware: Any = None,
        allow_multiple_tool_calls: bool | None = None,
        conversation_id: str | None = None,
        frequency_penalty: float | None = None,
        logit_bias: dict[str | int, float] | None = None,
        max_tokens: int | None = None,
        metadata: dict[str, Any] | None = None,
        model_id: str | None = None,
        presence_penalty: float | None = None,
        response_format: type[BaseModel] | None = None,
        seed: int | None = None,
        stop: str | Sequence[str] | None = None,
        store: bool | None = None,
        temperature: float | None = None,
        tool_choice: Any = "auto",
        tools: Any = None,
        top_p: float | None = None,
        user: str | None = None,
        additional_chat_options: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Create a ChatAgent and inject Foundry tools via a context provider.

        This allows `ChatClientWithFoundryTools.create_agent(...)` to behave like a normal
        chat client factory while ensuring the resulting ChatAgent has access to Foundry tools.
        """

        foundry_provider = FoundryToolsContextProvider(tools=self._tools)

        # Merge/append provider without mutating caller-owned provider objects.
        merged_providers: Any
        if context_providers is None:
            merged_providers = [foundry_provider]
        else:
            providers = context_providers if isinstance(context_providers, list) else [context_providers]

            if any(isinstance(p, FoundryToolsContextProvider) for p in providers):
                raise ValueError(
                    "Do not pass FoundryToolsContextProvider explicitly when using ChatClientWithFoundryTools. "
                    "It is injected automatically."
                )

            merged_providers = [*providers, foundry_provider]

        return super().create_agent(
            id=id,
            name=name,
            description=description,
            instructions=instructions,
            chat_message_store_factory=chat_message_store_factory,
            context_providers=merged_providers,
            middleware=middleware,
            allow_multiple_tool_calls=allow_multiple_tool_calls,
            conversation_id=conversation_id,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            max_tokens=max_tokens,
            metadata=metadata,
            model_id=model_id,
            presence_penalty=presence_penalty,
            response_format=response_format,
            seed=seed,
            stop=stop,
            store=store,
            temperature=temperature,
            tool_choice=tool_choice,
            tools=tools,
            top_p=top_p,
            user=user,
            additional_chat_options=additional_chat_options,
            **kwargs,
        )

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class FoundryToolsContextProvider(ContextProvider):
    """ContextProvider that injects Foundry tools as Agent Framework tools.

    This provider resolves the configured Foundry tools into Agent Framework `AIFunction`s
    and returns them via `Context.tools` so `ChatAgent` can merge them into the request.

    By default, it caches the resolved tool list for the lifetime of the provider.
    """

    def __init__(self, *, tools: Sequence[FoundryToolLike]) -> None:
        self._foundry_tool_client = FoundryToolClient(tools=tools)

    async def invoking(self, messages: Any, **kwargs: Any) -> Context:
        tools = await self._foundry_tool_client.list_tools()
        return Context(tools=tools)
