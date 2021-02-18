
# Release History

## 1.2.3 (Unreleased)


## 1.2.2 (2020-11-09)

### Bug Fixes

- Fixed bug to allow polling for PATCH long-running-operation.

## 1.2.1 (2020-10-05)

### Bug Fixes

- Fixed bug to allow polling in the case of parameterized endpoints with relative polling urls  #14097

## 1.2.0 (2020-07-06)

### Bug Fixes

- The `allowed_header_names` property of ARMHttpLoggingPolicy now includes the management plane specific
allowed headers  #12218

### Features

- Added `http_logging_policy` property on the `Configuration` object, allowing users to individually
set the http logging policy of the config  #12218

## 1.1.0 (2020-05-04)

### Features

- Info logger now logs ARM throttling information  #10940


## 1.0.0 (2020-04-09)

### Features

- Internal refactoring of polling on top of azure-core 1.4.0

## 1.0.0b1 (2020-03-10)

- Preview 1 release
