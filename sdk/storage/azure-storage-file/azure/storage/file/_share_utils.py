# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
from io import BytesIO

from .models import ShareProperties, DirectoryProperties, FileProperties
from ._generated.models import StorageErrorException
from ._shared.response_handlers import (
    process_storage_error,
    parse_length_from_content_range,
    deserialize_metadata)
from ._shared.upload_chunking import upload_file_chunks


def deserialize_share_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    share_properties = ShareProperties(
        metadata=metadata,
        **headers
    )
    return share_properties


def deserialize_directory_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    directory_properties = DirectoryProperties(
        metadata=metadata,
        **headers
    )
    return directory_properties


def deserialize_file_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    file_properties = FileProperties(
        metadata=metadata,
        **headers
    )
    if 'Content-Range' in headers:
        if 'x-ms-content-md5' in headers:
            file_properties.content_settings.content_md5 = headers['x-ms-content-md5']
        else:
            file_properties.content_settings.content_md5 = None
    return file_properties


def deserialize_file_stream(response, obj, headers):
    file_properties = deserialize_file_properties(response, obj, headers)
    obj.properties = file_properties
    return response.location_mode, obj


def upload_file_helper(
        client,
        stream,
        size,
        metadata,
        content_settings,
        validate_content,
        timeout,
        max_connections,
        file_settings,
        **kwargs):
    try:
        if size is None or size < 0:
            raise ValueError("A content size must be specified for a File.")
        response = client.create_file(
            size,
            content_settings=content_settings,
            metadata=metadata,
            timeout=timeout,
            **kwargs
        )
        if size == 0:
            return response

        return upload_file_chunks(
            file_service=client,
            file_size=size,
            block_size=file_settings.max_range_size,
            stream=stream,
            max_connections=max_connections,
            validate_content=validate_content,
            timeout=timeout,
            **kwargs)
    except StorageErrorException as error:
        process_storage_error(error)
