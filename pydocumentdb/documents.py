#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""AzureDocument classes and enums for the Azure DocumentDB database service.
"""

import pydocumentdb.retry_options as retry_options

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
        self._WritableLocations = []
        self._ReadableLocations = []

    @property
    def WritableLocations(self):
        """Gets the list of writable locations for a geo-replicated database account.
        """
        return self._WritableLocations

    @property
    def ReadableLocations(self):
        """Gets the list of readable locations for a geo-replicated database account.
        """
        return self._ReadableLocations

class ConsistencyLevel(object):
    """Represents the consistency levels supported for DocumentDB client
    operations.

    The requested ConsistencyLevel must match or be weaker than that provisioned
    for the database account. Consistency levels.

    Consistency levels by order of strength are Strong, BoundedStaleness,
    Session, ConsistentPrefix and Eventual.

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
        - `ConsistentPrefix`: ConsistentPrefix Consistency guarantees that
          reads will return some prefix of all writes with no gaps. All writes
          will be eventually be available for reads.
    """
    Strong = 'Strong'
    BoundedStaleness = 'BoundedStaleness'
    Session = 'Session'
    Eventual = 'Eventual'
    ConsistentPrefix = 'ConsistentPrefix'


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
        - `NoIndex`: No index is provided.

          Setting IndexingMode to "None" drops the index. Use this if you don't
          want to maintain the index for a document collection, to save the
          storage cost or improve the write throughput. Your queries will
          degenerate to scans of the entire collection.
    """
    Consistent = 'consistent'
    Lazy = 'lazy'
    NoIndex = 'none'


class IndexKind(object):
    """Specifies the index kind of index specs.

    :Attributes:
        - `Hash`: The index entries are hashed to serve point look up queries.
          Can be used to serve queries like: SELECT * FROM docs d WHERE d.prop = 5

        - `Range`: The index entries are ordered. Range indexes are optimized for
          inequality predicate queries with efficient range scans.
          Can be used to serve queries like: SELECT * FROM docs d WHERE d.prop > 5
    """
    Hash = 'Hash'
    Range = 'Range'

class PartitionKind(object):
    """Specifies the kind of partitioning to be applied.

    :Attributes:
        - `Hash`: The partition key definition path is hashed.
    """
    Hash = 'Hash'

class DataType(object):
    """Specifies the data type of index specs.

    :Attributes:
        - `Number`: Represents a numeric data type
        - `String`: Represents a string data type.
        - `Point`: Represents a point data type
        - `LineString`: Represents a line string data type
        - `Polygon`: Represents a polygon data type
    """
    Number = 'Number'
    String = 'String'
    Point = 'Point'
    LineString = 'LineString'
    Polygon = 'Polygon'


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

    Please refer to http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification for more detail.

    :Attributes:
        - `SSLKeyFile`: str, the path of the key file for ssl connection.
        - `SSLCertFile`: str, the path of the cert file for ssl connection.
        - `SSLCaCerts`: str, the path of the CA_BUNDLE file with certificates of trusted CAs.
    """
    def __init__(self):
        self.SSLKeyFile = None
        self.SSLCertFile = None
        self.SSLCaCerts = None


class ProxyConfiguration(object):
    """Configurations for proxy.

    :Attributes:
        - `Host`: str, the host address of the proxy.
        - `Port`: int, the port number of the proxy.
    """
    def __init__(self):
        self.Host = None
        self.Port = None


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
        - `ProxyConfiguration`: documents.ProxyConfiguration, gets or sets the proxy configuration.
        - `EnableEndpointDiscovery`: boolean, gets or sets endpoint discovery flag for geo-replicated database accounts.
           When EnableEndpointDiscovery is true, the client will automatically discover the
           current write and read locations and direct the requests to the correct location
           taking into consideration of the user's preference(if provided) as PreferredLocations.
        - `PreferredLocations`: list, gets or sets the preferred locations for geo-replicated database accounts.
           When EnableEndpointDiscovery is true and PreferredLocations is non-empty,
           the client will use this list to evaluate the final location, taking into consideration
           the order specified in PreferredLocations list. The locations in this list are specified as the names of
           the azure documentdb locations like, 'West US', 'East US', 'Central India' and so on.
        - `RetryOptions`: RetryOptions, gets or sets the retry options to be applied to all requests when retrying.
        - `DisableSSLVerification` : boolean, flag to disable SSL verification for the requests. SSL verification is enabled by default. 
           Don't set this when targeting production endpoints.
           This is intended to be used only when targeting emulator endpoint to avoid failing your requests with SSL related error.
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
        self.ProxyConfiguration = None
        self.EnableEndpointDiscovery = True
        self.PreferredLocations = []
        self.RetryOptions = retry_options.RetryOptions()
        self.DisableSSLVerification = False;

class Undefined(object):
    """Represents undefined value for partitionKey when it's mising.
    """
