# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, AnyStr, Dict, List, Tuple,
    TYPE_CHECKING
)

from azure.storage.blob._shared_access_signature import BlobSharedAccessSignature

try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse
    from urllib2 import quote, unquote

from azure.core import Configuration

from .common import BlobType
from .lease import Lease
from .blob_client import BlobClient
from .models import ContainerProperties, BlobProperties, BlobPropertiesPaged
from ._utils import (
    create_client,
    create_configuration,
    create_pipeline,
    basic_error_map,
    get_access_conditions,
    get_modification_conditions,
    return_response_headers,
    add_metadata_headers,
    process_storage_error,
    encode_base64,
    parse_connection_str
)
from ._deserialize import (
    deserialize_container_properties,
    deserialize_metadata
)
from ._generated.models import BlobHTTPHeaders, StorageErrorException

if TYPE_CHECKING:
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.pipeline.policies import HTTPPolicy
    from .common import PublicAccess
    from .models import ContainerPermissions
    from datetime import datetime


class ContainerClient(object):

    def __init__(
            self, url,  # type: str
            container=None,  # type: Union[ContainerProperties, str]
            credentials=None,  # type: Optional[HTTPPolicy]
            configuration=None,  # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        parsed_url = urlparse(url)

        if not parsed_url.path and not container:
            raise ValueError("Please specify a container name.")
        path_container = ""
        if parsed_url.path:
            path_container = parsed_url.path.partition('/')[0]
        try:
            self.name = container.name
        except AttributeError:
            self.name = container or unquote(path_container)

        self.scheme = parsed_url.scheme
        self.credentials = credentials
        self.account = parsed_url.hostname.split(".blob.core.")[0]
        self.url = url if parsed_url.path else "{}://{}/{}".format(
            self.scheme,
            parsed_url.hostname,
            quote(self.name)
        )
        self._config, self._pipeline = create_pipeline(configuration, credentials, **kwargs)
        self._client = create_client(self.url, self._pipeline)

    @staticmethod
    def create_configuration(**kwargs):
        # type: (**Any) -> Configuration
        return create_configuration(**kwargs)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            container,  # type: Union[str, ContainerProperties]
            credentials=None,  # type: Optional[HTTPPolicy]
            configuration=None,  # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        """
        Create BlobClient from a Connection String.
        """
        account_url, creds = parse_connection_str(conn_str, credentials)
        return cls(
            account_url, container=container,
            credentials=creds, configuration=configuration, **kwargs)

    def make_url(self, protocol=None, sas_token=None):
        # type: (Optional[str], Optional[str]) -> str
        parsed_url = urlparse(self.url)
        new_scheme = protocol or parsed_url.scheme
        query = []
        if sas_token:
            query.append(sas_token)
        new_url = "{}://{}{}".format(
            new_scheme,
            parsed_url.netloc,
            parsed_url.path)
        if query:
            new_url += "?{}".format('&'.join(query))
        return new_url

    def generate_shared_access_signature(
            self, permission=None,  # type: Optional[Union[ContainerPermissions, str]]
            expiry=None,  # type: Optional[Union[datetime, str]]
            start=None,  # type: Optional[Union[datetime, str]]
            policy_id=None,  # type: Optional[str]
            ip=None,  # type: Optional[str]
            protocol=None,  # type: Optional[str]
            cache_control=None,  # type: Optional[str]
            content_disposition=None,  # type: Optional[str]
            content_encoding=None,  # type: Optional[str]
            content_language=None,  # type: Optional[str]
            content_type=None  # type: Optional[str]
        ):
        # type: (...) -> str
        if not hasattr(self.credentials, 'account_key') and not self.credentials.account_key:
            raise ValueError("No account SAS key available.")
        sas = BlobSharedAccessSignature(self.account, self.credentials.account_key)
        return sas.generate_container(
            self.name,
            permission=permission,
            expiry=expiry,
            start=start,
            policy_id=policy_id,
            ip=ip,
            protocol=protocol,
            cache_control=cache_control,
            content_disposition=content_disposition,
            content_encoding=content_encoding,
            content_language=content_language,
            content_type=content_type,
        )

    def create_container(self, metadata=None, public_access=None, timeout=None, **kwargs):
        # type: (Optional[Dict[str, str]], Optional[Union[PublicAccess, str]], Optional[int]) -> None
        """
        :returns: None
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        return self._client.container.create(
            timeout=timeout,
            access=public_access,
            cls=return_response_headers,
            headers=headers,
            **kwargs)

    def delete_container(
            self, lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """
        Marks the specified container for deletion. The container and any blobs
        contained within it are later deleted during garbage collection.

        :param ~azure.storage.blob.lease.Lease lease:
            If specified, delete_container only succeeds if the
            container's lease is active and matches this ID.
            Required if the container has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        self._client.container.delete(
            timeout=timeout,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions,
            error_map=basic_error_map(),
            **kwargs)

    def acquire_lease(
            self, lease_duration=-1,  # type: int
            proposed_lease_id=None,  # type: Optional[str]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs):
        # type: (...) -> Lease
        """
        Requests a new lease. If the container does not have an active lease,
        the Blob service creates a lease on the container and returns a new
        lease ID.

        :param int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change. Default is -1 (infinite lease).
        :param str proposed_lease_id:
            Proposed lease ID, in a GUID string format. The Blob service returns
            400 (Invalid request) if the proposed lease ID is not in the correct format.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A Lease object, that can be run in a context manager.
        :rtype: ~azure.storage.blob.lease.Lease
        """
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        response = self._client.container.acquire_lease(
            timeout=timeout,
            duration=lease_duration,
            proposed_lease_id=proposed_lease_id,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            **kwargs)
        return Lease(self._client.container, **response)

    def break_lease(
            self, lease_break_period=None,  # type: Optional[int]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            timeout=None,  # type: Optional[int]
            **kwargs):
        # type: (...) -> int
        """
        Break the lease, if the container has an active lease. Once a lease is
        broken, it cannot be renewed. Any authorized request can break the lease;
        the request is not required to specify a matching lease ID. When a lease
        is broken, the lease break period is allowed to elapse, during which time
        no lease operation except break and release can be performed on the container.
        When a lease is successfully broken, the response indicates the interval
        in seconds until a new lease can be acquired. 

        :param int lease_break_period:
            This is the proposed duration of seconds that the lease
            should continue before it is broken, between 0 and 60 seconds. This
            break period is only used if it is shorter than the time remaining
            on the lease. If longer, the time remaining on the lease is used.
            A new lease will not be available before the break period has
            expired, but the lease may be held for longer than the break
            period. If this header does not appear with a break
            operation, a fixed-duration lease breaks after the remaining lease
            period elapses, and an infinite lease breaks immediately.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: Approximate time remaining in the lease period, in seconds.
        :rtype: int
        """
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since)
        response = self._client.container.break_lease(
            timeout=timeout,
            break_period=lease_break_period,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            **kwargs)
        return response.get('x-ms-lease-time')

    def get_account_information(self, timeout=None):
        # type: (Optional[int]) -> Dict[str, str]
        """
        :returns: A dict of account information (SKU and account type).
        """
        response = self._client.container.get_account_info(cls=return_response_headers, timeout=timeout)
        return {
            'SKU': response.get('x-ms-sku-name'),
            'AccountType': response.get('x-ms-account-kind')
        }

    def get_container_properties(self, lease=None, timeout=None, **kwargs):
        # type: (Optional[Union[Lease, str]], Optional[int], **Any) -> ContainerProperties
        """
        Returns all user-defined metadata and system properties for the specified
        container. The data returned does not include the container's list of blobs.

        :param ~azure.storage.blob.lease.Lease lease:
            If specified, get_container_properties only succeeds if the
            container's lease is active and matches this ID.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: properties for the specified container within a container object.
        :rtype: ~azure.storage.blob.models.ContainerProperties
        """
        access_conditions = get_access_conditions(lease)
        response = self._client.container.get_properties(
            timeout=timeout,
            lease_access_conditions=access_conditions,
            cls=deserialize_container_properties,
            **kwargs)
        response.name = self.name
        return response

    def get_container_metadata(self, lease=None, timeout=None):
        # type: (Optional[Union[Lease, str]], Optional[int]) -> Dict[str, str]
        """
        :returns: A dict of metadata.
        """
        access_conditions = get_access_conditions(lease)
        try:
            return self._client.container.get_properties(
                comp='metadata',
                timeout=timeout,
                lease_access_conditions=access_conditions,
                cls=deserialize_metadata,
                )
        except StorageErrorException as error:
            process_storage_error(error)

    def set_container_metadata(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            lease=None,  # type: Optional[Union[str, Lease]]
            if_modified_since=None,  # type: Optional[datetime]
            timeout=None,  # type: Optional[int]
            **kwargs
    ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :returns: Container-updated property dict (Etag and last modified).
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(if_modified_since)
        return self._client.container.set_metadata(
            timeout=timeout,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            headers=headers,
            **kwargs
        )

    def get_container_acl(self, lease=None, timeout=None):
        # type: (Optional[Union[Lease, str]], Optional[int]) -> Dict[str, str]
        """
        :returns: Access policy information in a dict.
        """
        access_conditions = get_access_conditions(lease)
        response = self._client.container.get_access_policy(
            timeout=timeout,
            lease_access_conditions=access_conditions,
            cls=return_response_headers,
        )
        return {
            'public-access': response.get('x-ms-blob-public-access'),
            'signed_identifiers': None
        }

    def set_container_acl(
            self, signed_identifiers=None,  # type: Optional[Dict[str, Optional[Tuple[Any, Any, Any]]]]
            public_access=None,  # type: Optional[Union[str, PublicAccess]]
            lease=None,  # type: Optional[Union[str, Lease]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            timeout=None  # type: Optional[int]
        ):
        """
        :returns: Container-updated property dict (Etag and last modified).
        """
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since)
        access_conditions = get_access_conditions(lease)
        response = self._client.container.set_access_policy(
            container_acl=signed_identifiers,
            timeout=timeout,
            access=public_access,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
        )
        return {
            'ETag': response.get('ETag'),
            'Last-Modified': response.get('Last-Modified')
        }

    def list_blob_properties(self, starts_with=None, include=None, timeout=None, **kwargs):
        # type: (Optional[str], Optional[str], Optional[int]) -> Iterable[BlobProperties]
        """
        Returns a generator to list the blobs under the specified container.
        The generator will lazily follow the continuation tokens returned by
        the service and stop when all blobs have been returned or num_results is reached.

        :param str starts_with:
            Filters the results to return only blobs whose names
            begin with the specified prefix.
        :param ~azure.storage.blob.models.Include include:
            Specifies one or more additional datasets to include in the response.
        :param str marker:
            An opaque continuation token. This value can be retrieved from the 
            next_marker field of a previous generator object. If specified,
            this generator will begin returning results from this point.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        :returns: An iterable (auto-paging) response of BlobProperties.
        """
        if include and not isinstance(include, list):
            include = [include]
        results_per_page = kwargs.pop('results_per_page', None)
        marker = kwargs.pop('marker', "")
        command = functools.partial(
            self._client.container.list_blob_flat_segment,
            prefix=starts_with,
            include=include,
            timeout=timeout,
            **kwargs)
        return BlobPropertiesPaged(command, prefix=prefix, results_per_page=results_per_page,  marker=marker)

    # def walk_blob_propertes(self, prefix=None, include=None, delimiter="/", timeout=None, **kwargs):
    #     # type: (Optional[str], Optional[str], str, Optional[int]) -> Iterable[BlobProperties]
    #     """
    #     :returns: A generator that honors directory hierarchy.
    #     """
    #     if include and not isinstance(include, list):
    #         include = [include]
    #     results_per_page = kwargs.pop('results_per_page', None)
    #     command = functools.partial(
    #         self._client.container.list_blob_hierarchy_segment,
    #         delimiter=delimiter,
    #         prefix=prefix,
    #         include=include,
    #         timeout=timeout,
    #         **kwargs)
    #     return BlobPropertiesPaged(command, prefix=prefix, results_per_page=results_per_page)

    def get_blob_client(
            self, blob,  # type: Union[str, BlobProperties]
            blob_type=BlobType.BlockBlob,  # type: Union[BlobType, str]
            snapshot=None  # type: str
        ):
        # type: (...) -> BlobClient
        """
        Get a client to interact with the specified blob.
        The blob need not already exist.

        :param ~azure.storage.blob.common.BlobType blob_type: The type of Blob. Default
         vale is BlobType.BlockBlob
        :param str snapshot: The optional blob snapshot on which to operate.
        :returns: A BlobClient.
        :rtype: ~azure.core.blob.blob_client.BlobClient
        """
        return BlobClient(
            self.url, container=self.name, blob=blob, blob_type=blob_type, snapshot=snapshot,
            credentials=self.credentials, configuration=self._config, _pipeline=self._pipeline)
