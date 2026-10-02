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

from typing import Callable, Iterator

from ._version import VERSION

__version__ = VERSION

try:
    from ._native import (
        upload_blob as _native_upload,
        download_blob as _native_download,
    )

    _NATIVE_AVAILABLE = True
except ImportError:
    _NATIVE_AVAILABLE = False


def is_available() -> bool:
    """Check if the native transfer extension module is available."""
    return _NATIVE_AVAILABLE


def upload_blob(
    url: str,
    data: bytes,
    *,
    token_provider: "Callable[[list], tuple] | None" = None,
    credential_id: "int | None" = None,
    overwrite: bool = False,
    content_type: "str | None" = None,
    content_encoding: "str | None" = None,
    content_language: "str | None" = None,
    content_disposition: "str | None" = None,
    cache_control: "str | None" = None,
    content_md5: "bytes | bytearray | None" = None,
    metadata: "dict[str, str] | None" = None,
    tags: "dict[str, str] | None" = None,
    lease_id: "str | None" = None,
    encryption_key: "str | None" = None,
    encryption_key_sha256: "str | None" = None,
    encryption_algorithm: "str | None" = None,
    encryption_scope: "str | None" = None,
    if_match: "str | None" = None,
    if_none_match: "str | None" = None,
    if_modified_since: "int | None" = None,
    if_unmodified_since: "int | None" = None,
    if_tags: "str | None" = None,
    immutability_policy_expiry: "int | None" = None,
    immutability_policy_mode: "str | None" = None,
    legal_hold: "bool | None" = None,
    tier: "str | None" = None,
    timeout: "int | None" = None,
    max_concurrency: "int | None" = None,
    max_block_size: "int | None" = None,
) -> dict:
    """Upload a block blob using the native Rust extension.

    :param str url: The fully-qualified blob URL
        (e.g. https://account.blob.core.windows.net/container/blob). Must be correctly
        percent-encoded and may include a SAS token in the query string.
    :param bytes data: The blob content to upload. Rust reads the immutable Python ``bytes``
        allocation directly without copying it across the FFI boundary. The payload must
        already be fully in memory; this function does not accept mutable buffers or file-like
        streams. Large or streamed uploads should use the ``azure-storage-blob`` Python upload
        path, which streams data in fixed-size chunks.
    :keyword token_provider: A callable invoked on demand to obtain an OAuth bearer token.
        It is called as ``token_provider(scopes: list[str])`` and must return a
        ``(token: str, expires_on: int)`` tuple, where ``expires_on`` is a Unix timestamp in
        seconds. The extension calls it whenever a fresh token is needed (including on
        refresh), so token expiry during long transfers is handled transparently. Not
        needed if ``url`` contains a SAS token.
    :paramtype token_provider: callable or None
    :keyword int credential_id: Stable identity for the Python credential behind
        ``token_provider``. Required when ``token_provider`` is provided. Calls with the same
        identity share a cached token; calls with different identities use separate token caches.
    :keyword bool overwrite: Whether to overwrite an existing blob. Defaults to False.
    :keyword str content_type: The content type of the blob.
    :keyword str content_encoding: The content encoding of the blob.
    :keyword str content_language: The content language of the blob.
    :keyword str content_disposition: The content disposition of the blob.
    :keyword str cache_control: The cache control value of the blob.
    :keyword bytes content_md5: The MD5 hash to store with the blob.
    :keyword dict metadata: Name-value pairs associated with the blob as metadata.
    :keyword dict tags: Name-value pairs to set as blob index tags.
    :keyword str lease_id: Lease ID required to upload to a leased blob.
    :keyword str encryption_key: Base64-encoded customer-provided encryption key.
    :keyword str encryption_key_sha256: Base64-encoded SHA-256 hash of the encryption key.
    :keyword str encryption_algorithm: Customer-provided encryption algorithm.
    :keyword str encryption_scope: Encryption scope to use for the blob.
    :keyword str if_match: Upload only if the blob's ETag matches this value.
    :keyword str if_none_match: Upload only if the blob's ETag does not match this value.
    :keyword int if_modified_since: Upload only if modified since this Unix timestamp.
    :keyword int if_unmodified_since: Upload only if unmodified since this Unix timestamp.
    :keyword str if_tags: SQL tag condition that must match for the upload.
    :keyword int immutability_policy_expiry: Immutability policy expiry as a Unix timestamp.
    :keyword str immutability_policy_mode: Immutability policy mode.
    :keyword bool legal_hold: Whether to place a legal hold on the blob.
    :keyword str tier: Access tier to set on the blob.
    :keyword int timeout: Server-side timeout applied to each upload request.
    :keyword int max_concurrency: Maximum number of parallel connections for chunked uploads.
    :keyword int max_block_size: Maximum size per block for chunked uploads.
    :returns: A dict containing available upload response values.
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
        credential_id=credential_id,
        overwrite=overwrite,
        content_type=content_type,
        content_encoding=content_encoding,
        content_language=content_language,
        content_disposition=content_disposition,
        cache_control=cache_control,
        content_md5=content_md5,
        metadata=metadata,
        tags=tags,
        lease_id=lease_id,
        encryption_key=encryption_key,
        encryption_key_sha256=encryption_key_sha256,
        encryption_algorithm=encryption_algorithm,
        encryption_scope=encryption_scope,
        if_match=if_match,
        if_none_match=if_none_match,
        if_modified_since=if_modified_since,
        if_unmodified_since=if_unmodified_since,
        if_tags=if_tags,
        immutability_policy_expiry=immutability_policy_expiry,
        immutability_policy_mode=immutability_policy_mode,
        legal_hold=legal_hold,
        tier=tier,
        timeout=timeout,
        max_concurrency=max_concurrency,
        max_block_size=max_block_size,
    )


def download_blob(
    url: str,
    *,
    token_provider: "Callable[[list], tuple] | None" = None,
    credential_id: "int | None" = None,
    offset: "int | None" = None,
    length: "int | None" = None,
    lease_id: "str | None" = None,
    encryption_key: "str | None" = None,
    encryption_key_sha256: "str | None" = None,
    encryption_algorithm: "str | None" = None,
    if_match: "str | None" = None,
    if_none_match: "str | None" = None,
    if_modified_since: "int | None" = None,
    if_unmodified_since: "int | None" = None,
    if_tags: "str | None" = None,
    version_id: "str | None" = None,
    timeout: "int | None" = None,
    max_concurrency: "int | None" = None,
    max_chunk_size: "int | None" = None,
) -> "Iterator[bytes]":
    """Begin a windowed download of a block blob using the native Rust extension.

    The returned object is a lazy iterator: each iteration downloads one window (up to
    ``max_chunk_size`` bytes, 256 MiB by default) via the Rust SDK's parallel ``download_into``.
    Peak memory is therefore bounded to a single window rather than the whole blob, while each
    window still benefits from concurrent range requests. This handles blobs of any size,
    including those larger than a single buffer.

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
    :keyword int credential_id: Stable identity for the Python credential behind
        ``token_provider``. Required when ``token_provider`` is provided. Calls with the same
        identity share a cached token; calls with different identities use separate token caches.
    :keyword int offset: Start of byte range to download.
    :keyword int length: Number of bytes to download from offset.
    :keyword str lease_id: Lease ID required to download a leased blob.
    :keyword str encryption_key: Base64-encoded customer-provided encryption key.
    :keyword str encryption_key_sha256: Base64-encoded SHA-256 hash of the encryption key.
    :keyword str encryption_algorithm: Customer-provided encryption algorithm.
    :keyword str if_match: Download only if the blob's ETag matches this value.
    :keyword str if_none_match: Download only if the blob's ETag does not match this value.
    :keyword int if_modified_since: Download only if modified since this Unix timestamp.
    :keyword int if_unmodified_since: Download only if unmodified since this Unix timestamp.
    :keyword str if_tags: SQL tag condition that must match for the download.
    :keyword str version_id: Blob version to download.
    :keyword int timeout: Server-side timeout applied to each download request.
    :keyword int max_concurrency: Maximum number of parallel connections for chunked downloads.
    :keyword int max_chunk_size: Size in bytes of each download window. Defaults to 256 MiB.
        Larger windows increase intra-window parallelism at the cost of higher peak memory.
    :returns: A lazy iterator yielding the blob content one window at a time. The object also
        exposes ``size`` (total bytes to be delivered).
    :rtype: Iterator[bytes]
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
        credential_id=credential_id,
        offset=offset,
        length=length,
        lease_id=lease_id,
        encryption_key=encryption_key,
        encryption_key_sha256=encryption_key_sha256,
        encryption_algorithm=encryption_algorithm,
        if_match=if_match,
        if_none_match=if_none_match,
        if_modified_since=if_modified_since,
        if_unmodified_since=if_unmodified_since,
        if_tags=if_tags,
        version_id=version_id,
        timeout=timeout,
        max_concurrency=max_concurrency,
        max_chunk_size=max_chunk_size,
    )
