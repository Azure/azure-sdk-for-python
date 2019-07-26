# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Dict, List,
    TYPE_CHECKING
)
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # type: ignore

from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

from ._shared.shared_access_signature import SharedAccessSignature
from ._shared.models import Services
from ._shared.base_client import StorageAccountHostsMixin, parse_connection_str, parse_query
from ._shared.response_handlers import process_storage_error
from ._generated import AzureFileStorage
from ._generated.models import StorageErrorException, StorageServiceProperties
from ._generated.version import VERSION
from .share_client import ShareClient
from .models import SharePropertiesPaged

if TYPE_CHECKING:
    from datetime import datetime
    from ._shared.models import ResourceTypes, AccountPermissions
    from .models import Metrics, CorsRule, ShareProperties


class FileServiceClient(StorageAccountHostsMixin):
    """A client to interact with the File Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete shares within the account.
    For operations relating to a specific share, a client for that entity
    can also be retrieved using the `get_share_client` function.

    :ivar str url:
        The full endpoint URL to the file service endpoint, including SAS token if used. This could be
        either the primary endpoint, or the secondard endpoint depending on the current `location_mode`.
    :ivar str primary_endpoint:
        The full primary endpoint URL.
    :ivar str primary_hostname:
        The hostname of the primary endpoint.
    :ivar str secondary_endpoint:
        The full secondard endpoint URL if configured. If not available
        a ValueError will be raised. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.
    :ivar str secondary_hostname:
        The hostname of the secondary endpoint. If not available this
        will be None. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.
    :ivar str location_mode:
        The location mode that the client is currently using. By default
        this will be "primary". Options include "primary" and "secondary".
    :param str account_url:
        The URL to the file storage account. Any other entities included
        in the URL path (e.g. share or file) will be discarded. This URL can be optionally
        authenticated with a SAS token.
    :param credential:
        The credential with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string or an account
        shared access key.

    Example:
        .. literalinclude:: ../tests/test_file_samples_authentication.py
            :start-after: [START create_file_service_client]
            :end-before: [END create_file_service_client]
            :language: python
            :dedent: 8
            :caption: Create the file service client with url and credential.
    """
    def __init__(
            self, account_url,  # type: str
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
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))
        if hasattr(credential, 'get_token'):
            raise ValueError("Token credentials not supported by the File service.")

        _, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError(
                'You need to provide either an account key or SAS token when creating a storage service.')
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(FileServiceClient, self).__init__(parsed_url, 'file', credential, **kwargs)
        self._client = AzureFileStorage(version=VERSION, url=self.url, pipeline=self._pipeline)

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}/{}".format(self.scheme, hostname, self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            credential=None, # type: Optional[Any]
            **kwargs  # type: Any
        ):
        """Create FileServiceClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param credential:
            The credential with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string or an account
            shared access key.

        Example:
            .. literalinclude:: ../tests/test_file_samples_authentication.py
                :start-after: [START create_file_service_client_from_conn_string]
                :end-before: [END create_file_service_client_from_conn_string]
                :language: python
                :dedent: 8
                :caption: Create the file service client with connection string.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'file')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(account_url, credential=credential, **kwargs)

    def generate_shared_access_signature(
            self, resource_types,  # type: Union[ResourceTypes, str]
            permission,  # type: Union[AccountPermissions, str]
            expiry,  # type: Optional[Union[datetime, str]]
            start=None,  # type: Optional[Union[datetime, str]]
            ip=None,  # type: Optional[str]
            protocol=None  # type: Optional[str]
        ):
        """Generates a shared access signature for the file service.

        Use the returned signature with the credential parameter of any FileServiceClient,
        ShareClient, DirectoryClient, or FileClient.

        :param ~azure.storage.file._shared.models.ResourceTypes resource_types:
            Specifies the resource types that are accessible with the account SAS.
        :param ~azure.storage.file._shared.models.AccountPermissions permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :param expiry:
            The time at which the shared access signature becomes invalid.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has
            been specified in an associated stored access policy. Azure will always
            convert values to UTC. If a date is passed in without timezone info, it
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If
            omitted, start time for this call is assumed to be the time when the
            storage service receives the request. Azure will always convert values
            to UTC. If a date is passed in without timezone info, it is assumed to
            be UTC.
        :type start: datetime or str
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value is https.
        :return: A Shared Access Signature (sas) token.
        :rtype: str

        Example:
            .. literalinclude:: ../tests/test_file_samples_authentication.py
                :start-after: [START generate_sas_token]
                :end-before: [END generate_sas_token]
                :language: python
                :dedent: 8
                :caption: Generate a sas token.
        """
        if not hasattr(self.credential, 'account_key') and not self.credential.account_key:
            raise ValueError("No account SAS key available.")

        sas = SharedAccessSignature(self.credential.account_name, self.credential.account_key)
        return sas.generate_account(
            Services.FILE, resource_types, permission, expiry, start=start, ip=ip, protocol=protocol) # type: ignore

    @distributed_trace
    def get_service_properties(self, timeout=None, **kwargs):
        # type(Optional[int]) -> Dict[str, Any]
        """Gets the properties of a storage account's File service, including
        Azure Storage Analytics.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.file._generated.models.StorageServiceProperties

        Example:
            .. literalinclude:: ../tests/test_file_samples_service.py
                :start-after: [START get_service_properties]
                :end-before: [END get_service_properties]
                :language: python
                :dedent: 8
                :caption: Get file service properties.
        """
        try:
            return self._client.service.get_properties(timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def set_service_properties(
            self, hour_metrics=None,  # type: Optional[Metrics]
            minute_metrics=None,  # type: Optional[Metrics]
            cors=None,  # type: Optional[List[CorsRule]]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """Sets the properties of a storage account's File service, including
        Azure Storage Analytics. If an element (e.g. Logging) is left as None, the
        existing settings on the service for that functionality are preserved.

        :param hour_metrics:
            The hour metrics settings provide a summary of request
            statistics grouped by API in hourly aggregates for files.
        :type hour_metrics: ~azure.storage.file.models.Metrics
        :param minute_metrics:
            The minute metrics settings provide request statistics
            for each minute for files.
        :type minute_metrics: ~azure.storage.file.models.Metrics
        :param cors:
            You can include up to five CorsRule elements in the
            list. If an empty list is specified, all CORS rules will be deleted,
            and CORS will be disabled for the service.
        :type cors: list(:class:`~azure.storage.file.models.CorsRule`)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        Example:
            .. literalinclude:: ../tests/test_file_samples_service.py
                :start-after: [START set_service_properties]
                :end-before: [END set_service_properties]
                :language: python
                :dedent: 8
                :caption: Sets file service properties.
        """
        props = StorageServiceProperties(
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=cors
        )
        try:
            self._client.service.set_properties(props, timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def list_shares(
            self, name_starts_with=None,  # type: Optional[str]
            include_metadata=False,  # type: Optional[bool]
            include_snapshots=False, # type: Optional[bool]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> ItemPaged[ShareProperties]
        """Returns auto-paging iterable of dict-like ShareProperties under the specified account.
        The generator will lazily follow the continuation tokens returned by
        the service and stop when all shares have been returned.

        :param str name_starts_with:
            Filters the results to return only shares whose names
            begin with the specified name_starts_with.
        :param bool include_metadata:
            Specifies that share metadata be returned in the response.
        :param bool include_snapshots:
            Specifies that share snapshot be returned in the response.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An iterable (auto-paging) of ShareProperties.
        :rtype: ~azure.core.paging.ItemPaged[~azure.storage.file.models.ShareProperties]

        Example:
            .. literalinclude:: ../tests/test_file_samples_service.py
                :start-after: [START fsc_list_shares]
                :end-before: [END fsc_list_shares]
                :language: python
                :dedent: 12
                :caption: List shares in the file service.
        """
        include = []
        if include_metadata:
            include.append('metadata')
        if include_snapshots:
            include.append('snapshots')
        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.service.list_shares_segment,
            include=include,
            timeout=timeout,
            **kwargs)
        return ItemPaged(
            command, prefix=name_starts_with, results_per_page=results_per_page,
            page_iterator_class=SharePropertiesPaged)

    @distributed_trace
    def create_share(
            self, share_name,  # type: str
            metadata=None,  # type: Optional[Dict[str, str]]
            quota=None,  # type: Optional[int]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> ShareClient
        """Creates a new share under the specified account. If the share
        with the same name already exists, the operation fails. Returns a client with
        which to interact with the newly created share.

        :param str share_name: The name of the share to create.
        :param metadata:
            A dict with name_value pairs to associate with the
            share as metadata. Example:{'Category':'test'}
        :type metadata: dict(str, str)
        :param int quota:
            Quota in bytes.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.file.share_client.ShareClient

        Example:
            .. literalinclude:: ../tests/test_file_samples_service.py
                :start-after: [START fsc_create_shares]
                :end-before: [END fsc_create_shares]
                :language: python
                :dedent: 8
                :caption: Create a share in the file service.
        """
        share = self.get_share_client(share_name)
        share.create_share(metadata, quota, timeout, **kwargs)
        return share

    @distributed_trace
    def delete_share(
            self, share_name,  # type: Union[ShareProperties, str]
            delete_snapshots=False, # type: Optional[bool]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """Marks the specified share for deletion. The share is
        later deleted during garbage collection.

        :param share_name:
            The share to delete. This can either be the name of the share,
            or an instance of ShareProperties.
        :type share_name: str or ~azure.storage.file.models.ShareProperties
        :param bool delete_snapshots:
            Indicates if snapshots are to be deleted.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        Example:
            .. literalinclude:: ../tests/test_file_samples_service.py
                :start-after: [START fsc_delete_shares]
                :end-before: [END fsc_delete_shares]
                :language: python
                :dedent: 12
                :caption: Delete a share in the file service.
        """
        share = self.get_share_client(share_name)
        share.delete_share(
            delete_snapshots=delete_snapshots, timeout=timeout, **kwargs)

    def get_share_client(self, share, snapshot=None):
        # type: (Union[ShareProperties, str],Optional[Union[Dict[str, Any], str]]) -> ShareClient
        """Get a client to interact with the specified share.
        The share need not already exist.

        :param share:
            The share. This can either be the name of the share,
            or an instance of ShareProperties.
        :type share: str or ~azure.storage.file.models.ShareProperties
        :param str snapshot:
            An optional share snapshot on which to operate.
        :returns: A ShareClient.
        :rtype: ~azure.storage.file.share_client.ShareClient

        Example:
            .. literalinclude:: ../tests/test_file_samples_service.py
                :start-after: [START get_share_client]
                :end-before: [END get_share_client]
                :language: python
                :dedent: 8
                :caption: Gets the share client.
        """
        return ShareClient(
            self.url, share=share, snapshot=snapshot, credential=self.credential, _hosts=self._hosts,
            _configuration=self._config, _pipeline=self._pipeline, _location_mode=self._location_mode)
