# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, TYPE_CHECKING

from ._client import (
    ServiceClient,
    ContainerClient,
    BlobClient,
    PageBlobClient,
    AppendBlobClient,
    BlockBlobClient,
)

from ._utils.serialization import Serializer

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class AzureBlobStorage:
    """Combined client that exposes all blob storage operations as attributes.

    This class wraps the individual operation mixins and exposes them as attributes
    to maintain backward compatibility with the previous autorest-generated client structure.

    :param url: The host name of the blob storage account.
    :type url: str
    :param credential: Credential used to authenticate requests to the service.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword version: Specifies the version of the operation to use for this request.
    :paramtype version: str
    """

    def __init__(
        self,
        url: str,
        credential: "AsyncTokenCredential",
        **kwargs: Any
    ) -> None:
        self._serialize = Serializer()
        self.service = ServiceClient(url, credential, **kwargs)
        self.container = ContainerClient(url, credential, **kwargs)
        self.blob = BlobClient(url, credential, **kwargs)
        self.page_blob = PageBlobClient(url, credential, **kwargs)
        self.append_blob = AppendBlobClient(url, credential, **kwargs)
        self.block_blob = BlockBlobClient(url, credential, **kwargs)

    async def close(self) -> None:
        await self.service.close()
        await self.container.close()
        await self.blob.close()
        await self.page_blob.close()
        await self.append_blob.close()
        await self.block_blob.close()

    async def __aenter__(self) -> "AzureBlobStorage":
        await self.service.__aenter__()
        await self.container.__aenter__()
        await self.blob.__aenter__()
        await self.page_blob.__aenter__()
        await self.append_blob.__aenter__()
        await self.block_blob.__aenter__()
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        await self.service.__aexit__(*exc_details)
        await self.container.__aexit__(*exc_details)
        await self.blob.__aexit__(*exc_details)
        await self.page_blob.__aexit__(*exc_details)
        await self.append_blob.__aexit__(*exc_details)
        await self.block_blob.__aexit__(*exc_details)


__all__: list[str] = ["AzureBlobStorage"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
