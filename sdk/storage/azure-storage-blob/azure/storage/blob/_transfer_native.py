# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Internal module for native transfer acceleration dispatch.

This module provides the bridge between azure-storage-blob's Python upload/download
paths and the optional azure-storage-extensionstransfer Rust extension. Transfers use
the Rust backend whenever the extension is available and raise for unsupported native
inputs rather than silently falling back to Python.
"""

from contextlib import contextmanager
from datetime import timezone
import os
import threading
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterator,
    NoReturn,
    Optional,
    Tuple,
    Type,
    TypeVar,
    TYPE_CHECKING,
)

from azure.core.credentials import AzureSasCredential
from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    DecodeError,
    HttpResponseError,
    IncompleteReadError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
    ServiceRequestError,
    ServiceResponseError,
)
from ._generated._utils.utils import prep_if_match, prep_if_none_match
from ._models import BlobType
from ._serialize import (
    get_modify_conditions,
    get_lease_id,
)

if TYPE_CHECKING:
    from ._shared.models import StorageConfiguration

_STORAGE_SCOPE = "https://storage.azure.com/.default"

_T = TypeVar("_T")

# Escape hatch to force the pure-Python transfer path even when the native extension is
# installed. Intended for benchmarking and troubleshooting. Set the environment variable
# AZURE_STORAGE_DISABLE_NATIVE_TRANSFER to a truthy value ("1", "true", "yes", "on").
_DISABLE_NATIVE_ENV_VAR = "AZURE_STORAGE_DISABLE_NATIVE_TRANSFER"

_NATIVE_HTTP_ERROR_TYPES: Dict[str, Type[HttpResponseError]] = {
    "ResourceNotFound": ResourceNotFoundError,
    "CannotVerifyCopySource": ResourceNotFoundError,
    "BlobNotFound": ResourceNotFoundError,
    "ContainerNotFound": ResourceNotFoundError,
    "AccountAlreadyExists": ResourceExistsError,
    "AccountBeingCreated": ResourceExistsError,
    "ResourceAlreadyExists": ResourceExistsError,
    "ResourceTypeMismatch": ResourceExistsError,
    "BlobAlreadyExists": ResourceExistsError,
    "ContainerAlreadyExists": ResourceExistsError,
    "ContainerBeingDeleted": ResourceExistsError,
    "ConditionNotMet": ResourceModifiedError,
    "BlobOverwritten": ResourceModifiedError,
    "InvalidAuthenticationInfo": ClientAuthenticationError,
    "AuthenticationFailed": ClientAuthenticationError,
}


def _native_error_type() -> Type[Exception]:
    try:
        # pylint: disable-next=import-error,no-name-in-module
        from azure.storage.extensions.transfer import (  # pylint: disable=import-outside-toplevel
            NativeTransferError,
        )
    except ImportError as error:
        raise RuntimeError(
            "The installed native transfer extension does not expose NativeTransferError. "
            "Install a compatible azure-storage-extensionstransfer build."
        ) from error
    return NativeTransferError


def _raise_native_error(error: Any) -> NoReturn:
    if error.kind == "http":
        status_error_type: Type[HttpResponseError] = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
        }.get(error.status_code, HttpResponseError)
        http_error_type = _NATIVE_HTTP_ERROR_TYPES.get(error.error_code, status_error_type)
        mapped = http_error_type(error.message)
        mapped.status_code = error.status_code
        setattr(mapped, "error_code", error.error_code)
        setattr(mapped, "additional_info", error.additional_info)
        setattr(mapped, "request_id", error.request_id)
        raise mapped from error

    error_type: Type[AzureError] = {
        "connection": ServiceRequestError,
        "io": ServiceResponseError,
        "incomplete_read": IncompleteReadError,
        "data_conversion": DecodeError,
        "credential": ClientAuthenticationError,
    }.get(error.kind, AzureError)
    raise error_type(error.message) from error


@contextmanager
def _translate_native_errors() -> Generator[None, None, None]:
    native_error = _native_error_type()
    try:
        yield
    except native_error as error:
        _raise_native_error(error)


class _NativeErrorIterator:
    def __init__(self, stream: Iterator[bytes]) -> None:
        self._stream = stream
        self._native_error = _native_error_type()
        self._failure: Optional[AzureError] = None

    def __iter__(self) -> "_NativeErrorIterator":
        return self

    def __next__(self) -> bytes:
        return self.call(next, self._stream)

    def call(self, function: Callable[..., _T], *args: Any) -> _T:
        """Invoke a native stream operation, mapping native errors and making failures sticky.

        :param function: The native operation to invoke.
        :type function: callable
        :param args: Positional arguments for the operation.
        :type args: any
        :returns: The operation's result.
        :rtype: any
        """
        if self._failure is not None:
            raise self._failure
        try:
            return function(*args)
        except self._native_error as error:
            try:
                _raise_native_error(error)
            except AzureError as mapped:
                self._failure = mapped
                raise


def _native_disabled() -> bool:
    """Check whether native transfers are explicitly disabled.

    :returns: Whether the disable environment variable is truthy.
    :rtype: bool
    """
    return os.environ.get(_DISABLE_NATIVE_ENV_VAR, "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _is_native_available() -> bool:
    """Check if the native transfer extension is installed, importable, and not disabled.

    :returns: Whether native transfers are available.
    :rtype: bool
    """
    if _native_disabled():
        return False
    try:
        # pylint: disable-next=import-error,no-name-in-module
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

    :param any credential: Credential used to obtain tokens.
    :returns: A token callback, or None for credentials without token support.
    :rtype: callable or None
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


def _get_native_modify_conditions(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    conditions = get_modify_conditions(dict(kwargs))
    etag = conditions.pop("etag", None)
    match_condition = conditions.pop("match_condition", None)
    conditions["if_match"] = prep_if_match(etag, match_condition)
    conditions["if_none_match"] = prep_if_none_match(etag, match_condition)
    return conditions


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

    :param str blob_type: Type of blob to upload.
    :param dict encryption_options: Client-side encryption settings.
    :param any validate_content: Content validation setting.
    :param any data: Upload payload.
    :param any credential: Authentication credential.
    :returns: Whether native upload is available for these inputs.
    :rtype: bool
    """
    if not _is_native_available():
        return False

    if blob_type not in (BlobType.BLOCKBLOB, BlobType.BlockBlob, "BlockBlob"):
        raise ValueError(f"Native upload supports only block blobs; received blob type {blob_type!r}.")

    if encryption_options.get("key") or encryption_options.get("required"):
        raise ValueError("Native upload does not support client-side encryption.")

    if validate_content not in (None, False):
        raise ValueError("Native upload does not support transactional content validation.")

    if kwargs.get("progress_hook"):
        raise ValueError("Native upload does not support progress hooks.")

    if credential is not None and not hasattr(credential, "get_token"):
        if not isinstance(credential, (str, AzureSasCredential)):
            raise ValueError(
                "Native upload requires a token credential or SAS credential; " f"received {type(credential).__name__}."
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
    """Validate native download support.

    Returns ``False`` only when the native extension is unavailable or explicitly disabled.
    If the extension is available, unsupported download options raise :class:`ValueError`
    with a reason-specific message instead of silently falling back to the Python download path.

    :param dict encryption_options: Client-side encryption settings.
    :param any validate_content: Content validation setting.
    :param any credential: Authentication credential.
    :returns: Whether native download is available for these inputs.
    :rtype: bool
    """
    if not _is_native_available():
        return False

    if encryption_options.get("key") or encryption_options.get("required") or encryption_options.get("resolver"):
        raise ValueError("Native download does not support client-side encryption.")

    if validate_content not in (None, False):
        raise ValueError("Native download does not support transactional content validation.")

    if kwargs.get("decompress", None) is True:
        raise ValueError("Native download does not support decompression.")

    if kwargs.get("encoding"):
        raise ValueError("Native download does not support text encoding.")

    if credential is not None and not hasattr(credential, "get_token"):
        if not isinstance(credential, (str, AzureSasCredential)):
            raise ValueError(
                "Native download requires a token credential or SAS credential; "
                f"received {type(credential).__name__}."
            )

    if kwargs.get("progress_hook"):
        raise ValueError("Native download does not support progress hooks.")

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

    :param any blob_client: Client for the target blob.
    :param any data: Upload payload.
    :param str blob_type: Type of blob to upload.
    :param dict encryption_options: Client-side encryption settings.
    :param any validate_content: Content validation setting.
    :param StorageConfiguration config: Transfer configuration.
    :returns: Upload response, or None when native transfers are unavailable.
    :rtype: dict or None
    """
    if not _can_use_native_upload(
        blob_type=blob_type,
        encryption_options=encryption_options,
        validate_content=validate_content,
        data=data,
        credential=blob_client.credential,
        **kwargs,
    ):
        return None

    # pylint: disable-next=import-error,no-name-in-module
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

    length = kwargs.get("length")
    if length is not None:
        upload_data = upload_data[:length]

    token_provider = _build_token_provider(blob_client.credential)

    content_settings = kwargs.get("content_settings", None)
    content_md5 = getattr(content_settings, "content_md5", None)
    if content_md5 is not None:
        content_md5 = bytes(content_md5)

    cpk = kwargs.get("cpk", None)
    lease = get_lease_id(kwargs.get("lease", None))
    tags = kwargs.get("tags", None)

    conditions = _get_native_modify_conditions(kwargs)
    if_tags = kwargs.get("if_tags_match_condition", None)

    immutability_policy = kwargs.get("immutability_policy", None)
    immutability_policy_expiry = None
    immutability_policy_mode = None
    if immutability_policy:
        immutability_policy_expiry = _to_unix_timestamp(immutability_policy.expiry_time)
        immutability_policy_mode = immutability_policy.policy_mode
        if hasattr(immutability_policy_mode, "value"):
            immutability_policy_mode = immutability_policy_mode.value

    tier = kwargs.get("standard_blob_tier", None)
    if tier is not None and hasattr(tier, "value"):
        tier = tier.value

    with _translate_native_errors():
        result = native_upload(
            url=(
                blob_client.url
                + ("&" if "?" in blob_client.url else "?")
                + blob_client.credential.signature.lstrip("?")
                if isinstance(blob_client.credential, AzureSasCredential)
                else blob_client.url
            ),
            data=upload_data,
            api_version=blob_client.api_version,
            token_provider=token_provider,
            credential_id=id(blob_client.credential) if token_provider else None,
            overwrite=kwargs.get("overwrite", False),
            content_type=getattr(content_settings, "content_type", None),
            content_encoding=getattr(content_settings, "content_encoding", None),
            content_language=getattr(content_settings, "content_language", None),
            content_disposition=getattr(content_settings, "content_disposition", None),
            cache_control=getattr(content_settings, "cache_control", None),
            content_md5=content_md5,
            metadata=kwargs.get("metadata", None),
            tags=tags,
            lease_id=lease,
            encryption_key=getattr(cpk, "key_value", None),
            encryption_key_sha256=getattr(cpk, "key_hash", None),
            encryption_algorithm=getattr(cpk, "algorithm", None),
            encryption_scope=kwargs.get("encryption_scope", None),
            if_match=conditions.get("if_match"),
            if_none_match=conditions.get("if_none_match"),
            if_modified_since=_to_unix_timestamp(conditions.get("if_modified_since")),
            if_unmodified_since=_to_unix_timestamp(conditions.get("if_unmodified_since")),
            if_tags=if_tags,
            immutability_policy_expiry=immutability_policy_expiry,
            immutability_policy_mode=immutability_policy_mode,
            legal_hold=kwargs.get("legal_hold", None),
            tier=tier,
            timeout=kwargs.get("timeout", None),
            max_concurrency=kwargs.get("max_concurrency", None),
            max_block_size=config.max_block_size,
        )
    return result


class NativeStorageStreamDownloader:
    """Lightweight wrapper returned when native download acceleration succeeds.

    Wraps the native download stream (an iterator of ``bytes`` chunks, one partition of
    ``max_chunk_get_size`` bytes each) and mimics the key parts of StorageStreamDownloader so callers
    (e.g. readall(), readinto()) work transparently. The native stream prefetches about
    one window (``max_concurrency`` partitions) ahead of consumption, so memory for the streaming
    paths (read/readinto) stays bounded. readall() necessarily materializes the full blob, and
    uses the native stream's own ``readall()`` when available to fill a single preallocated result.
    ``chunks()`` and direct iteration are not supported.
    """

    def __init__(self, stream: Any, name: str, container: str) -> None:
        self._stream = stream
        # Single persistent iterator over the native stream (which is single-pass).
        self._iter = _NativeErrorIterator(iter(stream))
        # Buffer holding bytes pulled from the stream but not yet consumed by read().
        self._buffer = bytearray()
        self.name = name
        self.container = container
        self.size = stream.size
        self.properties = None  # Not available from native path

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[bytes]:
        raise NotImplementedError(
            "Native downloads do not support direct iteration. Use read(), readall(), or readinto(), "
            "or set AZURE_STORAGE_DISABLE_NATIVE_TRANSFER=1 before downloading to iterate."
        )

    def readall(self) -> bytes:
        """Return the full blob content.

        :returns: The complete blob content.
        :rtype: bytes
        """
        buffered = bytes(self._buffer) if self._buffer else b""
        self._buffer = bytearray()
        native_readall = getattr(self._stream, "readall", None)
        if native_readall is not None:
            remainder = self._iter.call(native_readall)
            return buffered + remainder if buffered else remainder
        chunks = [buffered] if buffered else []
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
        buffer = self._buffer
        self._buffer = bytearray()
        # Pull chunks only until the buffer holds enough bytes or the stream is exhausted.
        while len(buffer) < size:
            chunk = next(self._iter, None)
            if chunk is None:
                break
            buffer += chunk
        result = bytes(buffer[:size])
        del buffer[:size]
        self._buffer = buffer
        return result

    def readinto(self, stream: Any) -> int:
        """Write the full content to a writable stream, one chunk at a time.

        :param any stream: A writable stream (file-like object).
        :returns: Number of bytes written.
        :rtype: int
        """
        total = 0
        if self._buffer:
            stream.write(self._buffer)
            total += len(self._buffer)
            self._buffer = bytearray()
        for chunk in self._iter:
            stream.write(chunk)
            total += len(chunk)
        return total

    def chunks(self) -> Iterator[bytes]:
        """Chunk iteration is not supported for native downloads.

        :returns: No value; always raises NotImplementedError.
        :rtype: Iterator[bytes]
        :raises NotImplementedError: Native downloads do not support chunk iteration.
        """
        raise NotImplementedError(
            "Native downloads do not support chunks(). Use read(), readall(), or readinto(), "
            "or set AZURE_STORAGE_DISABLE_NATIVE_TRANSFER=1 before downloading to use chunks()."
        )


def try_native_download(
    blob_client: Any,
    offset: Optional[int],
    length: Optional[int],
    encryption_options: Dict[str, Any],
    validate_content: Any,
    **kwargs: Any,
) -> Optional["NativeStorageStreamDownloader"]:
    """Download through the native Rust extension when it is available.

    If successful, returns a NativeStorageStreamDownloader wrapping the native download stream.
    The stream keeps up to ``max_concurrency`` ranged requests in flight, ETag-locked to the
    first response, and prefetches a bounded number of partitions ahead of consumption, so memory
    stays bounded for the streaming paths. readall() has the native stream copy the downloaded
    partitions straight into a single preallocated result.

    Returns ``None`` only when the extension is unavailable or explicitly disabled. Once the
    extension is available, unsupported inputs and native execution failures are raised rather
    than falling back to the Python download path.

    :param any blob_client: Client for the source blob.
    :param int offset: Start of the download range, or None.
    :param int length: Number of bytes to download, or None.
    :param dict encryption_options: Client-side encryption settings.
    :param any validate_content: Content validation setting.
    :returns: Native downloader, or None when native transfers are unavailable.
    :rtype: NativeStorageStreamDownloader or None
    """
    if not _can_use_native_download(
        encryption_options=encryption_options,
        validate_content=validate_content,
        credential=blob_client.credential,
        **kwargs,
    ):
        return None

    # pylint: disable-next=import-error,no-name-in-module
    from azure.storage.extensions.transfer import (  # pylint: disable=import-outside-toplevel
        download_blob as native_download,
    )

    token_provider = _build_token_provider(blob_client.credential)
    max_concurrency = kwargs.get("max_concurrency", None)
    cpk = kwargs.get("cpk", None)
    lease = get_lease_id(kwargs.get("lease", None))
    conditions = _get_native_modify_conditions(kwargs)
    version_id = kwargs.get("version_id", getattr(blob_client, "version_id", None))

    with _translate_native_errors():
        stream = native_download(
            url=(
                blob_client.url
                + ("&" if "?" in blob_client.url else "?")
                + blob_client.credential.signature.lstrip("?")
                if isinstance(blob_client.credential, AzureSasCredential)
                else blob_client.url
            ),
            api_version=blob_client.api_version,
            token_provider=token_provider,
            credential_id=id(blob_client.credential) if token_provider else None,
            offset=offset,
            length=length,
            lease_id=lease,
            encryption_key=getattr(cpk, "key_value", None),
            encryption_key_sha256=getattr(cpk, "key_hash", None),
            encryption_algorithm=getattr(cpk, "algorithm", None),
            if_match=conditions.get("if_match"),
            if_none_match=conditions.get("if_none_match"),
            if_modified_since=_to_unix_timestamp(conditions.get("if_modified_since")),
            if_unmodified_since=_to_unix_timestamp(conditions.get("if_unmodified_since")),
            if_tags=kwargs.get("if_tags_match_condition", None),
            version_id=version_id,
            timeout=kwargs.get("timeout", None),
            max_concurrency=max_concurrency,
            max_chunk_size=blob_client._config.max_chunk_get_size,  # pylint: disable=protected-access
        )
    return NativeStorageStreamDownloader(
        stream=stream,
        name=blob_client.blob_name,
        container=blob_client.container_name,
    )
