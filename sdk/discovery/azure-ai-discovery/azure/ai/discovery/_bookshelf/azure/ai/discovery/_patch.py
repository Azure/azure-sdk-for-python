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

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import HttpTransport


class BookshelfClient(_GeneratedBookshelfClient):
    """BookshelfClient with explicit ``transport`` keyword-only argument.

    See https://azure.github.io/azure-sdk/python_design.html#python-client-constructor-transport-argument

    :ivar knowledge_bases: KnowledgeBasesOperations operations
    :vartype knowledge_bases: azure.ai.discovery.operations.KnowledgeBasesOperations
    :ivar knowledge_base_versions: KnowledgeBaseVersionsOperations operations
    :vartype knowledge_base_versions: azure.ai.discovery.operations.KnowledgeBaseVersionsOperations
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
        """Create a new ``BookshelfClient``.

        :param endpoint: The Discovery service endpoint, in the form
            ``https://<your-resource-name>.services.ai.azure.com``. Required.
        :type endpoint: str
        :param credential: Credential used to authenticate requests to the service.
            Required.
        :type credential: ~azure.core.credentials.TokenCredential
        :keyword api_version: The API version to use for the request. Default value
            is the latest service version supported by this client. Note that
            overriding this default value may result in unsupported behavior.
        :paramtype api_version: str
        :keyword transport: The HTTP transport to use. If not specified, the default
            ``azure-core`` transport (``RequestsTransport``) is used.
        :paramtype transport: ~azure.core.pipeline.transport.HttpTransport
        """
        if api_version is not None:
            kwargs["api_version"] = api_version
        if transport is not None:
            kwargs["transport"] = transport
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)


__all__: list[str] = ["BookshelfClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
