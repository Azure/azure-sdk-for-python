```py
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
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


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
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


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
            ) -> AsyncItemPaged[Catalog]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Catalog]: ...

        @distributed_trace
        def list_deployments(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Deployment]: ...

        @overload
        def list_device_groups(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                list_device_groups_request: ListDeviceGroupsRequest, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeviceGroup]: ...

        @overload
        def list_device_groups(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                list_device_groups_request: ListDeviceGroupsRequest, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeviceGroup]: ...

        @overload
        def list_device_groups(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                list_device_groups_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeviceGroup]: ...

        @distributed_trace
        def list_device_insights(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeviceInsight]: ...

        @distributed_trace
        def list_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Device]: ...

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
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Certificate]: ...

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
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Deployment]: ...


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
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeviceGroup]: ...


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
            ) -> AsyncItemPaged[Device]: ...


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
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Image]: ...


    class azure.mgmt.sphere.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


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
            ) -> AsyncItemPaged[DeviceGroup]: ...

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
            ) -> AsyncItemPaged[Product]: ...


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
        properties: Optional[CatalogProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CatalogProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.CatalogProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        tenant_id: Optional[str]


    class azure.mgmt.sphere.models.CatalogUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.Certificate(ProxyResource):
        id: str
        name: str
        properties: Optional[CertificateProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CertificateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.CertificateChainResponse(_Model):
        certificate_chain: Optional[str]


    class azure.mgmt.sphere.models.CertificateProperties(_Model):
        certificate: Optional[str]
        expiry_utc: Optional[datetime]
        not_before_utc: Optional[datetime]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[Union[str, CertificateStatus]]
        subject: Optional[str]
        thumbprint: Optional[str]


    class azure.mgmt.sphere.models.CertificateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        EXPIRED = "Expired"
        INACTIVE = "Inactive"
        REVOKED = "Revoked"


    class azure.mgmt.sphere.models.ClaimDevicesRequest(_Model):
        device_identifiers: list[str]

        @overload
        def __init__(
                self, 
                *, 
                device_identifiers: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.CountDevicesResponse(CountElementsResponse):
        value: int

        @overload
        def __init__(
                self, 
                *, 
                value: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.CountElementsResponse(_Model):
        value: int

        @overload
        def __init__(
                self, 
                *, 
                value: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.sphere.models.Deployment(ProxyResource):
        id: str
        name: str
        properties: Optional[DeploymentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeploymentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.DeploymentProperties(_Model):
        deployed_images: Optional[list[Image]]
        deployment_date_utc: Optional[datetime]
        deployment_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                deployed_images: Optional[list[Image]] = ..., 
                deployment_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.Device(ProxyResource):
        id: str
        name: str
        properties: Optional[DeviceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeviceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.DeviceGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[DeviceGroupProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeviceGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.DeviceGroupProperties(_Model):
        allow_crash_dumps_collection: Optional[Union[str, AllowCrashDumpCollection]]
        description: Optional[str]
        has_deployment: Optional[bool]
        os_feed_type: Optional[Union[str, OSFeedType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        regional_data_boundary: Optional[Union[str, RegionalDataBoundary]]
        update_policy: Optional[Union[str, UpdatePolicy]]

        @overload
        def __init__(
                self, 
                *, 
                allow_crash_dumps_collection: Optional[Union[str, AllowCrashDumpCollection]] = ..., 
                description: Optional[str] = ..., 
                os_feed_type: Optional[Union[str, OSFeedType]] = ..., 
                regional_data_boundary: Optional[Union[str, RegionalDataBoundary]] = ..., 
                update_policy: Optional[Union[str, UpdatePolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.DeviceGroupUpdate(_Model):
        properties: Optional[DeviceGroupUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeviceGroupUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.sphere.models.DeviceGroupUpdateProperties(_Model):
        allow_crash_dumps_collection: Optional[Union[str, AllowCrashDumpCollection]]
        description: Optional[str]
        os_feed_type: Optional[Union[str, OSFeedType]]
        regional_data_boundary: Optional[Union[str, RegionalDataBoundary]]
        update_policy: Optional[Union[str, UpdatePolicy]]

        @overload
        def __init__(
                self, 
                *, 
                allow_crash_dumps_collection: Optional[Union[str, AllowCrashDumpCollection]] = ..., 
                description: Optional[str] = ..., 
                os_feed_type: Optional[Union[str, OSFeedType]] = ..., 
                regional_data_boundary: Optional[Union[str, RegionalDataBoundary]] = ..., 
                update_policy: Optional[Union[str, UpdatePolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.DeviceInsight(_Model):
        description: str
        device_id: str
        end_timestamp_utc: datetime
        event_category: str
        event_class: str
        event_count: int
        event_type: str
        start_timestamp_utc: datetime

        @overload
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
                start_timestamp_utc: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.DeviceProperties(_Model):
        chip_sku: Optional[str]
        device_id: Optional[str]
        last_available_os_version: Optional[str]
        last_installed_os_version: Optional[str]
        last_os_update_utc: Optional[datetime]
        last_update_request_utc: Optional[datetime]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                device_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.DeviceUpdate(_Model):
        properties: Optional[DeviceUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeviceUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.sphere.models.DeviceUpdateProperties(_Model):
        device_group_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                device_group_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.sphere.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.sphere.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.GenerateCapabilityImageRequest(_Model):
        capabilities: list[Union[str, CapabilityType]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: list[Union[str, CapabilityType]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.Image(ProxyResource):
        id: str
        name: str
        properties: Optional[ImageProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ImageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.ImageProperties(_Model):
        component_id: Optional[str]
        description: Optional[str]
        image: Optional[str]
        image_id: Optional[str]
        image_name: Optional[str]
        image_type: Optional[Union[str, ImageType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        regional_data_boundary: Optional[Union[str, RegionalDataBoundary]]
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                image: Optional[str] = ..., 
                image_id: Optional[str] = ..., 
                regional_data_boundary: Optional[Union[str, RegionalDataBoundary]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.sphere.models.ListDeviceGroupsRequest(_Model):
        device_group_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                device_group_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.OSFeedType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RETAIL = "Retail"
        RETAIL_EVAL = "RetailEval"


    class azure.mgmt.sphere.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.sphere.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.sphere.models.Product(ProxyResource):
        id: str
        name: str
        properties: Optional[ProductProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProductProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.ProductProperties(_Model):
        description: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.ProductUpdate(_Model):
        properties: Optional[ProductUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProductUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.sphere.models.ProductUpdateProperties(_Model):
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.ProofOfPossessionNonceRequest(_Model):
        proof_of_possession_nonce: str

        @overload
        def __init__(
                self, 
                *, 
                proof_of_possession_nonce: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sphere.models.ProofOfPossessionNonceResponse(CertificateProperties):
        certificate: str
        expiry_utc: datetime
        not_before_utc: datetime
        provisioning_state: Union[str, ProvisioningState]
        status: Union[str, CertificateStatus]
        subject: str
        thumbprint: str


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


    class azure.mgmt.sphere.models.RegionalDataBoundary(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EU = "EU"
        NONE = "None"


    class azure.mgmt.sphere.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.sphere.models.SignedCapabilityImageResponse(_Model):
        image: Optional[str]


    class azure.mgmt.sphere.models.SystemData(_Model):
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


    class azure.mgmt.sphere.models.TrackedResource(Resource):
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


    class azure.mgmt.sphere.models.UpdatePolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO3_RD_PARTY_APP_UPDATES = "No3rdPartyAppUpdates"
        UPDATE_ALL = "UpdateAll"


namespace azure.mgmt.sphere.operations

    class azure.mgmt.sphere.operations.CatalogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Catalog]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Catalog]: ...

        @distributed_trace
        def list_deployments(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Deployment]: ...

        @overload
        def list_device_groups(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                list_device_groups_request: ListDeviceGroupsRequest, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeviceGroup]: ...

        @overload
        def list_device_groups(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                list_device_groups_request: ListDeviceGroupsRequest, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeviceGroup]: ...

        @overload
        def list_device_groups(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                list_device_groups_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeviceGroup]: ...

        @distributed_trace
        def list_device_insights(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeviceInsight]: ...

        @distributed_trace
        def list_devices(
                self, 
                resource_group_name: str, 
                catalog_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Device]: ...

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
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Certificate]: ...

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
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Deployment]: ...


    class azure.mgmt.sphere.operations.DeviceGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeviceGroup]: ...


    class azure.mgmt.sphere.operations.DevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Device]: ...


    class azure.mgmt.sphere.operations.ImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Image]: ...


    class azure.mgmt.sphere.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.sphere.operations.ProductsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[DeviceGroup]: ...

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
            ) -> ItemPaged[Product]: ...


namespace azure.mgmt.sphere.types

    class azure.mgmt.sphere.types.Catalog(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CatalogProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: CatalogProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.sphere.types.CatalogProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "tenantId": str
        provisioningState: Union[str, ProvisioningState]
        tenantId: str


    class azure.mgmt.sphere.types.CatalogUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.sphere.types.ClaimDevicesRequest(TypedDict, total=False):
        key "deviceIdentifiers": Required[list[str]]
        deviceIdentifiers: list[str]


    class azure.mgmt.sphere.types.Deployment(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DeploymentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DeploymentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.sphere.types.DeploymentProperties(TypedDict, total=False):
        key "deploymentDateUtc": str
        key "deploymentId": str
        key "provisioningState": Union[str, ProvisioningState]
        deployedImages: list[Image]
        deploymentDateUtc: str
        deploymentId: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.sphere.types.Device(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DeviceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DeviceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.sphere.types.DeviceGroup(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DeviceGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DeviceGroupProperties
        systemData: SystemData
        type: str


    class azure.mgmt.sphere.types.DeviceGroupProperties(TypedDict, total=False):
        key "allowCrashDumpsCollection": Union[str, AllowCrashDumpCollection]
        key "description": str
        key "hasDeployment": bool
        key "osFeedType": Union[str, OSFeedType]
        key "provisioningState": Union[str, ProvisioningState]
        key "regionalDataBoundary": Union[str, RegionalDataBoundary]
        key "updatePolicy": Union[str, UpdatePolicy]
        allowCrashDumpsCollection: Union[str, AllowCrashDumpCollection]
        description: str
        hasDeployment: bool
        osFeedType: Union[str, OSFeedType]
        provisioningState: Union[str, ProvisioningState]
        regionalDataBoundary: Union[str, RegionalDataBoundary]
        updatePolicy: Union[str, UpdatePolicy]


    class azure.mgmt.sphere.types.DeviceGroupUpdate(TypedDict, total=False):
        key "properties": ForwardRef('DeviceGroupUpdateProperties', module='types')
        properties: DeviceGroupUpdateProperties


    class azure.mgmt.sphere.types.DeviceGroupUpdateProperties(TypedDict, total=False):
        key "allowCrashDumpsCollection": Union[str, AllowCrashDumpCollection]
        key "description": str
        key "osFeedType": Union[str, OSFeedType]
        key "regionalDataBoundary": Union[str, RegionalDataBoundary]
        key "updatePolicy": Union[str, UpdatePolicy]
        allowCrashDumpsCollection: Union[str, AllowCrashDumpCollection]
        description: str
        osFeedType: Union[str, OSFeedType]
        regionalDataBoundary: Union[str, RegionalDataBoundary]
        updatePolicy: Union[str, UpdatePolicy]


    class azure.mgmt.sphere.types.DeviceProperties(TypedDict, total=False):
        key "chipSku": str
        key "deviceId": str
        key "lastAvailableOsVersion": str
        key "lastInstalledOsVersion": str
        key "lastOsUpdateUtc": str
        key "lastUpdateRequestUtc": str
        key "provisioningState": Union[str, ProvisioningState]
        chipSku: str
        deviceId: str
        lastAvailableOsVersion: str
        lastInstalledOsVersion: str
        lastOsUpdateUtc: str
        lastUpdateRequestUtc: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.sphere.types.DeviceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('DeviceUpdateProperties', module='types')
        properties: DeviceUpdateProperties


    class azure.mgmt.sphere.types.DeviceUpdateProperties(TypedDict, total=False):
        key "deviceGroupId": str
        deviceGroupId: str


    class azure.mgmt.sphere.types.GenerateCapabilityImageRequest(TypedDict, total=False):
        key "capabilities": Required[list[Union[str, CapabilityType]]]
        capabilities: list[Union[str, CapabilityType]]


    class azure.mgmt.sphere.types.Image(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ImageProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ImageProperties
        systemData: SystemData
        type: str


    class azure.mgmt.sphere.types.ImageProperties(TypedDict, total=False):
        key "componentId": str
        key "description": str
        key "image": str
        key "imageId": str
        key "imageName": str
        key "imageType": Union[str, ImageType]
        key "provisioningState": Union[str, ProvisioningState]
        key "regionalDataBoundary": Union[str, RegionalDataBoundary]
        key "uri": str
        componentId: str
        description: str
        image: str
        imageId: str
        imageName: str
        imageType: Union[str, ImageType]
        provisioningState: Union[str, ProvisioningState]
        regionalDataBoundary: Union[str, RegionalDataBoundary]
        uri: str


    class azure.mgmt.sphere.types.ListDeviceGroupsRequest(TypedDict, total=False):
        key "deviceGroupName": str
        deviceGroupName: str


    class azure.mgmt.sphere.types.Product(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ProductProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ProductProperties
        systemData: SystemData
        type: str


    class azure.mgmt.sphere.types.ProductProperties(TypedDict, total=False):
        key "description": str
        key "provisioningState": Union[str, ProvisioningState]
        description: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.sphere.types.ProductUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ProductUpdateProperties', module='types')
        properties: ProductUpdateProperties


    class azure.mgmt.sphere.types.ProductUpdateProperties(TypedDict, total=False):
        key "description": str
        description: str


    class azure.mgmt.sphere.types.ProofOfPossessionNonceRequest(TypedDict, total=False):
        key "proofOfPossessionNonce": Required[str]
        proofOfPossessionNonce: str


    class azure.mgmt.sphere.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.sphere.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.sphere.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


    class azure.mgmt.sphere.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


```