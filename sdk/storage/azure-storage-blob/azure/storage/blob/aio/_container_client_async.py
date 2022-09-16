# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines, invalid-overridden-method

import functools
from typing import (  # pylint: disable=unused-import
    Any, AnyStr, AsyncIterator, Dict, List, IO, Iterable, Optional, overload, Union,
    TYPE_CHECKING
)

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import AsyncHttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .._shared.base_client_async import AsyncStorageAccountHostsMixin, AsyncTransportWrapper
from .._shared.policies_async import ExponentialRetry
from .._shared.request_handlers import add_metadata_headers, serialize_iso
from .._shared.response_handlers import (
    process_storage_error,
    return_response_headers,
    return_headers_and_deserialized
)
from .._generated.aio import AzureBlobStorage
from .._generated.models import SignedIdentifier
from .._container_client import ContainerClient as ContainerClientBase, _get_blob_name
from .._deserialize import deserialize_container_properties
from ._download_async import StorageStreamDownloader
from .._encryption import StorageEncryptionMixin
from .._models import ContainerProperties, BlobType, BlobProperties, FilteredBlob
from .._serialize import get_modify_conditions, get_container_cpk_scope_info, get_api_version, get_access_conditions
from ._blob_client_async import BlobClient
from ._lease_async import BlobLeaseClient
from ._list_blobs_helper import BlobNamesPaged, BlobPropertiesPaged, BlobPrefix
from .._list_blobs_helper import IgnoreListBlobsDeserializer
from ._models import FilteredBlobPaged

if TYPE_CHECKING:
    from datetime import datetime
    from .._models import ( # pylint: disable=unused-import
        AccessPolicy,
        StandardBlobTier,
        PremiumPageBlobTier,
        PublicAccess)


class ContainerClient(AsyncStorageAccountHostsMixin, ContainerClientBase, StorageEncryptionMixin):
    """A client to interact with a specific container, although that container
    may not yet exist.

    For operations relating to a specific blob within this container, a blob client can be
    retrieved using the :func:`~get_blob_client` function.

    :param str account_url:
        The URI to the storage account. In order to create a client given the full URI to the container,
        use the :func:`from_container_url` classmethod.
    :param container_name:
        The name of the container for the blob.
    :type container_name: str
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string,
        an instance of a AzureSasCredential or AzureNamedKeyCredential from azure.core.credentials,
        an account shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
        - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
        If using an instance of AzureNamedKeyCredential, "name" should be the storage account name, and "key"
        should be the storage account key.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is the most recent service version that is
        compatible with the current SDK. Setting to an older version may result in reduced feature compatibility.

        .. versionadded:: 12.2.0

    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    :keyword int max_block_size: The maximum chunk size for uploading a block blob in chunks.
        Defaults to 4*1024*1024, or 4MB.
    :keyword int max_single_put_size: If the blob size is less than or equal max_single_put_size, then the blob will be
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

        .. literalinclude:: ../samples/blob_samples_containers_async.py
            :start-after: [START create_container_client_from_service]
            :end-before: [END create_container_client_from_service]
            :language: python
            :dedent: 8
            :caption: Get a ContainerClient from an existing BlobServiceClient.

        .. literalinclude:: ../samples/blob_samples_containers_async.py
            :start-after: [START create_container_client_sasurl]
            :end-before: [END create_container_client_sasurl]
            :language: python
            :dedent: 12
            :caption: Creating the container client directly.
    """
    def __init__(
            self, account_url,  # type: str
            container_name,  # type: str
            credential=None,  # type: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, "TokenCredential"]] # pylint: disable=line-too-long
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        kwargs['retry_policy'] = kwargs.get('retry_policy') or ExponentialRetry(**kwargs)
        super(ContainerClient, self).__init__(
            account_url,
            container_name=container_name,
            credential=credential,
            **kwargs)
        self._api_version = get_api_version(kwargs)
        self._client = self._build_generated_client()
        self._configure_encryption(kwargs)

    def _build_generated_client(self):
        client = AzureBlobStorage(self.url, base_url=self.url, pipeline=self._pipeline)
        client._config.version = self._api_version # pylint: disable=protected-access
        return client

    @distributed_trace_async
    async def create_container(self, metadata=None, public_access=None, **kwargs):
        # type: (Optional[Dict[str, str]], Optional[Union[PublicAccess, str]], **Any) -> Dict[str, Union[str, datetime]]
        """
        Creates a new container under the specified account. If the container
        with the same name already exists, the operation fails.

        :param metadata:
            A dict with name_value pairs to associate with the
            container as metadata. Example:{'Category':'test'}
        :type metadata: dict[str, str]
        :param ~azure.storage.blob.PublicAccess public_access:
            Possible values include: 'container', 'blob'.
        :keyword container_encryption_scope:
            Specifies the default encryption scope to set on the container and use for
            all future writes.

            .. versionadded:: 12.2.0

        :paramtype container_encryption_scope: dict or ~azure.storage.blob.ContainerEncryptionScope
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A dictionary of response headers.
        :rtype: Dict[str, Union[str, datetime]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers_async.py
                :start-after: [START create_container]
                :end-before: [END create_container]
                :language: python
                :dedent: 16
                :caption: Creating a container to store blobs.
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata)) # type: ignore
        timeout = kwargs.pop('timeout', None)
        container_cpk_scope_info = get_container_cpk_scope_info(kwargs)
        try:
            return await self._client.container.create( # type: ignore
                timeout=timeout,
                access=public_access,
                container_cpk_scope_info=container_cpk_scope_info,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def _rename_container(self, new_name, **kwargs):
        # type: (str, **Any) -> ContainerClient
        """Renames a container.

        Operation is successful only if the source container exists.

        :param str new_name:
            The new container name the user wants to rename to.
        :keyword lease:
            Specify this to perform only if the lease ID given
            matches the active lease ID of the source container.
        :paramtype lease: ~azure.storage.blob.BlobLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.blob.ContainerClient
        """
        lease = kwargs.pop('lease', None)
        try:
            kwargs['source_lease_id'] = lease.id
        except AttributeError:
            kwargs['source_lease_id'] = lease
        try:
            renamed_container = ContainerClient(
                "{}://{}".format(self.scheme, self.primary_hostname), container_name=new_name,
                credential=self.credential, api_version=self.api_version, _configuration=self._config,
                _pipeline=self._pipeline, _location_mode=self._location_mode, _hosts=self._hosts,
                require_encryption=self.require_encryption, encryption_version=self.encryption_version,
                key_encryption_key=self.key_encryption_key, key_resolver_function=self.key_resolver_function)
            await renamed_container._client.container.rename(self.container_name, **kwargs)   # pylint: disable = protected-access
            return renamed_container
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def delete_container(
            self, **kwargs):
        # type: (Any) -> None
        """
        Marks the specified container for deletion. The container and any blobs
        contained within it are later deleted during garbage collection.

        :keyword lease:
            If specified, delete_container only succeeds if the
            container's lease is active and matches this ID.
            Required if the container has an active lease.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers_async.py
                :start-after: [START delete_container]
                :end-before: [END delete_container]
                :language: python
                :dedent: 16
                :caption: Delete a container.
        """
        lease = kwargs.pop('lease', None)
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modify_conditions(kwargs)
        timeout = kwargs.pop('timeout', None)
        try:
            await self._client.container.delete(
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def acquire_lease(
            self, lease_duration=-1,  # type: int
            lease_id=None,  # type: Optional[str]
            **kwargs):
        # type: (...) -> BlobLeaseClient
        """
        Requests a new lease. If the container does not have an active lease,
        the Blob service creates a lease on the container and returns a new
        lease ID.

        :param int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change. Default is -1 (infinite lease).
        :param str lease_id:
            Proposed lease ID, in a GUID string format. The Blob service returns
            400 (Invalid request) if the proposed lease ID is not in the correct format.
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A BlobLeaseClient object, that can be run in a context manager.
        :rtype: ~azure.storage.blob.aio.BlobLeaseClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers_async.py
                :start-after: [START acquire_lease_on_container]
                :end-before: [END acquire_lease_on_container]
                :language: python
                :dedent: 12
                :caption: Acquiring a lease on the container.
        """
        lease = BlobLeaseClient(self, lease_id=lease_id) # type: ignore
        kwargs.setdefault('merge_span', True)
        timeout = kwargs.pop('timeout', None)
        await lease.acquire(lease_duration=lease_duration, timeout=timeout, **kwargs)
        return lease

    @distributed_trace_async
    async def get_account_information(self, **kwargs):
        # type: (**Any) -> Dict[str, str]
        """Gets information related to the storage account.

        The information can also be retrieved if the user has a SAS to a container or blob.
        The keys in the returned dictionary include 'sku_name' and 'account_kind'.

        :returns: A dict of account information (SKU and account type).
        :rtype: dict(str, str)
        """
        try:
            return await self._client.container.get_account_info(cls=return_response_headers, **kwargs) # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_container_properties(self, **kwargs):
        # type: (**Any) -> ContainerProperties
        """Returns all user-defined metadata and system properties for the specified
        container. The data returned does not include the container's list of blobs.

        :keyword lease:
            If specified, get_container_properties only succeeds if the
            container's lease is active and matches this ID.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: Properties for the specified container within a container object.
        :rtype: ~azure.storage.blob.ContainerProperties

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers_async.py
                :start-after: [START get_container_properties]
                :end-before: [END get_container_properties]
                :language: python
                :dedent: 16
                :caption: Getting properties on the container.
        """
        lease = kwargs.pop('lease', None)
        access_conditions = get_access_conditions(lease)
        timeout = kwargs.pop('timeout', None)
        try:
            response = await self._client.container.get_properties(
                timeout=timeout,
                lease_access_conditions=access_conditions,
                cls=deserialize_container_properties,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        response.name = self.container_name
        return response # type: ignore

    @distributed_trace_async
    async def exists(self, **kwargs):
        # type: (**Any) -> bool
        """
        Returns True if a container exists and returns False otherwise.

        :kwarg int timeout:
            The timeout parameter is expressed in seconds.
        :returns: boolean
        """
        try:
            await self._client.container.get_properties(**kwargs)
            return True
        except HttpResponseError as error:
            try:
                process_storage_error(error)
            except ResourceNotFoundError:
                return False

    @distributed_trace_async
    async def set_container_metadata( # type: ignore
            self, metadata=None,  # type: Optional[Dict[str, str]]
            **kwargs
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """Sets one or more user-defined name-value pairs for the specified
        container. Each call to this operation replaces all existing metadata
        attached to the container. To remove all metadata from the container,
        call this operation with no metadata dict.

        :param metadata:
            A dict containing name-value pairs to associate with the container as
            metadata. Example: {'category':'test'}
        :type metadata: dict[str, str]
        :keyword lease:
            If specified, set_container_metadata only succeeds if the
            container's lease is active and matches this ID.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Container-updated property dict (Etag and last modified).

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers_async.py
                :start-after: [START set_container_metadata]
                :end-before: [END set_container_metadata]
                :language: python
                :dedent: 16
                :caption: Setting metadata on the container.
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        lease = kwargs.pop('lease', None)
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modify_conditions(kwargs)
        timeout = kwargs.pop('timeout', None)
        try:
            return await self._client.container.set_metadata( # type: ignore
                timeout=timeout,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def _get_blob_service_client(self):  # pylint: disable=client-method-missing-kwargs
        # type: (...) -> BlobServiceClient
        """Get a client to interact with the container's parent service account.

        Defaults to current container's credentials.

        :returns: A BlobServiceClient.
        :rtype: ~azure.storage.blob.BlobServiceClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_service_async.py
                :start-after: [START get_blob_service_client_from_container_client]
                :end-before: [END get_blob_service_client_from_container_client]
                :language: python
                :dedent: 8
                :caption: Get blob service client from container object.
        """
        from ._blob_service_client_async import BlobServiceClient
        if not isinstance(self._pipeline._transport, AsyncTransportWrapper): # pylint: disable = protected-access
            _pipeline = AsyncPipeline(
                transport=AsyncTransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
                policies=self._pipeline._impl_policies # pylint: disable = protected-access
            )
        else:
            _pipeline = self._pipeline  # pylint: disable = protected-access
        return BlobServiceClient(
            "{}://{}".format(self.scheme, self.primary_hostname),
            credential=self._raw_credential, api_version=self.api_version, _configuration=self._config,
            _location_mode=self._location_mode, _hosts=self._hosts, require_encryption=self.require_encryption,
            encryption_version=self.encryption_version, key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function, _pipeline=_pipeline)


    @distributed_trace_async
    async def get_container_access_policy(self, **kwargs):
        # type: (Any) -> Dict[str, Any]
        """Gets the permissions for the specified container.
        The permissions indicate whether container data may be accessed publicly.

        :keyword lease:
            If specified, get_container_access_policy only succeeds if the
            container's lease is active and matches this ID.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Access policy information in a dict.
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers_async.py
                :start-after: [START get_container_access_policy]
                :end-before: [END get_container_access_policy]
                :language: python
                :dedent: 16
                :caption: Getting the access policy on the container.
        """
        lease = kwargs.pop('lease', None)
        access_conditions = get_access_conditions(lease)
        timeout = kwargs.pop('timeout', None)
        try:
            response, identifiers = await self._client.container.get_access_policy(
                timeout=timeout,
                lease_access_conditions=access_conditions,
                cls=return_headers_and_deserialized,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        return {
            'public_access': response.get('blob_public_access'),
            'signed_identifiers': identifiers or []
        }

    @distributed_trace_async
    async def set_container_access_policy(
            self, signed_identifiers,  # type: Dict[str, AccessPolicy]
            public_access=None,  # type: Optional[Union[str, PublicAccess]]
            **kwargs  # type: Any
        ):  # type: (...) -> Dict[str, Union[str, datetime]]
        """Sets the permissions for the specified container or stored access
        policies that may be used with Shared Access Signatures. The permissions
        indicate whether blobs in a container may be accessed publicly.

        :param signed_identifiers:
            A dictionary of access policies to associate with the container. The
            dictionary may contain up to 5 elements. An empty dictionary
            will clear the access policies set on the service.
        :type signed_identifiers: dict[str, ~azure.storage.blob.AccessPolicy]
        :param ~azure.storage.blob.PublicAccess public_access:
            Possible values include: 'container', 'blob'.
        :keyword lease:
            Required if the container has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A datetime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified date/time.
        :keyword ~datetime.datetime if_unmodified_since:
            A datetime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Container-updated property dict (Etag and last modified).
        :rtype: dict[str, str or ~datetime.datetime]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers_async.py
                :start-after: [START set_container_access_policy]
                :end-before: [END set_container_access_policy]
                :language: python
                :dedent: 16
                :caption: Setting access policy on the container.
        """
        timeout = kwargs.pop('timeout', None)
        lease = kwargs.pop('lease', None)
        if len(signed_identifiers) > 5:
            raise ValueError(
                'Too many access policies provided. The server does not support setting '
                'more than 5 access policies on a single resource.')
        identifiers = []
        for key, value in signed_identifiers.items():
            if value:
                value.start = serialize_iso(value.start)
                value.expiry = serialize_iso(value.expiry)
            identifiers.append(SignedIdentifier(id=key, access_policy=value)) # type: ignore
        signed_identifiers = identifiers # type: ignore

        mod_conditions = get_modify_conditions(kwargs)
        access_conditions = get_access_conditions(lease)
        try:
            return await self._client.container.set_access_policy(
                container_acl=signed_identifiers or None,
                timeout=timeout,
                access=public_access,
                lease_access_conditions=access_conditions,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def list_blobs(self, name_starts_with=None, include=None, **kwargs):
        # type: (Optional[str], Optional[Union[str, List[str]]], **Any) -> AsyncItemPaged[BlobProperties]
        """Returns a generator to list the blobs under the specified container.
        The generator will lazily follow the continuation tokens returned by
        the service.

        :param str name_starts_with:
            Filters the results to return only blobs whose names
            begin with the specified prefix.
        :param include:
            Specifies one or more additional datasets to include in the response.
            Options include: 'snapshots', 'metadata', 'uncommittedblobs', 'copy', 'deleted', 'deletedwithversions',
            'tags', 'versions'.
        :paramtype include: list[str] or str
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An iterable (auto-paging) response of BlobProperties.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.storage.blob.BlobProperties]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers_async.py
                :start-after: [START list_blobs_in_container]
                :end-before: [END list_blobs_in_container]
                :language: python
                :dedent: 12
                :caption: List the blobs in the container.
        """
        if include and not isinstance(include, list):
            include = [include]

        results_per_page = kwargs.pop('results_per_page', None)
        timeout = kwargs.pop('timeout', None)
        command = functools.partial(
            self._client.container.list_blob_flat_segment,
            include=include,
            timeout=timeout,
            **kwargs)
        return AsyncItemPaged(
            command,
            prefix=name_starts_with,
            results_per_page=results_per_page,
            page_iterator_class=BlobPropertiesPaged
        )

    @distributed_trace
    def list_blob_names(self, **kwargs: Any) -> AsyncItemPaged[str]:
        """Returns a generator to list the names of blobs under the specified container.
        The generator will lazily follow the continuation tokens returned by
        the service.

        Note that no additional properties or metadata will be returned when using this API.
        Additionally this API does not have an option to include additional blobs such as snapshots,
        versions, soft-deleted blobs, etc. To get any of this data, use :func:`list_blobs()`.

        :keyword str name_starts_with:
            Filters the results to return only blobs whose names
            begin with the specified prefix.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An iterable (auto-paging) response of blob names as strings.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[str]
        """
        name_starts_with = kwargs.pop('name_starts_with', None)
        results_per_page = kwargs.pop('results_per_page', None)
        timeout = kwargs.pop('timeout', None)

        # For listing only names we need to create a one-off generated client and
        # override its deserializer to prevent deserialization of the full response.
        client = self._build_generated_client()
        client.container._deserialize = IgnoreListBlobsDeserializer()  # pylint: disable=protected-access

        command = functools.partial(
            client.container.list_blob_flat_segment,
            timeout=timeout,
            **kwargs)
        return AsyncItemPaged(
            command,
            prefix=name_starts_with,
            results_per_page=results_per_page,
            page_iterator_class=BlobNamesPaged)

    @distributed_trace
    def walk_blobs(
            self, name_starts_with=None, # type: Optional[str]
            include=None, # type: Optional[Any]
            delimiter="/", # type: str
            **kwargs # type: Optional[Any]
        ):
        # type: (...) -> AsyncItemPaged[BlobProperties]
        """Returns a generator to list the blobs under the specified container.
        The generator will lazily follow the continuation tokens returned by
        the service. This operation will list blobs in accordance with a hierarchy,
        as delimited by the specified delimiter character.

        :param str name_starts_with:
            Filters the results to return only blobs whose names
            begin with the specified prefix.
        :param list[str] include:
            Specifies one or more additional datasets to include in the response.
            Options include: 'snapshots', 'metadata', 'uncommittedblobs', 'copy', 'deleted'.
        :param str delimiter:
            When the request includes this parameter, the operation returns a BlobPrefix
            element in the response body that acts as a placeholder for all blobs whose
            names begin with the same substring up to the appearance of the delimiter
            character. The delimiter may be a single character or a string.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An iterable (auto-paging) response of BlobProperties.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.storage.blob.BlobProperties]
        """
        if include and not isinstance(include, list):
            include = [include]

        results_per_page = kwargs.pop('results_per_page', None)
        timeout = kwargs.pop('timeout', None)
        command = functools.partial(
            self._client.container.list_blob_hierarchy_segment,
            delimiter=delimiter,
            include=include,
            timeout=timeout,
            **kwargs)
        return BlobPrefix(
            command,
            prefix=name_starts_with,
            results_per_page=results_per_page,
            delimiter=delimiter)

    @distributed_trace
    def find_blobs_by_tags(
        self, filter_expression,  # type: str
        **kwargs  # type: Optional[Any]
    ):
        # type: (...) -> AsyncItemPaged[FilteredBlob]
        """Returns a generator to list the blobs under the specified container whose tags
        match the given search expression.
        The generator will lazily follow the continuation tokens returned by
        the service.

        :param str filter_expression:
            The expression to find blobs whose tags matches the specified condition.
            eg. "\"yourtagname\"='firsttag' and \"yourtagname2\"='secondtag'"
        :keyword int results_per_page:
            The max result per page when paginating.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An iterable (auto-paging) response of FilteredBlob.
        :rtype: ~azure.core.paging.ItemPaged[~azure.storage.blob.BlobProperties]
        """
        results_per_page = kwargs.pop('results_per_page', None)
        timeout = kwargs.pop('timeout', None)
        command = functools.partial(
            self._client.container.filter_blobs,
            timeout=timeout,
            where=filter_expression,
            **kwargs)
        return AsyncItemPaged(
            command, results_per_page=results_per_page,
            page_iterator_class=FilteredBlobPaged)

    @distributed_trace_async
    async def upload_blob(
            self, name,  # type: Union[str, BlobProperties]
            data,  # type: Union[Iterable[AnyStr], IO[AnyStr]]
            blob_type=BlobType.BlockBlob,  # type: Union[str, BlobType]
            length=None,  # type: Optional[int]
            metadata=None,  # type: Optional[Dict[str, str]]
            **kwargs
        ):
        # type: (...) -> BlobClient
        """Creates a new blob from a data source with automatic chunking.

        :param name: The blob with which to interact. If specified, this value will override
            a blob value specified in the blob URL.
        :type name: str or ~azure.storage.blob.BlobProperties
        :param data: The blob data to upload.
        :param ~azure.storage.blob.BlobType blob_type: The type of the blob. This can be
            either BlockBlob, PageBlob or AppendBlob. The default value is BlockBlob.
        :param int length:
            Number of bytes to read from the stream. This is optional, but
            should be supplied for optimal performance.
        :param metadata:
            Name-value pairs associated with the blob as metadata.
        :type metadata: dict(str, str)
        :keyword bool overwrite: Whether the blob to be uploaded should overwrite the current data.
            If True, upload_blob will overwrite the existing data. If set to False, the
            operation will fail with ResourceExistsError. The exception to the above is with Append
            blob types: if set to False and the data already exists, an error will not be raised
            and the data will be appended to the existing blob. If set overwrite=True, then the existing
            append blob will be deleted, and a new one created. Defaults to False.
        :keyword ~azure.storage.blob.ContentSettings content_settings:
            ContentSettings object used to set blob properties. Used to set content type, encoding,
            language, disposition, md5, and cache control.
        :keyword bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https, as https (the default), will
            already validate. Note that this MD5 hash is not stored with the
            blob. Also note that if enabled, the memory-efficient upload algorithm
            will not be used, because computing the MD5 hash requires buffering
            entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.
        :keyword lease:
            Required if the container has an active lease. Value can be a BlobLeaseClient object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :keyword ~azure.storage.blob.PremiumPageBlobTier premium_page_blob_tier:
            A page blob tier value to set the blob to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.
        :keyword ~azure.storage.blob.StandardBlobTier standard_blob_tier:
            A standard blob tier value to set the blob to. For this version of the library,
            this is only applicable to block blobs on standard storage accounts.
        :keyword int maxsize_condition:
            Optional conditional header. The max length in bytes permitted for
            the append blob. If the Append Block operation would cause the blob
            to exceed that limit or if the blob size is already greater than the
            value specified in this header, the request will fail with
            MaxBlobSizeConditionNotMet error (HTTP status code 412 - Precondition Failed).
        :keyword int max_concurrency:
            Maximum number of parallel connections to use when the blob size exceeds
            64MB.
        :keyword ~azure.storage.blob.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :keyword str encryption_scope:
            A predefined encryption scope used to encrypt the data on the service. An encryption
            scope can be created using the Management API and referenced here by name. If a default
            encryption scope has been defined at the container, this value will override it if the
            container-level scope is configured to allow overrides. Otherwise an error will be raised.

            .. versionadded:: 12.2.0

        :keyword str encoding:
            Defaults to UTF-8.
        :keyword progress_hook:
            An async callback to track the progress of a long running upload. The signature is
            function(current: int, total: Optional[int]) where current is the number of bytes transfered
            so far, and total is the size of the blob or None if the size is unknown.
        :paramtype progress_hook: Callable[[int, Optional[int]], Awaitable[None]]
        :returns: A BlobClient to interact with the newly uploaded blob.
        :rtype: ~azure.storage.blob.aio.BlobClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers_async.py
                :start-after: [START upload_blob_to_container]
                :end-before: [END upload_blob_to_container]
                :language: python
                :dedent: 12
                :caption: Upload blob to the container.
        """
        blob = self.get_blob_client(name)
        kwargs.setdefault('merge_span', True)
        timeout = kwargs.pop('timeout', None)
        encoding = kwargs.pop('encoding', 'UTF-8')
        await blob.upload_blob(
            data,
            blob_type=blob_type,
            length=length,
            metadata=metadata,
            timeout=timeout,
            encoding=encoding,
            **kwargs
        )
        return blob

    @distributed_trace_async
    async def delete_blob(
            self, blob,  # type: Union[str, BlobProperties]
            delete_snapshots=None,  # type: Optional[str]
            **kwargs
        ):
        # type: (...) -> None
        """Marks the specified blob or snapshot for deletion.

        The blob is later deleted during garbage collection.
        Note that in order to delete a blob, you must delete all of its
        snapshots. You can delete both at the same time with the delete_blob
        operation.

        If a delete retention policy is enabled for the service, then this operation soft deletes the blob or snapshot
        and retains the blob or snapshot for specified number of days.
        After specified number of days, blob's data is removed from the service during garbage collection.
        Soft deleted blobs or snapshots are accessible through :func:`list_blobs()` specifying `include=["deleted"]`
        Soft-deleted blob or snapshot can be restored using :func:`~azure.storage.blob.aio.BlobClient.undelete()`

        :param blob: The blob with which to interact. If specified, this value will override
            a blob value specified in the blob URL.
        :type blob: str or ~azure.storage.blob.BlobProperties
        :param str delete_snapshots:
            Required if the blob has associated snapshots. Values include:
             - "only": Deletes only the blobs snapshots.
             - "include": Deletes the blob along with all snapshots.
        :keyword str version_id:
            The version id parameter is an opaque DateTime
            value that, when present, specifies the version of the blob to delete.

            .. versionadded:: 12.4.0
            This keyword argument was introduced in API version '2019-12-12'.

        :keyword lease:
            Required if the blob has an active lease. Value can be a Lease object
            or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        blob = self.get_blob_client(blob) # type: ignore
        kwargs.setdefault('merge_span', True)
        timeout = kwargs.pop('timeout', None)
        await blob.delete_blob( # type: ignore
            delete_snapshots=delete_snapshots,
            timeout=timeout,
            **kwargs)

    @overload
    async def download_blob(
            self, blob: Union[str, BlobProperties],
            offset: int = None,
            length: int = None,
            *,
            encoding: str,
            **kwargs) -> StorageStreamDownloader[str]:
        ...

    @overload
    async def download_blob(
            self, blob: Union[str, BlobProperties],
            offset: int = None,
            length: int = None,
            *,
            encoding: None = None,
            **kwargs) -> StorageStreamDownloader[bytes]:
        ...

    @distributed_trace_async
    async def download_blob(
            self, blob: Union[str, BlobProperties],
            offset: int = None,
            length: int = None,
            *,
            encoding: Optional[str] = None,
            **kwargs) -> StorageStreamDownloader:
        """Downloads a blob to the StorageStreamDownloader. The readall() method must
        be used to read all the content or readinto() must be used to download the blob into
        a stream. Using chunks() returns an async iterator which allows the user to iterate over the content in chunks.

        :param blob: The blob with which to interact. If specified, this value will override
            a blob value specified in the blob URL.
        :type blob: str or ~azure.storage.blob.BlobProperties
        :param int offset:
            Start of byte range to use for downloading a section of the blob.
            Must be set if length is provided.
        :param int length:
            Number of bytes to read from the stream. This is optional, but
            should be supplied for optimal performance.
        :keyword str version_id:
            The version id parameter is an opaque DateTime
            value that, when present, specifies the version of the blob to download.

            .. versionadded:: 12.4.0
            This keyword argument was introduced in API version '2019-12-12'.

        :keyword bool validate_content:
            If true, calculates an MD5 hash for each chunk of the blob. The storage
            service checks the hash of the content that has arrived with the hash
            that was sent. This is primarily valuable for detecting bitflips on
            the wire if using http instead of https, as https (the default), will
            already validate. Note that this MD5 hash is not stored with the
            blob. Also note that if enabled, the memory-efficient upload algorithm
            will not be used because computing the MD5 hash requires buffering
            entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.
        :keyword lease:
            Required if the blob has an active lease. If specified, download_blob only
            succeeds if the blob's lease is active and matches this ID. Value can be a
            BlobLeaseClient object or the lease ID as a string.
        :paramtype lease: ~azure.storage.blob.aio.BlobLeaseClient or str
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword ~azure.storage.blob.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :keyword int max_concurrency:
            The number of parallel connections with which to download.
        :keyword str encoding:
            Encoding to decode the downloaded bytes. Default is None, i.e. no decoding.
        :keyword progress_hook:
            An async callback to track the progress of a long running download. The signature is
            function(current: int, total: int) where current is the number of bytes transfered
            so far, and total is the total size of the download.
        :paramtype progress_hook: Callable[[int, int], Awaitable[None]]
        :keyword int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :returns: A streaming object. (StorageStreamDownloader)
        :rtype: ~azure.storage.blob.aio.StorageStreamDownloader
        """
        blob_client = self.get_blob_client(blob) # type: ignore
        kwargs.setdefault('merge_span', True)
        return await blob_client.download_blob(
            offset=offset,
            length=length,
            encoding=encoding,
            **kwargs)

    @distributed_trace_async
    async def delete_blobs(
        self, *blobs: Union[str, Dict[str, Any], BlobProperties],
        **kwargs: Any
    ) -> AsyncIterator[AsyncHttpResponse]:
        """Marks the specified blobs or snapshots for deletion.

        The blobs are later deleted during garbage collection.
        Note that in order to delete blobs, you must delete all of their
        snapshots. You can delete both at the same time with the delete_blobs operation.

        If a delete retention policy is enabled for the service, then this operation soft deletes the blobs or snapshots
        and retains the blobs or snapshots for specified number of days.
        After specified number of days, blobs' data is removed from the service during garbage collection.
        Soft deleted blobs or snapshots are accessible through :func:`list_blobs()` specifying `include=["deleted"]`
        Soft-deleted blobs or snapshots can be restored using :func:`~azure.storage.blob.aio.BlobClient.undelete()`

        The maximum number of blobs that can be deleted in a single request is 256.

        :param blobs:
            The blobs to delete. This can be a single blob, or multiple values can
            be supplied, where each value is either the name of the blob (str) or BlobProperties.

            .. note::
                When the blob type is dict, here's a list of keys, value rules.

                blob name:
                    key: 'name', value type: str
                snapshot you want to delete:
                    key: 'snapshot', value type: str
                whether to delete snapthots when deleting blob:
                    key: 'delete_snapshots', value: 'include' or 'only'
                if the blob modified or not:
                    key: 'if_modified_since', 'if_unmodified_since', value type: datetime
                etag:
                    key: 'etag', value type: str
                match the etag or not:
                    key: 'match_condition', value type: MatchConditions
                tags match condition:
                    key: 'if_tags_match_condition', value type: str
                lease:
                    key: 'lease_id', value type: Union[str, LeaseClient]
                timeout for subrequest:
                    key: 'timeout', value type: int

        :type blobs: str or dict(str, Any) or ~azure.storage.blob.BlobProperties
        :keyword str delete_snapshots:
            Required if a blob has associated snapshots. Values include:
             - "only": Deletes only the blobs snapshots.
             - "include": Deletes the blob along with all snapshots.
        :keyword ~datetime.datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :keyword ~datetime.datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword bool raise_on_any_failure:
            This is a boolean param which defaults to True. When this is set, an exception
            is raised even if there is a single operation failure. For optimal performance,
            this should be set to False
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: An async iterator of responses, one for each blob in order
        :rtype: asynciterator[~azure.core.pipeline.transport.AsyncHttpResponse]

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_common_async.py
                :start-after: [START delete_multiple_blobs]
                :end-before: [END delete_multiple_blobs]
                :language: python
                :dedent: 12
                :caption: Deleting multiple blobs.
        """
        if len(blobs) == 0:
            return iter(list())

        reqs, options = self._generate_delete_blobs_options(*blobs, **kwargs)

        return await self._batch_send(*reqs, **options)

    @distributed_trace_async
    async def set_standard_blob_tier_blobs(
        self, standard_blob_tier: Union[str, 'StandardBlobTier'],
        *blobs: Union[str, Dict[str, Any], BlobProperties],
        **kwargs: Any
    ) -> AsyncIterator[AsyncHttpResponse]:
        """This operation sets the tier on block blobs.

        A block blob's tier determines Hot/Cool/Archive storage type.
        This operation does not update the blob's ETag.

        The maximum number of blobs that can be updated in a single request is 256.

        :param standard_blob_tier:
            Indicates the tier to be set on all blobs. Options include 'Hot', 'Cool',
            'Archive'. The hot tier is optimized for storing data that is accessed
            frequently. The cool storage tier is optimized for storing data that
            is infrequently accessed and stored for at least a month. The archive
            tier is optimized for storing data that is rarely accessed and stored
            for at least six months with flexible latency requirements.

            .. note::
                If you want to set different tier on different blobs please set this positional parameter to None.
                Then the blob tier on every BlobProperties will be taken.

        :type standard_blob_tier: str or ~azure.storage.blob.StandardBlobTier
        :param blobs:
            The blobs with which to interact. This can be a single blob, or multiple values can
            be supplied, where each value is either the name of the blob (str) or BlobProperties.

            .. note::
                When the blob type is dict, here's a list of keys, value rules.
                blob name:
                    key: 'name', value type: str
                standard blob tier:
                    key: 'blob_tier', value type: StandardBlobTier
                rehydrate priority:
                    key: 'rehydrate_priority', value type: RehydratePriority
                lease:
                    key: 'lease_id', value type: Union[str, LeaseClient]
                tags match condition:
                    key: 'if_tags_match_condition', value type: str
                timeout for subrequest:
                    key: 'timeout', value type: int

        :type blobs: str or dict(str, Any) or ~azure.storage.blob.BlobProperties
        :keyword ~azure.storage.blob.RehydratePriority rehydrate_priority:
            Indicates the priority with which to rehydrate an archived blob
        :keyword str if_tags_match_condition:
            Specify a SQL where clause on blob tags to operate only on blob with a matching value.
            eg. ``\"\\\"tagname\\\"='my tag'\"``

            .. versionadded:: 12.4.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :keyword bool raise_on_any_failure:
            This is a boolean param which defaults to True. When this is set, an exception
            is raised even if there is a single operation failure. For optimal performance,
            this should be set to False.
        :return: An async iterator of responses, one for each blob in order
        :rtype: asynciterator[~azure.core.pipeline.transport.AsyncHttpResponse]
        """
        reqs, options = self._generate_set_tiers_options(standard_blob_tier, *blobs, **kwargs)

        return await self._batch_send(*reqs, **options)

    @distributed_trace_async
    async def set_premium_page_blob_tier_blobs(
        self, premium_page_blob_tier: Union[str, 'PremiumPageBlobTier'],
        *blobs: Union[str, Dict[str, Any], BlobProperties],
        **kwargs: Any
    ) -> AsyncIterator[AsyncHttpResponse]:
        """Sets the page blob tiers on the blobs. This API is only supported for page blobs on premium accounts.

        The maximum number of blobs that can be updated in a single request is 256.

        :param premium_page_blob_tier:
            A page blob tier value to set on all blobs to. The tier correlates to the size of the
            blob and number of allowed IOPS. This is only applicable to page blobs on
            premium storage accounts.

            .. note::
                If you want to set different tier on different blobs please set this positional parameter to None.
                Then the blob tier on every BlobProperties will be taken.

        :type premium_page_blob_tier: ~azure.storage.blob.PremiumPageBlobTier
        :param blobs: The blobs with which to interact. This can be a single blob, or multiple values can
            be supplied, where each value is either the name of the blob (str) or BlobProperties.

            .. note::
                When the blob type is dict, here's a list of keys, value rules.

                blob name:
                    key: 'name', value type: str
                premium blob tier:
                    key: 'blob_tier', value type: PremiumPageBlobTier
                lease:
                    key: 'lease_id', value type: Union[str, LeaseClient]
                timeout for subrequest:
                    key: 'timeout', value type: int

        :type blobs: str or dict(str, Any) or ~azure.storage.blob.BlobProperties
        :keyword int timeout:
            The timeout parameter is expressed in seconds. This method may make
            multiple calls to the Azure service and the timeout will apply to
            each call individually.
        :keyword bool raise_on_any_failure:
            This is a boolean param which defaults to True. When this is set, an exception
            is raised even if there is a single operation failure. For optimal performance,
            this should be set to False.
        :return: An async iterator of responses, one for each blob in order
        :rtype: asynciterator[~azure.core.pipeline.transport.AsyncHttpResponse]
        """
        reqs, options = self._generate_set_tiers_options(premium_page_blob_tier, *blobs, **kwargs)

        return await self._batch_send(*reqs, **options)

    def get_blob_client(
            self, blob,  # type: Union[BlobProperties, str]
            snapshot=None  # type: str
        ):
        # type: (...) -> BlobClient
        """Get a client to interact with the specified blob.

        The blob need not already exist.

        :param blob:
            The blob with which to interact.
        :type blob: str or ~azure.storage.blob.BlobProperties
        :param str snapshot:
            The optional blob snapshot on which to operate. This can be the snapshot ID string
            or the response returned from :func:`~BlobClient.create_snapshot()`.
        :returns: A BlobClient.
        :rtype: ~azure.storage.blob.aio.BlobClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/blob_samples_containers_async.py
                :start-after: [START get_blob_client]
                :end-before: [END get_blob_client]
                :language: python
                :dedent: 12
                :caption: Get the blob client.
        """
        blob_name = _get_blob_name(blob)
        _pipeline = AsyncPipeline(
            transport=AsyncTransportWrapper(self._pipeline._transport), # pylint: disable = protected-access
            policies=self._pipeline._impl_policies # pylint: disable = protected-access
        )
        return BlobClient(
            self.url, container_name=self.container_name, blob_name=blob_name, snapshot=snapshot,
            credential=self.credential, api_version=self.api_version, _configuration=self._config,
            _pipeline=_pipeline, _location_mode=self._location_mode, _hosts=self._hosts,
            require_encryption=self.require_encryption, encryption_version=self.encryption_version,
            key_encryption_key=self.key_encryption_key, key_resolver_function=self.key_resolver_function)
