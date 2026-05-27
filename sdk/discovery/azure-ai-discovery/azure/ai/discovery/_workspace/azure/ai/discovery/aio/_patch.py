# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional, TYPE_CHECKING

from ._client import WorkspaceClient as _GeneratedWorkspaceClient

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.pipeline.transport import AsyncHttpTransport


class WorkspaceClient(_GeneratedWorkspaceClient):
    """Async WorkspaceClient with explicit ``transport`` keyword-only argument.

    See https://azure.github.io/azure-sdk/python_design.html#python-client-constructor-transport-argument
    """

    def __init__(
        self,
        endpoint: str,
        credential: "AsyncTokenCredential",
        *,
        transport: Optional["AsyncHttpTransport"] = None,
        **kwargs: Any,
    ) -> None:
        if transport is not None:
            kwargs["transport"] = transport
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)


__all__: list[str] = ["WorkspaceClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
