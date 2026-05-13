```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.databox

    class azure.mgmt.databox.DataBoxManagementClient(DataBoxManagementClientOperationsMixin): implements ContextManager 
        jobs: JobsOperations
        operations: Operations
        service: ServiceOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
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
                mitigate_job_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.mgmt.databox.aio

    class azure.mgmt.databox.aio.DataBoxManagementClient(DataBoxManagementClientOperationsMixin): implements AsyncContextManager 
        jobs: JobsOperations
        operations: Operations
        service: ServiceOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
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
                mitigate_job_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.mgmt.databox.aio.operations

    class azure.mgmt.databox.aio.operations.DataBoxManagementClientOperationsMixin(DataBoxManagementClientMixinABC):

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
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JobResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource_update_parameter: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
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
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> JobResource: ...

        @distributed_trace
        def list(
                self, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[JobResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[JobResource]: ...

        @distributed_trace
        def list_credentials(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[UnencryptedCredentials]: ...

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
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


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
            ) -> AsyncIterable[SkuInformation]: ...

        @overload
        def list_available_skus_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                available_sku_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[SkuInformation]: ...

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
                validation_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...


namespace azure.mgmt.databox.models

    class azure.mgmt.databox.models.AccessProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NFS = "NFS"
        SMB = "SMB"


    class azure.mgmt.databox.models.AccountCredentialDetails(Model):
        account_connection_string: str
        account_name: str
        data_account_type: Union[str, DataAccountType]
        share_credential_details: list[ShareCredentialDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.AdditionalErrorInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                info: Optional[JSON] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.AddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMERCIAL = "Commercial"
        NONE = "None"
        RESIDENTIAL = "Residential"


    class azure.mgmt.databox.models.AddressValidationOutput(Model):
        alternate_addresses: list[ShippingAddress]
        error: CloudError
        validation_status: Union[str, AddressValidationStatus]
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.AddressValidationProperties(ValidationInputResponse):
        alternate_addresses: list[ShippingAddress]
        error: CloudError
        validation_status: Union[str, AddressValidationStatus]
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.AddressValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMBIGUOUS = "Ambiguous"
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.databox.models.ApiError(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: ErrorDetail, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ApplianceNetworkConfiguration(Model):
        mac_address: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ArmBaseObject(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.AvailableSkuRequest(Model):
        country: str
        location: str
        sku_names: Union[list[str, SkuName]]
        transfer_type: Union[str, TransferType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                country: str, 
                location: str, 
                sku_names: Optional[List[Union[str, SkuName]]] = ..., 
                transfer_type: Union[str, TransferType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.AvailableSkusResult(Model):
        next_link: str
        value: list[SkuInformation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.AzureFileFilterDetails(Model):
        file_path_list: list[str]
        file_prefix_list: list[str]
        file_share_list: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                file_path_list: Optional[List[str]] = ..., 
                file_prefix_list: Optional[List[str]] = ..., 
                file_share_list: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.BlobFilterDetails(Model):
        blob_path_list: list[str]
        blob_prefix_list: list[str]
        container_list: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_path_list: Optional[List[str]] = ..., 
                blob_prefix_list: Optional[List[str]] = ..., 
                container_list: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.CancellationReason(Model):
        reason: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reason: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ClassDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_BOX = "DataBox"
        DATA_BOX_CUSTOMER_DISK = "DataBoxCustomerDisk"
        DATA_BOX_DISK = "DataBoxDisk"
        DATA_BOX_HEAVY = "DataBoxHeavy"


    class azure.mgmt.databox.models.CloudError(Model):
        additional_info: list[AdditionalErrorInfo]
        code: str
        details: list[CloudError]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ContactDetails(Model):
        contact_name: str
        email_list: list[str]
        mobile: str
        notification_preference: list[NotificationPreference]
        phone: str
        phone_extension: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_name: str, 
                email_list: List[str], 
                mobile: Optional[str] = ..., 
                notification_preference: Optional[List[NotificationPreference]] = ..., 
                phone: str, 
                phone_extension: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ContactInfo(Model):
        contact_name: str
        mobile: str
        phone: str
        phone_extension: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_name: str, 
                mobile: Optional[str] = ..., 
                phone: str, 
                phone_extension: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.CopyLogDetails(Model):
        copy_log_details_type: Union[str, ClassDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.CopyProgress(Model):
        account_id: str
        actions: Union[list[str, CustomerResolutionCode]]
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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.CreateJobValidations(ValidationRequest):
        individual_request_details: list[ValidationInputRequest]
        validation_category: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                individual_request_details: List[ValidationInputRequest], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.CreateOrderLimitForSubscriptionValidationRequest(ValidationInputRequest):
        device_type: Union[str, SkuName]
        model: Union[str, ModelName]
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                device_type: Union[str, SkuName], 
                model: Optional[Union[str, ModelName]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.CreateOrderLimitForSubscriptionValidationResponseProperties(ValidationInputResponse):
        error: CloudError
        status: Union[str, ValidationStatus]
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.CustomerDiskJobSecrets(JobSecrets):
        carrier_account_number: str
        dc_access_security_code: DcAccessSecurityCode
        disk_secrets: list[DiskSecret]
        error: CloudError
        job_secrets_type: Union[str, ClassDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.CustomerResolutionCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MOVE_TO_CLEAN_UP_DEVICE = "MoveToCleanUpDevice"
        NONE = "None"
        REACH_OUT_TO_OPERATION = "ReachOutToOperation"
        RESTART = "Restart"
        RESUME = "Resume"


    class azure.mgmt.databox.models.DataAccountDetails(Model):
        data_account_type: Union[str, DataAccountType]
        share_password: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                share_password: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_DISK = "ManagedDisk"
        STORAGE_ACCOUNT = "StorageAccount"


    class azure.mgmt.databox.models.DataBoxAccountCopyLogDetails(CopyLogDetails):
        account_name: str
        copy_log_details_type: Union[str, ClassDiscriminator]
        copy_log_link: str
        copy_verbose_log_link: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxCustomerDiskCopyLogDetails(CopyLogDetails):
        copy_log_details_type: Union[str, ClassDiscriminator]
        error_log_link: str
        serial_number: str
        verbose_log_link: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxCustomerDiskCopyProgress(CopyProgress):
        account_id: str
        actions: Union[list[str, CustomerResolutionCode]]
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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxCustomerDiskJobDetails(JobDetails):
        actions: Union[list[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copy_log_details: list[CopyLogDetails]
        copy_progress: list[DataBoxCustomerDiskCopyProgress]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        deliver_to_dc_package_details: PackageCarrierInfo
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        enable_manifest_backup: bool
        expected_data_size_in_tera_bytes: int
        export_disk_details_collection: dict[str, ExportDiskDetails]
        import_disk_details_collection: dict[str, ImportDiskDetails]
        job_details_type: Union[str, ClassDiscriminator]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        preferences: Preferences
        return_package: PackageShippingDetails
        return_to_customer_package_details: PackageCarrierDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_details: ContactDetails, 
                data_export_details: Optional[List[DataExportDetails]] = ..., 
                data_import_details: Optional[List[DataImportDetails]] = ..., 
                enable_manifest_backup: bool = False, 
                expected_data_size_in_tera_bytes: Optional[int] = ..., 
                import_disk_details_collection: Optional[Dict[str, ImportDiskDetails]] = ..., 
                key_encryption_key: Optional[KeyEncryptionKey] = ..., 
                preferences: Optional[Preferences] = ..., 
                return_to_customer_package_details: PackageCarrierDetails, 
                reverse_shipping_details: Optional[ReverseShippingDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxDiskCopyLogDetails(CopyLogDetails):
        copy_log_details_type: Union[str, ClassDiscriminator]
        disk_serial_number: str
        error_log_link: str
        verbose_log_link: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxDiskCopyProgress(Model):
        actions: Union[list[str, CustomerResolutionCode]]
        bytes_copied: int
        error: CloudError
        percent_complete: int
        serial_number: str
        status: Union[str, CopyStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxDiskGranularCopyLogDetails(GranularCopyLogDetails):
        account_id: str
        copy_log_details_type: Union[str, ClassDiscriminator]
        error_log_link: str
        serial_number: str
        verbose_log_link: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxDiskGranularCopyProgress(GranularCopyProgress):
        account_id: str
        actions: Union[list[str, CustomerResolutionCode]]
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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxDiskJobDetails(JobDetails):
        actions: Union[list[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copy_log_details: list[CopyLogDetails]
        copy_progress: list[DataBoxDiskCopyProgress]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        disks_and_size_details: dict[str, int]
        expected_data_size_in_tera_bytes: int
        granular_copy_log_details: list[DataBoxDiskGranularCopyLogDetails]
        granular_copy_progress: list[DataBoxDiskGranularCopyProgress]
        job_details_type: Union[str, ClassDiscriminator]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        passkey: str
        preferences: Preferences
        preferred_disks: dict[str, int]
        return_package: PackageShippingDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_details: ContactDetails, 
                data_export_details: Optional[List[DataExportDetails]] = ..., 
                data_import_details: Optional[List[DataImportDetails]] = ..., 
                expected_data_size_in_tera_bytes: Optional[int] = ..., 
                key_encryption_key: Optional[KeyEncryptionKey] = ..., 
                passkey: Optional[str] = ..., 
                preferences: Optional[Preferences] = ..., 
                preferred_disks: Optional[Dict[str, int]] = ..., 
                reverse_shipping_details: Optional[ReverseShippingDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxDiskJobSecrets(JobSecrets):
        dc_access_security_code: DcAccessSecurityCode
        disk_secrets: list[DiskSecret]
        error: CloudError
        is_passkey_user_defined: bool
        job_secrets_type: Union[str, ClassDiscriminator]
        pass_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxHeavyAccountCopyLogDetails(CopyLogDetails):
        account_name: str
        copy_log_details_type: Union[str, ClassDiscriminator]
        copy_log_link: list[str]
        copy_verbose_log_link: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxHeavyJobDetails(JobDetails):
        actions: Union[list[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copy_log_details: list[CopyLogDetails]
        copy_progress: list[CopyProgress]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        device_password: str
        expected_data_size_in_tera_bytes: int
        job_details_type: Union[str, ClassDiscriminator]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        preferences: Preferences
        return_package: PackageShippingDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_details: ContactDetails, 
                data_export_details: Optional[List[DataExportDetails]] = ..., 
                data_import_details: Optional[List[DataImportDetails]] = ..., 
                device_password: Optional[str] = ..., 
                expected_data_size_in_tera_bytes: Optional[int] = ..., 
                key_encryption_key: Optional[KeyEncryptionKey] = ..., 
                preferences: Optional[Preferences] = ..., 
                reverse_shipping_details: Optional[ReverseShippingDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxHeavyJobSecrets(JobSecrets):
        cabinet_pod_secrets: list[DataBoxHeavySecret]
        dc_access_security_code: DcAccessSecurityCode
        error: CloudError
        job_secrets_type: Union[str, ClassDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxHeavySecret(Model):
        account_credential_details: list[AccountCredentialDetails]
        device_password: str
        device_serial_number: str
        encoded_validation_cert_pub_key: str
        network_configurations: list[ApplianceNetworkConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxJobDetails(JobDetails):
        actions: Union[list[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copy_log_details: list[CopyLogDetails]
        copy_progress: list[CopyProgress]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        device_password: str
        expected_data_size_in_tera_bytes: int
        job_details_type: Union[str, ClassDiscriminator]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        preferences: Preferences
        return_package: PackageShippingDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_details: ContactDetails, 
                data_export_details: Optional[List[DataExportDetails]] = ..., 
                data_import_details: Optional[List[DataImportDetails]] = ..., 
                device_password: Optional[str] = ..., 
                expected_data_size_in_tera_bytes: Optional[int] = ..., 
                key_encryption_key: Optional[KeyEncryptionKey] = ..., 
                preferences: Optional[Preferences] = ..., 
                reverse_shipping_details: Optional[ReverseShippingDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxScheduleAvailabilityRequest(ScheduleAvailabilityRequest):
        country: str
        model: Union[str, ModelName]
        sku_name: Union[str, SkuName]
        storage_location: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                country: Optional[str] = ..., 
                model: Optional[Union[str, ModelName]] = ..., 
                storage_location: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataBoxSecret(Model):
        account_credential_details: list[AccountCredentialDetails]
        device_password: str
        device_serial_number: str
        encoded_validation_cert_pub_key: str
        network_configurations: list[ApplianceNetworkConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataExportDetails(Model):
        account_details: DataAccountDetails
        log_collection_level: Union[str, LogCollectionLevel]
        transfer_configuration: TransferConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_details: DataAccountDetails, 
                log_collection_level: Optional[Union[str, LogCollectionLevel]] = ..., 
                transfer_configuration: TransferConfiguration, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataImportDetails(Model):
        account_details: DataAccountDetails
        log_collection_level: Union[str, LogCollectionLevel]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_details: DataAccountDetails, 
                log_collection_level: Optional[Union[str, LogCollectionLevel]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataLocationToServiceLocationMap(Model):
        data_location: str
        service_location: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataTransferDetailsValidationRequest(ValidationInputRequest):
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        device_type: Union[str, SkuName]
        model: Union[str, ModelName]
        transfer_type: Union[str, TransferType]
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_export_details: Optional[List[DataExportDetails]] = ..., 
                data_import_details: Optional[List[DataImportDetails]] = ..., 
                device_type: Union[str, SkuName], 
                model: Optional[Union[str, ModelName]] = ..., 
                transfer_type: Union[str, TransferType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataTransferDetailsValidationResponseProperties(ValidationInputResponse):
        error: CloudError
        status: Union[str, ValidationStatus]
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DataboxJobSecrets(JobSecrets):
        dc_access_security_code: DcAccessSecurityCode
        error: CloudError
        job_secrets_type: Union[str, ClassDiscriminator]
        pod_secrets: list[DataBoxSecret]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                pod_secrets: Optional[List[DataBoxSecret]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DatacenterAddressInstructionResponse(DatacenterAddressResponse):
        communication_instruction: str
        data_center_azure_location: str
        datacenter_address_type: Union[str, DatacenterAddressType]
        supported_carriers_for_return_shipment: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DatacenterAddressLocationResponse(DatacenterAddressResponse):
        additional_shipping_information: str
        address_type: str
        city: str
        company: str
        contact_person_name: str
        country: str
        data_center_azure_location: str
        datacenter_address_type: Union[str, DatacenterAddressType]
        phone: str
        phone_extension: str
        state: str
        street1: str
        street2: str
        street3: str
        supported_carriers_for_return_shipment: list[str]
        zip: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DatacenterAddressRequest(Model):
        model: Union[str, ModelName]
        sku_name: Union[str, SkuName]
        storage_location: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                model: Optional[Union[str, ModelName]] = ..., 
                sku_name: Union[str, SkuName], 
                storage_location: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DatacenterAddressResponse(Model):
        data_center_azure_location: str
        datacenter_address_type: Union[str, DatacenterAddressType]
        supported_carriers_for_return_shipment: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DatacenterAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATACENTER_ADDRESS_INSTRUCTION = "DatacenterAddressInstruction"
        DATACENTER_ADDRESS_LOCATION = "DatacenterAddressLocation"


    class azure.mgmt.databox.models.DcAccessSecurityCode(Model):
        forward_dc_access_code: str
        reverse_dc_access_code: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                forward_dc_access_code: Optional[str] = ..., 
                reverse_dc_access_code: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DelayNotificationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        RESOLVED = "Resolved"


    class azure.mgmt.databox.models.Details(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: str, 
                message: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DeviceCapabilityDetails(Model):
        hardware_encryption: Union[str, HardwareEncryption]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DeviceCapabilityRequest(Model):
        model: Union[str, ModelName]
        sku_name: Union[str, SkuName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                model: Optional[Union[str, ModelName]] = ..., 
                sku_name: Optional[Union[str, SkuName]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DeviceCapabilityResponse(Model):
        device_capability_details: list[DeviceCapabilityDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DeviceErasureDetails(Model):
        device_erasure_status: Union[str, StageStatus]
        erasure_or_destruction_certificate_sas_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DiskScheduleAvailabilityRequest(ScheduleAvailabilityRequest):
        country: str
        expected_data_size_in_tera_bytes: int
        model: Union[str, ModelName]
        sku_name: Union[str, SkuName]
        storage_location: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                country: Optional[str] = ..., 
                expected_data_size_in_tera_bytes: int, 
                model: Optional[Union[str, ModelName]] = ..., 
                storage_location: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DiskSecret(Model):
        bit_locker_key: str
        disk_serial_number: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.DoubleEncryption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databox.models.EncryptionPreferences(Model):
        double_encryption: Union[str, DoubleEncryption]
        hardware_encryption: Union[str, HardwareEncryption]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                double_encryption: Union[str, DoubleEncryption] = "Disabled", 
                hardware_encryption: Optional[Union[str, HardwareEncryption]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ErrorDetail(Model):
        code: str
        details: list[Details]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[List[Details]] = ..., 
                message: str, 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ExportDiskDetails(Model):
        backup_manifest_cloud_path: str
        manifest_file: str
        manifest_hash: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.FilterFileDetails(Model):
        filter_file_path: str
        filter_file_type: Union[str, FilterFileType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                filter_file_path: str, 
                filter_file_type: Union[str, FilterFileType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.FilterFileType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "AzureBlob"
        AZURE_FILE = "AzureFile"


    class azure.mgmt.databox.models.GranularCopyLogDetails(Model):
        copy_log_details_type: Union[str, ClassDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.GranularCopyProgress(Model):
        account_id: str
        actions: Union[list[str, CustomerResolutionCode]]
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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.HardwareEncryption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.databox.models.HeavyScheduleAvailabilityRequest(ScheduleAvailabilityRequest):
        country: str
        model: Union[str, ModelName]
        sku_name: Union[str, SkuName]
        storage_location: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                country: Optional[str] = ..., 
                model: Optional[Union[str, ModelName]] = ..., 
                storage_location: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.IdentityProperties(Model):
        type: str
        user_assigned: UserAssignedProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[str] = ..., 
                user_assigned: Optional[UserAssignedProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ImportDiskDetails(Model):
        backup_manifest_cloud_path: str
        bit_locker_key: str
        manifest_file: str
        manifest_hash: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bit_locker_key: str, 
                manifest_file: str, 
                manifest_hash: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.JobDelayDetails(Model):
        description: str
        error_code: Union[str, PortalDelayErrorCode]
        resolution_time: datetime
        start_time: datetime
        status: Union[str, DelayNotificationStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.JobDeliveryInfo(Model):
        scheduled_date_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scheduled_date_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.JobDeliveryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NON_SCHEDULED = "NonScheduled"
        SCHEDULED = "Scheduled"


    class azure.mgmt.databox.models.JobDetails(Model):
        actions: Union[list[str, CustomerResolutionCode]]
        chain_of_custody_sas_key: str
        contact_details: ContactDetails
        copy_log_details: list[CopyLogDetails]
        data_center_code: Union[str, DataCenterCode]
        data_export_details: list[DataExportDetails]
        data_import_details: list[DataImportDetails]
        datacenter_address: DatacenterAddressResponse
        delivery_package: PackageShippingDetails
        device_erasure_details: DeviceErasureDetails
        expected_data_size_in_tera_bytes: int
        job_details_type: Union[str, ClassDiscriminator]
        job_stages: list[JobStages]
        key_encryption_key: KeyEncryptionKey
        last_mitigation_action_on_job: LastMitigationActionOnJob
        preferences: Preferences
        return_package: PackageShippingDetails
        reverse_shipment_label_sas_key: str
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_details: ContactDetails, 
                data_export_details: Optional[List[DataExportDetails]] = ..., 
                data_import_details: Optional[List[DataImportDetails]] = ..., 
                expected_data_size_in_tera_bytes: Optional[int] = ..., 
                key_encryption_key: Optional[KeyEncryptionKey] = ..., 
                preferences: Optional[Preferences] = ..., 
                reverse_shipping_details: Optional[ReverseShippingDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.JobResource(Resource):
        all_devices_lost: bool
        cancellation_reason: str
        delayed_stage: Union[str, StageName]
        delivery_info: JobDeliveryInfo
        delivery_type: Union[str, JobDeliveryType]
        details: JobDetails
        error: CloudError
        id: str
        identity: ResourceIdentity
        is_cancellable: bool
        is_cancellable_without_fee: bool
        is_deletable: bool
        is_prepare_to_ship_enabled: bool
        is_shipping_address_editable: bool
        location: str
        name: str
        reverse_shipping_details_update: Union[str, ReverseShippingDetailsEditStatus]
        reverse_transport_preference_update: Union[str, ReverseTransportPreferenceEditStatus]
        sku: Sku
        start_time: datetime
        status: Union[str, StageName]
        system_data: SystemData
        tags: dict[str, str]
        transfer_type: Union[str, TransferType]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delivery_info: Optional[JobDeliveryInfo] = ..., 
                delivery_type: Union[str, JobDeliveryType] = "NonScheduled", 
                details: Optional[JobDetails] = ..., 
                identity: Optional[ResourceIdentity] = ..., 
                location: str, 
                sku: Sku, 
                tags: Optional[Dict[str, str]] = ..., 
                transfer_type: Union[str, TransferType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.JobResourceList(Model):
        next_link: str
        value: list[JobResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[JobResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.JobResourceUpdateParameter(Model):
        details: UpdateJobDetails
        identity: ResourceIdentity
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                details: Optional[UpdateJobDetails] = ..., 
                identity: Optional[ResourceIdentity] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.JobSecrets(Model):
        dc_access_security_code: DcAccessSecurityCode
        error: CloudError
        job_secrets_type: Union[str, ClassDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.JobStages(Model):
        delay_information: list[JobDelayDetails]
        display_name: str
        job_stage_details: JSON
        stage_name: Union[str, StageName]
        stage_status: Union[str, StageStatus]
        stage_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.KekType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_MANAGED = "CustomerManaged"
        MICROSOFT_MANAGED = "MicrosoftManaged"


    class azure.mgmt.databox.models.KeyEncryptionKey(Model):
        identity_properties: IdentityProperties
        kek_type: Union[str, KekType]
        kek_url: str
        kek_vault_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity_properties: Optional[IdentityProperties] = ..., 
                kek_type: Union[str, KekType] = "MicrosoftManaged", 
                kek_url: Optional[str] = ..., 
                kek_vault_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.LastMitigationActionOnJob(Model):
        action_date_time_in_utc: datetime
        customer_resolution: Union[str, CustomerResolutionCode]
        is_performed_by_customer: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_date_time_in_utc: Optional[datetime] = ..., 
                customer_resolution: Optional[Union[str, CustomerResolutionCode]] = ..., 
                is_performed_by_customer: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.LogCollectionLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        VERBOSE = "Verbose"


    class azure.mgmt.databox.models.ManagedDiskDetails(DataAccountDetails):
        data_account_type: Union[str, DataAccountType]
        resource_group_id: str
        share_password: str
        staging_storage_account_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_group_id: str, 
                share_password: Optional[str] = ..., 
                staging_storage_account_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.MarkDevicesShippedRequest(Model):
        deliver_to_dc_package_details: PackageCarrierInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                deliver_to_dc_package_details: PackageCarrierInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.MitigateJobRequest(Model):
        customer_resolution_code: Union[str, CustomerResolutionCode]
        serial_number_customer_resolution_map: Union[dict[str, str, CustomerResolutionCode]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                customer_resolution_code: Optional[Union[str, CustomerResolutionCode]] = ..., 
                serial_number_customer_resolution_map: Optional[Dict[str, Union[str, CustomerResolutionCode]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ModelName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DATA_BOX120 = "AzureDataBox120"
        AZURE_DATA_BOX525 = "AzureDataBox525"
        DATA_BOX = "DataBox"
        DATA_BOX_CUSTOMER_DISK = "DataBoxCustomerDisk"
        DATA_BOX_DISK = "DataBoxDisk"
        DATA_BOX_HEAVY = "DataBoxHeavy"


    class azure.mgmt.databox.models.NotificationPreference(Model):
        send_notification: bool
        stage_name: Union[str, NotificationStageName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                send_notification: bool = True, 
                stage_name: Union[str, NotificationStageName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.NotificationStageName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AT_AZURE_DC = "AtAzureDC"
        CREATED = "Created"
        DATA_COPY = "DataCopy"
        DELIVERED = "Delivered"
        DEVICE_PREPARED = "DevicePrepared"
        DISPATCHED = "Dispatched"
        PICKED_UP = "PickedUp"
        SHIPPED_TO_CUSTOMER = "ShippedToCustomer"


    class azure.mgmt.databox.models.Operation(Model):
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: str
        properties: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_data_action: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.OperationList(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.OverallValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_VALID_TO_PROCEED = "AllValidToProceed"
        CERTAIN_INPUT_VALIDATIONS_SKIPPED = "CertainInputValidationsSkipped"
        INPUTS_REVISIT_REQUIRED = "InputsRevisitRequired"


    class azure.mgmt.databox.models.PackageCarrierDetails(Model):
        carrier_account_number: str
        carrier_name: str
        tracking_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                carrier_account_number: Optional[str] = ..., 
                carrier_name: Optional[str] = ..., 
                tracking_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.PackageCarrierInfo(Model):
        carrier_name: str
        tracking_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                carrier_name: Optional[str] = ..., 
                tracking_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.PackageShippingDetails(Model):
        carrier_name: str
        tracking_id: str
        tracking_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.PortalDelayErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_ORDER_LIMIT_BREACHED_DELAY = "ActiveOrderLimitBreachedDelay"
        HIGH_DEMAND_DELAY = "HighDemandDelay"
        INTERNAL_ISSUE_DELAY = "InternalIssueDelay"
        LARGE_NUMBER_OF_FILES_DELAY = "LargeNumberOfFilesDelay"


    class azure.mgmt.databox.models.Preferences(Model):
        encryption_preferences: EncryptionPreferences
        preferred_data_center_region: list[str]
        reverse_transport_preferences: TransportPreferences
        storage_account_access_tier_preferences: list[str]
        transport_preferences: TransportPreferences

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encryption_preferences: Optional[EncryptionPreferences] = ..., 
                preferred_data_center_region: Optional[List[str]] = ..., 
                reverse_transport_preferences: Optional[TransportPreferences] = ..., 
                storage_account_access_tier_preferences: Optional[List[Literal[Archive]]] = ..., 
                transport_preferences: Optional[TransportPreferences] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.PreferencesValidationRequest(ValidationInputRequest):
        device_type: Union[str, SkuName]
        model: Union[str, ModelName]
        preference: Preferences
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                device_type: Union[str, SkuName], 
                model: Optional[Union[str, ModelName]] = ..., 
                preference: Optional[Preferences] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.PreferencesValidationResponseProperties(ValidationInputResponse):
        error: CloudError
        status: Union[str, ValidationStatus]
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.RegionConfigurationRequest(Model):
        datacenter_address_request: DatacenterAddressRequest
        device_capability_request: DeviceCapabilityRequest
        schedule_availability_request: ScheduleAvailabilityRequest
        transport_availability_request: TransportAvailabilityRequest

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                datacenter_address_request: Optional[DatacenterAddressRequest] = ..., 
                device_capability_request: Optional[DeviceCapabilityRequest] = ..., 
                schedule_availability_request: Optional[ScheduleAvailabilityRequest] = ..., 
                transport_availability_request: Optional[TransportAvailabilityRequest] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.RegionConfigurationResponse(Model):
        datacenter_address_response: DatacenterAddressResponse
        device_capability_response: DeviceCapabilityResponse
        schedule_availability_response: ScheduleAvailabilityResponse
        transport_availability_response: TransportAvailabilityResponse

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.Resource(Model):
        identity: ResourceIdentity
        location: str
        sku: Sku
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ResourceIdentity] = ..., 
                location: str, 
                sku: Sku, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ResourceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: str
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: str = None, 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ReverseShippingDetails(Model):
        contact_details: ContactInfo
        is_updated: bool
        shipping_address: ShippingAddress

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_details: Optional[ContactInfo] = ..., 
                shipping_address: Optional[ShippingAddress] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ReverseShippingDetailsEditStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_SUPPORTED = "NotSupported"


    class azure.mgmt.databox.models.ReverseTransportPreferenceEditStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_SUPPORTED = "NotSupported"


    class azure.mgmt.databox.models.ScheduleAvailabilityRequest(Model):
        country: str
        model: Union[str, ModelName]
        sku_name: Union[str, SkuName]
        storage_location: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                country: Optional[str] = ..., 
                model: Optional[Union[str, ModelName]] = ..., 
                storage_location: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ScheduleAvailabilityResponse(Model):
        available_dates: list[datetime]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ShareCredentialDetails(Model):
        password: str
        share_name: str
        share_type: Union[str, ShareDestinationFormatType]
        supported_access_protocols: Union[list[str, AccessProtocol]]
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ShareDestinationFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FILE = "AzureFile"
        BLOCK_BLOB = "BlockBlob"
        HCS = "HCS"
        MANAGED_DISK = "ManagedDisk"
        PAGE_BLOB = "PageBlob"
        UNKNOWN_TYPE = "UnknownType"


    class azure.mgmt.databox.models.ShipmentPickUpRequest(Model):
        end_time: datetime
        shipment_location: str
        start_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: datetime, 
                shipment_location: str, 
                start_time: datetime, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ShipmentPickUpResponse(Model):
        confirmation_number: str
        ready_by_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ShippingAddress(Model):
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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address_type: Union[str, AddressType] = None, 
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
                zip_extended_code: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.Sku(Model):
        display_name: str
        family: str
        model: Union[str, ModelName]
        name: Union[str, SkuName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                family: Optional[str] = ..., 
                model: Optional[Union[str, ModelName]] = ..., 
                name: Union[str, SkuName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.SkuAvailabilityValidationRequest(ValidationInputRequest):
        country: str
        device_type: Union[str, SkuName]
        location: str
        model: Union[str, ModelName]
        transfer_type: Union[str, TransferType]
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                country: str, 
                device_type: Union[str, SkuName], 
                location: str, 
                model: Optional[Union[str, ModelName]] = ..., 
                transfer_type: Union[str, TransferType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.SkuAvailabilityValidationResponseProperties(ValidationInputResponse):
        error: CloudError
        status: Union[str, ValidationStatus]
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.SkuCapacity(Model):
        individual_sku_usable: str
        maximum: str
        usable: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.SkuCost(Model):
        meter_id: str
        meter_type: str
        multiplier: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.SkuDisabledReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNTRY = "Country"
        FEATURE = "Feature"
        NONE = "None"
        NO_SUBSCRIPTION_INFO = "NoSubscriptionInfo"
        OFFER_TYPE = "OfferType"
        REGION = "Region"


    class azure.mgmt.databox.models.SkuInformation(Model):
        api_versions: list[str]
        capacity: SkuCapacity
        costs: list[SkuCost]
        countries_within_commerce_boundary: list[str]
        data_location_to_service_location_map: list[DataLocationToServiceLocationMap]
        disabled_reason: Union[str, SkuDisabledReason]
        disabled_reason_message: str
        enabled: bool
        required_feature: str
        sku: Sku

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_BOX = "DataBox"
        DATA_BOX_CUSTOMER_DISK = "DataBoxCustomerDisk"
        DATA_BOX_DISK = "DataBoxDisk"
        DATA_BOX_HEAVY = "DataBoxHeavy"


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


    class azure.mgmt.databox.models.StorageAccountDetails(DataAccountDetails):
        data_account_type: Union[str, DataAccountType]
        share_password: str
        storage_account_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                share_password: Optional[str] = ..., 
                storage_account_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.SubscriptionIsAllowedToCreateJobValidationRequest(ValidationInputRequest):
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.SubscriptionIsAllowedToCreateJobValidationResponseProperties(ValidationInputResponse):
        error: CloudError
        status: Union[str, ValidationStatus]
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: str
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.TransferAllDetails(Model):
        data_account_type: Union[str, DataAccountType]
        transfer_all_blobs: bool
        transfer_all_files: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_account_type: Union[str, DataAccountType], 
                transfer_all_blobs: Optional[bool] = ..., 
                transfer_all_files: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.TransferConfiguration(Model):
        transfer_all_details: TransferConfigurationTransferAllDetails
        transfer_configuration_type: Union[str, TransferConfigurationType]
        transfer_filter_details: TransferConfigurationTransferFilterDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                transfer_all_details: Optional[TransferConfigurationTransferAllDetails] = ..., 
                transfer_configuration_type: Union[str, TransferConfigurationType], 
                transfer_filter_details: Optional[TransferConfigurationTransferFilterDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.TransferConfigurationTransferAllDetails(Model):
        include: TransferAllDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                include: Optional[TransferAllDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.TransferConfigurationTransferFilterDetails(Model):
        include: TransferFilterDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                include: Optional[TransferFilterDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.TransferConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TRANSFER_ALL = "TransferAll"
        TRANSFER_USING_FILTER = "TransferUsingFilter"


    class azure.mgmt.databox.models.TransferFilterDetails(Model):
        azure_file_filter_details: AzureFileFilterDetails
        blob_filter_details: BlobFilterDetails
        data_account_type: Union[str, DataAccountType]
        filter_file_details: list[FilterFileDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_file_filter_details: Optional[AzureFileFilterDetails] = ..., 
                blob_filter_details: Optional[BlobFilterDetails] = ..., 
                data_account_type: Union[str, DataAccountType], 
                filter_file_details: Optional[List[FilterFileDetails]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.TransferType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPORT_FROM_AZURE = "ExportFromAzure"
        IMPORT_TO_AZURE = "ImportToAzure"


    class azure.mgmt.databox.models.TransportAvailabilityDetails(Model):
        shipment_type: Union[str, TransportShipmentTypes]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.TransportAvailabilityRequest(Model):
        model: Union[str, ModelName]
        sku_name: Union[str, SkuName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                model: Optional[Union[str, ModelName]] = ..., 
                sku_name: Optional[Union[str, SkuName]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.TransportAvailabilityResponse(Model):
        transport_availability_details: list[TransportAvailabilityDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.TransportPreferences(Model):
        is_updated: bool
        preferred_shipment_type: Union[str, TransportShipmentTypes]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                preferred_shipment_type: Union[str, TransportShipmentTypes], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.TransportShipmentTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_MANAGED = "CustomerManaged"
        MICROSOFT_MANAGED = "MicrosoftManaged"


    class azure.mgmt.databox.models.UnencryptedCredentials(Model):
        job_name: str
        job_secrets: JobSecrets

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.UnencryptedCredentialsList(Model):
        next_link: str
        value: list[UnencryptedCredentials]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[UnencryptedCredentials]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.UpdateJobDetails(Model):
        contact_details: ContactDetails
        key_encryption_key: KeyEncryptionKey
        preferences: Preferences
        return_to_customer_package_details: PackageCarrierDetails
        reverse_shipping_details: ReverseShippingDetails
        shipping_address: ShippingAddress

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contact_details: Optional[ContactDetails] = ..., 
                key_encryption_key: Optional[KeyEncryptionKey] = ..., 
                preferences: Optional[Preferences] = ..., 
                return_to_customer_package_details: Optional[PackageCarrierDetails] = ..., 
                reverse_shipping_details: Optional[ReverseShippingDetails] = ..., 
                shipping_address: Optional[ShippingAddress] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.UserAssignedIdentity(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.UserAssignedProperties(Model):
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ValidateAddress(ValidationInputRequest):
        device_type: Union[str, SkuName]
        model: Union[str, ModelName]
        shipping_address: ShippingAddress
        transport_preferences: TransportPreferences
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                device_type: Union[str, SkuName], 
                model: Optional[Union[str, ModelName]] = ..., 
                shipping_address: ShippingAddress, 
                transport_preferences: Optional[TransportPreferences] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ValidationInputDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VALIDATE_ADDRESS = "ValidateAddress"
        VALIDATE_CREATE_ORDER_LIMIT = "ValidateCreateOrderLimit"
        VALIDATE_DATA_TRANSFER_DETAILS = "ValidateDataTransferDetails"
        VALIDATE_PREFERENCES = "ValidatePreferences"
        VALIDATE_SKU_AVAILABILITY = "ValidateSkuAvailability"
        VALIDATE_SUBSCRIPTION_IS_ALLOWED_TO_CREATE_JOB = "ValidateSubscriptionIsAllowedToCreateJob"


    class azure.mgmt.databox.models.ValidationInputRequest(Model):
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ValidationInputResponse(Model):
        error: CloudError
        validation_type: Union[str, ValidationInputDiscriminator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ValidationRequest(Model):
        individual_request_details: list[ValidationInputRequest]
        validation_category: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                individual_request_details: List[ValidationInputRequest], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ValidationResponse(Model):
        individual_response_details: list[ValidationInputResponse]
        status: Union[str, OverallValidationStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

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


    class azure.mgmt.databox.models.ValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        SKIPPED = "Skipped"
        VALID = "Valid"


namespace azure.mgmt.databox.operations

    class azure.mgmt.databox.operations.DataBoxManagementClientOperationsMixin(DataBoxManagementClientMixinABC):

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


    class azure.mgmt.databox.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JobResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_resource_update_parameter: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
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
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> JobResource: ...

        @distributed_trace
        def list(
                self, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[JobResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                skip_token: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[JobResource]: ...

        @distributed_trace
        def list_credentials(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> Iterable[UnencryptedCredentials]: ...

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
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.databox.operations.ServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def list_available_skus_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                available_sku_request: AvailableSkuRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[SkuInformation]: ...

        @overload
        def list_available_skus_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                available_sku_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[SkuInformation]: ...

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
                validation_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidationResponse: ...


```