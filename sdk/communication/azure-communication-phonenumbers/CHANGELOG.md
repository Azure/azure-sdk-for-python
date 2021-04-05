# Release History

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
[read_me]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/communication/azure-communication-phonenumbers/README.md
[documentation]: https://docs.microsoft.com/azure/communication-services/quickstarts/access-tokens?pivots=programming-language-python
