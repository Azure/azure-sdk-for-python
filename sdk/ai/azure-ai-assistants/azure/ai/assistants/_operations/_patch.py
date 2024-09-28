# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import sys, logging, os
from io import IOBase
from typing import Any, Dict, List, overload, IO, Union, Optional, TYPE_CHECKING
from azure.ai.assistants.models._enums import FilePurpose
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
from .._vendor import FileType


class AssistantsClientOperationsMixin(AssistantsClientOperationsMixinGenerated):

    @overload
    def create_assistant(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Assistant:
        """Creates a new assistant.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Assistant. The Assistant is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises ~azure.core.exceptions.HttpResponseError:
        """

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
        """Creates a new assistant.

        :keyword model: The ID of the model to use. Required.
        :paramtype model: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword name: The name of the new assistant. Default value is None.
        :paramtype name: str
        :keyword description: The description of the new assistant. Default value is None.
        :paramtype description: str
        :keyword instructions: The system instructions for the new assistant to use. Default value is
         None.
        :paramtype instructions: str
        :keyword tools: The collection of tools to enable for the new assistant. Default value is None.
        :paramtype tools: list[~azure.ai.assistants.models.ToolDefinition]
        :keyword tool_resources: A set of resources that are used by the assistant's tools. The
         resources are specific to the type of tool. For example, the ``code_interpreter``
         tool requires a list of file IDs, while the ``file_search`` tool requires a list of vector
         store IDs. Default value is None.
        :paramtype tool_resources: ~azure.ai.assistants.models.ToolResources
        :keyword temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8
         will make the output more random,
         while lower values like 0.2 will make it more focused and deterministic. Default value is
         None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature, called nucleus sampling, where the
         model considers the results of the tokens with top_p probability mass.
         So 0.1 means only the tokens comprising the top 10% probability mass are considered.

         We generally recommend altering this or temperature but not both. Default value is None.
        :paramtype top_p: float
        :keyword response_format: The response format of the tool calls used by this assistant. Is one
         of the following types: str, Union[str, "_models.AssistantsApiResponseFormatMode"],
         AssistantsApiResponseFormat Default value is None.
        :paramtype response_format: str or str or
         ~azure.ai.assistants.models.AssistantsApiResponseFormatMode or
         ~azure.ai.assistants.models.AssistantsApiResponseFormat
        :keyword metadata: A set of up to 16 key/value pairs that can be attached to an object, used
         for storing additional information about that object in a structured format. Keys may be up to
         64 characters in length and values may be up to 512 characters in length. Default value is
         None.
        :paramtype metadata: dict[str, str]
        :return: Assistant. The Assistant is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_assistant(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Assistant:
        """Creates a new assistant.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Assistant. The Assistant is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises ~azure.core.exceptions.HttpResponseError:
        """

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
        """
        Creates a new assistant with toolset.

        :keyword model: The ID of the model to use. Required if `body` is not provided.
        :paramtype model: str
        :keyword name: The name of the new assistant. Default value is None.
        :paramtype name: str
        :keyword description: A description for the new assistant. Default value is None.
        :paramtype description: str
        :keyword instructions: System instructions for the assistant. Default value is None.
        :paramtype instructions: str
        :keyword toolset: Collection of tools (alternative to `tools` and `tool_resources`). Default
         value is None.
        :paramtype toolset: ~azure.ai.assistants.models.ToolSet
        :keyword temperature: Sampling temperature for generating assistant responses. Default value
         is None.
        :paramtype temperature: float
        :keyword top_p: Nucleus sampling parameter. Default value is None.
        :paramtype top_p: float
        :keyword response_format: Response format for tool calls. Default value is None.
        :paramtype response_format: ~azure.ai.assistants.models.AssistantsApiResponseFormatOption
        :keyword metadata: Key/value pairs for storing additional information. Default value is None.
        :paramtype metadata: dict[str, str]
        :return: An Assistant object.
        :rtype: ~azure.ai.assistants.models.Assistant
        :raises: ~azure.core.exceptions.HttpResponseError
        """

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


    @overload
    def upload_file(self, body: JSON, **kwargs: Any) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param body: Required.
        :type body: JSON
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def upload_file(
        self, *, file: FileType, purpose: Union[str, _models.FilePurpose], filename: Optional[str] = None, **kwargs: Any
    ) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :keyword file: Required.
        :paramtype file: ~azure.ai.assistants._vendor.FileType
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str or ~azure.ai.assistants.models.FilePurpose
        :keyword filename: Default value is None.
        :paramtype filename: str
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def upload_file(
        self, file_path: str, *, purpose: str, **kwargs: Any
    ) -> _models.OpenAIFile:
        """Uploads a file for use by other operations.

        :param file_path: Required.
        :type file_path: str
        :keyword purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
         "assistants_output", "batch", "batch_output", and "vision". Required.
        :paramtype purpose: str
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :rtype: ~azure.ai.assistants.models.OpenAIFile
        :raises ~azure.core.exceptions.HttpResponseError:
        """        

    @distributed_trace
    def upload_file(
        self,
        body: Union[JSON, None] = None,
        *,
        file: Union[FileType, None] = None,
        file_path: Optional[str] = None,
        purpose: Optional[Union[str, _models.FilePurpose]] = None,
        filename: Optional[str] = None,
        **kwargs: Any
    ) -> _models.OpenAIFile:
        """
        Uploads a file for use by other operations, delegating to the generated operations.

        :param body: JSON. Required if `file` and `purpose` are not provided.
        :param file: File content. Required if `body` and `purpose` are not provided.
        :param file_path: Path to the file. Required if `body` and `purpose` are not provided.
        :param purpose: Known values are: "fine-tune", "fine-tune-results", "assistants",
            "assistants_output", "batch", "batch_output", and "vision". Required if `body` and `file` are not provided.
        :param filename: The name of the file.
        :param kwargs: Additional parameters.
        :return: OpenAIFile. The OpenAIFile is compatible with MutableMapping
        :raises FileNotFoundError: If the file_path is invalid.
        :raises IOError: If there are issues with reading the file.
        :raises: HttpResponseError for HTTP errors.
        """
        if body is not None:
            return super().upload_file(body=body, **kwargs)
        
        if isinstance(purpose, FilePurpose):
            purpose = purpose.value

        if file is not None and purpose is not None:
            return super().upload_file(file=file, purpose=purpose, filename=filename, **kwargs)

        if file_path is not None and purpose is not None:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"The file path provided does not exist: {file_path}")

            try:
                with open(file_path, 'rb') as f:
                    content = f.read()

                # Determine filename and create correct FileType
                base_filename = filename or os.path.basename(file_path)
                file_content: FileType = (base_filename, content)

                return super().upload_file(file=file_content, purpose=purpose, **kwargs)
            except IOError as e:
                raise IOError(f"Unable to read file: {file_path}. Reason: {str(e)}")

        raise ValueError("Invalid parameters for upload_file. Please provide the necessary arguments.")


# Define __all__ to specify what is publicly accessible at this package level
__all__: List[str] = ["AssistantsClientOperationsMixin"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
