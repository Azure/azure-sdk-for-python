# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

# THE VALUES IN THE ENUM ARE AUTO-GENERATED. DO NOT EDIT THIS MANUALLY.
# --------------------------------------------------------------------------------------------
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


# pylint: disable=enum-must-be-uppercase
class SystemEventNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """
    This enum represents the names of the various event types for the system events published to
    Azure Event Grid. To check the list of recognizable system topics,
    visit https://learn.microsoft.com/azure/event-grid/system-topics.
    """

    # These names at the top are 'corrected' aliases of duplicate values that appear below, which are
    # deprecated but maintained for backwards compatibility.
    AcsChatMemberAddedToThreadWithUserEventName = "Microsoft.Communication.ChatMemberAddedToThreadWithUser"

    ResourceWriteFailureEventName = "Microsoft.Resources.ResourceWriteFailure"

    IoTHubDeviceDeletedEventName = "Microsoft.Devices.DeviceDeleted"

    IoTHubDeviceDisconnectedEventName = "Microsoft.Devices.DeviceDisconnected"

    ResourceDeleteFailureEventName = "Microsoft.Resources.ResourceDeleteFailure"

    ResourceDeleteCancelEventName = "Microsoft.Resources.ResourceDeleteCancel"

    AcsChatThreadParticipantAddedEventName = "Microsoft.Communication.ChatThreadParticipantAdded"

    ResourceDeleteSuccessEventName = "Microsoft.Resources.ResourceDeleteSuccess"

    EventGridSubscriptionValidationEventName = "Microsoft.EventGrid.SubscriptionValidationEvent"

    ResourceWriteSuccessEventName = "Microsoft.Resources.ResourceWriteSuccess"

    ResourceActionSuccessEventName = "Microsoft.Resources.ResourceActionSuccess"

    ResourceWriteCancelEventName = "Microsoft.Resources.ResourceWriteCancel"

    ResourceActionFailureEventName = "Microsoft.Resources.ResourceActionFailure"

    AcsChatMemberRemovedFromThreadWithUserEventName = "Microsoft.Communication.ChatMemberRemovedFromThreadWithUser"

    IoTHubDeviceConnectedEventName = "Microsoft.Devices.DeviceConnected"

    EventGridSubscriptionDeletedEventName = "Microsoft.EventGrid.SubscriptionDeletedEvent"

    AcsChatThreadParticipantRemovedEventName = "Microsoft.Communication.ChatThreadParticipantRemoved"

    ResourceActionCancelEventName = "Microsoft.Resources.ResourceActionCancel"

    IoTHubDeviceCreatedEventName = "Microsoft.Devices.DeviceCreated"

    # Aliases end here
    AcsAdvancedMessageDeliveryStatusUpdatedEventName = "Microsoft.Communication.AdvancedMessageDeliveryStatusUpdated"

    AcsAdvancedMessageReceivedEventName = "Microsoft.Communication.AdvancedMessageReceived"

    AcsCallEndedEventName = "Microsoft.Communication.CallEnded"

    AcsCallParticipantAddedEventName = "Microsoft.Communication.CallParticipantAdded"

    AcsCallParticipantRemovedEventName = "Microsoft.Communication.CallParticipantRemoved"

    AcsCallStartedEventName = "Microsoft.Communication.CallStarted"

    AcsChatAzureBotCommandReceivedInThreadEventName = "Microsoft.Communication.ChatAzureBotCommandReceivedInThread"

    AcsChatMessageDeletedEventName = "Microsoft.Communication.ChatMessageDeleted"

    AcsChatMessageDeletedInThreadEventName = "Microsoft.Communication.ChatMessageDeletedInThread"

    AcsChatMessageEditedEventName = "Microsoft.Communication.ChatMessageEdited"

    AcsChatMessageEditedInThreadEventName = "Microsoft.Communication.ChatMessageEditedInThread"

    AcsChatMessageReceivedEventName = "Microsoft.Communication.ChatMessageReceived"

    AcsChatMessageReceivedInThreadEventName = "Microsoft.Communication.ChatMessageReceivedInThread"

    AcsChatParticipantAddedToThreadEventName = "Microsoft.Communication.ChatThreadParticipantAdded"

    AcsChatParticipantAddedToThreadWithUserEventName = "Microsoft.Communication.ChatParticipantAddedToThreadWithUser"

    AcsChatParticipantRemovedFromThreadEventName = "Microsoft.Communication.ChatThreadParticipantRemoved"

    AcsChatParticipantRemovedFromThreadWithUserEventName = (
        "Microsoft.Communication.ChatParticipantRemovedFromThreadWithUser"
    )

    AcsChatThreadCreatedEventName = "Microsoft.Communication.ChatThreadCreated"

    AcsChatThreadCreatedWithUserEventName = "Microsoft.Communication.ChatThreadCreatedWithUser"

    AcsChatThreadDeletedEventName = "Microsoft.Communication.ChatThreadDeleted"

    AcsChatThreadPropertiesUpdatedEventName = "Microsoft.Communication.ChatThreadPropertiesUpdated"

    AcsChatThreadPropertiesUpdatedPerUserEventName = "Microsoft.Communication.ChatThreadPropertiesUpdatedPerUser"

    AcsChatThreadWithUserDeletedEventName = "Microsoft.Communication.ChatThreadWithUserDeleted"

    AcsChatTypingIndicatorReceivedInThreadEventName = "Microsoft.Communication.ChatTypingIndicatorReceivedInThread"

    AcsEmailDeliveryReportReceivedEventName = "Microsoft.Communication.EmailDeliveryReportReceived"

    AcsEmailEngagementTrackingReportReceivedEventName = "Microsoft.Communication.EmailEngagementTrackingReportReceived"

    AcsIncomingCallEventName = "Microsoft.Communication.IncomingCall"

    AcsRecordingFileStatusUpdatedEventName = "Microsoft.Communication.RecordingFileStatusUpdated"

    AcsRouterJobCancelledEventName = "Microsoft.Communication.RouterJobCancelled"

    AcsRouterJobClassificationFailedEventName = "Microsoft.Communication.RouterJobClassificationFailed"

    AcsRouterJobClassifiedEventName = "Microsoft.Communication.RouterJobClassified"

    AcsRouterJobClosedEventName = "Microsoft.Communication.RouterJobClosed"

    AcsRouterJobCompletedEventName = "Microsoft.Communication.RouterJobCompleted"

    AcsRouterJobDeletedEventName = "Microsoft.Communication.RouterJobDeleted"

    AcsRouterJobExceptionTriggeredEventName = "Microsoft.Communication.RouterJobExceptionTriggered"

    AcsRouterJobQueuedEventName = "Microsoft.Communication.RouterJobQueued"

    AcsRouterJobReceivedEventName = "Microsoft.Communication.RouterJobReceived"

    AcsRouterJobSchedulingFailedEventName = "Microsoft.Communication.RouterJobSchedulingFailed"

    AcsRouterJobUnassignedEventName = "Microsoft.Communication.RouterJobUnassigned"

    AcsRouterJobWaitingForActivationEventName = "Microsoft.Communication.RouterJobWaitingForActivation"

    AcsRouterJobWorkerSelectorsExpiredEventName = "Microsoft.Communication.RouterJobWorkerSelectorsExpired"

    AcsRouterWorkerDeletedEventName = "Microsoft.Communication.RouterWorkerDeleted"

    AcsRouterWorkerDeregisteredEventName = "Microsoft.Communication.RouterWorkerDeregistered"

    AcsRouterWorkerOfferAcceptedEventName = "Microsoft.Communication.RouterWorkerOfferAccepted"

    AcsRouterWorkerOfferDeclinedEventName = "Microsoft.Communication.RouterWorkerOfferDeclined"

    AcsRouterWorkerOfferExpiredEventName = "Microsoft.Communication.RouterWorkerOfferExpired"

    AcsRouterWorkerOfferIssuedEventName = "Microsoft.Communication.RouterWorkerOfferIssued"

    AcsRouterWorkerOfferRevokedEventName = "Microsoft.Communication.RouterWorkerOfferRevoked"

    AcsRouterWorkerRegisteredEventName = "Microsoft.Communication.RouterWorkerRegistered"

    AcsRouterWorkerUpdatedEventName = "Microsoft.Communication.RouterWorkerUpdated"

    AcsSmsDeliveryReportReceivedEventName = "Microsoft.Communication.SMSDeliveryReportReceived"

    AcsSmsReceivedEventName = "Microsoft.Communication.SMSReceived"

    AcsUserDisconnectedEventName = "Microsoft.Communication.UserDisconnected"

    ApiCenterApiDefinitionAddedEventName = "Microsoft.ApiCenter.ApiDefinitionAdded"

    ApiCenterApiDefinitionUpdatedEventName = "Microsoft.ApiCenter.ApiDefinitionUpdated"

    ApiManagementApiCreatedEventName = "Microsoft.ApiManagement.APICreated"

    ApiManagementApiDeletedEventName = "Microsoft.ApiManagement.APIDeleted"

    ApiManagementApiReleaseCreatedEventName = "Microsoft.ApiManagement.APIReleaseCreated"

    ApiManagementApiReleaseDeletedEventName = "Microsoft.ApiManagement.APIReleaseDeleted"

    ApiManagementApiReleaseUpdatedEventName = "Microsoft.ApiManagement.APIReleaseUpdated"

    ApiManagementApiUpdatedEventName = "Microsoft.ApiManagement.APIUpdated"

    ApiManagementCircuitBreakerClosedEventName = "Microsoft.ApiManagement.CircuitBreaker.Closed"

    ApiManagementCircuitBreakerOpenedEventName = "Microsoft.ApiManagement.CircuitBreaker.Opened"

    ApiManagementGatewayApiAddedEventName = "Microsoft.ApiManagement.GatewayAPIAdded"

    ApiManagementGatewayApiRemovedEventName = "Microsoft.ApiManagement.GatewayAPIRemoved"

    ApiManagementGatewayCertificateAuthorityCreatedEventName = (
        "Microsoft.ApiManagement.GatewayCertificateAuthorityCreated"
    )

    ApiManagementGatewayCertificateAuthorityDeletedEventName = (
        "Microsoft.ApiManagement.GatewayCertificateAuthorityDeleted"
    )

    ApiManagementGatewayCertificateAuthorityUpdatedEventName = (
        "Microsoft.ApiManagement.GatewayCertificateAuthorityUpdated"
    )

    ApiManagementGatewayCreatedEventName = "Microsoft.ApiManagement.GatewayCreated"

    ApiManagementGatewayDeletedEventName = "Microsoft.ApiManagement.GatewayDeleted"

    ApiManagementGatewayHostnameConfigurationCreatedEventName = (
        "Microsoft.ApiManagement.GatewayHostnameConfigurationCreated"
    )

    ApiManagementGatewayHostnameConfigurationDeletedEventName = (
        "Microsoft.ApiManagement.GatewayHostnameConfigurationDeleted"
    )

    ApiManagementGatewayHostnameConfigurationUpdatedEventName = (
        "Microsoft.ApiManagement.GatewayHostnameConfigurationUpdated"
    )

    ApiManagementGatewayTokenExpiredEventName = "Microsoft.ApiManagement.GatewayTokenExpired"

    ApiManagementGatewayTokenNearExpiryEventName = "Microsoft.ApiManagement.GatewayTokenNearExpiry"

    ApiManagementGatewayUpdatedEventName = "Microsoft.ApiManagement.GatewayUpdated"

    ApiManagementProductCreatedEventName = "Microsoft.ApiManagement.ProductCreated"

    ApiManagementProductDeletedEventName = "Microsoft.ApiManagement.ProductDeleted"

    ApiManagementProductUpdatedEventName = "Microsoft.ApiManagement.ProductUpdated"

    ApiManagementSubscriptionCreatedEventName = "Microsoft.ApiManagement.SubscriptionCreated"

    ApiManagementSubscriptionDeletedEventName = "Microsoft.ApiManagement.SubscriptionDeleted"

    ApiManagementSubscriptionUpdatedEventName = "Microsoft.ApiManagement.SubscriptionUpdated"

    ApiManagementUserCreatedEventName = "Microsoft.ApiManagement.UserCreated"

    ApiManagementUserDeletedEventName = "Microsoft.ApiManagement.UserDeleted"

    ApiManagementUserUpdatedEventName = "Microsoft.ApiManagement.UserUpdated"

    AppConfigurationKeyValueDeletedEventName = "Microsoft.AppConfiguration.KeyValueDeleted"

    AppConfigurationKeyValueModifiedEventName = "Microsoft.AppConfiguration.KeyValueModified"

    AppConfigurationSnapshotCreatedEventName = "Microsoft.AppConfiguration.SnapshotCreated"

    AppConfigurationSnapshotModifiedEventName = "Microsoft.AppConfiguration.SnapshotModified"

    AvsClusterCreatedEventName = "Microsoft.AVS.ClusterCreated"

    AvsClusterDeletedEventName = "Microsoft.AVS.ClusterDeleted"

    AvsClusterFailedEventName = "Microsoft.AVS.ClusterFailed"

    AvsClusterUpdatedEventName = "Microsoft.AVS.ClusterUpdated"

    AvsClusterUpdatingEventName = "Microsoft.AVS.ClusterUpdating"

    AvsPrivateCloudFailedEventName = "Microsoft.AVS.PrivateCloudFailed"

    AvsPrivateCloudUpdatedEventName = "Microsoft.AVS.PrivateCloudUpdated"

    AvsPrivateCloudUpdatingEventName = "Microsoft.AVS.PrivateCloudUpdating"

    AvsScriptExecutionCancelledEventName = "Microsoft.AVS.ScriptExecutionCancelled"

    AvsScriptExecutionFailedEventName = "Microsoft.AVS.ScriptExecutionFailed"

    AvsScriptExecutionFinishedEventName = "Microsoft.AVS.ScriptExecutionFinished"

    AvsScriptExecutionStartedEventName = "Microsoft.AVS.ScriptExecutionStarted"

    ContainerRegistryChartDeletedEventName = "Microsoft.ContainerRegistry.ChartDeleted"

    ContainerRegistryChartPushedEventName = "Microsoft.ContainerRegistry.ChartPushed"

    ContainerRegistryImageDeletedEventName = "Microsoft.ContainerRegistry.ImageDeleted"

    ContainerRegistryImagePushedEventName = "Microsoft.ContainerRegistry.ImagePushed"

    ContainerServiceClusterSupportEndedEventName = "Microsoft.ContainerService.ClusterSupportEnded"

    ContainerServiceClusterSupportEndingEventName = "Microsoft.ContainerService.ClusterSupportEnding"

    ContainerServiceNewKubernetesVersionAvailableEventName = "Microsoft.ContainerService.NewKubernetesVersionAvailable"

    ContainerServiceNodePoolRollingFailedEventName = "Microsoft.ContainerService.NodePoolRollingFailed"

    ContainerServiceNodePoolRollingStartedEventName = "Microsoft.ContainerService.NodePoolRollingStarted"

    ContainerServiceNodePoolRollingSucceededEventName = "Microsoft.ContainerService.NodePoolRollingSucceeded"

    DataBoxCopyCompletedEventName = "Microsoft.DataBox.CopyCompleted"

    DataBoxCopyStartedEventName = "Microsoft.DataBox.CopyStarted"

    DataBoxOrderCompletedEventName = "Microsoft.DataBox.OrderCompleted"

    EdgeSolutionVersionPublishedEventName = "Microsoft.Edge.SolutionVersionPublished"

    EventGridMQTTClientCreatedOrUpdatedEventName = "Microsoft.EventGrid.MQTTClientCreatedOrUpdated"

    EventGridMQTTClientDeletedEventName = "Microsoft.EventGrid.MQTTClientDeleted"

    EventGridMQTTClientSessionConnectedEventName = "Microsoft.EventGrid.MQTTClientSessionConnected"

    EventGridMQTTClientSessionDisconnectedEventName = "Microsoft.EventGrid.MQTTClientSessionDisconnected"

    EventHubCaptureFileCreatedEventName = "Microsoft.EventHub.CaptureFileCreated"

    HealthcareDicomImageCreatedEventName = "Microsoft.HealthcareApis.DicomImageCreated"

    HealthcareDicomImageDeletedEventName = "Microsoft.HealthcareApis.DicomImageDeleted"

    HealthcareDicomImageUpdatedEventName = "Microsoft.HealthcareApis.DicomImageUpdated"

    HealthcareFhirResourceCreatedEventName = "Microsoft.HealthcareApis.FhirResourceCreated"

    HealthcareFhirResourceDeletedEventName = "Microsoft.HealthcareApis.FhirResourceDeleted"

    HealthcareFhirResourceUpdatedEventName = "Microsoft.HealthcareApis.FhirResourceUpdated"

    IotHubDeviceConnectedEventName = "Microsoft.Devices.DeviceConnected"

    IotHubDeviceCreatedEventName = "Microsoft.Devices.DeviceCreated"

    IotHubDeviceDeletedEventName = "Microsoft.Devices.DeviceDeleted"

    IotHubDeviceDisconnectedEventName = "Microsoft.Devices.DeviceDisconnected"

    IotHubDeviceTelemetryEventName = "Microsoft.Devices.DeviceTelemetry"

    KeyVaultCertificateExpiredEventName = "Microsoft.KeyVault.CertificateExpired"

    KeyVaultCertificateNearExpiryEventName = "Microsoft.KeyVault.CertificateNearExpiry"

    KeyVaultCertificateNewVersionCreatedEventName = "Microsoft.KeyVault.CertificateNewVersionCreated"

    KeyVaultKeyExpiredEventName = "Microsoft.KeyVault.KeyExpired"

    KeyVaultKeyNearExpiryEventName = "Microsoft.KeyVault.KeyNearExpiry"

    KeyVaultKeyNewVersionCreatedEventName = "Microsoft.KeyVault.KeyNewVersionCreated"

    KeyVaultSecretExpiredEventName = "Microsoft.KeyVault.SecretExpired"

    KeyVaultSecretNearExpiryEventName = "Microsoft.KeyVault.SecretNearExpiry"

    KeyVaultSecretNewVersionCreatedEventName = "Microsoft.KeyVault.SecretNewVersionCreated"

    KeyVaultVaultAccessPolicyChangedEventName = "Microsoft.KeyVault.VaultAccessPolicyChanged"

    MachineLearningServicesDatasetDriftDetectedEventName = "Microsoft.MachineLearningServices.DatasetDriftDetected"

    MachineLearningServicesModelDeployedEventName = "Microsoft.MachineLearningServices.ModelDeployed"

    MachineLearningServicesModelRegisteredEventName = "Microsoft.MachineLearningServices.ModelRegistered"

    MachineLearningServicesRunCompletedEventName = "Microsoft.MachineLearningServices.RunCompleted"

    MachineLearningServicesRunStatusChangedEventName = "Microsoft.MachineLearningServices.RunStatusChanged"

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

    MediaLiveEventChannelArchiveHeartbeatEventName = "Microsoft.Media.LiveEventChannelArchiveHeartbeat"

    MediaLiveEventConnectionRejectedEventName = "Microsoft.Media.LiveEventConnectionRejected"

    MediaLiveEventEncoderConnectedEventName = "Microsoft.Media.LiveEventEncoderConnected"

    MediaLiveEventEncoderDisconnectedEventName = "Microsoft.Media.LiveEventEncoderDisconnected"

    MediaLiveEventIncomingDataChunkDroppedEventName = "Microsoft.Media.LiveEventIncomingDataChunkDropped"

    MediaLiveEventIncomingStreamReceivedEventName = "Microsoft.Media.LiveEventIncomingStreamReceived"

    MediaLiveEventIncomingStreamsOutOfSyncEventName = "Microsoft.Media.LiveEventIncomingStreamsOutOfSync"

    MediaLiveEventIncomingVideoStreamsOutOfSyncEventName = "Microsoft.Media.LiveEventIncomingVideoStreamsOutOfSync"

    MediaLiveEventIngestHeartbeatEventName = "Microsoft.Media.LiveEventIngestHeartbeat"

    MediaLiveEventTrackDiscontinuityDetectedEventName = "Microsoft.Media.LiveEventTrackDiscontinuityDetected"

    PolicyInsightsPolicyStateChangedEventName = "Microsoft.PolicyInsights.PolicyStateChanged"

    PolicyInsightsPolicyStateCreatedEventName = "Microsoft.PolicyInsights.PolicyStateCreated"

    PolicyInsightsPolicyStateDeletedEventName = "Microsoft.PolicyInsights.PolicyStateDeleted"

    RedisExportRDBCompletedEventName = "Microsoft.Cache.ExportRDBCompleted"

    RedisImportRDBCompletedEventName = "Microsoft.Cache.ImportRDBCompleted"

    RedisPatchingCompletedEventName = "Microsoft.Cache.PatchingCompleted"

    RedisScalingCompletedEventName = "Microsoft.Cache.ScalingCompleted"

    ResourceActionCancelName = "Microsoft.Resources.ResourceActionCancel"

    ResourceActionFailureName = "Microsoft.Resources.ResourceActionFailure"

    ResourceActionSuccessName = "Microsoft.Resources.ResourceActionSuccess"

    ResourceDeleteCancelName = "Microsoft.Resources.ResourceDeleteCancel"

    ResourceDeleteFailureName = "Microsoft.Resources.ResourceDeleteFailure"

    ResourceDeleteSuccessName = "Microsoft.Resources.ResourceDeleteSuccess"

    ResourceNotificationsContainerServiceEventResourcesScheduledEventName = (
        "Microsoft.ResourceNotifications.ContainerServiceEventResources.ScheduledEventEmitted"
    )

    ResourceNotificationsHealthResourcesAnnotatedEventName = (
        "Microsoft.ResourceNotifications.HealthResources.ResourceAnnotated"
    )

    ResourceNotificationsHealthResourcesAvailabilityStatusChangedEventName = (
        "Microsoft.ResourceNotifications.HealthResources.AvailabilityStatusChanged"
    )

    ResourceNotificationsResourceManagementCreatedOrUpdatedEventName = (
        "Microsoft.ResourceNotifications.Resources.CreatedOrUpdated"
    )

    ResourceNotificationsResourceManagementDeletedEventName = "Microsoft.ResourceNotifications.Resources.Deleted"

    ResourceWriteCancelName = "Microsoft.Resources.ResourceWriteCancel"

    ResourceWriteFailureName = "Microsoft.Resources.ResourceWriteFailure"

    ResourceWriteSuccessName = "Microsoft.Resources.ResourceWriteSuccess"

    ServiceBusActiveMessagesAvailablePeriodicNotificationsEventName = (
        "Microsoft.ServiceBus.ActiveMessagesAvailablePeriodicNotifications"
    )

    ServiceBusActiveMessagesAvailableWithNoListenersEventName = (
        "Microsoft.ServiceBus.ActiveMessagesAvailableWithNoListeners"
    )

    ServiceBusDeadletterMessagesAvailablePeriodicNotificationsEventName = (
        "Microsoft.ServiceBus.DeadletterMessagesAvailablePeriodicNotifications"
    )

    ServiceBusDeadletterMessagesAvailableWithNoListenersEventName = (
        "Microsoft.ServiceBus.DeadletterMessagesAvailableWithNoListeners"
    )

    SignalRServiceClientConnectionConnectedEventName = "Microsoft.SignalRService.ClientConnectionConnected"

    SignalRServiceClientConnectionDisconnectedEventName = "Microsoft.SignalRService.ClientConnectionDisconnected"

    StorageAsyncOperationInitiatedEventName = "Microsoft.Storage.AsyncOperationInitiated"

    StorageBlobCreatedEventName = "Microsoft.Storage.BlobCreated"

    StorageBlobDeletedEventName = "Microsoft.Storage.BlobDeleted"

    StorageBlobInventoryPolicyCompletedEventName = "Microsoft.Storage.BlobInventoryPolicyCompleted"

    StorageBlobRenamedEventName = "Microsoft.Storage.BlobRenamed"

    StorageBlobTierChangedEventName = "Microsoft.Storage.BlobTierChanged"

    StorageDirectoryCreatedEventName = "Microsoft.Storage.DirectoryCreated"

    StorageDirectoryDeletedEventName = "Microsoft.Storage.DirectoryDeleted"

    StorageDirectoryRenamedEventName = "Microsoft.Storage.DirectoryRenamed"

    StorageLifecyclePolicyCompletedEventName = "Microsoft.Storage.LifecyclePolicyCompleted"

    StorageTaskAssignmentCompletedEventName = "Microsoft.Storage.StorageTaskAssignmentCompleted"

    StorageTaskAssignmentQueuedEventName = "Microsoft.Storage.StorageTaskAssignmentQueued"

    StorageTaskCompletedEventName = "Microsoft.Storage.StorageTaskCompleted"

    StorageTaskQueuedEventName = "Microsoft.Storage.StorageTaskQueued"

    SubscriptionDeletedEventName = "Microsoft.EventGrid.SubscriptionDeletedEvent"

    SubscriptionValidationEventName = "Microsoft.EventGrid.SubscriptionValidationEvent"

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

    WebSlotSwapWithPreviewCancelledEventName = "Microsoft.Web.SlotSwapWithPreviewCancelled"

    WebSlotSwapWithPreviewStartedEventName = "Microsoft.Web.SlotSwapWithPreviewStarted"

    ContainerRegistryArtifactEventName = "Microsoft.AppConfiguration.KeyValueModified"

    KeyVaultAccessPolicyChangedEventName = "Microsoft.KeyVault.VaultAccessPolicyChanged"

    ContainerRegistryEventName = "Microsoft.ContainerRegistry.ChartPushed"

    ServiceBusDeadletterMessagesAvailableWithNoListenerEventName = (
        "Microsoft.ServiceBus.DeadletterMessagesAvailableWithNoListeners"
    )
