# Copyright (c) Microsoft Corporation.  All rights reserved.

"""HTTP Constants.
"""


class HttpMethods:
    """Constants of http methods.
    """
    Get = 'GET'
    Post = 'POST'
    Put = 'PUT'
    Delete = 'DELETE'
    Head = 'HEAD'
    Options = 'OPTIONS'


class HttpHeaders:
    """Constants of http headers.
    """
    Authorization = 'authorization'
    ETag = 'etag'
    MethodOverride = 'X-HTTP-Method'
    Slug = 'Slug'
    ContentType = 'Content-Type'
    LastModified = 'Last-Modified'
    ContentEncoding = 'Content-Encoding'
    CharacterSet = 'CharacterSet'
    UserAgent = 'User-Agent'
    IfModified_since = 'If-Modified-Since'
    IfMatch = 'If-Match'
    IfNoneMatch = 'If-None-Match'
    ContentLength = 'Content-Length'
    AcceptEncoding = 'Accept-Encoding'
    KeepAlive = 'Keep-Alive'
    CacheControl = 'Cache-Control'
    TransferEncoding = 'Transfer-Encoding'
    ContentLanguage = 'Content-Language'
    ContentLocation = 'Content-Location'
    ContentMd5 = 'Content-Md5'
    ContentRange = 'Content-Range'
    Accept = 'Accept'
    AcceptCharset = 'Accept-Charset'
    AcceptLanguage = 'Accept-Language'
    IfRange = 'If-Range'
    IfUnmodifiedSince = 'If-Unmodified-Since'
    MaxForwards = 'Max-Forwards'
    ProxyAuthorization = 'Proxy-Authorization'
    AcceptRanges = 'Accept-Ranges'
    ProxyAuthenticate = 'Proxy-Authenticate'
    RetryAfter = 'Retry-After'
    SetCookie = 'Set-Cookie'
    WwwAuthenticate = 'Www-Authenticate'
    Origin = 'Origin'
    Host = 'Host'
    AccessControlAllowOrigin = 'Access-Control-Allow-Origin'
    AccessControlAllowHeaders = 'Access-Control-Allow-Headers'
    KeyValueEncodingFormat = 'application/x-www-form-urlencoded'
    WrapAssertionFormat = 'wrap_assertion_format'
    WrapAssertion = 'wrap_assertion'
    WrapScope = 'wrap_scope'
    SimpleToken = 'SWT'
    HttpDate = 'date'
    Prefer = 'Prefer'
    Location = 'Location'
    Referer = 'referer'

    # Query
    Query = 'x-ms-documentdb-query'
    IsQuery = 'x-ms-documentdb-isquery'

    # Our custom DocDB headers
    Continuation = 'x-ms-continuation'
    PageSize = 'x-ms-max-item-count'

    # Request sender generated. Simply echoed by backend.
    ActivityId = 'x-ms-activity-id'
    PreTriggerInclude = 'x-ms-documentdb-pre-trigger-include'
    PreTriggerExclude = 'x-ms-documentdb-pre-trigger-exclude'
    PostTriggerInclude = 'x-ms-documentdb-post-trigger-include'
    PostTriggerExclude = 'x-ms-documentdb-post-trigger-exclude'
    IndexingDirective = 'x-ms-indexing-directive'
    SessionToken = 'x-ms-session-token'
    ConsistencyLevel = 'x-ms-consistency-level'
    XDate = 'x-ms-date'
    CollectionPartitionInfo = 'x-ms-collection-partition-info'
    CollectionServiceInfo = 'x-ms-collection-service-info'
    RetryAfterInMilliseconds = 'x-ms-retry-after-ms'
    IsFeedUnfiltered = 'x-ms-is-feed-unfiltered'
    ResourceTokenExpiry = 'x-ms-documentdb-expiry-seconds'
    EnableScanInQuery = 'x-ms-documentdb-query-enable-scan'
    EmitVerboseTracesInQuery = 'x-ms-documentdb-query-emit-traces'

    # Quota Info
    MaxEntityCount = 'x-ms-root-entity-max-count'
    CurrentEntityCount = 'x-ms-root-entity-current-count'
    CollectionQuotaInMb = 'x-ms-collection-quota-mb'
    CollectionCurrentUsageInMb = 'x-ms-collection-usage-mb'
    MaxMediaStorageUsageInMB = 'x-ms-max-media-storage-usage-mb'

    # Usage Info
    CurrentMediaStorageUsageInMB = 'x-ms-media-storage-usage-mb'
    RequestCharge = 'x-ms-request-charge'

    #Address related headers.
    ForceRefresh = 'x-ms-force-refresh'
    ItemCount = 'x-ms-item-count'
    NewResourceId = 'x-ms-new-resource-id'
    UseMasterCollectionResolver = 'x-ms-use-master-collection-resolver'

    # Admin Headers
    FullUpgrade = 'x-ms-force-full-upgrade'
    OnlyUpgradeSystemApplications = 'x-ms-only-upgrade-system-applications'
    OnlyUpgradeNonSystemApplications = 'x-ms-only-upgrade-non-system-applications'
    UpgradeFabricRingCodeAndConfig = 'x-ms-upgrade-fabric-code-config'
    IgnoreInProgressUpgrade = 'x-ms-ignore-inprogress-upgrade'
    UpgradeVerificationKind = 'x-ms-upgrade-verification-kind'
    IsCanary = 'x-ms-iscanary'

    # Version headers and values
    Version = 'x-ms-version'

    # RDFE Resource Provider headers
    OcpResourceProviderRegisteredUri = 'ocp-resourceprovider-registered-uri'

    # For Document service management operations only. This is in
    # essence a 'handle' to (long running) operations.
    RequestId = 'x-ms-request-id'

    # Object returning this determines what constitutes state and what
    # last state change means. For replica, it is the last role change.
    LastStateChangeUtc = 'x-ms-last-state-change-utc'

    # Offer type.
    OfferType = 'x-ms-offer-type'
    
    # Partitioned collection headers
    OfferThroughput = "x-ms-offer-throughput"
    PartitionKey = "x-ms-documentdb-partitionkey"
    EnableCrossPartitionQuery = "x-ms-documentdb-query-enablecrosspartition"

    # Upsert header
    IsUpsert = 'x-ms-documentdb-is-upsert'

    # Index progress headers.
    IndexTransformationProgress = 'x-ms-documentdb-collection-index-transformation-progress'
    LazyIndexingProgress = 'x-ms-documentdb-collection-lazy-indexing-progress'

class HttpHeaderPreferenceTokens:
    """Constants of http header preference tokens.
    """
    PreferUnfilteredQueryResponse = 'PreferUnfilteredQueryResponse'


class HttpStatusDescriptions:
    """Constants of http status descriptions.
    """
    Accepted = 'Accepted'
    Conflict = 'Conflict'
    OK = 'Ok'
    PreconditionFailed = 'Precondition Failed'
    NotModified = 'Not Modified'
    NotFound = 'Not Found'
    BadGateway = 'Bad Gateway'
    BadRequest = 'Bad Request'
    InternalServerError = 'Internal Server Error'
    MethodNotAllowed = 'MethodNotAllowed'
    NotAcceptable = 'Not Acceptable'
    NoContent = 'No Content'
    Created = 'Created'
    UnsupportedMediaType = 'Unsupported Media Type'
    LengthRequired = 'Length Required'
    ServiceUnavailable = 'Service Unavailable'
    RequestEntityTooLarge = 'Request Entity Too Large'
    Unauthorized = 'Unauthorized'
    Forbidden = 'Forbidden'
    Gone = 'Gone'
    RequestTimeout = 'Request timed out'
    GatewayTimeout = 'Gateway timed out'
    TooManyRequests = 'Too Many Requests'
    RetryWith = 'Retry the request'


class QueryStrings:
    """Constants of query strings.
    """
    Filter = '$filter';
    GenerateId = '$generateFor'
    GenerateIdBatchSize = '$batchSize'
    GetChildResourcePartitions = '$getChildResourcePartitions'
    Url = '$resolveFor'
    RootIndex = '$rootIndex'
    Query = 'query'
    SQLQueryType = 'sql'

    # RDFE Resource Provider query strings
    ContentView = 'contentview'
    Generic = 'generic'


class CookieHeaders:
    """Constants of cookie headers.
    """
    SessionToken = 'x-ms-session-token'


class Versions:
    """Constants of versions.
    """
    CurrentVersion = '2015-12-16'
    UserAgent = 'documentdb-python-sdk-1.6.0'


class Delimiters:
    """Constants of delimiters.
    """
    ClientContinuationDelimiter = '!!'
    ClientContinuationFormat = '{0}!!{1}'


class HttpListenerErrorCodes:
    """Constants of http listener error codes.
    """
    ERROR_OPERATION_ABORTED = 995
    ERROR_CONNECTION_INVALID = 1229


class HttpContextProperties:
    """Constants of http context properties.
    """
    SubscriptionId = 'SubscriptionId'