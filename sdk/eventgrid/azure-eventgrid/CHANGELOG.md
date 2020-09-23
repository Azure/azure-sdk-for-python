# Release History

## 2.0.0b2 (2020-09-25)

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
