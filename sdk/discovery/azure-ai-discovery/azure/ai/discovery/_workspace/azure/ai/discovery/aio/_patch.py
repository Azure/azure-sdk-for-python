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

    :ivar investigations: InvestigationsOperations operations
    :vartype investigations: azure.ai.discovery.aio.operations.InvestigationsOperations
    :ivar conversations: ConversationsOperations operations
    :vartype conversations: azure.ai.discovery.aio.operations.ConversationsOperations
    :ivar tools: ToolsOperations operations
    :vartype tools: azure.ai.discovery.aio.operations.ToolsOperations
    :ivar tasks: TasksOperations operations
    :vartype tasks: azure.ai.discovery.aio.operations.TasksOperations
    """

    def __init__(
        self,
        endpoint: str,
        credential: "AsyncTokenCredential",
        *,
        api_version: Optional[str] = None,
        transport: Optional["AsyncHttpTransport"] = None,
        **kwargs: Any,
    ) -> None:
        """Create a new asynchronous ``WorkspaceClient``.

        :param endpoint: The Discovery service endpoint, in the form
            ``https://<your-resource-name>.services.ai.azure.com``. Required.
        :type endpoint: str
        :param credential: Credential used to authenticate requests to the service.
            Required.
        :type credential: ~azure.core.credentials_async.AsyncTokenCredential
        :keyword api_version: The API version to use for the request. Default value
            is the latest service version supported by this client. Note that
            overriding this default value may result in unsupported behavior.
        :paramtype api_version: str
        :keyword transport: The async HTTP transport to use. If not specified, the
            default ``azure-core`` async transport (``AioHttpTransport``) is used.
        :paramtype transport: ~azure.core.pipeline.transport.AsyncHttpTransport
        """
        if api_version is not None:
            kwargs["api_version"] = api_version
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
