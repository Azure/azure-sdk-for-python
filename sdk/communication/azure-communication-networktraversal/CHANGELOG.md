# Release History

## 1.1.0b1 (2022-03-23)

### Features Added

- Adding optional parameter to GetRelayConfiguration to choose credential Time-To-Live in seconds of max 48 hours.
  The default value will be used if given value exceeds it.

### Breaking Changes

- Making User, RouteType and Ttl part of the options parameter
- getRelayConfiguration can be called without parameters or passing the GetRelayConfigurationOptions parameter

## 1.0.0 (2022-02-04) (Deprecated)

### Breaking Changes

- Making parameters for get_relay_configuration keyword only

### Other Changes
Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 1.0.0b2 (2021-11-18)

### Features Added

- Made User Identity an optional parameter when getting a Relay Configuration.
- Added RouteType as optional parameter when getting a Relay Configuration so users can
  choose the routing type protocol of the requested Relay Configuration.

## 1.0.0b1 (2021-08-16)

- Preview release of `azure-communication-networktraversal`.

The first preview of the Azure Communication Relay Client has the following features:

- get a Relay Configuration by creating a CommunicationRelayClient

### Added

- Added CommunicationRelayClient in preview.
- Added CommunicationRelayClient.get_relay_configuration in preview.

<!-- LINKS -->

[read_me]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/communication/
