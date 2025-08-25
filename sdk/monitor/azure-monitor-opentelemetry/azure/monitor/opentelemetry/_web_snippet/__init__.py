
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

from ._snippet_injector import WebSnippetInjector
from ._config import WebSnippetConfig

# Import middleware but don't export it - it will be auto-patched
from ._django_middleware import DjangoWebSnippetMiddleware

__all__ = [
    "WebSnippetInjector",
    "WebSnippetConfig",
]
