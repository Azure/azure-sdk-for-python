# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class FileServiceClient():
    """ A client interact with the File Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete shares within the account.
    For operations relating to a specific share, clients for those entities
    can also be retrieved using the `get_client` functions.

    :ivar str url:
        The full endpoint URL to the File service account. This could be either the
        primary endpoint, or the secondard endpint depending on the current `location_mode`.
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
    """

    def __init__(
            self, account_url,  # type: str
            credentials=None,  # type: Optional[Any]
            configuration=None, # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        """A new FileServiceClient.

        :param str account_url:
            The URL to the file storage account. Any other entities included
            in the URL path (e.g. share or file) will be discarded. This URL can be optionally
            authenticated with a SAS token.
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string, and account
            shared access key, or an instance of a TokenCredentials class from azure.identity.
        :param ~azure.storage.file.Configuration configuration:
            An optional pipeline configuration.
        """

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            configuration=None, # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        """Create FileServiceClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string, and account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
        :param configuration:
            Optional pipeline configuration settings.
        :type configuration: ~azure.core.configuration.Configuration
        """

    def generate_shared_access_signature(
            self, resource_types,  # type: Union[ResourceTypes, str]
            permission,  # type: Union[AccountPermissions, str]
            expiry,  # type: Optional[Union[datetime, str]]
            start=None,  # type: Optional[Union[datetime, str]]
            ip=None,  # type: Optional[str]
            protocol=None  # type: Optional[str]
        ):
        """
        Generates a shared access signature for the file service.
        Use the returned signature with the credential parameter of any FileServiceClient,
        ShareClient or FileClient.

        :param ~azure.storage.file.models.ResourceTypes resource_types:
            Specifies the resource types that are accessible with the account SAS.
        :param ~azure.storage.file.models.AccountPermissions permission:
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
        """

    def get_account_information(self, **kwargs):
        # type: (Optional[int]) -> Dict[str, str]
        """Gets information related to the storage account.
        The information can also be retrieved if the user has a SAS to a share or file.

        :returns: A dict of account information (SKU and account type).
        :rtype: dict(str, str)
        """

    def get_service_stats(self, timeout=None, **kwargs):
        # type: (Optional[int], **Any) -> Dict[str, Any]
        """Retrieves statistics related to replication for the File service. It is
        only available when read-access geo-redundant replication is enabled for
        the storage account.

        With geo-redundant replication, Azure Storage maintains your data durable
        in two locations. In both locations, Azure Storage constantly maintains
        multiple healthy replicas of your data. The location where you read,
        create, update, or delete data is the primary storage account location.
        The primary location exists in the region you choose at the time you
        create an account via the Azure Management Azure classic portal, for
        example, North Central US. The location to which your data is replicated
        is the secondary location. The secondary location is automatically
        determined based on the location of the primary; it is in a second data
        center that resides in the same region as the primary location. Read-only
        access is available from the secondary location, if read-access geo-redundant
        replication is enabled for your storage account.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: The file service stats.
        :rtype: ~azure.storage.file._generated.models.StorageServiceStats
        """

    def get_service_properties(self, timeout=None, **kwargs):
        # type(Optional[int]) -> Dict[str, Any]
        """Gets the properties of a storage account's File service, including
        Azure Storage Analytics.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.file._generated.models.StorageServiceProperties
        """

    def set_service_properties(
            self, logging=None,  # type: Optional[Logging]
            hour_metrics=None,  # type: Optional[Metrics]
            minute_metrics=None,  # type: Optional[Metrics]
            cors=None,  # type: Optional[List[CorsRule]]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """Sets the properties of a storage account's File service, including
        Azure Storage Analytics. If an element (e.g. Logging) is left as None, the
        existing settings on the service for that functionality are preserved.

        :param logging:
            Groups the Azure Analytics Logging settings.
        :type logging:
            :class:`~azure.storage.file.models.Logging`
        :param hour_metrics:
            The hour metrics settings provide a summary of request
            statistics grouped by API in hourly aggregates for files.
        :type hour_metrics:
            :class:`~azure.storage.file.models.Metrics`
        :param minute_metrics:
            The minute metrics settings provide request statistics
            for each minute for files.
        :type minute_metrics:
            :class:`~azure.storage.file.models.Metrics`
        :param cors:
            You can include up to five CorsRule elements in the
            list. If an empty list is specified, all CORS rules will be deleted,
            and CORS will be disabled for the service.
        :type cors: list(:class:`~azure.storage.file.models.CorsRule`)
        :param str target_version:
            Indicates the default version to use for requests if an incoming
            request's version is not specified.
        :param delete_retention_policy:
            The delete retention policy specifies whether to retain deleted files.
            It also specifies the number of days and versions of file to keep.
        :type delete_retention_policy:
            :class:`~azure.storage.file..models.RetentionPolicy`
        :param static_website:
            Specifies whether the static website feature is enabled,
            and if yes, indicates the index document and 404 error document to use.
        :type static_website:
            :class:`~azure.storage.file.models.StaticWebsite`
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """

    def list_shares(
            self, prefix=None,  # type: Optional[str]
            include_metadata=False,  # type: Optional[bool]
            include_snapshots=False, # type: Optional[bool]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> SharePropertiesPaged
        """Returns auto-paging iterable of dict-like ShareProperties under the specified account.
        The generator will lazily follow the continuation tokens returned by
        the service and stop when all shares have been returned.

        :param str prefix:
            Filters the results to return only shares whose names
            begin with the specified prefix.
        :param bool include_metadata:
            Specifies that share metadata be returned in the response.
        :param bool include_snapshots:
            Specifies that share snapshot be returned in the response.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An iterable (auto-paging) of ShareProperties.
        :rtype: ~azure.core.file.models.SharePropertiesPaged
        """

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
        """

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
        :param delete_snapshots:
            Indicates if snapshots are to be deleted.
        :type delete_snapshots: bool
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """

    def get_share_client(self, share_name, snapshot=None):
        # type: (Union[ShareProperties, str],Optional[Union[SnapshotProperties, str]]) -> ShareClient
        """Get a client to interact with the specified share.
        The share need not already exist.

        :param share:
            The share. This can either be the name of the share,
            or an instance of ShareProperties.
        :type share: str or ~azure.storage.file.models.ShareProperties
        :returns: A ShareClient.
        :rtype: ~azure.core.file.share_client.ShareClient
        """
