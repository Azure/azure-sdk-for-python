# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, cast, Dict, IO, Optional, TYPE_CHECKING

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError

from ._deserialize import process_storage_error
from ._shared.response_handlers import return_response_headers
from ._shared.uploads import DataLakeFileChunkUploader, upload_data_chunks, upload_substream_blocks

if TYPE_CHECKING:
    from ._generated.operations import PathOperations
    from ._shared.models import StorageConfiguration


def _any_conditions(**kwargs):
    return any(
        [
            kwargs.get("if_modified_since"),
            kwargs.get("if_unmodified_since"),
            kwargs.get("etag"),
            kwargs.get("match_condition"),
        ]
    )


def upload_datalake_file(  # pylint: disable=too-many-locals
    client: "PathOperations",
    stream: IO,
    validate_content: bool,
    max_concurrency: int,
    file_settings: "StorageConfiguration",
    length: Optional[int] = None,
    overwrite: Optional[bool] = False,
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

        # Extract and pop parameters from kwargs
        cache_control = kwargs.pop("cache_control", None)
        content_type = kwargs.pop("content_type", None)
        content_encoding = kwargs.pop("content_encoding", None)
        content_language = kwargs.pop("content_language", None)
        content_disposition = kwargs.pop("content_disposition", None)
        content_md5 = kwargs.pop("content_md5", None)
        if_modified_since = kwargs.pop("if_modified_since", None)
        if_unmodified_since = kwargs.pop("if_unmodified_since", None)
        etag = kwargs.pop("etag", None)
        match_condition = kwargs.pop("match_condition", None)

        if not overwrite:
            # if customers didn't specify access conditions, they cannot flush data to existing file
            if not _any_conditions(
                if_modified_since=if_modified_since, if_unmodified_since=if_unmodified_since,
                etag=etag, match_condition=match_condition
            ):
                match_condition = MatchConditions.IfMissing
            if properties or umask or permissions:
                raise ValueError("metadata, umask and permissions can be set only when overwrite is enabled")

        if overwrite:
            response = cast(
                Dict[str, Any],
                client.create(
                    resource="file",
                    properties=properties,
                    umask=umask,
                    permissions=permissions,
                    encryption_context=encryption_context,
                    cache_control=cache_control,
                    content_type=content_type,
                    content_encoding=content_encoding,
                    content_language=content_language,
                    content_disposition=content_disposition,
                    if_modified_since=if_modified_since,
                    if_unmodified_since=if_unmodified_since,
                    etag=etag,
                    match_condition=match_condition,
                    cls=return_response_headers,
                    **kwargs
                ),
            )

            # Set etag-based conditions to ensure no other flush between create and the current flush
            etag = response["etag"]
            match_condition = MatchConditions.IfNotModified

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
            upload_data_chunks(
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
            upload_substream_blocks(
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
            client.flush_data(
                position=length,
                close=True,
                cache_control=cache_control,
                content_type=content_type,
                content_encoding=content_encoding,
                content_language=content_language,
                content_disposition=content_disposition,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                etag=etag,
                match_condition=match_condition,
                content_md5=content_md5,
                cls=return_response_headers,
                **kwargs
            ),
        )
    except HttpResponseError as error:
        process_storage_error(error)
