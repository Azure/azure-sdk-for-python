# Release History

## 1.5.0 (Unreleased)
- Improved type safety and consistency across all client methods

### Other Changes
- Replaced `**kwargs` parameters with explicit typed parameters for better IDE support and type checking
- Enhanced type annotations for Long Running Operation (LRO) methods with proper `Union[bool, "PollingMethod"]` typing
- Fixed type compatibility issues with optional parameters (e.g., `quantity` in search operations)
- Added proper type hints for all method parameters while maintaining backward compatibility
- Fixed pylint and mypy compliance issues
- Improved code organization and import structure

## 1.4.0 (2025-08-28)

### Features Added
- GA release of support for mobile number types

## 1.4.0b1 (2025-07-22)

### Features Added
- Adds support for mobile number types
  - mobile numbers are location associated phone numbers with SMS capabilities
- API version `2025-06-01` is the default.

## 1.3.0 (2025-06-20)

### Features Added
- GA release of the reservations functionality.
- GA support for automated purchases of phone numbers from countries requiring a do not resell agreement.
  - For more information, refer to: https://learn.microsoft.com/azure/communication-services/concepts/numbers/sub-eligibility-number-capability

## 1.3.0b1 (2025-05-21)

### Features Added
- Adds support for the Browse Available Phone Numbers and Reservations APIs.
  - This adds an alternate way to search and purchase phone numbers that allows customers to select which phone numbers they want to reserve and purchase.
- Adds support for automated purchases of phone numbers from countries requiring a Do Not Resell agreement.
  - For more information, refer to: https://learn.microsoft.com/azure/communication-services/concepts/numbers/sub-eligibility-number-capability
- API version `2025-04-01` is the default.

## 1.2.0 (2025-02-11)

### Features Added
- GA release of Number Insight.
- API version `2025-02-11` is the default.

### Other Changes
- Updated `search_operator_information` method signature to enforce `options` as a keyword-only argument.

## 1.2.0b2 (2024-03-01)

### Features Added
- Add support for number lookup
  - Format only can be returned for no cost
  - Additional number details can be returned for a cost

## 1.2.0b1 (2023-08-04)

### Features Added
- Number Lookup API public preview
- API version `2023-05-01-preview` is the default

## 1.1.0 (2023-03-28)

### Features Added
- API version `2022-12-01` is now the default for Phone Numbers clients.
- Added support for SIP routing API version `2023-03-01`, releasing SIP routing functionality from public preview to GA.
- Added environment variable `AZURE_TEST_DOMAIN` for SIP routing tests to support domain verification.

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
[documentation]: https://learn.microsoft.com/azure/communication-services/quickstarts/access-tokens?pivots=programming-language-python
