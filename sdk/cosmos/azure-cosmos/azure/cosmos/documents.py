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

from typing import List, Optional, TYPE_CHECKING, Union
from typing_extensions import Literal, TypedDict

from ._retry_options import RetryOptions

if TYPE_CHECKING:
    from ._retry_utility import ConnectionRetryPolicy


class UserConsistencyPolicy(TypedDict, total=False):
    defaultConsistencyLevel: str
    """The default consistency level."""
    maxStalenessPrefix: int
    """In bounded staleness consistency, the maximum allowed staleness in
    terms difference in sequence numbers (aka version)."""
    maxStalenessIntervalInSeconds: int
    """In bounded staleness consistency, the maximum allowed staleness in
    terms time interval."""


class DatabaseAccount:  # pylint: disable=too-many-instance-attributes
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
    :ivar ConsistencyPolicy:
        UserConsistencyPolicy settings.
    :vartype ConsistencyPolicy: Dict[str, Union[str, int]]
    :ivar boolean EnableMultipleWritableLocations:
        Flag on the azure Cosmos account that indicates if writes can take
        place in multiple locations.
    """

    def __init__(self) -> None:
        self.DatabasesLink: str = ""
        self.MediaLink: str = ""
        self.MaxMediaStorageUsageInMB: int = 0
        self.CurrentMediaStorageUsageInMB: int = 0
        self.ConsumedDocumentStorageInMB: int = 0
        self.ReservedDocumentStorageInMB: int = 0
        self.ProvisionedDocumentStorageInMB: int = 0
        self.ConsistencyPolicy: Optional[UserConsistencyPolicy] = None
        self._WritableLocations: List[str] = []
        self._ReadableLocations: List[str] = []
        self._EnableMultipleWritableLocations = False

    @property
    def WritableLocations(self) -> List[str]:
        """The list of writable locations for a geo-replicated database account.
        :returns: List of writable locations for the database account.
        :rtype: List[str]
        """
        return self._WritableLocations

    @property
    def ReadableLocations(self) -> List[str]:
        """The list of readable locations for a geo-replicated database account.
        :returns: List of readable locations for the database account.
        :rtype: List[str]
        """
        return self._ReadableLocations


class ConsistencyLevel:
    """Represents the consistency levels supported for Azure Cosmos client
    operations.

    The requested ConsistencyLevel must match or be weaker than that provisioned
    for the database account. Consistency levels.

    Consistency levels by order of strength are Strong, BoundedStaleness,
    Session, ConsistentPrefix and Eventual.
    """
    Strong: Literal["Strong"] = "Strong"
    """Strong Consistency guarantees that read operations always return the
    value that was last written.
    """
    BoundedStaleness: Literal["BoundedStaleness"] = "BoundedStaleness"
    """Bounded Staleness guarantees that reads are not too out-of-date. This
    can be configured based on number of operations (MaxStalenessPrefix)
    or time (MaxStalenessIntervalInSeconds).
    """
    Session: Literal["Session"] = "Session"
    """Session Consistency guarantees monotonic reads (you never read old data,
    then new, then old again), monotonic writes (writes are ordered) and
    read your writes (your writes are immediately visible to your reads)
    within any single session.
    """
    Eventual: Literal["Eventual"] = "Eventual"
    """Eventual Consistency guarantees that reads will return a subset of
    writes. All writes will be eventually be available for reads.
    """
    ConsistentPrefix: Literal["ConsistentPrefix"] = "ConsistentPrefix"
    """ConsistentPrefix Consistency guarantees that reads will return some
    prefix of all writes with no gaps. All writes will be eventually be
    available for reads.
    """


class IndexingMode:
    """Specifies the supported indexing modes."""
    Consistent: Literal["consistent"] = "consistent"
    """Index is updated synchronously with a create or update operation. With
    consistent indexing, query behavior is the same as the default
    consistency level for the collection.
    The index is always kept up to date with the data.
    """
    Lazy: Literal["lazy"] = "lazy"
    """Index is updated asynchronously with respect to a create or update
    operation. Not supported for new containers since June/2020.
    With lazy indexing, queries are eventually consistent. The index is
    updated when the collection is idle.
    """
    NoIndex: Literal["none"] = "none"
    """No index is provided.
    Setting IndexingMode to "None" drops the index. Use this if you don't
    want to maintain the index for a document collection, to save the
    storage cost or improve the write throughput. Your queries will
    degenerate to scans of the entire collection.
    """


class IndexKind:
    """Specifies the index kind of index specs."""
    Hash: Literal["Hash"] = "Hash"
    """The index entries are hashed to serve point look up queries.
    Can be used to serve queries like: SELECT * FROM docs d WHERE d.prop = 5
    """
    Range: Literal["Range"] = "Range"
    """
    The index entries are ordered. Range indexes are optimized for
    inequality predicate queries with efficient range scans.
    Can be used to serve queries like: SELECT * FROM docs d WHERE d.prop > 5
    """
    MultiHash: Literal["MultiHash"] = "MultiHash"
    """MultiHash"""


class PartitionKind:
    """Specifies the kind of partitioning to be applied."""
    Hash: Literal["Hash"] = "Hash"
    """The partition key definition path is hashed."""
    MultiHash: Literal["MultiHash"] = "MultiHash"
    """MultiHash"""


class DataType:
    """Specifies the data type of index specs."""
    Number: Literal["Number"] = "Number"
    """Represents a numeric data type."""
    String: Literal["String"] = "String"
    """Represents a string data type."""
    Point: Literal["Point"] = "Point"
    """Represents a point data type."""
    LineString: Literal["LineString"] = "LineString"
    """Represents a line string data type."""
    Polygon: Literal["Polygon"] = "Polygon"
    """Represents a polygon data type."""
    MultiPolygon: Literal["MultiPolygon"] = "MultiPolygon"
    """Represents a multi-polygon data type."""


class IndexingDirective:
    """Specifies whether or not the resource is to be indexed."""
    Default: int = 0
    """Use any pre-defined/pre-configured defaults."""
    Exclude: int = 1
    """Index the resource."""
    Include: int = 2
    """Do not index the resource."""


class ConnectionMode:
    """Represents the connection mode to be used by the client."""
    Gateway: int = 0
    """Use the Azure Cosmos gateway to route all requests. The gateway proxies
    requests to the right data partition.
    """


class PermissionMode:
    """Applicability of a permission."""
    NoneMode: Literal["none"] = "none"  # None is python's key word.
    """None"""
    Read: Literal["read"] = "read"
    """Permission applicable for read operations only."""
    All: Literal["all"] = "all"
    """Permission applicable for all operations."""


class TriggerType:
    """Specifies the type of a trigger."""
    Pre: Literal["pre"] = "pre"
    """Trigger should be executed before the associated operation(s)."""
    Post: Literal["post"] = "post"
    """Trigger should be executed after the associated operation(s)."""


class TriggerOperation:
    """Specifies the operations on which a trigger should be executed."""
    All: Literal["all"] = "all"
    """All operations."""
    Create: Literal["create"] = "create"
    """Create operations only."""
    Update: Literal["update"] = "update"
    """Update operations only."""
    Delete: Literal["delete"] = "delete"
    """Delete operations only."""
    Replace: Literal["replace"] = "replace"
    """Replace operations only."""


class SSLConfiguration:
    """Configuration for SSL connections.

    See https://requests.readthedocs.io/en/master/user/advanced/#ssl-cert-verification
    for more information.

    :ivar str SSLKeyFIle:
        The path of the key file for ssl connection.
    :ivar str SSLCertFile:
        The path of the cert file for ssl connection.
    :ivar SSLCaCerts:
        The path of the CA_BUNDLE file with certificates of trusted CAs.
    :vartype SSLCaCerts: str or bool
    """
    def __init__(self) -> None:
        self.SSLKeyFile: Optional[str] = None
        self.SSLCertFile: Optional[str] = None
        self.SSLCaCerts: Optional[Union[str, bool]] = None


class ProxyConfiguration:
    """Configuration for a proxy.

    :ivar str Host:
        The host address of the proxy.
    :ivar int Port:
        The port number of the proxy.
    """
    def __init__(self) -> None:
        self.Host: Optional[str] = None
        self.Port: Optional[int] = None


class ConnectionPolicy:  # pylint: disable=too-many-instance-attributes
    """Represents the Connection policy associated with a CosmosClientConnection.

    :ivar int RequestTimeout:
        Gets or sets the request timeout (time to wait for a response from a
        network peer).
    :ivar ConnectionMode:
        Gets or sets the connection mode used in the client. (Currently only
        Gateway is supported.)
    :vartype ConnectionMode: ~azure.cosmos.documents.ConnectionMode
    :ivar SSLConfiguration:
        Gets or sets the SSL configuration.
    :vartype SSLConfiguration: ~azure.cosmos.documents.SSLConfiguration
    :ivar ProxyConfiguration:
        Gets or sets the proxy configuration.
    :vartype ProxyConfiguration: ~azure.cosmos.documents.ProxyConfiguration
    :ivar boolean EnableEndpointDiscovery:
        Gets or sets endpoint discovery flag for geo-replicated database
        accounts. When EnableEndpointDiscovery is true, the client will
        automatically discover the current write and read locations and direct
        the requests to the correct location taking into consideration of the
        user's preference(if provided) as PreferredLocations.
    :ivar PreferredLocations:
        Gets or sets the preferred locations for geo-replicated database
        accounts. When EnableEndpointDiscovery is true and PreferredLocations is
        non-empty, the client will use this list to evaluate the final location,
        taking into consideration the order specified in PreferredLocations. The
        locations in this list are specified as the names of the azure Cosmos
        locations like, 'West US', 'East US', 'Central India' and so on.
    :vartype PreferredLocations: List[str]
    :ivar RetryOptions:
        Gets or sets the retry options to be applied to all requests when
        retrying.
    :vartype RetryOptions: ~RetryOptions
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
        int or ~azure.cosmos.ConnectionRetryPolicy
    """

    __defaultRequestTimeout: int = 60  # seconds

    def __init__(self) -> None:
        self.RequestTimeout: int = self.__defaultRequestTimeout
        self.ConnectionMode: int = ConnectionMode.Gateway
        self.SSLConfiguration: Optional[SSLConfiguration] = None
        self.ProxyConfiguration: Optional[ProxyConfiguration] = None
        self.EnableEndpointDiscovery: bool = True
        self.PreferredLocations: List[str] = []
        self.RetryOptions: RetryOptions = RetryOptions()
        self.DisableSSLVerification: bool = False
        self.UseMultipleWriteLocations: bool = False
        self.ConnectionRetryConfiguration: Optional["ConnectionRetryPolicy"] = None


class _OperationType:
    """Represents the type of the operation"""
    Create: Literal["Create"] = "Create"
    Delete: Literal["Delete"] = "Delete"
    ExecuteJavaScript: Literal["ExecuteJavaScript"] = "ExecuteJavaScript"
    Head: Literal["Head"] = "Head"
    HeadFeed: Literal["HeadFeed"] = "HeadFeed"
    Patch: Literal["Patch"] = "Patch"
    Query: Literal["Query"] = "Query"
    QueryPlan: Literal["QueryPlan"] = "QueryPlan"
    Read: Literal["Read"] = "Read"
    ReadFeed: Literal["ReadFeed"] = "ReadFeed"
    Recreate: Literal["Recreate"] = "Recreate"
    Replace: Literal["Replace"] = "Replace"
    SqlQuery: Literal["SqlQuery"] = "SqlQuery"
    Update: Literal["Update"] = "Update"
    Upsert: Literal["Upsert"] = "Upsert"
    Batch: Literal["Batch"] = "Batch"

    @staticmethod
    def IsWriteOperation(operationType: str) -> bool:
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
    def IsReadOnlyOperation(operationType: str) -> bool:
        return operationType in (
            _OperationType.Read,
            _OperationType.ReadFeed,
            _OperationType.Head,
            _OperationType.HeadFeed,
            _OperationType.Query,
            _OperationType.SqlQuery,
        )

    @staticmethod
    def IsFeedOperation(operationType: str) -> bool:
        return operationType in (
            _OperationType.Create,
            _OperationType.Upsert,
            _OperationType.ReadFeed,
            _OperationType.Query,
            _OperationType.SqlQuery,
            _OperationType.QueryPlan,
            _OperationType.HeadFeed,
        )


class _QueryFeature:
    NoneQuery: Literal["NoneQuery"] = "NoneQuery"
    Aggregate: Literal["Aggregate"] = "Aggregate"
    CompositeAggregate: Literal["CompositeAggregate"] = "CompositeAggregate"
    Distinct: Literal["Distinct"] = "Distinct"
    GroupBy: Literal["GroupBy"] = "GroupBy"
    MultipleAggregates: Literal["MultipleAggregates"] = "MultipleAggregates"
    MultipleOrderBy: Literal["MultipleOrderBy"] = "MultipleOrderBy"
    OffsetAndLimit: Literal["OffsetAndLimit"] = "OffsetAndLimit"
    OrderBy: Literal["OrderBy"] = "OrderBy"
    Top: Literal["Top"] = "Top"
    NonStreamingOrderBy: Literal["NonStreamingOrderBy"] = "NonStreamingOrderBy"


class _DistinctType:
    NoneType: Literal["None"] = "None"
    Ordered: Literal["Ordered"] = "Ordered"
    Unordered: Literal["Unordered"] = "Unordered"
