# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Checkpoint destination/manifest validation and sync/async preparation."""

from dataclasses import dataclass
from os import PathLike, scandir
from pathlib import Path
import re
from stat import S_ISDIR
from typing import Any, Optional, Union
from unicodedata import normalize
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit

from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict

from ._exceptions import FineTuningSessionsError, MalformedResponseError
from ._operation_compat import (
    _NO_BODY,
    _SERIALIZER,
    _identifier,
    _polling_endpoint,
    _polling_interval,
    _raise_request_error,
    _request,
    _retry_delay,
)
from .models._enums import FoundryFeaturesOptInKeys

_RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {
    f"{prefix}{suffix}" for prefix in ("COM", "LPT") for suffix in "123456789\u00b9\u00b2\u00b3"
}
_FILE_ID = re.compile(r"[0-9a-f]{64}")
_STRONG_ETAG = re.compile(r'"[\x21\x23-\x7e\x80-\xff]*"')


@dataclass(frozen=True)
class _CheckpointDownloadFile:
    """Validated private metadata; filename retains its relative POSIX spelling."""

    file_id: str
    filename: str
    size_bytes: int
    etag: str
    download_url: str


_CheckpointDownloadManifest = tuple[_CheckpointDownloadFile, ...]


def _validate_path_component(value: str, name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if (
        not value
        or value in {".", ".."}
        or value.endswith((".", " "))
        or any(ord(char) < 32 or char in '<>:"/\\|?*' for char in value)
        or value.partition(".")[0].rstrip(" ").upper() in _RESERVED_NAMES
    ):
        raise ValueError(f"{name} must be a single portable directory name")


def _directory_exists(path: Path) -> bool:
    try:
        mode = path.stat().st_mode
    except FileNotFoundError:
        # Windows can report a missing child when its ancestor is actually a file.
        if path.parent != path:
            _directory_exists(path.parent)
        return False
    if not S_ISDIR(mode):
        raise NotADirectoryError(f"Expected a directory: {path}")
    return True


def _validate_checkpoint_output_path(
    session_id: str, checkpoint_id: str, output_path: Union[str, PathLike[str]]
) -> None:
    """Check an empty/absent destination without creating or writing it.

    :param str session_id: Verbatim session directory component.
    :param str checkpoint_id: Verbatim checkpoint directory component.
    :param output_path: Local root containing session and checkpoint directories.
    :type output_path: str or ~os.PathLike[str]
    """
    _validate_path_component(session_id, "session_id")
    _validate_path_component(checkpoint_id, "checkpoint_id")
    output = Path(output_path)
    root = output.resolve()
    session = output / session_id
    checkpoint = session / checkpoint_id
    for path in (output, session, checkpoint):
        if path != output:
            resolved = path.resolve()
            if resolved == root or not resolved.is_relative_to(root):
                raise ValueError("Checkpoint destination must remain within output_path")
        if _directory_exists(path) and path == checkpoint:
            with scandir(path) as entries:
                if next(entries, None) is not None:
                    raise ValueError(f"Checkpoint directory must be empty: {path}")


def _build_checkpoint_download_request(
    session_id: str, checkpoint_id: str, *, foundry_features: str, api_version: str, **kwargs: Any
) -> HttpRequest:
    """Build the bodyless preparation POST using the existing preview headers.

    :param str session_id: Canonical session identifier.
    :param str checkpoint_id: Registered sampler checkpoint identifier.
    :keyword str foundry_features: Required feature opt-in header.
    :keyword str api_version: API version preserved in the query.
    :return: Bodyless checkpoint preparation request.
    :rtype: ~azure.core.rest.HttpRequest
    """
    headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    params = case_insensitive_dict(kwargs.pop("params", {}) or {})
    headers["Accept"] = "application/json"
    headers["Foundry-Features"] = _SERIALIZER.header("foundry_features", foundry_features, "str")
    params["api-version"] = _SERIALIZER.query("api_version", api_version, "str")
    session = _SERIALIZER.url("session_id", session_id, "str")
    checkpoint = _SERIALIZER.url("checkpoint_id", checkpoint_id, "str")
    return HttpRequest(
        "POST",
        f"/fine_tuning_sessions/{session}/checkpoints/{checkpoint}/download",
        headers=headers,
        params=params,
        **kwargs,
    )


def _parse_checkpoint_download_manifest(files: Any, preparation_url: str) -> _CheckpointDownloadManifest:
    """Validate the entire inventory without I/O.

    :param files: Complete file inventory returned by preparation.
    :type files: list[dict]
    :param str preparation_url: Successful public preparation URL.
    :return: Immutable descriptors resolving only API-issued locators.
    :rtype: tuple
    """
    if not isinstance(files, list) or not files:
        raise ValueError("files must be a nonempty list")
    preparation = urlsplit(preparation_url)
    versions = parse_qsl(preparation.query, keep_blank_values=True, strict_parsing=True)
    if any(key != "api-version" for key, _ in versions):
        raise ValueError("unexpected preparation query")
    query = urlencode(versions)
    query_suffix = "?" + query if query else ""
    manifest = []
    file_ids: set[str] = set()
    file_paths: set[tuple[str, ...]] = set()
    paths: dict[tuple[str, ...], tuple[str, ...]] = {}
    for file in files:
        if not isinstance(file, dict):
            raise ValueError("each file must be an object")
        file_id = file.get("file_id")
        filename = file.get("filename")
        size = file.get("size_bytes")
        etag = file.get("etag")
        locator = file.get("download_url")
        if not isinstance(file_id, str) or not _FILE_ID.fullmatch(file_id) or file_id in file_ids:
            raise ValueError("file_id must be a unique opaque file identifier")
        if not isinstance(filename, str) or "\x7f" in filename:
            raise ValueError("filename must be a portable relative file path")
        try:
            filename.encode("utf-8")
        except UnicodeError as error:
            raise ValueError("filename must contain valid Unicode") from error
        components = tuple(filename.split("/"))
        for component in components:
            _validate_path_component(component, "filename component")
        # Compare aliases conservatively across case-insensitive and normalizing filesystems.
        folded = tuple(normalize("NFC", component.upper().casefold()) for component in components)
        for length in range(1, len(components) + 1):
            key, spelling = folded[:length], components[:length]
            if (
                key in file_paths
                or (length == len(components) and key in paths)
                or (key in paths and paths[key] != spelling)
            ):
                raise ValueError("filenames collide or conflict with a directory")
            paths[key] = spelling
        if type(size) is not int or size < 0:  # pylint: disable=unidiomatic-typecheck
            raise ValueError("size_bytes must be an exact nonnegative integer")
        if not isinstance(etag, str) or not _STRONG_ETAG.fullmatch(etag):
            raise ValueError("etag must be one strong entity tag")
        # The API emits this exact request-relative form, never storage or backend URLs.
        if locator != f"download/files/{file_id}{query_suffix}":
            raise ValueError("download_url must be the version-preserving request-relative file locator")
        download_url = urljoin(preparation_url, locator)
        # The fixed relative locator cannot change authority; reject path normalization.
        if urlsplit(download_url).path != preparation.path + "/files/" + file_id:
            raise ValueError("download_url must remain on the preparation checkpoint route")
        manifest.append(_CheckpointDownloadFile(file_id, filename, size, etag, download_url))
        file_ids.add(file_id)
        file_paths.add(folded)
    return tuple(manifest)


def _checkpoint_download_result(
    response: Any, session_id: str, preparation_url: str
) -> Optional[_CheckpointDownloadManifest]:
    """Return a complete manifest or pending state, preserving explicit failures.

    :param response: Preparation HTTP response.
    :type response: ~azure.core.rest.HttpResponse
    :param str session_id: Session identifier used for typed error context.
    :param str preparation_url: Exact URL used for preparation.
    """
    if response.status_code not in (200, 202):
        _raise_request_error(response, {}, session_id)
    payload = response.json()
    status = payload.get("status") if isinstance(payload, dict) else None
    if (response.status_code == 202 and status != "Pending") or (
        response.status_code == 200 and status not in ("Succeeded", "Failed")
    ):
        raise MalformedResponseError("Invalid checkpoint download preparation status.", response=response)
    if status == "Failed":
        raise FineTuningSessionsError("Checkpoint download preparation failed.", response=response)
    if status == "Pending":
        return None
    try:
        if response.request.url != preparation_url:
            raise ValueError("successful preparation URL changed")
        return _parse_checkpoint_download_manifest(payload.get("files"), response.request.url)
    except ValueError as error:
        raise MalformedResponseError(f"Invalid checkpoint download manifest: {error}.", response=response) from error


def _checkpoint_download_setup(operation: Any, session_id: str, checkpoint_id: str) -> tuple[dict[str, str], float]:
    """Resolve request identifiers and polling options after local validation.

    :param operation: Maintained checkpoint operation group.
    :type operation: object
    :param str session_id: Session identifier to normalize for HTTP.
    :param str checkpoint_id: Registered sampler checkpoint identifier.
    :return: Validated request arguments and polling interval.
    :rtype: tuple[dict[str, str], float]
    """
    # pylint: disable=protected-access
    # Resolve lazily because the public client patch imports operation hooks.
    from ._patch import _canonical_session_id

    _polling_endpoint(operation._config.endpoint)
    session_id = _canonical_session_id(_identifier(session_id, "session_id"))
    checkpoint_id = _identifier(checkpoint_id, "checkpoint_id")
    _identifier(session_id.removeprefix("session_"), "session_id")
    interval = _polling_interval(operation._config.polling_interval)
    arguments = {
        "session_id": session_id,
        "checkpoint_id": checkpoint_id,
        "foundry_features": FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW,
        "api_version": getattr(operation._config, "api_version", "v1"),
    }
    return arguments, interval


def _prepare_checkpoint_download(operation: Any, session_id: str, checkpoint_id: str) -> _CheckpointDownloadManifest:
    """Poll until ready without delivering files.

    :param operation: Synchronous maintained checkpoint operation group.
    :type operation: object
    :param str session_id: Session that owns the checkpoint.
    :param str checkpoint_id: Registered sampler checkpoint identifier.
    :return: Complete validated private file descriptors.
    :rtype: tuple
    """
    # pylint: disable=protected-access
    arguments, interval = _checkpoint_download_setup(operation, session_id, checkpoint_id)
    while True:
        request = _request(operation, _build_checkpoint_download_request, arguments, _NO_BODY, {})
        preparation_url = request.url
        response = operation._client._pipeline.run(
            request, stream=False, permit_redirects=False, retry_total=0
        ).http_response
        manifest = _checkpoint_download_result(response, arguments["session_id"], preparation_url)
        if manifest is not None:
            return manifest
        operation._client._pipeline._transport.sleep(_retry_delay(response, {}, interval))


async def _prepare_checkpoint_download_async(
    operation: Any, session_id: str, checkpoint_id: str
) -> _CheckpointDownloadManifest:
    """Asynchronously prepare and validate the manifest without file delivery.

    :param operation: Asynchronous maintained checkpoint operation group.
    :type operation: object
    :param str session_id: Session that owns the checkpoint.
    :param str checkpoint_id: Registered sampler checkpoint identifier.
    :return: Complete validated private file descriptors.
    :rtype: tuple
    """
    # pylint: disable=protected-access
    arguments, interval = _checkpoint_download_setup(operation, session_id, checkpoint_id)
    while True:
        request = _request(operation, _build_checkpoint_download_request, arguments, _NO_BODY, {})
        preparation_url = request.url
        response = (
            await operation._client._pipeline.run(request, stream=False, permit_redirects=False, retry_total=0)
        ).http_response
        manifest = _checkpoint_download_result(response, arguments["session_id"], preparation_url)
        if manifest is not None:
            return manifest
        await operation._client._pipeline._transport.sleep(_retry_delay(response, {}, interval))
