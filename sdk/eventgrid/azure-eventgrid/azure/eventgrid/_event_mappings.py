# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from enum import Enum


class SystemEventNames(str, Enum):
    """
    This enum represents the names of the various event types for the system events published to
    Azure Event Grid. To check the list of recognizable system topics,
    visit https://docs.microsoft.com/azure/event-grid/system-topics.
    """

    AcsChatMemberAddedToThreadWithUserEventName = (
        "Microsoft.Communication.ChatMemberAddedToThreadWithUser"
    )
    AcsChatMemberRemovedFromThreadWithUserEventName = (
        "Microsoft.Communication.ChatMemberRemovedFromThreadWithUser"
    )
    AcsChatMessageDeletedEventName = "Microsoft.Communication.ChatMessageDeleted"
    AcsChatMessageEditedEventName = "Microsoft.Communication.ChatMessageEdited"
    AcsChatMessageReceivedEventName = "Microsoft.Communication.ChatMessageReceived"
    AcsChatThreadCreatedWithUserEventName = (
        "Microsoft.Communication.ChatThreadCreatedWithUser"
    )
    AcsChatThreadParticipantAddedEventName = "Microsoft.Communication.ChatThreadParticipantAdded"
    AcsChatThreadParticipantRemovedEventName = "Microsoft.Communication.ChatThreadParticipantRemoved"
    AcsChatThreadPropertiesUpdatedPerUserEventName = (
        "Microsoft.Communication.ChatThreadPropertiesUpdatedPerUser"
    )
    AcsChatThreadWithUserDeletedEventName = (
        "Microsoft.Communication.ChatThreadWithUserDeleted"
    )
    AcsSmsDeliveryReportReceivedEventName = (
        "Microsoft.Communication.SMSDeliveryReportReceived"
    )
    AcsSmsReceivedEventName = "Microsoft.Communication.SMSReceived"
    AppConfigurationKeyValueDeletedEventName = (
        "Microsoft.AppConfiguration.KeyValueDeleted"
    )
    AppConfigurationKeyValueModifiedEventName = (
        "Microsoft.AppConfiguration.KeyValueModified"
    )
    ContainerRegistryChartDeletedEventName = "Microsoft.ContainerRegistry.ChartDeleted"
    ContainerRegistryChartPushedEventName = "Microsoft.ContainerRegistry.ChartPushed"
    ContainerRegistryImageDeletedEventName = "Microsoft.ContainerRegistry.ImageDeleted"
    ContainerRegistryImagePushedEventName = "Microsoft.ContainerRegistry.ImagePushed"
    EventGridSubscriptionDeletedEventName = (
        "Microsoft.EventGrid.SubscriptionDeletedEvent"
    )
    EventGridSubscriptionValidationEventName = (
        "Microsoft.EventGrid.SubscriptionValidationEvent"
    )
    EventHubCaptureFileCreatedEventName = "Microsoft.EventHub.CaptureFileCreated"
    IoTHubDeviceConnectedEventName = "Microsoft.Devices.DeviceConnected"
    IoTHubDeviceCreatedEventName = "Microsoft.Devices.DeviceCreated"
    IoTHubDeviceDeletedEventName = "Microsoft.Devices.DeviceDeleted"
    IoTHubDeviceDisconnectedEventName = "Microsoft.Devices.DeviceDisconnected"
    IotHubDeviceTelemetryEventName = "Microsoft.Devices.DeviceTelemetry"
    KeyVaultAccessPolicyChangedEventName = "Microsoft.KeyVault.VaultAccessPolicyChanged"
    KeyVaultCertificateExpiredEventName = "Microsoft.KeyVault.CertificateExpired"
    KeyVaultCertificateNearExpiryEventName = "Microsoft.KeyVault.CertificateNearExpiry"
    KeyVaultCertificateNewVersionCreatedEventName = (
        "Microsoft.KeyVault.CertificateNewVersionCreated"
    )
    KeyVaultKeyExpiredEventName = "Microsoft.KeyVault.KeyExpired"
    KeyVaultKeyNearExpiryEventName = "Microsoft.KeyVault.KeyNearExpiry"
    KeyVaultKeyNewVersionCreatedEventName = "Microsoft.KeyVault.KeyNewVersionCreated"
    KeyVaultSecretExpiredEventName = "Microsoft.KeyVault.SecretExpired"
    KeyVaultSecretNearExpiryEventName = "Microsoft.KeyVault.SecretNearExpiry"
    KeyVaultSecretNewVersionCreatedEventName = (
        "Microsoft.KeyVault.SecretNewVersionCreated"
    )
    MachineLearningServicesDatasetDriftDetectedEventName = (
        "Microsoft.MachineLearningServices.DatasetDriftDetected"
    )
    MachineLearningServicesModelDeployedEventName = (
        "Microsoft.MachineLearningServices.ModelDeployed"
    )
    MachineLearningServicesModelRegisteredEventName = (
        "Microsoft.MachineLearningServices.ModelRegistered"
    )
    MachineLearningServicesRunCompletedEventName = (
        "Microsoft.MachineLearningServices.RunCompleted"
    )
    MachineLearningServicesRunStatusChangedEventName = (
        "Microsoft.MachineLearningServices.RunStatusChanged"
    )
    MapsGeofenceEnteredEventName = "Microsoft.Maps.GeofenceEntered"
    MapsGeofenceExitedEventName = "Microsoft.Maps.GeofenceExited"
    MapsGeofenceResultEventName = "Microsoft.Maps.GeofenceResult"
    MediaJobCanceledEventName = "Microsoft.Media.JobCanceled"
    MediaJobCancelingEventName = "Microsoft.Media.JobCanceling"
    MediaJobErroredEventName = "Microsoft.Media.JobErrored"
    MediaJobFinishedEventName = "Microsoft.Media.JobFinished"
    MediaJobOutputCanceledEventName = "Microsoft.Media.JobOutputCanceled"
    MediaJobOutputCancelingEventName = "Microsoft.Media.JobOutputCanceling"
    MediaJobOutputErroredEventName = "Microsoft.Media.JobOutputErrored"
    MediaJobOutputFinishedEventName = "Microsoft.Media.JobOutputFinished"
    MediaJobOutputProcessingEventName = "Microsoft.Media.JobOutputProcessing"
    MediaJobOutputProgressEventName = "Microsoft.Media.JobOutputProgress"
    MediaJobOutputScheduledEventName = "Microsoft.Media.JobOutputScheduled"
    MediaJobOutputStateChangeEventName = "Microsoft.Media.JobOutputStateChange"
    MediaJobProcessingEventName = "Microsoft.Media.JobProcessing"
    MediaJobScheduledEventName = "Microsoft.Media.JobScheduled"
    MediaJobStateChangeEventName = "Microsoft.Media.JobStateChange"
    MediaLiveEventConnectionRejectedEventName = (
        "Microsoft.Media.LiveEventConnectionRejected"
    )
    MediaLiveEventEncoderConnectedEventName = (
        "Microsoft.Media.LiveEventEncoderConnected"
    )
    MediaLiveEventEncoderDisconnectedEventName = (
        "Microsoft.Media.LiveEventEncoderDisconnected"
    )
    MediaLiveEventIncomingDataChunkDroppedEventName = (
        "Microsoft.Media.LiveEventIncomingDataChunkDropped"
    )
    MediaLiveEventIncomingStreamReceivedEventName = (
        "Microsoft.Media.LiveEventIncomingStreamReceived"
    )
    MediaLiveEventIncomingStreamsOutOfSyncEventName = (
        "Microsoft.Media.LiveEventIncomingStreamsOutOfSync"
    )
    MediaLiveEventIncomingVideoStreamsOutOfSyncEventName = (
        "Microsoft.Media.LiveEventIncomingVideoStreamsOutOfSync"
    )
    MediaLiveEventIngestHeartbeatEventName = "Microsoft.Media.LiveEventIngestHeartbeat"
    MediaLiveEventTrackDiscontinuityDetectedEventName = (
        "Microsoft.Media.LiveEventTrackDiscontinuityDetected"
    )
    ResourceActionCancelEventName = "Microsoft.Resources.ResourceActionCancel"
    ResourceActionFailureEventName = "Microsoft.Resources.ResourceActionFailure"
    ResourceActionSuccessEventName = "Microsoft.Resources.ResourceActionSuccess"
    ResourceDeleteCancelEventName = "Microsoft.Resources.ResourceDeleteCancel"
    ResourceDeleteFailureEventName = "Microsoft.Resources.ResourceDeleteFailure"
    ResourceDeleteSuccessEventName = "Microsoft.Resources.ResourceDeleteSuccess"
    ResourceWriteCancelEventName = "Microsoft.Resources.ResourceWriteCancel"
    ResourceWriteFailureEventName = "Microsoft.Resources.ResourceWriteFailure"
    ResourceWriteSuccessEventName = "Microsoft.Resources.ResourceWriteSuccess"
    ServiceBusActiveMessagesAvailableWithNoListenersEventName = (
        "Microsoft.ServiceBus.ActiveMessagesAvailableWithNoListeners"
    )
    ServiceBusDeadletterMessagesAvailableWithNoListenerEventName = (
        "Microsoft.ServiceBus.DeadletterMessagesAvailableWithNoListener"
    )
    ServiceBusDeadletterMessagesAvailablePeriodicNotificationsEventName = (
        "Microsoft.ServiceBus.DeadletterMessagesAvailablePeriodicNotifications"
    )
    ServiceBusActiveMessagesAvailablePeriodicNotificationsEventName = (
        "Microsoft.ServiceBus.ActiveMessagesAvailablePeriodicNotifications"
    )
    StorageBlobCreatedEventName = "Microsoft.Storage.BlobCreated"
    StorageBlobDeletedEventName = "Microsoft.Storage.BlobDeleted"
    StorageBlobRenamedEventName = "Microsoft.Storage.BlobRenamed"
    StorageDirectoryCreatedEventName = "Microsoft.Storage.DirectoryCreated"
    StorageDirectoryDeletedEventName = "Microsoft.Storage.DirectoryDeleted"
    StorageDirectoryRenamedEventName = "Microsoft.Storage.DirectoryRenamed"
    StorageLifecyclePolicyCompletedEventName = (
        "Microsoft.Storage.LifecyclePolicyCompleted"
    )
    WebAppServicePlanUpdatedEventName = "Microsoft.Web.AppServicePlanUpdated"
    WebAppUpdatedEventName = "Microsoft.Web.AppUpdated"
    WebBackupOperationCompletedEventName = "Microsoft.Web.BackupOperationCompleted"
    WebBackupOperationFailedEventName = "Microsoft.Web.BackupOperationFailed"
    WebBackupOperationStartedEventName = "Microsoft.Web.BackupOperationStarted"
    WebRestoreOperationCompletedEventName = "Microsoft.Web.RestoreOperationCompleted"
    WebRestoreOperationFailedEventName = "Microsoft.Web.RestoreOperationFailed"
    WebRestoreOperationStartedEventName = "Microsoft.Web.RestoreOperationStarted"
    WebSlotSwapCompletedEventName = "Microsoft.Web.SlotSwapCompleted"
    WebSlotSwapFailedEventName = "Microsoft.Web.SlotSwapFailed"
    WebSlotSwapStartedEventName = "Microsoft.Web.SlotSwapStarted"
    WebSlotSwapWithPreviewCancelledEventName = (
        "Microsoft.Web.SlotSwapWithPreviewCancelled"
    )
    WebSlotSwapWithPreviewStartedEventName = "Microsoft.Web.SlotSwapWithPreviewStarted"
