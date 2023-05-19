# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Classes and enums for documents in the Azure Cosmos database service.
"""

from . import _retry_options


class DatabaseAccount(object):  # pylint: disable=too-many-instance-attributes
    """Database account.

    A DatabaseAccount is the container for databases.

    :ivar str DatabaseLink:
        The self-link for Databases in the databaseAccount.
    :ivar str MediaLink:
        The self-link for Media in the databaseAccount.
    :ivar int MaxMediaStorageUsageInMB:
        Attachment content (media) storage quota in MBs (Retrieved from gateway).
    :ivar int CurrentMediaStorageUsageInMB:
        Current attachment content (media) usage in MBs (Retrieved from gateway).
        Value is returned from cached information updated periodically and
        is not guaranteed to be real time.
    :ivar dict ConsistencyPolicy:
        UserConsistencyPolicy settings.
    :ivar dict ConsistencyPolicy['defaultConsistencyLevel']:
        The default consistency level.
    :ivar int ConsistencyPolicy['maxStalenessPrefix']:
        In bounded staleness consistency, the maximum allowed staleness in
        terms difference in sequence numbers (aka version).
    :ivar int ConsistencyPolicy['maxStalenessIntervalInSeconds']:
        In bounded staleness consistency, the maximum allowed staleness in
        terms time interval.
    :ivar boolean EnableMultipleWritableLocations:
        Flag on the azure Cosmos account that indicates if writes can take
        place in multiple locations.
    """

    def __init__(self):
        self.DatabasesLink = ""
        self.MediaLink = ""
        self.MaxMediaStorageUsageInMB = 0
        self.CurrentMediaStorageUsageInMB = 0
        self.ConsumedDocumentStorageInMB = 0
        self.ReservedDocumentStorageInMB = 0
        self.ProvisionedDocumentStorageInMB = 0
        self.ConsistencyPolicy = None
        self._WritableLocations = []
        self._ReadableLocations = []
        self._EnableMultipleWritableLocations = False

    @property
    def WritableLocations(self):
        """The list of writable locations for a geo-replicated database account.
        """
        return self._WritableLocations

    @property
    def ReadableLocations(self):
        """The list of readable locations for a geo-replicated database account.
        """
        return self._ReadableLocations


class ConsistencyLevel(object):
    """Represents the consistency levels supported for Azure Cosmos client
    operations.

    The requested ConsistencyLevel must match or be weaker than that provisioned
    for the database account. Consistency levels.

    Consistency levels by order of strength are Strong, BoundedStaleness,
    Session, ConsistentPrefix and Eventual.

    :ivar str ConsistencyLevel.Strong:
        Strong Consistency guarantees that read operations always return the
        value that was last written.
    :ivar str ConsistencyLevel.BoundedStaleness:
        Bounded Staleness guarantees that reads are not too out-of-date. This
        can be configured based on number of operations (MaxStalenessPrefix)
        or time (MaxStalenessIntervalInSeconds).
    :ivar str ConsistencyLevel.Session:
        Session Consistency guarantees monotonic reads (you never read old data,
        then new, then old again), monotonic writes (writes are ordered) and
        read your writes (your writes are immediately visible to your reads)
        within any single session.
    :ivar str ConsistencyLevel.Eventual:
        Eventual Consistency guarantees that reads will return a subset of
        writes. All writes will be eventually be available for reads.
    :ivar str ConsistencyLevel.ConsistentPrefix:
        ConsistentPrefix Consistency guarantees that reads will return some
        prefix of all writes with no gaps. All writes will be eventually be
        available for reads.
    """

    Strong = "Strong"
    BoundedStaleness = "BoundedStaleness"
    Session = "Session"
    Eventual = "Eventual"
    ConsistentPrefix = "ConsistentPrefix"


class IndexingMode(object):
    """Specifies the supported indexing modes.

    :ivar str Consistent:
        Index is updated synchronously with a create or update operation. With
        consistent indexing, query behavior is the same as the default
        consistency level for the collection.

        The index is always kept up to date with the data.
    :ivar str Lazy:
        Index is updated asynchronously with respect to a create or update
        operation. Not supported for new containers since June/2020.

        With lazy indexing, queries are eventually consistent. The index is
        updated when the collection is idle.
    :ivar str NoIndex:
        No index is provided.

        Setting IndexingMode to "None" drops the index. Use this if you don't
        want to maintain the index for a document collection, to save the
        storage cost or improve the write throughput. Your queries will
        degenerate to scans of the entire collection.
    """

    Consistent = "consistent"
    Lazy = "lazy"
    NoIndex = "none"


class IndexKind(object):
    """Specifies the index kind of index specs.

    :ivar str IndexKind.Hash:
        The index entries are hashed to serve point look up queries.
        Can be used to serve queries like: SELECT * FROM docs d WHERE d.prop = 5

    :ivar str IndexKind.Range:
        The index entries are ordered. Range indexes are optimized for
        inequality predicate queries with efficient range scans.
        Can be used to serve queries like: SELECT * FROM docs d WHERE d.prop > 5
    """

    Hash = "Hash"
    Range = "Range"


class PartitionKind(object):
    """Specifies the kind of partitioning to be applied.

    :ivar str PartitionKind.Hash:
        The partition key definition path is hashed.
    """

    Hash = "Hash"


class DataType(object):
    """Specifies the data type of index specs.

    :ivar str Number:
        Represents a numeric data type.
    :ivar str String:
        Represents a string data type.
    :ivar str Point:
        Represents a point data type.
    :ivar str LineString:
        Represents a line string data type.
    :ivar str Polygon:
        Represents a polygon data type.
    :ivar str MultiPolygon:
        Represents a multi-polygon data type.
    """

    Number = "Number"
    String = "String"
    Point = "Point"
    LineString = "LineString"
    Polygon = "Polygon"
    MultiPolygon = "MultiPolygon"


class IndexingDirective(object):
    """Specifies whether or not the resource is to be indexed.

    :ivar int Default:
        Use any pre-defined/pre-configured defaults.
    :ivar int Exclude:
        Index the resource.
    :ivar int Include:
        Do not index the resource.
    """

    Default = 0
    Exclude = 1
    Include = 2


class ConnectionMode(object):
    """Represents the connection mode to be used by the client.

    :ivar int Gateway:
        Use the Azure Cosmos gateway to route all requests. The gateway proxies
        requests to the right data partition.
    """

    Gateway = 0


class PermissionMode(object):
    """Enumeration specifying applicability of a permission.

    :ivar str PermissionMode.NoneMode:
        None.
    :ivar str PermissionMode.Read:
        Permission applicable for read operations only.
    :ivar str PermissionMode.All:
        Permission applicable for all operations.
    """

    NoneMode = "none"  # None is python's key word.
    Read = "read"
    All = "all"


class TriggerType(object):
    """Specifies the type of a trigger.

    :ivar str TriggerType.Pre:
        Trigger should be executed before the associated operation(s).
    :ivar str TriggerType.Post:
        Trigger should be executed after the associated operation(s).
    """

    Pre = "pre"
    Post = "post"


class TriggerOperation(object):
    """Specifies the operations on which a trigger should be executed.

    :ivar str TriggerOperation.All:
        All operations.
    :ivar str TriggerOperation.Create:
        Create operations only.
    :ivar str TriggerOperation.Update:
        Update operations only.
    :ivar str TriggerOperation.Delete:
        Delete operations only.
    :ivar str TriggerOperation.Replace:
        Replace operations only.
    """

    All = "all"
    Create = "create"
    Update = "update"
    Delete = "delete"
    Replace = "replace"


class SSLConfiguration(object):
    """Configuration for SSL connections.

    See https://requests.readthedocs.io/en/master/user/advanced/#ssl-cert-verification
    for more information.

    :ivar str SSLKeyFIle:
        The path of the key file for ssl connection.
    :ivar str SSLCertFile:
        The path of the cert file for ssl connection.
    :ivar str SSLCaCerts:
        The path of the CA_BUNDLE file with certificates of trusted CAs.
    """

    def __init__(self):
        self.SSLKeyFile = None
        self.SSLCertFile = None
        self.SSLCaCerts = None


class ProxyConfiguration(object):
    """Configuration for a proxy.

    :ivar str Host:
        The host address of the proxy.
    :ivar int Port:
        The port number of the proxy.
    """

    def __init__(self):
        self.Host = None
        self.Port = None


class ConnectionPolicy(object):  # pylint: disable=too-many-instance-attributes
    """Represents the Connection policy associated with a CosmosClientConnection.

    :ivar int RequestTimeout:
        Gets or sets the request timeout (time to wait for a response from a
        network peer).
    :ivar documents.ConnectionMode ConnectionMode:
        Gets or sets the connection mode used in the client. (Currently only
        Gateway is supported.)
    :ivar documents.SSLConfiguration SSLConfiguration:
        Gets or sets the SSL configuration.
    :ivar documents.ProxyConfiguration ProxyConfiguration:
        Gets or sets the proxy configuration.
    :ivar boolean EnableEndpointDiscovery:
        Gets or sets endpoint discovery flag for geo-replicated database
        accounts. When EnableEndpointDiscovery is true, the client will
        automatically discover the current write and read locations and direct
        the requests to the correct location taking into consideration of the
        user's preference(if provided) as PreferredLocations.
    :ivar list PreferredLocations:
        Gets or sets the preferred locations for geo-replicated database
        accounts. When EnableEndpointDiscovery is true and PreferredLocations is
        non-empty, the client will use this list to evaluate the final location,
        taking into consideration the order specified in PreferredLocations. The
        locations in this list are specified as the names of the azure Cosmos
        locations like, 'West US', 'East US', 'Central India' and so on.
    :ivar RetryOptions RetryOptions:
        Gets or sets the retry options to be applied to all requests when
        retrying.
    :ivar boolean DisableSSLVerification:
        Flag to disable SSL verification for the requests. SSL verification is
        enabled by default.

        This is intended to be used only when targeting emulator endpoint to
        avoid failing your requests with SSL related error.

        DO NOT set this when targeting production endpoints.
    :ivar boolean UseMultipleWriteLocations:
        Flag to enable writes on any locations (regions) for geo-replicated
        database accounts in the Azure Cosmos database service.
    :ivar ConnectionRetryConfiguration:
        Retry Configuration to be used for connection retries.
    :vartype ConnectionRetryConfiguration:
        int or azure.cosmos.ConnectionRetryPolicy or urllib3.util.retry
    """

    __defaultRequestTimeout = 60  # seconds

    def __init__(self):
        self.RequestTimeout = self.__defaultRequestTimeout
        self.ConnectionMode = ConnectionMode.Gateway
        self.SSLConfiguration = None
        self.ProxyConfiguration = None
        self.EnableEndpointDiscovery = True
        self.PreferredLocations = []
        self.RetryOptions = _retry_options.RetryOptions()
        self.DisableSSLVerification = False
        self.UseMultipleWriteLocations = False
        self.ConnectionRetryConfiguration = None


class _OperationType(object):
    """Represents the type of the operation
    """
    Create = "Create"
    Delete = "Delete"
    ExecuteJavaScript = "ExecuteJavaScript"
    Head = "Head"
    HeadFeed = "HeadFeed"
    Patch = "Patch"
    Query = "Query"
    QueryPlan = "QueryPlan"
    Read = "Read"
    ReadFeed = "ReadFeed"
    Recreate = "Recreate"
    Replace = "Replace"
    SqlQuery = "SqlQuery"
    Update = "Update"
    Upsert = "Upsert"

    @staticmethod
    def IsWriteOperation(operationType):
        return operationType in (
            _OperationType.Create,
            _OperationType.Delete,
            _OperationType.Recreate,
            _OperationType.ExecuteJavaScript,
            _OperationType.Replace,
            _OperationType.Upsert,
            _OperationType.Update,
        )

    @staticmethod
    def IsReadOnlyOperation(operationType):
        return operationType in (
            _OperationType.Read,
            _OperationType.ReadFeed,
            _OperationType.Head,
            _OperationType.HeadFeed,
            _OperationType.Query,
            _OperationType.SqlQuery,
        )

    @staticmethod
    def IsFeedOperation(operationType):
        return operationType in (
            _OperationType.Create,
            _OperationType.Upsert,
            _OperationType.ReadFeed,
            _OperationType.Query,
            _OperationType.SqlQuery,
            _OperationType.QueryPlan,
            _OperationType.HeadFeed,
        )

class _QueryFeature(object):
    NoneQuery = "NoneQuery"
    Aggregate = "Aggregate"
    CompositeAggregate = "CompositeAggregate"
    Distinct = "Distinct"
    GroupBy = "GroupBy"
    MultipleAggregates = "MultipleAggregates"
    MultipleOrderBy = "MultipleOrderBy"
    OffsetAndLimit = "OffsetAndLimit"
    OrderBy = "OrderBy"
    Top = "Top"

class _DistinctType(object):
    NoneType = "None"
    Ordered = "Ordered"
    Unordered = "Unordered"
