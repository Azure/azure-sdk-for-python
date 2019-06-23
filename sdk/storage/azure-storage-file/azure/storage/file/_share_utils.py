# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .models import ShareProperties, DirectoryProperties, FileProperty
from ._shared.utils import return_response_headers
from ._upload_chunking import _upload_file_chunks
from ._generated.models import StorageErrorException
from ._shared.utils import process_storage_error


def deserialize_metadata(response, obj, headers):
    raw_metadata = {k: v for k, v in response.headers.items() if k.startswith("x-ms-meta-")}
    return {k[10:]: v for k, v in raw_metadata.items()}

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
    file_properties = FileProperty(
        metadata=metadata,
        **headers
    )
    return file_properties

def upload_file_helper(
        client,
        share_name,
        directory_name,
        file_name,
        stream,
        size,
        headers,
        file_http_headers,
        validate_content,
        timeout,
        max_connections,
        file_settings,
        encryption_data,
        **kwargs):
    try:
        if size is None or size < 0:
            raise ValueError("A content size must be specified for a File.")
        if size % 512 != 0:
            raise ValueError("Invalidfile size: {0}. "
                             "The size must be aligned to a 512-byte boundary.".format(size))
        if encryption_data is not None:
            headers['x-ms-meta-encryptiondata'] = encryption_data
        response = client.create(
                file_content_length=size,
                timeout=timeout,
                file_http_headers=file_http_headers,
                headers=headers,
                cls=return_response_headers,
                **kwargs)
        if size == 0:
            return response

        return _upload_file_chunks(
            file_service=client,
            file_size=size,
            share_name=share_name,
            directory_name=directory_name,
            file_name=file_name,
            block_size=file_settings.max_page_size,
            stream=stream,
            max_connections=max_connections,
            validate_content=validate_content,
            timeout=timeout,
            **kwargs)
    except StorageErrorException as error:
        process_storage_error(error)

class StorageStreamDownloader(object):  # pylint: disable=too-many-instance-attributes

    def __init__(
            self, name, share_name, directory_name, service, config, length, validate_content,
            timeout, require_encryption, key_encryption_key, key_resolver_function, **kwargs
    ):
        pass