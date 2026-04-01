# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Public API surface for the Azure AI Agent Server Responses package."""

from ._version import VERSION

__version__ = VERSION

from .streaming._builders import (
    OutputItemCodeInterpreterCallBuilder,
    OutputItemBuilder,
    OutputItemCustomToolCallBuilder,
    OutputItemFileSearchCallBuilder,
    OutputItemFunctionCallBuilder,
    OutputItemFunctionCallOutputBuilder,
    OutputItemImageGenCallBuilder,
    OutputItemMcpCallBuilder,
    OutputItemMcpListToolsBuilder,
    OutputItemMessageBuilder,
    OutputItemReasoningItemBuilder,
    OutputItemWebSearchCallBuilder,
    ReasoningSummaryPartBuilder,
    RefusalContentBuilder,
    TextContentBuilder,
)
from .streaming._event_stream import ResponseEventStream
from ._response_context import ResponseContext
from ._options import ResponsesServerOptions
from .store._base import ResponseProviderProtocol, ResponseStreamProviderProtocol
from .store._foundry_errors import FoundryApiError, FoundryBadRequestError, FoundryResourceNotFoundError, FoundryStorageError
from .store._foundry_provider import FoundryStorageProvider
from .store._foundry_settings import FoundryStorageSettings
from .store._memory import InMemoryResponseProvider
from .models import (
    CreateResponse,
    ResponseObject
)
from .models._helpers import (
    get_conversation_id,
    get_input_expanded,
    get_input_text,
)

__all__ = [
    "__version__",
    "ResponseContext",
    "ResponsesServerOptions",
    "ResponseProviderProtocol",
    "ResponseStreamProviderProtocol",
    "InMemoryResponseProvider",
    "FoundryStorageProvider",
    "FoundryStorageSettings",
    "FoundryStorageError",
    "FoundryResourceNotFoundError",
    "FoundryBadRequestError",
    "FoundryApiError",
    "TextContentBuilder",
    "OutputItemMessageBuilder",
    "OutputItemBuilder",
    "OutputItemFunctionCallBuilder",
    "OutputItemFunctionCallOutputBuilder",
    "RefusalContentBuilder",
    "OutputItemReasoningItemBuilder",
    "ReasoningSummaryPartBuilder",
    "OutputItemFileSearchCallBuilder",
    "OutputItemWebSearchCallBuilder",
    "OutputItemCodeInterpreterCallBuilder",
    "OutputItemImageGenCallBuilder",
    "OutputItemMcpCallBuilder",
    "OutputItemMcpListToolsBuilder",
    "OutputItemCustomToolCallBuilder",
    "ResponseEventStream",
    "CreateResponse",
    "ResponseObject",
    "get_conversation_id",
    "get_input_expanded",
    "get_input_text",
]
