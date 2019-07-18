# Change Log azure-cosmos
## Version 4.0.0b1:

Version 4.0.0b1 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Cosmos. For more information about this, and preview releases of other Azure SDK libraries, please visit https://aka.ms/azure-sdk-preview1-python.

**Breaking changes: New API design**

- Operations are now scoped to a particular client:
    - `CosmosClient`: This client handles account-level operations. This includes managing service properties and listing the databases within an account.
    - `Database`: This client handles database-level operations. This includes creating and deleting containers, users and stored procedurs. It can be accessed from a `CosmosClient` instance by name.
    - `Container`: This client handles operations for a particular container. This includes querying and inserting items and managing properties.
    - `User`: This client handles operations for a particular user. This includes adding and deleting permissions and managing user properties.
    
    These clients can be accessed by navigating down the client hierarchy using the `get_<child>_client` method. For full details on the new API, please see the [reference documentation](http://azure.github.io/azure-sdk-for-python/ref/azure.cosmos.html).
- Clients are accessed by name rather than by Id. No need to concatenate strings to create links.
- No more need to import types and methods from individual modules. The public API surface area is available directly in the `azure.cosmos` package.
- Individual request properties can be provided as keyword arguments rather than constructing a separate `RequestOptions` instance.

## Changes in 3.0.2 : ##

- Added Support for MultiPolygon Datatype
- Bug Fix in Session Read Retry Policy
- Bug Fix for Incorrect padding issues while decoding base 64 strings

## Changes in 3.0.1 : ##

- Bug fix in LocationCache
- Bug fix endpoint retry logic
- Fixed documentation

## Changes in 3.0.0 : ##

- Multi-region write support added
- Naming changes
  - DocumentClient to CosmosClient
  - Collection to Container
  - Document to Item
  - Package name updated to "azure-cosmos"
  - Namespace updated to "azure.cosmos"

## Changes in 2.3.3 : ##

- Added support for proxy
- Added support for reading change feed
- Added support for collection quota headers
- Bugfix for large session tokens issue
- Bugfix for ReadMedia API
- Bugfix in partition key range cache

## Changes in 2.3.2 : ##

- Added support for default retries on connection issues.

## Changes in 2.3.1 : ##

- Updated documentation to reference Azure Cosmos DB instead of Azure DocumentDB.

## Changes in 2.3.0 : ##

- This SDK version requires the latest version of Azure Cosmos DB Emulator available for download from https://aka.ms/cosmosdb-emulator.

## Changes in 2.2.1 : ##

- bugfix for aggregate dict
- bugfix for trimming slashes in the resource link
- tests for unicode encoding

## Changes in 2.2.0 : ##

- Added support for Request Unit per Minute (RU/m) feature.
- Added support for a new consistency level called ConsistentPrefix.

## Changes in 2.1.0 : ##

- Added support for aggregation queries (COUNT, MIN, MAX, SUM, and AVG).
- Added an option for disabling SSL verification when running against DocumentDB Emulator.
- Removed the restriction of dependent requests module to be exactly 2.10.0.
- Lowered minimum throughput on partitioned collections from 10,100 RU/s to 2500 RU/s.
- Added support for enabling script logging during stored procedure execution.
- REST API version bumped to '2017-01-19' with this release.

## Changes in 2.0.1 : ##

- Made editorial changes to documentation comments.

## Changes in 2.0.0 : ##

- Added support for Python 3.5.
- Added support for connection pooling using the requests module.
- Added support for session consistency.
- Added support for TOP/ORDERBY queries for partitioned collections.

## Changes in 1.9.0 : ##

- Added retry policy support for throttled requests. (Throttled requests receive a request rate too large exception, error code 429.)
  By default, DocumentDB retries nine times for each request when error code 429 is encountered, honoring the retryAfter time in the response header.
  A fixed retry interval time can now be set as part of the RetryOptions property on the ConnectionPolicy object if you want to ignore the retryAfter time returned by server between the retries.
  DocumentDB now waits for a maximum of 30 seconds for each request that is being throttled (irrespective of retry count) and returns the response with error code 429.
  This time can also be overriden in the RetryOptions property on ConnectionPolicy object.

- DocumentDB now returns x-ms-throttle-retry-count and x-ms-throttle-retry-wait-time-ms as the response headers in every request to denote the throttle retry count
  and the cummulative time the request waited between the retries.

- Removed the RetryPolicy class and the corresponding property (retry_policy) exposed on the document_client class and instead introduced a RetryOptions class
  exposing the RetryOptions property on ConnectionPolicy class that can be used to override some of the default retry options.

## Changes in 1.8.0 : ##

- Added the support for geo-replicated database accounts.
- Test fixes to move the global host and masterKey into the individual test classes.

## Changes in 1.7.0 : ##

- Added the support for Time To Live(TTL) feature for documents.

## Changes in 1.6.1 : ##

- Bug fixes related to server side partitioning to allow special characters in partitionkey path.

## Changes in 1.6.0 : ##

- Added the support for server side partitioned collections feature.

## Changes in 1.5.0 : ##

- Added Client-side sharding framework to the SDK. Implemented HashPartionResolver and RangePartitionResolver classes.

## Changes in 1.4.2 : ##

- Implement Upsert. New UpsertXXX methods added to support Upsert feature.
- Implement ID Based Routing. No public API changes, all changes internal.

## Changes in 1.3.0 : ##

- Release skipped to bring version number in alignment with other SDKs

## Changes in 1.2.0 : ##

- Supports GeoSpatial index.
- Validates id property for all resources. Ids for resources cannot contain ?, /, #, \\, characters or end with a space.
- Adds new header "index transformation progress" to ResourceResponse.

## Changes in 1.1.0 : ##

- Implements V2 indexing policy

## Changes in 1.0.1 : ##

- Supports proxy connection


