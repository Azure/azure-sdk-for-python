```py
namespace azure.mgmt.hybridconnectivity

    class azure.mgmt.hybridconnectivity.HybridConnectivityMgmtClient: implements ContextManager 
        endpoints: EndpointsOperations
        generate_aws_template: GenerateAwsTemplateOperations
        generate_gcp_template: GenerateGcpTemplateOperations
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


namespace azure.mgmt.hybridconnectivity.aio

    class azure.mgmt.hybridconnectivity.aio.HybridConnectivityMgmtClient: implements AsyncContextManager 
        endpoints: EndpointsOperations
        generate_aws_template: GenerateAwsTemplateOperations
        generate_gcp_template: GenerateGcpTemplateOperations
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
            ) -> AsyncItemPaged[EndpointResource]: ...

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
            ) -> GenerateAwsTemplateResponse: ...

        @overload
        async def post(
                self, 
                generate_aws_template_request: GenerateAwsTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GenerateAwsTemplateResponse: ...

        @overload
        async def post(
                self, 
                generate_aws_template_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GenerateAwsTemplateResponse: ...


    class azure.mgmt.hybridconnectivity.aio.operations.GenerateGcpTemplateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def post(
                self, 
                generate_gcp_template_request: GenerateGcpTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GenerateGcpTemplateResponse: ...

        @overload
        async def post(
                self, 
                generate_gcp_template_request: GenerateGcpTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GenerateGcpTemplateResponse: ...

        @overload
        async def post(
                self, 
                generate_gcp_template_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GenerateGcpTemplateResponse: ...


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
            ) -> AsyncItemPaged[InventoryResource]: ...


    class azure.mgmt.hybridconnectivity.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


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
            ) -> AsyncItemPaged[PublicCloudConnector]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[PublicCloudConnector]: ...

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
            ) -> AsyncItemPaged[ServiceConfigurationResource]: ...

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
            ) -> AsyncItemPaged[SolutionConfiguration]: ...

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
            ) -> AsyncItemPaged[SolutionTypeResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SolutionTypeResource]: ...


namespace azure.mgmt.hybridconnectivity.models

    class azure.mgmt.hybridconnectivity.models.AADProfileProperties(_Model):
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


    class azure.mgmt.hybridconnectivity.models.AwsCloudProfile(_Model):
        account_id: str
        excluded_accounts: Optional[list[str]]
        is_organizational_account: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                account_id: str, 
                excluded_accounts: Optional[list[str]] = ..., 
                is_organizational_account: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.AwsCloudProfileUpdate(_Model):
        excluded_accounts: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                excluded_accounts: Optional[list[str]] = ...
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


    class azure.mgmt.hybridconnectivity.models.EndpointAccessResource(_Model):
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


    class azure.mgmt.hybridconnectivity.models.EndpointProperties(_Model):
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


    class azure.mgmt.hybridconnectivity.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.hybridconnectivity.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.hybridconnectivity.models.ErrorResponse(_Model):
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


    class azure.mgmt.hybridconnectivity.models.GcpCloudProfile(_Model):
        organization_properties: Optional[GcpOrganizationProperties]
        project_properties: Optional[GcpProjectProperties]

        @overload
        def __init__(
                self, 
                *, 
                organization_properties: Optional[GcpOrganizationProperties] = ..., 
                project_properties: Optional[GcpProjectProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.GcpCloudProfileUpdate(_Model):
        organization_properties: Optional[GcpOrganizationPropertiesUpdate]

        @overload
        def __init__(
                self, 
                *, 
                organization_properties: Optional[GcpOrganizationPropertiesUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.GcpOrganizationProperties(_Model):
        excluded_folder_ids: Optional[list[str]]
        excluded_project_numbers: Optional[list[str]]
        management_project_id: str
        management_project_number: str
        organization_id: str

        @overload
        def __init__(
                self, 
                *, 
                excluded_folder_ids: Optional[list[str]] = ..., 
                excluded_project_numbers: Optional[list[str]] = ..., 
                management_project_id: str, 
                management_project_number: str, 
                organization_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.GcpOrganizationPropertiesUpdate(_Model):
        excluded_folder_ids: Optional[list[str]]
        excluded_project_numbers: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                excluded_folder_ids: Optional[list[str]] = ..., 
                excluded_project_numbers: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.GcpProjectProperties(_Model):
        project_id: str
        project_number: str

        @overload
        def __init__(
                self, 
                *, 
                project_id: str, 
                project_number: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.GcpTemplateFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHELL_SCRIPT = "shellscript"
        TERRAFORM = "terraform"


    class azure.mgmt.hybridconnectivity.models.GenerateAwsTemplateRequest(_Model):
        connector_id: str
        solution_types: Optional[list[SolutionTypeSettings]]

        @overload
        def __init__(
                self, 
                *, 
                connector_id: str, 
                solution_types: Optional[list[SolutionTypeSettings]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.GenerateAwsTemplateResponse(_Model):


    class azure.mgmt.hybridconnectivity.models.GenerateGcpTemplateRequest(_Model):
        connector_id: str
        gcp_cloud_profile: Optional[GcpCloudProfile]
        gcp_template_format: Optional[Union[str, GcpTemplateFormat]]
        solution_types: Optional[list[SolutionTypeSettings]]

        @overload
        def __init__(
                self, 
                *, 
                connector_id: str, 
                gcp_cloud_profile: Optional[GcpCloudProfile] = ..., 
                gcp_template_format: Optional[Union[str, GcpTemplateFormat]] = ..., 
                solution_types: Optional[list[SolutionTypeSettings]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.GenerateGcpTemplateResponse(_Model):


    class azure.mgmt.hybridconnectivity.models.HostType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS = "AWS"
        GCP = "GCP"


    class azure.mgmt.hybridconnectivity.models.IngressGatewayResource(_Model):
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


    class azure.mgmt.hybridconnectivity.models.IngressProfileProperties(_Model):
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


    class azure.mgmt.hybridconnectivity.models.InventoryProperties(_Model):
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


    class azure.mgmt.hybridconnectivity.models.ListCredentialsRequest(_Model):
        service_name: Optional[Union[str, ServiceName]]

        @overload
        def __init__(
                self, 
                *, 
                service_name: Optional[Union[str, ServiceName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ListIngressGatewayCredentialsRequest(_Model):
        service_name: Optional[Union[str, ServiceName]]

        @overload
        def __init__(
                self, 
                *, 
                service_name: Optional[Union[str, ServiceName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.ManagedProxyRequest(_Model):
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


    class azure.mgmt.hybridconnectivity.models.ManagedProxyResource(_Model):
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


    class azure.mgmt.hybridconnectivity.models.Operation(_Model):
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


    class azure.mgmt.hybridconnectivity.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.hybridconnectivity.models.OperationStatusResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
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
                operations: Optional[list[OperationStatusResult]] = ..., 
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
        kind: Optional[Union[str, HostType]]
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
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.PublicCloudConnectorProperties(_Model):
        aws_cloud_profile: Optional[AwsCloudProfile]
        connector_primary_identifier: Optional[str]
        gcp_cloud_profile: Optional[GcpCloudProfile]
        host_type: Union[str, HostType]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                aws_cloud_profile: Optional[AwsCloudProfile] = ..., 
                gcp_cloud_profile: Optional[GcpCloudProfile] = ..., 
                host_type: Union[str, HostType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.PublicCloudConnectorPropertiesUpdate(_Model):
        aws_cloud_profile: Optional[AwsCloudProfileUpdate]
        gcp_cloud_profile: Optional[GcpCloudProfileUpdate]

        @overload
        def __init__(
                self, 
                *, 
                aws_cloud_profile: Optional[AwsCloudProfileUpdate] = ..., 
                gcp_cloud_profile: Optional[GcpCloudProfileUpdate] = ...
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
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.RelayNamespaceAccessProperties(_Model):
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


    class azure.mgmt.hybridconnectivity.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.hybridconnectivity.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.hybridconnectivity.models.ServiceConfigurationProperties(_Model):
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


    class azure.mgmt.hybridconnectivity.models.ServiceConfigurationPropertiesPatch(_Model):
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


    class azure.mgmt.hybridconnectivity.models.ServiceConfigurationResourcePatch(_Model):
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


    class azure.mgmt.hybridconnectivity.models.SolutionConfigurationProperties(_Model):
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


    class azure.mgmt.hybridconnectivity.models.SolutionConfigurationPropertiesUpdate(_Model):
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


    class azure.mgmt.hybridconnectivity.models.SolutionSettings(_Model):


    class azure.mgmt.hybridconnectivity.models.SolutionTypeProperties(_Model):
        description: Optional[str]
        host_types: Optional[list[Union[str, HostType]]]
        solution_settings: Optional[list[SolutionTypeSettingsProperties]]
        solution_type: Optional[str]
        supported_azure_regions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                host_types: Optional[list[Union[str, HostType]]] = ..., 
                solution_settings: Optional[list[SolutionTypeSettingsProperties]] = ..., 
                solution_type: Optional[str] = ..., 
                supported_azure_regions: Optional[list[str]] = ...
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


    class azure.mgmt.hybridconnectivity.models.SolutionTypeSettings(_Model):
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


    class azure.mgmt.hybridconnectivity.models.SolutionTypeSettingsProperties(_Model):
        allowed_values: list[str]
        default_value: str
        description: str
        display_name: str
        host_types: list[Union[str, HostType]]
        name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                allowed_values: list[str], 
                default_value: str, 
                description: str, 
                display_name: str, 
                host_types: list[Union[str, HostType]], 
                name: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.hybridconnectivity.models.SystemData(_Model):
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


    class azure.mgmt.hybridconnectivity.models.TrackedResourceUpdate(Resource):
        id: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
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
            ) -> None: ...

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
            ) -> ItemPaged[EndpointResource]: ...

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
            ) -> None: ...

        @overload
        def post(
                self, 
                generate_aws_template_request: GenerateAwsTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GenerateAwsTemplateResponse: ...

        @overload
        def post(
                self, 
                generate_aws_template_request: GenerateAwsTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GenerateAwsTemplateResponse: ...

        @overload
        def post(
                self, 
                generate_aws_template_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GenerateAwsTemplateResponse: ...


    class azure.mgmt.hybridconnectivity.operations.GenerateGcpTemplateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def post(
                self, 
                generate_gcp_template_request: GenerateGcpTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GenerateGcpTemplateResponse: ...

        @overload
        def post(
                self, 
                generate_gcp_template_request: GenerateGcpTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GenerateGcpTemplateResponse: ...

        @overload
        def post(
                self, 
                generate_gcp_template_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GenerateGcpTemplateResponse: ...


    class azure.mgmt.hybridconnectivity.operations.InventoryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[InventoryResource]: ...


    class azure.mgmt.hybridconnectivity.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.hybridconnectivity.operations.PublicCloudConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[PublicCloudConnector]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[PublicCloudConnector]: ...

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
            ) -> None: ...

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
            ) -> ItemPaged[ServiceConfigurationResource]: ...

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
            ) -> None: ...

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
            ) -> ItemPaged[SolutionConfiguration]: ...

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
            ) -> None: ...

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
            ) -> ItemPaged[SolutionTypeResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SolutionTypeResource]: ...


namespace azure.mgmt.hybridconnectivity.types

    class azure.mgmt.hybridconnectivity.types.AwsCloudProfile(TypedDict, total=False):
        key "accountId": Required[str]
        key "isOrganizationalAccount": bool
        accountId: str
        excludedAccounts: list[str]
        isOrganizationalAccount: bool


    class azure.mgmt.hybridconnectivity.types.AwsCloudProfileUpdate(TypedDict, total=False):
        excludedAccounts: list[str]


    class azure.mgmt.hybridconnectivity.types.EndpointProperties(TypedDict, total=False):
        key "provisioningState": str
        key "resourceId": str
        key "type": Required[Union[str, Type]]
        provisioningState: str
        resourceId: str
        type: Union[str, Type]


    class azure.mgmt.hybridconnectivity.types.EndpointResource(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EndpointProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EndpointProperties
        systemData: SystemData
        type: str


    class azure.mgmt.hybridconnectivity.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.hybridconnectivity.types.GcpCloudProfile(TypedDict, total=False):
        key "organizationProperties": ForwardRef('GcpOrganizationProperties', module='types')
        key "projectProperties": ForwardRef('GcpProjectProperties', module='types')
        organizationProperties: GcpOrganizationProperties
        projectProperties: GcpProjectProperties


    class azure.mgmt.hybridconnectivity.types.GcpCloudProfileUpdate(TypedDict, total=False):
        key "organizationProperties": ForwardRef('GcpOrganizationPropertiesUpdate', module='types')
        organizationProperties: GcpOrganizationPropertiesUpdate


    class azure.mgmt.hybridconnectivity.types.GcpOrganizationProperties(TypedDict, total=False):
        key "managementProjectId": Required[str]
        key "managementProjectNumber": Required[str]
        key "organizationId": Required[str]
        excludedFolderIds: list[str]
        excludedProjectNumbers: list[str]
        managementProjectId: str
        managementProjectNumber: str
        organizationId: str


    class azure.mgmt.hybridconnectivity.types.GcpOrganizationPropertiesUpdate(TypedDict, total=False):
        excludedFolderIds: list[str]
        excludedProjectNumbers: list[str]


    class azure.mgmt.hybridconnectivity.types.GcpProjectProperties(TypedDict, total=False):
        key "projectId": Required[str]
        key "projectNumber": Required[str]
        projectId: str
        projectNumber: str


    class azure.mgmt.hybridconnectivity.types.GenerateAwsTemplateRequest(TypedDict, total=False):
        key "connectorId": Required[str]
        connectorId: str
        solutionTypes: list[SolutionTypeSettings]


    class azure.mgmt.hybridconnectivity.types.GenerateGcpTemplateRequest(TypedDict, total=False):
        key "connectorId": Required[str]
        key "gcpCloudProfile": ForwardRef('GcpCloudProfile', module='types')
        key "gcpTemplateFormat": Union[str, GcpTemplateFormat]
        connectorId: str
        gcpCloudProfile: GcpCloudProfile
        gcpTemplateFormat: Union[str, GcpTemplateFormat]
        solutionTypes: list[SolutionTypeSettings]


    class azure.mgmt.hybridconnectivity.types.ListCredentialsRequest(TypedDict, total=False):
        key "serviceName": Union[str, ServiceName]
        serviceName: Union[str, ServiceName]


    class azure.mgmt.hybridconnectivity.types.ListIngressGatewayCredentialsRequest(TypedDict, total=False):
        key "serviceName": Union[str, ServiceName]
        serviceName: Union[str, ServiceName]


    class azure.mgmt.hybridconnectivity.types.ManagedProxyRequest(TypedDict, total=False):
        key "hostname": str
        key "service": Required[str]
        key "serviceName": Union[str, ServiceName]
        hostname: str
        service: str
        serviceName: Union[str, ServiceName]


    class azure.mgmt.hybridconnectivity.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.hybridconnectivity.types.PublicCloudConnector(TrackedResource):
        key "id": str
        key "kind": Union[str, HostType]
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('PublicCloudConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Union[str, HostType]
        location: str
        name: str
        properties: PublicCloudConnectorProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.hybridconnectivity.types.PublicCloudConnectorProperties(TypedDict, total=False):
        key "awsCloudProfile": ForwardRef('AwsCloudProfile', module='types')
        key "connectorPrimaryIdentifier": str
        key "gcpCloudProfile": ForwardRef('GcpCloudProfile', module='types')
        key "hostType": Required[Union[str, HostType]]
        key "provisioningState": Union[str, ResourceProvisioningState]
        awsCloudProfile: AwsCloudProfile
        connectorPrimaryIdentifier: str
        gcpCloudProfile: GcpCloudProfile
        hostType: Union[str, HostType]
        provisioningState: Union[str, ResourceProvisioningState]


    class azure.mgmt.hybridconnectivity.types.PublicCloudConnectorPropertiesUpdate(TypedDict, total=False):
        key "awsCloudProfile": ForwardRef('AwsCloudProfileUpdate', module='types')
        key "gcpCloudProfile": ForwardRef('GcpCloudProfileUpdate', module='types')
        awsCloudProfile: AwsCloudProfileUpdate
        gcpCloudProfile: GcpCloudProfileUpdate


    class azure.mgmt.hybridconnectivity.types.PublicCloudConnectorUpdate(TrackedResourceUpdate):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PublicCloudConnectorPropertiesUpdate', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PublicCloudConnectorPropertiesUpdate
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.hybridconnectivity.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.hybridconnectivity.types.ServiceConfigurationProperties(TypedDict, total=False):
        key "port": int
        key "provisioningState": Union[str, ProvisioningState]
        key "resourceId": str
        key "serviceName": Required[Union[str, ServiceName]]
        port: int
        provisioningState: Union[str, ProvisioningState]
        resourceId: str
        serviceName: Union[str, ServiceName]


    class azure.mgmt.hybridconnectivity.types.ServiceConfigurationPropertiesPatch(TypedDict, total=False):
        key "port": int
        port: int


    class azure.mgmt.hybridconnectivity.types.ServiceConfigurationResource(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ServiceConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ServiceConfigurationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.hybridconnectivity.types.ServiceConfigurationResourcePatch(TypedDict, total=False):
        key "properties": ForwardRef('ServiceConfigurationPropertiesPatch', module='types')
        properties: ServiceConfigurationPropertiesPatch


    class azure.mgmt.hybridconnectivity.types.SolutionConfiguration(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SolutionConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SolutionConfigurationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.hybridconnectivity.types.SolutionConfigurationProperties(TypedDict, total=False):
        key "lastSyncTime": str
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "solutionSettings": ForwardRef('SolutionSettings', module='types')
        key "solutionType": Required[str]
        key "status": Union[str, SolutionConfigurationStatus]
        key "statusDetails": str
        lastSyncTime: str
        provisioningState: Union[str, ResourceProvisioningState]
        solutionSettings: SolutionSettings
        solutionType: str
        status: Union[str, SolutionConfigurationStatus]
        statusDetails: str


    class azure.mgmt.hybridconnectivity.types.SolutionConfigurationPropertiesUpdate(TypedDict, total=False):
        key "solutionSettings": ForwardRef('SolutionSettings', module='types')
        key "solutionType": str
        solutionSettings: SolutionSettings
        solutionType: str


    class azure.mgmt.hybridconnectivity.types.SolutionConfigurationUpdate(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SolutionConfigurationPropertiesUpdate', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SolutionConfigurationPropertiesUpdate
        systemData: SystemData
        type: str


    class azure.mgmt.hybridconnectivity.types.SolutionSettings(TypedDict, total=False):


    class azure.mgmt.hybridconnectivity.types.SolutionTypeSettings(TypedDict, total=False):
        key "solutionSettings": ForwardRef('SolutionSettings', module='types')
        key "solutionType": Required[str]
        solutionSettings: SolutionSettings
        solutionType: str


    class azure.mgmt.hybridconnectivity.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.hybridconnectivity.types.TrackedResource(Resource):
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


    class azure.mgmt.hybridconnectivity.types.TrackedResourceUpdate(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


```