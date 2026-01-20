# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

from .client._client import FoundryToolClient
from ._exceptions import (
    ToolInvocationError,
    OAuthConsentRequiredError,
    UnableToResolveToolInvocationError,
    InvalidToolFacadeError,
)
from .client._models import (
    FoundryConnectedTool,
    FoundryHostedMcpTool,
    FoundryTool,
    FoundryToolProtocol,
    FoundryToolSource,
    ResolvedFoundryTool,
    SchemaDefinition,
    SchemaProperty,
    SchemaType,
    UserInfo,
)
from .runtime._catalog import (
    FoundryToolCatalog,
    CachedFoundryToolCatalog,
    DefaultFoundryToolCatalog,
)
from .runtime._facade import FoundryToolFacade, FoundryToolLike, ensure_foundry_tool
from .runtime._invoker import FoundryToolInvoker, DefaultFoundryToolInvoker
from .runtime._resolver import FoundryToolInvocationResolver, DefaultFoundryToolInvocationResolver
from .runtime._runtime import FoundryToolRuntime, DefaultFoundryToolRuntime
from .runtime._starlette import UserInfoContextMiddleware
from .runtime._user import UserProvider, ContextVarUserProvider

__all__ = [
    # Client
    "FoundryToolClient",
    # Exceptions
    "ToolInvocationError",
    "OAuthConsentRequiredError",
    "UnableToResolveToolInvocationError",
    "InvalidToolFacadeError",
    # Models
    "FoundryConnectedTool",
    "FoundryHostedMcpTool",
    "FoundryTool",
    "FoundryToolProtocol",
    "FoundryToolSource",
    "ResolvedFoundryTool",
    "SchemaDefinition",
    "SchemaProperty",
    "SchemaType",
    "UserInfo",
    # Catalog
    "FoundryToolCatalog",
    "CachedFoundryToolCatalog",
    "DefaultFoundryToolCatalog",
    # Facade
    "FoundryToolFacade",
    "FoundryToolLike",
    "ensure_foundry_tool",
    # Invoker
    "FoundryToolInvoker",
    "DefaultFoundryToolInvoker",
    # Resolver
    "FoundryToolInvocationResolver",
    "DefaultFoundryToolInvocationResolver",
    # Runtime
    "FoundryToolRuntime",
    "DefaultFoundryToolRuntime",
    # Starlette
    "UserInfoContextMiddleware",
    # User
    "UserProvider",
    "ContextVarUserProvider",
]
