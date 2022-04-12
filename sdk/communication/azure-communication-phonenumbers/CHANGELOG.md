# Release History

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
