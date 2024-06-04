# Release History

## 1.0.0b3 (2023-07-18)

### Features Added

- Added the new share resources capability that allows listing resources associated with sent and received shares.
- Added missing test cases to test_sent_shares and test_received_shares

### Breaking Changes

- In _operations.py, the `skip_token` parameter was removed from list definitions in favor of placing it within `nextLink` 
- The `orderby` parameter in all definitions that relate to listing shares has been renamed to `order_by`

### Bugs Fixed

- Fixed Samples and Tests
- Updated broken link in samples README to point to Azure/azure-python-sdk instead of developer fork

### Other Changes

- Updated and fixed README according to feedback
- Migrated test recordings to the azure-sdk-assets repo
- Added more sanitizers to conftest.py

## 1.0.0b2 (2023-06-05)

### Bugs Fixed

- Fixed Samples and Tests

## 1.0.0b1 (2023-03-30)

### New Features

- Initial release of the Purview Share client library for python