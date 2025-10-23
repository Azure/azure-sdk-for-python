# Release History

## 1.2.0 (Unreleased)

### Features Added

- Added `TelcoMessagingClient` as a unified client providing access to all SMS-related operations through organized sub-clients.
- Added `DeliveryReportsClient` for retrieving SMS delivery reports.
- Added `OptOutsClient` for managing SMS opt-out lists.
- Enhanced documentation with comprehensive examples for all new clients.
- Added sample files demonstrating usage of the new clients.
- `SmsClient.send` now supports `delivery_report_timeout_in_seconds` option (60-43200 seconds). If no delivery report is received within the configured time, the service generates an Expired report.
- `SmsClient.send` now supports MessagingConnect option, where clients can pass `messaging_connect_api_key` and `messaging_connect_partner_name` for Messaging Connect feature to enable SMS delivery through partner networks.
- All clients now support optional `api_version` parameter to specify a custom API version. Supports both direct instantiation and `from_connection_string` methods.

## 1.1.0 (2024-10-03)

### Other Changes
- Python 2.7 is no longer supported. Please use Python version 3.7 or later. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).

## 1.0.1 (2021-06-08)

### Bug Fixes

- Fixed async client to use async bearer token credential policy instead of sync policy.

## 1.0.0 (2021-03-29)

- Stable release of `azure-communication-sms`.

## 1.0.0b6 (2021-03-09)

### Added

- Added support for Azure Active Directory authentication.
- Added support for 1:N SMS messaging.
- Added support for SMS idempotency.
- Send method series in SmsClient are idempotent under retry policy.
- Added support for tagging SMS messages.
- The SmsClient constructor uses type `TokenCredential` and `AsyncTokenCredential` for the credential parameter.

### Breaking

- Send method takes in strings for phone numbers instead of `PhoneNumberIdentifier`.
- Send method returns a list of `SmsSendResult`s instead of a `SendSmsResponse`.
- Dropped support for Python 3.5

## 1.0.0b4 (2020-11-16)

- Updated `azure-communication-sms` version.

### Breaking Changes

- Replaced CommunicationUser with CommunicationUserIdentifier.
- Replaced PhoneNumber with PhoneNumberIdentifier.

## 1.0.0b3 (2020-10-07)

- Add dependency to `azure-communication-nspkg` package, to support py2

## 1.0.0b2 (2020-10-06)

- Updated `azure-communication-sms` version.

## 1.0.0b1 (2020-09-22)

- Preview release of the package.
