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

"""HTTP Constants in the Azure Cosmos database service.
"""


class HttpMethods:
    """Constants of http methods.
    """

    Get = "GET"
    Post = "POST"
    Put = "PUT"
    Delete = "DELETE"
    Head = "HEAD"
    Options = "OPTIONS"

class HttpHeaders:
    """Constants of http headers.
    """

    Authorization = "authorization"
    ETag = "etag"
    MethodOverride = "X-HTTP-Method"
    Slug = "Slug"
    ContentType = "Content-Type"
    LastModified = "Last-Modified"
    ContentEncoding = "Content-Encoding"
    CharacterSet = "CharacterSet"
    UserAgent = "User-Agent"
    IfModified_since = "If-Modified-Since"
    IfMatch = "If-Match"
    IfNoneMatch = "If-None-Match"
    ContentLength = "Content-Length"
    AcceptEncoding = "Accept-Encoding"
    KeepAlive = "Keep-Alive"
    CacheControl = "Cache-Control"
    TransferEncoding = "Transfer-Encoding"
    ContentLanguage = "Content-Language"
    ContentLocation = "Content-Location"
    ContentMd5 = "Content-Md5"
    ContentRange = "Content-Range"
    Accept = "Accept"
    AcceptCharset = "Accept-Charset"
    AcceptLanguage = "Accept-Language"
    IfRange = "If-Range"
    IfUnmodifiedSince = "If-Unmodified-Since"
    MaxForwards = "Max-Forwards"
    ProxyAuthorization = "Proxy-Authorization"
    AcceptRanges = "Accept-Ranges"
    ProxyAuthenticate = "Proxy-Authenticate"
    RetryAfter = "Retry-After"
    SetCookie = "Set-Cookie"
    WwwAuthenticate = "Www-Authenticate"
    Origin = "Origin"
    Host = "Host"
    AccessControlAllowOrigin = "Access-Control-Allow-Origin"
    AccessControlAllowHeaders = "Access-Control-Allow-Headers"
    KeyValueEncodingFormat = "application/x-www-form-urlencoded"
    WrapAssertionFormat = "wrap_assertion_format"
    WrapAssertion = "wrap_assertion"
    WrapScope = "wrap_scope"
    SimpleToken = "SWT"
    HttpDate = "date"
    Prefer = "Prefer"
    Location = "Location"
    Referer = "referer"
    Pragma = "Pragma"

    # Bulk/Batch
    IsBatchRequest = "x-ms-cosmos-is-batch-request"
    IsBatchAtomic = "x-ms-cosmos-batch-atomic"
    ShouldBatchContinueOnError = "x-ms-cosmos-batch-continue-on-error"

    # Query
    Query = "x-ms-documentdb-query"
    IsQuery = "x-ms-documentdb-isquery"
    IsQueryPlanRequest = "x-ms-cosmos-is-query-plan-request"
    SupportedQueryFeatures = "x-ms-cosmos-supported-query-features"
    QueryVersion = "x-ms-cosmos-query-version"
    QueryMetrics = "x-ms-documentdb-query-metrics"
    QueryExecutionInfo = "x-ms-cosmos-query-execution-info"
    IndexUtilization = "x-ms-cosmos-index-utilization"

    # Our custom DocDB headers
    Continuation = "x-ms-continuation"
    PageSize = "x-ms-max-item-count"
    ResponseContinuationTokenLimitInKb = "x-ms-documentdb-responsecontinuationtokenlimitinkb"  # cspell:disable-line
    PriorityLevel = "x-ms-cosmos-priority-level"

    # Request sender generated. Simply echoed by backend.
    ActivityId = "x-ms-activity-id"
    CorrelatedActivityId = "x-ms-cosmos-correlated-activityid"  # cspell:disable-line
    PreTriggerInclude = "x-ms-documentdb-pre-trigger-include"
    PreTriggerExclude = "x-ms-documentdb-pre-trigger-exclude"
    PostTriggerInclude = "x-ms-documentdb-post-trigger-include"
    PostTriggerExclude = "x-ms-documentdb-post-trigger-exclude"
    IndexingDirective = "x-ms-indexing-directive"
    SessionToken = "x-ms-session-token"
    ConsistencyLevel = "x-ms-consistency-level"
    XDate = "x-ms-date"
    CollectionPartitionInfo = "x-ms-collection-partition-info"
    CollectionServiceInfo = "x-ms-collection-service-info"
    RetryAfterInMilliseconds = "x-ms-retry-after-ms"
    IsFeedUnfiltered = "x-ms-is-feed-unfiltered"
    ResourceTokenExpiry = "x-ms-documentdb-expiry-seconds"
    EnableScanInQuery = "x-ms-documentdb-query-enable-scan"
    EmitVerboseTracesInQuery = "x-ms-documentdb-query-emit-traces"
    SubStatus = "x-ms-substatus"
    AlternateContentPath = "x-ms-alt-content-path"
    ContentPath = "x-ms-content-path"
    IsContinuationExpected = "x-ms-documentdb-query-iscontinuationexpected"
    PopulateQueryMetrics = "x-ms-documentdb-populatequerymetrics"
    PopulateIndexMetrics = "x-ms-cosmos-populateindexmetrics"
    ResourceQuota = "x-ms-resource-quota"
    ResourceUsage = "x-ms-resource-usage"
    IntendedCollectionRID = "x-ms-cosmos-intended-collection-rid"
    Prefer = "Prefer"

    # Quota Info
    MaxEntityCount = "x-ms-root-entity-max-count"
    CurrentEntityCount = "x-ms-root-entity-current-count"
    CollectionQuotaInMb = "x-ms-collection-quota-mb"
    CollectionCurrentUsageInMb = "x-ms-collection-usage-mb"
    MaxMediaStorageUsageInMB = "x-ms-max-media-storage-usage-mb"

    # Collection quota
    PopulateQuotaInfo = "x-ms-documentdb-populatequotainfo"
    PopulatePartitionKeyRangeStatistics = "x-ms-documentdb-populatepartitionstatistics"

    # Usage Info
    CurrentMediaStorageUsageInMB = "x-ms-media-storage-usage-mb"
    RequestCharge = "x-ms-request-charge"

    # Address related headers.
    ForceRefresh = "x-ms-force-refresh"
    ItemCount = "x-ms-item-count"
    NewResourceId = "x-ms-new-resource-id"
    UseMasterCollectionResolver = "x-ms-use-master-collection-resolver"

    # Admin Headers
    FullUpgrade = "x-ms-force-full-upgrade"
    OnlyUpgradeSystemApplications = "x-ms-only-upgrade-system-applications"
    OnlyUpgradeNonSystemApplications = "x-ms-only-upgrade-non-system-applications"
    UpgradeFabricRingCodeAndConfig = "x-ms-upgrade-fabric-code-config"
    IgnoreInProgressUpgrade = "x-ms-ignore-inprogress-upgrade"
    UpgradeVerificationKind = "x-ms-upgrade-verification-kind"
    IsCanary = "x-ms-iscanary"

    # Version headers and values
    Version = "x-ms-version"

    # RDFE Resource Provider headers
    OcpResourceProviderRegisteredUri = "ocp-resourceprovider-registered-uri"

    # For Document service management operations only. This is in
    # essence a 'handle' to (long-running) operations.
    RequestId = "x-ms-request-id"

    # Object returning this determines what constitutes state and what
    # last state change means. For replica, it is the last role change.
    LastStateChangeUtc = "x-ms-last-state-change-utc"

    # Offer type.
    OfferType = "x-ms-offer-type"
    OfferThroughput = "x-ms-offer-throughput"
    AutoscaleSettings = "x-ms-cosmos-offer-autopilot-settings"

    # Custom RUs/minute headers
    DisableRUPerMinuteUsage = "x-ms-documentdb-disable-ru-per-minute-usage"
    IsRUPerMinuteUsed = "x-ms-documentdb-is-ru-per-minute-used"
    OfferIsRUPerMinuteThroughputEnabled = "x-ms-offer-is-ru-per-minute-throughput-enabled"

    # Partitioned collection headers
    PartitionKey = "x-ms-documentdb-partitionkey"
    EnableCrossPartitionQuery = "x-ms-documentdb-query-enablecrosspartition"
    PartitionKeyRangeID = "x-ms-documentdb-partitionkeyrangeid"
    PhysicalPartitionId = "x-ms-cosmos-physical-partition-id"
    PartitionKeyDeletePending = "x-ms-cosmos-is-partition-key-delete-pending"
    StartEpkString = "x-ms-start-epk"
    EndEpkString = "x-ms-end-epk"
    ReadFeedKeyType = "x-ms-read-key-type"
    SDKSupportedCapabilities = "x-ms-cosmos-sdk-supportedcapabilities"

    # Upsert header
    IsUpsert = "x-ms-documentdb-is-upsert"

    # Index progress headers.
    IndexTransformationProgress = "x-ms-documentdb-collection-index-transformation-progress"
    LazyIndexingProgress = "x-ms-documentdb-collection-lazy-indexing-progress"

    # Client generated retry count response header
    ThrottleRetryCount = "x-ms-throttle-retry-count"
    ThrottleRetryWaitTimeInMs = "x-ms-throttle-retry-wait-time-ms"

    # StoredProcedure related headers
    EnableScriptLogging = "x-ms-documentdb-script-enable-logging"
    ScriptLogResults = "x-ms-documentdb-script-log-results"

    # Change feed
    AIM = "A-IM"
    IncrementalFeedHeaderValue = "Incremental feed"

    # For Using Multiple Write Locations
    AllowTentativeWrites = "x-ms-cosmos-allow-tentative-writes"

    # Dedicated Gateway headers
    DedicatedGatewayCacheStaleness = "x-ms-dedicatedgateway-max-age"
    IntegratedCacheHit = "x-ms-cosmos-cachehit"

    # Backend headers
    Server = "Server"
    StrictTransportSecurity = "Strict-Transport-Security"
    LSN = "lsn"
    GatewayVersion = "x-ms-gatewayversion"
    ServiceVersion = "x-ms-serviceversion"
    SchemaVersion = "x-ms-schemaversion"
    QuorumAckedLsn = "x-ms-quorum-acked-lsn"  # cspell:disable-line
    CurrentWriteQuorum = "x-ms-current-write-quorum"
    CurrentReplicaSetSize = "x-ms-current-replica-set-size"
    XpRole = "x-ms-xp-role"
    GlobalCommittedLsn = "x-ms-global-committed-lsn"
    NumberOfReadRegions = "x-ms-number-of-read-regions"
    TransportRequestId = "x-ms-transport-request-id"
    ItemLsn = "x-ms-item-lsn"
    CosmosItemLsn = "x-ms-cosmos-item-llsn"  # cspell:disable-line
    CosmosLsn = "x-ms-cosmos-llsn"  # cspell:disable-line
    CosmosQuorumAckedLsn = "x-ms-cosmos-quorum-acked-llsn"  # cspell:disable-line
    RequestDurationMs = "x-ms-request-duration-ms"

class HttpHeaderPreferenceTokens:
    """Constants of http header preference tokens.
    """
    PreferUnfilteredQueryResponse = "PreferUnfilteredQueryResponse"


class HttpStatusDescriptions:
    """Constants of http status descriptions.
    """
    Accepted = "Accepted"
    Conflict = "Conflict"
    OK = "Ok"
    PreconditionFailed = "Precondition Failed"
    NotModified = "Not Modified"
    NotFound = "Not Found"
    BadGateway = "Bad Gateway"
    BadRequest = "Bad Request"
    InternalServerError = "Internal Server Error"
    MethodNotAllowed = "MethodNotAllowed"
    NotAcceptable = "Not Acceptable"
    NoContent = "No Content"
    Created = "Created"
    UnsupportedMediaType = "Unsupported Media Type"
    LengthRequired = "Length Required"
    ServiceUnavailable = "Service Unavailable"
    RequestEntityTooLarge = "Request Entity Too Large"
    Unauthorized = "Unauthorized"
    Forbidden = "Forbidden"
    Gone = "Gone"
    RequestTimeout = "Request timed out"
    GatewayTimeout = "Gateway timed out"
    TooManyRequests = "Too Many Requests"
    RetryWith = "Retry the request"


class QueryStrings:
    """Constants of query strings.
    """
    Filter = "$filter"
    GenerateId = "$generateFor"
    GenerateIdBatchSize = "$batchSize"
    GetChildResourcePartitions = "$getChildResourcePartitions"
    Url = "$resolveFor"
    RootIndex = "$rootIndex"
    Query = "query"
    SQLQueryType = "sql"

    # RDFE Resource Provider query strings
    ContentView = "contentview"
    Generic = "generic"


class CookieHeaders:
    """Constants of cookie headers.
    """
    SessionToken = "x-ms-session-token"


class Versions:
    """Constants of versions.
    """
    CurrentVersion = "2020-07-15"
    SDKName = "azure-cosmos"
    QueryVersion = "1.0"


class Delimiters:
    """Constants of delimiters.
    """

    ClientContinuationDelimiter = "!!"
    ClientContinuationFormat = "{0}!!{1}"


class HttpListenerErrorCodes:
    """Constants of http listener error codes.
    """

    ERROR_OPERATION_ABORTED = 995
    ERROR_CONNECTION_INVALID = 1229


class HttpContextProperties:
    """Constants of http context properties.
    """

    SubscriptionId = "SubscriptionId"


class _ErrorCodes:
    """Constants of error codes.
    """

    # Windows Socket Error Codes
    WindowsInterruptedFunctionCall = 10004
    WindowsFileHandleNotValid = 10009
    WindowsPermissionDenied = 10013
    WindowsBadAddress = 10014
    WindowsInvalidArgumnet = 10022
    WindowsResourceTemporarilyUnavailable = 10035
    WindowsOperationNowInProgress = 10036
    WindowsAddressAlreadyInUse = 10048
    WindowsConnectionResetByPeer = 10054
    WindowsCannotSendAfterSocketShutdown = 10058
    WindowsConnectionTimedOut = 10060
    WindowsConnectionRefused = 10061
    WindowsNameTooLong = 10063
    WindowsHostIsDown = 10064
    WindowsNoRouteTohost = 10065

    # Linux Error Codes
    LinuxConnectionReset = 131


class StatusCodes:
    """HTTP status codes returned by the REST operations
    """
    # Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    NOT_MODIFIED = 304

    # Client Error
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    PRECONDITION_FAILED = 412
    REQUEST_ENTITY_TOO_LARGE = 413
    FAILED_DEPENDENCY = 424
    TOO_MANY_REQUESTS = 429
    RETRY_WITH = 449

    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

    # Operation pause and cancel. These are FAKE status codes for QOS logging purpose only.
    OPERATION_PAUSED = 1200
    OPERATION_CANCELLED = 1201


class SubStatusCodes:
    """Sub status codes returned by the REST operations specifying the details of the operation
    """
    UNKNOWN = 0

    # 400: Bad Request Substatus
    PARTITION_KEY_MISMATCH = 1001
    CROSS_PARTITION_QUERY_NOT_SERVABLE = 1004
    COLLECTION_RID_MISMATCH = 1024

    # 410: StatusCodeType_Gone: substatus
    NAME_CACHE_IS_STALE = 1000
    PARTITION_KEY_RANGE_GONE = 1002
    COMPLETING_SPLIT = 1007
    COMPLETING_PARTITION_MIGRATION = 1008

    # 403: Forbidden Substatus.
    WRITE_FORBIDDEN = 3
    PROVISION_LIMIT_REACHED = 1005
    DATABASE_ACCOUNT_NOT_FOUND = 1008
    REDUNDANT_COLLECTION_PUT = 1009
    SHARED_THROUGHPUT_DATABASE_QUOTA_EXCEEDED = 1010
    SHARED_THROUGHPUT_OFFER_GROW_NOT_NEEDED = 1011
    AAD_REQUEST_NOT_AUTHORIZED = 5300

    # 404: LSN in session token is higher
    READ_SESSION_NOTAVAILABLE = 1002
    OWNER_RESOURCE_NOT_FOUND = 1003

    # 409: Conflict exception
    CONFLICT_WITH_CONTROL_PLANE = 1006

    # 503: Service Unavailable due to region being out of capacity for bindable partitions
    INSUFFICIENT_BINDABLE_PARTITIONS = 1007

    # Client Side substatus codes
    THROUGHPUT_OFFER_NOT_FOUND = 10004


class ResourceType:
    """Types of resources in Azure Cosmos
    """

    Database = "dbs"
    Collection = "colls"
    User = "users"
    Document = "docs"
    Permission = "permissions"
    StoredProcedure = "sprocs"
    Trigger = "triggers"
    UserDefinedFunction = "udfs"
    Conflict = "conflicts"
    Attachment = "attachments"
    PartitionKeyRange = "pkranges"
    Schema = "schemas"
    Offer = "offers"
    Topology = "topology"
    DatabaseAccount = "databaseaccount"
    PartitionKey = "partitionkey"

    @staticmethod
    def IsCollectionChild(resourceType: str) -> bool:
        return resourceType in (
            ResourceType.Document,
            ResourceType.Attachment,
            ResourceType.Conflict,
            ResourceType.Schema,
            ResourceType.UserDefinedFunction,
            ResourceType.Trigger,
            ResourceType.StoredProcedure,
            ResourceType.PartitionKey,
        )
