# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines

from io import BytesIO
from typing import (
    Any, AnyStr, AsyncGenerator, AsyncIterable, cast,
    Dict, IO, Iterable, List, Optional, Tuple, Union,
    TYPE_CHECKING
)
from urllib.parse import quote, unquote, urlparse

from ._deserialize import deserialize_blob_stream
from ._encryption import modify_user_agent_for_encryption, _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION
from ._generated.models import (
    AppendPositionAccessConditions,
    BlobHTTPHeaders,
    BlockList,
    BlockLookupList,
    CpkInfo,
    DeleteSnapshotsOptionType,
    QueryRequest,
    SequenceNumberAccessConditions
)
from ._models import (
    BlobBlock,
    BlobProperties,
    BlobType,
    DelimitedJsonDialect,
    DelimitedTextDialect,
    PremiumPageBlobTier,
    QuickQueryDialect
)
from ._serialize import (
    get_access_conditions,
    get_cpk_scope_info,
    get_modify_conditions,
    get_source_conditions,
    serialize_blob_tags_header,
    serialize_blob_tags,
    serialize_query_format
)
from ._shared import encode_base64
from ._shared.base_client import parse_query
from ._shared.request_handlers import (
    add_metadata_headers,
    get_length,
    read_length,
    validate_and_format_range_headers
)
from ._shared.response_handlers import return_headers_and_deserialized, return_response_headers
from ._shared.uploads import IterStreamer
from ._shared.uploads_async import AsyncIterStreamer
from ._upload_helpers import _any_conditions

if TYPE_CHECKING:
    from urllib.parse import ParseResult
    from ._generated import AzureBlobStorage
    from ._models import ContentSettings
    from ._shared.models import StorageConfiguration


def _parse_url(
    account_url: str,
    container_name: str,
    blob_name: str
) -> Tuple["ParseResult", Optional[str], Optional[str]]:
    """Performs initial input validation and returns the parsed URL, SAS token, and path snapshot.

    :param str account_url:
        The URL to the storage account.
    :param str container_name:
        The name of the container.
    :param str blob_name:
        The name of the blob.
    :returns: The parsed URL, SAS token, and path snapshot.
    :rtype: Tuple[ParseResult, Optional[str], Optional[str]]
    """
    try:
        if not account_url.lower().startswith('http'):
            account_url = "https://" + account_url
    except AttributeError as exc:
        raise ValueError("Account URL must be a string.") from exc
    parsed_url = urlparse(account_url.rstrip('/'))

    if not (container_name and blob_name):
        raise ValueError("Please specify a container name and blob name.")
    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {account_url}")

    path_snapshot, sas_token = parse_query(parsed_url.query)

    return parsed_url, sas_token, path_snapshot

def _format_url(container_name: Union[bytes, str], scheme: str, blob_name: str, query_str: str, hostname: str) -> str:
    """Format the endpoint URL according to the current location mode hostname.

    :param Union[bytes, str] container_name:
        The name of the container.
    :param str scheme:
        The scheme for the current location mode hostname.
    :param str blob_name:
        The name of the blob.
    :param str query_str:
        The query string of the endpoint URL being formatted.
    :param str hostname:
        The current location mode hostname.
    :returns: The formatted endpoint URL according to the specified location mode hostname.
    :rtype: str
    """
    if isinstance(container_name, str):
        container_name = container_name.encode('UTF-8')
    return f"{scheme}://{hostname}/{quote(container_name)}/{quote(blob_name, safe='~/')}{query_str}"

def _encode_source_url(source_url: str) -> str:
    """Encodes the source URL.

    :param str source_url:
        The source_url to be encoded.
    :returns: The encoded source URL.
    :rtype: str
    """
    parsed_source_url = urlparse(source_url)
    source_scheme = parsed_source_url.scheme
    source_hostname = parsed_source_url.netloc.rstrip('/')
    source_path = unquote(parsed_source_url.path)
    source_query = parsed_source_url.query
    result = [f"{source_scheme}://{source_hostname}{quote(source_path, safe='~/')}"]
    if source_query:
        result.append(source_query)
    return '?'.join(result)

def _upload_blob_options(  # pylint:disable=too-many-statements
    data: Union[bytes, str, Iterable[AnyStr], AsyncIterable[AnyStr], IO[AnyStr]],
    blob_type: Union[str, BlobType],
    length: Optional[int],
    metadata: Optional[Dict[str, str]],
    encryption_options: Dict[str, Any],
    config: "StorageConfiguration",
    sdk_moniker: str,
    client: "AzureBlobStorage",
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for an upload blob operation.

    :param data:
        The blob data to be uploaded.
    :paramtype data: Union[bytes, str, Iterable[AnyStr], AsyncIterable[AnyStr], IO[AnyStr]]
    :param Union[str, BlobType] blob_type:
        The type of the blob. This can be either BlockBlob, PageBlob or AppendBlob. The default value is BlockBlob.
    :param Optional[int] length:
        Number of bytes to read from the stream. This is optional, but should be supplied for optimal performance.
    :param Optional[Dict[str, str]] metadata:
        Name-value pairs associated with the blob as metadata.
    :param Dict[str, Any] encryption_options:
        The options for encryption, if enabled.
    :param StorageConfiguration config:
        The Storage configuration options.
    :param str sdk_moniker:
        The string representing the SDK package version.
    :param AzureBlobStorage client:
        The generated Blob Storage client.
    :returns: A dictionary containing the upload blob options.
    :rtype: Dict[str, Any]
    """
    encoding = kwargs.pop('encoding', 'UTF-8')
    if isinstance(data, str):
        data = data.encode(encoding)
    if length is None:
        length = get_length(data)
    if isinstance(data, bytes):
        data = data[:length]

    stream: Optional[Any] = None
    if isinstance(data, bytes):
        stream = BytesIO(data)
    elif hasattr(data, 'read'):
        stream = data
    elif hasattr(data, '__iter__') and not isinstance(data, (list, tuple, set, dict)):
        stream = IterStreamer(data, encoding=encoding)
    elif hasattr(data, '__aiter__'):
        stream = AsyncIterStreamer(cast(AsyncGenerator, data), encoding=encoding)
    else:
        raise TypeError(f"Unsupported data type: {type(data)}")

    validate_content = kwargs.pop('validate_content', False)
    content_settings = kwargs.pop('content_settings', None)
    overwrite = kwargs.pop('overwrite', False)
    max_concurrency = kwargs.pop('max_concurrency', 1)
    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
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
            blob_content_md5=content_settings.content_md5,
            blob_content_encoding=content_settings.content_encoding,
            blob_content_language=content_settings.content_language,
            blob_content_disposition=content_settings.content_disposition
        )
    kwargs['blob_tags_string'] = serialize_blob_tags_header(kwargs.pop('tags', None))
    kwargs['stream'] = stream
    kwargs['length'] = length
    kwargs['overwrite'] = overwrite
    kwargs['headers'] = headers
    kwargs['validate_content'] = validate_content
    kwargs['blob_settings'] = config
    kwargs['max_concurrency'] = max_concurrency
    kwargs['encryption_options'] = encryption_options
    # Add feature flag to user agent for encryption
    if encryption_options['key']:
        modify_user_agent_for_encryption(
            config.user_agent_policy.user_agent,
            sdk_moniker,
            encryption_options['version'],
            kwargs)

    if blob_type == BlobType.BlockBlob:
        kwargs['client'] = client.block_blob
        kwargs['data'] = data
    elif blob_type == BlobType.PageBlob:
        if (encryption_options['version'] == '2.0' and
            (encryption_options['required'] or encryption_options['key'] is not None)):
            raise ValueError("Encryption version 2.0 does not currently support page blobs.")
        kwargs['client'] = client.page_blob
    elif blob_type == BlobType.AppendBlob:
        if encryption_options['required'] or (encryption_options['key'] is not None):
            raise ValueError(_ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION)
        kwargs['client'] = client.append_blob
    else:
        raise ValueError(f"Unsupported BlobType: {blob_type}")
    return kwargs

def _upload_blob_from_url_options(
    source_url: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for an upload blob operation from URL.

    :param str source_url:
        A URL of up to 2 KB in length that specifies a file or blob.
        The value should be URL-encoded as it would appear in a request URI.
        If the source is in another account, the source must either be public
        or must be authenticated via a shared access signature. If the source
        is public, no authentication is required.
    :returns: A dictionary containing the upload blob from URL options.
    :rtype: Dict[str, Any]
    """
    source_url = _encode_source_url(source_url=source_url)
    tier = kwargs.pop('standard_blob_tier', None)
    overwrite = kwargs.pop('overwrite', False)
    content_settings = kwargs.pop('content_settings', None)
    source_authorization = kwargs.pop('source_authorization', None)
    if content_settings:
        kwargs['blob_http_headers'] = BlobHTTPHeaders(
            blob_cache_control=content_settings.cache_control,
            blob_content_type=content_settings.content_type,
            blob_content_md5=None,
            blob_content_encoding=content_settings.content_encoding,
            blob_content_language=content_settings.content_language,
            blob_content_disposition=content_settings.content_disposition
        )
    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
        cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                            encryption_algorithm=cpk.algorithm)

    options = {
        'copy_source_authorization': source_authorization,
        'content_length': 0,
        'copy_source_blob_properties': kwargs.pop('include_source_blob_properties', True),
        'source_content_md5': kwargs.pop('source_content_md5', None),
        'copy_source': source_url,
        'modified_access_conditions': get_modify_conditions(kwargs),
        'blob_tags_string': serialize_blob_tags_header(kwargs.pop('tags', None)),
        'cls': return_response_headers,
        'lease_access_conditions': get_access_conditions(kwargs.pop('destination_lease', None)),
        'tier': tier.value if tier else None,
        'source_modified_access_conditions': get_source_conditions(kwargs),
        'cpk_info': cpk_info,
        'cpk_scope_info': get_cpk_scope_info(kwargs)
    }
    options.update(kwargs)
    if not overwrite and not _any_conditions(**options): # pylint: disable=protected-access
        options['modified_access_conditions'].if_none_match = '*'
    return options

def _download_blob_options(
    blob_name: str,
    container_name: str,
    version_id: Optional[str],
    offset: Optional[int],
    length: Optional[int],
    encoding: Optional[str],
    encryption_options: Dict[str, Any],
    config: "StorageConfiguration",
    sdk_moniker: str,
    client: "AzureBlobStorage",
    **kwargs
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for a download blob operation.

    :param str blob_name:
        The name of the blob.
    :param str container_name:
        The name of the container.
    :param Optional[str] version_id:
        The version id parameter is a value that, when present, specifies the version of the blob to download.
    :param Optional[int] offset:
        Start of byte range to use for downloading a section of the blob. Must be set if length is provided.
    :param Optional[int] length:
        Number of bytes to read from the stream. This is optional, but should be supplied for optimal performance.
    :param Optional[str] encoding:
        Encoding to decode the downloaded bytes. Default is None, i.e. no decoding.
    :param Dict[str, Any] encryption_options:
        The options for encryption, if enabled.
    :param StorageConfiguration config:
        The Storage configuration options.
    :param str sdk_moniker:
        The string representing the SDK package version.
    :param AzureBlobStorage client:
        The generated Blob Storage client.
    :returns: A dictionary containing the download blob options.
    :rtype: Dict[str, Any]
    """
    if length is not None:
        if offset is None:
            raise ValueError("Offset must be provided if length is provided.")
        length = offset + length - 1  # Service actually uses an end-range inclusive index

    validate_content = kwargs.pop('validate_content', False)
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)

    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
        cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                            encryption_algorithm=cpk.algorithm)

    # Add feature flag to user agent for encryption
    if encryption_options['key'] or encryption_options['resolver']:
        modify_user_agent_for_encryption(
            config.user_agent_policy.user_agent,
            sdk_moniker,
            encryption_options['version'],
            kwargs)

    options = {
        'clients': client,
        'config': config,
        'start_range': offset,
        'end_range': length,
        'version_id': version_id,
        'validate_content': validate_content,
        'encryption_options': {
            'required': encryption_options['required'],
            'key': encryption_options['key'],
            'resolver': encryption_options['resolver']},
        'lease_access_conditions': access_conditions,
        'modified_access_conditions': mod_conditions,
        'cpk_info': cpk_info,
        'download_cls': kwargs.pop('cls', None) or deserialize_blob_stream,
        'max_concurrency':kwargs.pop('max_concurrency', 1),
        'encoding': encoding,
        'timeout': kwargs.pop('timeout', None),
        'name': blob_name,
        'container': container_name}
    options.update(kwargs)
    return options

def _quick_query_options(
    snapshot: Optional[str],
    query_expression: str,
    **kwargs: Any
) -> Tuple[Dict[str, Any], str]:
    """Creates a dictionary containing the options for a quick query operation.

    :param Optional[str] snapshot:
        The snapshot data of the blob.
    :param str query_expression:
        A query statement.
    :returns: A dictionary containing the quick query options and offset.
    :rtype: Tuple[Dict[str, Any], str]
    """
    delimiter = '\n'
    input_format = kwargs.pop('blob_format', None)
    if input_format == QuickQueryDialect.DelimitedJson:
        input_format = DelimitedJsonDialect()
    if input_format == QuickQueryDialect.DelimitedText:
        input_format = DelimitedTextDialect()
    input_parquet_format = input_format == "ParquetDialect"
    if input_format and not input_parquet_format:
        try:
            delimiter = input_format.lineterminator
        except AttributeError:
            try:
                delimiter = input_format.delimiter
            except AttributeError as exc:
                raise ValueError("The Type of blob_format can only be DelimitedTextDialect or "
                                    "DelimitedJsonDialect or ParquetDialect") from exc
    output_format = kwargs.pop('output_format', None)
    if output_format == QuickQueryDialect.DelimitedJson:
        output_format = DelimitedJsonDialect()
    if output_format == QuickQueryDialect.DelimitedText:
        output_format = DelimitedTextDialect()
    if output_format:
        if output_format == "ParquetDialect":
            raise ValueError("ParquetDialect is invalid as an output format.")
        try:
            delimiter = output_format.lineterminator
        except AttributeError:
            try:
                delimiter = output_format.delimiter
            except AttributeError:
                pass
    else:
        output_format = input_format if not input_parquet_format else None
    query_request = QueryRequest(
        expression=query_expression,
        input_serialization=serialize_query_format(input_format),
        output_serialization=serialize_query_format(output_format)
    )
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)

    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
        cpk_info = CpkInfo(
            encryption_key=cpk.key_value,
            encryption_key_sha256=cpk.key_hash,
            encryption_algorithm=cpk.algorithm
        )
    options = {
        'query_request': query_request,
        'lease_access_conditions': access_conditions,
        'modified_access_conditions': mod_conditions,
        'cpk_info': cpk_info,
        'snapshot': snapshot,
        'timeout': kwargs.pop('timeout', None),
        'cls': return_headers_and_deserialized,
    }
    options.update(kwargs)
    return options, delimiter

def _generic_delete_blob_options(delete_snapshots: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
    """Creates a dictionary containing the options for a generic delete blob operation.

    :param Optional[str] delete_snapshots:
        Required if the blob has associated snapshots. Values include:
         - "only": Deletes only the blobs snapshots.
         - "include": Deletes the blob along with all snapshots.
    :returns: A dictionary containing the generic delete blob options.
    :rtype: Dict[str, Any]
    """
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)
    if delete_snapshots:
        delete_snapshots = DeleteSnapshotsOptionType(delete_snapshots)
    options = {
        'timeout': kwargs.pop('timeout', None),
        'snapshot': kwargs.pop('snapshot', None),  # this is added for delete_blobs
        'delete_snapshots': delete_snapshots or None,
        'lease_access_conditions': access_conditions,
        'modified_access_conditions': mod_conditions}
    options.update(kwargs)
    return options

def _delete_blob_options(
    snapshot: Optional[str],
    version_id: Optional[str],
    delete_snapshots: Optional[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for a specific delete blob operation.

    :param Optional[str] snapshot:
        The snapshot data of the blob.
    :param Optional[str] version_id:
        The version id that specifies the version of the blob to operate on.
    :param Optional[str] delete_snapshots:
        Required if the blob has associated snapshots. Values include:
         - "only": Deletes only the blobs snapshots.
         - "include": Deletes the blob along with all snapshots.
    :returns: A dictionary containing the specific delete blob options.
    :rtype: Dict[str, Any]
    """
    if snapshot and delete_snapshots:
        raise ValueError("The delete_snapshots option cannot be used with a specific snapshot.")
    options = _generic_delete_blob_options(delete_snapshots, **kwargs)
    options['snapshot'] = snapshot
    options['version_id'] = version_id
    options['blob_delete_type'] = kwargs.pop('blob_delete_type', None)
    return options

def _set_http_headers_options(content_settings: Optional["ContentSettings"] = None, **kwargs: Any) -> Dict[str, Any]:
    """Creates a dictionary containing the options for a set HTTP headers operation.

    :param Optional["ContentSettings"] content_settings:
        ContentSettings object used to set blob properties. Used to set content type, encoding,
        language, disposition, md5, and cache control.
    :returns: A dictionary containing the set HTTP headers options.
    :rtype: Dict[str, Any]
    """
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)
    blob_headers = None
    if content_settings:
        blob_headers = BlobHTTPHeaders(
            blob_cache_control=content_settings.cache_control,
            blob_content_type=content_settings.content_type,
            blob_content_md5=content_settings.content_md5,
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

def _set_blob_metadata_options(metadata: Optional[Dict[str, str]] = None, **kwargs: Any):
    """Creates a dictionary containing the options for a set blob metadata operation.

    :param Optional[Dict[str, str]] metadata:
        Dict containing name and value pairs. Each call to this operation
        replaces all existing metadata attached to the blob. To remove all
        metadata from the blob, call this operation with no metadata headers.
    :returns: A dictionary containing the set HTTP headers options.
    :rtype: Dict[str, Any]
    """
    headers = kwargs.pop('headers', {})
    headers.update(add_metadata_headers(metadata))
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)
    cpk_scope_info = get_cpk_scope_info(kwargs)

    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
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
    size: int,
    content_settings: Optional["ContentSettings"] = None,
    metadata: Optional[Dict[str, str]] = None,
    premium_page_blob_tier: Optional[Union[str, "PremiumPageBlobTier"]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for creating a page blob.

    :param int size:
        This specifies the maximum size for the page blob, up to 1 TB.
        The page blob size must be aligned to a 512-byte boundary.
    :param ContentSettings content_settings:
        ContentSettings object used to set blob properties. Used to set content type, encoding,
        language, disposition, md5, and cache control.
    :param metadata: Name-value pairs associated with the blob as metadata.
    :paramtype metadata: Optional[Dict[str, str]]
    :param PremiumPageBlobTier premium_page_blob_tier:
        A page blob tier value to set the blob to. The tier correlates to the size of the
        blob and number of allowed IOPS. This is only applicable to page blobs on
        premium storage accounts.
    :returns: A dictionary containing the options for a create page blob operation.
    :rtype: Dict[str, Any]
    """
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
            blob_content_md5=content_settings.content_md5,
            blob_content_encoding=content_settings.content_encoding,
            blob_content_language=content_settings.content_language,
            blob_content_disposition=content_settings.content_disposition
        )

    sequence_number = kwargs.pop('sequence_number', None)
    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
        cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                            encryption_algorithm=cpk.algorithm)

    immutability_policy = kwargs.pop('immutability_policy', None)
    if immutability_policy:
        kwargs['immutability_policy_expiry'] = immutability_policy.expiry_time
        kwargs['immutability_policy_mode'] = immutability_policy.policy_mode

    tier = None
    if premium_page_blob_tier:
        try:
            tier = premium_page_blob_tier.value  # type: ignore
        except AttributeError:
            tier = premium_page_blob_tier  # type: ignore

    blob_tags_string = serialize_blob_tags_header(kwargs.pop('tags', None))

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
        'blob_tags_string': blob_tags_string,
        'cls': return_response_headers,
        "tier": tier,
        'headers': headers}
    options.update(kwargs)
    return options

def _create_append_blob_options(
    content_settings: Optional["ContentSettings"] = None,
    metadata: Optional[Dict[str, str]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for creating an append blob.

    :param ContentSettings content_settings:
        ContentSettings object used to set blob properties. Used to set content type, encoding,
        language, disposition, md5, and cache control.
    :param metadata: Name-value pairs associated with the blob as metadata.
    :paramtype metadata: Optional[Dict[str, str]]
    :returns: A dictionary containing the options for a create append blob operation.
    :rtype: Dict[str, Any]
    """
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
            blob_content_md5=content_settings.content_md5,
            blob_content_encoding=content_settings.content_encoding,
            blob_content_language=content_settings.content_language,
            blob_content_disposition=content_settings.content_disposition
        )

    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
        cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                            encryption_algorithm=cpk.algorithm)

    immutability_policy = kwargs.pop('immutability_policy', None)
    if immutability_policy:
        kwargs['immutability_policy_expiry'] = immutability_policy.expiry_time
        kwargs['immutability_policy_mode'] = immutability_policy.policy_mode

    blob_tags_string = serialize_blob_tags_header(kwargs.pop('tags', None))

    options = {
        'content_length': 0,
        'blob_http_headers': blob_headers,
        'timeout': kwargs.pop('timeout', None),
        'lease_access_conditions': access_conditions,
        'modified_access_conditions': mod_conditions,
        'cpk_scope_info': cpk_scope_info,
        'cpk_info': cpk_info,
        'blob_tags_string': blob_tags_string,
        'cls': return_response_headers,
        'headers': headers}
    options.update(kwargs)
    return options

def _create_snapshot_options(metadata: Optional[Dict[str, str]] = None, **kwargs: Any) -> Dict[str, Any]:
    """Creates a dictionary containing the options for creating a blob snapshot.

    :param metadata: Name-value pairs associated with the blob as metadata.
    :paramtype metadata: Optional[Dict[str, str]]
    :returns: A dictionary containing the options for creating a blob snapshot.
    :rtype: Dict[str, Any]
    """
    headers = kwargs.pop('headers', {})
    headers.update(add_metadata_headers(metadata))
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)
    cpk_scope_info = get_cpk_scope_info(kwargs)
    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
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

def _start_copy_from_url_options(  # pylint:disable=too-many-statements
    source_url: str,
    metadata: Optional[Dict[str, str]] = None,
    incremental_copy: bool = False,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for starting a blob copy from URL.

    :param str source_url:
        A URL of up to 2 KB in length that specifies a file or blob.
        The value should be URL-encoded as it would appear in a request URI.
        If the source is in another account, the source must either be public
        or must be authenticated via a shared access signature. If the source
        is public, no authentication is required.
    :param metadata: Name-value pairs associated with the blob as metadata.
    :paramtype metadata: Optional[Dict[str, str]]
    :param bool incremental_copy:
        Copies the snapshot of the source page blob to a destination page blob.
        The snapshot is copied such that only the differential changes between
        the previously copied snapshot are transferred to the destination.
        The copied snapshots are complete copies of the original snapshot and
        can be read or copied from as usual. Defaults to False.
    :returns: A dictionary containing the options for a start copy from URL operation.
    :rtype: Dict[str, Any]
    """
    source_url = _encode_source_url(source_url=source_url)
    headers = kwargs.pop('headers', {})
    headers.update(add_metadata_headers(metadata))
    if 'source_lease' in kwargs:
        source_lease = kwargs.pop('source_lease')
        try:
            headers['x-ms-source-lease-id'] = source_lease.id
        except AttributeError:
            headers['x-ms-source-lease-id'] = source_lease

    tier = kwargs.pop('premium_page_blob_tier', None) or kwargs.pop('standard_blob_tier', None)
    tags = kwargs.pop('tags', None)

    # Options only available for sync copy
    requires_sync = kwargs.pop('requires_sync', None)
    encryption_scope_str = kwargs.pop('encryption_scope', None)
    source_authorization = kwargs.pop('source_authorization', None)
    # If tags is a str, interpret that as copy_source_tags
    copy_source_tags = isinstance(tags, str)

    if incremental_copy:
        if source_authorization:
            raise ValueError("Source authorization tokens are not applicable for incremental copying.")
        if copy_source_tags:
            raise ValueError("Copying source tags is not applicable for incremental copying.")

    # TODO: refactor start_copy_from_url api in _blob_client.py. Call _generated/_blob_operations.py copy_from_url
    #  when requires_sync=True is set.
    #  Currently both sync copy and async copy are calling _generated/_blob_operations.py start_copy_from_url.
    #  As sync copy diverges more from async copy, more problem will surface.
    if requires_sync is True:
        headers['x-ms-requires-sync'] = str(requires_sync)
        if encryption_scope_str:
            headers['x-ms-encryption-scope'] = encryption_scope_str
        if source_authorization:
            headers['x-ms-copy-source-authorization'] = source_authorization
        if copy_source_tags:
            headers['x-ms-copy-source-tag-option'] = tags
    else:
        if encryption_scope_str:
            raise ValueError(
                "Encryption_scope is only supported for sync copy, please specify requires_sync=True")
        if source_authorization:
            raise ValueError(
                "Source authorization tokens are only supported for sync copy, please specify requires_sync=True")
        if copy_source_tags:
            raise ValueError(
                "Copying source tags is only supported for sync copy, please specify requires_sync=True")

    timeout = kwargs.pop('timeout', None)
    dest_mod_conditions = get_modify_conditions(kwargs)
    blob_tags_string = serialize_blob_tags_header(tags) if not copy_source_tags else None

    immutability_policy = kwargs.pop('immutability_policy', None)
    if immutability_policy:
        kwargs['immutability_policy_expiry'] = immutability_policy.expiry_time
        kwargs['immutability_policy_mode'] = immutability_policy.policy_mode

    options = {
        'copy_source': source_url,
        'seal_blob': kwargs.pop('seal_destination_blob', None),
        'timeout': timeout,
        'modified_access_conditions': dest_mod_conditions,
        'blob_tags_string': blob_tags_string,
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

def _abort_copy_options(copy_id: Union[str, Dict[str, Any], BlobProperties], **kwargs: Any) -> Dict[str, Any]:
    """Creates a dictionary containing the options for aborting a copy.

    :param copy_id:
        The copy operation to abort. This can be either an ID string, or an instance of BlobProperties.
    :paramtype copy_id: Union[str, Dict[str, Any], BlobProperties]
    :returns: A dictionary containing the options for an abort copy operation.
    :rtype: Dict[str, Any]
    """
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    if isinstance(copy_id, BlobProperties):
        copy_id = copy_id.copy.id  # type: ignore [assignment]
    elif isinstance(copy_id, dict):
        copy_id = copy_id['copy_id']
    options = {
        'copy_id': copy_id,
        'lease_access_conditions': access_conditions,
        'timeout': kwargs.pop('timeout', None)}
    options.update(kwargs)
    return options

def _stage_block_options(
    block_id: str,
    data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]],
    length: Optional[int] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for staging a block.

    :param str block_id:
        A string value that identifies the block.
        The string should be less than or equal to 64 bytes in size.
        For a given blob, the block_id must be the same size for each block.
    :param data: The blob data.
    :type data: data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]]
    :param int length: Size of the block.
    :returns: A dictionary containing the options for a stage block operation.
    :rtype: Dict[str, Any]
    """
    block_id = encode_base64(str(block_id))
    if isinstance(data, str):
        data = data.encode(kwargs.pop('encoding', 'UTF-8'))  # type: ignore
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
    block_id: str,
    source_url: str,
    source_offset: Optional[int] = None,
    source_length: Optional[int] = None,
    source_content_md5: Optional[Union[bytes, bytearray]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for staging a block from URL

    :param str block_id: A string value that identifies the block.
        The string should be less than or equal to 64 bytes in size.
        For a given blob, the block_id must be the same size for each block.
    :param str source_url: The URL.
    :param int source_offset:
        Start of byte range to use for the block. Must be set if source length is provided.
    :param int source_length: The size of the block in bytes.
    :param bytearray source_content_md5:
        Specify the md5 calculated for the range of bytes that must be read from the copy source.
    :returns: A dictionary containing the options for a create page blob operation.
    :rtype: Dict[str, Any]
    """
    source_url = _encode_source_url(source_url=source_url)
    source_authorization = kwargs.pop('source_authorization', None)
    if source_length is not None and source_offset is None:
        raise ValueError("Source offset value must not be None if length is set.")
    if source_length is not None and source_offset is not None:
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
        cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                            encryption_algorithm=cpk.algorithm)
    options = {
        'copy_source_authorization': source_authorization,
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
    }
    options.update(kwargs)
    return options

def _get_block_list_result(blocks: BlockList) -> Tuple[List[Optional[BlobBlock]], List[Optional[BlobBlock]]]:
    """Gets the block list results from the provided blocks.

    :param BlockList blocks:
        The blocks returned from generated code.
    :returns: A list of blocks.
    :rtype: Tuple[List[Optional[BlobBlock]], List[Optional[BlobBlock]]]
    """
    committed = []
    uncommitted = []
    if blocks.committed_blocks:
        committed = [BlobBlock._from_generated(b) for b in blocks.committed_blocks]  # pylint: disable=protected-access
    if blocks.uncommitted_blocks:
        uncommitted = [BlobBlock._from_generated(b) for b in blocks.uncommitted_blocks]  # pylint: disable=protected-access
    return committed, uncommitted

def _commit_block_list_options(
    block_list: List[BlobBlock],
    content_settings: Optional["ContentSettings"] = None,
    metadata: Optional[Dict[str, str]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for committing a block list.

    :param List[BlobBlock] block_list:
        List of Block blobs.
    :param ContentSettings content_settings:
        ContentSettings object used to set blob properties. Used to set content type, encoding,
        language, disposition, md5, and cache control.
    :param metadata: Name-value pairs associated with the blob as metadata.
    :paramtype metadata: Optional[Dict[str, str]]
    :returns: A dictionary containing the options for a commit block list operation.
    :rtype: Dict[str, Any]
    """
    block_lookup = BlockLookupList(committed=[], uncommitted=[], latest=[])
    for block in block_list:
        if isinstance(block, BlobBlock):
            if block.state.value == 'committed':
                cast(List[str], block_lookup.committed).append(encode_base64(str(block.id)))
            elif block.state.value == 'uncommitted':
                cast(List[str], block_lookup.uncommitted).append(encode_base64(str(block.id)))
            elif block_lookup.latest is not None:
                block_lookup.latest.append(encode_base64(str(block.id)))
        else:
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
            blob_content_md5=content_settings.content_md5,
            blob_content_encoding=content_settings.content_encoding,
            blob_content_language=content_settings.content_language,
            blob_content_disposition=content_settings.content_disposition
        )

    validate_content = kwargs.pop('validate_content', False)
    cpk_scope_info = get_cpk_scope_info(kwargs)
    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
        cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                            encryption_algorithm=cpk.algorithm)

    immutability_policy = kwargs.pop('immutability_policy', None)
    if immutability_policy:
        kwargs['immutability_policy_expiry'] = immutability_policy.expiry_time
        kwargs['immutability_policy_mode'] = immutability_policy.policy_mode

    tier = kwargs.pop('standard_blob_tier', None)
    blob_tags_string = serialize_blob_tags_header(kwargs.pop('tags', None))

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
        'blob_tags_string': blob_tags_string,
        'headers': headers
    }
    options.update(kwargs)
    return options

def _set_blob_tags_options(
    version_id: Optional[str],
    tags: Optional[Dict[str, str]] = None,
    **kwargs: Any
)-> Dict[str, Any]:
    """Creates a dictionary containing the options for setting blob tags.

    :param Optional[str] version_id:
        The version id that specifies the version of the blob to operate on.
    :param tags:
        Name-value pairs associated with the blob as tag. Tags are case-sensitive.
        The tag set may contain at most 10 tags.  Tag keys must be between 1 and 128 characters,
        and tag values must be between 0 and 256 characters.
        Valid tag key and value characters include: lowercase and uppercase letters, digits (0-9),
        space (` `), plus (+), minus (-), period (.), solidus (/), colon (:), equals (=), underscore (_)
    :paramtype tags: Optional[Dict[str, str]]
    :returns: A dictionary containing the options for a set blob tags operation.
    :rtype: Dict[str, Any]
    """
    serialized_tags = serialize_blob_tags(tags)
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)

    options = {
        'tags': serialized_tags,
        'lease_access_conditions': access_conditions,
        'modified_access_conditions': mod_conditions,
        'version_id': version_id,
        'cls': return_response_headers}
    options.update(kwargs)
    return options

def _get_blob_tags_options(version_id: Optional[str], snapshot: Optional[str], **kwargs: Any) -> Dict[str, Any]:
    """Creates a dictionary containing the options for getting blob tags.

    :param Optional[str] version_id:
        The version id that specifies the version of the blob to operate on.
    :param Optional[str] snapshot:
        The snapshot data of the blob.
    :returns: A dictionary containing the options for a get blob tags operation.
    :rtype: Dict[str, Any]
    """
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)

    options = {
        'version_id': version_id,
        'snapshot': snapshot,
        'lease_access_conditions': access_conditions,
        'modified_access_conditions': mod_conditions,
        'timeout': kwargs.pop('timeout', None),
        'cls': return_headers_and_deserialized}
    return options

def _get_page_ranges_options( # type: ignore
    snapshot: Optional[str],
    offset: Optional[int] = None,
    length: Optional[int] = None,
    previous_snapshot_diff: Optional[Union[str, Dict[str, Any]]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for getting page ranges.

    :param Optional[str] snapshot:
        The snapshot data of the blob.
    :param Optional[int] offset:
        Start of byte range to use for getting valid page ranges.
        If no length is given, all bytes after the offset will be searched.
        Pages must be aligned with 512-byte boundaries, the start offset
        must be a modulus of 512 and the length must be a modulus of
        512.
    :param Optional[int] length:
        Number of bytes to use for getting valid page ranges.
        If length is given, offset must be provided.
        This range will return valid page ranges from the offset start up to
        the specified length.
        Pages must be aligned with 512-byte boundaries, the start offset
        must be a modulus of 512 and the length must be a modulus of
        512.
    :param previous_snapshot_diff:
        The snapshot diff parameter that contains an opaque DateTime value that
        specifies a previous blob snapshot to be compared against a more recent snapshot
        or the current blob.
    :paramtype previous_snapshot_diff: Optional[Union[str, Dict[str, Any]]]
    :returns: A dictionary containing the options for a get page ranges operation.
    :rtype: Dict[str, Any]
    """
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)
    if length is not None and offset is None:
        raise ValueError("Offset value must not be None if length is set.")
    if length is not None and offset is not None:
        length = offset + length - 1  # Reformat to an inclusive range index
    page_range, _ = validate_and_format_range_headers(
        offset, length, start_range_required=False, end_range_required=False, align_to_page=True
    )
    options = {
        'snapshot': snapshot,
        'lease_access_conditions': access_conditions,
        'modified_access_conditions': mod_conditions,
        'timeout': kwargs.pop('timeout', None),
        'range': page_range}
    if previous_snapshot_diff:
        try:
            options['prevsnapshot'] = previous_snapshot_diff.snapshot # type: ignore
        except AttributeError:
            try:
                options['prevsnapshot'] = previous_snapshot_diff['snapshot'] # type: ignore
            except TypeError:
                options['prevsnapshot'] = previous_snapshot_diff
    options.update(kwargs)
    return options

def _set_sequence_number_options(
    sequence_number_action: str,
    sequence_number: Optional[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for setting a sequence number.

    :param str sequence_number_action:
        This property indicates how the service should modify the blob's sequence
        number. See :class:`~azure.storage.blob.SequenceNumberAction` for more information.
    :param Optional[str] sequence_number:
        This property sets the blob's sequence number. The sequence number is a
        user-controlled property that you can use to track requests and manage
        concurrency issues.
    :returns: A dictionary containing the options for a set sequence number operation.
    :rtype: Dict[str, Any]
    """
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

def _resize_blob_options(size: int, **kwargs: Any) -> Dict[str, Any]:
    """Creates a dictionary containing the options for resizing a blob.

    :param int size:
        Size used to resize blob. Maximum size for a page blob is up to 1 TB.
        The page blob size must be aligned to a 512-byte boundary.
    :returns: A dictionary containing the options for a resize blob operation.
    :rtype: Dict[str, Any]
    """
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)
    if size is None:
        raise ValueError("A content length must be specified for a Page Blob.")

    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
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
    page: bytes,
    offset: int,
    length: int,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for uploading a page.

    :param bytes page:
        Content of the page.
    :param int offset:
        Start of byte range to use for writing to a section of the blob.
        Pages must be aligned with 512-byte boundaries, the start offset
        must be a modulus of 512 and the length  must be a modulus of
        512.
    :param int length:
        Number of bytes to use for writing to a section of the blob.
        Pages must be aligned with 512-byte boundaries, the start offset
        must be a modulus of 512 and the length must be a modulus of
        512.
    :returns: A dictionary containing the options for an upload page operation.
    :rtype: Dict[str, Any]
    """
    if isinstance(page, str):
        page = page.encode(kwargs.pop('encoding', 'UTF-8'))
    if offset is None or offset % 512 != 0:
        raise ValueError("offset must be an integer that aligns with 512 page size")
    if length is None or length % 512 != 0:
        raise ValueError("length must be an integer that aligns with 512 page size")
    end_range = offset + length - 1  # Reformat to an inclusive range index
    content_range = f'bytes={offset}-{end_range}' # type: ignore
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
    source_url: str,
    offset: int,
    length: int,
    source_offset: int,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for uploading pages from URL.

    :param str source_url:
        The URL of the source data. It can point to any Azure Blob or File, that is either public or has a
        shared access signature attached.
    :param int offset:
        Start of byte range to use for writing to a section of the blob.
        Pages must be aligned with 512-byte boundaries, the start offset
        must be a modulus of 512 and the length  must be a modulus of
        512.
    :param int length:
        Number of bytes to use for writing to a section of the blob.
        Pages must be aligned with 512-byte boundaries, the start offset
        must be a modulus of 512 and the length must be a modulus of
        512.
    :param int source_offset:
        This indicates the start of the range of bytes(inclusive) that has to be taken from the copy source.
        The service will read the same number of bytes as the destination range (length-offset).
    :returns: A dictionary containing the options for an upload pages from URL operation.
    :rtype: Dict[str, Any]
    """
    source_url = _encode_source_url(source_url=source_url)
    # TODO: extract the code to a method format_range
    if offset is None or offset % 512 != 0:
        raise ValueError("offset must be an integer that aligns with 512 page size")
    if length is None or length % 512 != 0:
        raise ValueError("length must be an integer that aligns with 512 page size")
    if source_offset is None or offset % 512 != 0:
        raise ValueError("source_offset must be an integer that aligns with 512 page size")

    # Format range
    end_range = offset + length - 1
    destination_range = f'bytes={offset}-{end_range}'
    source_range = f'bytes={source_offset}-{source_offset + length - 1}'  # should subtract 1 here?

    seq_conditions = SequenceNumberAccessConditions(
        if_sequence_number_less_than_or_equal_to=kwargs.pop('if_sequence_number_lte', None),
        if_sequence_number_less_than=kwargs.pop('if_sequence_number_lt', None),
        if_sequence_number_equal_to=kwargs.pop('if_sequence_number_eq', None)
    )
    source_authorization = kwargs.pop('source_authorization', None)
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)
    source_mod_conditions = get_source_conditions(kwargs)
    cpk_scope_info = get_cpk_scope_info(kwargs)
    source_content_md5 = kwargs.pop('source_content_md5', None)
    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
        cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                            encryption_algorithm=cpk.algorithm)

    options = {
        'copy_source_authorization': source_authorization,
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

def _clear_page_options(
    offset: int,
    length: int,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for clearing a range of pages.

    :param int offset:
        Start of byte range to use for writing to a section of the blob.
        Pages must be aligned with 512-byte boundaries, the start offset
        must be a modulus of 512 and the length must be a modulus of
        512.
    :param int length:
        Number of bytes to use for writing to a section of the blob.
        Pages must be aligned with 512-byte boundaries, the start offset
        must be a modulus of 512 and the length must be a modulus of
        512.
    :returns: A dictionary containing the options for a clear range of pages operation.
    :rtype: Dict[str, Any]
    """
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
    content_range = f'bytes={offset}-{end_range}'

    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
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
    data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]],
    length: Optional[int] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for appending a block.

    :param data:
        Content of the block. This can be bytes, text, an iterable or a file-like object.
    :type data: bytes or str or Iterable
    :param int length:
        Size of the block in bytes.
    :returns: A dictionary containing the options for an append block operation.
    :rtype: Dict[str, Any]
    """
    if isinstance(data, str):
        data = data.encode(kwargs.pop('encoding', 'UTF-8')) # type: ignore
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
    copy_source_url: str,
    source_offset: Optional[int] = None,
    source_length: Optional[int] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Creates a dictionary containing the options for appending blocks from URL.

    :param str copy_source_url:
        The URL of the source data. It can point to any Azure Blob or File, that is either public or has a
        shared access signature attached.
    :param int source_offset:
        This indicates the start of the range of bytes (inclusive) that has to be taken from the copy source.
    :param int source_length:
        This indicates the end of the range of bytes that has to be taken from the copy source.
    :returns: A dictionary containing the options for an append block from URL operation.
    :rtype: Dict[str, Any]
    """
    copy_source_url = _encode_source_url(source_url=copy_source_url)
    # If end range is provided, start range must be provided
    if source_length is not None and source_offset is None:
        raise ValueError("source_offset should also be specified if source_length is specified")
    # Format based on whether length is present
    source_range = None
    if source_length is not None and source_offset is not None:
        end_range = source_offset + source_length - 1
        source_range = f'bytes={source_offset}-{end_range}'
    elif source_offset is not None:
        source_range = f"bytes={source_offset}-"

    appendpos_condition = kwargs.pop('appendpos_condition', None)
    maxsize_condition = kwargs.pop('maxsize_condition', None)
    source_content_md5 = kwargs.pop('source_content_md5', None)
    append_conditions = None
    if maxsize_condition or appendpos_condition is not None:
        append_conditions = AppendPositionAccessConditions(
            max_size=maxsize_condition,
            append_position=appendpos_condition
        )
    source_authorization = kwargs.pop('source_authorization', None)
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)
    source_mod_conditions = get_source_conditions(kwargs)
    cpk_scope_info = get_cpk_scope_info(kwargs)
    cpk = kwargs.pop('cpk', None)
    cpk_info = None
    if cpk:
        cpk_info = CpkInfo(encryption_key=cpk.key_value, encryption_key_sha256=cpk.key_hash,
                            encryption_algorithm=cpk.algorithm)

    options = {
        'copy_source_authorization': source_authorization,
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

def _seal_append_blob_options(**kwargs: Any) -> Dict[str, Any]:
    """Creates a dictionary containing the options for sealing an append blob.

    :returns: A dictionary containing the options for a seal append blob operation.
    :rtype: Dict[str, Any]
    """
    appendpos_condition = kwargs.pop('appendpos_condition', None)
    append_conditions = None
    if appendpos_condition is not None:
        append_conditions = AppendPositionAccessConditions(
            append_position=appendpos_condition
        )
    access_conditions = get_access_conditions(kwargs.pop('lease', None))
    mod_conditions = get_modify_conditions(kwargs)

    options = {
        'timeout': kwargs.pop('timeout', None),
        'lease_access_conditions': access_conditions,
        'append_position_access_conditions': append_conditions,
        'modified_access_conditions': mod_conditions,
        'cls': return_response_headers}
    options.update(kwargs)
    return options

def _from_blob_url(
    blob_url: str,
    snapshot: Optional[Union[BlobProperties, str, Dict[str, Any]]]
) -> Tuple[str, str, str, Optional[str]]:
    """Creates a blob URL to interact with a specific Blob.

    :param str blob_url:
        The full endpoint URL to the Blob, including SAS token and snapshot if used. This could be
        either the primary endpoint, or the secondary endpoint depending on the current `location_mode`.
    :param Union[str, Dict[str, Any]] snapshot:
        The optional blob snapshot on which to operate. This can be the snapshot ID string
        or the response returned from :func:`create_snapshot`. If specified, this will override
        the snapshot in the url.
    :returns: The parsed out account_url, container_name, blob_name, and path_snapshot
    :rtype: Tuple[str, str, str, Optional[str]]
    """
    try:
        if not blob_url.lower().startswith('http'):
            blob_url = "https://" + blob_url
    except AttributeError as exc:
        raise ValueError("Blob URL must be a string.") from exc
    parsed_url = urlparse(blob_url.rstrip('/'))

    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {blob_url}")

    account_path = ""
    if ".core." in parsed_url.netloc:
        # .core. is indicating non-customized url. Blob name with directory info can also be parsed.
        path_blob = parsed_url.path.lstrip('/').split('/', maxsplit=1)
    elif "localhost" in parsed_url.netloc or "127.0.0.1" in parsed_url.netloc:
        path_blob = parsed_url.path.lstrip('/').split('/', maxsplit=2)
        account_path += '/' + path_blob[0]
    else:
        # for customized url. blob name that has directory info cannot be parsed.
        path_blob = parsed_url.path.lstrip('/').split('/')
        if len(path_blob) > 2:
            account_path = "/" + "/".join(path_blob[:-2])

    account_url = f"{parsed_url.scheme}://{parsed_url.netloc.rstrip('/')}{account_path}?{parsed_url.query}"

    msg_invalid_url = "Invalid URL. Provide a blob_url with a valid blob and container name."
    if len(path_blob) <= 1:
        raise ValueError(msg_invalid_url)
    container_name, blob_name = unquote(path_blob[-2]), unquote(path_blob[-1])
    if not container_name or not blob_name:
        raise ValueError(msg_invalid_url)

    path_snapshot, _ = parse_query(parsed_url.query)
    if snapshot:
        if isinstance(snapshot, BlobProperties):
            path_snapshot = snapshot.snapshot
        elif isinstance(snapshot, dict):
            path_snapshot = snapshot['snapshot']
        else:
            path_snapshot = snapshot
    return (account_url, container_name, blob_name, path_snapshot)
