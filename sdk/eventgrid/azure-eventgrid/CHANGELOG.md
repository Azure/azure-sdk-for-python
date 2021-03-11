# Release History

## 4.0.0 (2021-03-09)

  **Note:** This is the first stable release of our efforts to create a user-friendly and Pythonic client library for Azure EventGrid. Users migrating from `v1.x` are advised to view the [migration guide](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/migration_guide.md).

  **New Features**
  - `azure-eventgrid` package now supports `azure.core.messaging.CloudEvent` which honors the CNCF CloudEvent spec.
  - `azure.eventgrid.SystemEventNames` can be used to get the event model type mapping for system events.
  - Implements the `EventGridPublisherClient` for the publish flow for EventGrid Events, CloudEvents and Custom schema events.

  **Breaking Changes**
  - `azure.eventgrid.models` namespace along with all the models in it are now removed.:
      - JSON documentation on the events is available here: https://docs.microsoft.com/azure/event-grid/system-topics
      - `azure.eventgrid.SystemEventNames` provides the list of available events name for easy switching.
  - `azure.eventgrid.event_grid_client.EventGridClient` is now removed in favor of `azure.eventgrid.EventGridPublisherClient`.
  - `azure.eventgrid.event_grid_client.EventGridClientConfiguration` is now removed.


## 2.0.0 (2021-03-09)

  **Disclaimer:** v2.0.0 is functionally equivalent to v4.0.0. Users are advised to use v4.0.0 instead of this.

  **Breaking Changes**
  - `~azure.eventgrid.CloudEvent` is now removed in favor of `~azure.core.messaging.CloudEvent`.
  - All the `SystemEventNames` related to Azure Communication Service starting with `ACS****` are renamed to `Acs***` to honor pascal case.

  **Features**
  - Added support for two new `SystemEvents` - `ServiceBusDeadletterMessagesAvailablePeriodicNotificationsEventData` and `ServiceBusActiveMessagesAvailablePeriodicNotificationsEventData`

## 2.0.0b5 (2021-02-10)

  **Breaking Changes**
  - `EventGridSharedAccessSignatureCredential` is deprecated in favor of `AzureSasCredential`.
  - `azure.eventgrid.models` namespace along with all the models in it are now removed. `azure.eventgrid.SystemEventNames` can be used to get the event model type mapping.
  - `topic_hostname` is renamed to `endpoint` in the `EventGridPublisherClient`.
  - `azure.eventgrid.generate_shared_access_signature` method is now renamed to `generate_sas`.
  - `EventGridConsumer`is now removed. Please see the samples to see how events can be deserialized.
  - `CustomEvent` model is removed. Dictionaries must be used to send a custom schema.
  
  **Bug Fixes**
  - `EventGridEvent` has two additional required positional parameters namely, `data` and `data_version`.
  - `EventGridPublisherClient` now appropriately throws a `ValueError` if an invalid credential is passed during initialization.

## 2.0.0b4 (2020-11-11)

  **Bug Fixes**
  - `TypeError` is raised when bytes are passed to an `EventGridEvent`.

## 2.0.0b3 (2020-10-05)

  **Feature**
  - Added support for Keyvault Event Types
  - Added distributed tracing support for CloudEvents

## 2.0.0b2 (2020-09-24)

  **Features**
  - Added support for Azure Communication Services event types.

## 2.0.0b1 (2020-09-08)

  **Features**
  - Version (2.0.0b1) is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure EventGrid.
  For more information about this, and preview releases of other Azure SDK libraries, please visit https://azure.github.io/azure-sdk/releases/latest/python.html.
  - Added Support for `CloudEvents`.
  - Implements the `EventGridPublisherClient` for the publish flow for EventGrid Events, CloudEvents and CustomEvents.
  - Implements the `EventGridConsumer` for the consume flow of the events.

## 1.3.0 (2019-05-20)

  - Event Schemas for new event types from IotHub, Media Services,
    Container Registry, Maps, and AppConfiguration services.

## 1.2.0 (2018-08-28)

  - Event Schemas for new events (IotHub DeviceConnected and
    DeviceDisconnected events, Resource events related to actions), and
    breaking changes to the schema for IotHub DeviceCreated event and
    IotHub DeviceDeleted event.

## 1.1.0 (2018-05-24)

  - Event Schemas for EventGrid subscription validation event, Azure
    Media events, and ServiceBus events.

## 1.0.0 (2018-04-26)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**Features**

  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance
  - Support for consuming Azure Container Registry events and Azure IoT
    Hub events published to Event Grid.

## 0.1.0 (2018-01-30)

  - Initial Release
