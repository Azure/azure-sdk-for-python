```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.servicenetworking

    class azure.mgmt.servicenetworking.ServiceNetworkingMgmtClient: implements ContextManager 
        associations_interface: AssociationsInterfaceOperations
        frontends_interface: FrontendsInterfaceOperations
        operations: Operations
        security_policies_interface: SecurityPoliciesInterfaceOperations
        traffic_controller_interface: TrafficControllerInterfaceOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
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


namespace azure.mgmt.servicenetworking.aio

    class azure.mgmt.servicenetworking.aio.ServiceNetworkingMgmtClient: implements AsyncContextManager 
        associations_interface: AssociationsInterfaceOperations
        frontends_interface: FrontendsInterfaceOperations
        operations: Operations
        security_policies_interface: SecurityPoliciesInterfaceOperations
        traffic_controller_interface: TrafficControllerInterfaceOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
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
                resource: JSON, 
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
            ) -> AsyncIterable[Association]: ...

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
                properties: JSON, 
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
                resource: JSON, 
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
            ) -> AsyncIterable[Frontend]: ...

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
                properties: JSON, 
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
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'security_policy_name', 'accept']})
        async def begin_delete(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'security_policy_name', 'accept']})
        async def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> SecurityPolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'accept']})
        def list_by_traffic_controller(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SecurityPolicy]: ...

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
                properties: JSON, 
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
                resource: JSON, 
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
            ) -> AsyncIterable[TrafficController]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[TrafficController]: ...

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
                properties: JSON, 
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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.AssociationProperties(Model):
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


    class azure.mgmt.servicenetworking.models.AssociationSubnet(Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.AssociationSubnetUpdate(Model):
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


    class azure.mgmt.servicenetworking.models.AssociationUpdate(Model):
        properties: Optional[AssociationUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AssociationUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.AssociationUpdateProperties(Model):
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


    class azure.mgmt.servicenetworking.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.servicenetworking.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.servicenetworking.models.ErrorResponse(Model):
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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.FrontendProperties(Model):
        fqdn: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        security_policy_configurations: Optional[SecurityPolicyConfigurations]

        @overload
        def __init__(
                self, 
                *, 
                security_policy_configurations: Optional[SecurityPolicyConfigurations] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.FrontendUpdate(Model):
        properties: Optional[FrontendUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FrontendUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.FrontendUpdateProperties(Model):
        security_policy_configurations: Optional[SecurityPolicyConfigurations]

        @overload
        def __init__(
                self, 
                *, 
                security_policy_configurations: Optional[SecurityPolicyConfigurations] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.IpAccessRule(Model):
        action: Union[str, IpAccessRuleAction]
        name: str
        priority: int
        source_address_prefixes: List[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, IpAccessRuleAction], 
                name: str, 
                priority: int, 
                source_address_prefixes: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.IpAccessRuleAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "allow"
        DENY = "deny"


    class azure.mgmt.servicenetworking.models.IpAccessRulesPolicy(Model):
        rules: Optional[List[IpAccessRule]]

        @overload
        def __init__(
                self, 
                *, 
                rules: Optional[List[IpAccessRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.IpAccessRulesSecurityPolicy(Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.Operation(Model):
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


    class azure.mgmt.servicenetworking.models.OperationDisplay(Model):
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


    class azure.mgmt.servicenetworking.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.servicenetworking.models.Resource(Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.servicenetworking.models.ResourceId(Model):
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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.SecurityPolicyConfigurations(Model):
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


    class azure.mgmt.servicenetworking.models.SecurityPolicyProperties(Model):
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


    class azure.mgmt.servicenetworking.models.SecurityPolicyUpdate(Model):
        properties: Optional[SecurityPolicyUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityPolicyUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.SecurityPolicyUpdateProperties(Model):
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


    class azure.mgmt.servicenetworking.models.SystemData(Model):
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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.TrafficControllerProperties(Model):
        associations: Optional[List[ResourceId]]
        configuration_endpoints: Optional[List[str]]
        frontends: Optional[List[ResourceId]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        security_policies: Optional[List[ResourceId]]
        security_policy_configurations: Optional[SecurityPolicyConfigurations]

        @overload
        def __init__(
                self, 
                *, 
                security_policy_configurations: Optional[SecurityPolicyConfigurations] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.TrafficControllerUpdate(Model):
        properties: Optional[TrafficControllerUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TrafficControllerUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.TrafficControllerUpdateProperties(Model):
        security_policy_configurations: Optional[SecurityPolicyConfigurations]

        @overload
        def __init__(
                self, 
                *, 
                security_policy_configurations: Optional[SecurityPolicyConfigurations] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.WafPolicy(Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicenetworking.models.WafSecurityPolicy(Model):
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
            ): ...

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
                resource: JSON, 
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
            ) -> Iterable[Association]: ...

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
                properties: JSON, 
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
            ): ...

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
                resource: JSON, 
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
            ) -> Iterable[Frontend]: ...

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
                properties: JSON, 
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
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.servicenetworking.operations.SecurityPoliciesInterfaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'security_policy_name', 'accept']})
        def begin_delete(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'security_policy_name', 'accept']})
        def get(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> SecurityPolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'traffic_controller_name', 'accept']})
        def list_by_traffic_controller(
                self, 
                resource_group_name: str, 
                traffic_controller_name: str, 
                **kwargs: Any
            ) -> Iterable[SecurityPolicy]: ...

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
                properties: JSON, 
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
            ): ...

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
                resource: JSON, 
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
            ) -> Iterable[TrafficController]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[TrafficController]: ...

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
                properties: JSON, 
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


```