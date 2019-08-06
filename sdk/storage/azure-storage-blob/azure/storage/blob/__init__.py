# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os

from typing import Union, Iterable, AnyStr, IO, Any # pylint: disable=unused-import
from .version import VERSION
from .blob_client import BlobClient
from .container_client import ContainerClient
from .blob_service_client import BlobServiceClient
from .lease import LeaseClient
from ._shared.policies import ExponentialRetry, LinearRetry, NoRetry
from ._shared.downloads import StorageStreamDownloader
from ._shared.models import(
    LocationMode,
    ResourceTypes,
    AccountPermissions,
    StorageErrorCode
)
from .models import (
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
    ContainerPropertiesPaged,
    BlobProperties,
    BlobPropertiesPaged,
    BlobPrefix,
    LeaseProperties,
    ContentSettings,
    CopyProperties,
    BlobBlock,
    PageRange,
    AccessPolicy,
    ContainerPermissions,
    BlobPermissions,
)

__version__ = VERSION


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
    'ContainerPermissions',
    'BlobPermissions',
    'ResourceTypes',
    'AccountPermissions',
    'StorageStreamDownloader',
]


def upload_blob_to_url(
        blob_url,  # type: str
        data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
        overwrite=False,  # type: bool
        max_connections=1,  # type: int
        encoding='UTF-8', # type: str
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
    :param credential:
        The credentials with which to authenticate. This is optional if the
        blob URL already has a SAS token. The value can be a SAS token string, an account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the URL already has a SAS token, specifying an explicit credential will take priority.
    :returns: Blob-updated property dict (Etag and last modified)
    :rtype: dict(str, Any)
    """
    with BlobClient(blob_url, credential=credential) as client:
        return client.upload_blob(
            data=data,
            blob_type=BlobType.BlockBlob,
            overwrite=overwrite,
            max_connections=max_connections,
            encoding=encoding,
            **kwargs)


def _download_to_stream(client, handle, max_connections, **kwargs):
    """Download data to specified open file-handle."""
    stream = client.download_blob(**kwargs)
    stream.download_to_stream(handle, max_connections=max_connections)


def download_blob_from_url(
        blob_url,  # type: str
        output,  # type: str
        overwrite=False,  # type: bool
        max_connections=1,  # type: int
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
    :rtype: None
    """
    with BlobClient(blob_url, credential=credential) as client:
        if hasattr(output, 'write'):
            _download_to_stream(client, output, max_connections, **kwargs)
        else:
            if not overwrite and os.path.isfile(output):
                raise ValueError("The file '{}' already exists.".format(output))
            with open(output, 'wb') as file_handle:
                _download_to_stream(client, file_handle, max_connections, **kwargs)
