```py
namespace azure.mgmt.databox

    class azure.mgmt.databox.DataBoxManagementClient(_DataBoxManagementClientOperationsMixin): implements ContextManager 
        jobs: JobsOperations
        operations: Operations
        service: ServiceOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def mitigate(
                self, 
                job_name: str, 
                resource_group_name: str, 
                mitigate_job_request: MitigateJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def mitigate(
                self, 
                job_name: str, 
                resource_group_name: str, 
                mitigate_job_request: MitigateJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def mitigate(
                self, 
                job_name: str, 
                resource_group_name: str, 
                mitigate_job_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.databox.aio

    class azure.mgmt.databox.aio.DataBoxManagementClient(_DataBoxManagementClientOperationsMixin): implements AsyncContextManager 
        jobs: JobsOperations
        operations: Operations
        service: ServiceOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def mitigate(
                self, 
                job_name: str, 
                resource_group_name: str, 
                mitigate_job_request: MitigateJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def mitigate(
                self, 
                job_name: str, 
                resource_group_name: str, 
                mitigate_job_request: MitigateJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def mitigate(
                self, 
                job_name: str, 
                resource_group_name: str, 
                mitigate_job_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.databox.aio.operations

    class azure.mgmt.databox.aio.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource: JobResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JobResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource: JobResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JobResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JobResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource_update_parameter: JobResourceUpdateParameter, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[JobResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource_update_parameter: JobResourceUpdateParameter, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[JobResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource_update_parameter: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[JobResource]: ...

        @overload
        async def book_shipment_pick_up(
                self, 
                resource_group_name: str, 
                job_name: str, 
                shipment_pick_up_request: ShipmentPickUpRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShipmentPickUpResponse: ...

        @overload
        async def book_shipment_pick_up(
                self, 
                resource_group_name: str, 
                job_name: str, 
                shipment_pick_up_request: ShipmentPickUpRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShipmentPickUpResponse: ...

        @overload
        async def book_shipment_pick_up(
                self, 
                resource_group_name: str, 
                job_name: str, 
                shipment_pick_up_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShipmentPickUpResponse: ...

        @overload
        async def cancel(
                self, 
                resource_group_name: str, 
                job_name: str, 
                cancellation_reason: CancellationReason, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def cancel(
                self, 
                resource_group_name: str, 
                job_name: str, 
                cancellation_reason: CancellationReason, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def cancel(
                self, 
                resource_group_name: str, 
                job_name: str, 
                cancellation_reason: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                job_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> JobResource: ...

        @distributed_trace
        def list(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JobResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JobResource]: ...

        @distributed_trace
        def list_credentials(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[UnencryptedCredentials]: ...

        @overload
        async def mark_devices_shipped(
                self, 
                job_name: str, 
                resource_group_name: str, 
                mark_devices_shipped_request: MarkDevicesShippedRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def mark_devices_shipped(
                self, 
                job_name: str, 
                resource_group_name: str, 
                mark_devices_shipped_request: MarkDevicesShippedRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def mark_devices_shipped(
                self, 
                job_name: str, 
                resource_group_name: str, 
                mark_devices_shipped_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.databox.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.databox.aio.operations.ServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list_available_skus_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                available_sku_request: AvailableSkuRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[SkuInformation]: ...

        @overload
        def list_available_skus_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                available_sku_request: AvailableSkuRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[SkuInformation]: ...

        @overload
        def list_available_skus_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                available_sku_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[SkuInformation]: ...

        @overload
        async def region_configuration(
                self, 
                location: str, 
                region_configuration_request: RegionConfigurationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegionConfigurationResponse: ...

        @overload
        async def region_configuration(
                self, 
                location: str, 
                region_configuration_request: RegionConfigurationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegionConfigurationResponse: ...

        @overload
        async def region_configuration(
                self, 
                location: str, 
                region_configuration_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegionConfigurationResponse: ...

        @overload
        async def region_configuration_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                region_configuration_request: RegionConfigurationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegionConfigurationResponse: ...

        @overload
        async def region_configuration_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                region_configuration_request: RegionConfigurationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegionConfigurationResponse: ...

        @overload
        async def region_configuration_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                region_configuration_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegionConfigurationResponse: ...

        @overload
        async def validate_address(
                self, 
                location: str, 
                validate_address: ValidateAddress, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddressValidationOutput: ...

        @overload
        async def validate_address(
                self, 
                location: str, 
                validate_address: ValidateAddress, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddressValidationOutput: ...

        @overload
        async def validate_address(
                self, 
                location: str, 
                validate_address: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddressValidationOutput: ...

        @overload
        async def validate_inputs(
                self, 
                location: str, 
                validation_request: ValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        async def validate_inputs(
                self, 
                location: str, 
                validation_request: ValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        async def validate_inputs(
                self, 
                location: str, 
                validation_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        async def validate_inputs_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                validation_request: ValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        async def validate_inputs_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                validation_request: ValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        async def validate_inputs_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                validation_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...


namespace azure.mgmt.databox.models

    class azure.mgmt.databox.models.AccessProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NFS = "NFS"
        SMB = "SMB"


    class azure.mgmt.databox.models.AccountCredentialDetails(_Model):
        account_connection_string: Optional[str]
        account_name: Optional[str]
        data_account_type: Optional[Union[str, DataAccountType]]
        share_credential_details: Optional[list[ShareCredentialDetails]]


    class azure.mgmt.databox.models.AdditionalErrorInfo(_Model):
        info: Optional[dict[str, Any]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                info: Optional[dict[str, Any]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.AddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMERCIAL = "Commercial"
        NONE = "None"
        RESIDENTIAL = "Residential"


    class azure.mgmt.databox.models.AddressValidationOutput(_Model):
        properties: Optional[AddressValidationProperties]


    class azure.mgmt.databox.models.AddressValidationProperties(ValidationInputResponse, discriminator='ValidateAddress'):
        alternate_addresses: Optional[list[ShippingAddress]]
        error: CloudError
        validation_status: Optional[Union[str, AddressValidationStatus]]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_ADDRESS]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.AddressValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMBIGUOUS = "Ambiguous"
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.databox.models.ApiError(_Model):
        error: ErrorDetail

        @overload
        def __init__(
                self, 
                *, 
                error: ErrorDetail
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ApplianceNetworkConfiguration(_Model):
        mac_address: Optional[str]
        name: Optional[str]


    class azure.mgmt.databox.models.AvailableSkuRequest(_Model):
        country: str
        location: str
        sku_names: Optional[list[Union[str, SkuName]]]
        transfer_type: Union[str, TransferType]

        @overload
        def __init__(
                self, 
                *, 
                country: str, 
                location: str, 
                sku_names: Optional[list[Union[str, SkuName]]] = ..., 
                transfer_type: Union[str, TransferType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.AzureFileFilterDetails(_Model):
        file_path_list: Optional[list[str]]
        file_prefix_list: Optional[list[str]]
        file_share_list: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                file_path_list: Optional[list[str]] = ..., 
                file_prefix_list: Optional[list[str]] = ..., 
                file_share_list: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.BlobFilterDetails(_Model):
        blob_path_list: Optional[list[str]]
        blob_prefix_list: Optional[list[str]]
        container_list: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                blob_path_list: Optional[list[str]] = ..., 
                blob_prefix_list: Optional[list[str]] = ..., 
                container_list: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.CancellationReason(_Model):
        reason: str

        @overload
        def __init__(
                self, 
                *, 
                reason: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ClassDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_BOX = "DataBox"
        DATA_BOX_CUSTOMER_DISK = "DataBoxCustomerDisk"
        DATA_BOX_DISK = "DataBoxDisk"
        DATA_BOX_HEAVY = "DataBoxHeavy"


    class azure.mgmt.databox.models.CloudError(_Model):
        additional_info: Optional[list[AdditionalErrorInfo]]
        code: Optional[str]
        details: Optional[list[CloudError]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ContactDetails(_Model):
        contact_name: str
        email_list: list[str]
        mobile: Optional[str]
        notification_preference: Optional[list[NotificationPreference]]
        phone: str
        phone_extension: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                contact_name: str, 
                email_list: list[str], 
                mobile: Optional[str] = ..., 
                notification_preference: Optional[list[NotificationPreference]] = ..., 
                phone: str, 
                phone_extension: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ContactInfo(_Model):
        contact_name: str
        mobile: Optional[str]
        phone: str
        phone_extension: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                contact_name: str, 
                mobile: Optional[str] = ..., 
                phone: str, 
                phone_extension: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.CopyLogDetails(_Model):
        copy_log_details_type: str

        @overload
        def __init__(
                self, 
                *, 
                copy_log_details_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.CopyProgress(_Model):
        account_id: Optional[str]
        actions: Optional[list[Union[str, CustomerResolutionCode]]]
        bytes_processed: Optional[int]
        data_account_type: Optional[Union[str, DataAccountType]]
        directories_errored_out: Optional[int]
        error: Optional[CloudError]
        files_errored_out: Optional[int]
        files_processed: Optional[int]
        invalid_directories_processed: Optional[int]
        invalid_file_bytes_uploaded: Optional[int]
        invalid_files_processed: Optional[int]
        is_enumeration_in_progress: Optional[bool]
        renamed_container_count: Optional[int]
        storage_account_name: Optional[str]
        total_bytes_to_process: Optional[int]
        total_files_to_process: Optional[int]
        transfer_type: Optional[Union[str, TransferType]]


    class azure.mgmt.databox.models.CopyStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        COMPLETED_WITH_ERRORS = "CompletedWithErrors"
        DEVICE_FORMATTED = "DeviceFormatted"
        DEVICE_METADATA_MODIFIED = "DeviceMetadataModified"
        DRIVE_CORRUPTED = "DriveCorrupted"
        DRIVE_NOT_DETECTED = "DriveNotDetected"
        DRIVE_NOT_RECEIVED = "DriveNotReceived"
        FAILED = "Failed"
        HARDWARE_ERROR = "HardwareError"
        IN_PROGRESS = "InProgress"
        METADATA_FILES_MODIFIED_OR_REMOVED = "MetadataFilesModifiedOrRemoved"
        NOT_RETURNED = "NotReturned"
        NOT_STARTED = "NotStarted"
        OTHER_SERVICE_ERROR = "OtherServiceError"
        OTHER_USER_ERROR = "OtherUserError"
        STORAGE_ACCOUNT_NOT_ACCESSIBLE = "StorageAccountNotAccessible"
        UNSUPPORTED_DATA = "UnsupportedData"
        UNSUPPORTED_DRIVE = "UnsupportedDrive"


    class azure.mgmt.databox.models.CreateJobValidations(ValidationRequest, discriminator='JobCreationValidation'):
        individual_request_details: list[ValidationInputRequest]
        validation_category: str

        @overload
        def __init__(
                self, 
                *, 
                individual_request_details: list[ValidationInputRequest]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.CreateOrderLimitForSubscriptionValidationRequest(ValidationInputRequest, discriminator='ValidateCreateOrderLimit'):
        device_type: Union[str, SkuName]
        model: Optional[Union[str, ModelName]]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_CREATE_ORDER_LIMIT]

        @overload
        def __init__(
                self, 
                *, 
                device_type: Union[str, SkuName], 
                model: Optional[Union[str, ModelName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.CreateOrderLimitForSubscriptionValidationResponseProperties(ValidationInputResponse, discriminator='ValidateCreateOrderLimit'):
        error: CloudError
        status: Optional[Union[str, ValidationStatus]]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_CREATE_ORDER_LIMIT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.databox.models.CustomerDiskJobSecrets(JobSecrets, discriminator='DataBoxCustomerDisk'):
        carrier_account_number: Optional[str]
        dc_access_security_code: DcAccessSecurityCode
        disk_secrets: Optional[list[DiskSecret]]
        error: CloudError
        job_secrets_type: Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.CustomerResolutionCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MOVE_TO_CLEAN_UP_DEVICE = "MoveToCleanUpDevice"
        NONE = "None"
        REACH_OUT_TO_OPERATION = "ReachOutToOperation"
        RESTART = "Restart"
        RESUME = "Resume"


    class azure.mgmt.databox.models.DataAccountDetails(_Model):
        data_account_type: str
        share_password: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_account_type: str, 
                share_password: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_DISK = "ManagedDisk"
        STORAGE_ACCOUNT = "StorageAccount"


    class azure.mgmt.databox.models.DataBoxAccountCopyLogDetails(CopyLogDetails, discriminator='DataBox'):
        account_name: Optional[str]
        copy_log_details_type: Literal[ClassDiscriminator.DATA_BOX]
        copy_log_link: Optional[str]
        copy_verbose_log_link: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataBoxCustomerDiskCopyLogDetails(CopyLogDetails, discriminator='DataBoxCustomerDisk'):
        copy_log_details_type: Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]
        error_log_link: Optional[str]
        serial_number: Optional[str]
        verbose_log_link: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataBoxCustomerDiskCopyProgress(CopyProgress):
        account_id: str
        actions: Union[list[str, CustomerResolutionCode]]
        bytes_processed: int
        copy_status: Optional[Union[str, CopyStatus]]
        data_account_type: Union[str, DataAccountType]
        directories_errored_out: int
        error: CloudError
        files_errored_out: int
        files_processed: int
        invalid_directories_processed: int
        invalid_file_bytes_uploaded: int
        invalid_files_processed: int
        is_enumeration_in_progress: bool
        renamed_container_count: int
        serial_number: Optional[str]
        storage_account_name: str
        total_bytes_to_process: int
        total_files_to_process: int
        transfer_type: Union[str, TransferType]


    class azure.mgmt.databox.models.DataBoxCustomerDiskJobDetails(JobDetails, discriminator='DataBoxCustomerDisk'):
        actions: Union[list[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copy_log_details: list[CopyLogDetails]
        copy_progress: Optional[list[DataBoxCustomerDiskCopyProgress]]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        deliver_to_dc_package_details: Optional[PackageCarrierInfo]
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        enable_manifest_backup: Optional[bool]
        expected_data_size_in_tera_bytes: int
        export_disk_details_collection: Optional[dict[str, ExportDiskDetails]]
        import_disk_details_collection: Optional[dict[str, ImportDiskDetails]]
        job_details_type: Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        preferences: Preferences
        return_package: PackageShippingDetails
        return_to_customer_package_details: PackageCarrierDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress

        @overload
        def __init__(
                self, 
                *, 
                contact_details: ContactDetails, 
                data_export_details: Optional[list[DataExportDetails]] = ..., 
                data_import_details: Optional[list[DataImportDetails]] = ..., 
                enable_manifest_backup: Optional[bool] = ..., 
                expected_data_size_in_tera_bytes: Optional[int] = ..., 
                import_disk_details_collection: Optional[dict[str, ImportDiskDetails]] = ..., 
                key_encryption_key: Optional[KeyEncryptionKey] = ..., 
                preferences: Optional[Preferences] = ..., 
                return_to_customer_package_details: PackageCarrierDetails, 
                reverse_shipping_details: Optional[ReverseShippingDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataBoxDiskCopyLogDetails(CopyLogDetails, discriminator='DataBoxDisk'):
        copy_log_details_type: Literal[ClassDiscriminator.DATA_BOX_DISK]
        disk_serial_number: Optional[str]
        error_log_link: Optional[str]
        verbose_log_link: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataBoxDiskCopyProgress(_Model):
        actions: Optional[list[Union[str, CustomerResolutionCode]]]
        bytes_copied: Optional[int]
        error: Optional[CloudError]
        percent_complete: Optional[int]
        serial_number: Optional[str]
        status: Optional[Union[str, CopyStatus]]


    class azure.mgmt.databox.models.DataBoxDiskGranularCopyLogDetails(GranularCopyLogDetails, discriminator='DataBoxCustomerDisk'):
        account_id: Optional[str]
        copy_log_details_type: Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]
        error_log_link: Optional[str]
        serial_number: Optional[str]
        verbose_log_link: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataBoxDiskGranularCopyProgress(GranularCopyProgress):
        account_id: str
        actions: Union[list[str, CustomerResolutionCode]]
        bytes_processed: int
        copy_status: Optional[Union[str, CopyStatus]]
        data_account_type: Union[str, DataAccountType]
        directories_errored_out: int
        error: CloudError
        files_errored_out: int
        files_processed: int
        invalid_directories_processed: int
        invalid_file_bytes_uploaded: int
        invalid_files_processed: int
        is_enumeration_in_progress: bool
        renamed_container_count: int
        serial_number: Optional[str]
        storage_account_name: str
        total_bytes_to_process: int
        total_files_to_process: int
        transfer_type: Union[str, TransferType]


    class azure.mgmt.databox.models.DataBoxDiskJobDetails(JobDetails, discriminator='DataBoxDisk'):
        actions: Union[list[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copy_log_details: list[CopyLogDetails]
        copy_progress: Optional[list[DataBoxDiskCopyProgress]]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        disks_and_size_details: Optional[dict[str, int]]
        expected_data_size_in_tera_bytes: int
        granular_copy_log_details: Optional[list[DataBoxDiskGranularCopyLogDetails]]
        granular_copy_progress: Optional[list[DataBoxDiskGranularCopyProgress]]
        job_details_type: Literal[ClassDiscriminator.DATA_BOX_DISK]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        passkey: Optional[str]
        preferences: Preferences
        preferred_disks: Optional[dict[str, int]]
        return_package: PackageShippingDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress

        @overload
        def __init__(
                self, 
                *, 
                contact_details: ContactDetails, 
                data_export_details: Optional[list[DataExportDetails]] = ..., 
                data_import_details: Optional[list[DataImportDetails]] = ..., 
                expected_data_size_in_tera_bytes: Optional[int] = ..., 
                key_encryption_key: Optional[KeyEncryptionKey] = ..., 
                passkey: Optional[str] = ..., 
                preferences: Optional[Preferences] = ..., 
                preferred_disks: Optional[dict[str, int]] = ..., 
                reverse_shipping_details: Optional[ReverseShippingDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataBoxDiskJobSecrets(JobSecrets, discriminator='DataBoxDisk'):
        dc_access_security_code: DcAccessSecurityCode
        disk_secrets: Optional[list[DiskSecret]]
        error: CloudError
        is_passkey_user_defined: Optional[bool]
        job_secrets_type: Literal[ClassDiscriminator.DATA_BOX_DISK]
        pass_key: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataBoxHeavyAccountCopyLogDetails(CopyLogDetails, discriminator='DataBoxHeavy'):
        account_name: Optional[str]
        copy_log_details_type: Literal[ClassDiscriminator.DATA_BOX_HEAVY]
        copy_log_link: Optional[list[str]]
        copy_verbose_log_link: Optional[list[str]]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataBoxHeavyJobDetails(JobDetails, discriminator='DataBoxHeavy'):
        actions: Union[list[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copy_log_details: list[CopyLogDetails]
        copy_progress: Optional[list[CopyProgress]]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        device_password: Optional[str]
        expected_data_size_in_tera_bytes: int
        job_details_type: Literal[ClassDiscriminator.DATA_BOX_HEAVY]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        preferences: Preferences
        return_package: PackageShippingDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress

        @overload
        def __init__(
                self, 
                *, 
                contact_details: ContactDetails, 
                data_export_details: Optional[list[DataExportDetails]] = ..., 
                data_import_details: Optional[list[DataImportDetails]] = ..., 
                device_password: Optional[str] = ..., 
                expected_data_size_in_tera_bytes: Optional[int] = ..., 
                key_encryption_key: Optional[KeyEncryptionKey] = ..., 
                preferences: Optional[Preferences] = ..., 
                reverse_shipping_details: Optional[ReverseShippingDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataBoxHeavyJobSecrets(JobSecrets, discriminator='DataBoxHeavy'):
        cabinet_pod_secrets: Optional[list[DataBoxHeavySecret]]
        dc_access_security_code: DcAccessSecurityCode
        error: CloudError
        job_secrets_type: Literal[ClassDiscriminator.DATA_BOX_HEAVY]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataBoxHeavySecret(_Model):
        account_credential_details: Optional[list[AccountCredentialDetails]]
        device_password: Optional[str]
        device_serial_number: Optional[str]
        encoded_validation_cert_pub_key: Optional[str]
        network_configurations: Optional[list[ApplianceNetworkConfiguration]]


    class azure.mgmt.databox.models.DataBoxJobDetails(JobDetails, discriminator='DataBox'):
        actions: Union[list[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copy_log_details: list[CopyLogDetails]
        copy_progress: Optional[list[CopyProgress]]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        device_password: Optional[str]
        expected_data_size_in_tera_bytes: int
        job_details_type: Literal[ClassDiscriminator.DATA_BOX]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        preferences: Preferences
        return_package: PackageShippingDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress

        @overload
        def __init__(
                self, 
                *, 
                contact_details: ContactDetails, 
                data_export_details: Optional[list[DataExportDetails]] = ..., 
                data_import_details: Optional[list[DataImportDetails]] = ..., 
                device_password: Optional[str] = ..., 
                expected_data_size_in_tera_bytes: Optional[int] = ..., 
                key_encryption_key: Optional[KeyEncryptionKey] = ..., 
                preferences: Optional[Preferences] = ..., 
                reverse_shipping_details: Optional[ReverseShippingDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataBoxScheduleAvailabilityRequest(ScheduleAvailabilityRequest, discriminator='DataBox'):
        country: str
        model: Union[str, ModelName]
        sku_name: Literal[SkuName.DATA_BOX]
        storage_location: str

        @overload
        def __init__(
                self, 
                *, 
                country: Optional[str] = ..., 
                model: Optional[Union[str, ModelName]] = ..., 
                storage_location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataBoxSecret(_Model):
        account_credential_details: Optional[list[AccountCredentialDetails]]
        device_password: Optional[str]
        device_serial_number: Optional[str]
        encoded_validation_cert_pub_key: Optional[str]
        network_configurations: Optional[list[ApplianceNetworkConfiguration]]


    class azure.mgmt.databox.models.DataCenterCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AD_HOC = "AdHoc"
        AM2 = "AM2"
        AMS06 = "AMS06"
        AMS20 = "AMS20"
        AMS25 = "AMS25"
        AUH20 = "AUH20"
        BJB = "BJB"
        BJS20 = "BJS20"
        BL20 = "BL20"
        BL24 = "BL24"
        BL7 = "BL7"
        BN1 = "BN1"
        BN7 = "BN7"
        BOM01 = "BOM01"
        BY1 = "BY1"
        BY2 = "BY2"
        BY21 = "BY21"
        BY24 = "BY24"
        CBR20 = "CBR20"
        CH1 = "CH1"
        CPQ02 = "CPQ02"
        CPQ20 = "CPQ20"
        CPQ21 = "CPQ21"
        CWL20 = "CWL20"
        CYS04 = "CYS04"
        DSM05 = "DSM05"
        DSM11 = "DSM11"
        DUB07 = "DUB07"
        DXB23 = "DXB23"
        FRA22 = "FRA22"
        HKG20 = "HKG20"
        IDC5 = "IDC5"
        INVALID = "Invalid"
        JNB21 = "JNB21"
        JNB22 = "JNB22"
        LON24 = "LON24"
        MAA01 = "MAA01"
        MEL23 = "MEL23"
        MNZ21 = "MNZ21"
        MWH01 = "MWH01"
        NTG20 = "NTG20"
        ORK70 = "ORK70"
        OSA02 = "OSA02"
        OSA20 = "OSA20"
        OSA22 = "OSA22"
        OSA23 = "OSA23"
        PAR22 = "PAR22"
        PNQ01 = "PNQ01"
        PUS20 = "PUS20"
        SEL20 = "SEL20"
        SEL21 = "SEL21"
        SG2 = "SG2"
        SHA03 = "SHA03"
        SIN20 = "SIN20"
        SN5 = "SN5"
        SN6 = "SN6"
        SN8 = "SN8"
        SSE90 = "SSE90"
        SVG20 = "SVG20"
        SYD03 = "SYD03"
        SYD23 = "SYD23"
        TYO01 = "TYO01"
        TYO22 = "TYO22"
        TYO23 = "TYO23"
        YQB20 = "YQB20"
        YTO20 = "YTO20"
        YTO21 = "YTO21"
        ZRH20 = "ZRH20"


    class azure.mgmt.databox.models.DataExportDetails(_Model):
        account_details: DataAccountDetails
        log_collection_level: Optional[Union[str, LogCollectionLevel]]
        transfer_configuration: TransferConfiguration

        @overload
        def __init__(
                self, 
                *, 
                account_details: DataAccountDetails, 
                log_collection_level: Optional[Union[str, LogCollectionLevel]] = ..., 
                transfer_configuration: TransferConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataImportDetails(_Model):
        account_details: DataAccountDetails
        log_collection_level: Optional[Union[str, LogCollectionLevel]]

        @overload
        def __init__(
                self, 
                *, 
                account_details: DataAccountDetails, 
                log_collection_level: Optional[Union[str, LogCollectionLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataLocationToServiceLocationMap(_Model):
        data_location: Optional[str]
        service_location: Optional[str]


    class azure.mgmt.databox.models.DataTransferDetailsValidationRequest(ValidationInputRequest, discriminator='ValidateDataTransferDetails'):
        data_export_details: Optional[list[DataExportDetails]]
        data_import_details: Optional[list[DataImportDetails]]
        device_type: Union[str, SkuName]
        model: Optional[Union[str, ModelName]]
        transfer_type: Union[str, TransferType]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_DATA_TRANSFER_DETAILS]

        @overload
        def __init__(
                self, 
                *, 
                data_export_details: Optional[list[DataExportDetails]] = ..., 
                data_import_details: Optional[list[DataImportDetails]] = ..., 
                device_type: Union[str, SkuName], 
                model: Optional[Union[str, ModelName]] = ..., 
                transfer_type: Union[str, TransferType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataTransferDetailsValidationResponseProperties(ValidationInputResponse, discriminator='ValidateDataTransferDetails'):
        error: CloudError
        status: Optional[Union[str, ValidationStatus]]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_DATA_TRANSFER_DETAILS]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DataboxJobSecrets(JobSecrets, discriminator='DataBox'):
        dc_access_security_code: DcAccessSecurityCode
        error: CloudError
        job_secrets_type: Literal[ClassDiscriminator.DATA_BOX]
        pod_secrets: Optional[list[DataBoxSecret]]

        @overload
        def __init__(
                self, 
                *, 
                pod_secrets: Optional[list[DataBoxSecret]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DatacenterAddressInstructionResponse(DatacenterAddressResponse, discriminator='DatacenterAddressInstruction'):
        communication_instruction: Optional[str]
        data_center_azure_location: str
        datacenter_address_type: Literal[DatacenterAddressType.DATACENTER_ADDRESS_INSTRUCTION]
        supported_carriers_for_return_shipment: list[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DatacenterAddressLocationResponse(DatacenterAddressResponse, discriminator='DatacenterAddressLocation'):
        additional_shipping_information: Optional[str]
        address_type: Optional[str]
        city: Optional[str]
        company: Optional[str]
        contact_person_name: Optional[str]
        country: Optional[str]
        data_center_azure_location: str
        datacenter_address_type: Literal[DatacenterAddressType.DATACENTER_ADDRESS_LOCATION]
        phone: Optional[str]
        phone_extension: Optional[str]
        state: Optional[str]
        street1: Optional[str]
        street2: Optional[str]
        street3: Optional[str]
        supported_carriers_for_return_shipment: list[str]
        zip: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DatacenterAddressRequest(_Model):
        model: Optional[Union[str, ModelName]]
        sku_name: Union[str, SkuName]
        storage_location: str

        @overload
        def __init__(
                self, 
                *, 
                model: Optional[Union[str, ModelName]] = ..., 
                sku_name: Union[str, SkuName], 
                storage_location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DatacenterAddressResponse(_Model):
        data_center_azure_location: Optional[str]
        datacenter_address_type: str
        supported_carriers_for_return_shipment: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                datacenter_address_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DatacenterAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATACENTER_ADDRESS_INSTRUCTION = "DatacenterAddressInstruction"
        DATACENTER_ADDRESS_LOCATION = "DatacenterAddressLocation"


    class azure.mgmt.databox.models.DcAccessSecurityCode(_Model):
        forward_dc_access_code: Optional[str]
        reverse_dc_access_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                forward_dc_access_code: Optional[str] = ..., 
                reverse_dc_access_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DelayNotificationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        RESOLVED = "Resolved"


    class azure.mgmt.databox.models.Details(_Model):
        code: str
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DeviceCapabilityDetails(_Model):
        hardware_encryption: Optional[Union[str, HardwareEncryption]]


    class azure.mgmt.databox.models.DeviceCapabilityRequest(_Model):
        model: Optional[Union[str, ModelName]]
        sku_name: Optional[Union[str, SkuName]]

        @overload
        def __init__(
                self, 
                *, 
                model: Optional[Union[str, ModelName]] = ..., 
                sku_name: Optional[Union[str, SkuName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DeviceCapabilityResponse(_Model):
        device_capability_details: Optional[list[DeviceCapabilityDetails]]


    class azure.mgmt.databox.models.DeviceErasureDetails(_Model):
        device_erasure_status: Optional[Union[str, StageStatus]]
        erasure_or_destruction_certificate_sas_key: Optional[str]
        secure_erasure_certificate_sas_key: Optional[str]


    class azure.mgmt.databox.models.DiskScheduleAvailabilityRequest(ScheduleAvailabilityRequest, discriminator='DataBoxDisk'):
        country: str
        expected_data_size_in_tera_bytes: int
        model: Union[str, ModelName]
        sku_name: Literal[SkuName.DATA_BOX_DISK]
        storage_location: str

        @overload
        def __init__(
                self, 
                *, 
                country: Optional[str] = ..., 
                expected_data_size_in_tera_bytes: int, 
                model: Optional[Union[str, ModelName]] = ..., 
                storage_location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.DiskSecret(_Model):
        bit_locker_key: Optional[str]
        disk_serial_number: Optional[str]


    class azure.mgmt.databox.models.DoubleEncryption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databox.models.EncryptionPreferences(_Model):
        double_encryption: Optional[Union[str, DoubleEncryption]]
        hardware_encryption: Optional[Union[str, HardwareEncryption]]

        @overload
        def __init__(
                self, 
                *, 
                double_encryption: Optional[Union[str, DoubleEncryption]] = ..., 
                hardware_encryption: Optional[Union[str, HardwareEncryption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ErrorDetail(_Model):
        code: str
        details: Optional[list[Details]]
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[list[Details]] = ..., 
                message: str, 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ExportDiskDetails(_Model):
        backup_manifest_cloud_path: Optional[str]
        manifest_file: Optional[str]
        manifest_hash: Optional[str]


    class azure.mgmt.databox.models.FilterFileDetails(_Model):
        filter_file_path: str
        filter_file_type: Union[str, FilterFileType]

        @overload
        def __init__(
                self, 
                *, 
                filter_file_path: str, 
                filter_file_type: Union[str, FilterFileType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.FilterFileType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "AzureBlob"
        AZURE_FILE = "AzureFile"


    class azure.mgmt.databox.models.GranularCopyLogDetails(_Model):
        copy_log_details_type: str

        @overload
        def __init__(
                self, 
                *, 
                copy_log_details_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.GranularCopyProgress(_Model):
        account_id: Optional[str]
        actions: Optional[list[Union[str, CustomerResolutionCode]]]
        bytes_processed: Optional[int]
        data_account_type: Optional[Union[str, DataAccountType]]
        directories_errored_out: Optional[int]
        error: Optional[CloudError]
        files_errored_out: Optional[int]
        files_processed: Optional[int]
        invalid_directories_processed: Optional[int]
        invalid_file_bytes_uploaded: Optional[int]
        invalid_files_processed: Optional[int]
        is_enumeration_in_progress: Optional[bool]
        renamed_container_count: Optional[int]
        storage_account_name: Optional[str]
        total_bytes_to_process: Optional[int]
        total_files_to_process: Optional[int]
        transfer_type: Optional[Union[str, TransferType]]


    class azure.mgmt.databox.models.HardwareEncryption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databox.models.HeavyScheduleAvailabilityRequest(ScheduleAvailabilityRequest, discriminator='DataBoxHeavy'):
        country: str
        model: Union[str, ModelName]
        sku_name: Literal[SkuName.DATA_BOX_HEAVY]
        storage_location: str

        @overload
        def __init__(
                self, 
                *, 
                country: Optional[str] = ..., 
                model: Optional[Union[str, ModelName]] = ..., 
                storage_location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.IdentityProperties(_Model):
        type: Optional[str]
        user_assigned: Optional[UserAssignedProperties]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[str] = ..., 
                user_assigned: Optional[UserAssignedProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ImportDiskDetails(_Model):
        backup_manifest_cloud_path: Optional[str]
        bit_locker_key: str
        manifest_file: str
        manifest_hash: str

        @overload
        def __init__(
                self, 
                *, 
                bit_locker_key: str, 
                manifest_file: str, 
                manifest_hash: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.JobDelayDetails(_Model):
        description: Optional[str]
        error_code: Optional[Union[str, PortalDelayErrorCode]]
        resolution_time: Optional[datetime]
        start_time: Optional[datetime]
        status: Optional[Union[str, DelayNotificationStatus]]


    class azure.mgmt.databox.models.JobDeliveryInfo(_Model):
        scheduled_date_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                scheduled_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.JobDeliveryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NON_SCHEDULED = "NonScheduled"
        SCHEDULED = "Scheduled"


    class azure.mgmt.databox.models.JobDetails(_Model):
        actions: Optional[list[Union[str, CustomerResolutionCode]]]
        chain_of_custody_sas_key: Optional[str]
        contact_details: ContactDetails
        copy_log_details: Optional[list[CopyLogDetails]]
        data_center_code: Optional[Union[str, DataCenterCode]]
        data_export_details: Optional[list[DataExportDetails]]
        data_import_details: Optional[list[DataImportDetails]]
        datacenter_address: Optional[DatacenterAddressResponse]
        delivery_package: Optional[PackageShippingDetails]
        device_erasure_details: Optional[DeviceErasureDetails]
        expected_data_size_in_tera_bytes: Optional[int]
        job_details_type: str
        job_stages: Optional[list[JobStages]]
        key_encryption_key: Optional[KeyEncryptionKey]
        last_mitigation_action_on_job: Optional[LastMitigationActionOnJob]
        preferences: Optional[Preferences]
        return_package: Optional[PackageShippingDetails]
        reverse_shipment_label_sas_key: Optional[str]
        reverse_shipping_details: Optional[ReverseShippingDetails]
        shipping_address: Optional[ShippingAddress]

        @overload
        def __init__(
                self, 
                *, 
                contact_details: ContactDetails, 
                data_export_details: Optional[list[DataExportDetails]] = ..., 
                data_import_details: Optional[list[DataImportDetails]] = ..., 
                expected_data_size_in_tera_bytes: Optional[int] = ..., 
                job_details_type: str, 
                key_encryption_key: Optional[KeyEncryptionKey] = ..., 
                preferences: Optional[Preferences] = ..., 
                reverse_shipping_details: Optional[ReverseShippingDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.JobProperties(_Model):
        all_devices_lost: Optional[bool]
        cancellation_reason: Optional[str]
        delayed_stage: Optional[Union[str, StageName]]
        delivery_info: Optional[JobDeliveryInfo]
        delivery_type: Optional[Union[str, JobDeliveryType]]
        details: Optional[JobDetails]
        error: Optional[CloudError]
        is_cancellable: Optional[bool]
        is_cancellable_without_fee: Optional[bool]
        is_deletable: Optional[bool]
        is_prepare_to_ship_enabled: Optional[bool]
        is_shipping_address_editable: Optional[bool]
        reverse_shipping_details_update: Optional[Union[str, ReverseShippingDetailsEditStatus]]
        reverse_transport_preference_update: Optional[Union[str, ReverseTransportPreferenceEditStatus]]
        start_time: Optional[datetime]
        status: Optional[Union[str, StageName]]
        transfer_type: Union[str, TransferType]

        @overload
        def __init__(
                self, 
                *, 
                delivery_info: Optional[JobDeliveryInfo] = ..., 
                delivery_type: Optional[Union[str, JobDeliveryType]] = ..., 
                details: Optional[JobDetails] = ..., 
                transfer_type: Union[str, TransferType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.JobResource(TrackedResource):
        id: str
        identity: Optional[ResourceIdentity]
        location: str
        name: str
        properties: JobProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ResourceIdentity] = ..., 
                location: str, 
                properties: JobProperties, 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databox.models.JobResourceUpdateParameter(_Model):
        identity: Optional[ResourceIdentity]
        properties: Optional[UpdateJobProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ResourceIdentity] = ..., 
                properties: Optional[UpdateJobProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databox.models.JobSecrets(_Model):
        dc_access_security_code: Optional[DcAccessSecurityCode]
        error: Optional[CloudError]
        job_secrets_type: str

        @overload
        def __init__(
                self, 
                *, 
                job_secrets_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.JobStages(_Model):
        delay_information: Optional[list[JobDelayDetails]]
        display_name: Optional[str]
        job_stage_details: Optional[Any]
        stage_name: Optional[Union[str, StageName]]
        stage_status: Optional[Union[str, StageStatus]]
        stage_time: Optional[datetime]


    class azure.mgmt.databox.models.KekType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_MANAGED = "CustomerManaged"
        MICROSOFT_MANAGED = "MicrosoftManaged"


    class azure.mgmt.databox.models.KeyEncryptionKey(_Model):
        identity_properties: Optional[IdentityProperties]
        kek_type: Union[str, KekType]
        kek_url: Optional[str]
        kek_vault_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_properties: Optional[IdentityProperties] = ..., 
                kek_type: Union[str, KekType], 
                kek_url: Optional[str] = ..., 
                kek_vault_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.LastMitigationActionOnJob(_Model):
        action_date_time_in_utc: Optional[datetime]
        customer_resolution: Optional[Union[str, CustomerResolutionCode]]
        is_performed_by_customer: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                action_date_time_in_utc: Optional[datetime] = ..., 
                customer_resolution: Optional[Union[str, CustomerResolutionCode]] = ..., 
                is_performed_by_customer: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.LogCollectionLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        VERBOSE = "Verbose"


    class azure.mgmt.databox.models.ManagedDiskDetails(DataAccountDetails, discriminator='ManagedDisk'):
        data_account_type: Literal[DataAccountType.MANAGED_DISK]
        resource_group_id: str
        share_password: str
        staging_storage_account_id: str

        @overload
        def __init__(
                self, 
                *, 
                resource_group_id: str, 
                share_password: Optional[str] = ..., 
                staging_storage_account_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.MarkDevicesShippedRequest(_Model):
        deliver_to_dc_package_details: PackageCarrierInfo

        @overload
        def __init__(
                self, 
                *, 
                deliver_to_dc_package_details: PackageCarrierInfo
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.MitigateJobRequest(_Model):
        customer_resolution_code: Optional[Union[str, CustomerResolutionCode]]
        serial_number_customer_resolution_map: Optional[dict[str, Union[str, CustomerResolutionCode]]]

        @overload
        def __init__(
                self, 
                *, 
                customer_resolution_code: Optional[Union[str, CustomerResolutionCode]] = ..., 
                serial_number_customer_resolution_map: Optional[dict[str, Union[str, CustomerResolutionCode]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ModelName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DATA_BOX120 = "AzureDataBox120"
        AZURE_DATA_BOX525 = "AzureDataBox525"
        DATA_BOX = "DataBox"
        DATA_BOX_CUSTOMER_DISK = "DataBoxCustomerDisk"
        DATA_BOX_DISK = "DataBoxDisk"
        DATA_BOX_HEAVY = "DataBoxHeavy"


    class azure.mgmt.databox.models.NotificationPreference(_Model):
        send_notification: bool
        stage_name: Union[str, NotificationStageName]

        @overload
        def __init__(
                self, 
                *, 
                send_notification: bool, 
                stage_name: Union[str, NotificationStageName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.NotificationStageName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AT_AZURE_DC = "AtAzureDC"
        CREATED = "Created"
        DATA_COPY = "DataCopy"
        DELIVERED = "Delivered"
        DEVICE_PREPARED = "DevicePrepared"
        DISPATCHED = "Dispatched"
        PICKED_UP = "PickedUp"
        SHIPPED_TO_CUSTOMER = "ShippedToCustomer"


    class azure.mgmt.databox.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[OperationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                is_data_action: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.databox.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.OperationProperties(_Model):


    class azure.mgmt.databox.models.OverallValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_VALID_TO_PROCEED = "AllValidToProceed"
        CERTAIN_INPUT_VALIDATIONS_SKIPPED = "CertainInputValidationsSkipped"
        INPUTS_REVISIT_REQUIRED = "InputsRevisitRequired"


    class azure.mgmt.databox.models.PackageCarrierDetails(_Model):
        carrier_account_number: Optional[str]
        carrier_name: Optional[str]
        tracking_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                carrier_account_number: Optional[str] = ..., 
                carrier_name: Optional[str] = ..., 
                tracking_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.PackageCarrierInfo(_Model):
        carrier_name: Optional[str]
        tracking_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                carrier_name: Optional[str] = ..., 
                tracking_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.PackageShippingDetails(_Model):
        carrier_name: Optional[str]
        tracking_id: Optional[str]
        tracking_url: Optional[str]


    class azure.mgmt.databox.models.PortalDelayErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_ORDER_LIMIT_BREACHED_DELAY = "ActiveOrderLimitBreachedDelay"
        HIGH_DEMAND_DELAY = "HighDemandDelay"
        INTERNAL_ISSUE_DELAY = "InternalIssueDelay"
        LARGE_NUMBER_OF_FILES_DELAY = "LargeNumberOfFilesDelay"


    class azure.mgmt.databox.models.Preferences(_Model):
        encryption_preferences: Optional[EncryptionPreferences]
        preferred_data_center_region: Optional[list[str]]
        reverse_transport_preferences: Optional[TransportPreferences]
        storage_account_access_tier_preferences: Optional[list[Literal["Archive"]]]
        transport_preferences: Optional[TransportPreferences]

        @overload
        def __init__(
                self, 
                *, 
                encryption_preferences: Optional[EncryptionPreferences] = ..., 
                preferred_data_center_region: Optional[list[str]] = ..., 
                reverse_transport_preferences: Optional[TransportPreferences] = ..., 
                storage_account_access_tier_preferences: Optional[list[Literal[Archive]]] = ..., 
                transport_preferences: Optional[TransportPreferences] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.PreferencesValidationRequest(ValidationInputRequest, discriminator='ValidatePreferences'):
        device_type: Union[str, SkuName]
        model: Optional[Union[str, ModelName]]
        preference: Optional[Preferences]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_PREFERENCES]

        @overload
        def __init__(
                self, 
                *, 
                device_type: Union[str, SkuName], 
                model: Optional[Union[str, ModelName]] = ..., 
                preference: Optional[Preferences] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.PreferencesValidationResponseProperties(ValidationInputResponse, discriminator='ValidatePreferences'):
        error: CloudError
        status: Optional[Union[str, ValidationStatus]]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_PREFERENCES]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.RegionConfigurationRequest(_Model):
        datacenter_address_request: Optional[DatacenterAddressRequest]
        device_capability_request: Optional[DeviceCapabilityRequest]
        schedule_availability_request: Optional[ScheduleAvailabilityRequest]
        transport_availability_request: Optional[TransportAvailabilityRequest]

        @overload
        def __init__(
                self, 
                *, 
                datacenter_address_request: Optional[DatacenterAddressRequest] = ..., 
                device_capability_request: Optional[DeviceCapabilityRequest] = ..., 
                schedule_availability_request: Optional[ScheduleAvailabilityRequest] = ..., 
                transport_availability_request: Optional[TransportAvailabilityRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.RegionConfigurationResponse(_Model):
        datacenter_address_response: Optional[DatacenterAddressResponse]
        device_capability_response: Optional[DeviceCapabilityResponse]
        schedule_availability_response: Optional[ScheduleAvailabilityResponse]
        transport_availability_response: Optional[TransportAvailabilityResponse]


    class azure.mgmt.databox.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.databox.models.ResourceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[str]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[str] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ReverseShippingDetails(_Model):
        contact_details: Optional[ContactInfo]
        is_updated: Optional[bool]
        shipping_address: Optional[ShippingAddress]

        @overload
        def __init__(
                self, 
                *, 
                contact_details: Optional[ContactInfo] = ..., 
                shipping_address: Optional[ShippingAddress] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ReverseShippingDetailsEditStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_SUPPORTED = "NotSupported"


    class azure.mgmt.databox.models.ReverseTransportPreferenceEditStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_SUPPORTED = "NotSupported"


    class azure.mgmt.databox.models.ScheduleAvailabilityRequest(_Model):
        country: Optional[str]
        model: Optional[Union[str, ModelName]]
        sku_name: str
        storage_location: str

        @overload
        def __init__(
                self, 
                *, 
                country: Optional[str] = ..., 
                model: Optional[Union[str, ModelName]] = ..., 
                sku_name: str, 
                storage_location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ScheduleAvailabilityResponse(_Model):
        available_dates: Optional[list[datetime]]


    class azure.mgmt.databox.models.ShareCredentialDetails(_Model):
        password: Optional[str]
        share_name: Optional[str]
        share_type: Optional[Union[str, ShareDestinationFormatType]]
        supported_access_protocols: Optional[list[Union[str, AccessProtocol]]]
        user_name: Optional[str]


    class azure.mgmt.databox.models.ShareDestinationFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FILE = "AzureFile"
        BLOCK_BLOB = "BlockBlob"
        HCS = "HCS"
        MANAGED_DISK = "ManagedDisk"
        PAGE_BLOB = "PageBlob"
        UNKNOWN_TYPE = "UnknownType"


    class azure.mgmt.databox.models.ShipmentPickUpRequest(_Model):
        end_time: datetime
        shipment_location: str
        start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                end_time: datetime, 
                shipment_location: str, 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ShipmentPickUpResponse(_Model):
        confirmation_number: Optional[str]
        ready_by_time: Optional[datetime]


    class azure.mgmt.databox.models.ShippingAddress(_Model):
        address_type: Optional[Union[str, AddressType]]
        city: Optional[str]
        company_name: Optional[str]
        country: str
        postal_code: Optional[str]
        skip_address_validation: Optional[bool]
        state_or_province: Optional[str]
        street_address1: str
        street_address2: Optional[str]
        street_address3: Optional[str]
        tax_identification_number: Optional[str]
        zip_extended_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address_type: Optional[Union[str, AddressType]] = ..., 
                city: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: str, 
                postal_code: Optional[str] = ..., 
                skip_address_validation: Optional[bool] = ..., 
                state_or_province: Optional[str] = ..., 
                street_address1: str, 
                street_address2: Optional[str] = ..., 
                street_address3: Optional[str] = ..., 
                tax_identification_number: Optional[str] = ..., 
                zip_extended_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.Sku(_Model):
        display_name: Optional[str]
        family: Optional[str]
        model: Optional[Union[str, ModelName]]
        name: Union[str, SkuName]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                family: Optional[str] = ..., 
                model: Optional[Union[str, ModelName]] = ..., 
                name: Union[str, SkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.SkuAvailabilityValidationRequest(ValidationInputRequest, discriminator='ValidateSkuAvailability'):
        country: str
        device_type: Union[str, SkuName]
        location: str
        model: Optional[Union[str, ModelName]]
        transfer_type: Union[str, TransferType]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_SKU_AVAILABILITY]

        @overload
        def __init__(
                self, 
                *, 
                country: str, 
                device_type: Union[str, SkuName], 
                location: str, 
                model: Optional[Union[str, ModelName]] = ..., 
                transfer_type: Union[str, TransferType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.SkuAvailabilityValidationResponseProperties(ValidationInputResponse, discriminator='ValidateSkuAvailability'):
        error: CloudError
        status: Optional[Union[str, ValidationStatus]]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_SKU_AVAILABILITY]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.SkuCapacity(_Model):
        individual_sku_usable: Optional[str]
        maximum: Optional[str]
        usable: Optional[str]


    class azure.mgmt.databox.models.SkuCost(_Model):
        meter_id: Optional[str]
        meter_type: Optional[str]
        multiplier: Optional[float]


    class azure.mgmt.databox.models.SkuDisabledReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNTRY = "Country"
        FEATURE = "Feature"
        NONE = "None"
        NO_SUBSCRIPTION_INFO = "NoSubscriptionInfo"
        OFFER_TYPE = "OfferType"
        REGION = "Region"


    class azure.mgmt.databox.models.SkuInformation(_Model):
        enabled: Optional[bool]
        properties: Optional[SkuProperties]
        sku: Optional[Sku]


    class azure.mgmt.databox.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_BOX = "DataBox"
        DATA_BOX_CUSTOMER_DISK = "DataBoxCustomerDisk"
        DATA_BOX_DISK = "DataBoxDisk"
        DATA_BOX_HEAVY = "DataBoxHeavy"


    class azure.mgmt.databox.models.SkuProperties(_Model):
        api_versions: Optional[list[str]]
        capacity: Optional[SkuCapacity]
        costs: Optional[list[SkuCost]]
        countries_within_commerce_boundary: Optional[list[str]]
        data_location_to_service_location_map: Optional[list[DataLocationToServiceLocationMap]]
        disabled_reason: Optional[Union[str, SkuDisabledReason]]
        disabled_reason_message: Optional[str]
        required_feature: Optional[str]


    class azure.mgmt.databox.models.StageName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABORTED = "Aborted"
        AT_AZURE_DC = "AtAzureDC"
        AWAITING_SHIPMENT_DETAILS = "AwaitingShipmentDetails"
        CANCELLED = "Cancelled"
        COMPLETED = "Completed"
        COMPLETED_WITH_ERRORS = "CompletedWithErrors"
        COMPLETED_WITH_WARNINGS = "CompletedWithWarnings"
        CREATED = "Created"
        DATA_COPY = "DataCopy"
        DELIVERED = "Delivered"
        DEVICE_ORDERED = "DeviceOrdered"
        DEVICE_PREPARED = "DevicePrepared"
        DISPATCHED = "Dispatched"
        FAILED_ISSUE_DETECTED_AT_AZURE_DC = "Failed_IssueDetectedAtAzureDC"
        FAILED_ISSUE_REPORTED_AT_CUSTOMER = "Failed_IssueReportedAtCustomer"
        PICKED_UP = "PickedUp"
        PREPARING_TO_SHIP_FROM_AZURE_DC = "PreparingToShipFromAzureDC"
        READY_TO_DISPATCH_FROM_AZURE_DC = "ReadyToDispatchFromAzureDC"
        READY_TO_RECEIVE_AT_AZURE_DC = "ReadyToReceiveAtAzureDC"
        SHIPPED_TO_AZURE_DC = "ShippedToAzureDC"
        SHIPPED_TO_CUSTOMER = "ShippedToCustomer"


    class azure.mgmt.databox.models.StageStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        CANCELLING = "Cancelling"
        CUSTOMER_ACTION_PERFORMED = "CustomerActionPerformed"
        CUSTOMER_ACTION_PERFORMED_FOR_CLEAN_UP = "CustomerActionPerformedForCleanUp"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NONE = "None"
        SUCCEEDED = "Succeeded"
        SUCCEEDED_WITH_ERRORS = "SucceededWithErrors"
        SUCCEEDED_WITH_WARNINGS = "SucceededWithWarnings"
        WAITING_FOR_CUSTOMER_ACTION = "WaitingForCustomerAction"
        WAITING_FOR_CUSTOMER_ACTION_FOR_CLEAN_UP = "WaitingForCustomerActionForCleanUp"
        WAITING_FOR_CUSTOMER_ACTION_FOR_KEK = "WaitingForCustomerActionForKek"


    class azure.mgmt.databox.models.StorageAccountDetails(DataAccountDetails, discriminator='StorageAccount'):
        data_account_type: Literal[DataAccountType.STORAGE_ACCOUNT]
        share_password: str
        storage_account_id: str

        @overload
        def __init__(
                self, 
                *, 
                share_password: Optional[str] = ..., 
                storage_account_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.SubscriptionIsAllowedToCreateJobValidationRequest(ValidationInputRequest, discriminator='ValidateSubscriptionIsAllowedToCreateJob'):
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_SUBSCRIPTION_IS_ALLOWED_TO_CREATE_JOB]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.SubscriptionIsAllowedToCreateJobValidationResponseProperties(ValidationInputResponse, discriminator='ValidateSubscriptionIsAllowedToCreateJob'):
        error: CloudError
        status: Optional[Union[str, ValidationStatus]]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_SUBSCRIPTION_IS_ALLOWED_TO_CREATE_JOB]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.SystemData(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, CreatedByType]]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, CreatedByType]]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.TransferAllDetails(_Model):
        data_account_type: Union[str, DataAccountType]
        transfer_all_blobs: Optional[bool]
        transfer_all_files: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                data_account_type: Union[str, DataAccountType], 
                transfer_all_blobs: Optional[bool] = ..., 
                transfer_all_files: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.TransferConfiguration(_Model):
        transfer_all_details: Optional[TransferConfigurationTransferAllDetails]
        transfer_configuration_type: Union[str, TransferConfigurationType]
        transfer_filter_details: Optional[TransferConfigurationTransferFilterDetails]

        @overload
        def __init__(
                self, 
                *, 
                transfer_all_details: Optional[TransferConfigurationTransferAllDetails] = ..., 
                transfer_configuration_type: Union[str, TransferConfigurationType], 
                transfer_filter_details: Optional[TransferConfigurationTransferFilterDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.TransferConfigurationTransferAllDetails(_Model):
        include: Optional[TransferAllDetails]

        @overload
        def __init__(
                self, 
                *, 
                include: Optional[TransferAllDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.TransferConfigurationTransferFilterDetails(_Model):
        include: Optional[TransferFilterDetails]

        @overload
        def __init__(
                self, 
                *, 
                include: Optional[TransferFilterDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.TransferConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TRANSFER_ALL = "TransferAll"
        TRANSFER_USING_FILTER = "TransferUsingFilter"


    class azure.mgmt.databox.models.TransferFilterDetails(_Model):
        azure_file_filter_details: Optional[AzureFileFilterDetails]
        blob_filter_details: Optional[BlobFilterDetails]
        data_account_type: Union[str, DataAccountType]
        filter_file_details: Optional[list[FilterFileDetails]]

        @overload
        def __init__(
                self, 
                *, 
                azure_file_filter_details: Optional[AzureFileFilterDetails] = ..., 
                blob_filter_details: Optional[BlobFilterDetails] = ..., 
                data_account_type: Union[str, DataAccountType], 
                filter_file_details: Optional[list[FilterFileDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.TransferType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPORT_FROM_AZURE = "ExportFromAzure"
        IMPORT_TO_AZURE = "ImportToAzure"


    class azure.mgmt.databox.models.TransportAvailabilityDetails(_Model):
        shipment_type: Optional[Union[str, TransportShipmentTypes]]


    class azure.mgmt.databox.models.TransportAvailabilityRequest(_Model):
        model: Optional[Union[str, ModelName]]
        sku_name: Optional[Union[str, SkuName]]

        @overload
        def __init__(
                self, 
                *, 
                model: Optional[Union[str, ModelName]] = ..., 
                sku_name: Optional[Union[str, SkuName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.TransportAvailabilityResponse(_Model):
        transport_availability_details: Optional[list[TransportAvailabilityDetails]]


    class azure.mgmt.databox.models.TransportPreferences(_Model):
        is_updated: Optional[bool]
        preferred_shipment_type: Union[str, TransportShipmentTypes]

        @overload
        def __init__(
                self, 
                *, 
                preferred_shipment_type: Union[str, TransportShipmentTypes]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.TransportShipmentTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_MANAGED = "CustomerManaged"
        MICROSOFT_MANAGED = "MicrosoftManaged"


    class azure.mgmt.databox.models.UnencryptedCredentials(_Model):
        job_name: Optional[str]
        job_secrets: Optional[JobSecrets]


    class azure.mgmt.databox.models.UpdateJobDetails(_Model):
        contact_details: Optional[ContactDetails]
        key_encryption_key: Optional[KeyEncryptionKey]
        preferences: Optional[Preferences]
        return_to_customer_package_details: Optional[PackageCarrierDetails]
        reverse_shipping_details: Optional[ReverseShippingDetails]
        shipping_address: Optional[ShippingAddress]

        @overload
        def __init__(
                self, 
                *, 
                contact_details: Optional[ContactDetails] = ..., 
                key_encryption_key: Optional[KeyEncryptionKey] = ..., 
                preferences: Optional[Preferences] = ..., 
                return_to_customer_package_details: Optional[PackageCarrierDetails] = ..., 
                reverse_shipping_details: Optional[ReverseShippingDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.UpdateJobProperties(_Model):
        details: Optional[UpdateJobDetails]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[UpdateJobDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.databox.models.UserAssignedProperties(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ValidateAddress(ValidationInputRequest, discriminator='ValidateAddress'):
        device_type: Union[str, SkuName]
        model: Optional[Union[str, ModelName]]
        shipping_address: ShippingAddress
        transport_preferences: Optional[TransportPreferences]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_ADDRESS]

        @overload
        def __init__(
                self, 
                *, 
                device_type: Union[str, SkuName], 
                model: Optional[Union[str, ModelName]] = ..., 
                shipping_address: ShippingAddress, 
                transport_preferences: Optional[TransportPreferences] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ValidationInputDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VALIDATE_ADDRESS = "ValidateAddress"
        VALIDATE_CREATE_ORDER_LIMIT = "ValidateCreateOrderLimit"
        VALIDATE_DATA_TRANSFER_DETAILS = "ValidateDataTransferDetails"
        VALIDATE_PREFERENCES = "ValidatePreferences"
        VALIDATE_SKU_AVAILABILITY = "ValidateSkuAvailability"
        VALIDATE_SUBSCRIPTION_IS_ALLOWED_TO_CREATE_JOB = "ValidateSubscriptionIsAllowedToCreateJob"


    class azure.mgmt.databox.models.ValidationInputRequest(_Model):
        validation_type: str

        @overload
        def __init__(
                self, 
                *, 
                validation_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ValidationInputResponse(_Model):
        error: Optional[CloudError]
        validation_type: str

        @overload
        def __init__(
                self, 
                *, 
                validation_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ValidationRequest(_Model):
        individual_request_details: list[ValidationInputRequest]
        validation_category: Literal["JobCreationValidation"]

        @overload
        def __init__(
                self, 
                *, 
                individual_request_details: list[ValidationInputRequest]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databox.models.ValidationResponse(_Model):
        properties: Optional[ValidationResponseProperties]


    class azure.mgmt.databox.models.ValidationResponseProperties(_Model):
        individual_response_details: Optional[list[ValidationInputResponse]]
        status: Optional[Union[str, OverallValidationStatus]]


    class azure.mgmt.databox.models.ValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        SKIPPED = "Skipped"
        VALID = "Valid"


namespace azure.mgmt.databox.operations

    class azure.mgmt.databox.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource: JobResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JobResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource: JobResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JobResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JobResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource_update_parameter: JobResourceUpdateParameter, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[JobResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource_update_parameter: JobResourceUpdateParameter, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[JobResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource_update_parameter: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[JobResource]: ...

        @overload
        def book_shipment_pick_up(
                self, 
                resource_group_name: str, 
                job_name: str, 
                shipment_pick_up_request: ShipmentPickUpRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShipmentPickUpResponse: ...

        @overload
        def book_shipment_pick_up(
                self, 
                resource_group_name: str, 
                job_name: str, 
                shipment_pick_up_request: ShipmentPickUpRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShipmentPickUpResponse: ...

        @overload
        def book_shipment_pick_up(
                self, 
                resource_group_name: str, 
                job_name: str, 
                shipment_pick_up_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShipmentPickUpResponse: ...

        @overload
        def cancel(
                self, 
                resource_group_name: str, 
                job_name: str, 
                cancellation_reason: CancellationReason, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def cancel(
                self, 
                resource_group_name: str, 
                job_name: str, 
                cancellation_reason: CancellationReason, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def cancel(
                self, 
                resource_group_name: str, 
                job_name: str, 
                cancellation_reason: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                job_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> JobResource: ...

        @distributed_trace
        def list(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JobResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JobResource]: ...

        @distributed_trace
        def list_credentials(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> ItemPaged[UnencryptedCredentials]: ...

        @overload
        def mark_devices_shipped(
                self, 
                job_name: str, 
                resource_group_name: str, 
                mark_devices_shipped_request: MarkDevicesShippedRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def mark_devices_shipped(
                self, 
                job_name: str, 
                resource_group_name: str, 
                mark_devices_shipped_request: MarkDevicesShippedRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def mark_devices_shipped(
                self, 
                job_name: str, 
                resource_group_name: str, 
                mark_devices_shipped_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.databox.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.databox.operations.ServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list_available_skus_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                available_sku_request: AvailableSkuRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[SkuInformation]: ...

        @overload
        def list_available_skus_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                available_sku_request: AvailableSkuRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[SkuInformation]: ...

        @overload
        def list_available_skus_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                available_sku_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[SkuInformation]: ...

        @overload
        def region_configuration(
                self, 
                location: str, 
                region_configuration_request: RegionConfigurationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegionConfigurationResponse: ...

        @overload
        def region_configuration(
                self, 
                location: str, 
                region_configuration_request: RegionConfigurationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegionConfigurationResponse: ...

        @overload
        def region_configuration(
                self, 
                location: str, 
                region_configuration_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegionConfigurationResponse: ...

        @overload
        def region_configuration_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                region_configuration_request: RegionConfigurationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegionConfigurationResponse: ...

        @overload
        def region_configuration_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                region_configuration_request: RegionConfigurationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegionConfigurationResponse: ...

        @overload
        def region_configuration_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                region_configuration_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegionConfigurationResponse: ...

        @overload
        def validate_address(
                self, 
                location: str, 
                validate_address: ValidateAddress, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddressValidationOutput: ...

        @overload
        def validate_address(
                self, 
                location: str, 
                validate_address: ValidateAddress, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddressValidationOutput: ...

        @overload
        def validate_address(
                self, 
                location: str, 
                validate_address: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddressValidationOutput: ...

        @overload
        def validate_inputs(
                self, 
                location: str, 
                validation_request: ValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        def validate_inputs(
                self, 
                location: str, 
                validation_request: ValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        def validate_inputs(
                self, 
                location: str, 
                validation_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        def validate_inputs_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                validation_request: ValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        def validate_inputs_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                validation_request: ValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...

        @overload
        def validate_inputs_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                validation_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...


namespace azure.mgmt.databox.types

    class azure.mgmt.databox.types.AccountCredentialDetails(TypedDict, total=False):
        key "accountConnectionString": str
        key "accountName": str
        key "dataAccountType": Union[str, DataAccountType]
        account_connection_string: str
        account_name: str
        data_account_type: Union[str, DataAccountType]
        shareCredentialDetails: list[ShareCredentialDetails]
        share_credential_details: list[ShareCredentialDetails]


    class azure.mgmt.databox.types.AdditionalErrorInfo(TypedDict, total=False):
        key "type": str
        info: dict[str, Any]
        type: str


    class azure.mgmt.databox.types.AddressValidationOutput(TypedDict, total=False):
        key "properties": ForwardRef('AddressValidationProperties', module='types')
        properties: AddressValidationProperties


    class azure.mgmt.databox.types.AddressValidationProperties(TypedDict, total=False):
        key "error": ForwardRef('CloudError', module='types')
        key "validationStatus": Union[str, AddressValidationStatus]
        key "validationType": Required[Literal[ValidationInputDiscriminator.VALIDATE_ADDRESS]]
        alternateAddresses: list[ShippingAddress]
        alternate_addresses: list[ShippingAddress]
        error: CloudError
        validation_status: Union[str, AddressValidationStatus]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_ADDRESS]


    class azure.mgmt.databox.types.ApiError(TypedDict, total=False):
        key "error": Required[ErrorDetail]
        error: ErrorDetail


    class azure.mgmt.databox.types.ApplianceNetworkConfiguration(TypedDict, total=False):
        key "macAddress": str
        key "name": str
        mac_address: str
        name: str


    class azure.mgmt.databox.types.AvailableSkuRequest(TypedDict, total=False):
        key "country": Required[str]
        key "location": Required[str]
        key "transferType": Required[Union[str, TransferType]]
        country: str
        location: str
        skuNames: list[Union[str, SkuName]]
        sku_names: list[Union[str, SkuName]]
        transfer_type: Union[str, TransferType]


    class azure.mgmt.databox.types.AzureFileFilterDetails(TypedDict, total=False):
        filePathList: list[str]
        filePrefixList: list[str]
        fileShareList: list[str]
        file_path_list: list[str]
        file_prefix_list: list[str]
        file_share_list: list[str]


    class azure.mgmt.databox.types.BlobFilterDetails(TypedDict, total=False):
        blobPathList: list[str]
        blobPrefixList: list[str]
        blob_path_list: list[str]
        blob_prefix_list: list[str]
        containerList: list[str]
        container_list: list[str]


    class azure.mgmt.databox.types.CancellationReason(TypedDict, total=False):
        key "reason": Required[str]
        reason: str


    class azure.mgmt.databox.types.ClassDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_BOX = "DataBox"
        DATA_BOX_CUSTOMER_DISK = "DataBoxCustomerDisk"
        DATA_BOX_DISK = "DataBoxDisk"
        DATA_BOX_HEAVY = "DataBoxHeavy"


    class azure.mgmt.databox.types.CloudError(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[AdditionalErrorInfo]
        additional_info: list[AdditionalErrorInfo]
        code: str
        details: list[CloudError]
        message: str
        target: str


    class azure.mgmt.databox.types.ContactDetails(TypedDict, total=False):
        key "contactName": Required[str]
        key "emailList": Required[list[str]]
        key "mobile": str
        key "phone": Required[str]
        key "phoneExtension": str
        contact_name: str
        email_list: list[str]
        mobile: str
        notificationPreference: list[NotificationPreference]
        notification_preference: list[NotificationPreference]
        phone: str
        phone_extension: str


    class azure.mgmt.databox.types.ContactInfo(TypedDict, total=False):
        key "contactName": Required[str]
        key "mobile": str
        key "phone": Required[str]
        key "phoneExtension": str
        contact_name: str
        mobile: str
        phone: str
        phone_extension: str


    class azure.mgmt.databox.types.CopyProgress(TypedDict, total=False):
        key "accountId": str
        key "bytesProcessed": int
        key "dataAccountType": Union[str, DataAccountType]
        key "directoriesErroredOut": int
        key "error": ForwardRef('CloudError', module='types')
        key "filesErroredOut": int
        key "filesProcessed": int
        key "invalidDirectoriesProcessed": int
        key "invalidFileBytesUploaded": int
        key "invalidFilesProcessed": int
        key "isEnumerationInProgress": bool
        key "renamedContainerCount": int
        key "storageAccountName": str
        key "totalBytesToProcess": int
        key "totalFilesToProcess": int
        key "transferType": Union[str, TransferType]
        account_id: str
        actions: list[Union[str, CustomerResolutionCode]]
        bytes_processed: int
        data_account_type: Union[str, DataAccountType]
        directories_errored_out: int
        error: CloudError
        files_errored_out: int
        files_processed: int
        invalid_directories_processed: int
        invalid_file_bytes_uploaded: int
        invalid_files_processed: int
        is_enumeration_in_progress: bool
        renamed_container_count: int
        storage_account_name: str
        total_bytes_to_process: int
        total_files_to_process: int
        transfer_type: Union[str, TransferType]


    class azure.mgmt.databox.types.CreateJobValidations(TypedDict, total=False):
        key "individualRequestDetails": Required[list[ValidationInputRequest]]
        key "validationCategory": Required[Literal["JobCreationValidation"]]
        individual_request_details: list[ValidationInputRequest]
        validation_category: Literal[JobCreationValidation]


    class azure.mgmt.databox.types.CreateOrderLimitForSubscriptionValidationRequest(TypedDict, total=False):
        key "deviceType": Required[Union[str, SkuName]]
        key "model": Union[str, ModelName]
        key "validationType": Required[Literal[ValidationInputDiscriminator.VALIDATE_CREATE_ORDER_LIMIT]]
        device_type: Union[str, SkuName]
        model: Union[str, ModelName]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_CREATE_ORDER_LIMIT]


    class azure.mgmt.databox.types.CreateOrderLimitForSubscriptionValidationResponseProperties(TypedDict, total=False):
        key "error": ForwardRef('CloudError', module='types')
        key "status": Union[str, ValidationStatus]
        key "validationType": Required[Literal[ValidationInputDiscriminator.VALIDATE_CREATE_ORDER_LIMIT]]
        error: CloudError
        status: Union[str, ValidationStatus]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_CREATE_ORDER_LIMIT]


    class azure.mgmt.databox.types.CustomerDiskJobSecrets(TypedDict, total=False):
        key "carrierAccountNumber": str
        key "dcAccessSecurityCode": ForwardRef('DcAccessSecurityCode', module='types')
        key "error": ForwardRef('CloudError', module='types')
        key "jobSecretsType": Required[Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]]
        carrier_account_number: str
        dc_access_security_code: DcAccessSecurityCode
        diskSecrets: list[DiskSecret]
        disk_secrets: list[DiskSecret]
        error: CloudError
        job_secrets_type: Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]


    class azure.mgmt.databox.types.DataAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_DISK = "ManagedDisk"
        STORAGE_ACCOUNT = "StorageAccount"


    class azure.mgmt.databox.types.DataBoxAccountCopyLogDetails(TypedDict, total=False):
        key "accountName": str
        key "copyLogDetailsType": Required[Literal[ClassDiscriminator.DATA_BOX]]
        key "copyLogLink": str
        key "copyVerboseLogLink": str
        account_name: str
        copy_log_details_type: Literal[ClassDiscriminator.DATA_BOX]
        copy_log_link: str
        copy_verbose_log_link: str


    class azure.mgmt.databox.types.DataBoxCustomerDiskCopyLogDetails(TypedDict, total=False):
        key "copyLogDetailsType": Required[Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]]
        key "errorLogLink": str
        key "serialNumber": str
        key "verboseLogLink": str
        copy_log_details_type: Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]
        error_log_link: str
        serial_number: str
        verbose_log_link: str


    class azure.mgmt.databox.types.DataBoxCustomerDiskCopyProgress(CopyProgress):
        key "accountId": str
        key "bytesProcessed": int
        key "copyStatus": Union[str, CopyStatus]
        key "dataAccountType": Union[str, DataAccountType]
        key "directoriesErroredOut": int
        key "error": ForwardRef('CloudError', module='types')
        key "filesErroredOut": int
        key "filesProcessed": int
        key "invalidDirectoriesProcessed": int
        key "invalidFileBytesUploaded": int
        key "invalidFilesProcessed": int
        key "isEnumerationInProgress": bool
        key "renamedContainerCount": int
        key "serialNumber": str
        key "storageAccountName": str
        key "totalBytesToProcess": int
        key "totalFilesToProcess": int
        key "transferType": Union[str, TransferType]
        account_id: str
        actions: list[Union[str, CustomerResolutionCode]]
        bytes_processed: int
        copy_status: Union[str, CopyStatus]
        data_account_type: Union[str, DataAccountType]
        directories_errored_out: int
        error: CloudError
        files_errored_out: int
        files_processed: int
        invalid_directories_processed: int
        invalid_file_bytes_uploaded: int
        invalid_files_processed: int
        is_enumeration_in_progress: bool
        renamed_container_count: int
        serial_number: str
        storage_account_name: str
        total_bytes_to_process: int
        total_files_to_process: int
        transfer_type: Union[str, TransferType]


    class azure.mgmt.databox.types.DataBoxCustomerDiskJobDetails(TypedDict, total=False):
        key "chainOfCustodySasKey": str
        key "contactDetails": Required[ContactDetails]
        key "dataCenterCode": Union[str, DataCenterCode]
        key "datacenterAddress": ForwardRef('DatacenterAddressResponse', module='types')
        key "deliverToDcPackageDetails": ForwardRef('PackageCarrierInfo', module='types')
        key "deliveryPackage": ForwardRef('PackageShippingDetails', module='types')
        key "deviceErasureDetails": ForwardRef('DeviceErasureDetails', module='types')
        key "enableManifestBackup": bool
        key "expectedDataSizeInTeraBytes": int
        key "jobDetailsType": Required[Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]]
        key "keyEncryptionKey": ForwardRef('KeyEncryptionKey', module='types')
        key "lastMitigationActionOnJob": ForwardRef('LastMitigationActionOnJob', module='types')
        key "preferences": ForwardRef('Preferences', module='types')
        key "returnPackage": ForwardRef('PackageShippingDetails', module='types')
        key "returnToCustomerPackageDetails": Required[PackageCarrierDetails]
        key "reverseShipmentLabelSasKey": str
        key "reverseShippingDetails": ForwardRef('ReverseShippingDetails', module='types')
        key "shippingAddress": ForwardRef('ShippingAddress', module='types')
        actions: list[Union[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copyLogDetails: list[CopyLogDetails]
        copyProgress: list[DataBoxCustomerDiskCopyProgress]
        copy_log_details: list[CopyLogDetails]
        copy_progress: list[DataBoxCustomerDiskCopyProgress]
        dataExportDetails: list[DataExportDetails]
        dataImportDetails: list[DataImportDetails]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        deliver_to_dc_package_details: PackageCarrierInfo
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        enable_manifest_backup: bool
        expected_data_size_in_tera_bytes: int
        exportDiskDetailsCollection: dict[str, ExportDiskDetails]
        export_disk_details_collection: dict[str, ExportDiskDetails]
        importDiskDetailsCollection: dict[str, ImportDiskDetails]
        import_disk_details_collection: dict[str, ImportDiskDetails]
        jobStages: list[JobStages]
        job_details_type: Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        preferences: Preferences
        return_package: PackageShippingDetails
        return_to_customer_package_details: PackageCarrierDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress


    class azure.mgmt.databox.types.DataBoxDiskCopyLogDetails(TypedDict, total=False):
        key "copyLogDetailsType": Required[Literal[ClassDiscriminator.DATA_BOX_DISK]]
        key "diskSerialNumber": str
        key "errorLogLink": str
        key "verboseLogLink": str
        copy_log_details_type: Literal[ClassDiscriminator.DATA_BOX_DISK]
        disk_serial_number: str
        error_log_link: str
        verbose_log_link: str


    class azure.mgmt.databox.types.DataBoxDiskCopyProgress(TypedDict, total=False):
        key "bytesCopied": int
        key "error": ForwardRef('CloudError', module='types')
        key "percentComplete": int
        key "serialNumber": str
        key "status": Union[str, CopyStatus]
        actions: list[Union[str, CustomerResolutionCode]]
        bytes_copied: int
        error: CloudError
        percent_complete: int
        serial_number: str
        status: Union[str, CopyStatus]


    class azure.mgmt.databox.types.DataBoxDiskGranularCopyLogDetails(TypedDict, total=False):
        key "accountId": str
        key "copyLogDetailsType": Required[Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]]
        key "errorLogLink": str
        key "serialNumber": str
        key "verboseLogLink": str
        account_id: str
        copy_log_details_type: Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]
        error_log_link: str
        serial_number: str
        verbose_log_link: str


    class azure.mgmt.databox.types.DataBoxDiskGranularCopyProgress(GranularCopyProgress):
        key "accountId": str
        key "bytesProcessed": int
        key "copyStatus": Union[str, CopyStatus]
        key "dataAccountType": Union[str, DataAccountType]
        key "directoriesErroredOut": int
        key "error": ForwardRef('CloudError', module='types')
        key "filesErroredOut": int
        key "filesProcessed": int
        key "invalidDirectoriesProcessed": int
        key "invalidFileBytesUploaded": int
        key "invalidFilesProcessed": int
        key "isEnumerationInProgress": bool
        key "renamedContainerCount": int
        key "serialNumber": str
        key "storageAccountName": str
        key "totalBytesToProcess": int
        key "totalFilesToProcess": int
        key "transferType": Union[str, TransferType]
        account_id: str
        actions: list[Union[str, CustomerResolutionCode]]
        bytes_processed: int
        copy_status: Union[str, CopyStatus]
        data_account_type: Union[str, DataAccountType]
        directories_errored_out: int
        error: CloudError
        files_errored_out: int
        files_processed: int
        invalid_directories_processed: int
        invalid_file_bytes_uploaded: int
        invalid_files_processed: int
        is_enumeration_in_progress: bool
        renamed_container_count: int
        serial_number: str
        storage_account_name: str
        total_bytes_to_process: int
        total_files_to_process: int
        transfer_type: Union[str, TransferType]


    class azure.mgmt.databox.types.DataBoxDiskJobDetails(TypedDict, total=False):
        key "chainOfCustodySasKey": str
        key "contactDetails": Required[ContactDetails]
        key "dataCenterCode": Union[str, DataCenterCode]
        key "datacenterAddress": ForwardRef('DatacenterAddressResponse', module='types')
        key "deliveryPackage": ForwardRef('PackageShippingDetails', module='types')
        key "deviceErasureDetails": ForwardRef('DeviceErasureDetails', module='types')
        key "expectedDataSizeInTeraBytes": int
        key "jobDetailsType": Required[Literal[ClassDiscriminator.DATA_BOX_DISK]]
        key "keyEncryptionKey": ForwardRef('KeyEncryptionKey', module='types')
        key "lastMitigationActionOnJob": ForwardRef('LastMitigationActionOnJob', module='types')
        key "passkey": str
        key "preferences": ForwardRef('Preferences', module='types')
        key "returnPackage": ForwardRef('PackageShippingDetails', module='types')
        key "reverseShipmentLabelSasKey": str
        key "reverseShippingDetails": ForwardRef('ReverseShippingDetails', module='types')
        key "shippingAddress": ForwardRef('ShippingAddress', module='types')
        actions: list[Union[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copyLogDetails: list[CopyLogDetails]
        copyProgress: list[DataBoxDiskCopyProgress]
        copy_log_details: list[CopyLogDetails]
        copy_progress: list[DataBoxDiskCopyProgress]
        dataExportDetails: list[DataExportDetails]
        dataImportDetails: list[DataImportDetails]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        disksAndSizeDetails: dict[str, int]
        disks_and_size_details: dict[str, int]
        expected_data_size_in_tera_bytes: int
        granularCopyLogDetails: list[DataBoxDiskGranularCopyLogDetails]
        granularCopyProgress: list[DataBoxDiskGranularCopyProgress]
        granular_copy_log_details: list[DataBoxDiskGranularCopyLogDetails]
        granular_copy_progress: list[DataBoxDiskGranularCopyProgress]
        jobStages: list[JobStages]
        job_details_type: Literal[ClassDiscriminator.DATA_BOX_DISK]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        passkey: str
        preferences: Preferences
        preferredDisks: dict[str, int]
        preferred_disks: dict[str, int]
        return_package: PackageShippingDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress


    class azure.mgmt.databox.types.DataBoxDiskJobSecrets(TypedDict, total=False):
        key "dcAccessSecurityCode": ForwardRef('DcAccessSecurityCode', module='types')
        key "error": ForwardRef('CloudError', module='types')
        key "isPasskeyUserDefined": bool
        key "jobSecretsType": Required[Literal[ClassDiscriminator.DATA_BOX_DISK]]
        key "passKey": str
        dc_access_security_code: DcAccessSecurityCode
        diskSecrets: list[DiskSecret]
        disk_secrets: list[DiskSecret]
        error: CloudError
        is_passkey_user_defined: bool
        job_secrets_type: Literal[ClassDiscriminator.DATA_BOX_DISK]
        pass_key: str


    class azure.mgmt.databox.types.DataBoxHeavyAccountCopyLogDetails(TypedDict, total=False):
        key "accountName": str
        key "copyLogDetailsType": Required[Literal[ClassDiscriminator.DATA_BOX_HEAVY]]
        account_name: str
        copyLogLink: list[str]
        copyVerboseLogLink: list[str]
        copy_log_details_type: Literal[ClassDiscriminator.DATA_BOX_HEAVY]
        copy_log_link: list[str]
        copy_verbose_log_link: list[str]


    class azure.mgmt.databox.types.DataBoxHeavyJobDetails(TypedDict, total=False):
        key "chainOfCustodySasKey": str
        key "contactDetails": Required[ContactDetails]
        key "dataCenterCode": Union[str, DataCenterCode]
        key "datacenterAddress": ForwardRef('DatacenterAddressResponse', module='types')
        key "deliveryPackage": ForwardRef('PackageShippingDetails', module='types')
        key "deviceErasureDetails": ForwardRef('DeviceErasureDetails', module='types')
        key "devicePassword": str
        key "expectedDataSizeInTeraBytes": int
        key "jobDetailsType": Required[Literal[ClassDiscriminator.DATA_BOX_HEAVY]]
        key "keyEncryptionKey": ForwardRef('KeyEncryptionKey', module='types')
        key "lastMitigationActionOnJob": ForwardRef('LastMitigationActionOnJob', module='types')
        key "preferences": ForwardRef('Preferences', module='types')
        key "returnPackage": ForwardRef('PackageShippingDetails', module='types')
        key "reverseShipmentLabelSasKey": str
        key "reverseShippingDetails": ForwardRef('ReverseShippingDetails', module='types')
        key "shippingAddress": ForwardRef('ShippingAddress', module='types')
        actions: list[Union[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copyLogDetails: list[CopyLogDetails]
        copyProgress: list[CopyProgress]
        copy_log_details: list[CopyLogDetails]
        copy_progress: list[CopyProgress]
        dataExportDetails: list[DataExportDetails]
        dataImportDetails: list[DataImportDetails]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        device_password: str
        expected_data_size_in_tera_bytes: int
        jobStages: list[JobStages]
        job_details_type: Literal[ClassDiscriminator.DATA_BOX_HEAVY]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        preferences: Preferences
        return_package: PackageShippingDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress


    class azure.mgmt.databox.types.DataBoxHeavyJobSecrets(TypedDict, total=False):
        key "dcAccessSecurityCode": ForwardRef('DcAccessSecurityCode', module='types')
        key "error": ForwardRef('CloudError', module='types')
        key "jobSecretsType": Required[Literal[ClassDiscriminator.DATA_BOX_HEAVY]]
        cabinetPodSecrets: list[DataBoxHeavySecret]
        cabinet_pod_secrets: list[DataBoxHeavySecret]
        dc_access_security_code: DcAccessSecurityCode
        error: CloudError
        job_secrets_type: Literal[ClassDiscriminator.DATA_BOX_HEAVY]


    class azure.mgmt.databox.types.DataBoxHeavySecret(TypedDict, total=False):
        key "devicePassword": str
        key "deviceSerialNumber": str
        key "encodedValidationCertPubKey": str
        accountCredentialDetails: list[AccountCredentialDetails]
        account_credential_details: list[AccountCredentialDetails]
        device_password: str
        device_serial_number: str
        encoded_validation_cert_pub_key: str
        networkConfigurations: list[ApplianceNetworkConfiguration]
        network_configurations: list[ApplianceNetworkConfiguration]


    class azure.mgmt.databox.types.DataBoxJobDetails(TypedDict, total=False):
        key "chainOfCustodySasKey": str
        key "contactDetails": Required[ContactDetails]
        key "dataCenterCode": Union[str, DataCenterCode]
        key "datacenterAddress": ForwardRef('DatacenterAddressResponse', module='types')
        key "deliveryPackage": ForwardRef('PackageShippingDetails', module='types')
        key "deviceErasureDetails": ForwardRef('DeviceErasureDetails', module='types')
        key "devicePassword": str
        key "expectedDataSizeInTeraBytes": int
        key "jobDetailsType": Required[Literal[ClassDiscriminator.DATA_BOX]]
        key "keyEncryptionKey": ForwardRef('KeyEncryptionKey', module='types')
        key "lastMitigationActionOnJob": ForwardRef('LastMitigationActionOnJob', module='types')
        key "preferences": ForwardRef('Preferences', module='types')
        key "returnPackage": ForwardRef('PackageShippingDetails', module='types')
        key "reverseShipmentLabelSasKey": str
        key "reverseShippingDetails": ForwardRef('ReverseShippingDetails', module='types')
        key "shippingAddress": ForwardRef('ShippingAddress', module='types')
        actions: list[Union[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copyLogDetails: list[CopyLogDetails]
        copyProgress: list[CopyProgress]
        copy_log_details: list[CopyLogDetails]
        copy_progress: list[CopyProgress]
        dataExportDetails: list[DataExportDetails]
        dataImportDetails: list[DataImportDetails]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        device_password: str
        expected_data_size_in_tera_bytes: int
        jobStages: list[JobStages]
        job_details_type: Literal[ClassDiscriminator.DATA_BOX]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        preferences: Preferences
        return_package: PackageShippingDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress


    class azure.mgmt.databox.types.DataBoxScheduleAvailabilityRequest(TypedDict, total=False):
        key "country": str
        key "model": Union[str, ModelName]
        key "skuName": Required[Literal[SkuName.DATA_BOX]]
        key "storageLocation": Required[str]
        country: str
        model: Union[str, ModelName]
        sku_name: Literal[SkuName.DATA_BOX]
        storage_location: str


    class azure.mgmt.databox.types.DataBoxSecret(TypedDict, total=False):
        key "devicePassword": str
        key "deviceSerialNumber": str
        key "encodedValidationCertPubKey": str
        accountCredentialDetails: list[AccountCredentialDetails]
        account_credential_details: list[AccountCredentialDetails]
        device_password: str
        device_serial_number: str
        encoded_validation_cert_pub_key: str
        networkConfigurations: list[ApplianceNetworkConfiguration]
        network_configurations: list[ApplianceNetworkConfiguration]


    class azure.mgmt.databox.types.DataExportDetails(TypedDict, total=False):
        key "accountDetails": Required[DataAccountDetails]
        key "logCollectionLevel": Union[str, LogCollectionLevel]
        key "transferConfiguration": Required[TransferConfiguration]
        account_details: DataAccountDetails
        log_collection_level: Union[str, LogCollectionLevel]
        transfer_configuration: TransferConfiguration


    class azure.mgmt.databox.types.DataImportDetails(TypedDict, total=False):
        key "accountDetails": Required[DataAccountDetails]
        key "logCollectionLevel": Union[str, LogCollectionLevel]
        account_details: DataAccountDetails
        log_collection_level: Union[str, LogCollectionLevel]


    class azure.mgmt.databox.types.DataLocationToServiceLocationMap(TypedDict, total=False):
        key "dataLocation": str
        key "serviceLocation": str
        data_location: str
        service_location: str


    class azure.mgmt.databox.types.DataTransferDetailsValidationRequest(TypedDict, total=False):
        key "deviceType": Required[Union[str, SkuName]]
        key "model": Union[str, ModelName]
        key "transferType": Required[Union[str, TransferType]]
        key "validationType": Required[Literal[ValidationInputDiscriminator.VALIDATE_DATA_TRANSFER_DETAILS]]
        dataExportDetails: list[DataExportDetails]
        dataImportDetails: list[DataImportDetails]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        device_type: Union[str, SkuName]
        model: Union[str, ModelName]
        transfer_type: Union[str, TransferType]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_DATA_TRANSFER_DETAILS]


    class azure.mgmt.databox.types.DataTransferDetailsValidationResponseProperties(TypedDict, total=False):
        key "error": ForwardRef('CloudError', module='types')
        key "status": Union[str, ValidationStatus]
        key "validationType": Required[Literal[ValidationInputDiscriminator.VALIDATE_DATA_TRANSFER_DETAILS]]
        error: CloudError
        status: Union[str, ValidationStatus]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_DATA_TRANSFER_DETAILS]


    class azure.mgmt.databox.types.DataboxJobSecrets(TypedDict, total=False):
        key "dcAccessSecurityCode": ForwardRef('DcAccessSecurityCode', module='types')
        key "error": ForwardRef('CloudError', module='types')
        key "jobSecretsType": Required[Literal[ClassDiscriminator.DATA_BOX]]
        dc_access_security_code: DcAccessSecurityCode
        error: CloudError
        job_secrets_type: Literal[ClassDiscriminator.DATA_BOX]
        podSecrets: list[DataBoxSecret]
        pod_secrets: list[DataBoxSecret]


    class azure.mgmt.databox.types.DatacenterAddressInstructionResponse(TypedDict, total=False):
        key "communicationInstruction": str
        key "dataCenterAzureLocation": str
        key "datacenterAddressType": Required[Literal[DatacenterAddressType.DATACENTER_ADDRESS_INSTRUCTION]]
        communication_instruction: str
        data_center_azure_location: str
        datacenter_address_type: Literal[DatacenterAddressType.DATACENTER_ADDRESS_INSTRUCTION]
        supportedCarriersForReturnShipment: list[str]
        supported_carriers_for_return_shipment: list[str]


    class azure.mgmt.databox.types.DatacenterAddressLocationResponse(TypedDict, total=False):
        key "additionalShippingInformation": str
        key "addressType": str
        key "city": str
        key "company": str
        key "contactPersonName": str
        key "country": str
        key "dataCenterAzureLocation": str
        key "datacenterAddressType": Required[Literal[DatacenterAddressType.DATACENTER_ADDRESS_LOCATION]]
        key "phone": str
        key "phoneExtension": str
        key "state": str
        key "street1": str
        key "street2": str
        key "street3": str
        key "zip": str
        additional_shipping_information: str
        address_type: str
        city: str
        company: str
        contact_person_name: str
        country: str
        data_center_azure_location: str
        datacenter_address_type: Literal[DatacenterAddressType.DATACENTER_ADDRESS_LOCATION]
        phone: str
        phone_extension: str
        state: str
        street1: str
        street2: str
        street3: str
        supportedCarriersForReturnShipment: list[str]
        supported_carriers_for_return_shipment: list[str]
        zip: str


    class azure.mgmt.databox.types.DatacenterAddressRequest(TypedDict, total=False):
        key "model": Union[str, ModelName]
        key "skuName": Required[Union[str, SkuName]]
        key "storageLocation": Required[str]
        model: Union[str, ModelName]
        sku_name: Union[str, SkuName]
        storage_location: str


    class azure.mgmt.databox.types.DatacenterAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATACENTER_ADDRESS_INSTRUCTION = "DatacenterAddressInstruction"
        DATACENTER_ADDRESS_LOCATION = "DatacenterAddressLocation"


    class azure.mgmt.databox.types.DcAccessSecurityCode(TypedDict, total=False):
        key "forwardDCAccessCode": str
        key "reverseDCAccessCode": str
        forward_dc_access_code: str
        reverse_dc_access_code: str


    class azure.mgmt.databox.types.Details(TypedDict, total=False):
        key "code": Required[str]
        key "message": Required[str]
        code: str
        message: str


    class azure.mgmt.databox.types.DeviceCapabilityDetails(TypedDict, total=False):
        key "hardwareEncryption": Union[str, HardwareEncryption]
        hardware_encryption: Union[str, HardwareEncryption]


    class azure.mgmt.databox.types.DeviceCapabilityRequest(TypedDict, total=False):
        key "model": Union[str, ModelName]
        key "skuName": Union[str, SkuName]
        model: Union[str, ModelName]
        sku_name: Union[str, SkuName]


    class azure.mgmt.databox.types.DeviceCapabilityResponse(TypedDict, total=False):
        deviceCapabilityDetails: list[DeviceCapabilityDetails]
        device_capability_details: list[DeviceCapabilityDetails]


    class azure.mgmt.databox.types.DeviceErasureDetails(TypedDict, total=False):
        key "deviceErasureStatus": Union[str, StageStatus]
        key "erasureOrDestructionCertificateSasKey": str
        key "secureErasureCertificateSasKey": str
        device_erasure_status: Union[str, StageStatus]
        erasure_or_destruction_certificate_sas_key: str
        secure_erasure_certificate_sas_key: str


    class azure.mgmt.databox.types.DiskScheduleAvailabilityRequest(TypedDict, total=False):
        key "country": str
        key "expectedDataSizeInTeraBytes": Required[int]
        key "model": Union[str, ModelName]
        key "skuName": Required[Literal[SkuName.DATA_BOX_DISK]]
        key "storageLocation": Required[str]
        country: str
        expected_data_size_in_tera_bytes: int
        model: Union[str, ModelName]
        sku_name: Literal[SkuName.DATA_BOX_DISK]
        storage_location: str


    class azure.mgmt.databox.types.DiskSecret(TypedDict, total=False):
        key "bitLockerKey": str
        key "diskSerialNumber": str
        bit_locker_key: str
        disk_serial_number: str


    class azure.mgmt.databox.types.EncryptionPreferences(TypedDict, total=False):
        key "doubleEncryption": Union[str, DoubleEncryption]
        key "hardwareEncryption": Union[str, HardwareEncryption]
        double_encryption: Union[str, DoubleEncryption]
        hardware_encryption: Union[str, HardwareEncryption]


    class azure.mgmt.databox.types.ErrorDetail(TypedDict, total=False):
        key "code": Required[str]
        key "message": Required[str]
        key "target": str
        code: str
        details: list[Details]
        message: str
        target: str


    class azure.mgmt.databox.types.ExportDiskDetails(TypedDict, total=False):
        key "backupManifestCloudPath": str
        key "manifestFile": str
        key "manifestHash": str
        backup_manifest_cloud_path: str
        manifest_file: str
        manifest_hash: str


    class azure.mgmt.databox.types.FilterFileDetails(TypedDict, total=False):
        key "filterFilePath": Required[str]
        key "filterFileType": Required[Union[str, FilterFileType]]
        filter_file_path: str
        filter_file_type: Union[str, FilterFileType]


    class azure.mgmt.databox.types.GranularCopyLogDetails(TypedDict, total=False):
        key "accountId": str
        key "copyLogDetailsType": Required[Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]]
        key "errorLogLink": str
        key "serialNumber": str
        key "verboseLogLink": str
        account_id: str
        copy_log_details_type: Literal[ClassDiscriminator.DATA_BOX_CUSTOMER_DISK]
        error_log_link: str
        serial_number: str
        verbose_log_link: str


    class azure.mgmt.databox.types.GranularCopyProgress(TypedDict, total=False):
        key "accountId": str
        key "bytesProcessed": int
        key "dataAccountType": Union[str, DataAccountType]
        key "directoriesErroredOut": int
        key "error": ForwardRef('CloudError', module='types')
        key "filesErroredOut": int
        key "filesProcessed": int
        key "invalidDirectoriesProcessed": int
        key "invalidFileBytesUploaded": int
        key "invalidFilesProcessed": int
        key "isEnumerationInProgress": bool
        key "renamedContainerCount": int
        key "storageAccountName": str
        key "totalBytesToProcess": int
        key "totalFilesToProcess": int
        key "transferType": Union[str, TransferType]
        account_id: str
        actions: list[Union[str, CustomerResolutionCode]]
        bytes_processed: int
        data_account_type: Union[str, DataAccountType]
        directories_errored_out: int
        error: CloudError
        files_errored_out: int
        files_processed: int
        invalid_directories_processed: int
        invalid_file_bytes_uploaded: int
        invalid_files_processed: int
        is_enumeration_in_progress: bool
        renamed_container_count: int
        storage_account_name: str
        total_bytes_to_process: int
        total_files_to_process: int
        transfer_type: Union[str, TransferType]


    class azure.mgmt.databox.types.HeavyScheduleAvailabilityRequest(TypedDict, total=False):
        key "country": str
        key "model": Union[str, ModelName]
        key "skuName": Required[Literal[SkuName.DATA_BOX_HEAVY]]
        key "storageLocation": Required[str]
        country: str
        model: Union[str, ModelName]
        sku_name: Literal[SkuName.DATA_BOX_HEAVY]
        storage_location: str


    class azure.mgmt.databox.types.IdentityProperties(TypedDict, total=False):
        key "type": str
        key "userAssigned": ForwardRef('UserAssignedProperties', module='types')
        type: str
        user_assigned: UserAssignedProperties


    class azure.mgmt.databox.types.ImportDiskDetails(TypedDict, total=False):
        key "backupManifestCloudPath": str
        key "bitLockerKey": Required[str]
        key "manifestFile": Required[str]
        key "manifestHash": Required[str]
        backup_manifest_cloud_path: str
        bit_locker_key: str
        manifest_file: str
        manifest_hash: str


    class azure.mgmt.databox.types.JobDelayDetails(TypedDict, total=False):
        key "description": str
        key "errorCode": Union[str, PortalDelayErrorCode]
        key "resolutionTime": str
        key "startTime": str
        key "status": Union[str, DelayNotificationStatus]
        description: str
        error_code: Union[str, PortalDelayErrorCode]
        resolution_time: str
        start_time: str
        status: Union[str, DelayNotificationStatus]


    class azure.mgmt.databox.types.JobDeliveryInfo(TypedDict, total=False):
        key "scheduledDateTime": str
        scheduled_date_time: str


    class azure.mgmt.databox.types.JobProperties(TypedDict, total=False):
        key "allDevicesLost": bool
        key "cancellationReason": str
        key "delayedStage": Union[str, StageName]
        key "deliveryInfo": ForwardRef('JobDeliveryInfo', module='types')
        key "deliveryType": Union[str, JobDeliveryType]
        key "details": ForwardRef('JobDetails', module='types')
        key "error": ForwardRef('CloudError', module='types')
        key "isCancellable": bool
        key "isCancellableWithoutFee": bool
        key "isDeletable": bool
        key "isPrepareToShipEnabled": bool
        key "isShippingAddressEditable": bool
        key "reverseShippingDetailsUpdate": Union[str, ReverseShippingDetailsEditStatus]
        key "reverseTransportPreferenceUpdate": Union[str, ReverseTransportPreferenceEditStatus]
        key "startTime": str
        key "status": Union[str, StageName]
        key "transferType": Required[Union[str, TransferType]]
        all_devices_lost: bool
        cancellation_reason: str
        delayed_stage: Union[str, StageName]
        delivery_info: JobDeliveryInfo
        delivery_type: Union[str, JobDeliveryType]
        details: JobDetails
        error: CloudError
        is_cancellable: bool
        is_cancellable_without_fee: bool
        is_deletable: bool
        is_prepare_to_ship_enabled: bool
        is_shipping_address_editable: bool
        reverse_shipping_details_update: Union[str, ReverseShippingDetailsEditStatus]
        reverse_transport_preference_update: Union[str, ReverseTransportPreferenceEditStatus]
        start_time: str
        status: Union[str, StageName]
        transfer_type: Union[str, TransferType]


    class azure.mgmt.databox.types.JobResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ResourceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[JobProperties]
        key "sku": Required[Sku]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ResourceIdentity
        location: str
        name: str
        properties: JobProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.databox.types.JobResourceUpdateParameter(TypedDict, total=False):
        key "identity": ForwardRef('ResourceIdentity', module='types')
        key "properties": ForwardRef('UpdateJobProperties', module='types')
        identity: ResourceIdentity
        properties: UpdateJobProperties
        tags: dict[str, str]


    class azure.mgmt.databox.types.JobStages(TypedDict, total=False):
        key "displayName": str
        key "jobStageDetails": Any
        key "stageName": Union[str, StageName]
        key "stageStatus": Union[str, StageStatus]
        key "stageTime": str
        delayInformation: list[JobDelayDetails]
        delay_information: list[JobDelayDetails]
        display_name: str
        job_stage_details: Any
        stage_name: Union[str, StageName]
        stage_status: Union[str, StageStatus]
        stage_time: str


    class azure.mgmt.databox.types.KeyEncryptionKey(TypedDict, total=False):
        key "identityProperties": ForwardRef('IdentityProperties', module='types')
        key "kekType": Required[Union[str, KekType]]
        key "kekUrl": str
        key "kekVaultResourceID": str
        identity_properties: IdentityProperties
        kek_type: Union[str, KekType]
        kek_url: str
        kek_vault_resource_id: str


    class azure.mgmt.databox.types.LastMitigationActionOnJob(TypedDict, total=False):
        key "actionDateTimeInUtc": str
        key "customerResolution": Union[str, CustomerResolutionCode]
        key "isPerformedByCustomer": bool
        action_date_time_in_utc: str
        customer_resolution: Union[str, CustomerResolutionCode]
        is_performed_by_customer: bool


    class azure.mgmt.databox.types.ManagedDiskDetails(TypedDict, total=False):
        key "dataAccountType": Required[Literal[DataAccountType.MANAGED_DISK]]
        key "resourceGroupId": Required[str]
        key "sharePassword": str
        key "stagingStorageAccountId": Required[str]
        data_account_type: Literal[DataAccountType.MANAGED_DISK]
        resource_group_id: str
        share_password: str
        staging_storage_account_id: str


    class azure.mgmt.databox.types.MarkDevicesShippedRequest(TypedDict, total=False):
        key "deliverToDcPackageDetails": Required[PackageCarrierInfo]
        deliver_to_dc_package_details: PackageCarrierInfo


    class azure.mgmt.databox.types.MitigateJobRequest(TypedDict, total=False):
        key "customerResolutionCode": Union[str, CustomerResolutionCode]
        customer_resolution_code: Union[str, CustomerResolutionCode]
        serialNumberCustomerResolutionMap: dict[str, Union[str, CustomerResolutionCode]]
        serial_number_customer_resolution_map: dict[str, Union[str, CustomerResolutionCode]]


    class azure.mgmt.databox.types.NotificationPreference(TypedDict, total=False):
        key "sendNotification": Required[bool]
        key "stageName": Required[Union[str, NotificationStageName]]
        send_notification: bool
        stage_name: Union[str, NotificationStageName]


    class azure.mgmt.databox.types.Operation(TypedDict, total=False):
        key "display": ForwardRef('OperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        key "origin": str
        key "properties": ForwardRef('OperationProperties', module='types')
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: str
        properties: OperationProperties


    class azure.mgmt.databox.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.databox.types.OperationProperties(TypedDict, total=False):


    class azure.mgmt.databox.types.PackageCarrierDetails(TypedDict, total=False):
        key "carrierAccountNumber": str
        key "carrierName": str
        key "trackingId": str
        carrier_account_number: str
        carrier_name: str
        tracking_id: str


    class azure.mgmt.databox.types.PackageCarrierInfo(TypedDict, total=False):
        key "carrierName": str
        key "trackingId": str
        carrier_name: str
        tracking_id: str


    class azure.mgmt.databox.types.PackageShippingDetails(TypedDict, total=False):
        key "carrierName": str
        key "trackingId": str
        key "trackingUrl": str
        carrier_name: str
        tracking_id: str
        tracking_url: str


    class azure.mgmt.databox.types.Preferences(TypedDict, total=False):
        key "encryptionPreferences": ForwardRef('EncryptionPreferences', module='types')
        key "reverseTransportPreferences": ForwardRef('TransportPreferences', module='types')
        key "transportPreferences": ForwardRef('TransportPreferences', module='types')
        encryption_preferences: EncryptionPreferences
        preferredDataCenterRegion: list[str]
        preferred_data_center_region: list[str]
        reverse_transport_preferences: TransportPreferences
        storageAccountAccessTierPreferences: list[Literal["Archive"]]
        storage_account_access_tier_preferences: list[Literal[Archive]]
        transport_preferences: TransportPreferences


    class azure.mgmt.databox.types.PreferencesValidationRequest(TypedDict, total=False):
        key "deviceType": Required[Union[str, SkuName]]
        key "model": Union[str, ModelName]
        key "preference": ForwardRef('Preferences', module='types')
        key "validationType": Required[Literal[ValidationInputDiscriminator.VALIDATE_PREFERENCES]]
        device_type: Union[str, SkuName]
        model: Union[str, ModelName]
        preference: Preferences
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_PREFERENCES]


    class azure.mgmt.databox.types.PreferencesValidationResponseProperties(TypedDict, total=False):
        key "error": ForwardRef('CloudError', module='types')
        key "status": Union[str, ValidationStatus]
        key "validationType": Required[Literal[ValidationInputDiscriminator.VALIDATE_PREFERENCES]]
        error: CloudError
        status: Union[str, ValidationStatus]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_PREFERENCES]


    class azure.mgmt.databox.types.RegionConfigurationRequest(TypedDict, total=False):
        key "datacenterAddressRequest": ForwardRef('DatacenterAddressRequest', module='types')
        key "deviceCapabilityRequest": ForwardRef('DeviceCapabilityRequest', module='types')
        key "scheduleAvailabilityRequest": ForwardRef('ScheduleAvailabilityRequest', module='types')
        key "transportAvailabilityRequest": ForwardRef('TransportAvailabilityRequest', module='types')
        datacenter_address_request: DatacenterAddressRequest
        device_capability_request: DeviceCapabilityRequest
        schedule_availability_request: ScheduleAvailabilityRequest
        transport_availability_request: TransportAvailabilityRequest


    class azure.mgmt.databox.types.RegionConfigurationResponse(TypedDict, total=False):
        key "datacenterAddressResponse": ForwardRef('DatacenterAddressResponse', module='types')
        key "deviceCapabilityResponse": ForwardRef('DeviceCapabilityResponse', module='types')
        key "scheduleAvailabilityResponse": ForwardRef('ScheduleAvailabilityResponse', module='types')
        key "transportAvailabilityResponse": ForwardRef('TransportAvailabilityResponse', module='types')
        datacenter_address_response: DatacenterAddressResponse
        device_capability_response: DeviceCapabilityResponse
        schedule_availability_response: ScheduleAvailabilityResponse
        transport_availability_response: TransportAvailabilityResponse


    class azure.mgmt.databox.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.databox.types.ResourceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": str
        principal_id: str
        tenant_id: str
        type: str
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.databox.types.ReverseShippingDetails(TypedDict, total=False):
        key "contactDetails": ForwardRef('ContactInfo', module='types')
        key "isUpdated": bool
        key "shippingAddress": ForwardRef('ShippingAddress', module='types')
        contact_details: ContactInfo
        is_updated: bool
        shipping_address: ShippingAddress


    class azure.mgmt.databox.types.ScheduleAvailabilityResponse(TypedDict, total=False):
        availableDates: list[str]
        available_dates: list[str]


    class azure.mgmt.databox.types.ShareCredentialDetails(TypedDict, total=False):
        key "password": str
        key "shareName": str
        key "shareType": Union[str, ShareDestinationFormatType]
        key "userName": str
        password: str
        share_name: str
        share_type: Union[str, ShareDestinationFormatType]
        supportedAccessProtocols: list[Union[str, AccessProtocol]]
        supported_access_protocols: list[Union[str, AccessProtocol]]
        user_name: str


    class azure.mgmt.databox.types.ShipmentPickUpRequest(TypedDict, total=False):
        key "endTime": Required[str]
        key "shipmentLocation": Required[str]
        key "startTime": Required[str]
        end_time: str
        shipment_location: str
        start_time: str


    class azure.mgmt.databox.types.ShipmentPickUpResponse(TypedDict, total=False):
        key "confirmationNumber": str
        key "readyByTime": str
        confirmation_number: str
        ready_by_time: str


    class azure.mgmt.databox.types.ShippingAddress(TypedDict, total=False):
        key "addressType": Union[str, AddressType]
        key "city": str
        key "companyName": str
        key "country": Required[str]
        key "postalCode": str
        key "skipAddressValidation": bool
        key "stateOrProvince": str
        key "streetAddress1": Required[str]
        key "streetAddress2": str
        key "streetAddress3": str
        key "taxIdentificationNumber": str
        key "zipExtendedCode": str
        address_type: Union[str, AddressType]
        city: str
        company_name: str
        country: str
        postal_code: str
        skip_address_validation: bool
        state_or_province: str
        street_address1: str
        street_address2: str
        street_address3: str
        tax_identification_number: str
        zip_extended_code: str


    class azure.mgmt.databox.types.Sku(TypedDict, total=False):
        key "displayName": str
        key "family": str
        key "model": Union[str, ModelName]
        key "name": Required[Union[str, SkuName]]
        display_name: str
        family: str
        model: Union[str, ModelName]
        name: Union[str, SkuName]


    class azure.mgmt.databox.types.SkuAvailabilityValidationRequest(TypedDict, total=False):
        key "country": Required[str]
        key "deviceType": Required[Union[str, SkuName]]
        key "location": Required[str]
        key "model": Union[str, ModelName]
        key "transferType": Required[Union[str, TransferType]]
        key "validationType": Required[Literal[ValidationInputDiscriminator.VALIDATE_SKU_AVAILABILITY]]
        country: str
        device_type: Union[str, SkuName]
        location: str
        model: Union[str, ModelName]
        transfer_type: Union[str, TransferType]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_SKU_AVAILABILITY]


    class azure.mgmt.databox.types.SkuAvailabilityValidationResponseProperties(TypedDict, total=False):
        key "error": ForwardRef('CloudError', module='types')
        key "status": Union[str, ValidationStatus]
        key "validationType": Required[Literal[ValidationInputDiscriminator.VALIDATE_SKU_AVAILABILITY]]
        error: CloudError
        status: Union[str, ValidationStatus]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_SKU_AVAILABILITY]


    class azure.mgmt.databox.types.SkuCapacity(TypedDict, total=False):
        key "individualSkuUsable": str
        key "maximum": str
        key "usable": str
        individual_sku_usable: str
        maximum: str
        usable: str


    class azure.mgmt.databox.types.SkuCost(TypedDict, total=False):
        key "meterId": str
        key "meterType": str
        key "multiplier": float
        meter_id: str
        meter_type: str
        multiplier: float


    class azure.mgmt.databox.types.SkuInformation(TypedDict, total=False):
        key "enabled": bool
        key "properties": ForwardRef('SkuProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        enabled: bool
        properties: SkuProperties
        sku: Sku


    class azure.mgmt.databox.types.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_BOX = "DataBox"
        DATA_BOX_CUSTOMER_DISK = "DataBoxCustomerDisk"
        DATA_BOX_DISK = "DataBoxDisk"
        DATA_BOX_HEAVY = "DataBoxHeavy"


    class azure.mgmt.databox.types.SkuProperties(TypedDict, total=False):
        key "capacity": ForwardRef('SkuCapacity', module='types')
        key "disabledReason": Union[str, SkuDisabledReason]
        key "disabledReasonMessage": str
        key "requiredFeature": str
        apiVersions: list[str]
        api_versions: list[str]
        capacity: SkuCapacity
        costs: list[SkuCost]
        countriesWithinCommerceBoundary: list[str]
        countries_within_commerce_boundary: list[str]
        dataLocationToServiceLocationMap: list[DataLocationToServiceLocationMap]
        data_location_to_service_location_map: list[DataLocationToServiceLocationMap]
        disabled_reason: Union[str, SkuDisabledReason]
        disabled_reason_message: str
        required_feature: str


    class azure.mgmt.databox.types.StorageAccountDetails(TypedDict, total=False):
        key "dataAccountType": Required[Literal[DataAccountType.STORAGE_ACCOUNT]]
        key "sharePassword": str
        key "storageAccountId": Required[str]
        data_account_type: Literal[DataAccountType.STORAGE_ACCOUNT]
        share_password: str
        storage_account_id: str


    class azure.mgmt.databox.types.SubscriptionIsAllowedToCreateJobValidationRequest(TypedDict, total=False):
        key "validationType": Required[Literal[ValidationInputDiscriminator.VALIDATE_SUBSCRIPTION_IS_ALLOWED_TO_CREATE_JOB]]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_SUBSCRIPTION_IS_ALLOWED_TO_CREATE_JOB]


    class azure.mgmt.databox.types.SubscriptionIsAllowedToCreateJobValidationResponseProperties(TypedDict, total=False):
        key "error": ForwardRef('CloudError', module='types')
        key "status": Union[str, ValidationStatus]
        key "validationType": Required[Literal[ValidationInputDiscriminator.VALIDATE_SUBSCRIPTION_IS_ALLOWED_TO_CREATE_JOB]]
        error: CloudError
        status: Union[str, ValidationStatus]
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_SUBSCRIPTION_IS_ALLOWED_TO_CREATE_JOB]


    class azure.mgmt.databox.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.databox.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.databox.types.TransferAllDetails(TypedDict, total=False):
        key "dataAccountType": Required[Union[str, DataAccountType]]
        key "transferAllBlobs": bool
        key "transferAllFiles": bool
        data_account_type: Union[str, DataAccountType]
        transfer_all_blobs: bool
        transfer_all_files: bool


    class azure.mgmt.databox.types.TransferConfiguration(TypedDict, total=False):
        key "transferAllDetails": ForwardRef('TransferConfigurationTransferAllDetails', module='types')
        key "transferConfigurationType": Required[Union[str, TransferConfigurationType]]
        key "transferFilterDetails": ForwardRef('TransferConfigurationTransferFilterDetails', module='types')
        transfer_all_details: TransferConfigurationTransferAllDetails
        transfer_configuration_type: Union[str, TransferConfigurationType]
        transfer_filter_details: TransferConfigurationTransferFilterDetails


    class azure.mgmt.databox.types.TransferConfigurationTransferAllDetails(TypedDict, total=False):
        key "include": ForwardRef('TransferAllDetails', module='types')
        include: TransferAllDetails


    class azure.mgmt.databox.types.TransferConfigurationTransferFilterDetails(TypedDict, total=False):
        key "include": ForwardRef('TransferFilterDetails', module='types')
        include: TransferFilterDetails


    class azure.mgmt.databox.types.TransferFilterDetails(TypedDict, total=False):
        key "azureFileFilterDetails": ForwardRef('AzureFileFilterDetails', module='types')
        key "blobFilterDetails": ForwardRef('BlobFilterDetails', module='types')
        key "dataAccountType": Required[Union[str, DataAccountType]]
        azure_file_filter_details: AzureFileFilterDetails
        blob_filter_details: BlobFilterDetails
        data_account_type: Union[str, DataAccountType]
        filterFileDetails: list[FilterFileDetails]
        filter_file_details: list[FilterFileDetails]


    class azure.mgmt.databox.types.TransportAvailabilityDetails(TypedDict, total=False):
        key "shipmentType": Union[str, TransportShipmentTypes]
        shipment_type: Union[str, TransportShipmentTypes]


    class azure.mgmt.databox.types.TransportAvailabilityRequest(TypedDict, total=False):
        key "model": Union[str, ModelName]
        key "skuName": Union[str, SkuName]
        model: Union[str, ModelName]
        sku_name: Union[str, SkuName]


    class azure.mgmt.databox.types.TransportAvailabilityResponse(TypedDict, total=False):
        transportAvailabilityDetails: list[TransportAvailabilityDetails]
        transport_availability_details: list[TransportAvailabilityDetails]


    class azure.mgmt.databox.types.TransportPreferences(TypedDict, total=False):
        key "isUpdated": bool
        key "preferredShipmentType": Required[Union[str, TransportShipmentTypes]]
        is_updated: bool
        preferred_shipment_type: Union[str, TransportShipmentTypes]


    class azure.mgmt.databox.types.UnencryptedCredentials(TypedDict, total=False):
        key "jobName": str
        key "jobSecrets": ForwardRef('JobSecrets', module='types')
        job_name: str
        job_secrets: JobSecrets


    class azure.mgmt.databox.types.UpdateJobDetails(TypedDict, total=False):
        key "contactDetails": ForwardRef('ContactDetails', module='types')
        key "keyEncryptionKey": ForwardRef('KeyEncryptionKey', module='types')
        key "preferences": ForwardRef('Preferences', module='types')
        key "returnToCustomerPackageDetails": ForwardRef('PackageCarrierDetails', module='types')
        key "reverseShippingDetails": ForwardRef('ReverseShippingDetails', module='types')
        key "shippingAddress": ForwardRef('ShippingAddress', module='types')
        contact_details: ContactDetails
        key_encryption_key: KeyEncryptionKey
        preferences: Preferences
        return_to_customer_package_details: PackageCarrierDetails
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress


    class azure.mgmt.databox.types.UpdateJobProperties(TypedDict, total=False):
        key "details": ForwardRef('UpdateJobDetails', module='types')
        details: UpdateJobDetails


    class azure.mgmt.databox.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.databox.types.UserAssignedProperties(TypedDict, total=False):
        key "resourceId": str
        resource_id: str


    class azure.mgmt.databox.types.ValidateAddress(TypedDict, total=False):
        key "deviceType": Required[Union[str, SkuName]]
        key "model": Union[str, ModelName]
        key "shippingAddress": Required[ShippingAddress]
        key "transportPreferences": ForwardRef('TransportPreferences', module='types')
        key "validationType": Required[Literal[ValidationInputDiscriminator.VALIDATE_ADDRESS]]
        device_type: Union[str, SkuName]
        model: Union[str, ModelName]
        shipping_address: ShippingAddress
        transport_preferences: TransportPreferences
        validation_type: Literal[ValidationInputDiscriminator.VALIDATE_ADDRESS]


    class azure.mgmt.databox.types.ValidationInputDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VALIDATE_ADDRESS = "ValidateAddress"
        VALIDATE_CREATE_ORDER_LIMIT = "ValidateCreateOrderLimit"
        VALIDATE_DATA_TRANSFER_DETAILS = "ValidateDataTransferDetails"
        VALIDATE_PREFERENCES = "ValidatePreferences"
        VALIDATE_SKU_AVAILABILITY = "ValidateSkuAvailability"
        VALIDATE_SUBSCRIPTION_IS_ALLOWED_TO_CREATE_JOB = "ValidateSubscriptionIsAllowedToCreateJob"


    class azure.mgmt.databox.types.ValidationRequest(TypedDict, total=False):
        key "individualRequestDetails": Required[list[ValidationInputRequest]]
        key "validationCategory": Required[Literal["JobCreationValidation"]]
        individual_request_details: list[ValidationInputRequest]
        validation_category: Literal[JobCreationValidation]


    class azure.mgmt.databox.types.ValidationResponse(TypedDict, total=False):
        key "properties": ForwardRef('ValidationResponseProperties', module='types')
        properties: ValidationResponseProperties


    class azure.mgmt.databox.types.ValidationResponseProperties(TypedDict, total=False):
        key "status": Union[str, OverallValidationStatus]
        individualResponseDetails: list[ValidationInputResponse]
        individual_response_details: list[ValidationInputResponse]
        status: Union[str, OverallValidationStatus]


```