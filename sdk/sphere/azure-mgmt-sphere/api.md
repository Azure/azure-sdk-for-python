```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.sphere

    class azure.mgmt.sphere.AzureSphereMgmtClient: implements ContextManager 
        catalogs: CatalogsOperations
        certificates: CertificatesOperations
        deployments: DeploymentsOperations
        device_groups: DeviceGroupsOperations
        devices: DevicesOperations
        images: ImagesOperations
        operations: Operations
        products: ProductsOperations

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


namespace azure.mgmt.sphere.aio

    class azure.mgmt.sphere.aio.AzureSphereMgmtClient: implements AsyncContextManager 
        catalogs: CatalogsOperations
        certificates: CertificatesOperations
        deployments: DeploymentsOperations
        device_groups: DeviceGroupsOperations
        devices: DevicesOperations
        images: ImagesOperations
        operations: Operations
        products: ProductsOperations

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


namespace azure.mgmt.sphere.aio.operations

    class azure.mgmt.sphere.aio.operations.CatalogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                resource: Catalog, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Catalog]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Catalog]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upload_image(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                upload_image_request: Image, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upload_image(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                upload_image_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def count_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> CountDevicesResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> Catalog: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Catalog]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[Catalog]: ...

        @distributed_trace
        def list_deployments(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Deployment]: ...

        @overload
        def list_device_groups(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                list_device_groups_request: ListDeviceGroupsRequest, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[DeviceGroup]: ...

        @overload
        def list_device_groups(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                list_device_groups_request: IO[bytes], 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[DeviceGroup]: ...

        @distributed_trace
        def list_device_insights(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DeviceInsight]: ...

        @distributed_trace
        def list_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Device]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                properties: CatalogUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Catalog: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Catalog: ...


    class azure.mgmt.sphere.aio.operations.CertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                serial_number: str, 
                **kwargs: Any
            ) -> Certificate: ...

        @distributed_trace
        def list_by_catalog(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Certificate]: ...

        @distributed_trace_async
        async def retrieve_cert_chain(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                serial_number: str, 
                **kwargs: Any
            ) -> CertificateChainResponse: ...

        @overload
        async def retrieve_proof_of_possession_nonce(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                serial_number: str, 
                proof_of_possession_nonce_request: ProofOfPossessionNonceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProofOfPossessionNonceResponse: ...

        @overload
        async def retrieve_proof_of_possession_nonce(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                serial_number: str, 
                proof_of_possession_nonce_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProofOfPossessionNonceResponse: ...


    class azure.mgmt.sphere.aio.operations.DeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                deployment_name: str, 
                resource: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Deployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                deployment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Deployment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace
        def list_by_device_group(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Deployment]: ...


    class azure.mgmt.sphere.aio.operations.DeviceGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_claim_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                claim_devices_request: ClaimDevicesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_claim_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                claim_devices_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                resource: DeviceGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeviceGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeviceGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                properties: DeviceGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeviceGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeviceGroup]: ...

        @distributed_trace_async
        async def count_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                **kwargs: Any
            ) -> CountDevicesResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                **kwargs: Any
            ) -> DeviceGroup: ...

        @distributed_trace
        def list_by_product(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DeviceGroup]: ...


    class azure.mgmt.sphere.aio.operations.DevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                resource: Device, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Device]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Device]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_generate_capability_image(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                generate_device_capability_request: GenerateCapabilityImageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignedCapabilityImageResponse]: ...

        @overload
        async def begin_generate_capability_image(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                generate_device_capability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignedCapabilityImageResponse]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                properties: DeviceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Device]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Device]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                **kwargs: Any
            ) -> Device: ...

        @distributed_trace
        def list_by_device_group(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Device]: ...


    class azure.mgmt.sphere.aio.operations.ImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                image_name: str, 
                resource: Image, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Image]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                image_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Image]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def list_by_catalog(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Image]: ...


    class azure.mgmt.sphere.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.sphere.aio.operations.ProductsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                resource: Product, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Product]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Product]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                properties: ProductUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Product]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Product]: ...

        @distributed_trace_async
        async def count_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                **kwargs: Any
            ) -> CountDevicesResponse: ...

        @distributed_trace
        def generate_default_device_groups(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[DeviceGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                **kwargs: Any
            ) -> Product: ...

        @distributed_trace
        def list_by_catalog(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Product]: ...


namespace azure.mgmt.sphere.models

    class azure.mgmt.sphere.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.sphere.models.AllowCrashDumpCollection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.sphere.models.CapabilityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_DEVELOPMENT = "ApplicationDevelopment"
        FIELD_SERVICING = "FieldServicing"


    class azure.mgmt.sphere.models.Catalog(TrackedResource):
        id: str
        location: str
        name: str
        properties: CatalogProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CatalogProperties] = ..., 
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


    class azure.mgmt.sphere.models.CatalogListResult(Model):
        next_link: str
        value: list[Catalog]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[Catalog], 
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


    class azure.mgmt.sphere.models.CatalogProperties(Model):
        provisioning_state: Union[str, ProvisioningState]
        tenant_id: str

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


    class azure.mgmt.sphere.models.CatalogUpdate(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.sphere.models.Certificate(ProxyResource):
        id: str
        name: str
        properties: CertificateProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[CertificateProperties] = ..., 
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


    class azure.mgmt.sphere.models.CertificateChainResponse(Model):
        certificate_chain: str

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


    class azure.mgmt.sphere.models.CertificateListResult(Model):
        next_link: str
        value: list[Certificate]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[Certificate], 
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


    class azure.mgmt.sphere.models.CertificateProperties(Model):
        certificate: str
        expiry_utc: datetime
        not_before_utc: datetime
        provisioning_state: Union[str, ProvisioningState]
        status: Union[str, CertificateStatus]
        subject: str
        thumbprint: str

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


    class azure.mgmt.sphere.models.CertificateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        EXPIRED = "Expired"
        INACTIVE = "Inactive"
        REVOKED = "Revoked"


    class azure.mgmt.sphere.models.ClaimDevicesRequest(Model):
        device_identifiers: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                device_identifiers: List[str], 
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


    class azure.mgmt.sphere.models.CountDeviceResponse(CountElementsResponse):
        value: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: int, 
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


    class azure.mgmt.sphere.models.CountDevicesResponse(CountElementsResponse):
        value: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: int, 
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


    class azure.mgmt.sphere.models.CountElementsResponse(Model):
        value: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: int, 
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


    class azure.mgmt.sphere.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.sphere.models.Deployment(ProxyResource):
        id: str
        name: str
        properties: DeploymentProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DeploymentProperties] = ..., 
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


    class azure.mgmt.sphere.models.DeploymentListResult(Model):
        next_link: str
        value: list[Deployment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[Deployment], 
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


    class azure.mgmt.sphere.models.DeploymentProperties(Model):
        deployed_images: list[Image]
        deployment_date_utc: datetime
        deployment_id: str
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                deployed_images: Optional[List[Image]] = ..., 
                deployment_id: Optional[str] = ..., 
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


    class azure.mgmt.sphere.models.Device(ProxyResource):
        id: str
        name: str
        properties: DeviceProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DeviceProperties] = ..., 
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


    class azure.mgmt.sphere.models.DeviceGroup(ProxyResource):
        id: str
        name: str
        properties: DeviceGroupProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DeviceGroupProperties] = ..., 
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


    class azure.mgmt.sphere.models.DeviceGroupListResult(Model):
        next_link: str
        value: list[DeviceGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[DeviceGroup], 
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


    class azure.mgmt.sphere.models.DeviceGroupProperties(Model):
        allow_crash_dumps_collection: Union[str, AllowCrashDumpCollection]
        description: str
        has_deployment: bool
        os_feed_type: Union[str, OSFeedType]
        provisioning_state: Union[str, ProvisioningState]
        regional_data_boundary: Union[str, RegionalDataBoundary]
        update_policy: Union[str, UpdatePolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_crash_dumps_collection: Optional[Union[str, AllowCrashDumpCollection]] = ..., 
                description: Optional[str] = ..., 
                os_feed_type: Optional[Union[str, OSFeedType]] = ..., 
                regional_data_boundary: Optional[Union[str, RegionalDataBoundary]] = ..., 
                update_policy: Optional[Union[str, UpdatePolicy]] = ..., 
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


    class azure.mgmt.sphere.models.DeviceGroupUpdate(Model):
        properties: DeviceGroupUpdateProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DeviceGroupUpdateProperties] = ..., 
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


    class azure.mgmt.sphere.models.DeviceGroupUpdateProperties(Model):
        allow_crash_dumps_collection: Union[str, AllowCrashDumpCollection]
        description: str
        os_feed_type: Union[str, OSFeedType]
        regional_data_boundary: Union[str, RegionalDataBoundary]
        update_policy: Union[str, UpdatePolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_crash_dumps_collection: Optional[Union[str, AllowCrashDumpCollection]] = ..., 
                description: Optional[str] = ..., 
                os_feed_type: Optional[Union[str, OSFeedType]] = ..., 
                regional_data_boundary: Optional[Union[str, RegionalDataBoundary]] = ..., 
                update_policy: Optional[Union[str, UpdatePolicy]] = ..., 
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


    class azure.mgmt.sphere.models.DeviceInsight(Model):
        description: str
        device_id: str
        end_timestamp_utc: datetime
        event_category: str
        event_class: str
        event_count: int
        event_type: str
        start_timestamp_utc: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: str, 
                device_id: str, 
                end_timestamp_utc: datetime, 
                event_category: str, 
                event_class: str, 
                event_count: int, 
                event_type: str, 
                start_timestamp_utc: datetime, 
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


    class azure.mgmt.sphere.models.DeviceListResult(Model):
        next_link: str
        value: list[Device]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[Device], 
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


    class azure.mgmt.sphere.models.DeviceProperties(Model):
        chip_sku: str
        device_id: str
        last_available_os_version: str
        last_installed_os_version: str
        last_os_update_utc: datetime
        last_update_request_utc: datetime
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                device_id: Optional[str] = ..., 
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


    class azure.mgmt.sphere.models.DeviceUpdate(Model):
        properties: DeviceUpdateProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DeviceUpdateProperties] = ..., 
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


    class azure.mgmt.sphere.models.DeviceUpdateProperties(Model):
        device_group_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                device_group_id: Optional[str] = ..., 
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


    class azure.mgmt.sphere.models.ErrorAdditionalInfo(Model):
        info: JSON
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


    class azure.mgmt.sphere.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

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


    class azure.mgmt.sphere.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
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


    class azure.mgmt.sphere.models.GenerateCapabilityImageRequest(Model):
        capabilities: Union[list[str, CapabilityType]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capabilities: List[Union[str, CapabilityType]], 
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


    class azure.mgmt.sphere.models.Image(ProxyResource):
        id: str
        name: str
        properties: ImageProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ImageProperties] = ..., 
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


    class azure.mgmt.sphere.models.ImageListResult(Model):
        next_link: str
        value: list[Image]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[Image], 
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


    class azure.mgmt.sphere.models.ImageProperties(Model):
        component_id: str
        description: str
        image: str
        image_id: str
        image_name: str
        image_type: Union[str, ImageType]
        provisioning_state: Union[str, ProvisioningState]
        regional_data_boundary: Union[str, RegionalDataBoundary]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                image: Optional[str] = ..., 
                image_id: Optional[str] = ..., 
                regional_data_boundary: Optional[Union[str, RegionalDataBoundary]] = ..., 
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


    class azure.mgmt.sphere.models.ImageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATIONS = "Applications"
        BASE_SYSTEM_UPDATE_MANIFEST = "BaseSystemUpdateManifest"
        BOOT_MANIFEST = "BootManifest"
        CUSTOMER_BOARD_CONFIG = "CustomerBoardConfig"
        CUSTOMER_UPDATE_MANIFEST = "CustomerUpdateManifest"
        FIRMWARE_UPDATE_MANIFEST = "FirmwareUpdateManifest"
        FW_CONFIG = "FwConfig"
        INVALID_IMAGE_TYPE = "InvalidImageType"
        MANIFEST_SET = "ManifestSet"
        NORMAL_WORLD_DTB = "NormalWorldDtb"
        NORMAL_WORLD_KERNEL = "NormalWorldKernel"
        NORMAL_WORLD_LOADER = "NormalWorldLoader"
        NWFS = "Nwfs"
        ONE_BL = "OneBl"
        OTHER = "Other"
        PLUTON_RUNTIME = "PlutonRuntime"
        POLICY = "Policy"
        RECOVERY_MANIFEST = "RecoveryManifest"
        ROOT_FS = "RootFs"
        SECURITY_MONITOR = "SecurityMonitor"
        SERVICES = "Services"
        TRUSTED_KEYSTORE = "TrustedKeystore"
        UPDATE_CERT_STORE = "UpdateCertStore"
        WIFI_FIRMWARE = "WifiFirmware"


    class azure.mgmt.sphere.models.ListDeviceGroupsRequest(Model):
        device_group_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                device_group_name: Optional[str] = ..., 
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


    class azure.mgmt.sphere.models.OSFeedType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RETAIL = "Retail"
        RETAIL_EVAL = "RetailEval"


    class azure.mgmt.sphere.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.sphere.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

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


    class azure.mgmt.sphere.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

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


    class azure.mgmt.sphere.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.sphere.models.PagedDeviceInsight(Model):
        next_link: str
        value: list[DeviceInsight]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[DeviceInsight], 
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


    class azure.mgmt.sphere.models.Product(ProxyResource):
        id: str
        name: str
        properties: ProductProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ProductProperties] = ..., 
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


    class azure.mgmt.sphere.models.ProductListResult(Model):
        next_link: str
        value: list[Product]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[Product], 
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


    class azure.mgmt.sphere.models.ProductProperties(Model):
        description: str
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
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


    class azure.mgmt.sphere.models.ProductUpdate(Model):
        properties: ProductUpdateProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ProductUpdateProperties] = ..., 
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


    class azure.mgmt.sphere.models.ProductUpdateProperties(Model):
        description: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
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


    class azure.mgmt.sphere.models.ProofOfPossessionNonceRequest(Model):
        proof_of_possession_nonce: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                proof_of_possession_nonce: str, 
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


    class azure.mgmt.sphere.models.ProofOfPossessionNonceResponse(CertificateProperties):
        certificate: str
        expiry_utc: datetime
        not_before_utc: datetime
        provisioning_state: Union[str, ProvisioningState]
        status: Union[str, CertificateStatus]
        subject: str
        thumbprint: str

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


    class azure.mgmt.sphere.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.sphere.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
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


    class azure.mgmt.sphere.models.RegionalDataBoundary(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EU = "EU"
        NONE = "None"


    class azure.mgmt.sphere.models.Resource(Model):
        id: str
        name: str
        system_data: SystemData
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


    class azure.mgmt.sphere.models.SignedCapabilityImageResponse(Model):
        image: str

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


    class azure.mgmt.sphere.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
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


    class azure.mgmt.sphere.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
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


    class azure.mgmt.sphere.models.UpdatePolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO3_RD_PARTY_APP_UPDATES = "No3rdPartyAppUpdates"
        UPDATE_ALL = "UpdateAll"


namespace azure.mgmt.sphere.operations

    class azure.mgmt.sphere.operations.CatalogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                resource: Catalog, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Catalog]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Catalog]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upload_image(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                upload_image_request: Image, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upload_image(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                upload_image_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def count_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> CountDevicesResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> Catalog: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[Catalog]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[Catalog]: ...

        @distributed_trace
        def list_deployments(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Deployment]: ...

        @overload
        def list_device_groups(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                list_device_groups_request: ListDeviceGroupsRequest, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[DeviceGroup]: ...

        @overload
        def list_device_groups(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                list_device_groups_request: IO[bytes], 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[DeviceGroup]: ...

        @distributed_trace
        def list_device_insights(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[DeviceInsight]: ...

        @distributed_trace
        def list_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Device]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                properties: CatalogUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Catalog: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Catalog: ...


    class azure.mgmt.sphere.operations.CertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                serial_number: str, 
                **kwargs: Any
            ) -> Certificate: ...

        @distributed_trace
        def list_by_catalog(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Certificate]: ...

        @distributed_trace
        def retrieve_cert_chain(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                serial_number: str, 
                **kwargs: Any
            ) -> CertificateChainResponse: ...

        @overload
        def retrieve_proof_of_possession_nonce(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                serial_number: str, 
                proof_of_possession_nonce_request: ProofOfPossessionNonceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProofOfPossessionNonceResponse: ...

        @overload
        def retrieve_proof_of_possession_nonce(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                serial_number: str, 
                proof_of_possession_nonce_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProofOfPossessionNonceResponse: ...


    class azure.mgmt.sphere.operations.DeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                deployment_name: str, 
                resource: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Deployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                deployment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Deployment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace
        def list_by_device_group(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Deployment]: ...


    class azure.mgmt.sphere.operations.DeviceGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_claim_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                claim_devices_request: ClaimDevicesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_claim_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                claim_devices_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                resource: DeviceGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeviceGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeviceGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                properties: DeviceGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeviceGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeviceGroup]: ...

        @distributed_trace
        def count_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                **kwargs: Any
            ) -> CountDevicesResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                **kwargs: Any
            ) -> DeviceGroup: ...

        @distributed_trace
        def list_by_product(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[DeviceGroup]: ...


    class azure.mgmt.sphere.operations.DevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                resource: Device, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Device]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Device]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_generate_capability_image(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                generate_device_capability_request: GenerateCapabilityImageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignedCapabilityImageResponse]: ...

        @overload
        def begin_generate_capability_image(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                generate_device_capability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignedCapabilityImageResponse]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                properties: DeviceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Device]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Device]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                device_name: str, 
                **kwargs: Any
            ) -> Device: ...

        @distributed_trace
        def list_by_device_group(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                device_group_name: str, 
                **kwargs: Any
            ) -> Iterable[Device]: ...


    class azure.mgmt.sphere.operations.ImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                image_name: str, 
                resource: Image, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Image]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                image_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Image]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def list_by_catalog(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                maxpagesize: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Image]: ...


    class azure.mgmt.sphere.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.sphere.operations.ProductsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                resource: Product, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Product]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Product]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                properties: ProductUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Product]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Product]: ...

        @distributed_trace
        def count_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                **kwargs: Any
            ) -> CountDevicesResponse: ...

        @distributed_trace
        def generate_default_device_groups(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                **kwargs: Any
            ) -> Iterable[DeviceGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                product_name: str, 
                **kwargs: Any
            ) -> Product: ...

        @distributed_trace
        def list_by_catalog(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> Iterable[Product]: ...


```