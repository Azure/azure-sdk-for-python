# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Public API surface for the Azure AI Agent Server Responses package."""

from ._version import VERSION

__version__ = VERSION

from . import _data_url as data_url
from ._options import ResponsesServerOptions
from ._response_context import IsolationContext, ResponseContext
from .hosting._routing import ResponsesAgentServerHost
from .models import CreateResponse, ResponseObject
from .models._helpers import (
    get_conversation_id,
    get_input_expanded,
    to_output_item,
)
from .store._base import ResponseProviderProtocol, ResponseStreamProviderProtocol
from .store._foundry_errors import (
    FoundryApiError,
    FoundryBadRequestError,
    FoundryResourceNotFoundError,
    FoundryStorageError,
)
from .store._foundry_provider import FoundryStorageProvider
from .store._foundry_settings import FoundryStorageSettings
from .store._memory import InMemoryResponseProvider
from .streaming._event_stream import ResponseEventStream
from .streaming._text_response import TextResponse

__all__ = [
    "__version__",
    "data_url",  # pylint: disable=naming-mismatch
    "ResponsesAgentServerHost",
    "ResponseContext",
    "IsolationContext",
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
    "ResponseEventStream",
    "TextResponse",
    "CreateResponse",
    "ResponseObject",
    "get_conversation_id",
    "get_input_expanded",
    "to_output_item",
]
