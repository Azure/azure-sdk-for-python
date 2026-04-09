# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Public API surface for the Azure AI Agent Server Responses package.

Core types for building response handlers::

    from azure.ai.agentserver.responses import (
        ResponsesAgentServerHost,
        ResponseContext,
        ResponseEventStream,
        TextResponse,
        CreateResponse,
    )

Builder types for advanced event construction are available from the
``streaming`` subpackage::

    from azure.ai.agentserver.responses.streaming import (
        OutputItemMessageBuilder,
        OutputItemFunctionCallBuilder,
        ...
    )
"""

from ._version import VERSION

__version__ = VERSION

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

# Builder types are available from azure.ai.agentserver.responses.streaming
# for advanced use cases. They are not re-exported here to keep the root
# namespace focused on the most commonly used types.

__all__ = [
    # Core
    "__version__",
    "ResponsesAgentServerHost",
    "ResponseContext",
    "IsolationContext",
    "ResponsesServerOptions",
    # Event stream
    "ResponseEventStream",
    "TextResponse",
    # Models
    "CreateResponse",
    "ResponseObject",
    # Helpers
    "get_conversation_id",
    "get_input_expanded",
    "to_output_item",
    # Storage
    "ResponseProviderProtocol",
    "ResponseStreamProviderProtocol",
    "InMemoryResponseProvider",
    "FoundryStorageProvider",
    "FoundryStorageSettings",
    "FoundryStorageError",
    "FoundryResourceNotFoundError",
    "FoundryBadRequestError",
    "FoundryApiError",
]
