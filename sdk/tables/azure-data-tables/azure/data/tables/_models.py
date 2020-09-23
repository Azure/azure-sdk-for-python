# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum
from azure.core.exceptions import HttpResponseError
from azure.core.paging import PageIterator
from azure.data.tables._generated.models import TableServiceStats as GenTableServiceStats

from ._generated.models import AccessPolicy as GenAccessPolicy
from ._generated.models import Logging as GeneratedLogging
from ._generated.models import Metrics as GeneratedMetrics
from ._generated.models import RetentionPolicy as GeneratedRetentionPolicy
from ._generated.models import CorsRule as GeneratedCorsRule
from ._deserialize import (
    _convert_to_entity,
    _return_context_and_deserialized
)
from ._error import _process_table_error

class TableServiceStats(GenTableServiceStats):
    """Stats for the service
    :param geo_replication: Geo-Replication information for the Secondary Storage Service.
    :type geo_replication: ~azure_table.models.GeoReplication
    """

    def __init__(self, geo_replication=None, **kwargs):  # pylint:disable=W0231
        self.geo_replication = geo_replication


class AccessPolicy(GenAccessPolicy):
    """Access Policy class used by the set and get access policy methods.

    A stored access policy can specify the start time, expiry time, and
    permissions for the Shared Access Signatures with which it's associated.
    Depending on how you want to control access to your resource, you can
    specify all of these parameters within the stored access policy, and omit
    them from the URL for the Shared Access Signature. Doing so permits you to
    modify the associated signature's behavior at any time, as well as to revoke
    it. Or you can specify one or more of the access policy parameters within
    the stored access policy, and the others on the URL. Finally, you can
    specify all of the parameters on the URL. In this case, you can use the
    stored access policy to revoke the signature, but not to modify its behavior.

    Together the Shared Access Signature and the stored access policy must
    include all fields required to authenticate the signature. If any required
    fields are missing, the request will fail. Likewise, if a field is specified
    both in the Shared Access Signature URL and in the stored access policy, the
    request will fail with status code 400 (Bad Request).

    :param str permission:
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
    :type expiry: ~datetime.datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :type start: ~datetime.datetime or str
    """

    def __init__(self, permission=None, expiry=None, start=None, **kwargs):  # pylint:disable=W0231
        self.start = start
        self.expiry = expiry
        self.permission = permission


class TableAnalyticsLogging(GeneratedLogging):
    """Azure Analytics Logging settings.

   All required parameters must be populated in order to send to Azure.

   :keyword str version: Required. The version of Storage Analytics to configure.
   :keyword bool delete: Required. Indicates whether all delete requests should be logged.
   :keyword bool read: Required. Indicates whether all read requests should be logged.
   :keyword bool write: Required. Indicates whether all write requests should be logged.
   :keyword ~azure.data.tables.RetentionPolicy retention_policy: Required.
       The retention policy for the metrics.
   """

    def __init__(  # pylint:disable=W0231
            self,
            **kwargs  # type: Any
    ):
        # type: (...)-> None

        self.version = kwargs.get('version', u'1.0')
        self.delete = kwargs.get('delete', False)
        self.read = kwargs.get('read', False)
        self.write = kwargs.get('write', False)
        self.retention_policy = kwargs.get('retention_policy') or RetentionPolicy()

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            version=generated.version,
            delete=generated.delete,
            read=generated.read,
            write=generated.write,
            retention_policy=RetentionPolicy._from_generated(generated.retention_policy)  # pylint:disable=W0212
            # pylint: disable=protected-access
        )


class Metrics(GeneratedMetrics):
    """A summary of request statistics grouped by API in hour or minute aggregates.

    All required parameters must be populated in order to send to Azure.

    :keyword str version: The version of Storage Analytics to configure.
    :keyword bool enabled: Required. Indicates whether metrics are enabled for the service.
    :keyword bool include_ap_is: Indicates whether metrics should generate summary
        statistics for called API operations.
    :keyword ~azure.data.tables.RetentionPolicy retention_policy: Required.
        The retention policy for the metrics.
    """

    def __init__(self,  # pylint:disable=W0231
                 **kwargs  # type: Any
                 ):
        self.version = kwargs.get('version', u'1.0')
        self.enabled = kwargs.get('enabled', False)
        self.include_apis = kwargs.get('include_apis')
        self.retention_policy = kwargs.get('retention_policy') or RetentionPolicy()

    @classmethod
    def _from_generated(cls, generated):
        # type: (...) -> cls
        """A summary of request statistics grouped by API in hour or minute aggregates.

           :param Metrics generated: generated Metrics
           """
        if not generated:
            return cls()
        return cls(
            version=generated.version,
            enabled=generated.enabled,
            include_apis=generated.include_apis,
            retention_policy=RetentionPolicy._from_generated(generated.retention_policy)  # pylint:disable=W0212
            # pylint: disable=protected-access
        )


class RetentionPolicy(GeneratedRetentionPolicy):

    def __init__(  # pylint:disable=W0231
            self,
            enabled=False,  # type: bool
            days=None,  # type: int
            **kwargs  # type: Any
    ):
        # type: (...) ->None
        """The retention policy which determines how long the associated data should
          persist.

          All required parameters must be populated in order to send to Azure.

          :param bool enabled: Required. Indicates whether a retention policy is enabled
              for the storage service.
          :param int days: Indicates the number of days that metrics or logging or
              soft-deleted data should be retained. All data older than this value will
              be deleted.
          :param Any kwargs:
          """
        self.enabled = enabled
        self.days = days
        if self.enabled and (self.days is None):
            raise ValueError("If policy is enabled, 'days' must be specified.")

    @classmethod
    def _from_generated(cls, generated, **kwargs):  # pylint:disable=W0613
        # type: (...) -> cls
        """The retention policy which determines how long the associated data should
            persist.

            All required parameters must be populated in order to send to Azure.

            :param RetentionPolicy generated: Generated Retention Policy
            """

        if not generated:
            return cls()
        return cls(
            enabled=generated.enabled,
            days=generated.days,
        )


class CorsRule(GeneratedCorsRule):
    """CORS is an HTTP feature that enables a web application running under one
    domain to access resources in another domain. Web browsers implement a
    security restriction known as same-origin policy that prevents a web page
    from calling APIs in a different domain; CORS provides a secure way to
    allow one domain (the origin domain) to call APIs in another domain.

    All required parameters must be populated in order to send to Azure.

    :param list[str] allowed_origins:
        A list of origin domains that will be allowed via CORS, or "*" to allow
        all domains. The list of must contain at least one entry. Limited to 64
        origin domains. Each allowed origin can have up to 256 characters.
    :param list[str] allowed_methods:
        A list of HTTP methods that are allowed to be executed by the origin.
        The list of must contain at least one entry. For Azure Storage,
        permitted methods are DELETE, GET, HEAD, MERGE, POST, OPTIONS or PUT.
    :keyword int max_age_in_seconds:
        The number of seconds that the client/browser should cache a
        pre-flight response.
    :keyword list[str] exposed_headers:
        Defaults to an empty list. A list of response headers to expose to CORS
        clients. Limited to 64 defined headers and two prefixed headers. Each
        header can be up to 256 characters.
    :keyword list[str] allowed_headers:
        Defaults to an empty list. A list of headers allowed to be part of
        the cross-origin request. Limited to 64 defined headers and 2 prefixed
        headers. Each header can be up to 256 characters.
    """

    def __init__(  # pylint:disable=W0231
            self,
            allowed_origins,  # type: list[str]
            allowed_methods,  # type: list[str]
            **kwargs  # type: Any
    ):
        # type: (...)-> None

        self.allowed_origins = ','.join(allowed_origins)
        self.allowed_methods = ','.join(allowed_methods)
        self.allowed_headers = ','.join(kwargs.get('allowed_headers', []))
        self.exposed_headers = ','.join(kwargs.get('exposed_headers', []))
        self.max_age_in_seconds = kwargs.get('max_age_in_seconds', 0)

    @classmethod
    def _from_generated(cls, generated):
        return cls(
            [generated.allowed_origins],
            [generated.allowed_methods],
            allowed_headers=[generated.allowed_headers],
            exposed_headers=[generated.exposed_headers],
            max_age_in_seconds=generated.max_age_in_seconds,
        )


class TablePropertiesPaged(PageIterator):
    """An iterable of Table properties.

    :keyword str service_endpoint: The service URL.
    :keyword str prefix: A queue name prefix being used to filter the list.
    :keyword str marker: The continuation token of the current page of results.
    :keyword int results_per_page: The maximum number of results retrieved per API call.
    :keyword str next_marker: The continuation token to retrieve the next page of results.
    :keyword str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only queues whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of queue names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """

    def __init__(self, command, prefix=None, continuation_token=None):
        super(TablePropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.prefix = prefix
        self.next_table_name = None
        self._headers = None
        self.location_mode = None

    def _get_next_cb(self, continuation_token, **kwargs):
        try:
            return self._command(
                next_table_name=continuation_token or None,
                cls=kwargs.pop('cls', None) or _return_context_and_deserialized,
                use_location=self.location_mode
            )
        except HttpResponseError as error:
            _process_table_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response, self._headers = get_next_return
        props_list = [TableItem(t, self._headers) for t in self._response.value]
        return self._headers['x-ms-continuation-NextTableName'] or None, props_list


class TableEntityPropertiesPaged(PageIterator):
    """An iterable of TableEntity properties.

    :keyword str service_endpoint: The service URL.
    :keyword str prefix: A queue name prefix being used to filter the list.
    :keyword str marker: The continuation token of the current page of results.
    :keyword int results_per_page: The maximum number of results retrieved per API call.
    :keyword str next_marker: The continuation token to retrieve the next page of results.
    :keyword str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only queues whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of queue names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """

    def __init__(self, command, results_per_page=None, table=None,
                 continuation_token=None):
        super(TableEntityPropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=continuation_token or {}
        )
        self._command = command
        self._headers = None
        self.results_per_page = results_per_page
        self.table = table
        self.location_mode = None

    def _get_next_cb(self, continuation_token, **kwargs):
        row_key = ""
        partition_key = ""
        for key, value in continuation_token.items():
            if key == "RowKey":
                row_key = value
            if key == "PartitionKey":
                partition_key = value
        try:
            return self._command(
                query_options=self.results_per_page or None,
                next_row_key=row_key or None,
                next_partition_key=partition_key or None,
                table=self.table,
                cls=kwargs.pop('cls', None) or _return_context_and_deserialized,
                use_location=self.location_mode
            )
        except HttpResponseError as error:
            _process_table_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response, self._headers = get_next_return
        props_list = [_convert_to_entity(t) for t in self._response.value]
        next_entity = {}
        if self._headers['x-ms-continuation-NextPartitionKey'] or self._headers['x-ms-continuation-NextRowKey']:
            next_entity = {'PartitionKey': self._headers['x-ms-continuation-NextPartitionKey'],
                           'RowKey': self._headers['x-ms-continuation-NextRowKey']}
        return next_entity or None, props_list


class TableSasPermissions(object):
    def __init__(
            self,
            _str=None,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """
        :keyword bool read:
            Get entities and query entities.
        :keyword bool add:
            Add entities. Add and Update permissions are required for upsert operations.
        :keyword bool update:
            Update entities. Add and Update permissions are required for upsert operations.
        :keyword bool delete:
            Delete entities.
        :param str _str:
            A string representing the permissions.
        """
        if not _str:
            _str = ''
        self.read = kwargs.pop('read', None) or ('r' in _str)
        self.add = kwargs.pop('add', None) or ('a' in _str)
        self.update = kwargs.pop('update', None) or ('u' in _str)
        self.delete = kwargs.pop('delete', None) or ('d' in _str)

    def __or__(self, other):
        return TableSasPermissions(_str=str(self) + str(other))

    def __add__(self, other):
        return TableSasPermissions(_str=str(self) + str(other))

    def __str__(self):
        return (('r' if self.read else '') +
                ('a' if self.add else '') +
                ('u' if self.update else '') +
                ('d' if self.delete else ''))

    @classmethod
    def from_string(cls,
                    permission,  # type: str
                    **kwargs):  # pylint:disable=W0613
        """Create AccountSasPermissions from a string.

        To specify read, write, delete, etc. permissions you need only to
        include the first letter of the word in the string. E.g. for read and write
        permissions you would provide a string "rw".

        :param str permission: Specify permissions in
            the string with the first letter of the word.
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: A AccountSasPermissions object
        :rtype: ~azure.data.tables.AccountSasPermissions
        """
        p_read = 'r' in permission
        p_add = 'a' in permission
        p_delete = 'd' in permission
        p_update = 'u' in permission

        parsed = cls(
            **dict(kwargs, read=p_read, add=p_add, delete=p_delete, update=p_update))
        parsed._str = permission  # pylint: disable = W0201
        return parsed


TableSasPermissions.READ = TableSasPermissions(**dict(read=True))
TableSasPermissions.ADD = TableSasPermissions(**dict(add=True))
TableSasPermissions.UPDATE = TableSasPermissions(**dict(update=True))
TableSasPermissions.DELETE = TableSasPermissions(**dict(delete=True))


def service_stats_deserialize(generated):
    """Deserialize a ServiceStats objects into a dict.
    """
    return {
        'geo_replication': {
            'status': generated.geo_replication.status,
            'last_sync_time': generated.geo_replication.last_sync_time,
        }
    }


def service_properties_deserialize(generated):
    """Deserialize a ServiceProperties objects into a dict.
    """
    return {
        'analytics_logging': TableAnalyticsLogging._from_generated(generated.logging),
        # pylint: disable=protected-access
        'hour_metrics': Metrics._from_generated(generated.hour_metrics),  # pylint: disable=protected-access
        'minute_metrics': Metrics._from_generated(generated.minute_metrics),  # pylint: disable=protected-access
        'cors': [CorsRule._from_generated(cors) for cors in generated.cors],  # pylint: disable=protected-access
    }


class TableItem(object):
    """
    Represents an Azure TableItem. Returned by TableServiceClient.list_tables
    and TableServiceClient.query_tables.

    :ivar str name: The name of the table.
    :ivar str api_version: The API version included in the service call
    :ivar str date: The date the service call was made
    """

    def __init__(
        self,
        table, # type: str
        headers=None # type: dict[str,str]
    ):
        # type: (...) -> None
        self.table_name = table
        self.api_version = headers.pop('version', None)
        self.date = headers.pop('date', None) or headers.pop('Date', None)


class TablePayloadFormat(object):
    '''
    Specifies the accepted content type of the response payload. More information
    can be found here: https://msdn.microsoft.com/en-us/library/azure/dn535600.aspx
    '''

    JSON_NO_METADATA = 'application/json;odata=nometadata'
    '''Returns no type information for the entity properties.'''

    JSON_MINIMAL_METADATA = 'application/json;odata=minimalmetadata'
    '''Returns minimal type information for the entity properties.'''

    JSON_FULL_METADATA = 'application/json;odata=fullmetadata'
    '''Returns minimal type information for the entity properties plus some extra odata properties.'''


class UpdateMode(str, Enum):
    REPLACE = "replace"
    MERGE = "merge"


class SASProtocol(str, Enum):
    HTTPS = "https"
    HTTP = "http"


class PartialBatchErrorException(HttpResponseError):
    """There is a partial failure in batch operations.

    :param str message: The message of the exception.
    :param response: Server response to be deserialized.
    :param list parts: A list of the parts in multipart response.
    """

    def __init__(self, message, response, parts):
        self.parts = parts
        super(PartialBatchErrorException, self).__init__(message=message, response=response)



class LocationMode(object):
    """
    Specifies the location the request should be sent to. This mode only applies
    for RA-GRS accounts which allow secondary read access. All other account types
    must use PRIMARY.
    """

    PRIMARY = 'primary'  #: Requests should be sent to the primary location.
    SECONDARY = 'secondary'  #: Requests should be sent to the secondary location, if possible.


class ResourceTypes(object):
    """
    Specifies the resource types that are accessible with the account SAS.

    :param bool service:
        Access to service-level APIs (e.g., Get/Set Service Properties,
        Get Service Stats, List Containers/Queues/Shares)
    :param bool object:
        Access to object-level APIs for blobs, queue messages, and
        files(e.g. Put Blob, Query Entity, Get Messages, Create File, etc.)
    """

    def __init__(self, service=False, object=False):  # pylint: disable=redefined-builtin
        self.service = service
        self.object = object
        self._str = (('s' if self.service else '') +
                     ('o' if self.object else ''))

    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, string):
        """Create a ResourceTypes from a string.

        To specify service, container, or object you need only to
        include the first letter of the word in the string. E.g. service and container,
        you would provide a string "sc".

        :param str string: Specify service, container, or object in
            in the string with the first letter of the word.
        :return: A ResourceTypes object
        :rtype: ~azure.data.tables.ResourceTypes
        """
        res_service = 's' in string
        res_object = 'o' in string

        parsed = cls(res_service, res_object)
        parsed._str = string  # pylint: disable = protected-access
        return parsed


class AccountSasPermissions(object):
    """
    :class:`~ResourceTypes` class to be used with generate_account_sas
    function and for the AccessPolicies used with set_*_acl. There are two types of
    SAS which may be used to grant resource access. One is to grant access to a
    specific resource (resource-specific). Another is to grant access to the
    entire service for a specific account and allow certain operations based on
    perms found here.

    :ivar bool read:
        Valid for all signed resources types (Service, Container, and Object).
        Permits read permissions to the specified resource type.
    :ivar bool write:
        Valid for all signed resources types (Service, Container, and Object).
        Permits write permissions to the specified resource type.
    :ivar bool delete:
        Valid for Container and Object resource types, except for queue messages.
    :ivar bool list:
        Valid for Service and Container resource types only.
    :ivar bool add:
        Valid for the following Object resource types only: queue messages, and append blobs.
    :ivar bool create:
        Valid for the following Object resource types only: blobs and files.
        Users can create new blobs or files, but may not overwrite existing
        blobs or files.
    :ivar bool update:
        Valid for the following Object resource types only: queue messages.
    :ivar bool process:
        Valid for the following Object resource type only: queue messages.
    """

    def __init__(self, **kwargs):  # pylint: disable=redefined-builtin
        self.read = kwargs.pop('read', None)
        self.write = kwargs.pop('write', None)
        self.delete = kwargs.pop('delete', None)
        self.list = kwargs.pop('list', None)
        self.add = kwargs.pop('add', None)
        self.create = kwargs.pop('create', None)
        self.update = kwargs.pop('update', None)
        self.process = kwargs.pop('process', None)
        self._str = (('r' if self.read else '') +
                     ('w' if self.write else '') +
                     ('d' if self.delete else '') +
                     ('l' if self.list else '') +
                     ('a' if self.add else '') +
                     ('c' if self.create else '') +
                     ('u' if self.update else '') +
                     ('p' if self.process else ''))

    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, permission, **kwargs):  # pylint:disable=W0613
        """Create AccountSasPermissions from a string.

        To specify read, write, delete, etc. permissions you need only to
        include the first letter of the word in the string. E.g. for read and write
        permissions you would provide a string "rw".

        :param str permission: Specify permissions in
            the string with the first letter of the word.
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: A AccountSasPermissions object
        :rtype: ~azure.data.tables.AccountSasPermissions
        """
        p_read = 'r' in permission
        p_write = 'w' in permission
        p_delete = 'd' in permission
        p_list = 'l' in permission
        p_add = 'a' in permission
        p_create = 'c' in permission
        p_update = 'u' in permission
        p_process = 'p' in permission

        parsed = cls(
            **dict(kwargs, read=p_read, write=p_write, delete=p_delete, list=p_list, add=p_add, create=p_create,
                   update=p_update, process=p_process))
        parsed._str = permission  # pylint: disable = protected-access
        return parsed
