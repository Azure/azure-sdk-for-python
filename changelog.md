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
