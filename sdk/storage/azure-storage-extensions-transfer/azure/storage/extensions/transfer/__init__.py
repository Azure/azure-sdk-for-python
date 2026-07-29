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

from typing import Callable

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
    url: str,
    data: "bytes | bytearray | memoryview",
    *,
    token_provider: "Callable[[list], tuple] | None" = None,
    overwrite: bool = False,
    content_type: "str | None" = None,
    metadata: "dict[str, str] | None" = None,
    max_concurrency: "int | None" = None,
    max_single_put_size: "int | None" = None,
    max_block_size: "int | None" = None,
) -> dict:
    """Upload a block blob using the native Rust extension.

    :param str url: The fully-qualified blob URL
        (e.g. https://account.blob.core.windows.net/container/blob). Must be correctly
        percent-encoded and may include a SAS token in the query string.
    :param data: The blob content to upload. Accepts any C-contiguous buffer-protocol
        object (``bytes``, ``bytearray``, or ``memoryview``); no copy to ``bytes`` is required.
        The payload must already be fully in memory — this function does not accept
        file-like streams. Large or streamed uploads should use the ``azure-storage-blob``
        Python upload path, which streams data in fixed-size chunks.
    :type data: bytes or bytearray or memoryview
    :keyword token_provider: A callable invoked on demand to obtain an OAuth bearer token.
        It is called as ``token_provider(scopes: list[str])`` and must return a
        ``(token: str, expires_on: int)`` tuple, where ``expires_on`` is a Unix timestamp in
        seconds. The extension calls it whenever a fresh token is needed (including on
        refresh), so token expiry during long transfers is handled transparently. Not
        needed if ``url`` contains a SAS token.
    :paramtype token_provider: callable or None
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
        url,
        data,
        token_provider=token_provider,
        overwrite=overwrite,
        content_type=content_type,
        metadata=metadata,
        max_concurrency=max_concurrency,
        _max_single_put_size=max_single_put_size,
        max_block_size=max_block_size,
    )


def download_blob(
    url: str,
    *,
    token_provider: "Callable[[list], tuple] | None" = None,
    offset: "int | None" = None,
    length: "int | None" = None,
    max_concurrency: "int | None" = None,
    expected_size: "int | None" = None,
) -> bytes:
    """Download a block blob using the native Rust extension.

    :param str url: The fully-qualified blob URL
        (e.g. https://account.blob.core.windows.net/container/blob). Must be correctly
        percent-encoded and may include a SAS token in the query string.
    :keyword token_provider: A callable invoked on demand to obtain an OAuth bearer token.
        It is called as ``token_provider(scopes: list[str])`` and must return a
        ``(token: str, expires_on: int)`` tuple, where ``expires_on`` is a Unix timestamp in
        seconds. The extension calls it whenever a fresh token is needed (including on
        refresh), so token expiry during long transfers is handled transparently. Not
        needed if ``url`` contains a SAS token.
    :paramtype token_provider: callable or None
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
        url,
        token_provider=token_provider,
        offset=offset,
        length=length,
        max_concurrency=max_concurrency,
        expected_size=expected_size,
    )
