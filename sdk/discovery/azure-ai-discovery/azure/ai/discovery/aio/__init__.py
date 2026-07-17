# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""Async clients for Azure AI Discovery.

This module mirrors the top-level :mod:`azure.ai.discovery` package and exposes the
asynchronous variants of both ``WorkspaceClient`` and ``BookshelfClient`` from a
single import location::

    from azure.ai.discovery.aio import WorkspaceClient, BookshelfClient
"""

from .._workspace.azure.ai.discovery.aio import WorkspaceClient  # type: ignore
from .._bookshelf.azure.ai.discovery.aio import BookshelfClient  # type: ignore

__all__ = [
    "BookshelfClient",
    "WorkspaceClient",
]
