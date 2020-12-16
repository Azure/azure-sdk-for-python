# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=no-self-use
from azure.core.exceptions import HttpResponseError
from .._deserialize import (
    process_storage_error)
from .._shared.response_handlers import return_response_headers
from .._shared.uploads_async import (
    upload_data_chunks,
    DataLakeFileChunkUploader)


def _any_conditions(modified_access_conditions=None, **kwargs):  # pylint: disable=unused-argument
    return any([
        modified_access_conditions.if_modified_since,
        modified_access_conditions.if_unmodified_since,
        modified_access_conditions.if_none_match,
        modified_access_conditions.if_match
    ])


async def upload_datalake_file(  # pylint: disable=unused-argument
        client=None,
        stream=None,
        length=None,
        overwrite=None,
        validate_content=None,
        max_concurrency=None,
        **kwargs):
    try:
        if length == 0:
            return {}
        properties = kwargs.pop('properties', None)
        umask = kwargs.pop('umask', None)
        permissions = kwargs.pop('permissions', None)
        path_http_headers = kwargs.pop('path_http_headers', None)
        modified_access_conditions = kwargs.pop('modified_access_conditions', None)
        chunk_size = kwargs.pop('chunk_size', 100 * 1024 * 1024)

        if not overwrite:
            # if customers didn't specify access conditions, they cannot flush data to existing file
            if not _any_conditions(modified_access_conditions):
                modified_access_conditions.if_none_match = '*'
            if properties or umask or permissions:
                raise ValueError("metadata, umask and permissions can be set only when overwrite is enabled")

        if overwrite:
            response = await client.create(
                resource='file',
                path_http_headers=path_http_headers,
                properties=properties,
                modified_access_conditions=modified_access_conditions,
                umask=umask,
                permissions=permissions,
                cls=return_response_headers,
                **kwargs)

            # this modified_access_conditions will be applied to flush_data to make sure
            # no other flush between create and the current flush
            modified_access_conditions.if_match = response['etag']
            modified_access_conditions.if_none_match = None
            modified_access_conditions.if_modified_since = None
            modified_access_conditions.if_unmodified_since = None

        await upload_data_chunks(
            service=client,
            uploader_class=DataLakeFileChunkUploader,
            total_size=length,
            chunk_size=chunk_size,
            stream=stream,
            max_concurrency=max_concurrency,
            validate_content=validate_content,
            **kwargs)

        return await client.flush_data(position=length,
                                       path_http_headers=path_http_headers,
                                       modified_access_conditions=modified_access_conditions,
                                       close=True,
                                       cls=return_response_headers,
                                       **kwargs)
    except HttpResponseError as error:
        process_storage_error(error)
