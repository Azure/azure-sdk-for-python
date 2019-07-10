# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=no-self-use

import sys
from io import SEEK_SET, UnsupportedOperation
from typing import Optional, Union, Any, TypeVar, TYPE_CHECKING # pylint: disable=unused-import

import six
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError

from ._shared.request_handlers import validate_and_format_range_headers
from ._shared.response_handlers import (
    process_storage_error,
    parse_length_from_content_range,
    deserialize_metadata,
    return_response_headers)
from ._shared.models import StorageErrorCode, ModifiedAccessConditions
from ._shared.upload_chunking import (
    upload_blob_chunks,
    upload_blob_substream_blocks,
    BlockBlobChunkUploader,
    PageBlobChunkUploader,
    AppendBlobChunkUploader)
from ._shared.encryption import generate_blob_encryption_data, encrypt_blob
from ._generated.models import (
    StorageErrorException,
    BlockLookupList,
    AppendPositionAccessConditions,
    LeaseAccessConditions,
    SequenceNumberAccessConditions
)
from .models import BlobProperties, ContainerProperties

if TYPE_CHECKING:
    from datetime import datetime # pylint: disable=unused-import
    LeaseClient = TypeVar("LeaseClient")

_LARGE_BLOB_UPLOAD_MAX_READ_BUFFER_SIZE = 4 * 1024 * 1024
_ERROR_VALUE_SHOULD_BE_SEEKABLE_STREAM = '{0} should be a seekable file-like/io.IOBase type stream object.'


def _convert_mod_error(error):
    message = error.message.replace(
        "The condition specified using HTTP conditional header(s) is not met.",
        "The specified blob already exists.")
    message = message.replace("ConditionNotMet", "BlobAlreadyExists")
    overwrite_error = ResourceExistsError(
        message=message,
        response=error.response,
        error=error)
    overwrite_error.error_code = StorageErrorCode.blob_already_exists
    raise overwrite_error


def get_access_conditions(lease):
    # type: (Optional[Union[LeaseClient, str]]) -> Union[LeaseAccessConditions, None]
    try:
        lease_id = lease.id # type: ignore
    except AttributeError:
        lease_id = lease # type: ignore
    return LeaseAccessConditions(lease_id=lease_id) if lease_id else None


def get_sequence_conditions(
        if_sequence_number_lte=None, # type: Optional[int]
        if_sequence_number_lt=None, # type: Optional[int]
        if_sequence_number_eq=None, # type: Optional[int]
    ):
    # type: (...) -> Union[SequenceNumberAccessConditions, None]
    if any([if_sequence_number_lte, if_sequence_number_lt, if_sequence_number_eq]):
        return SequenceNumberAccessConditions(
            if_sequence_number_less_than_or_equal_to=if_sequence_number_lte,
            if_sequence_number_less_than=if_sequence_number_lt,
            if_sequence_number_equal_to=if_sequence_number_eq
        )
    return None


def get_modification_conditions(
        if_modified_since=None,  # type: Optional[datetime]
        if_unmodified_since=None,  # type: Optional[datetime]
        if_match=None,  # type: Optional[str]
        if_none_match=None  # type: Optional[str]
    ):
    # type: (...) -> Union[ModifiedAccessConditions, None]
    if any([if_modified_since, if_unmodified_since, if_match, if_none_match]):
        return ModifiedAccessConditions(
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match
        )
    return ModifiedAccessConditions()


def upload_block_blob(  # pylint: disable=too-many-locals
        client,
        data,
        stream,
        length,
        overwrite,
        headers,
        blob_headers,
        access_conditions,
        mod_conditions,
        validate_content,
        timeout,
        max_connections,
        blob_settings,
        require_encryption,
        key_encryption_key,
        **kwargs):
    try:
        overwrite_mod_conditions = None
        if not overwrite:
            overwrite_mod_conditions = get_modification_conditions(if_none_match='*')
        adjusted_count = length
        if (key_encryption_key is not None) and (adjusted_count is not None):
            adjusted_count += (16 - (length % 16))

        # Do single put if the size is smaller than config.max_single_put_size
        if adjusted_count is not None and (adjusted_count < blob_settings.max_single_put_size):
            try:
                data = data.read(length)
                if not isinstance(data, six.binary_type):
                    raise TypeError('Blob data should be of type bytes.')
            except AttributeError:
                pass
            if key_encryption_key:
                encryption_data, data = encrypt_blob(data, key_encryption_key)
                headers['x-ms-meta-encryptiondata'] = encryption_data
            return client.upload(
                data,
                content_length=adjusted_count,
                timeout=timeout,
                blob_http_headers=blob_headers,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions or overwrite_mod_conditions,
                headers=headers,
                cls=return_response_headers,
                validate_content=validate_content,
                data_stream_total=adjusted_count,
                upload_stream_current=0,
                **kwargs)

        cek, iv, encryption_data = None, None, None
        use_original_upload_path = blob_settings.use_byte_buffer or \
            validate_content or require_encryption or \
            blob_settings.max_block_size < blob_settings.min_large_block_upload_threshold or \
            hasattr(stream, 'seekable') and not stream.seekable() or \
            not hasattr(stream, 'seek') or not hasattr(stream, 'tell')

        if use_original_upload_path:
            if key_encryption_key:
                cek, iv, encryption_data = generate_blob_encryption_data(key_encryption_key)
                headers['x-ms-meta-encryptiondata'] = encryption_data
            block_ids = upload_blob_chunks(
                blob_service=client,
                blob_size=length,
                block_size=blob_settings.max_block_size,
                stream=stream,
                max_connections=max_connections,
                validate_content=validate_content,
                access_conditions=access_conditions,
                uploader_class=BlockBlobChunkUploader,
                timeout=timeout,
                content_encryption_key=cek,
                initialization_vector=iv,
                **kwargs
            )
        else:
            block_ids = upload_blob_substream_blocks(
                blob_service=client,
                blob_size=length,
                block_size=blob_settings.max_block_size,
                stream=stream,
                max_connections=max_connections,
                validate_content=validate_content,
                access_conditions=access_conditions,
                uploader_class=BlockBlobChunkUploader,
                timeout=timeout,
                **kwargs
            )

        block_lookup = BlockLookupList(committed=[], uncommitted=[], latest=[])
        block_lookup.latest = block_ids
        return client.commit_block_list(
            block_lookup,
            blob_http_headers=blob_headers,
            lease_access_conditions=access_conditions,
            timeout=timeout,
            modified_access_conditions=mod_conditions or overwrite_mod_conditions,
            cls=return_response_headers,
            validate_content=validate_content,
            headers=headers,
            **kwargs)
    except StorageErrorException as error:
        try:
            process_storage_error(error)
        except ResourceModifiedError as mod_error:
            if overwrite_mod_conditions:
                _convert_mod_error(mod_error)
            raise


def upload_page_blob(
        client,
        stream,
        length,
        overwrite,
        headers,
        blob_headers,
        access_conditions,
        mod_conditions,
        validate_content,
        premium_page_blob_tier,
        timeout,
        max_connections,
        blob_settings,
        cek,
        iv,
        encryption_data,
        **kwargs):
    try:
        overwrite_mod_conditions = None
        if not overwrite:
            overwrite_mod_conditions = get_modification_conditions(if_none_match='*')
        if length is None or length < 0:
            raise ValueError("A content length must be specified for a Page Blob.")
        if length % 512 != 0:
            raise ValueError("Invalid page blob size: {0}. "
                             "The size must be aligned to a 512-byte boundary.".format(length))
        if premium_page_blob_tier:
            try:
                headers['x-ms-access-tier'] = premium_page_blob_tier.value
            except AttributeError:
                headers['x-ms-access-tier'] = premium_page_blob_tier
        if encryption_data is not None:
            headers['x-ms-meta-encryptiondata'] = encryption_data
        response = client.create(
            content_length=0,
            blob_content_length=length,
            blob_sequence_number=None,
            blob_http_headers=blob_headers,
            timeout=timeout,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions or overwrite_mod_conditions,
            cls=return_response_headers,
            headers=headers,
            **kwargs)
        if length == 0:
            return response

        mod_conditions = get_modification_conditions(if_match=response['etag'])
        return upload_blob_chunks(
            blob_service=client,
            blob_size=length,
            block_size=blob_settings.max_page_size,
            stream=stream,
            max_connections=max_connections,
            validate_content=validate_content,
            access_conditions=access_conditions,
            uploader_class=PageBlobChunkUploader,
            modified_access_conditions=mod_conditions,
            timeout=timeout,
            content_encryption_key=cek,
            initialization_vector=iv,
            **kwargs)
    except StorageErrorException as error:
        try:
            process_storage_error(error)
        except ResourceModifiedError as mod_error:
            if overwrite_mod_conditions:
                _convert_mod_error(mod_error)
            raise


def _create_append_blob(
        client,
        blob_headers,
        timeout,
        access_conditions,
        mod_conditions,
        headers,
        **kwargs):
    created = client.create(
        content_length=0,
        blob_http_headers=blob_headers,
        timeout=timeout,
        lease_access_conditions=access_conditions,
        modified_access_conditions=mod_conditions,
        cls=return_response_headers,
        headers=headers,
        **kwargs)
    get_modification_conditions(if_match=created['etag'])  # TODO: Not working...


def upload_append_blob(
        client,
        stream,
        length,
        overwrite,
        headers,
        blob_headers,
        access_conditions,
        mod_conditions,
        maxsize_condition,
        validate_content,
        timeout,
        max_connections,
        blob_settings,
        **kwargs
    ):
    try:
        if length == 0:
            return {}
        append_conditions = AppendPositionAccessConditions(
            max_size=maxsize_condition,
            append_position=None)
        try:
            if overwrite:
                _create_append_blob(
                    client,
                    blob_headers,
                    timeout,
                    access_conditions,
                    mod_conditions,
                    headers,
                    **kwargs)
            return upload_blob_chunks(
                blob_service=client,
                blob_size=length,
                block_size=blob_settings.max_block_size,
                stream=stream,
                append_conditions=append_conditions,
                max_connections=max_connections,
                validate_content=validate_content,
                access_conditions=access_conditions,
                uploader_class=AppendBlobChunkUploader,
                modified_access_conditions=mod_conditions,
                timeout=timeout,
                **kwargs)
        except StorageErrorException as error:
            if error.response.status_code != 404:
                raise
            # rewind the request body if it is a stream
            if hasattr(stream, 'read'):
                try:
                    # attempt to rewind the body to the initial position
                    stream.seek(0, SEEK_SET)
                except UnsupportedOperation:
                    # if body is not seekable, then retry would not work
                    raise error
            _create_append_blob(
                client,
                blob_headers,
                timeout,
                access_conditions,
                mod_conditions,
                headers,
                **kwargs)
            return upload_blob_chunks(
                blob_service=client,
                blob_size=length,
                block_size=blob_settings.max_block_size,
                stream=stream,
                append_conditions=append_conditions,
                max_connections=max_connections,
                validate_content=validate_content,
                access_conditions=access_conditions,
                uploader_class=AppendBlobChunkUploader,
                modified_access_conditions=mod_conditions,
                timeout=timeout,
                **kwargs)
    except StorageErrorException as error:
        process_storage_error(error)


def deserialize_blob_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    blob_properties = BlobProperties(
        metadata=metadata,
        **headers
    )
    if 'Content-Range' in headers:
        if 'x-ms-blob-content-md5' in headers:
            blob_properties.content_settings.content_md5 = headers['x-ms-blob-content-md5']
        else:
            blob_properties.content_settings.content_md5 = None
    return blob_properties


def deserialize_blob_stream(response, obj, headers):
    blob_properties = deserialize_blob_properties(response, obj, headers)
    obj.properties = blob_properties
    return response.location_mode, obj


def deserialize_container_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    container_properties = ContainerProperties(
        metadata=metadata,
        **headers
    )
    return container_properties
