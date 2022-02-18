# Release History

## 1.1.0 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes
Python 2.7 is no longer supported. Please use Python version 3.6 or later.

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
