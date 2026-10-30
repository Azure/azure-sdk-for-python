```py
namespace azure.mgmt.serviceconnectioncontroller

    class azure.mgmt.serviceconnectioncontroller.ServiceConnectionControllerMgmtClient: implements ContextManager 
        azure_service_connection_controllers: AzureServiceConnectionControllersOperations
        operations: Operations

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


namespace azure.mgmt.serviceconnectioncontroller.aio

    class azure.mgmt.serviceconnectioncontroller.aio.ServiceConnectionControllerMgmtClient: implements AsyncContextManager 
        azure_service_connection_controllers: AzureServiceConnectionControllersOperations
        operations: Operations

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


namespace azure.mgmt.serviceconnectioncontroller.aio.operations

    class azure.mgmt.serviceconnectioncontroller.aio.operations.AzureServiceConnectionControllersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                resource: AzureServiceConnectionController, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureServiceConnectionController]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                resource: AzureServiceConnectionController, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureServiceConnectionController]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureServiceConnectionController]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                **kwargs: Any
            ) -> AzureServiceConnectionController: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureServiceConnectionController]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AzureServiceConnectionController]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                properties: AzureServiceConnectionControllerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureServiceConnectionController: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                properties: AzureServiceConnectionControllerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureServiceConnectionController: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureServiceConnectionController: ...


    class azure.mgmt.serviceconnectioncontroller.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.serviceconnectioncontroller.models

    class azure.mgmt.serviceconnectioncontroller.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.serviceconnectioncontroller.models.AzureServiceConnectionController(TrackedResource):
        id: str
        location: str
        managed_by: Optional[str]
        name: str
        properties: Optional[AzureServiceConnectionControllerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                managed_by: Optional[str] = ..., 
                properties: Optional[AzureServiceConnectionControllerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serviceconnectioncontroller.models.AzureServiceConnectionControllerProperties(_Model):
        ip_configurations: Optional[list[IpConfiguration]]
        managed_on_behalf_of_configuration: Optional[ManagedOnBehalfOfConfiguration]
        provider_connections: Optional[list[ProviderConnectionProperties]]
        provisioning_state: Optional[Union[str, AzureServiceConnectionControllerProvisioningState]]
        subnet_id: Optional[str]
        udr: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_configurations: Optional[list[IpConfiguration]] = ..., 
                provider_connections: Optional[list[ProviderConnectionProperties]] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serviceconnectioncontroller.models.AzureServiceConnectionControllerProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.serviceconnectioncontroller.models.AzureServiceConnectionControllerTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serviceconnectioncontroller.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.serviceconnectioncontroller.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.serviceconnectioncontroller.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.serviceconnectioncontroller.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serviceconnectioncontroller.models.IPAllocationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STATIC = "Static"


    class azure.mgmt.serviceconnectioncontroller.models.IpConfiguration(_Model):
        ip_allocation_method: Optional[Union[str, IPAllocationMethod]]
        private_ip_v4_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_allocation_method: Optional[Union[str, IPAllocationMethod]] = ..., 
                private_ip_v4_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serviceconnectioncontroller.models.ManagedOnBehalfOfConfiguration(_Model):
        mobo_broker_resources: Optional[list[MoboBrokerResource]]


    class azure.mgmt.serviceconnectioncontroller.models.MoboBrokerResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serviceconnectioncontroller.models.Operation(_Model):
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


    class azure.mgmt.serviceconnectioncontroller.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.serviceconnectioncontroller.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.serviceconnectioncontroller.models.ProviderConnectionProperties(_Model):
        ip_configuration: Optional[IpConfiguration]
        name: Optional[str]
        private_endpoint_resource_group: Optional[str]
        source_resource_id: Optional[str]
        subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_configuration: Optional[IpConfiguration] = ..., 
                name: Optional[str] = ..., 
                private_endpoint_resource_group: Optional[str] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serviceconnectioncontroller.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.serviceconnectioncontroller.models.SystemData(_Model):
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


    class azure.mgmt.serviceconnectioncontroller.models.TrackedResource(Resource):
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


namespace azure.mgmt.serviceconnectioncontroller.operations

    class azure.mgmt.serviceconnectioncontroller.operations.AzureServiceConnectionControllersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                resource: AzureServiceConnectionController, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureServiceConnectionController]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                resource: AzureServiceConnectionController, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureServiceConnectionController]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureServiceConnectionController]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                **kwargs: Any
            ) -> AzureServiceConnectionController: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AzureServiceConnectionController]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AzureServiceConnectionController]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                properties: AzureServiceConnectionControllerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureServiceConnectionController: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                properties: AzureServiceConnectionControllerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureServiceConnectionController: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_service_connection_controller_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureServiceConnectionController: ...


    class azure.mgmt.serviceconnectioncontroller.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.serviceconnectioncontroller.types

    class azure.mgmt.serviceconnectioncontroller.types.AzureServiceConnectionController(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "managedBy": str
        key "name": str
        key "properties": ForwardRef('AzureServiceConnectionControllerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        managedBy: str
        name: str
        properties: AzureServiceConnectionControllerProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.serviceconnectioncontroller.types.AzureServiceConnectionControllerProperties(TypedDict, total=False):
        key "managedOnBehalfOfConfiguration": ForwardRef('ManagedOnBehalfOfConfiguration', module='types')
        key "provisioningState": Union[str, AzureServiceConnectionControllerProvisioningState]
        key "subnetId": str
        key "udr": str
        ipConfigurations: list[IpConfiguration]
        managedOnBehalfOfConfiguration: ManagedOnBehalfOfConfiguration
        providerConnections: list[ProviderConnectionProperties]
        provisioningState: Union[str, AzureServiceConnectionControllerProvisioningState]
        subnetId: str
        udr: str


    class azure.mgmt.serviceconnectioncontroller.types.AzureServiceConnectionControllerTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.serviceconnectioncontroller.types.IpConfiguration(TypedDict, total=False):
        key "ipAllocationMethod": Union[str, IPAllocationMethod]
        key "privateIpV4Address": str
        ipAllocationMethod: Union[str, IPAllocationMethod]
        privateIpV4Address: str


    class azure.mgmt.serviceconnectioncontroller.types.ManagedOnBehalfOfConfiguration(TypedDict, total=False):
        moboBrokerResources: list[MoboBrokerResource]


    class azure.mgmt.serviceconnectioncontroller.types.MoboBrokerResource(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.serviceconnectioncontroller.types.ProviderConnectionProperties(TypedDict, total=False):
        key "ipConfiguration": ForwardRef('IpConfiguration', module='types')
        key "name": str
        key "privateEndpointResourceGroup": str
        key "sourceResourceId": str
        key "subnetId": str
        ipConfiguration: IpConfiguration
        name: str
        privateEndpointResourceGroup: str
        sourceResourceId: str
        subnetId: str


    class azure.mgmt.serviceconnectioncontroller.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.serviceconnectioncontroller.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.serviceconnectioncontroller.types.TrackedResource(Resource):
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