#############################################################################
####These files are used to extract the enums - update this list as necessary
#############################################################################
files = [

    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.Communication/stable/2018-01-01/AzureCommunicationServices.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.ApiManagement/stable/2018-01-01/APIManagement.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.AppConfiguration/stable/2018-01-01/AppConfiguration.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.ContainerRegistry/stable/2018-01-01/ContainerRegistry.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.ContainerService/stable/2018-01-01/ContainerService.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.EventHub/stable/2018-01-01/EventHub.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.EventGrid/stable/2018-01-01/EventGrid.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.Devices/stable/2018-01-01/IotHub.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.KeyVault/stable/2018-01-01/KeyVault.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.MachineLearningServices/stable/2018-01-01/MachineLearningServices.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.Media/stable/2018-01-01/MediaServices.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.Maps/stable/2018-01-01/Maps.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.PolicyInsights/stable/2018-01-01/PolicyInsights.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.Cache/stable/2018-01-01/RedisCache.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.Resources/stable/2018-01-01/Resources.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.ServiceBus/stable/2018-01-01/ServiceBus.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.SignalRService/stable/2018-01-01/SignalRService.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.Storage/stable/2018-01-01/Storage.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.Web/stable/2018-01-01/Web.json",
    "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/eventgrid/data-plane/Microsoft.HealthcareApis/stable/2018-01-01/HealthcareApis.json",
    ]


#######################################################
### Used for backward compatibility. Don't change this
#######################################################
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
    'IoTHubDeviceCreatedEventName': "Microsoft.Devices.DeviceCreated",
}

additional_events = {
    'ContainerRegistryArtifactEventName': 'Microsoft.AppConfiguration.KeyValueModified',
    'KeyVaultAccessPolicyChangedEventName': 'Microsoft.KeyVault.VaultAccessPolicyChanged',
    'ContainerRegistryEventName': 'Microsoft.ContainerRegistry.ChartPushed',
    'ServiceBusDeadletterMessagesAvailableWithNoListenerEventName': 'Microsoft.ServiceBus.DeadletterMessagesAvailableWithNoListeners'
}

EXCEPTIONS = ['ContainerRegistryArtifactEventData', 'ContainerRegistryEventData']
