# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import sys, logging
from io import IOBase
from typing import Any, Dict, List, overload, IO, Union, Optional, TYPE_CHECKING
from azure.core.tracing.decorator import distributed_trace

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    import _types

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()
_LOGGER = logging.getLogger(__name__)

from ._operations import AssistantsClientOperationsMixin as AssistantsClientOperationsMixinGenerated
from .. import models as _models


class AssistantsClientOperationsMixin(AssistantsClientOperationsMixinGenerated):

    @overload
    def create_assistant(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Assistant:
        ...

    @overload
    def create_assistant(
        self,
        *,
        model: str,
        content_type: str = "application/json",
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        tool_resources: Optional[_models.ToolResources] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> _models.Assistant:
        ...

    @overload
    def create_assistant(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Assistant:
        ...

    @overload
    def create_assistant(
        self,
        model: str = _Unset,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        toolset: Optional[_models.ToolSet] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> _models.Assistant:
        ...

    @distributed_trace
    def create_assistant(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        model: str = _Unset,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[_models.ToolDefinition]] = None,
        tool_resources: Optional[_models.ToolResources] = None,
        toolset: Optional[_models.ToolSet] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        response_format: Optional["_types.AssistantsApiResponseFormatOption"] = None,
        metadata: Optional[Dict[str, str]] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models.Assistant:
        """
        Creates a new assistant with various configurations, delegating to the generated operations.

        :param body: JSON or IO[bytes]. Required if `model` is not provided.
        :param model: The ID of the model to use. Required if `body` is not provided.
        :param name: The name of the new assistant.
        :param description: A description for the new assistant.
        :param instructions: System instructions for the assistant.
        :param tools: List of tools definitions for the assistant.
        :param tool_resources: Resources used by the assistant's tools.
        :param toolset: Collection of tools (alternative to `tools` and `tool_resources`).
        :param temperature: Sampling temperature for generating assistant responses.
        :param top_p: Nucleus sampling parameter.
        :param response_format: Response format for tool calls.
        :param metadata: Key/value pairs for storing additional information.
        :param content_type: Content type of the body.
        :param kwargs: Additional parameters.
        :return: An Assistant object.
        :raises: HttpResponseError for HTTP errors.
        """

        if body is not _Unset:
            if isinstance(body, IOBase):
                return super().create_assistant(
                    body=body, content_type=content_type, **kwargs
                )
            return super().create_assistant(body=body, **kwargs)

        if toolset is not None:
            self._toolset = toolset
            tools = toolset.definitions
            tool_resources = toolset.resources

        return super().create_assistant(
            model=model,
            name=name,
            description=description,
            instructions=instructions,
            tools=tools,
            tool_resources=tool_resources,
            temperature=temperature,
            top_p=top_p,
            response_format=response_format,
            metadata=metadata,
            **kwargs
        )

# Define __all__ to specify what is publicly accessible at this package level
__all__: List[str] = ["AssistantsClientOperationsMixin"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
