# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, cast, Dict, IO, Optional, TYPE_CHECKING

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError

from .._deserialize import process_storage_error
from .._shared.response_handlers import return_response_headers
from .._shared.uploads_async import DataLakeFileChunkUploader, upload_data_chunks, upload_substream_blocks

if TYPE_CHECKING:
    from .._generated.aio.operations import PathOperations
    from .._shared.models import StorageConfiguration


def _any_conditions(**kwargs):
    return any(
        [
            kwargs.get("if_modified_since"),
            kwargs.get("if_unmodified_since"),
            kwargs.get("etag"),
            kwargs.get("match_condition"),
        ]
    )


async def upload_datalake_file(
    client: "PathOperations",
    stream: IO,
    validate_content: bool,
    max_concurrency: int,
    file_settings: "StorageConfiguration",
    length: Optional[int] = None,
    overwrite: Optional[bool] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    try:
        if length == 0:
            return {}
        properties = kwargs.pop("properties", None)
        umask = kwargs.pop("umask", None)
        permissions = kwargs.pop("permissions", None)
        chunk_size = kwargs.pop("chunk_size", 100 * 1024 * 1024)
        encryption_context = kwargs.pop("encryption_context", None)
        progress_hook = kwargs.pop("progress_hook", None)

        # Extract the flat access condition params from kwargs
        access_kwargs: Dict[str, Any] = {}
        for key in ("if_modified_since", "if_unmodified_since", "etag", "match_condition"):
            val = kwargs.pop(key, None)
            if val is not None:
                access_kwargs[key] = val

        # Extract path HTTP headers from kwargs
        path_http_header_kwargs: Dict[str, Any] = {}
        for key in (
            "cache_control",
            "content_type",
            "content_md5",
            "content_encoding",
            "content_language",
            "content_disposition",
        ):
            val = kwargs.pop(key, None)
            if val is not None:
                path_http_header_kwargs[key] = val

        if not overwrite:
            # if customers didn't specify access conditions, they cannot flush data to existing file
            if not _any_conditions(**access_kwargs):
                access_kwargs["match_condition"] = MatchConditions.IfMissing
            if properties or umask or permissions:
                raise ValueError("metadata, umask and permissions can be set only when overwrite is enabled")

        if overwrite:
            response = cast(
                Dict[str, Any],
                await client.create(
                    resource="file",
                    properties=properties,
                    umask=umask,
                    permissions=permissions,
                    encryption_context=encryption_context,
                    cls=return_response_headers,
                    **path_http_header_kwargs,
                    **access_kwargs,
                    **kwargs
                ),
            )

            # Set etag-based conditions to ensure no other flush between create and the current flush
            access_kwargs = {
                "etag": response["etag"],
                "match_condition": MatchConditions.IfNotModified,
            }

        use_original_upload_path = (
            file_settings.use_byte_buffer
            or validate_content
            or chunk_size < file_settings.min_large_chunk_upload_threshold
            or hasattr(stream, "seekable")
            and not stream.seekable()
            or not hasattr(stream, "seek")
            or not hasattr(stream, "tell")
        )

        if use_original_upload_path:
            await upload_data_chunks(
                service=client,
                uploader_class=DataLakeFileChunkUploader,
                total_size=length,
                chunk_size=chunk_size,
                stream=stream,
                max_concurrency=max_concurrency,
                validate_content=validate_content,
                progress_hook=progress_hook,
                **kwargs
            )
        else:
            await upload_substream_blocks(
                service=client,
                uploader_class=DataLakeFileChunkUploader,
                total_size=length,
                chunk_size=chunk_size,
                max_concurrency=max_concurrency,
                stream=stream,
                validate_content=validate_content,
                progress_hook=progress_hook,
                **kwargs
            )

        return cast(
            Dict[str, Any],
            await client.flush_data(
                position=length,
                close=True,
                cls=return_response_headers,
                **path_http_header_kwargs,
                **access_kwargs,
                **kwargs
            ),
        )
    except HttpResponseError as error:
        process_storage_error(error)
