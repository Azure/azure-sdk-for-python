# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Internal module for native transfer acceleration dispatch.

This module provides the bridge between azure-storage-blob's Python upload/download
paths and the optional azure-storage-extensions-transfer Rust extension. When the
extension is installed and conditions are met, transfers are dispatched to the Rust
backend for improved performance.
"""

from typing import Any, Callable, Dict, Iterator, Optional, Tuple, TYPE_CHECKING

import logging
import threading

if TYPE_CHECKING:
    from ._shared.models import StorageConfiguration

_STORAGE_SCOPE = "https://storage.azure.com/.default"

_LOGGER = logging.getLogger(__name__)


def _is_native_available() -> bool:
    """Check if the native transfer extension is installed and importable."""
    try:
        from azure.storage.extensions.transfer import is_available  # pylint: disable=import-outside-toplevel

        return is_available()
    except ImportError:
        return False


def _build_token_provider(credential: Any) -> Optional[Callable[[Any], Tuple[str, int]]]:
    """Build a token-provider callable for the native extension.

    The native extension refreshes tokens on demand by calling back into Python
    rather than caching a single token string. This returns a callable with the
    signature ``provider(scopes) -> (token, expires_on)`` (``expires_on`` is a Unix
    timestamp in seconds), or ``None`` if the credential doesn't use OAuth tokens
    (e.g. shared key or SAS — those authenticate via the URL).

    The returned closure calls ``credential.get_token`` **fresh on every invocation**
    (no local caching), deferring all caching and refresh to the credential itself.
    azure-identity credentials proactively refresh within 5 minutes of expiry and force
    a synchronous refresh once a token is expired, so the extension never receives an
    already-expired token. A per-provider :class:`threading.Lock` serializes concurrent
    calls (the native side may invoke the provider from multiple worker threads).
    """
    if credential is None:
        return None
    if not hasattr(credential, "get_token"):
        return None

    lock = threading.Lock()

    def provider(scopes: Any) -> Tuple[str, int]:
        # Rust passes the scopes requested by the bearer-token policy; fall back to the
        # storage scope if none were provided.
        requested = tuple(scopes) if scopes else (_STORAGE_SCOPE,)
        with lock:
            token = credential.get_token(*requested)
        return token.token, int(token.expires_on)

    return provider


def _can_use_native_upload(
    blob_type: str,
    encryption_options: Dict[str, Any],
    validate_content: Any,
    data: Any,
    credential: Any,
    **kwargs: Any,
) -> bool:
    """Determine if native upload acceleration can be used for this call."""
    if not _is_native_available():
        return False

    # Only block blob supported
    from ._models import BlobType  # pylint: disable=import-outside-toplevel

    if blob_type not in (BlobType.BLOCKBLOB, BlobType.BlockBlob, "BlockBlob"):
        return False

    # No encryption support
    if encryption_options.get("key") or encryption_options.get("required"):
        return False

    # No content validation support
    if validate_content not in (None, False):
        return False

    # No progress hook support (yet)
    if kwargs.get("progress_hook"):
        return False

    # No CPK support
    if kwargs.get("cpk"):
        return False

    # Credential must be TokenCredential or SAS (not shared key)
    if credential is not None and not hasattr(credential, "get_token"):
        # Check if it's a SAS credential or string — those work via URL
        from azure.core.credentials import AzureSasCredential  # pylint: disable=import-outside-toplevel

        if not isinstance(credential, (str, AzureSasCredential)):
            return False

    # No conditional access support
    if any(kwargs.get(k) for k in (
        "if_modified_since", "if_unmodified_since", "etag", "if_tags_match_condition",
    )):
        return False

    # No lease support
    if kwargs.get("lease"):
        return False

    # No tags support
    if kwargs.get("tags"):
        return False

    # No immutability policy support
    if kwargs.get("immutability_policy") or kwargs.get("legal_hold"):
        return False

    # No tier support
    if kwargs.get("standard_blob_tier") or kwargs.get("premium_page_blob_tier"):
        return False

    # Native acceleration only handles data that is already fully in memory
    # (bytes/bytearray/memoryview, or str which encodes to in-memory bytes).
    # File-like streams are intentionally NOT eligible: reading them would
    # materialize the entire payload in memory, which is unsafe for large blobs.
    # The Python upload path streams such inputs in fixed-size chunks, so we
    # fall back to it for anything that isn't already resident in memory.
    if isinstance(data, (bytes, bytearray, memoryview, str)):
        return True

    _LOGGER.debug(
        "Native upload not eligible for %s input (streams use the Python upload path).",
        type(data).__name__,
    )
    return False


def _can_use_native_download(
    encryption_options: Dict[str, Any],
    validate_content: Any,
    credential: Any,
    **kwargs: Any,
) -> bool:
    """Determine if native download acceleration can be used for this call."""
    if not _is_native_available():
        return False

    # No encryption support
    if encryption_options.get("key") or encryption_options.get("required"):
        return False

    # No content validation support
    if validate_content not in (None, False):
        return False

    # No decompression support — if explicitly requested
    if kwargs.get("decompress", None) is True:
        return False

    # No encoding (text mode) support
    if kwargs.get("encoding"):
        return False

    # No CPK support
    if kwargs.get("cpk"):
        return False

    # Credential must be TokenCredential or SAS
    if credential is not None and not hasattr(credential, "get_token"):
        from azure.core.credentials import AzureSasCredential  # pylint: disable=import-outside-toplevel

        if not isinstance(credential, (str, AzureSasCredential)):
            return False

    # No conditional access support
    if any(kwargs.get(k) for k in (
        "if_modified_since", "if_unmodified_since", "etag", "if_tags_match_condition",
    )):
        return False

    # No lease support
    if kwargs.get("lease"):
        return False

    # No progress hook support
    if kwargs.get("progress_hook"):
        return False

    return True


def try_native_upload(
    blob_client: Any,
    data: Any,
    blob_type: str,
    encryption_options: Dict[str, Any],
    validate_content: Any,
    config: "StorageConfiguration",
    **kwargs: Any,
) -> Optional[Dict[str, Any]]:
    """Attempt to perform upload via the native Rust extension.

    Returns the upload result dict if native upload was used successfully,
    or None if conditions aren't met or native upload fails.
    """
    if not _can_use_native_upload(
        blob_type=blob_type,
        encryption_options=encryption_options,
        validate_content=validate_content,
        data=data,
        credential=blob_client.credential,
        **kwargs,
    ):
        _LOGGER.debug("Native upload not eligible; using Python upload path.")
        return None

    try:
        from azure.storage.extensions.transfer import (  # pylint: disable=import-outside-toplevel
            upload_blob as native_upload,
        )

        # Prepare data as a buffer-protocol object. The native module accepts bytes,
        # bytearray, and contiguous memoryview directly (via PyBuffer), so we avoid an
        # extra Python-side copy for the non-bytes buffer types. Only str needs encoding.
        # File-like streams are rejected by _can_use_native_upload (they use the Python
        # path to avoid materializing large payloads in memory), so we don't handle them
        # here.
        if isinstance(data, str):
            encoding = kwargs.get("encoding", "UTF-8")
            upload_data = data.encode(encoding)
        elif isinstance(data, (bytes, bytearray, memoryview)):
            upload_data = data
        else:
            _LOGGER.debug("Native upload data type unsupported; using Python upload path.")
            return None

        token_provider = _build_token_provider(blob_client.credential)

        overwrite = kwargs.get("overwrite", False)
        content_settings = kwargs.get("content_settings", None)
        content_type = None
        if content_settings and hasattr(content_settings, "content_type"):
            content_type = content_settings.content_type

        metadata = kwargs.get("metadata", None)
        max_concurrency = kwargs.get("max_concurrency", None)

        result = native_upload(
            url=blob_client.url,
            data=upload_data,
            token_provider=token_provider,
            overwrite=overwrite,
            content_type=content_type,
            metadata=metadata,
            max_concurrency=max_concurrency,
            max_single_put_size=config.max_single_put_size,
            max_block_size=config.max_block_size,
        )
        _LOGGER.info("Used native Rust extension for blob upload.")
        return result

    except Exception:  # pylint: disable=broad-except
        # If native upload fails for any reason, fall back to Python path
        _LOGGER.warning("Native upload failed; falling back to Python upload path.", exc_info=True)
        return None


class NativeStorageStreamDownloader:
    """Lightweight wrapper returned when native download acceleration succeeds eagerly.

    Mimics the key parts of StorageStreamDownloader so callers (e.g. readall(), readinto(),
    chunks()) work transparently without needing the full Python download infrastructure.
    """

    def __init__(self, data: bytes, name: str, container: str) -> None:
        self._data = data
        self._offset = 0
        self.name = name
        self.container = container
        self.size = len(data)
        self.properties = None  # Not available from native path

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[bytes]:
        return self.chunks()

    def readall(self) -> bytes:
        """Return the full blob content."""
        return self._data

    def read(self, size: int = -1) -> bytes:
        """Read up to *size* bytes from the downloaded content."""
        if size == -1 or size is None:
            chunk = self._data[self._offset:]
            self._offset = len(self._data)
            return chunk
        chunk = self._data[self._offset:self._offset + size]
        self._offset += len(chunk)
        return chunk

    def readinto(self, stream: Any) -> int:
        """Write the full content to a writable stream.

        :param stream: A writable stream (file-like object).
        :returns: Number of bytes written.
        :rtype: int
        """
        stream.write(self._data)
        return len(self._data)

    def chunks(self) -> Iterator[bytes]:
        """Iterate over the download in a single chunk."""
        yield self._data


def try_native_download_eager(
    blob_client: Any,
    offset: Optional[int],
    length: Optional[int],
    encryption_options: Dict[str, Any],
    validate_content: Any,
    **kwargs: Any,
) -> Optional["NativeStorageStreamDownloader"]:
    """Attempt to eagerly download the blob via the native Rust extension.

    If successful, returns a NativeStorageStreamDownloader wrapping the data.
    This avoids the initial HTTP request that StorageStreamDownloader would make.

    Returns None if conditions aren't met or native download fails, allowing
    the caller to fall back to the standard StorageStreamDownloader path.
    """
    if not _can_use_native_download(
        encryption_options=encryption_options,
        validate_content=validate_content,
        credential=blob_client.credential,
        **kwargs,
    ):
        _LOGGER.debug("Native download not eligible; using Python download path.")
        return None

    try:
        from azure.storage.extensions.transfer import (  # pylint: disable=import-outside-toplevel
            download_blob as native_download,
        )

        token_provider = _build_token_provider(blob_client.credential)
        max_concurrency = kwargs.get("max_concurrency", None)

        data = native_download(
            url=blob_client.url,
            token_provider=token_provider,
            offset=offset,
            length=length,
            max_concurrency=max_concurrency,
        )
        _LOGGER.info("Used native Rust extension for blob download.")
        return NativeStorageStreamDownloader(
            data=data,
            name=blob_client.blob_name,
            container=blob_client.container_name,
        )

    except Exception:  # pylint: disable=broad-except
        _LOGGER.warning("Native download failed; falling back to Python download path.", exc_info=True)
        return None
