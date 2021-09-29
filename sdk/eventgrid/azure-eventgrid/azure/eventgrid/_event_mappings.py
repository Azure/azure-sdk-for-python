# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from enum import Enum

# pylint: disable=line-too-long

class SystemEventNames(str, Enum):
    """
    This enum represents the names of the various event types for the system events published to
    Azure Event Grid. To check the list of recognizable system topics,
    visit https://docs.microsoft.com/azure/event-grid/system-topics.
    """
    # these names below are for backward compat only - refrain from using them.
    AcsChatMemberAddedToThreadWithUserEventName = 'Microsoft.Communication.ChatMemberAddedToThreadWithUser'

    ResourceWriteFailureEventName = 'Microsoft.Resources.ResourceWriteFailure'

    IoTHubDeviceDeletedEventName = 'Microsoft.Devices.DeviceDeleted'

    IoTHubDeviceDisconnectedEventName = 'Microsoft.Devices.DeviceDisconnected'

    ResourceDeleteFailureEventName = 'Microsoft.Resources.ResourceDeleteFailure'

    ResourceDeleteCancelEventName = 'Microsoft.Resources.ResourceDeleteCancel'

    AcsChatThreadParticipantAddedEventName = 'Microsoft.Communication.ChatThreadParticipantAdded'

    ResourceDeleteSuccessEventName = 'Microsoft.Resources.ResourceDeleteSuccess'

    EventGridSubscriptionValidationEventName = 'Microsoft.EventGrid.SubscriptionValidationEvent'

    ResourceWriteSuccessEventName = 'Microsoft.Resources.ResourceWriteSuccess'

    ResourceActionSuccessEventName = 'Microsoft.Resources.ResourceActionSuccess'

    ResourceWriteCancelEventName = 'Microsoft.Resources.ResourceWriteCancel'

    ResourceActionFailureEventName = 'Microsoft.Resources.ResourceActionFailure'

    AcsChatMemberRemovedFromThreadWithUserEventName = 'Microsoft.Communication.ChatMemberRemovedFromThreadWithUser'

    IoTHubDeviceConnectedEventName = 'Microsoft.Devices.DeviceConnected'

    EventGridSubscriptionDeletedEventName = 'Microsoft.EventGrid.SubscriptionDeletedEvent'

    AcsChatThreadParticipantRemovedEventName = 'Microsoft.Communication.ChatThreadParticipantRemoved'

    ResourceActionCancelEventName = 'Microsoft.Resources.ResourceActionCancel'

    IoTHubDeviceCreatedEventName = 'Microsoft.Devices.DeviceCreated'

    # backward compat names end here.
    AcsChatMessageDeletedEventName = 'Microsoft.Communication.ChatMessageDeleted'

    AcsChatMessageDeletedInThreadEventName = 'Microsoft.Communication.ChatMessageDeletedInThread'

    AcsChatMessageEditedEventName = 'Microsoft.Communication.ChatMessageEdited'

    AcsChatMessageEditedInThreadEventName = 'Microsoft.Communication.ChatMessageEditedInThread'

    AcsChatMessageReceivedEventName = 'Microsoft.Communication.ChatMessageReceived'

    AcsChatMessageReceivedInThreadEventName = 'Microsoft.Communication.ChatMessageReceivedInThread'

    AcsChatParticipantAddedToThreadEventName = 'Microsoft.Communication.ChatThreadParticipantAdded'

    AcsChatParticipantAddedToThreadWithUserEventName = 'Microsoft.Communication.ChatParticipantAddedToThreadWithUser'

    AcsChatParticipantRemovedFromThreadEventName = 'Microsoft.Communication.ChatThreadParticipantRemoved'

    AcsChatParticipantRemovedFromThreadWithUserEventName = 'Microsoft.Communication.ChatParticipantRemovedFromThreadWithUser'

    AcsChatThreadCreatedEventName = 'Microsoft.Communication.ChatThreadCreated'

    AcsChatThreadCreatedWithUserEventName = 'Microsoft.Communication.ChatThreadCreatedWithUser'

    AcsChatThreadDeletedEventName = 'Microsoft.Communication.ChatThreadDeleted'

    AcsChatThreadPropertiesUpdatedEventName = 'Microsoft.Communication.ChatThreadPropertiesUpdated'

    AcsChatThreadPropertiesUpdatedPerUserEventName = 'Microsoft.Communication.ChatThreadPropertiesUpdatedPerUser'

    AcsChatThreadWithUserDeletedEventName = 'Microsoft.Communication.ChatThreadWithUserDeleted'

    AcsRecordingFileStatusUpdatedEventName = 'Microsoft.Communication.RecordingFileStatusUpdated'

    AcsSmsDeliveryReportReceivedEventName = 'Microsoft.Communication.SMSDeliveryReportReceived'

    AcsSmsReceivedEventName = 'Microsoft.Communication.SMSReceived'

    AppConfigurationKeyValueDeletedEventName = 'Microsoft.AppConfiguration.KeyValueDeleted'

    AppConfigurationKeyValueModifiedEventName = 'Microsoft.AppConfiguration.KeyValueModified'

    ContainerRegistryArtifactEventName = 'Microsoft.AppConfiguration.KeyValueModified'

    ContainerRegistryChartDeletedEventName = 'Microsoft.ContainerRegistry.ChartDeleted'

    ContainerRegistryChartPushedEventName = 'Microsoft.ContainerRegistry.ChartPushed'

    ContainerRegistryEventName = 'Microsoft.ContainerRegistry.ChartPushed'

    ContainerRegistryImageDeletedEventName = 'Microsoft.ContainerRegistry.ImageDeleted'

    ContainerRegistryImagePushedEventName = 'Microsoft.ContainerRegistry.ImagePushed'

    ContainerServiceNewKubernetesVersionAvailableEventName = 'Microsoft.ContainerService.NewKubernetesVersionAvailable'

    EventHubCaptureFileCreatedEventName = 'Microsoft.EventHub.CaptureFileCreated'

    IotHubDeviceConnectedEventName = 'Microsoft.Devices.DeviceConnected'

    IotHubDeviceCreatedEventName = 'Microsoft.Devices.DeviceCreated'

    IotHubDeviceDeletedEventName = 'Microsoft.Devices.DeviceDeleted'

    IotHubDeviceDisconnectedEventName = 'Microsoft.Devices.DeviceDisconnected'

    IotHubDeviceTelemetryEventName = 'Microsoft.Devices.DeviceTelemetry'

    KeyVaultAccessPolicyChangedEventName = 'Microsoft.KeyVault.VaultAccessPolicyChanged'

    KeyVaultCertificateExpiredEventName = 'Microsoft.KeyVault.CertificateExpired'

    KeyVaultCertificateNearExpiryEventName = 'Microsoft.KeyVault.CertificateNearExpiry'

    KeyVaultCertificateNewVersionCreatedEventName = 'Microsoft.KeyVault.CertificateNewVersionCreated'

    KeyVaultKeyExpiredEventName = 'Microsoft.KeyVault.KeyExpired'

    KeyVaultKeyNearExpiryEventName = 'Microsoft.KeyVault.KeyNearExpiry'

    KeyVaultKeyNewVersionCreatedEventName = 'Microsoft.KeyVault.KeyNewVersionCreated'

    KeyVaultSecretExpiredEventName = 'Microsoft.KeyVault.SecretExpired'

    KeyVaultSecretNearExpiryEventName = 'Microsoft.KeyVault.SecretNearExpiry'

    KeyVaultSecretNewVersionCreatedEventName = 'Microsoft.KeyVault.SecretNewVersionCreated'

    MachineLearningServicesDatasetDriftDetectedEventName = 'Microsoft.MachineLearningServices.DatasetDriftDetected'

    MachineLearningServicesModelDeployedEventName = 'Microsoft.MachineLearningServices.ModelDeployed'

    MachineLearningServicesModelRegisteredEventName = 'Microsoft.MachineLearningServices.ModelRegistered'

    MachineLearningServicesRunCompletedEventName = 'Microsoft.MachineLearningServices.RunCompleted'

    MachineLearningServicesRunStatusChangedEventName = 'Microsoft.MachineLearningServices.RunStatusChanged'

    MapsGeofenceEnteredEventName = 'Microsoft.Maps.GeofenceEntered'

    MapsGeofenceExitedEventName = 'Microsoft.Maps.GeofenceExited'

    MapsGeofenceResultEventName = 'Microsoft.Maps.GeofenceResult'

    MediaJobCanceledEventName = 'Microsoft.Media.JobCanceled'

    MediaJobCancelingEventName = 'Microsoft.Media.JobCanceling'

    MediaJobErroredEventName = 'Microsoft.Media.JobErrored'

    MediaJobFinishedEventName = 'Microsoft.Media.JobFinished'

    MediaJobOutputCanceledEventName = 'Microsoft.Media.JobOutputCanceled'

    MediaJobOutputCancelingEventName = 'Microsoft.Media.JobOutputCanceling'

    MediaJobOutputErroredEventName = 'Microsoft.Media.JobOutputErrored'

    MediaJobOutputFinishedEventName = 'Microsoft.Media.JobOutputFinished'

    MediaJobOutputProcessingEventName = 'Microsoft.Media.JobOutputProcessing'

    MediaJobOutputProgressEventName = 'Microsoft.Media.JobOutputProgress'

    MediaJobOutputScheduledEventName = 'Microsoft.Media.JobOutputScheduled'

    MediaJobOutputStateChangeEventName = 'Microsoft.Media.JobOutputStateChange'

    MediaJobProcessingEventName = 'Microsoft.Media.JobProcessing'

    MediaJobScheduledEventName = 'Microsoft.Media.JobScheduled'

    MediaJobStateChangeEventName = 'Microsoft.Media.JobStateChange'

    MediaLiveEventConnectionRejectedEventName = 'Microsoft.Media.LiveEventConnectionRejected'

    MediaLiveEventEncoderConnectedEventName = 'Microsoft.Media.LiveEventEncoderConnected'

    MediaLiveEventEncoderDisconnectedEventName = 'Microsoft.Media.LiveEventEncoderDisconnected'

    MediaLiveEventIncomingDataChunkDroppedEventName = 'Microsoft.Media.LiveEventIncomingDataChunkDropped'

    MediaLiveEventIncomingStreamReceivedEventName = 'Microsoft.Media.LiveEventIncomingStreamReceived'

    MediaLiveEventIncomingStreamsOutOfSyncEventName = 'Microsoft.Media.LiveEventIncomingStreamsOutOfSync'

    MediaLiveEventIncomingVideoStreamsOutOfSyncEventName = 'Microsoft.Media.LiveEventIncomingVideoStreamsOutOfSync'

    MediaLiveEventIngestHeartbeatEventName = 'Microsoft.Media.LiveEventIngestHeartbeat'

    MediaLiveEventTrackDiscontinuityDetectedEventName = 'Microsoft.Media.LiveEventTrackDiscontinuityDetected'

    PolicyInsightsPolicyStateChangedEventName = 'Microsoft.PolicyInsights.PolicyStateChanged'

    PolicyInsightsPolicyStateCreatedEventName = 'Microsoft.PolicyInsights.PolicyStateCreated'

    PolicyInsightsPolicyStateDeletedEventName = 'Microsoft.PolicyInsights.PolicyStateDeleted'

    RedisExportRDBCompletedEventName = 'Microsoft.Cache.ExportRDBCompleted'

    RedisImportRDBCompletedEventName = 'Microsoft.Cache.ImportRDBCompleted'

    RedisPatchingCompletedEventName = 'Microsoft.Cache.PatchingCompleted'

    RedisScalingCompletedEventName = 'Microsoft.Cache.ScalingCompleted'

    ResourceActionCancelName = 'Microsoft.Resources.ResourceActionCancel'

    ResourceActionFailureName = 'Microsoft.Resources.ResourceActionFailure'

    ResourceActionSuccessName = 'Microsoft.Resources.ResourceActionSuccess'

    ResourceDeleteCancelName = 'Microsoft.Resources.ResourceDeleteCancel'

    ResourceDeleteFailureName = 'Microsoft.Resources.ResourceDeleteFailure'

    ResourceDeleteSuccessName = 'Microsoft.Resources.ResourceDeleteSuccess'

    ResourceWriteCancelName = 'Microsoft.Resources.ResourceWriteCancel'

    ResourceWriteFailureName = 'Microsoft.Resources.ResourceWriteFailure'

    ResourceWriteSuccessName = 'Microsoft.Resources.ResourceWriteSuccess'

    ServiceBusActiveMessagesAvailablePeriodicNotificationsEventName = 'Microsoft.ServiceBus.ActiveMessagesAvailablePeriodicNotifications'

    ServiceBusActiveMessagesAvailableWithNoListenersEventName = 'Microsoft.ServiceBus.ActiveMessagesAvailableWithNoListeners'

    ServiceBusDeadletterMessagesAvailablePeriodicNotificationsEventName = 'Microsoft.ServiceBus.DeadletterMessagesAvailablePeriodicNotifications'

    ServiceBusDeadletterMessagesAvailableWithNoListenersEventName = 'Microsoft.ServiceBus.DeadletterMessagesAvailableWithNoListeners'

    SignalRServiceClientConnectionConnectedEventName = 'Microsoft.SignalRService.ClientConnectionConnected'

    SignalRServiceClientConnectionDisconnectedEventName = 'Microsoft.SignalRService.ClientConnectionDisconnected'

    StorageAsyncOperationInitiatedEventName = 'Microsoft.Storage.AsyncOperationInitiated'

    StorageBlobCreatedEventName = 'Microsoft.Storage.BlobCreated'

    StorageBlobDeletedEventName = 'Microsoft.Storage.BlobDeleted'

    StorageBlobInventoryPolicyCompletedEventName = 'Microsoft.Storage.BlobInventoryPolicyCompleted'

    StorageBlobRenamedEventName = 'Microsoft.Storage.BlobRenamed'

    StorageBlobTierChangedEventName = 'Microsoft.Storage.BlobTierChanged'

    StorageDirectoryCreatedEventName = 'Microsoft.Storage.DirectoryCreated'

    StorageDirectoryDeletedEventName = 'Microsoft.Storage.DirectoryDeleted'

    StorageDirectoryRenamedEventName = 'Microsoft.Storage.DirectoryRenamed'

    StorageLifecyclePolicyCompletedEventName = 'Microsoft.Storage.LifecyclePolicyCompleted'

    SubscriptionDeletedEventName = 'Microsoft.EventGrid.SubscriptionDeletedEvent'

    SubscriptionValidationEventName = 'Microsoft.EventGrid.SubscriptionValidationEvent'

    WebAppServicePlanUpdatedEventName = 'Microsoft.Web.AppServicePlanUpdated'

    WebAppUpdatedEventName = 'Microsoft.Web.AppUpdated'

    WebBackupOperationCompletedEventName = 'Microsoft.Web.BackupOperationCompleted'

    WebBackupOperationFailedEventName = 'Microsoft.Web.BackupOperationFailed'

    WebBackupOperationStartedEventName = 'Microsoft.Web.BackupOperationStarted'

    WebRestoreOperationCompletedEventName = 'Microsoft.Web.RestoreOperationCompleted'

    WebRestoreOperationFailedEventName = 'Microsoft.Web.RestoreOperationFailed'

    WebRestoreOperationStartedEventName = 'Microsoft.Web.RestoreOperationStarted'

    WebSlotSwapCompletedEventName = 'Microsoft.Web.SlotSwapCompleted'

    WebSlotSwapFailedEventName = 'Microsoft.Web.SlotSwapFailed'

    WebSlotSwapStartedEventName = 'Microsoft.Web.SlotSwapStarted'

    WebSlotSwapWithPreviewCancelledEventName = 'Microsoft.Web.SlotSwapWithPreviewCancelled'

    WebSlotSwapWithPreviewStartedEventName = 'Microsoft.Web.SlotSwapWithPreviewStarted'

    # servicebus alias
    ServiceBusDeadletterMessagesAvailableWithNoListenerEventName = 'Microsoft.ServiceBus.DeadletterMessagesAvailableWithNoListeners'
