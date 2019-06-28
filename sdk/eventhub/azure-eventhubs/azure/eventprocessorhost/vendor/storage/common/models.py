# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys

if sys.version_info < (3,):
    from collections import Iterable

    _unicode_type = unicode
else:
    from collections.abc import Iterable

    _unicode_type = str

from ._error import (
    _validate_not_none
)


class _HeaderDict(dict):
    def __getitem__(self, index):
        return super(_HeaderDict, self).__getitem__(index.lower())


class _list(list):
    '''Used so that additional properties can be set on the return list'''
    pass


class _dict(dict):
    '''Used so that additional properties can be set on the return dictionary'''
    pass


class _OperationContext(object):
    '''
    Contains information that lasts the lifetime of an operation. This operation 
    may span multiple calls to the Azure service.

    :ivar bool location_lock: 
        Whether the location should be locked for this operation.
    :ivar str location: 
        The location to lock to.
    '''

    def __init__(self, location_lock=False):
        self.location_lock = location_lock
        self.host_location = None


class ListGenerator(Iterable):
    '''
    A generator object used to list storage resources. The generator will lazily 
    follow the continuation tokens returned by the service and stop when all 
    resources have been returned or max_results is reached.

    If max_results is specified and the account has more than that number of 
    resources, the generator will have a populated next_marker field once it 
    finishes. This marker can be used to create a new generator if more 
    results are desired.
    '''

    def __init__(self, resources, list_method, list_args, list_kwargs):
        self.items = resources
        self.next_marker = resources.next_marker

        self._list_method = list_method
        self._list_args = list_args
        self._list_kwargs = list_kwargs

    def __iter__(self):
        # return results
        for i in self.items:
            yield i

        while True:
            # if no more results on the service, return
            if not self.next_marker:
                break

            # update the marker args
            self._list_kwargs['marker'] = self.next_marker

            # handle max results, if present
            max_results = self._list_kwargs.get('max_results')
            if max_results is not None:
                max_results = max_results - len(self.items)

                # if we've reached max_results, return
                # else, update the max_results arg
                if max_results <= 0:
                    break
                else:
                    self._list_kwargs['max_results'] = max_results

            # get the next segment
            resources = self._list_method(*self._list_args, **self._list_kwargs)
            self.items = resources
            self.next_marker = resources.next_marker

            # return results
            for i in self.items:
                yield i


class RetryContext(object):
    '''
    Contains the request and response information that can be used to determine 
    whether and how to retry. This context is stored across retries and may be 
    used to store other information relevant to the retry strategy.

    :ivar ~azure.storage.common._http.HTTPRequest request:
        The request sent to the storage service.
    :ivar ~azure.storage.common._http.HTTPResponse response:
        The response returned by the storage service.
    :ivar LocationMode location_mode:
        The location the request was sent to.
    :ivar Exception exception:
        The exception that just occurred. The type could either be AzureException (for HTTP errors),
        or other Exception types from lower layers, which are kept unwrapped for easier processing.
    :ivar bool is_emulated:
        Whether retry is targeting the emulator. The default value is False.
    :ivar int body_position:
        The initial position of the body stream. It is useful when retries happen and we need to rewind the stream.
    '''

    def __init__(self):
        self.request = None
        self.response = None
        self.location_mode = None
        self.exception = None
        self.is_emulated = False
        self.body_position = None


class LocationMode(object):
    '''
    Specifies the location the request should be sent to. This mode only applies 
    for RA-GRS accounts which allow secondary read access. All other account types 
    must use PRIMARY.
    '''

    PRIMARY = 'primary'
    ''' Requests should be sent to the primary location. '''

    SECONDARY = 'secondary'
    ''' Requests should be sent to the secondary location, if possible. '''


class RetentionPolicy(object):
    '''
    By default, Storage Analytics will not delete any logging or metrics data. Blobs
    will continue to be written until the shared 20TB limit is
    reached. Once the 20TB limit is reached, Storage Analytics will stop writing 
    new data and will not resume until free space is available. This 20TB limit 
    is independent of the total limit for your storage account.

    There are two ways to delete Storage Analytics data: by manually making deletion 
    requests or by setting a data retention policy. Manual requests to delete Storage 
    Analytics data are billable, but delete requests resulting from a retention policy 
    are not billable.
    '''

    def __init__(self, enabled=False, days=None):
        '''
        :param bool enabled: 
            Indicates whether a retention policy is enabled for the 
            storage service. If disabled, logging and metrics data will be retained 
            infinitely by the service unless explicitly deleted.
        :param int days: 
            Required if enabled is true. Indicates the number of 
            days that metrics or logging data should be retained. All data older 
            than this value will be deleted. The minimum value you can specify is 1; 
            the largest value is 365 (one year).
        '''
        _validate_not_none("enabled", enabled)
        if enabled:
            _validate_not_none("days", days)

        self.enabled = enabled
        self.days = days


class Logging(object):
    '''
    Storage Analytics logs detailed information about successful and failed requests 
    to a storage service. This information can be used to monitor individual requests 
    and to diagnose issues with a storage service. Requests are logged on a best-effort 
    basis.

    All logs are stored in block blobs in a container named $logs, which is
    automatically created when Storage Analytics is enabled for a storage account. 
    The $logs container is located in the blob namespace of the storage account. 
    This container cannot be deleted once Storage Analytics has been enabled, though 
    its contents can be deleted.

    For more information, see  https://msdn.microsoft.com/en-us/library/azure/hh343262.aspx
    '''

    def __init__(self, delete=False, read=False, write=False,
                 retention_policy=None):
        '''
        :param bool delete: 
            Indicates whether all delete requests should be logged.
        :param bool read: 
            Indicates whether all read requests should be logged.
        :param bool write: 
            Indicates whether all write requests should be logged.
        :param RetentionPolicy retention_policy: 
            The retention policy for the metrics.
        '''
        _validate_not_none("read", read)
        _validate_not_none("write", write)
        _validate_not_none("delete", delete)

        self.version = u'1.0'
        self.delete = delete
        self.read = read
        self.write = write
        self.retention_policy = retention_policy if retention_policy else RetentionPolicy()


class Metrics(object):
    '''
    Metrics include aggregated transaction statistics and capacity data about requests 
    to a storage service. Transactions are reported at both the API operation level 
    as well as at the storage service level, and capacity is reported at the storage 
    service level. Metrics data can be used to analyze storage service usage, diagnose 
    issues with requests made against the storage service, and to improve the 
    performance of applications that use a service.

    For more information, see https://msdn.microsoft.com/en-us/library/azure/hh343258.aspx
    '''

    def __init__(self, enabled=False, include_apis=None,
                 retention_policy=None):
        '''
        :param bool enabled: 
            Indicates whether metrics are enabled for 
            the service.
        :param bool include_apis: 
            Required if enabled is True. Indicates whether metrics 
            should generate summary statistics for called API operations.
        :param RetentionPolicy retention_policy: 
            The retention policy for the metrics.
        '''
        _validate_not_none("enabled", enabled)
        if enabled:
            _validate_not_none("include_apis", include_apis)

        self.version = u'1.0'
        self.enabled = enabled
        self.include_apis = include_apis
        self.retention_policy = retention_policy if retention_policy else RetentionPolicy()


class CorsRule(object):
    '''
    CORS is an HTTP feature that enables a web application running under one domain 
    to access resources in another domain. Web browsers implement a security 
    restriction known as same-origin policy that prevents a web page from calling 
    APIs in a different domain; CORS provides a secure way to allow one domain 
    (the origin domain) to call APIs in another domain. 

    For more information, see https://msdn.microsoft.com/en-us/library/azure/dn535601.aspx
    '''

    def __init__(self, allowed_origins, allowed_methods, max_age_in_seconds=0,
                 exposed_headers=None, allowed_headers=None):
        '''
        :param allowed_origins: 
            A list of origin domains that will be allowed via CORS, or "*" to allow 
            all domains. The list of must contain at least one entry. Limited to 64 
            origin domains. Each allowed origin can have up to 256 characters.
        :type allowed_origins: list(str)
        :param allowed_methods:
            A list of HTTP methods that are allowed to be executed by the origin. 
            The list of must contain at least one entry. For Azure Storage, 
            permitted methods are DELETE, GET, HEAD, MERGE, POST, OPTIONS or PUT.
        :type allowed_methods: list(str)
        :param int max_age_in_seconds:
            The number of seconds that the client/browser should cache a 
            preflight response.
        :param exposed_headers:
            Defaults to an empty list. A list of response headers to expose to CORS 
            clients. Limited to 64 defined headers and two prefixed headers. Each 
            header can be up to 256 characters.
        :type exposed_headers: list(str)
        :param allowed_headers:
            Defaults to an empty list. A list of headers allowed to be part of 
            the cross-origin request. Limited to 64 defined headers and 2 prefixed 
            headers. Each header can be up to 256 characters.
        :type allowed_headers: list(str)
        '''
        _validate_not_none("allowed_origins", allowed_origins)
        _validate_not_none("allowed_methods", allowed_methods)
        _validate_not_none("max_age_in_seconds", max_age_in_seconds)

        self.allowed_origins = allowed_origins if allowed_origins else list()
        self.allowed_methods = allowed_methods if allowed_methods else list()
        self.max_age_in_seconds = max_age_in_seconds
        self.exposed_headers = exposed_headers if exposed_headers else list()
        self.allowed_headers = allowed_headers if allowed_headers else list()


class DeleteRetentionPolicy(object):
    '''
    To set DeleteRetentionPolicy, you must call Set Blob Service Properties using version 2017-07-29 or later.
    This class groups the settings related to delete retention policy.
    '''

    def __init__(self, enabled=False, days=None):
        '''
        :param bool enabled:
            Required. Indicates whether a deleted blob or snapshot is retained or immediately removed by delete operation.
        :param int days:
            Required only if Enabled is true. Indicates the number of days that deleted blob be retained.
            All data older than this value will be permanently deleted.
            The minimum value you can specify is 1; the largest value is 365.
        '''
        _validate_not_none("enabled", enabled)
        if enabled:
            _validate_not_none("days", days)

        self.enabled = enabled
        self.days = days


class StaticWebsite(object):
    '''
    Class representing the service properties pertaining to static websites.
    To set StaticWebsite, you must call Set Blob Service Properties using version 2018-03-28 or later.
    '''

    def __init__(self, enabled=False, index_document=None, error_document_404_path=None):
        '''
        :param bool enabled:
            Required. True if static websites should be enabled on the blob service for the corresponding Storage Account.
        :param str index_document:
            Represents the name of the index document. This is commonly "index.html".
        :param str error_document_404_path:
            Represents the path to the error document that should be shown when an error 404 is issued,
            in other words, when a browser requests a page that does not exist.
        '''
        _validate_not_none("enabled", enabled)

        self.enabled = enabled
        self.index_document = index_document
        self.error_document_404_path = error_document_404_path


class ServiceProperties(object):
    ''' 
    Returned by get_*_service_properties functions. Contains the properties of a 
    storage service, including Analytics and CORS rules.

    Azure Storage Analytics performs logging and provides metrics data for a storage 
    account. You can use this data to trace requests, analyze usage trends, and 
    diagnose issues with your storage account. To use Storage Analytics, you must 
    enable it individually for each service you want to monitor.

    The aggregated data is stored in a well-known blob (for logging) and in well-known 
    tables (for metrics), which may be accessed using the Blob service and Table 
    service APIs.

    For an in-depth guide on using Storage Analytics and other tools to identify, 
    diagnose, and troubleshoot Azure Storage-related issues, see 
    http://azure.microsoft.com/documentation/articles/storage-monitoring-diagnosing-troubleshooting/

    For more information on CORS, see https://msdn.microsoft.com/en-us/library/azure/dn535601.aspx
    '''

    pass


class ServiceStats(object):
    ''' 
    Returned by get_*_service_stats functions. Contains statistics related to 
    replication for the given service. It is only available when read-access 
    geo-redundant replication is enabled for the storage account.

    :ivar GeoReplication geo_replication:
        An object containing statistics related to replication for the given service.
    '''
    pass


class GeoReplication(object):
    ''' 
    Contains statistics related to replication for the given service.

    :ivar str status:
        The status of the secondary location. Possible values are:
            live: Indicates that the secondary location is active and operational.
            bootstrap: Indicates initial synchronization from the primary location 
                to the secondary location is in progress. This typically occurs 
                when replication is first enabled.
            unavailable: Indicates that the secondary location is temporarily 
                unavailable.
    :ivar date last_sync_time:
        A GMT date value, to the second. All primary writes preceding this value 
        are guaranteed to be available for read operations at the secondary. 
        Primary writes after this point in time may or may not be available for 
        reads. The value may be empty if LastSyncTime is not available. This can 
        happen if the replication status is bootstrap or unavailable. Although 
        geo-replication is continuously enabled, the LastSyncTime result may 
        reflect a cached value from the service that is refreshed every few minutes.
    '''
    pass


class AccessPolicy(object):
    '''
    Access Policy class used by the set and get acl methods in each service.

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
    '''

    def __init__(self, permission=None, expiry=None, start=None):
        '''
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
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If 
            omitted, start time for this call is assumed to be the time when the 
            storage service receives the request. Azure will always convert values 
            to UTC. If a date is passed in without timezone info, it is assumed to 
            be UTC.
        :type start: datetime or str
        '''
        self.start = start
        self.expiry = expiry
        self.permission = permission


class Protocol(object):
    '''
    Specifies the protocol permitted for a SAS token. Note that HTTP only is 
    not allowed.
    '''

    HTTPS = 'https'
    ''' Allow HTTPS requests only. '''

    HTTPS_HTTP = 'https,http'
    ''' Allow HTTP and HTTPS requests. '''


class ResourceTypes(object):
    '''
    Specifies the resource types that are accessible with the account SAS.

    :ivar ResourceTypes ResourceTypes.CONTAINER:
        Access to container-level APIs (e.g., Create/Delete Container, 
        Create/Delete Queue, Create/Delete Share,
        List Blobs/Files and Directories) 
    :ivar ResourceTypes ResourceTypes.OBJECT:
        Access to object-level APIs for blobs, queue messages, and
        files(e.g. Put Blob, Query Entity, Get Messages, Create File, etc.) 
    :ivar ResourceTypes ResourceTypes.SERVICE:
        Access to service-level APIs (e.g., Get/Set Service Properties, 
        Get Service Stats, List Containers/Queues/Shares)
    '''

    def __init__(self, service=False, container=False, object=False, _str=None):
        '''
        :param bool service:
            Access to service-level APIs (e.g., Get/Set Service Properties, 
            Get Service Stats, List Containers/Queues/Shares)
        :param bool container:
            Access to container-level APIs (e.g., Create/Delete Container, 
            Create/Delete Queue, Create/Delete Share,
            List Blobs/Files and Directories) 
        :param bool object:
            Access to object-level APIs for blobs, queue messages, and
            files(e.g. Put Blob, Query Entity, Get Messages, Create File, etc.) 
        :param str _str: 
            A string representing the resource types.
        '''
        if not _str:
            _str = ''
        self.service = service or ('s' in _str)
        self.container = container or ('c' in _str)
        self.object = object or ('o' in _str)

    def __or__(self, other):
        return ResourceTypes(_str=str(self) + str(other))

    def __add__(self, other):
        return ResourceTypes(_str=str(self) + str(other))

    def __str__(self):
        return (('s' if self.service else '') +
                ('c' if self.container else '') +
                ('o' if self.object else ''))


ResourceTypes.SERVICE = ResourceTypes(service=True)
ResourceTypes.CONTAINER = ResourceTypes(container=True)
ResourceTypes.OBJECT = ResourceTypes(object=True)


class Services(object):
    '''
    Specifies the services accessible with the account SAS.

    :ivar Services Services.BLOB: The blob service.
    :ivar Services Services.FILE: The file service
    :ivar Services Services.QUEUE: The queue service.
    :ivar Services Services.TABLE: The table service.
    '''

    def __init__(self, blob=False, queue=False, file=False, table=False, _str=None):
        '''
        :param bool blob:
            Access to any blob service, for example, the `.BlockBlobService`
        :param bool queue:
            Access to the `.QueueService`
        :param bool file:
            Access to the `.FileService`
        :param bool table:
            Access to the TableService
        :param str _str: 
            A string representing the services.
        '''
        if not _str:
            _str = ''
        self.blob = blob or ('b' in _str)
        self.queue = queue or ('q' in _str)
        self.file = file or ('f' in _str)
        self.table = table or ('t' in _str)

    def __or__(self, other):
        return Services(_str=str(self) + str(other))

    def __add__(self, other):
        return Services(_str=str(self) + str(other))

    def __str__(self):
        return (('b' if self.blob else '') +
                ('q' if self.queue else '') +
                ('t' if self.table else '') +
                ('f' if self.file else ''))


Services.BLOB = Services(blob=True)
Services.QUEUE = Services(queue=True)
Services.TABLE = Services(table=True)
Services.FILE = Services(file=True)


class AccountPermissions(object):
    '''
    :class:`~ResourceTypes` class to be used with generate_shared_access_signature 
    method and for the AccessPolicies used with set_*_acl. There are two types of 
    SAS which may be used to grant resource access. One is to grant access to a 
    specific resource (resource-specific). Another is to grant access to the 
    entire service for a specific account and allow certain operations based on 
    perms found here.

    :ivar AccountPermissions AccountPermissions.ADD:
        Valid for the following Object resource types only: queue messages and append blobs.
    :ivar AccountPermissions AccountPermissions.CREATE:
        Valid for the following Object resource types only: blobs and files. Users 
        can create new blobs or files, but may not overwrite existing blobs or files. 
    :ivar AccountPermissions AccountPermissions.DELETE:
        Valid for Container and Object resource types, except for queue messages. 
    :ivar AccountPermissions AccountPermissions.LIST:
        Valid for Service and Container resource types only. 
    :ivar AccountPermissions AccountPermissions.PROCESS:
        Valid for the following Object resource type only: queue messages. 
    :ivar AccountPermissions AccountPermissions.READ:
        Valid for all signed resources types (Service, Container, and Object). 
        Permits read permissions to the specified resource type. 
    :ivar AccountPermissions AccountPermissions.UPDATE:
        Valid for the following Object resource types only: queue messages.
    :ivar AccountPermissions AccountPermissions.WRITE:
        Valid for all signed resources types (Service, Container, and Object). 
        Permits write permissions to the specified resource type. 
    '''

    def __init__(self, read=False, write=False, delete=False, list=False,
                 add=False, create=False, update=False, process=False, _str=None):
        '''
        :param bool read:
            Valid for all signed resources types (Service, Container, and Object). 
            Permits read permissions to the specified resource type.
        :param bool write:
            Valid for all signed resources types (Service, Container, and Object). 
            Permits write permissions to the specified resource type.
        :param bool delete: 
            Valid for Container and Object resource types, except for queue messages.
        :param bool list:
            Valid for Service and Container resource types only.
        :param bool add:
            Valid for the following Object resource types only: queue messages, and append blobs.
        :param bool create:
            Valid for the following Object resource types only: blobs and files. 
            Users can create new blobs or files, but may not overwrite existing 
            blobs or files.
        :param bool update:
            Valid for the following Object resource types only: queue messages.
        :param bool process:
            Valid for the following Object resource type only: queue messages.
        :param str _str: 
            A string representing the permissions.
        '''
        if not _str:
            _str = ''
        self.read = read or ('r' in _str)
        self.write = write or ('w' in _str)
        self.delete = delete or ('d' in _str)
        self.list = list or ('l' in _str)
        self.add = add or ('a' in _str)
        self.create = create or ('c' in _str)
        self.update = update or ('u' in _str)
        self.process = process or ('p' in _str)

    def __or__(self, other):
        return AccountPermissions(_str=str(self) + str(other))

    def __add__(self, other):
        return AccountPermissions(_str=str(self) + str(other))

    def __str__(self):
        return (('r' if self.read else '') +
                ('w' if self.write else '') +
                ('d' if self.delete else '') +
                ('l' if self.list else '') +
                ('a' if self.add else '') +
                ('c' if self.create else '') +
                ('u' if self.update else '') +
                ('p' if self.process else ''))


AccountPermissions.READ = AccountPermissions(read=True)
AccountPermissions.WRITE = AccountPermissions(write=True)
AccountPermissions.DELETE = AccountPermissions(delete=True)
AccountPermissions.LIST = AccountPermissions(list=True)
AccountPermissions.ADD = AccountPermissions(add=True)
AccountPermissions.CREATE = AccountPermissions(create=True)
AccountPermissions.UPDATE = AccountPermissions(update=True)
AccountPermissions.PROCESS = AccountPermissions(process=True)
