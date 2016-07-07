## Changes in 1.9.0 : ##

- Added the retry policy support for throttle requests(Request Rate too large - Error code 429). By default, we now retry 9 times for each request when we get a 429, honoring the retryAfter time in the response header.
  We also allow setting a fixed retry interval time as part of the RetryOptions property on the ConnectionPolicy object if you want to ignore the retryAfter time returned by server between the retries. We will also 
  now wait for max 30 sec for each request that is being throttled(irrespective of retry count) and will return the request with a 429. This time can also be overriden in the RetryOptions property on ConnectionPolicy object.

- We also return x-ms-throttle-retry-count and x-ms-throttle-retry-wait-time-ms as the response headers in every request to denote the throttle retry count and the cummulative time the request waited between the retries.

- Removing the RetryPolicy class and the corresponding property(retry_policy) exposed on document_client class and instead introducing a RetryOptions class and exposing the RetryOptions property on ConnectionPolicy class 
  that can be used to override some of the default retry options we set.

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
