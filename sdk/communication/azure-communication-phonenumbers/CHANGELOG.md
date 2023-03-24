# Release History

## 1.1.0b4 (Unreleased)

### Features Added
- API version `2022-12-01` is now the default for Phone Numbers clients.
- Added support for SIP routing API version `2023-03-01`, releasing SIP routing functionality from public preview to GA.
- Added environment variable `AZURE_TEST_DOMAIN` for SIP routing tests to support domain verification.

### Breaking Changes

### Bugs Fixed
- Adds missing API version `2022-12-01` to the list of supported API versions.

### Other Changes
- Changed list_routes and list_trunks functions on SIP routing client to return (Async)ItemPaged object.

## 1.1.0b3 (2023-01-10)
- Users can now manage SIP configuration for Direct routing.
- Adds support for Azure Communication Services Phone Numbers Browse API Methods.

### Features Added
- Added support for API version `2022-12-01`, giving users the ability to:
  - Get all supported countries
  - Get all supported localities given a country code.
  - Get all area codes from a given country code / locality.
  - Get all offerings from a given country code.
- Added new SIP routing client for handling Direct routing numbers.
- Added the ability specify the API version by an optional `api_version` keyword parameter.

### Other Changes
- Python 3.6 is no longer supported. Please use Python version 3.7 or later. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).
- Updated the default polling interval to 2 seconds, it can still be overwritten by using the keyword argument "polling_interval".
- Trying to update capabilities with empty phone number will throw `ValueError`. Prior to this change, the client would make an HTTP request that would always fail.
- Migrated tests from vcrpy to test proxy.

## 1.1.0b2 (2022-03-30)

### Other Changes
- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 1.1.0b1 (2022-01-24)

- Users can now purchase United Kingdom (GB) toll free and geographic phone numbers for PSTN Calling
- Users can now purchase Denmark (DK) toll free and geographic phone numbers for PSTN Calling

### Features Added
- Adds support for API verion `2022-01-11-preview2`

### Other Changes
- Updates dependency `azure-core` to `1.20.0`

## 1.0.1 (2021-06-08)

### Bug Fixes

- Fixed async client to use async bearer token credential policy instead of sync policy.

## 1.0.0 (2021-04-26)

- Stable release of `azure-communication-phonenumbers`.

## 1.0.0b5 (2021-03-29)

### Breaking Changes

- Renamed AcquiredPhoneNumber to PurchasedPhoneNumber
- Renamed PhoneNumbersClient.get_phone_number and PhoneNumbersAsyncClient.get_phone_number to PhoneNumbersClient.get_purchased_phone_number
  and PhoneNumbersAsyncClient.get_purchased_phone_number
- Renamed PhoneNumbersClient.list_acquired_phone_numbers and PhoneNumbersAsyncClient.list_acquired_phone_numbers to PhoneNumbersClient.list_purchased_phone_numbers
  and PhoneNumbersAsyncClient.list_purchased_phone_numbers

## 1.0.0b4 (2021-03-09)

- Dropped support for Python 3.5

### Added

- Added PhoneNumbersClient (originally was part of the azure.communication.administration package).

<!-- LINKS -->

[read_me]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-phonenumbers/README.md
[documentation]: https://docs.microsoft.com/azure/communication-services/quickstarts/access-tokens?pivots=programming-language-python
