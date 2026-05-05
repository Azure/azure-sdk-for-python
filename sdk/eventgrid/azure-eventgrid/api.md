```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.eventgrid

    def azure.eventgrid.generate_sas(
            endpoint: str, 
            shared_access_key: str, 
            expiration_date_utc: datetime, 
            *, 
            api_version: str = constants.DEFAULT_API_VERSION
        ) -> str: ...


    class azure.eventgrid.EventGridConsumerClient(InternalEventGridConsumerClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                namespace_topic: str, 
                subscription: str, 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        @distributed_trace
        def acknowledge(
                self, 
                *, 
                lock_tokens: List[str], 
                **kwargs: Any
            ) -> AcknowledgeResult: ...

        def close(self) -> None: ...

        @distributed_trace
        def receive(
                self, 
                *, 
                max_events: Optional[int] = ..., 
                max_wait_time: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[ReceiveDetails]: ...

        @distributed_trace
        def reject(
                self, 
                *, 
                lock_tokens: List[str], 
                **kwargs: Any
            ) -> RejectResult: ...

        @api_version_validation(params_added_on={'2023-10-01-preview': ['release_delay']})
        def release(
                self, 
                *, 
                lock_tokens: List[str], 
                release_delay: Optional[Union[int, ReleaseDelay]] = ..., 
                **kwargs: Any
            ) -> ReleaseResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-10-01-preview', params_added_on={'2023-10-01-preview': ['api_version', 'content_type', 'accept']})
        def renew_locks(
                self, 
                *, 
                lock_tokens: List[str], 
                **kwargs: Any
            ) -> RenewLocksResult: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.eventgrid.EventGridEvent(InternalEventGridEvent):
        data: object
        data_version: str
        event_time: datetime
        event_type: str
        id: str
        metadata_version: str
        subject: str
        topic: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                subject: str, 
                event_type: str, 
                data: Any, 
                data_version: str, 
                *, 
                event_time: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                metadata_version: Optional[str] = ..., 
                topic: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def from_json(cls, event: Any) -> EventGridEvent: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.eventgrid.EventGridPublisherClient(InternalEventGridPublisherClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AzureSasCredential, TokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                namespace_topic: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def close(self) -> None: ...

        @distributed_trace
        def send(
                self, 
                events: Union[CloudEvent, List[CloudEvent], Dict[str, Any], List[Dict[str, Any]], CNCFCloudEvent, List[CNCFCloudEvent], EventGridEvent, List[EventGridEvent]], 
                *, 
                channel_name: Optional[str] = ..., 
                content_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.eventgrid.SystemEventNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AcsAdvancedMessageDeliveryStatusUpdatedEventName = "Microsoft.Communication.AdvancedMessageDeliveryStatusUpdated"
        AcsAdvancedMessageReceivedEventName = "Microsoft.Communication.AdvancedMessageReceived"
        AcsCallEndedEventName = "Microsoft.Communication.CallEnded"
        AcsCallParticipantAddedEventName = "Microsoft.Communication.CallParticipantAdded"
        AcsCallParticipantRemovedEventName = "Microsoft.Communication.CallParticipantRemoved"
        AcsCallStartedEventName = "Microsoft.Communication.CallStarted"
        AcsChatAzureBotCommandReceivedInThreadEventName = "Microsoft.Communication.ChatAzureBotCommandReceivedInThread"
        AcsChatMemberAddedToThreadWithUserEventName = "Microsoft.Communication.ChatMemberAddedToThreadWithUser"
        AcsChatMemberRemovedFromThreadWithUserEventName = "Microsoft.Communication.ChatMemberRemovedFromThreadWithUser"
        AcsChatMessageDeletedEventName = "Microsoft.Communication.ChatMessageDeleted"
        AcsChatMessageDeletedInThreadEventName = "Microsoft.Communication.ChatMessageDeletedInThread"
        AcsChatMessageEditedEventName = "Microsoft.Communication.ChatMessageEdited"
        AcsChatMessageEditedInThreadEventName = "Microsoft.Communication.ChatMessageEditedInThread"
        AcsChatMessageReceivedEventName = "Microsoft.Communication.ChatMessageReceived"
        AcsChatMessageReceivedInThreadEventName = "Microsoft.Communication.ChatMessageReceivedInThread"
        AcsChatParticipantAddedToThreadEventName = "Microsoft.Communication.ChatThreadParticipantAdded"
        AcsChatParticipantAddedToThreadWithUserEventName = "Microsoft.Communication.ChatParticipantAddedToThreadWithUser"
        AcsChatParticipantRemovedFromThreadEventName = "Microsoft.Communication.ChatThreadParticipantRemoved"
        AcsChatParticipantRemovedFromThreadWithUserEventName = "Microsoft.Communication.ChatParticipantRemovedFromThreadWithUser"
        AcsChatThreadCreatedEventName = "Microsoft.Communication.ChatThreadCreated"
        AcsChatThreadCreatedWithUserEventName = "Microsoft.Communication.ChatThreadCreatedWithUser"
        AcsChatThreadDeletedEventName = "Microsoft.Communication.ChatThreadDeleted"
        AcsChatThreadParticipantAddedEventName = "Microsoft.Communication.ChatThreadParticipantAdded"
        AcsChatThreadParticipantRemovedEventName = "Microsoft.Communication.ChatThreadParticipantRemoved"
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
        ApiManagementGatewayCertificateAuthorityCreatedEventName = "Microsoft.ApiManagement.GatewayCertificateAuthorityCreated"
        ApiManagementGatewayCertificateAuthorityDeletedEventName = "Microsoft.ApiManagement.GatewayCertificateAuthorityDeleted"
        ApiManagementGatewayCertificateAuthorityUpdatedEventName = "Microsoft.ApiManagement.GatewayCertificateAuthorityUpdated"
        ApiManagementGatewayCreatedEventName = "Microsoft.ApiManagement.GatewayCreated"
        ApiManagementGatewayDeletedEventName = "Microsoft.ApiManagement.GatewayDeleted"
        ApiManagementGatewayHostnameConfigurationCreatedEventName = "Microsoft.ApiManagement.GatewayHostnameConfigurationCreated"
        ApiManagementGatewayHostnameConfigurationDeletedEventName = "Microsoft.ApiManagement.GatewayHostnameConfigurationDeleted"
        ApiManagementGatewayHostnameConfigurationUpdatedEventName = "Microsoft.ApiManagement.GatewayHostnameConfigurationUpdated"
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
        ContainerRegistryArtifactEventName = "Microsoft.AppConfiguration.KeyValueModified"
        ContainerRegistryChartDeletedEventName = "Microsoft.ContainerRegistry.ChartDeleted"
        ContainerRegistryChartPushedEventName = "Microsoft.ContainerRegistry.ChartPushed"
        ContainerRegistryEventName = "Microsoft.ContainerRegistry.ChartPushed"
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
        EventGridSubscriptionDeletedEventName = "Microsoft.EventGrid.SubscriptionDeletedEvent"
        EventGridSubscriptionValidationEventName = "Microsoft.EventGrid.SubscriptionValidationEvent"
        EventHubCaptureFileCreatedEventName = "Microsoft.EventHub.CaptureFileCreated"
        HealthcareDicomImageCreatedEventName = "Microsoft.HealthcareApis.DicomImageCreated"
        HealthcareDicomImageDeletedEventName = "Microsoft.HealthcareApis.DicomImageDeleted"
        HealthcareDicomImageUpdatedEventName = "Microsoft.HealthcareApis.DicomImageUpdated"
        HealthcareFhirResourceCreatedEventName = "Microsoft.HealthcareApis.FhirResourceCreated"
        HealthcareFhirResourceDeletedEventName = "Microsoft.HealthcareApis.FhirResourceDeleted"
        HealthcareFhirResourceUpdatedEventName = "Microsoft.HealthcareApis.FhirResourceUpdated"
        IoTHubDeviceConnectedEventName = "Microsoft.Devices.DeviceConnected"
        IoTHubDeviceCreatedEventName = "Microsoft.Devices.DeviceCreated"
        IoTHubDeviceDeletedEventName = "Microsoft.Devices.DeviceDeleted"
        IoTHubDeviceDisconnectedEventName = "Microsoft.Devices.DeviceDisconnected"
        IotHubDeviceConnectedEventName = "Microsoft.Devices.DeviceConnected"
        IotHubDeviceCreatedEventName = "Microsoft.Devices.DeviceCreated"
        IotHubDeviceDeletedEventName = "Microsoft.Devices.DeviceDeleted"
        IotHubDeviceDisconnectedEventName = "Microsoft.Devices.DeviceDisconnected"
        IotHubDeviceTelemetryEventName = "Microsoft.Devices.DeviceTelemetry"
        KeyVaultAccessPolicyChangedEventName = "Microsoft.KeyVault.VaultAccessPolicyChanged"
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
        ResourceActionCancelEventName = "Microsoft.Resources.ResourceActionCancel"
        ResourceActionCancelName = "Microsoft.Resources.ResourceActionCancel"
        ResourceActionFailureEventName = "Microsoft.Resources.ResourceActionFailure"
        ResourceActionFailureName = "Microsoft.Resources.ResourceActionFailure"
        ResourceActionSuccessEventName = "Microsoft.Resources.ResourceActionSuccess"
        ResourceActionSuccessName = "Microsoft.Resources.ResourceActionSuccess"
        ResourceDeleteCancelEventName = "Microsoft.Resources.ResourceDeleteCancel"
        ResourceDeleteCancelName = "Microsoft.Resources.ResourceDeleteCancel"
        ResourceDeleteFailureEventName = "Microsoft.Resources.ResourceDeleteFailure"
        ResourceDeleteFailureName = "Microsoft.Resources.ResourceDeleteFailure"
        ResourceDeleteSuccessEventName = "Microsoft.Resources.ResourceDeleteSuccess"
        ResourceDeleteSuccessName = "Microsoft.Resources.ResourceDeleteSuccess"
        ResourceNotificationsContainerServiceEventResourcesScheduledEventName = "Microsoft.ResourceNotifications.ContainerServiceEventResources.ScheduledEventEmitted"
        ResourceNotificationsHealthResourcesAnnotatedEventName = "Microsoft.ResourceNotifications.HealthResources.ResourceAnnotated"
        ResourceNotificationsHealthResourcesAvailabilityStatusChangedEventName = "Microsoft.ResourceNotifications.HealthResources.AvailabilityStatusChanged"
        ResourceNotificationsResourceManagementCreatedOrUpdatedEventName = "Microsoft.ResourceNotifications.Resources.CreatedOrUpdated"
        ResourceNotificationsResourceManagementDeletedEventName = "Microsoft.ResourceNotifications.Resources.Deleted"
        ResourceWriteCancelEventName = "Microsoft.Resources.ResourceWriteCancel"
        ResourceWriteCancelName = "Microsoft.Resources.ResourceWriteCancel"
        ResourceWriteFailureEventName = "Microsoft.Resources.ResourceWriteFailure"
        ResourceWriteFailureName = "Microsoft.Resources.ResourceWriteFailure"
        ResourceWriteSuccessEventName = "Microsoft.Resources.ResourceWriteSuccess"
        ResourceWriteSuccessName = "Microsoft.Resources.ResourceWriteSuccess"
        ServiceBusActiveMessagesAvailablePeriodicNotificationsEventName = "Microsoft.ServiceBus.ActiveMessagesAvailablePeriodicNotifications"
        ServiceBusActiveMessagesAvailableWithNoListenersEventName = "Microsoft.ServiceBus.ActiveMessagesAvailableWithNoListeners"
        ServiceBusDeadletterMessagesAvailablePeriodicNotificationsEventName = "Microsoft.ServiceBus.DeadletterMessagesAvailablePeriodicNotifications"
        ServiceBusDeadletterMessagesAvailableWithNoListenerEventName = "Microsoft.ServiceBus.DeadletterMessagesAvailableWithNoListeners"
        ServiceBusDeadletterMessagesAvailableWithNoListenersEventName = "Microsoft.ServiceBus.DeadletterMessagesAvailableWithNoListeners"
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


namespace azure.eventgrid.aio

    class azure.eventgrid.aio.EventGridConsumerClient(InternalEventGridConsumerClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                namespace_topic: str, 
                subscription: str, 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        @distributed_trace_async
        async def acknowledge(
                self, 
                *, 
                lock_tokens: List[str], 
                **kwargs: Any
            ) -> AcknowledgeResult: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def receive(
                self, 
                *, 
                max_events: Optional[int] = ..., 
                max_wait_time: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[ReceiveDetails]: ...

        @distributed_trace_async
        async def reject(
                self, 
                *, 
                lock_tokens: List[str], 
                **kwargs: Any
            ) -> RejectResult: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'2023-10-01-preview': ['release_delay']})
        async def release(
                self, 
                *, 
                lock_tokens: List[str], 
                release_delay: Optional[Union[int, ReleaseDelay]] = ..., 
                **kwargs: Any
            ) -> ReleaseResult: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2023-10-01-preview', params_added_on={'2023-10-01-preview': ['api_version', 'content_type', 'accept']})
        async def renew_locks(
                self, 
                *, 
                lock_tokens: List[str], 
                **kwargs: Any
            ) -> RenewLocksResult: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.eventgrid.aio.EventGridPublisherClient(InternalEventGridPublisherClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AzureSasCredential, AsyncTokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                namespace_topic: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def send(
                self, 
                events: Union[CloudEvent, List[CloudEvent], Dict[str, Any], List[Dict[str, Any]], CNCFCloudEvent, List[CNCFCloudEvent], EventGridEvent, List[EventGridEvent]], 
                *, 
                channel_name: Optional[str] = ..., 
                content_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.eventgrid.models

    class azure.eventgrid.models.AcknowledgeResult(Model):
        failed_lock_tokens: List[FailedLockToken]
        succeeded_lock_tokens: List[str]

        @overload
        def __init__(
                self, 
                *, 
                failed_lock_tokens: List[FailedLockToken], 
                succeeded_lock_tokens: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.eventgrid.models.BrokerProperties(InternalBrokerProperties):
        delivery_count: int
        lock_token: str

        @overload
        def __init__(
                self, 
                *, 
                delivery_count: int, 
                lock_token: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.eventgrid.models.FailedLockToken(Model):
        error: ODataV4Format
        lock_token: str

        @overload
        def __init__(
                self, 
                *, 
                error: ODataV4Format, 
                lock_token: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.eventgrid.models.ReceiveDetails(InternalReceiveDetails, Generic[DataType]):
        broker_properties: BrokerProperties
        event: CloudEvent

        @overload
        def __init__(
                self, 
                *, 
                broker_properties: BrokerProperties, 
                event: CloudEvent[DataType]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.eventgrid.models.RejectResult(Model):
        failed_lock_tokens: List[FailedLockToken]
        succeeded_lock_tokens: List[str]

        @overload
        def __init__(
                self, 
                *, 
                failed_lock_tokens: List[FailedLockToken], 
                succeeded_lock_tokens: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.eventgrid.models.ReleaseDelay(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_DELAY = "0"
        ONE_HOUR = "3600"
        ONE_MINUTE = "60"
        TEN_MINUTES = "600"
        TEN_SECONDS = "10"


    class azure.eventgrid.models.ReleaseResult(Model):
        failed_lock_tokens: List[FailedLockToken]
        succeeded_lock_tokens: List[str]

        @overload
        def __init__(
                self, 
                *, 
                failed_lock_tokens: List[FailedLockToken], 
                succeeded_lock_tokens: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.eventgrid.models.RenewLocksResult(Model):
        failed_lock_tokens: List[FailedLockToken]
        succeeded_lock_tokens: List[str]

        @overload
        def __init__(
                self, 
                *, 
                failed_lock_tokens: List[FailedLockToken], 
                succeeded_lock_tokens: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```