```py
namespace azure.mgmt.servicenetworking

    class azure.mgmt.servicenetworking.ServiceNetworkingMgmtClient: implements ContextManager 
        associations_interface: AssociationsInterfaceOperations
        frontends_interface: FrontendsInterfaceOperations
        operations: Operations
        private_endpoint_connections_interface: PrivateEndpointConnectionsInterfaceOperations
        private_link_resources_interface: PrivateLinkResourcesInterfaceOperations
        security_policies_interface: SecurityPoliciesInterfaceOperations
        traffic_controller_interface: TrafficControllerInterfaceOperations

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


namespace azure.mgmt.servicenetworking.aio

    class azure.mgmt.servicenetworking.aio.ServiceNetworkingMgmtClient: implements AsyncContextManager 
        associations_interface: AssociationsInterfaceOperations
        frontends_interface: FrontendsInterfaceOperations
        operations: Operations
        private_endpoint_connections_interface: PrivateEndpointConnectionsInterfaceOperations
        private_link_resources_interface: PrivateLinkResourcesInterfaceOperations
        security_policies_interface: SecurityPoliciesInterfaceOperations
        traffic_controller_interface: TrafficControllerInterfaceOperations

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


namespace azure.mgmt.servicenetworking.aio.operations

    class azure.mgmt.servicenetworking.aio.operations.AssociationsInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                resource: Association, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Association]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                resource: Association, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Association]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Association]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                **kwargs: Any
            ) -> Association: ...

        @distributed_trace
        def list_by_traffic_controller(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Association]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                properties: AssociationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Association: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                properties: AssociationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Association: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Association: ...


    class azure.mgmt.servicenetworking.aio.operations.FrontendsInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                resource: Frontend, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Frontend]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                resource: Frontend, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Frontend]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Frontend]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                **kwargs: Any
            ) -> Frontend: ...

        @distributed_trace
        def list_by_traffic_controller(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Frontend]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                properties: FrontendUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Frontend: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                properties: FrontendUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Frontend: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Frontend: ...


    class azure.mgmt.servicenetworking.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.servicenetworking.aio.operations.PrivateEndpointConnectionsInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'private_endpoint_connection_name']}, api_versions_list=['2026-03-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2026-03-01'])
        async def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'accept']}, api_versions_list=['2026-03-01'])
        def list_by_traffic_controller(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.servicenetworking.aio.operations.PrivateLinkResourcesInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2026-03-01'])
        async def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'accept']}, api_versions_list=['2026-03-01'])
        def list_by_traffic_controller(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.servicenetworking.aio.operations.SecurityPoliciesInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                resource: SecurityPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                resource: SecurityPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityPolicy]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'security_policy_name']}, api_versions_list=['2024-05-01-preview', '2025-01-01', '2025-03-01-preview', '2026-03-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'security_policy_name', 'accept']}, api_versions_list=['2024-05-01-preview', '2025-01-01', '2025-03-01-preview', '2026-03-01'])
        async def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> SecurityPolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'accept']}, api_versions_list=['2024-05-01-preview', '2025-01-01', '2025-03-01-preview', '2026-03-01'])
        def list_by_traffic_controller(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityPolicy]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                properties: SecurityPolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityPolicy: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                properties: SecurityPolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityPolicy: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityPolicy: ...


    class azure.mgmt.servicenetworking.aio.operations.TrafficControllerInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                resource: TrafficController, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TrafficController]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                resource: TrafficController, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TrafficController]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TrafficController]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> TrafficController: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TrafficController]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[TrafficController]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                properties: TrafficControllerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficController: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                properties: TrafficControllerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficController: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficController: ...


namespace azure.mgmt.servicenetworking.models

    class azure.mgmt.servicenetworking.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.servicenetworking.models.Association(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AssociationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AssociationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.AssociationProperties(_Model):
        association_type: Union[str, AssociationType]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        subnet: Optional[AssociationSubnet]

        @overload
        def __init__(
                self, 
                *, 
                association_type: Union[str, AssociationType], 
                subnet: Optional[AssociationSubnet] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.AssociationSubnet(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.AssociationSubnetUpdate(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.AssociationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SUBNETS = "subnets"


    class azure.mgmt.servicenetworking.models.AssociationUpdate(_Model):
        properties: Optional[AssociationUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AssociationUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicenetworking.models.AssociationUpdateProperties(_Model):
        association_type: Optional[Union[str, AssociationType]]
        subnet: Optional[AssociationSubnetUpdate]

        @overload
        def __init__(
                self, 
                *, 
                association_type: Optional[Union[str, AssociationType]] = ..., 
                subnet: Optional[AssociationSubnetUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.servicenetworking.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.servicenetworking.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.servicenetworking.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.Frontend(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[FrontendProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[FrontendProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.FrontendAssociation(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.FrontendProperties(_Model):
        association: Optional[FrontendAssociation]
        fqdn: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        security_policy_configurations: Optional[SecurityPolicyConfigurations]

        @overload
        def __init__(
                self, 
                *, 
                association: Optional[FrontendAssociation] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                security_policy_configurations: Optional[SecurityPolicyConfigurations] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.FrontendUpdate(_Model):
        properties: Optional[FrontendUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FrontendUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.FrontendUpdateProperties(_Model):
        association: Optional[FrontendAssociation]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        security_policy_configurations: Optional[SecurityPolicyConfigurations]

        @overload
        def __init__(
                self, 
                *, 
                association: Optional[FrontendAssociation] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                security_policy_configurations: Optional[SecurityPolicyConfigurations] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.IpAccessRule(_Model):
        action: Union[str, IpAccessRuleAction]
        name: str
        priority: int
        source_address_prefixes: list[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, IpAccessRuleAction], 
                name: str, 
                priority: int, 
                source_address_prefixes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.IpAccessRuleAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "allow"
        DENY = "deny"


    class azure.mgmt.servicenetworking.models.IpAccessRulesPolicy(_Model):
        rules: Optional[list[IpAccessRule]]

        @overload
        def __init__(
                self, 
                *, 
                rules: Optional[list[IpAccessRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.IpAccessRulesSecurityPolicy(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.Operation(_Model):
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


    class azure.mgmt.servicenetworking.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.servicenetworking.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.servicenetworking.models.PolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IP_ACCESS_RULES = "ipAccessRules"
        WAF = "waf"


    class azure.mgmt.servicenetworking.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.PrivateEndpointConnectionProperties(_Model):
        private_endpoint: Optional[PrivateEndpointReference]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.PrivateEndpointReference(_Model):
        id: Optional[str]


    class azure.mgmt.servicenetworking.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]


    class azure.mgmt.servicenetworking.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateLinkServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateLinkServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.PrivateLinkServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.servicenetworking.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.servicenetworking.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.servicenetworking.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.servicenetworking.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.servicenetworking.models.ResourceId(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.SecurityPolicy(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[SecurityPolicyProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SecurityPolicyProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.SecurityPolicyConfigurations(_Model):
        ip_access_rules_security_policy: Optional[IpAccessRulesSecurityPolicy]
        waf_security_policy: Optional[WafSecurityPolicy]

        @overload
        def __init__(
                self, 
                *, 
                ip_access_rules_security_policy: Optional[IpAccessRulesSecurityPolicy] = ..., 
                waf_security_policy: Optional[WafSecurityPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.SecurityPolicyProperties(_Model):
        ip_access_rules_policy: Optional[IpAccessRulesPolicy]
        policy_type: Optional[Union[str, PolicyType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        waf_policy: Optional[WafPolicy]

        @overload
        def __init__(
                self, 
                *, 
                ip_access_rules_policy: Optional[IpAccessRulesPolicy] = ..., 
                waf_policy: Optional[WafPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.SecurityPolicyUpdate(_Model):
        properties: Optional[SecurityPolicyUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityPolicyUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.SecurityPolicyUpdateProperties(_Model):
        ip_access_rules_policy: Optional[IpAccessRulesPolicy]
        waf_policy: Optional[WafPolicy]

        @overload
        def __init__(
                self, 
                *, 
                ip_access_rules_policy: Optional[IpAccessRulesPolicy] = ..., 
                waf_policy: Optional[WafPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.SystemData(_Model):
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


    class azure.mgmt.servicenetworking.models.TrackedResource(Resource):
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


    class azure.mgmt.servicenetworking.models.TrafficController(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[TrafficControllerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[TrafficControllerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.TrafficControllerProperties(_Model):
        associations: Optional[list[ResourceId]]
        configuration_endpoints: Optional[list[str]]
        frontends: Optional[list[ResourceId]]
        private_endpoint_connections: Optional[list[ResourceId]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        security_policies: Optional[list[ResourceId]]
        security_policy_configurations: Optional[SecurityPolicyConfigurations]

        @overload
        def __init__(
                self, 
                *, 
                security_policy_configurations: Optional[SecurityPolicyConfigurations] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.TrafficControllerUpdate(_Model):
        properties: Optional[TrafficControllerUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TrafficControllerUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.TrafficControllerUpdateProperties(_Model):
        security_policy_configurations: Optional[SecurityPolicyConfigurations]

        @overload
        def __init__(
                self, 
                *, 
                security_policy_configurations: Optional[SecurityPolicyConfigurations] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.WafPolicy(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.WafSecurityPolicy(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.servicenetworking.operations

    class azure.mgmt.servicenetworking.operations.AssociationsInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                resource: Association, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Association]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                resource: Association, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Association]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Association]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                **kwargs: Any
            ) -> Association: ...

        @distributed_trace
        def list_by_traffic_controller(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Association]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                properties: AssociationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Association: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                properties: AssociationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Association: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                association_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Association: ...


    class azure.mgmt.servicenetworking.operations.FrontendsInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                resource: Frontend, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Frontend]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                resource: Frontend, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Frontend]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Frontend]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                **kwargs: Any
            ) -> Frontend: ...

        @distributed_trace
        def list_by_traffic_controller(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Frontend]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                properties: FrontendUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Frontend: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                properties: FrontendUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Frontend: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                frontend_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Frontend: ...


    class azure.mgmt.servicenetworking.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.servicenetworking.operations.PrivateEndpointConnectionsInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'private_endpoint_connection_name']}, api_versions_list=['2026-03-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2026-03-01'])
        def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'accept']}, api_versions_list=['2026-03-01'])
        def list_by_traffic_controller(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.servicenetworking.operations.PrivateLinkResourcesInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2026-03-01'])
        def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'accept']}, api_versions_list=['2026-03-01'])
        def list_by_traffic_controller(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.servicenetworking.operations.SecurityPoliciesInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                resource: SecurityPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecurityPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                resource: SecurityPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecurityPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecurityPolicy]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'security_policy_name']}, api_versions_list=['2024-05-01-preview', '2025-01-01', '2025-03-01-preview', '2026-03-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'security_policy_name', 'accept']}, api_versions_list=['2024-05-01-preview', '2025-01-01', '2025-03-01-preview', '2026-03-01'])
        def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> SecurityPolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'accept']}, api_versions_list=['2024-05-01-preview', '2025-01-01', '2025-03-01-preview', '2026-03-01'])
        def list_by_traffic_controller(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SecurityPolicy]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                properties: SecurityPolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityPolicy: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                properties: SecurityPolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityPolicy: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityPolicy: ...


    class azure.mgmt.servicenetworking.operations.TrafficControllerInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                resource: TrafficController, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TrafficController]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                resource: TrafficController, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TrafficController]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TrafficController]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> TrafficController: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TrafficController]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[TrafficController]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                properties: TrafficControllerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficController: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                properties: TrafficControllerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficController: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TrafficController: ...


namespace azure.mgmt.servicenetworking.types

    class azure.mgmt.servicenetworking.types.Association(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AssociationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: AssociationProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicenetworking.types.AssociationProperties(TypedDict, total=False):
        key "associationType": Required[Union[str, AssociationType]]
        key "provisioningState": Union[str, ProvisioningState]
        key "subnet": ForwardRef('AssociationSubnet', module='types')
        associationType: Union[str, AssociationType]
        provisioningState: Union[str, ProvisioningState]
        subnet: AssociationSubnet


    class azure.mgmt.servicenetworking.types.AssociationSubnet(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.servicenetworking.types.AssociationSubnetUpdate(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.servicenetworking.types.AssociationUpdate(TypedDict, total=False):
        key "properties": ForwardRef('AssociationUpdateProperties', module='types')
        properties: AssociationUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.servicenetworking.types.AssociationUpdateProperties(TypedDict, total=False):
        key "associationType": Union[str, AssociationType]
        key "subnet": ForwardRef('AssociationSubnetUpdate', module='types')
        associationType: Union[str, AssociationType]
        subnet: AssociationSubnetUpdate


    class azure.mgmt.servicenetworking.types.Frontend(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('FrontendProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: FrontendProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicenetworking.types.FrontendAssociation(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.servicenetworking.types.FrontendProperties(TypedDict, total=False):
        key "association": ForwardRef('FrontendAssociation', module='types')
        key "fqdn": str
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "securityPolicyConfigurations": ForwardRef('SecurityPolicyConfigurations', module='types')
        association: FrontendAssociation
        fqdn: str
        provisioningState: Union[str, ProvisioningState]
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        securityPolicyConfigurations: SecurityPolicyConfigurations


    class azure.mgmt.servicenetworking.types.FrontendUpdate(TypedDict, total=False):
        key "properties": ForwardRef('FrontendUpdateProperties', module='types')
        properties: FrontendUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.servicenetworking.types.FrontendUpdateProperties(TypedDict, total=False):
        key "association": ForwardRef('FrontendAssociation', module='types')
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "securityPolicyConfigurations": ForwardRef('SecurityPolicyConfigurations', module='types')
        association: FrontendAssociation
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        securityPolicyConfigurations: SecurityPolicyConfigurations


    class azure.mgmt.servicenetworking.types.IpAccessRule(TypedDict, total=False):
        key "action": Required[Union[str, IpAccessRuleAction]]
        key "name": Required[str]
        key "priority": Required[int]
        key "sourceAddressPrefixes": Required[list[str]]
        action: Union[str, IpAccessRuleAction]
        name: str
        priority: int
        sourceAddressPrefixes: list[str]


    class azure.mgmt.servicenetworking.types.IpAccessRulesPolicy(TypedDict, total=False):
        rules: list[IpAccessRule]


    class azure.mgmt.servicenetworking.types.IpAccessRulesSecurityPolicy(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.servicenetworking.types.PrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.servicenetworking.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpointReference', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, ProvisioningState]
        privateEndpoint: PrivateEndpointReference
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.servicenetworking.types.PrivateEndpointReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.servicenetworking.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateLinkServiceConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PrivateLinkServiceConnectionStatus]


    class azure.mgmt.servicenetworking.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.servicenetworking.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.servicenetworking.types.ResourceId(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.servicenetworking.types.SecurityPolicy(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SecurityPolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SecurityPolicyProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicenetworking.types.SecurityPolicyConfigurations(TypedDict, total=False):
        key "ipAccessRulesSecurityPolicy": ForwardRef('IpAccessRulesSecurityPolicy', module='types')
        key "wafSecurityPolicy": ForwardRef('WafSecurityPolicy', module='types')
        ipAccessRulesSecurityPolicy: IpAccessRulesSecurityPolicy
        wafSecurityPolicy: WafSecurityPolicy


    class azure.mgmt.servicenetworking.types.SecurityPolicyProperties(TypedDict, total=False):
        key "ipAccessRulesPolicy": ForwardRef('IpAccessRulesPolicy', module='types')
        key "policyType": Union[str, PolicyType]
        key "provisioningState": Union[str, ProvisioningState]
        key "wafPolicy": ForwardRef('WafPolicy', module='types')
        ipAccessRulesPolicy: IpAccessRulesPolicy
        policyType: Union[str, PolicyType]
        provisioningState: Union[str, ProvisioningState]
        wafPolicy: WafPolicy


    class azure.mgmt.servicenetworking.types.SecurityPolicyUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SecurityPolicyUpdateProperties', module='types')
        properties: SecurityPolicyUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.servicenetworking.types.SecurityPolicyUpdateProperties(TypedDict, total=False):
        key "ipAccessRulesPolicy": ForwardRef('IpAccessRulesPolicy', module='types')
        key "wafPolicy": ForwardRef('WafPolicy', module='types')
        ipAccessRulesPolicy: IpAccessRulesPolicy
        wafPolicy: WafPolicy


    class azure.mgmt.servicenetworking.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.servicenetworking.types.TrackedResource(Resource):
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


    class azure.mgmt.servicenetworking.types.TrafficController(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('TrafficControllerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: TrafficControllerProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicenetworking.types.TrafficControllerProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "securityPolicyConfigurations": ForwardRef('SecurityPolicyConfigurations', module='types')
        associations: list[ResourceId]
        configurationEndpoints: list[str]
        frontends: list[ResourceId]
        privateEndpointConnections: list[ResourceId]
        provisioningState: Union[str, ProvisioningState]
        securityPolicies: list[ResourceId]
        securityPolicyConfigurations: SecurityPolicyConfigurations


    class azure.mgmt.servicenetworking.types.TrafficControllerUpdate(TypedDict, total=False):
        key "properties": ForwardRef('TrafficControllerUpdateProperties', module='types')
        properties: TrafficControllerUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.servicenetworking.types.TrafficControllerUpdateProperties(TypedDict, total=False):
        key "securityPolicyConfigurations": ForwardRef('SecurityPolicyConfigurations', module='types')
        securityPolicyConfigurations: SecurityPolicyConfigurations


    class azure.mgmt.servicenetworking.types.WafPolicy(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.servicenetworking.types.WafSecurityPolicy(TypedDict, total=False):
        key "id": Required[str]
        id: str


```