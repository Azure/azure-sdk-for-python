import inspect
import re
import warnings
import sys
from azure.eventgrid._generated import models

backward_compat = {
    'AcsChatMemberAddedToThreadWithUserEventName': "Microsoft.Communication.ChatMemberAddedToThreadWithUser",
    'ResourceWriteFailureEventName': "Microsoft.Resources.ResourceWriteFailure",
    'IoTHubDeviceDeletedEventName': "Microsoft.Devices.DeviceDeleted",
    'IoTHubDeviceDisconnectedEventName': "Microsoft.Devices.DeviceDisconnected",
    'ResourceDeleteFailureEventName': "Microsoft.Resources.ResourceDeleteFailure",
    'ResourceDeleteCancelEventName': "Microsoft.Resources.ResourceDeleteCancel",
    'AcsChatThreadParticipantAddedEventName': "Microsoft.Communication.ChatThreadParticipantAdded",
    'ResourceDeleteSuccessEventName': "Microsoft.Resources.ResourceDeleteSuccess",
    'EventGridSubscriptionValidationEventName': "Microsoft.EventGrid.SubscriptionValidationEvent",
    'ResourceWriteSuccessEventName': "Microsoft.Resources.ResourceWriteSuccess",
    'ResourceActionSuccessEventName': "Microsoft.Resources.ResourceActionSuccess",
    'ResourceWriteCancelEventName': "Microsoft.Resources.ResourceWriteCancel",
    'ResourceActionFailureEventName': "Microsoft.Resources.ResourceActionFailure",
    'AcsChatMemberRemovedFromThreadWithUserEventName': "Microsoft.Communication.ChatMemberRemovedFromThreadWithUser",
    'IoTHubDeviceConnectedEventName': "Microsoft.Devices.DeviceConnected",
    'EventGridSubscriptionDeletedEventName': "Microsoft.EventGrid.SubscriptionDeletedEvent",
    'AcsChatThreadParticipantRemovedEventName': "Microsoft.Communication.ChatThreadParticipantRemoved",
    'ResourceActionCancelEventName': "Microsoft.Resources.ResourceActionCancel",
    'IoTHubDeviceCreatedEventName': "Microsoft.Devices.DeviceCreated"
}

def event_tuples(system_events):
    tup_list = []
    for event in system_events:
        class_name = "Name".join(event[0].rsplit('Data', 1))
        try:
            event_name = re.findall("Microsoft.[a-zA-Z]+.[a-zA-Z]+", event[1].__doc__)[0]
        except:
            # these two are just superclasses and are known exceptions.
            if event[0] not in ('ContainerRegistryArtifactEventData', 'ContainerRegistryEventData'):
                warnings.warn("Unable to generate the event mapping for {}".format(event[0]))
                sys.exit(1)
        tup_list.append((class_name, event_name))
    return tup_list

def generate_enum_content(tuples):
    print("# these names below are for backward compat only - refrain from using them.")
    for k, v in backward_compat.items():
        print(k + " = '" + v + "'\n")
    print("# backward compat names end here.")
    for tup in tup_list:
        print(tup[0] + " = '" + tup[1].replace('API', 'Api') + "'\n")
    print("# servicebus alias")
    print("ServiceBusDeadletterMessagesAvailableWithNoListenerEventName = 'Microsoft.ServiceBus.DeadletterMessagesAvailableWithNoListeners'")

system_events = [m for m in inspect.getmembers(models) if m[0].endswith('Data')]
tup_list = event_tuples(system_events)

generate_enum_content(tup_list)
