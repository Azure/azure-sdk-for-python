# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union, overload

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field, create_model

from azure.ai.agentserver.core import AgentServerContext
from azure.ai.agentserver.core.tools import FoundryToolLike, ResolvedFoundryTool, SchemaDefinition, ensure_foundry_tool
from azure.ai.agentserver.core.tools.utils import ToolNameResolver


class ResolvedTools(Iterable[BaseTool]):
    """A resolved view of foundry tools into LangChain tools.

    :param tools: An iterable of tuples of resolved foundry tools and their corresponding LangChain tools.
    :type tools: Iterable[Tuple[ResolvedFoundryTool, BaseTool]]
    """
    def __init__(self, tools: Iterable[Tuple[ResolvedFoundryTool, BaseTool]]):
        self._by_source_id: Dict[str, List[BaseTool]] = defaultdict(list)
        for rt, t in tools:
            self._by_source_id[rt.definition.id].append(t)

    @overload
    def get(self, tool: FoundryToolLike, /) -> Iterable[BaseTool]:  # pylint: disable=C4743
        """Get the LangChain tools for the given foundry tool.

        :param tool: The foundry tool to get the LangChain tools for.
        :type tool: FoundryToolLike
        :return: The list of LangChain tools for the given foundry tool.
        :rtype: Iterable[BaseTool]
        """
        ...

    @overload
    def get(self, tools: Iterable[FoundryToolLike], /) -> Iterable[BaseTool]:  # pylint: disable=C4743
        """Get the LangChain tools for the given foundry tools.

        :param tools: The foundry tools to get the LangChain tools for.
        :type tools: Iterable[FoundryToolLike]
        :return: The list of LangChain tools for the given foundry tools.
        :rtype: Iterable[BaseTool]
        """
        ...

    @overload
    def get(self) -> Iterable[BaseTool]:
        """Get all LangChain tools.

        :return: The list of all LangChain tools.
        :rtype: Iterable[BaseTool]
        """
        ...

    def get(self, tool: Union[FoundryToolLike, Iterable[FoundryToolLike], None] = None) -> Iterable[BaseTool]:
        """Get the LangChain tools for the given foundry tool(s), or all tools if none is given.

        :param tool: The foundry tool or tools to get the LangChain tools for, or None to get all tools.
        :type tool: Union[FoundryToolLike, Iterable[FoundryToolLike], None]
        :return: The list of LangChain tools for the given foundry tool(s), or all tools if none is given.
        :rtype: Iterable[BaseTool]
        """
        if tool is None:
            yield from self
            return

        tool_list = [tool] if not isinstance(tool, Iterable) else tool  # type: ignore[assignment]
        for t in tool_list:
            ft = ensure_foundry_tool(t)  # type: ignore[arg-type]
            yield from self._by_source_id.get(ft.id, [])

    def __iter__(self):
        for tool_list in self._by_source_id.values():
            yield from tool_list


class FoundryLangChainToolResolver:
    """Resolves foundry tools into LangChain tools.

    :param name_resolver: The tool name resolver.
    :type name_resolver: Optional[ToolNameResolver]
    """
    def __init__(self, name_resolver: Optional[ToolNameResolver] = None):
        self._name_resolver = name_resolver or ToolNameResolver()

    async def resolve_from_registry(self) -> ResolvedTools:
        """Resolve the foundry tools from the global registry into LangChain tools.

        :return: The resolved LangChain tools.
        :rtype: Iterable[Tuple[ResolvedFoundryTool, BaseTool]]
        """
        return await self.resolve(get_registry())

    async def resolve(self, foundry_tools: List[FoundryToolLike]) -> ResolvedTools:
        """Resolve the given foundry tools into LangChain tools.

        :param foundry_tools: The foundry tools to resolve.
        :type foundry_tools: List[FoundryToolLike]
        :return: The resolved LangChain tools.
        :rtype: Iterable[Tuple[ResolvedFoundryTool, BaseTool]]
        """
        context = AgentServerContext.get()
        resolved_foundry_tools = await context.tools.catalog.list(foundry_tools)
        return ResolvedTools(tools=((tool, self._create_structured_tool(tool)) for tool in resolved_foundry_tools))

    def _create_structured_tool(self, resolved_tool: ResolvedFoundryTool) -> StructuredTool:
        name = self._name_resolver.resolve(resolved_tool)
        args_schema = self._create_pydantic_model(name, resolved_tool.input_schema)

        async def _tool_func(**kwargs: Any) -> str:
            result = await AgentServerContext.get().tools.invoke(resolved_tool, kwargs)
            if isinstance(result, dict):
                import json
                return json.dumps(result)
            return str(result)

        return StructuredTool.from_function(
            name=name,
            description=resolved_tool.details.description,
            coroutine=_tool_func,
            args_schema=args_schema
        )

    @classmethod
    def _create_pydantic_model(cls, tool_name: str, input_schema: SchemaDefinition) -> type[BaseModel]:
        field_definitions: Dict[str, Any] = {}
        required_fields = input_schema.required or set()
        for prop_name, prop in input_schema.properties.items():
            py_type = prop.type.py_type
            default = ... if prop_name in required_fields else None
            field_definitions[prop_name] = (py_type, Field(default, description=prop.description))

        model_name = f"{tool_name.replace('-', '_').replace(' ', '_').title()}-Input"
        return create_model(model_name, **field_definitions)  # type: ignore[call-overload]


_tool_registry: List[FoundryToolLike] = []


def get_registry() -> List[FoundryToolLike]:
    """Get the global foundry tool registry.

    :return: The list of registered foundry tools.
    :rtype: List[FoundryToolLike]
    """
    return _tool_registry
