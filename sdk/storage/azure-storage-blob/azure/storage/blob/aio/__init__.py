# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os

from .._shared.policies_async import ExponentialRetry, LinearRetry, NoRetry
from .._shared.models import(
    LocationMode,
    ResourceTypes,
    AccountSasPermissions,
    StorageErrorCode
)
from ..models import (
    BlobType,
    BlockState,
    StandardBlobTier,
    PremiumPageBlobTier,
    SequenceNumberAction,
    PublicAccess,
    Logging,
    Metrics,
    RetentionPolicy,
    StaticWebsite,
    CorsRule,
    ContainerProperties,
    BlobProperties,
    LeaseProperties,
    ContentSettings,
    CopyProperties,
    BlobBlock,
    PageRange,
    AccessPolicy,
    ContainerSasPermissions,
    BlobSasPermissions,
)
from .models import (
    ContainerPropertiesPaged,
    BlobPropertiesPaged,
    BlobPrefix
)
from .download_async import StorageStreamDownloader
from .blob_client_async import BlobClient
from .container_client_async import ContainerClient
from .blob_service_client_async import BlobServiceClient
from .lease_async import LeaseClient


__all__ = [
    'BlobServiceClient',
    'ContainerClient',
    'BlobClient',
    'BlobType',
    'LeaseClient',
    'StorageErrorCode',
    'ExponentialRetry',
    'LinearRetry',
    'NoRetry',
    'LocationMode',
    'BlockState',
    'StandardBlobTier',
    'PremiumPageBlobTier',
    'SequenceNumberAction',
    'PublicAccess',
    'Logging',
    'Metrics',
    'RetentionPolicy',
    'StaticWebsite',
    'CorsRule',
    'ContainerProperties',
    'ContainerPropertiesPaged',
    'BlobProperties',
    'BlobPropertiesPaged',
    'BlobPrefix',
    'LeaseProperties',
    'ContentSettings',
    'CopyProperties',
    'BlobBlock',
    'PageRange',
    'AccessPolicy',
    'ContainerSasPermissions',
    'BlobSasPermissions',
    'ResourceTypes',
    'AccountSasPermissions',
    'StorageStreamDownloader',
]


async def upload_blob_to_url(
        blob_url,  # type: str
        data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
        credential=None,  # type: Any
        **kwargs):
    # type: (...) -> dict[str, Any]
    """Upload data to a given URL

    The data will be uploaded as a block blob.

    :param str blob_url:
        The full URI to the blob. This can also include a SAS token.
    :param data:
        The data to upload. This can be bytes, text, an iterable or a file-like object.
    :type data: bytes or str or Iterable
    :param bool overwrite:
        Whether the blob to be uploaded should overwrite the current data.
        If True, upload_blob_to_url will overwrite any existing data. If set to False, the
        operation will fail with a ResourceExistsError.
    :param int max_concurrency:
        The number of parallel connections with which to download.
    :param credential:
        The credentials with which to authenticate. This is optional if the
        blob URL already has a SAS token. The value can be a SAS token string, an account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the URL already has a SAS token, specifying an explicit credential will take priority.
    :returns: Blob-updated property dict (Etag and last modified)
    :rtype: dict(str, Any)
    """
    async with BlobClient.from_blob_url(blob_url, credential=credential) as client:
        return await client.upload_blob(data=data, blob_type=BlobType.BlockBlob, **kwargs)


async def _download_to_stream(client, handle, **kwargs):
    """Download data to specified open file-handle."""
    stream = await client.download_blob(**kwargs)
    await stream.readinto(handle)


async def download_blob_from_url(
        blob_url,  # type: str
        output,  # type: str
        overwrite=False,  # type: bool
        credential=None,  # type: Any
        **kwargs):
    # type: (...) -> None
    """Download the contents of a blob to a local file or stream.

    :param str blob_url:
        The full URI to the blob. This can also include a SAS token.
    :param output:
        Where the data should be downloaded to. This could be either a file path to write to,
        or an open IO handle to write to.
    :type output: str or writable stream.
    :param bool overwrite:
        Whether the local file should be overwritten if it already exists. The default value is
        `False` - in which case a ValueError will be raised if the file already exists. If set to
        `True`, an attempt will be made to write to the existing file. If a stream handle is passed
        in, this value is ignored.
    :param credential:
        The credentials with which to authenticate. This is optional if the
        blob URL already has a SAS token or the blob is public. The value can be a SAS token string,
        an account shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the URL already has a SAS token, specifying an explicit credential will take priority.
    :param int max_concurrency:
        The number of parallel connections with which to download.
    :rtype: None
    """
    async with BlobClient.from_blob_url(blob_url, credential=credential) as client:
        if hasattr(output, 'write'):
            await _download_to_stream(client, output, **kwargs)
        else:
            if not overwrite and os.path.isfile(output):
                raise ValueError("The file '{}' already exists.".format(output))
            with open(output, 'wb') as file_handle:
                await _download_to_stream(client, file_handle, **kwargs)
