# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Azure Storage Transfer Extensions — Rust-based acceleration for blob transfers.

This package provides native Rust-based acceleration for Azure Storage Blob
upload and download operations. It is not intended for direct use; instead,
install it via the `ext-transfer` extra on `azure-storage-blob`:

    pip install azure-storage-blob[ext-transfer]
"""

from ._version import VERSION

__version__ = VERSION

try:
    from ._native import upload_blob as _native_upload, download_blob as _native_download

    _NATIVE_AVAILABLE = True
except ImportError:
    _NATIVE_AVAILABLE = False


def is_available() -> bool:
    """Check if the native transfer extension module is available."""
    return _NATIVE_AVAILABLE


def upload_blob(
    account_url: str,
    container: str,
    blob: str,
    data: bytes,
    *,
    access_token: "str | None" = None,
    overwrite: bool = False,
    content_type: "str | None" = None,
    metadata: "dict[str, str] | None" = None,
    max_concurrency: "int | None" = None,
    max_single_put_size: "int | None" = None,
    max_block_size: "int | None" = None,
) -> dict:
    """Upload a block blob using the native Rust extension.

    :param str account_url: The storage account URL (e.g. https://account.blob.core.windows.net).
        May include a SAS token in the query string.
    :param str container: The container name.
    :param str blob: The blob name.
    :param bytes data: The blob content to upload.
    :keyword str access_token: An OAuth access token for authentication.
        Not needed if account_url contains a SAS token.
    :keyword bool overwrite: Whether to overwrite an existing blob. Defaults to False.
    :keyword str content_type: The content type of the blob.
    :keyword dict metadata: Name-value pairs associated with the blob as metadata.
    :keyword int max_concurrency: Maximum number of parallel connections for chunked uploads.
    :keyword int max_single_put_size: Maximum size for a single PUT operation before chunking.
    :keyword int max_block_size: Maximum size per block for chunked uploads.
    :returns: A dict with response headers (etag, last_modified, etc.).
    :rtype: dict
    :raises ValueError: If the native module is not available.
    """
    if not _NATIVE_AVAILABLE:
        raise ValueError(
            "Native transfer extension is not available. "
            "Install azure-storage-extensions-transfer to use this function."
        )
    return _native_upload(
        account_url,
        container,
        blob,
        data,
        access_token=access_token,
        overwrite=overwrite,
        content_type=content_type,
        metadata=metadata,
        max_concurrency=max_concurrency,
        _max_single_put_size=max_single_put_size,
        max_block_size=max_block_size,
    )


def download_blob(
    account_url: str,
    container: str,
    blob: str,
    *,
    access_token: "str | None" = None,
    offset: "int | None" = None,
    length: "int | None" = None,
    max_concurrency: "int | None" = None,
    expected_size: "int | None" = None,
) -> bytes:
    """Download a block blob using the native Rust extension.

    :param str account_url: The storage account URL (e.g. https://account.blob.core.windows.net).
        May include a SAS token in the query string.
    :param str container: The container name.
    :param str blob: The blob name.
    :keyword str access_token: An OAuth access token for authentication.
        Not needed if account_url contains a SAS token.
    :keyword int offset: Start of byte range to download.
    :keyword int length: Number of bytes to download from offset.
    :keyword int max_concurrency: Maximum number of parallel connections for chunked downloads.
    :keyword int expected_size: Expected blob size in bytes. Used to pre-allocate the download buffer.
    :returns: The blob content as bytes.
    :rtype: bytes
    :raises ValueError: If the native module is not available.
    """
    if not _NATIVE_AVAILABLE:
        raise ValueError(
            "Native transfer extension is not available. "
            "Install azure-storage-extensions-transfer to use this function."
        )
    return _native_download(
        account_url,
        container,
        blob,
        access_token=access_token,
        offset=offset,
        length=length,
        max_concurrency=max_concurrency,
        expected_size=expected_size,
    )
