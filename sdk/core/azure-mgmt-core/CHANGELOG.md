# Release History

## 1.4.0 (Unreleased)

### Features

- Added AuxiliaryAuthenticationPolicy

## 1.3.1 (2022-06-14)

### Other Changes

- Updated mindep about `azure-core` from `1.15.0` to `1.23.0`

## 1.3.0 (2021-07-01)

### Features

- Support CAE

## 1.3.0b3 (2021-06-07)

### Changed

- Updated required `azure-core` version

## 1.3.0b2 (2021-05-13)

### Changed

- Updated required `azure-core` version

## 1.3.0b1 (2021-03-10)

### Features

- ARMChallengeAuthenticationPolicy supports bearer token authorization and CAE challenges

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
