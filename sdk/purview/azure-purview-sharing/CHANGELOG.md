# Release History

## 1.0.0b4 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.0b3 (2023-06-29)

### Features Added

- Added the new share resources capability that allows listing resources associated with sent and received shares.
- Added missing test cases to test_sent_shares and test_received_shares

### Breaking Changes

- In _operations.py, under the list_attached definition, the `skip_token` parameter was removed list definitions in favor of placing it within `nextLink`. 

### Bugs Fixed

- Fixed Samples and Tests

### Other Changes

- Updated and fixed README

## 1.0.0b2 (2023-06-05)

### Bugs Fixed

- Fixed Samples and Tests

## 1.0.0b1 (2023-03-30)

### New Features

- Initial release of the Purview Share client library for python
