# Copyright (c) Microsoft Corporation.  All rights reserved.

"""AzureDocument classes and enums.
"""


class DatabaseAccount(object):
    """Database account. A DatabaseAccount is the container for databases.

    :Attributes:
        - `DatabaseLink`: str, the self-link for Databases in the
          databaseAccount.
        - `MediaLink`: str, the self-link for Media in the databaseAccount.
        - `MaxMediaStorageUsageInMB`: int, attachment content (media) storage
          quota in MBs ( Retrieved from gateway ).
        - `CurrentMediaStorageUsageInMB`: int, current attachment content
          (media) usage in MBs (Retrieved from gateway ).

          Value is returned from cached information updated periodically and
          is not guaranteed to be real time.
        - `CapacityUnitsConsumed`: int, the number is capacity units database
          account is currently consuming.

          Value is returned from cached information updated periodically and is
          not guaranteed to be real time.
        - `CapacityUnitsProvisioned`: int, the number of provisioned capacity
          units for the database account.

          Value is returned from cached information updated periodically and
          is not guaranteed to be real time.
        - `ConsumedDocumentStorageInMB`: int, the cumulative sum of current
          sizes of created collection in MB.

          Value is returned from cached information updated periodically and
          is not guaranteed to be real time.
        - `ReservedDocumentStorageInMB`: int, the cumulative sum of maximum
          sizes of created collection in MB.

          Value is returned from cached information updated periodically and
          is not guaranteed to be real time.
        - `ProvisionedDocumentStorageInMB`: int, the provisioned documented
          storage capacity for the database account.

          Value is returned from cached information updated periodically and
          is not guaranteed to be real time.
        - `ConsistencyPolicy`: dict, UserConsistencyPolicy settings.
        - `ConsistencyPolicy['defaultConsistencyLevel']`: dict, the default
          consistency level.
        - `ConsistencyPolicy['maxStalenessPrefix']`: int, in bounded staleness
          consistency, the maximum allowed staleness in terms difference in
          sequence numbers (aka version).
        - `ConsistencyPolicy['maxStalenessIntervalInSeconds']`: int, In bounded
          staleness consistency, the maximum allowed staleness in terms time
          interval.
    """

    def __init__(self):
        self.DatabasesLink = ''
        self.MediaLink = ''
        self.MaxMediaStorageUsageInMB = 0
        self.CurrentMediaStorageUsageInMB = 0
        self.CapacityUnitsConsumed = 0
        self.CapacityUnitsProvisioned = 0
        self.ConsumedDocumentStorageInMB = 0
        self.ReservedDocumentStorageInMB = 0
        self.ProvisionedDocumentStorageInMB = 0
        self.ConsistencyPolicy = None


class ConsistencyLevel(object):
    """Represents the consistency levels supported for DocumentDB client
    operations.

    The requested ConsistencyLevel must match or be weaker than that provisioned
    for the database account. Consistency levels.

    Consistency levels by order of strength are Strong, BoundedStaleness,
    Session and Eventual.

    :Attributes:
        - `Strong`: Strong Consistency guarantees that read operations always
          return the value that was last written.
        - `BoundedStaleness` Bounded Staleness guarantees that reads are not
          too out-of-date. This can be configured based on number of operations
          (MaxStalenessPrefix) or time (MaxStalenessIntervalInSeconds).
        - `Session`: Session Consistency guarantees monotonic reads (you never
          read old data, then new, then old again), monotonic writes (writes
          are ordered) and read your writes (your writes are immediately
          visible to your reads) within any single session.
        - `Eventual`: Eventual Consistency guarantees that reads will return
          a subset of writes. All writes will be eventually be available for
          reads.
    """
    Strong = 'Strong'
    BoundedStaleness = 'BoundedStaleness'
    Session = 'Session'
    Eventual = 'Eventual'


class IndexingMode(object):
    """Specifies the supported indexing modes.

    :Attributes:
        - `Consistent`: Index is updated synchronously with a create or
          update operation. With consistent indexing, query behavior is the
          same as the default consistency level for the collection.
         
          The index is
          always kept up to date with the data.
        - `Lazy`: Index is updated asynchronously with respect to a create
          or update operation.

          With lazy indexing, queries are eventually consistent. The index is
          updated when the collection is idle.
    """
    Consistent = 'consistent'
    Lazy = 'lazy'


class IndexingDirective(object):
    """Specifies whether or not the resource is to be indexed.

    :Attributes:
        - `Default`: Use any pre-defined/pre-configured defaults.
        - `Include`: Index the resource.
        - `Exclude`: Do not index the resource.
    """
    Default = 0
    Exclude = 1
    Include = 2


class Protocol(object):
    """Protocol to be used by DocumentClient for communicating to the DocumentDB
    service.
    
    :Attributes:
        - `Tcp`: A custom binary protocol on TCP.
        - `Https`: HTTPS.
    """
    Tcp = 1
    Https = 2


class ConnectionMode(object):
    """Represents the connection mode to be used by the client.

    :Attributes:
        - `Direct`: Use direct connectivity to the data nodes. Use gateway only
          to initialize and cache logical addresses and refresh on updates.
        - `Gateway`: Use the DocumentDB gateway to route all requests. The
          gateway proxies requests to the right data partition.
    """
    Direct = 0
    Gateway = 1


class MediaReadMode(object):
    """Represents the mode for use with downloading attachment content
    (aka media).

    :Attributes:
        - `Buffered`: Content is buffered at the client and not directly
          streamed from the content store.

          Use Buffered to reduce the time taken to read and write media files.
        - `Streamed`: Content is directly streamed from the content store
          without any buffering at the client.

          Use Streamed to reduce the client memory overhead of reading and
          writing media files.
    """
    Buffered = 'Buffered'
    Streamed = 'Streamed'


class PermissionMode(object):
    """Enumeration specifying applicability of permission.

    :Attributes:
        - `NoneMode`: None.
        - `Read`: Permission applicable for read operations only.
        - `All`: Permission applicable for all operations.
    """
    NoneMode = 'none'  # None is python's key word.
    Read = 'read'
    All = 'all'


class TriggerType(object):
    """Specifies the type of the trigger.

    :Attributes:
        - `Pre`: Trigger should be executed before the associated operation(s).
        - `Post`: Trigger should be executed after the associated operation(s).
    """
    Pre = 'pre'
    Post = 'post'


class TriggerOperation(object):
    """Specifies the operations on which a trigger should be executed.
   
    :Attributes:
        - `All`: All operations.
        - `Create`: Create operations only.
        - `Update`: Update operations only.
        - `Delete`: Delete operations only.
        - `Replace`: Replace operations only.
    """
    All = 'all'
    Create = 'create'
    Update = 'update'
    Delete = 'delete'
    Replace = 'replace'


class ConnectionPolicy(object):
    """Represents the Connection policy assocated with a DocumentClient.

    :Attributes:
        - `MaxConnections`: int, gets or sets the maximum number of simultaneous
          network connections with a specific data partition.

          Currently used only for Protocol.Tcp.
        - `RequestTimeout`: int, gets or sets the request timeout (time to wait
          for response from network peer)
        - `MediaRequestTimeout`: int, gets or sets Time to wait for response
          from network peer for attachment content (aka media) operations.
        - `ConnectionMode`: int (documents.ConnectionMode), gets or sets the
          connection mode used the client Gateway or Direct.
        - `ConnectionProtocol`: int (documents.Protocol), gets or sets the
          connection protocol.

          This setting is not used for Gateway as Gateway
          only supports HTTPS.
        - `MaxCallsPerConnections`: int, gets or sets the number of maximum
          simultaneous calls permitted on a single data connection.

          Currently
          used only for Protocol.Tcp.
        - `MaxConcurrentFanoutRequests`: int, gets or sets the maximum number
          of concurrent fanout requests.
        - `MediaReadMode`: str (MediaReadMode.Buffered), gets or sets the
          attachment content (aka media) download mode.
    """

    __defaultMaxConnections = 20
    __defaultMaxConcurrentCallsPerConnection = 50
    __defaultRequestTimeout = 10000  # milliseconds
    # defaultMediaRequestTimeout is based upon the blob client timeout and the
    # retry policy.
    __defaultMediaRequestTimeout = 300000  # milliseconds
    __defaultMaxConcurrentFanoutRequests = 32

    def __init__(self):
        self.MaxConnections = self.__defaultMaxConnections
        self.RequestTimeout = self.__defaultRequestTimeout
        self.MediaRequestTimeout = self.__defaultMediaRequestTimeout
        self.ConnectionMode = ConnectionMode.Direct
        self.ConnectionProtocol = Protocol.Https
        self.MaxCallsPerConnections = (
            self.__defaultMaxConcurrentCallsPerConnection)
        self.MaxConcurrentFanoutRequests = (
            self.__defaultMaxConcurrentFanoutRequests)
        self.MediaReadMode = MediaReadMode.Buffered