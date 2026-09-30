# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Internal module for native transfer acceleration dispatch.

This module provides the bridge between azure-storage-blob's Python upload/download
paths and the optional azure-storage-extensions-transfer Rust extension. Uploads use
the Rust backend whenever the extension is available and raise for unsupported native
inputs rather than silently falling back to Python.
"""

from datetime import timezone
import logging
import os
import threading
from typing import Any, Callable, Dict, Iterator, Optional, Tuple, TYPE_CHECKING

from azure.core.credentials import AzureSasCredential
from ._models import BlobType
from ._serialize import (
    get_blob_modify_conditions,
    get_lease_id,
)

if TYPE_CHECKING:
    from ._shared.models import StorageConfiguration

_STORAGE_SCOPE = "https://storage.azure.com/.default"

_LOGGER = logging.getLogger(__name__)

# Escape hatch to force the pure-Python transfer path even when the native extension is
# installed. Intended for benchmarking and troubleshooting. Set the environment variable
# AZURE_STORAGE_DISABLE_NATIVE_TRANSFER to a truthy value ("1", "true", "yes", "on").
_DISABLE_NATIVE_ENV_VAR = "AZURE_STORAGE_DISABLE_NATIVE_TRANSFER"


def _native_disabled() -> bool:
    """Return True if the native transfer path has been explicitly disabled via env var."""
    return os.environ.get(_DISABLE_NATIVE_ENV_VAR, "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _is_native_available() -> bool:
    """Check if the native transfer extension is installed, importable, and not disabled."""
    if _native_disabled():
        return False
    try:
        from azure.storage.extensions.transfer import (
            is_available,
        )  # pylint: disable=import-outside-toplevel

        return is_available()
    except ImportError:
        return False


def _build_token_provider(
    credential: Any,
) -> Optional[Callable[[Any], Tuple[str, int]]]:
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


def _to_unix_timestamp(value: Any) -> Optional[int]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return int(value.timestamp())


def _can_use_native_upload(
    blob_type: str,
    encryption_options: Dict[str, Any],
    validate_content: Any,
    data: Any,
    credential: Any,
    **kwargs: Any,
) -> bool:
    """Validate native upload support.

    Returns ``False`` only when the native extension is unavailable or explicitly disabled.
    If the extension is available, unsupported upload options raise :class:`ValueError`
    with a reason-specific message instead of silently falling back to the Python upload path.
    """
    if not _is_native_available():
        return False

    if blob_type not in (BlobType.BLOCKBLOB, BlobType.BlockBlob, "BlockBlob"):
        raise ValueError(
            f"Native upload supports only block blobs; received blob type {blob_type!r}."
        )

    if encryption_options.get("key") or encryption_options.get("required"):
        raise ValueError("Native upload does not support client-side encryption.")

    if validate_content not in (None, False):
        raise ValueError(
            "Native upload does not support transactional content validation."
        )

    if kwargs.get("progress_hook"):
        raise ValueError("Native upload does not support progress hooks.")

    if credential is not None and not hasattr(credential, "get_token"):
        if not isinstance(credential, (str, AzureSasCredential)):
            raise ValueError(
                "Native upload requires a token credential or SAS credential; "
                f"received {type(credential).__name__}."
            )

    if isinstance(data, (bytes, str)):
        return True

    raise ValueError(
        "Native upload requires immutable bytes or str data that is already fully in memory; "
        f"received {type(data).__name__}."
    )


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
        if not isinstance(credential, (str, AzureSasCredential)):
            return False

    # No conditional access support
    if any(
        kwargs.get(k)
        for k in (
            "if_modified_since",
            "if_unmodified_since",
            "etag",
            "if_tags_match_condition",
        )
    ):
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
    """Upload through the native Rust extension when it is available.

    Returns ``None`` only when the extension is unavailable or explicitly disabled. Once the
    extension is available, unsupported inputs and native execution failures are raised rather
    than falling back to the Python upload path.
    """
    if not _can_use_native_upload(
        blob_type=blob_type,
        encryption_options=encryption_options,
        validate_content=validate_content,
        data=data,
        credential=blob_client.credential,
        **kwargs,
    ):
        _LOGGER.debug("Native upload extension unavailable; using Python upload path.")
        return None

    from azure.storage.extensions.transfer import (  # pylint: disable=import-outside-toplevel
        upload_blob as native_upload,
    )

    if isinstance(data, str):
        encoding = kwargs.get("encoding", "UTF-8")
        upload_data = data.encode(encoding)
    elif isinstance(data, bytes):
        upload_data = data
    else:
        raise ValueError(
            "Native upload requires immutable bytes or str data that is already fully in memory; "
            f"received {type(data).__name__}."
        )

    token_provider = _build_token_provider(blob_client.credential)

    overwrite = kwargs.get("overwrite", False)
    content_settings = kwargs.get("content_settings", None)
    content_type = getattr(content_settings, "content_type", None)
    content_encoding = getattr(content_settings, "content_encoding", None)
    content_language = getattr(content_settings, "content_language", None)
    content_disposition = getattr(content_settings, "content_disposition", None)
    cache_control = getattr(content_settings, "cache_control", None)
    content_md5 = getattr(content_settings, "content_md5", None)
    if content_md5 is not None:
        content_md5 = bytes(content_md5)

    metadata = kwargs.get("metadata", None)
    max_concurrency = kwargs.get("max_concurrency", None)
    cpk = kwargs.get("cpk", None)
    lease = get_lease_id(kwargs.get("lease", None))
    tags = kwargs.get("tags", None)

    conditions = get_blob_modify_conditions(dict(kwargs))
    if_tags = kwargs.get("if_tags_match_condition", None)

    immutability_policy = kwargs.get("immutability_policy", None)
    immutability_policy_expiry = None
    immutability_policy_mode = None
    if immutability_policy:
        immutability_policy_expiry = _to_unix_timestamp(
            immutability_policy.expiry_time
        )
        immutability_policy_mode = immutability_policy.policy_mode
        if hasattr(immutability_policy_mode, "value"):
            immutability_policy_mode = immutability_policy_mode.value

    tier = kwargs.get("standard_blob_tier", None)
    if hasattr(tier, "value"):
        tier = tier.value

    result = native_upload(
        url=blob_client.url,
        data=upload_data,
        token_provider=token_provider,
        credential_id=id(blob_client.credential) if token_provider else None,
        overwrite=overwrite,
        content_type=content_type,
        content_encoding=content_encoding,
        content_language=content_language,
        content_disposition=content_disposition,
        cache_control=cache_control,
        content_md5=content_md5,
        metadata=metadata,
        tags=tags,
        lease_id=lease,
        encryption_key=getattr(cpk, "key_value", None),
        encryption_key_sha256=getattr(cpk, "key_hash", None),
        encryption_algorithm=getattr(cpk, "algorithm", None),
        encryption_scope=kwargs.get("encryption_scope", None),
        if_match=conditions.get("if_match"),
        if_none_match=conditions.get("if_none_match"),
        if_modified_since=_to_unix_timestamp(conditions.get("if_modified_since")),
        if_unmodified_since=_to_unix_timestamp(
            conditions.get("if_unmodified_since")
        ),
        if_tags=if_tags,
        immutability_policy_expiry=immutability_policy_expiry,
        immutability_policy_mode=immutability_policy_mode,
        legal_hold=kwargs.get("legal_hold", None),
        tier=tier,
        timeout=kwargs.get("timeout", None),
        max_concurrency=max_concurrency,
        max_block_size=config.max_block_size,
    )
    _LOGGER.info("Used native Rust extension for blob upload.")
    return result


class NativeStorageStreamDownloader:
    """Lightweight wrapper returned when native download acceleration succeeds.

    Wraps the native windowed download stream (an iterator of ``bytes`` windows) and mimics the
    key parts of StorageStreamDownloader so callers (e.g. readall(), readinto(), chunks()) work
    transparently. Data is pulled from the native stream on demand, so only a single window is
    resident in memory at a time for the streaming paths (readinto/chunks); readall() necessarily
    materializes the full blob.
    """

    def __init__(self, stream: Any, name: str, container: str) -> None:
        self._stream = stream
        # Single persistent iterator over the native stream (which is single-pass).
        self._iter = iter(stream)
        # Buffer holding bytes pulled from the stream but not yet consumed by read().
        self._buffer = bytearray()
        self.name = name
        self.container = container
        self.size = stream.size
        self.properties = None  # Not available from native path

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[bytes]:
        return self.chunks()

    def readall(self) -> bytes:
        """Return the full blob content.

        :returns: The complete blob content.
        :rtype: bytes
        """
        chunks = []
        if self._buffer:
            chunks.append(bytes(self._buffer))
            self._buffer = bytearray()
        chunks.extend(self._iter)
        return b"".join(chunks)

    def read(self, size: int = -1) -> bytes:
        """Read up to *size* bytes from the downloaded content.

        :param int size: Maximum number of bytes to read. A negative value or ``None`` reads
            the remainder of the blob.
        :returns: Up to *size* bytes of content.
        :rtype: bytes
        """
        if size is None or size < 0:
            return self.readall()
        # Pull windows only until the buffer holds enough bytes or the stream is exhausted.
        while len(self._buffer) < size:
            window = next(self._iter, None)
            if window is None:
                break
            self._buffer += window
        result = bytes(self._buffer[:size])
        del self._buffer[:size]
        return result

    def readinto(self, stream: Any) -> int:
        """Write the full content to a writable stream, one window at a time.

        :param stream: A writable stream (file-like object).
        :returns: Number of bytes written.
        :rtype: int
        """
        total = 0
        if self._buffer:
            stream.write(self._buffer)
            total += len(self._buffer)
            self._buffer = bytearray()
        for window in self._iter:
            stream.write(window)
            total += len(window)
        return total

    def chunks(self) -> Iterator[bytes]:
        """Iterate over the download one window at a time.

        :returns: An iterator over the blob content windows.
        :rtype: Iterator[bytes]
        """
        if self._buffer:
            yield bytes(self._buffer)
            self._buffer = bytearray()
        yield from self._iter


def try_native_download_eager(
    blob_client: Any,
    offset: Optional[int],
    length: Optional[int],
    encryption_options: Dict[str, Any],
    validate_content: Any,
    **kwargs: Any,
) -> Optional["NativeStorageStreamDownloader"]:
    """Attempt to download the blob via the native Rust extension.

    If successful, returns a NativeStorageStreamDownloader wrapping the native windowed
    download stream. The stream fetches one window at a time using the Rust SDK's parallel
    ``download_into``, so peak memory is bounded to a single window for the streaming paths.

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

        stream = native_download(
            url=blob_client.url,
            token_provider=token_provider,
            credential_id=id(blob_client.credential) if token_provider else None,
            offset=offset,
            length=length,
            max_concurrency=max_concurrency,
        )
        _LOGGER.info("Used native Rust extension for blob download.")
        return NativeStorageStreamDownloader(
            stream=stream,
            name=blob_client.blob_name,
            container=blob_client.container_name,
        )

    except Exception:  # pylint: disable=broad-except
        _LOGGER.warning(
            "Native download failed; falling back to Python download path.",
            exc_info=True,
        )
        return None
