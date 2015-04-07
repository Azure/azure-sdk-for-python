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


class ConnectionMode(object):
    """Represents the connection mode to be used by the client.

    :Attributes:
        - `Gateway`: Use the DocumentDB gateway to route all requests. The
          gateway proxies requests to the right data partition.
    """
    Gateway = 0


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


class SSLConfiguration(object):
    """Configurations for SSL connections.

    Please refer to https://docs.python.org/2/library/ssl.html#socket-creation for more detail.

    :Attributes:
        - `SSLKeyFile`: str, the path of the key file for ssl connection.
        - `SSLCertFile`: str, the path of the cert file for ssl connection.
        - `SSLCaCerts`: str, the path of the ca_certs file for ssl connection.
    """
    def __init__(self):
        self.SSLKeyFile = None
        self.SSLCertFile = None
        self.SSLCaCerts = None


class ConnectionPolicy(object):
    """Represents the Connection policy assocated with a DocumentClient.

    :Attributes:
        - `RequestTimeout`: int, gets or sets the request timeout (time to wait
          for response from network peer)
        - `MediaRequestTimeout`: int, gets or sets Time to wait for response
          from network peer for attachment content (aka media) operations.
        - `ConnectionMode`: int (documents.ConnectionMode), gets or sets the
          connection mode used in the client. Currently only Gateway is supported.
        - `MediaReadMode`: str (MediaReadMode.Buffered), gets or sets the
          attachment content (aka media) download mode.
        - `SSLConfiguration`: documents.SSLConfiguration, gets or sets the SSL configuration.
    """

    __defaultRequestTimeout = 60000  # milliseconds
    # defaultMediaRequestTimeout is based upon the blob client timeout and the
    # retry policy.
    __defaultMediaRequestTimeout = 300000  # milliseconds

    def __init__(self):
        self.RequestTimeout = self.__defaultRequestTimeout
        self.MediaRequestTimeout = self.__defaultMediaRequestTimeout
        self.ConnectionMode = ConnectionMode.Gateway
        self.MediaReadMode = MediaReadMode.Buffered
        self.SSLConfiguration = None


class RetryPolicy(object):
    """The retry policy.

    :Attributes:
        - `MaxRetryAttemptsOnRequest`: int, the max retry attempts on request.
        - `MaxRetryAttemptsOnQuery`: int, the max retry attempts on query.
    """
    def __init__(self):
        self.MaxRetryAttemptsOnRequest = 0
        self.MaxRetryAttemptsOnQuery = 3