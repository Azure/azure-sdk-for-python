# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Optional, TYPE_CHECKING

from ._client import BookshelfClient as _GeneratedBookshelfClient
from ._client import WorkspaceClient as _GeneratedWorkspaceClient

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import HttpTransport


class WorkspaceClient(_GeneratedWorkspaceClient):
    """WorkspaceClient with an explicit ``transport`` keyword-only argument.

    See https://azure.github.io/azure-sdk/python_design.html#python-client-constructor-transport-argument

    :keyword api_version: The API version to use for this operation. Known values are "2026-06-01".
     Overriding the default may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: "TokenCredential",
        *,
        api_version: Optional[str] = None,
        transport: Optional["HttpTransport"] = None,
        **kwargs: Any,
    ) -> None:
        if api_version is not None:
            kwargs["api_version"] = api_version
        if transport is not None:
            kwargs["transport"] = transport
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)


class BookshelfClient(_GeneratedBookshelfClient):
    """BookshelfClient with an explicit ``transport`` keyword-only argument.

    See https://azure.github.io/azure-sdk/python_design.html#python-client-constructor-transport-argument

    :keyword api_version: The API version to use for this operation. Known values are "2026-06-01".
     Overriding the default may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: "TokenCredential",
        *,
        api_version: Optional[str] = None,
        transport: Optional["HttpTransport"] = None,
        **kwargs: Any,
    ) -> None:
        if api_version is not None:
            kwargs["api_version"] = api_version
        if transport is not None:
            kwargs["transport"] = transport
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)


__all__: list[str] = ["WorkspaceClient", "BookshelfClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
