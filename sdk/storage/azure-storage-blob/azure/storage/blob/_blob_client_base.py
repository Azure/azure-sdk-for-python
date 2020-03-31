# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines,no-self-use

from io import BytesIO
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, IO, Iterable, AnyStr, Dict, List, Tuple, cast,
    TYPE_CHECKING
)
try:
    from urllib.parse import urlparse, quote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import quote # type: ignore

import six

from ._shared import encode_base64
from ._shared.base_client import StorageAccountHostsMixin, parse_query
from ._shared.encryption import generate_blob_encryption_data
from ._shared.uploads import IterStreamer
from ._shared.request_handlers import (
    add_metadata_headers, get_length, read_length,
    validate_and_format_range_headers)
from ._shared.response_handlers import return_response_headers
from ._generated import AzureBlobStorage, VERSION
from ._generated.models import ( # pylint: disable=unused-import
    DeleteSnapshotsOptionType,
    BlobHTTPHeaders,
    BlockLookupList,
    AppendPositionAccessConditions,
    SequenceNumberAccessConditions,
    StorageErrorException,
    UserDelegationKey,
    CpkInfo)
from ._serialize import get_modify_conditions, get_source_conditions, get_cpk_scope_info, get_api_version
from ._deserialize import deserialize_blob_stream
from ._models import BlobType, BlobBlock, BlobProperties
from ._lease import get_access_conditions

if TYPE_CHECKING:
    from datetime import datetime
    from ._generated.models import BlockList
    from ._models import (  # pylint: disable=unused-import
        ContainerProperties,
        BlobSasPermissions,
        ContentSettings,
        PremiumPageBlobTier,
        StandardBlobTier,
        SequenceNumberAction
    )

_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION = (
    'The require_encryption flag is set, but encryption is not supported'
    ' for this method.')


class BlobClientBase(StorageAccountHostsMixin):  # pylint: disable=too-many-public-methods
    """A client to interact with a specific blob, although that blob may not yet exist.

    :param str account_url:
        The URI to the storage account. In order to create a client given the full URI to the blob,
        use the :func:`from_blob_url` classmethod.
    :param container_name: The container name for the blob.
    :type container_name: str
    :param blob_name: The name of the blob with which to interact. If specified, this value will override
        a blob value specified in the blob URL.
    :type blob_name: str
    :param str snapshot:
        The optional blob snapshot on which to operate. This can be the snapshot ID string
        or the response returned from :func:`create_snapshot`.
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string, an account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the URL already has a SAS token, specifying an explicit credential will take priority.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is '2019-07-07'.
        Setting to an older version may result in reduced feature compatibility.

        .. versionadded:: 12.2.0

    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    :keyword int max_block_size: The maximum chunk size for uploading a block blob in chunks.
        Defaults to 4*1024*1024, or 4MB.
    :keyword int max_single_put_size: If the blob size is less than max_single_put_size, then the blob will be
        uploaded with only one http PUT request. If the blob size is larger than max_single_put_size,
        the blob will be uploaded in chunks. Defaults to 64*1024*1024, or 64MB.
    :keyword int min_large_block_upload_threshold: The minimum chunk size required to use the memory efficient
        algorithm when uploading a block blob. Defaults to 4*1024*1024+1.
    :keyword bool use_byte_buffer: Use a byte buffer for block blob uploads. Defaults to False.
    :keyword int max_page_size: The maximum chunk size for uploading a page blob. Defaults to 4*1024*1024, or 4MB.
    :keyword int max_single_get_size: The maximum size for a blob to be downloaded in a single call,
        the exceeded part will be downloaded in chunks (could be parallel). Defaults to 32*1024*1024, or 32MB.
    :keyword int max_chunk_get_size: The maximum chunk size used for downloading a blob. Defaults to 4*1024*1024,
        or 4MB.

    .. admonition:: Example:

        .. literalinclude:: ../samples/blob_samples_authentication.py
            :start-after: [START create_blob_client]
            :end-before: [END create_blob_client]
            :language: python
            :dedent: 8
            :caption: Creating the BlobClient from a URL to a public blob (no auth needed).

        .. literalinclude:: ../samples/blob_samples_authentication.py
            :start-after: [START create_blob_client_sas_url]
            :end-before: [END create_blob_client_sas_url]
            :language: python
            :dedent: 8
            :caption: Creating the BlobClient from a SAS URL to a blob.
    """
    def __init__(
            self, account_url,  # type: str
            container_name,  # type: str
            blob_name,  # type: str
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))

        if not (container_name and blob_name):
            raise ValueError("Please specify a container name and blob name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        path_snapshot, sas_token = parse_query(parsed_url.query)

        self.container_name = container_name
        self.blob_name = blob_name
        try:
            self.snapshot = snapshot.snapshot
        except AttributeError:
            if isinstance(snapshot, Dict):
                self.snapshot = snapshot['snapshot']
            else:
                self.snapshot = snapshot or path_snapshot

        self._query_str, credential = self._format_query_string(sas_token, credential, snapshot=self.snapshot)
        super(BlobClientBase, self).__init__(parsed_url, service='blob', credential=credential, **kwargs)
        self._client = AzureBlobStorage(self.url, pipeline=self._pipeline)
        self._client._config.version = get_api_version(kwargs, VERSION)  # pylint: disable=protected-access

    def _format_url(self, hostname):
        container_name = self.container_name
        if isinstance(container_name, six.text_type):
            container_name = container_name.encode('UTF-8')
        return "{}://{}/{}/{}{}".format(
            self.scheme,
            hostname,
            quote(container_name),
            quote(self.blob_name, safe='~'),
            self._query_str)

    def _upload_blob_options(  # pylint:disable=too-many-statements
            self, data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            blob_type=BlobType.BlockBlob,  # type: Union[str, BlobType]
            length=None,  # type: Optional[int]
            metadata=None,  # type: Optional[Dict[str, str]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")
        encryption_options = {
            'required': self.require_encryption,
            'key': self.key_encryption_key,
            'resolver': self.key_resolver_function,
        }
        if self.key_encryption_key is not None:
            cek, iv, encryption_data = generate_blob_encryption_data(self.key_encryption_key)
            encryption_options['cek'] = cek
            encryption_options['vector'] = iv
            encryption_options['data'] = encryption_data

        encoding = kwargs.pop('encoding', 'UTF-8')
        if isinstance(data, six.text_type):
            data = cast(Iterable, data.encode(encoding))
        if length is None:
            length = get_length(data)
        if isinstance(data, bytes):
            data = data[:length]

        if isinstance(data, bytes):
            stream = BytesIO(data)
        elif hasattr(data, 'read'):
            stream = data
        elif hasattr(data, '__iter__'):
            stream = IterStreamer(data, encoding=encoding)
        else:
            raise TypeError("Unsupported data type: {}".format(type(data)))

        validate_content = kwargs.pop('validate_content', False)
        content_settings = kwargs.pop('content_settings', None)
        overwrite = kwargs.pop('overwrite', False)
        max_concurrency = kwargs.pop('max_concurrency', 1)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        kwargs['cpk_info'] = cpk_info

        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        kwargs['lease_access_conditions'] = get_access_conditions(kwargs.pop('lease', None))
        kwargs['modified_access_conditions'] = get_modify_conditions(kwargs)
        kwargs['cpk_scope_info'] = get_cpk_scope_info(kwargs)
        if content_settings:
            kwargs['blob_headers'] = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )
        kwargs['stream'] = stream
        kwargs['length'] = length
        kwargs['overwrite'] = overwrite
        kwargs['headers'] = headers
        kwargs['validate_content'] = validate_content
        kwargs['blob_settings'] = self._config
        kwargs['max_concurrency'] = max_concurrency
        kwargs['encryption_options'] = encryption_options
        if blob_type == BlobType.BlockBlob:
            kwargs['client'] = self._client.block_blob
            kwargs['data'] = data
        elif blob_type == BlobType.PageBlob:
            kwargs['client'] = self._client.page_blob
        elif blob_type == BlobType.AppendBlob:
            if self.require_encryption or (self.key_encryption_key is not None):
                raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
            kwargs['client'] = self._client.append_blob
        else:
            raise ValueError("Unsupported BlobType: {}".format(blob_type))
        return kwargs

    def _download_blob_options(self, offset=None, length=None, **kwargs):
        # type: (Optional[int], Optional[int], **Any) -> Dict[str, Any]
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")
        if length is not None:
            if offset is None:
                raise ValueError("Offset value must not be None if length is set.")
            length = offset + length - 1  # Service actually uses an end-range inclusive index

        validate_content = kwargs.pop('validate_content', False)
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)

        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'clients': self._client,
            'config': self._config,
            'start_range': offset,
            'end_range': length,
            'validate_content': validate_content,
            'encryption_options': {
                'required': self.require_encryption,
                'key': self.key_encryption_key,
                'resolver': self.key_resolver_function},
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_info': cpk_info,
            'cls': deserialize_blob_stream,
            'max_concurrency':kwargs.pop('max_concurrency', 1),
            'encoding': kwargs.pop('encoding', None),
            'timeout': kwargs.pop('timeout', None),
            'name': self.blob_name,
            'container': self.container_name}
        options.update(kwargs)
        return options

    @staticmethod
    def _generic_delete_blob_options(delete_snapshots=False, **kwargs):
        # type: (bool, **Any) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if delete_snapshots:
            delete_snapshots = cast(bool, DeleteSnapshotsOptionType(delete_snapshots))
        options = {
            'timeout': kwargs.pop('timeout', None),
            'delete_snapshots': delete_snapshots or None,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions}
        options.update(kwargs)
        return options

    def _delete_blob_options(self, delete_snapshots=False, **kwargs):
        # type: (bool, **Any) -> Dict[str, Any]
        if self.snapshot and delete_snapshots:
            raise ValueError("The delete_snapshots option cannot be used with a specific snapshot.")
        options = self._generic_delete_blob_options(delete_snapshots, **kwargs)
        options['snapshot'] = self.snapshot
        return options

    def _set_http_headers_options(self, content_settings=None, **kwargs):
        # type: (Optional[ContentSettings], **Any) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        blob_headers = None
        if content_settings:
            blob_headers = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )
        options = {
            'timeout': kwargs.pop('timeout', None),
            'blob_http_headers': blob_headers,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def _set_blob_metadata_options(self, metadata=None, **kwargs):
        # type: (Optional[Dict[str, str]], **Any) -> Dict[str, Any]
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)

        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        options = {
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers,
            'headers': headers}
        options.update(kwargs)
        return options

    def _create_page_blob_options(
            self, size,  # type: int
            content_settings=None,  # type: Optional[ContentSettings]
            metadata=None, # type: Optional[Dict[str, str]]
            premium_page_blob_tier=None,  # type: Optional[Union[str, PremiumPageBlobTier]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        blob_headers = None
        if content_settings:
            blob_headers = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )

        sequence_number = kwargs.pop('sequence_number', None)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        if premium_page_blob_tier:
            if isinstance(premium_page_blob_tier, PremiumPageBlobTier):
                headers['x-ms-access-tier'] = premium_page_blob_tier.value
            else:
                headers['x-ms-access-tier'] = premium_page_blob_tier
        options = {
            'content_length': 0,
            'blob_content_length': size,
            'blob_sequence_number': sequence_number,
            'blob_http_headers': blob_headers,
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers,
            'headers': headers}
        options.update(kwargs)
        return options

    def _create_append_blob_options(self, content_settings=None, metadata=None, **kwargs):
        # type: (Optional[ContentSettings], Optional[Dict[str, str]], **Any) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        blob_headers = None
        if content_settings:
            blob_headers = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )

        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'content_length': 0,
            'blob_http_headers': blob_headers,
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers,
            'headers': headers}
        options.update(kwargs)
        return options

    def _create_snapshot_options(self, metadata=None, **kwargs):
        # type: (Optional[Dict[str, str]], **Any) -> Dict[str, Any]
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers,
            'headers': headers}
        options.update(kwargs)
        return options

    def _start_copy_from_url_options(self, source_url, metadata=None, incremental_copy=False, **kwargs):
        # type: (str, Optional[Dict[str, str]], bool, **Any) -> Dict[str, Any]
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        if 'source_lease' in kwargs:
            source_lease = kwargs.pop('source_lease')
            try:
                headers['x-ms-source-lease-id'] = source_lease.id
            except AttributeError:
                headers['x-ms-source-lease-id'] = source_lease

        tier = kwargs.pop('premium_page_blob_tier', None) or kwargs.pop('standard_blob_tier', None)

        if kwargs.get('requires_sync'):
            headers['x-ms-requires-sync'] = str(kwargs.pop('requires_sync'))

        timeout = kwargs.pop('timeout', None)
        dest_mod_conditions = get_modify_conditions(kwargs)
        options = {
            'copy_source': source_url,
            'timeout': timeout,
            'modified_access_conditions': dest_mod_conditions,
            'headers': headers,
            'cls': return_response_headers,
        }
        if not incremental_copy:
            source_mod_conditions = get_source_conditions(kwargs)
            dest_access_conditions = get_access_conditions(kwargs.pop('destination_lease', None))
            options['source_modified_access_conditions'] = source_mod_conditions
            options['lease_access_conditions'] = dest_access_conditions
            options['tier'] = tier.value if tier else None
        options.update(kwargs)
        return options

    def _abort_copy_options(self, copy_id, **kwargs):
        # type: (Union[str, Dict[str, Any], BlobProperties], **Any) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        if isinstance(copy_id, BlobProperties):
            copy_id = copy_id.copy.id
        else:
            if isinstance(copy_id, Dict):
                copy_id = copy_id['copy_id']
            elif isinstance(copy_id, str):
                pass
        options = {
            'copy_id': copy_id,
            'lease_access_conditions': access_conditions,
            'timeout': kwargs.pop('timeout', None)}
        options.update(kwargs)
        return options

    def _stage_block_options(
            self, block_id,  # type: str
            data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        block_id = encode_base64(str(block_id))
        if isinstance(data, six.text_type):
            data = cast(Iterable, data.encode(kwargs.pop('encoding', 'UTF-8')))
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        if length is None:
            length = get_length(data)
            if length is None:
                length, data = read_length(data)
        if isinstance(data, bytes):
            data = data[:length]

        validate_content = kwargs.pop('validate_content', False)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'block_id': block_id,
            'content_length': length,
            'body': data,
            'transactional_content_md5': None,
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'validate_content': validate_content,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers,
        }
        options.update(kwargs)
        return options

    def _stage_block_from_url_options(
            self, block_id,  # type: str
            source_url,  # type: str
            source_offset=None,  # type: Optional[int]
            source_length=None,  # type: Optional[int]
            source_content_md5=None,  # type: Optional[Union[bytes, bytearray]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if source_length is not None:
            if source_offset is None:
                raise ValueError("Source offset value must not be None if length is set.")
            source_length = source_offset + source_length - 1
        block_id = encode_base64(str(block_id))
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        range_header = None
        if source_offset is not None:
            range_header, _ = validate_and_format_range_headers(source_offset, source_length)

        cpk_scope_info = get_cpk_scope_info(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        options = {
            'block_id': block_id,
            'content_length': 0,
            'source_url': source_url,
            'source_range': range_header,
            'source_content_md5': bytearray(source_content_md5) if source_content_md5 else None,
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers,
        } # type: Dict[str, Any]
        options.update(kwargs)
        return options

    def _get_block_list_result(self, blocks):
        # type: (BlockList) -> Tuple[List[BlobBlock], List[BlobBlock]]
        committed = [] # type: List
        uncommitted = [] # type: List
        if blocks.committed_blocks:
            committed = [BlobBlock._from_generated(b) for b in blocks.committed_blocks]  # pylint: disable=protected-access
        if blocks.uncommitted_blocks:
            uncommitted = [BlobBlock._from_generated(b) for b in blocks.uncommitted_blocks]  # pylint: disable=protected-access
        return committed, uncommitted

    def _commit_block_list_options(
            self, block_list,  # type: List[BlobBlock]
            content_settings=None,  # type: Optional[ContentSettings]
            metadata=None,  # type: Optional[Dict[str, str]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        block_lookup = BlockLookupList(committed=[], uncommitted=[], latest=[])
        for block in block_list:
            try:
                if block.state.value == 'committed':
                    block_lookup.committed.append(encode_base64(str(block.id)))
                elif block.state.value == 'uncommitted':
                    block_lookup.uncommitted.append(encode_base64(str(block.id)))
                else:
                    block_lookup.latest.append(encode_base64(str(block.id)))
            except AttributeError:
                block_lookup.latest.append(encode_base64(str(block)))
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        blob_headers = None
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if content_settings:
            blob_headers = BlobHTTPHeaders(
                blob_cache_control=content_settings.cache_control,
                blob_content_type=content_settings.content_type,
                blob_content_md5=bytearray(content_settings.content_md5) if content_settings.content_md5 else None,
                blob_content_encoding=content_settings.content_encoding,
                blob_content_language=content_settings.content_language,
                blob_content_disposition=content_settings.content_disposition
            )

        validate_content = kwargs.pop('validate_content', False)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        tier = kwargs.pop('standard_blob_tier', None)

        options = {
            'blocks': block_lookup,
            'blob_http_headers': blob_headers,
            'lease_access_conditions': access_conditions,
            'timeout': kwargs.pop('timeout', None),
            'modified_access_conditions': mod_conditions,
            'cls': return_response_headers,
            'validate_content': validate_content,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'tier': tier.value if tier else None,
            'headers': headers
        }
        options.update(kwargs)
        return options

    def _get_page_ranges_options(
            self, offset=None, # type: Optional[int]
            length=None, # type: Optional[int]
            previous_snapshot_diff=None,  # type: Optional[Union[str, Dict[str, Any]]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if length is not None:
            if offset is None:
                raise ValueError("Offset value must not be None if length is set.")
            length = offset + length - 1  # Reformat to an inclusive range index
        page_range, _ = validate_and_format_range_headers(
            offset, length, start_range_required=False, end_range_required=False, align_to_page=True
        )
        options = {
            'snapshot': self.snapshot,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'timeout': kwargs.pop('timeout', None),
            'range': page_range}
        if previous_snapshot_diff:
            try:
                options['prevsnapshot'] = previous_snapshot_diff.snapshot
            except AttributeError:
                if isinstance(previous_snapshot_diff, Dict):
                    options['prevsnapshot'] = previous_snapshot_diff['snapshot']
                else:
                    options['prevsnapshot'] = previous_snapshot_diff

        options.update(kwargs)
        return options

    def _set_sequence_number_options(self, sequence_number_action, sequence_number=None, **kwargs):
        # type: (Union[str, SequenceNumberAction], Optional[str], **Any) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if sequence_number_action is None:
            raise ValueError("A sequence number action must be specified")
        options = {
            'sequence_number_action': sequence_number_action,
            'timeout': kwargs.pop('timeout', None),
            'blob_sequence_number': sequence_number,
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def _resize_blob_options(self, size, **kwargs):
        # type: (int, **Any) -> Dict[str, Any]
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        if size is None:
            raise ValueError("A content length must be specified for a Page Blob.")

        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        options = {
            'blob_content_length': size,
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_info': cpk_info,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def _upload_page_options(
            self, page,  # type: bytes
            offset,  # type: int
            length,  # type: int
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if isinstance(page, six.text_type):
            page = page.encode(kwargs.pop('encoding', 'UTF-8'))
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        if offset is None or offset % 512 != 0:
            raise ValueError("offset must be an integer that aligns with 512 page size")
        if length is None or length % 512 != 0:
            raise ValueError("length must be an integer that aligns with 512 page size")
        end_range = offset + length - 1  # Reformat to an inclusive range index
        content_range = 'bytes={0}-{1}'.format(offset, end_range)
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        seq_conditions = SequenceNumberAccessConditions(
            if_sequence_number_less_than_or_equal_to=kwargs.pop('if_sequence_number_lte', None),
            if_sequence_number_less_than=kwargs.pop('if_sequence_number_lt', None),
            if_sequence_number_equal_to=kwargs.pop('if_sequence_number_eq', None)
        )
        mod_conditions = get_modify_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        validate_content = kwargs.pop('validate_content', False)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        options = {
            'body': page[:length],
            'content_length': length,
            'transactional_content_md5': None,
            'timeout': kwargs.pop('timeout', None),
            'range': content_range,
            'lease_access_conditions': access_conditions,
            'sequence_number_access_conditions': seq_conditions,
            'modified_access_conditions': mod_conditions,
            'validate_content': validate_content,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def _upload_pages_from_url_options(
            self, source_url,  # type: str
            offset,  # type: int
            length,  # type: int
            source_offset,  # type: int
            **kwargs
    ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        # TODO: extract the code to a method format_range
        if offset is None or offset % 512 != 0:
            raise ValueError("offset must be an integer that aligns with 512 page size")
        if length is None or length % 512 != 0:
            raise ValueError("length must be an integer that aligns with 512 page size")
        if source_offset is None or offset % 512 != 0:
            raise ValueError("source_offset must be an integer that aligns with 512 page size")

        # Format range
        end_range = offset + length - 1
        destination_range = 'bytes={0}-{1}'.format(offset, end_range)
        source_range = 'bytes={0}-{1}'.format(source_offset, source_offset + length - 1)  # should subtract 1 here?

        seq_conditions = SequenceNumberAccessConditions(
            if_sequence_number_less_than_or_equal_to=kwargs.pop('if_sequence_number_lte', None),
            if_sequence_number_less_than=kwargs.pop('if_sequence_number_lt', None),
            if_sequence_number_equal_to=kwargs.pop('if_sequence_number_eq', None)
        )
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        source_mod_conditions = get_source_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        source_content_md5 = kwargs.pop('source_content_md5', None)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'source_url': source_url,
            'content_length': 0,
            'source_range': source_range,
            'range': destination_range,
            'source_content_md5': bytearray(source_content_md5) if source_content_md5 else None,
            'timeout': kwargs.pop('timeout', None),
            'lease_access_conditions': access_conditions,
            'sequence_number_access_conditions': seq_conditions,
            'modified_access_conditions': mod_conditions,
            'source_modified_access_conditions': source_mod_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def _clear_page_options(self, offset, length, **kwargs):
        # type: (int, int, **Any) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        seq_conditions = SequenceNumberAccessConditions(
            if_sequence_number_less_than_or_equal_to=kwargs.pop('if_sequence_number_lte', None),
            if_sequence_number_less_than=kwargs.pop('if_sequence_number_lt', None),
            if_sequence_number_equal_to=kwargs.pop('if_sequence_number_eq', None)
        )
        mod_conditions = get_modify_conditions(kwargs)
        if offset is None or offset % 512 != 0:
            raise ValueError("offset must be an integer that aligns with 512 page size")
        if length is None or length % 512 != 0:
            raise ValueError("length must be an integer that aligns with 512 page size")
        end_range = length + offset - 1  # Reformat to an inclusive range index
        content_range = 'bytes={0}-{1}'.format(offset, end_range)

        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'content_length': 0,
            'timeout': kwargs.pop('timeout', None),
            'range': content_range,
            'lease_access_conditions': access_conditions,
            'sequence_number_access_conditions': seq_conditions,
            'modified_access_conditions': mod_conditions,
            'cpk_info': cpk_info,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def _append_block_options(
            self, data,  # type: Union[AnyStr, Iterable[AnyStr], IO[AnyStr]]
            length=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)

        if isinstance(data, six.text_type):
            data = cast(Iterable, data.encode(kwargs.pop('encoding', 'UTF-8')))
        if length is None:
            length = get_length(data)
            if length is None:
                length, data = read_length(data)
        if length == 0:
            return {}
        if isinstance(data, bytes):
            data = data[:length]

        appendpos_condition = kwargs.pop('appendpos_condition', None)
        maxsize_condition = kwargs.pop('maxsize_condition', None)
        validate_content = kwargs.pop('validate_content', False)
        append_conditions = None
        if maxsize_condition or appendpos_condition is not None:
            append_conditions = AppendPositionAccessConditions(
                max_size=maxsize_condition,
                append_position=appendpos_condition
            )
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)
        options = {
            'body': data,
            'content_length': length,
            'timeout': kwargs.pop('timeout', None),
            'transactional_content_md5': None,
            'lease_access_conditions': access_conditions,
            'append_position_access_conditions': append_conditions,
            'modified_access_conditions': mod_conditions,
            'validate_content': validate_content,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers}
        options.update(kwargs)
        return options

    def _append_block_from_url_options(
            self, copy_source_url,  # type: str
            source_offset=None,  # type: Optional[int]
            source_length=None,  # type: Optional[int]
            **kwargs
    ):
        # type: (...) -> Dict[str, Any]
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        # Format based on whether length is present
        source_range = None
        # If end range is provided, start range must be provided
        if source_length is not None:
            if source_offset is None:
                raise ValueError("source_offset should also be specified if source_length is specified")
            end_range = source_offset + source_length - 1
            source_range = 'bytes={0}-{1}'.format(source_offset, end_range)
        elif source_length is None and source_offset is not None:
            source_range = "bytes={0}-".format(source_offset)

        appendpos_condition = kwargs.pop('appendpos_condition', None)
        maxsize_condition = kwargs.pop('maxsize_condition', None)
        source_content_md5 = kwargs.pop('source_content_md5', None)
        append_conditions = None
        if maxsize_condition or appendpos_condition is not None:
            append_conditions = AppendPositionAccessConditions(
                max_size=maxsize_condition,
                append_position=appendpos_condition
            )
        access_conditions = get_access_conditions(kwargs.pop('lease', None))
        mod_conditions = get_modify_conditions(kwargs)
        source_mod_conditions = get_source_conditions(kwargs)
        cpk_scope_info = get_cpk_scope_info(kwargs)
        cpk = kwargs.pop('cpk', None)
        cpk_info = None
        if cpk:
            if self.scheme.lower() != 'https':
                raise ValueError("Customer provided encryption key must be used over HTTPS.")
            cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                               encryption_algorithm=cpk.algorithm)

        options = {
            'source_url': copy_source_url,
            'content_length': 0,
            'source_range': source_range,
            'source_content_md5': source_content_md5,
            'transactional_content_md5': None,
            'lease_access_conditions': access_conditions,
            'append_position_access_conditions': append_conditions,
            'modified_access_conditions': mod_conditions,
            'source_modified_access_conditions': source_mod_conditions,
            'cpk_scope_info': cpk_scope_info,
            'cpk_info': cpk_info,
            'cls': return_response_headers,
            'timeout': kwargs.pop('timeout', None)}
        options.update(kwargs)
        return options
