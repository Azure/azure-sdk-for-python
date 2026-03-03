# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=client-accepts-api-version-keyword,missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
# pylint: disable=no-name-in-module,import-error
from __future__ import annotations

import inspect
from typing import Any, Dict, List, Optional, Sequence

from agent_framework import AgentSession, BaseContextProvider, FunctionTool, SessionContext, SupportsAgentRun
from pydantic import Field, create_model

from azure.ai.agentserver.core import AgentServerContext
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.tools import FoundryToolLike, ResolvedFoundryTool, ensure_foundry_tool

logger = get_logger()


def _attach_signature_from_pydantic_model(func, input_model) -> None:
    params = []
    annotations: Dict[str, Any] = {}

    for name, field in input_model.model_fields.items():
        ann = field.annotation or Any
        annotations[name] = ann

        default = inspect._empty if field.is_required() else field.default  # pylint: disable=protected-access
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
        self._allowed_tools: List[FoundryToolLike] = [ensure_foundry_tool(tool) for tool in tools]

    async def list_tools(self) -> List[FunctionTool]:
        server_context = AgentServerContext.get()
        foundry_tool_catalog = server_context.tools.catalog
        resolved_tools = await foundry_tool_catalog.list(self._allowed_tools)
        return [self._to_aifunction(tool) for tool in resolved_tools]

    def _to_aifunction(self, foundry_tool: "ResolvedFoundryTool") -> FunctionTool:
        """Convert an FoundryTool to an Agent Framework Function Tool

        :param foundry_tool: The FoundryTool to convert.
        :type foundry_tool: ~azure.ai.agentserver.core.client.tools.aio.FoundryTool
        :return: A Function Tool.
        :rtype: FunctionTool
        """
        # Get the input schema from the tool descriptor
        input_schema = foundry_tool.input_schema or {}

        # Create a Pydantic model from the input schema
        properties = input_schema.properties or {}
        required_fields = set(input_schema.required or [])

        # Build field definitions for the Pydantic model
        field_definitions: Dict[str, Any] = {}
        for field_name, field_info in properties.items():
            if field_info.type is None:
                logger.warning("Skipping field '%s' in tool '%s': unknown or empty schema type.",
                               field_name, foundry_tool.name)
                continue
            field_type = field_info.type.py_type
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
            logger.debug("Invoking tool: %s with input: %s", foundry_tool.name, kwargs)
            return await server_context.tools.invoke(foundry_tool, kwargs)
        _attach_signature_from_pydantic_model(tool_func, input_model)

        # Create and return the FunctionTool
        return FunctionTool(
            name=foundry_tool.name,
            description=foundry_tool.description or "No description available",
            func=tool_func,
            input_model=input_model
        )


class FoundryToolsContextProvider(BaseContextProvider):
    """Context provider to inject Foundry tools into an agent run."""

    DEFAULT_SOURCE_ID = "foundry_tools"

    def __init__(
        self,
        tools: Sequence[FoundryToolLike],
        *,
        source_id: Optional[str] = None,
    ) -> None:
        super().__init__(source_id or self.DEFAULT_SOURCE_ID)
        self._foundry_tool_client = FoundryToolClient(tools=tools)

    async def before_run(
        self,
        *,
        agent: SupportsAgentRun,
        session: AgentSession,
        context: SessionContext,
        state: Dict[str, Any],
    ) -> None:
        tools = await self._foundry_tool_client.list_tools()
        if tools:
            context.extend_tools(self.source_id, tools)
