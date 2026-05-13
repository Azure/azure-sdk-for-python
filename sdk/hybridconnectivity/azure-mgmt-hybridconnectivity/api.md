```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.hybridconnectivity

    class azure.mgmt.hybridconnectivity.HybridConnectivityMgmtClient: implements ContextManager 
        endpoints: EndpointsOperations
        generate_aws_template: GenerateAwsTemplateOperations
        inventory: InventoryOperations
        operations: Operations
        public_cloud_connectors: PublicCloudConnectorsOperations
        service_configurations: ServiceConfigurationsOperations
        solution_configurations: SolutionConfigurationsOperations
        solution_types: SolutionTypesOperations

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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.hybridconnectivity.aio

    class azure.mgmt.hybridconnectivity.aio.HybridConnectivityMgmtClient: implements AsyncContextManager 
        endpoints: EndpointsOperations
        generate_aws_template: GenerateAwsTemplateOperations
        inventory: InventoryOperations
        operations: Operations
        public_cloud_connectors: PublicCloudConnectorsOperations
        service_configurations: ServiceConfigurationsOperations
        solution_configurations: SolutionConfigurationsOperations
        solution_types: SolutionTypesOperations

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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.hybridconnectivity.aio.operations

    class azure.mgmt.hybridconnectivity.aio.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                endpoint_resource: EndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EndpointResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                endpoint_resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EndpointResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                endpoint_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EndpointResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> EndpointResource: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncIterable[EndpointResource]: ...

        @overload
        async def list_credentials(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                list_credentials_request: Optional[ListCredentialsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                expiresin: Optional[int] = ..., 
                **kwargs: Any
            ) -> EndpointAccessResource: ...

        @overload
        async def list_credentials(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                list_credentials_request: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                expiresin: Optional[int] = ..., 
                **kwargs: Any
            ) -> EndpointAccessResource: ...

        @overload
        async def list_credentials(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                list_credentials_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                expiresin: Optional[int] = ..., 
                **kwargs: Any
            ) -> EndpointAccessResource: ...

        @overload
        async def list_ingress_gateway_credentials(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                list_ingress_gateway_credentials_request: Optional[ListIngressGatewayCredentialsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                expiresin: Optional[int] = ..., 
                **kwargs: Any
            ) -> IngressGatewayResource: ...

        @overload
        async def list_ingress_gateway_credentials(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                list_ingress_gateway_credentials_request: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                expiresin: Optional[int] = ..., 
                **kwargs: Any
            ) -> IngressGatewayResource: ...

        @overload
        async def list_ingress_gateway_credentials(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                list_ingress_gateway_credentials_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                expiresin: Optional[int] = ..., 
                **kwargs: Any
            ) -> IngressGatewayResource: ...

        @overload
        async def list_managed_proxy_details(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                managed_proxy_request: ManagedProxyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedProxyResource: ...

        @overload
        async def list_managed_proxy_details(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                managed_proxy_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedProxyResource: ...

        @overload
        async def list_managed_proxy_details(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                managed_proxy_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedProxyResource: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                endpoint_resource: EndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EndpointResource: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                endpoint_resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EndpointResource: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                endpoint_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EndpointResource: ...


    class azure.mgmt.hybridconnectivity.aio.operations.GenerateAwsTemplateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def post(
                self, 
                generate_aws_template_request: GenerateAwsTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...

        @overload
        async def post(
                self, 
                generate_aws_template_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...

        @overload
        async def post(
                self, 
                generate_aws_template_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...


    class azure.mgmt.hybridconnectivity.aio.operations.InventoryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                inventory_id: str, 
                **kwargs: Any
            ) -> InventoryResource: ...

        @distributed_trace
        def list_by_solution_configuration(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                **kwargs: Any
            ) -> AsyncIterable[InventoryResource]: ...


    class azure.mgmt.hybridconnectivity.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.hybridconnectivity.aio.operations.PublicCloudConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                resource: PublicCloudConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PublicCloudConnector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PublicCloudConnector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PublicCloudConnector]: ...

        @distributed_trace_async
        async def begin_test_permissions(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                **kwargs: Any
            ) -> PublicCloudConnector: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PublicCloudConnector]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[PublicCloudConnector]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                properties: PublicCloudConnectorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PublicCloudConnector: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PublicCloudConnector: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PublicCloudConnector: ...


    class azure.mgmt.hybridconnectivity.aio.operations.ServiceConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_orupdate(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                service_configuration_resource: ServiceConfigurationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...

        @overload
        async def create_orupdate(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                service_configuration_resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...

        @overload
        async def create_orupdate(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                service_configuration_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...

        @distributed_trace
        def list_by_endpoint_resource(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ServiceConfigurationResource]: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                service_configuration_resource: ServiceConfigurationResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                service_configuration_resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                service_configuration_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...


    class azure.mgmt.hybridconnectivity.aio.operations.SolutionConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_sync_now(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                resource: SolutionConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionConfiguration: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionConfiguration: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionConfiguration: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                **kwargs: Any
            ) -> SolutionConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncIterable[SolutionConfiguration]: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                properties: SolutionConfigurationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionConfiguration: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionConfiguration: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionConfiguration: ...


    class azure.mgmt.hybridconnectivity.aio.operations.SolutionTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                solution_type: str, 
                **kwargs: Any
            ) -> SolutionTypeResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SolutionTypeResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[SolutionTypeResource]: ...


namespace azure.mgmt.hybridconnectivity.models

    class azure.mgmt.hybridconnectivity.models.AADProfileProperties(Model):
        server_id: str
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                server_id: str, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.hybridconnectivity.models.AwsCloudProfile(Model):
        account_id: str
        excluded_accounts: Optional[List[str]]
        is_organizational_account: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                account_id: str, 
                excluded_accounts: Optional[List[str]] = ..., 
                is_organizational_account: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.AwsCloudProfileUpdate(Model):
        excluded_accounts: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                excluded_accounts: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.CloudNativeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EC2 = "ec2"


    class azure.mgmt.hybridconnectivity.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.hybridconnectivity.models.EndpointAccessResource(Model):
        relay: Optional[RelayNamespaceAccessProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                relay: Optional[RelayNamespaceAccessProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridconnectivity.models.EndpointProperties(Model):
        provisioning_state: Optional[str]
        resource_id: Optional[str]
        type: Union[str, Type]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                type: Union[str, Type]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.EndpointResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[EndpointProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.hybridconnectivity.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.hybridconnectivity.models.ErrorResponse(Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.hybridconnectivity.models.GenerateAwsTemplateRequest(Model):
        connector_id: str
        solution_types: Optional[List[SolutionTypeSettings]]

        @overload
        def __init__(
                self, 
                *, 
                connector_id: str, 
                solution_types: Optional[List[SolutionTypeSettings]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.HostType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS = "AWS"


    class azure.mgmt.hybridconnectivity.models.IngressGatewayResource(Model):
        ingress: Optional[IngressProfileProperties]
        relay: Optional[RelayNamespaceAccessProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                ingress: Optional[IngressProfileProperties] = ..., 
                relay: Optional[RelayNamespaceAccessProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridconnectivity.models.IngressProfileProperties(Model):
        aad_profile: AADProfileProperties
        hostname: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                aad_profile: AADProfileProperties, 
                hostname: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridconnectivity.models.InventoryProperties(Model):
        azure_resource_id: Optional[str]
        cloud_native_resource_id: Optional[str]
        cloud_native_type: Optional[Union[str, CloudNativeType]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        status: Optional[Union[str, SolutionConfigurationStatus]]
        status_details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_id: Optional[str] = ..., 
                cloud_native_resource_id: Optional[str] = ..., 
                cloud_native_type: Optional[Union[str, CloudNativeType]] = ..., 
                status: Optional[Union[str, SolutionConfigurationStatus]] = ..., 
                status_details: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.InventoryResource(ProxyResource):
        id: str
        name: str
        properties: Optional[InventoryProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[InventoryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ListCredentialsRequest(Model):
        service_name: Optional[Union[str, ServiceName]]

        @overload
        def __init__(
                self, 
                *, 
                service_name: Optional[Union[str, ServiceName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ListIngressGatewayCredentialsRequest(Model):
        service_name: Optional[Union[str, ServiceName]]

        @overload
        def __init__(
                self, 
                *, 
                service_name: Optional[Union[str, ServiceName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ManagedProxyRequest(Model):
        hostname: Optional[str]
        service: str
        service_name: Optional[Union[str, ServiceName]]

        @overload
        def __init__(
                self, 
                *, 
                hostname: Optional[str] = ..., 
                service: str, 
                service_name: Optional[Union[str, ServiceName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ManagedProxyResource(Model):
        expires_on: int
        proxy: str

        @overload
        def __init__(
                self, 
                *, 
                expires_on: int, 
                proxy: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.Operation(Model):
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


    class azure.mgmt.hybridconnectivity.models.OperationDisplay(Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.hybridconnectivity.models.OperationStatusResult(Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[List[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[List[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.hybridconnectivity.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.hybridconnectivity.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.hybridconnectivity.models.PublicCloudConnector(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[PublicCloudConnectorProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[PublicCloudConnectorProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.PublicCloudConnectorProperties(Model):
        aws_cloud_profile: AwsCloudProfile
        connector_primary_identifier: Optional[str]
        host_type: Union[str, HostType]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                aws_cloud_profile: AwsCloudProfile, 
                host_type: Union[str, HostType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.PublicCloudConnectorPropertiesUpdate(Model):
        aws_cloud_profile: Optional[AwsCloudProfileUpdate]

        @overload
        def __init__(
                self, 
                *, 
                aws_cloud_profile: Optional[AwsCloudProfileUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.PublicCloudConnectorUpdate(TrackedResourceUpdate):
        id: str
        name: str
        properties: Optional[PublicCloudConnectorPropertiesUpdate]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PublicCloudConnectorPropertiesUpdate] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.RelayNamespaceAccessProperties(Model):
        access_key: Optional[str]
        expires_on: Optional[int]
        hybrid_connection_name: str
        namespace_name: str
        namespace_name_suffix: str
        service_configuration_token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expires_on: Optional[int] = ..., 
                hybrid_connection_name: str, 
                namespace_name: str, 
                namespace_name_suffix: str, 
                service_configuration_token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.Resource(Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.hybridconnectivity.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.hybridconnectivity.models.ServiceConfigurationProperties(Model):
        port: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_id: Optional[str]
        service_name: Union[str, ServiceName]

        @overload
        def __init__(
                self, 
                *, 
                port: Optional[int] = ..., 
                resource_id: Optional[str] = ..., 
                service_name: Union[str, ServiceName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ServiceConfigurationPropertiesPatch(Model):
        port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ServiceConfigurationResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[ServiceConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ServiceConfigurationResourcePatch(Model):
        properties: Optional[ServiceConfigurationPropertiesPatch]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceConfigurationPropertiesPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ServiceName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SSH = "SSH"
        WAC = "WAC"


    class azure.mgmt.hybridconnectivity.models.SolutionConfiguration(ExtensionResource):
        id: str
        name: str
        properties: Optional[SolutionConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.SolutionConfigurationProperties(Model):
        last_sync_time: Optional[datetime]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        solution_settings: Optional[SolutionSettings]
        solution_type: str
        status: Optional[Union[str, SolutionConfigurationStatus]]
        status_details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                solution_settings: Optional[SolutionSettings] = ..., 
                solution_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.SolutionConfigurationPropertiesUpdate(Model):
        solution_settings: Optional[SolutionSettings]
        solution_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                solution_settings: Optional[SolutionSettings] = ..., 
                solution_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.SolutionConfigurationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NEW = "New"


    class azure.mgmt.hybridconnectivity.models.SolutionConfigurationUpdate(ProxyResource):
        id: str
        name: str
        properties: Optional[SolutionConfigurationPropertiesUpdate]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionConfigurationPropertiesUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.SolutionSettings(Model):


    class azure.mgmt.hybridconnectivity.models.SolutionTypeProperties(Model):
        description: Optional[str]
        solution_settings: Optional[List[SolutionTypeSettingsProperties]]
        solution_type: Optional[str]
        supported_azure_regions: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                solution_settings: Optional[List[SolutionTypeSettingsProperties]] = ..., 
                solution_type: Optional[str] = ..., 
                supported_azure_regions: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.SolutionTypeResource(ProxyResource):
        id: str
        name: str
        properties: Optional[SolutionTypeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionTypeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.SolutionTypeSettings(Model):
        solution_settings: Optional[SolutionSettings]
        solution_type: str

        @overload
        def __init__(
                self, 
                *, 
                solution_settings: Optional[SolutionSettings] = ..., 
                solution_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.SolutionTypeSettingsProperties(Model):
        allowed_values: List[str]
        default_value: str
        description: str
        display_name: str
        name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                allowed_values: List[str], 
                default_value: str, 
                description: str, 
                display_name: str, 
                name: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.SystemData(Model):
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


    class azure.mgmt.hybridconnectivity.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[Dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.TrackedResourceUpdate(Resource):
        id: str
        name: str
        system_data: SystemData
        tags: Optional[Dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "custom"
        DEFAULT = "default"


namespace azure.mgmt.hybridconnectivity.operations

    class azure.mgmt.hybridconnectivity.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                endpoint_resource: EndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EndpointResource: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                endpoint_resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EndpointResource: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                endpoint_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EndpointResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> EndpointResource: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> Iterable[EndpointResource]: ...

        @overload
        def list_credentials(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                list_credentials_request: Optional[ListCredentialsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                expiresin: Optional[int] = ..., 
                **kwargs: Any
            ) -> EndpointAccessResource: ...

        @overload
        def list_credentials(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                list_credentials_request: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                expiresin: Optional[int] = ..., 
                **kwargs: Any
            ) -> EndpointAccessResource: ...

        @overload
        def list_credentials(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                list_credentials_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                expiresin: Optional[int] = ..., 
                **kwargs: Any
            ) -> EndpointAccessResource: ...

        @overload
        def list_ingress_gateway_credentials(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                list_ingress_gateway_credentials_request: Optional[ListIngressGatewayCredentialsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                expiresin: Optional[int] = ..., 
                **kwargs: Any
            ) -> IngressGatewayResource: ...

        @overload
        def list_ingress_gateway_credentials(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                list_ingress_gateway_credentials_request: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                expiresin: Optional[int] = ..., 
                **kwargs: Any
            ) -> IngressGatewayResource: ...

        @overload
        def list_ingress_gateway_credentials(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                list_ingress_gateway_credentials_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                expiresin: Optional[int] = ..., 
                **kwargs: Any
            ) -> IngressGatewayResource: ...

        @overload
        def list_managed_proxy_details(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                managed_proxy_request: ManagedProxyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedProxyResource: ...

        @overload
        def list_managed_proxy_details(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                managed_proxy_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedProxyResource: ...

        @overload
        def list_managed_proxy_details(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                managed_proxy_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedProxyResource: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                endpoint_resource: EndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EndpointResource: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                endpoint_resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EndpointResource: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                endpoint_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EndpointResource: ...


    class azure.mgmt.hybridconnectivity.operations.GenerateAwsTemplateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def post(
                self, 
                generate_aws_template_request: GenerateAwsTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...

        @overload
        def post(
                self, 
                generate_aws_template_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...

        @overload
        def post(
                self, 
                generate_aws_template_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...


    class azure.mgmt.hybridconnectivity.operations.InventoryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                inventory_id: str, 
                **kwargs: Any
            ) -> InventoryResource: ...

        @distributed_trace
        def list_by_solution_configuration(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                **kwargs: Any
            ) -> Iterable[InventoryResource]: ...


    class azure.mgmt.hybridconnectivity.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.hybridconnectivity.operations.PublicCloudConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                resource: PublicCloudConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PublicCloudConnector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PublicCloudConnector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PublicCloudConnector]: ...

        @distributed_trace
        def begin_test_permissions(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                **kwargs: Any
            ) -> PublicCloudConnector: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[PublicCloudConnector]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[PublicCloudConnector]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                properties: PublicCloudConnectorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PublicCloudConnector: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PublicCloudConnector: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                public_cloud_connector: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PublicCloudConnector: ...


    class azure.mgmt.hybridconnectivity.operations.ServiceConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_orupdate(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                service_configuration_resource: ServiceConfigurationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...

        @overload
        def create_orupdate(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                service_configuration_resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...

        @overload
        def create_orupdate(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                service_configuration_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...

        @distributed_trace
        def list_by_endpoint_resource(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Iterable[ServiceConfigurationResource]: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                service_configuration_resource: ServiceConfigurationResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                service_configuration_resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                endpoint_name: str, 
                service_configuration_name: str, 
                service_configuration_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceConfigurationResource: ...


    class azure.mgmt.hybridconnectivity.operations.SolutionConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_sync_now(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                resource: SolutionConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionConfiguration: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionConfiguration: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionConfiguration: ...

        @distributed_trace
        def delete(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                **kwargs: Any
            ) -> SolutionConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> Iterable[SolutionConfiguration]: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                properties: SolutionConfigurationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionConfiguration: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionConfiguration: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                solution_configuration: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionConfiguration: ...


    class azure.mgmt.hybridconnectivity.operations.SolutionTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                solution_type: str, 
                **kwargs: Any
            ) -> SolutionTypeResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[SolutionTypeResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[SolutionTypeResource]: ...


```