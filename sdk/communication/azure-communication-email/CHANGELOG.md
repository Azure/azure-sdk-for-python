# Release History

## 1.0.1 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.0 (2023-03-31)

### Features Added
The public release of the Azure Communication Services SDK for Email has the following features:

- send emails with a variety of options (multiple recipients, attachments, etc.)
- poll for the status of the email that was sent to track its progress

## 1.0.0b2 (2023-03-01)

### Features Added
- Adding support for AAD token authentication
- Added the ability to specify the API version by an optional `api_version` keyword parameter.

### Breaking Changes
- Made the SDK Model-less. Objects are now constructed using a dictionary instead of a model.
- Reworked the SDK to follow the LRO (long running operation) approach. The 'begin_send' method returns a poller that can be used to check for the status of sending the email and retrieve the result. The return object has been adjusted to fit this approach. 
- The `get_send_status` method has been removed.
- The `sender` property has been changed to `senderAddress`.
- The `email` property under the recipient object has been changed to `address`.
- The `attachmentType` property under `attachments` has been changed to 'contentType'. This now accepts the attachment mime type.
- The `contentBytesBase64` property under `attachments` has been changed to `contentInBase64`
- Custom headers in the email message are now key/value pairs.
- The importance property was removed. Email importance can now be specified through either the `x-priority` or `x-msmail-priority` custom headers.

### Other Changes
Python 3.6 is no longer supported. Please use Python version 3.7 or later. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).

## 1.0.0b1 (2022-08-09)

The first preview of the Azure Communication Email Client has the following features:

- send emails to multiple recipients with attachments
- get the status of a sent message
