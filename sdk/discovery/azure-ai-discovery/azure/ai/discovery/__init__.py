# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""Azure AI Discovery client library for Python.

This package exposes both the WorkspaceClient and BookshelfClient from a single
unified ``azure-ai-discovery`` package.
"""

from ._workspace import WorkspaceClient  # type: ignore
from ._bookshelf import BookshelfClient  # type: ignore
from ._version import VERSION

__version__ = VERSION

__all__ = [
    "BookshelfClient",
    "WorkspaceClient",
]
