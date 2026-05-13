```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.iothubprovisioningservices

    class azure.mgmt.iothubprovisioningservices.IotDpsClient: implements ContextManager 
        dps_certificate: DpsCertificateOperations
        iot_dps_resource: IotDpsResourceOperations
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


namespace azure.mgmt.iothubprovisioningservices.aio

    class azure.mgmt.iothubprovisioningservices.aio.IotDpsClient: implements AsyncContextManager 
        dps_certificate: DpsCertificateOperations
        iot_dps_resource: IotDpsResourceOperations
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


namespace azure.mgmt.iothubprovisioningservices.aio.operations

    class azure.mgmt.iothubprovisioningservices.aio.operations.DpsCertificateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                certificate_description: CertificateResponse, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateResponse: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                certificate_description: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateResponse: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                certificate_description: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateResponse: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                *, 
                certificate_created: Optional[datetime] = ..., 
                certificate_has_private_key: Optional[bool] = ..., 
                certificate_is_verified: Optional[bool] = ..., 
                certificate_last_updated: Optional[datetime] = ..., 
                certificate_name1: Optional[str] = ..., 
                certificate_nonce: Optional[str] = ..., 
                certificate_purpose: Optional[Union[str, CertificatePurpose]] = ..., 
                certificate_raw_bytes: Optional[bytes] = ..., 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def generate_verification_code(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                *, 
                certificate_created: Optional[datetime] = ..., 
                certificate_has_private_key: Optional[bool] = ..., 
                certificate_is_verified: Optional[bool] = ..., 
                certificate_last_updated: Optional[datetime] = ..., 
                certificate_name1: Optional[str] = ..., 
                certificate_nonce: Optional[str] = ..., 
                certificate_purpose: Optional[Union[str, CertificatePurpose]] = ..., 
                certificate_raw_bytes: Optional[bytes] = ..., 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> VerificationCodeResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CertificateResponse]: ...

        @overload
        async def verify_certificate(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                request: VerificationCodeRequest, 
                *, 
                certificate_created: Optional[datetime] = ..., 
                certificate_has_private_key: Optional[bool] = ..., 
                certificate_is_verified: Optional[bool] = ..., 
                certificate_last_updated: Optional[datetime] = ..., 
                certificate_name1: Optional[str] = ..., 
                certificate_nonce: Optional[str] = ..., 
                certificate_purpose: Optional[Union[str, CertificatePurpose]] = ..., 
                certificate_raw_bytes: Optional[bytes] = ..., 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateResponse: ...

        @overload
        async def verify_certificate(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                request: JSON, 
                *, 
                certificate_created: Optional[datetime] = ..., 
                certificate_has_private_key: Optional[bool] = ..., 
                certificate_is_verified: Optional[bool] = ..., 
                certificate_last_updated: Optional[datetime] = ..., 
                certificate_name1: Optional[str] = ..., 
                certificate_nonce: Optional[str] = ..., 
                certificate_purpose: Optional[Union[str, CertificatePurpose]] = ..., 
                certificate_raw_bytes: Optional[bytes] = ..., 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateResponse: ...

        @overload
        async def verify_certificate(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                request: IO[bytes], 
                *, 
                certificate_created: Optional[datetime] = ..., 
                certificate_has_private_key: Optional[bool] = ..., 
                certificate_is_verified: Optional[bool] = ..., 
                certificate_last_updated: Optional[datetime] = ..., 
                certificate_name1: Optional[str] = ..., 
                certificate_nonce: Optional[str] = ..., 
                certificate_purpose: Optional[Union[str, CertificatePurpose]] = ..., 
                certificate_raw_bytes: Optional[bytes] = ..., 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateResponse: ...


    class azure.mgmt.iothubprovisioningservices.aio.operations.IotDpsResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                iot_dps_description: ProvisioningServiceDescription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProvisioningServiceDescription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                iot_dps_description: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProvisioningServiceDescription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                iot_dps_description: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProvisioningServiceDescription]: ...

        @overload
        async def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                provisioning_service_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                provisioning_service_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProvisioningServiceDescription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                provisioning_service_tags: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProvisioningServiceDescription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                provisioning_service_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProvisioningServiceDescription]: ...

        @overload
        async def check_provisioning_service_name_availability(
                self, 
                arguments: OperationInputs, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityInfo: ...

        @overload
        async def check_provisioning_service_name_availability(
                self, 
                arguments: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityInfo: ...

        @overload
        async def check_provisioning_service_name_availability(
                self, 
                arguments: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityInfo: ...

        @distributed_trace_async
        async def get(
                self, 
                provisioning_service_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ProvisioningServiceDescription: ...

        @distributed_trace_async
        async def get_operation_result(
                self, 
                operation_id: str, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                *, 
                asyncinfo: str, 
                **kwargs: Any
            ) -> AsyncOperationResult: ...

        @distributed_trace_async
        async def get_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def get_private_link_resources(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                group_id: str, 
                **kwargs: Any
            ) -> GroupIdInformation: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProvisioningServiceDescription]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ProvisioningServiceDescription]: ...

        @distributed_trace
        def list_keys(
                self, 
                provisioning_service_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SharedAccessSignatureAuthorizationRuleAccessRightsDescription]: ...

        @distributed_trace_async
        async def list_keys_for_key_name(
                self, 
                provisioning_service_name: str, 
                key_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> SharedAccessSignatureAuthorizationRuleAccessRightsDescription: ...

        @distributed_trace_async
        async def list_private_endpoint_connections(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> List[PrivateEndpointConnection]: ...

        @distributed_trace
        def list_private_link_resources(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GroupIdInformation]: ...

        @distributed_trace
        def list_valid_skus(
                self, 
                provisioning_service_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IotDpsSkuDefinition]: ...


    class azure.mgmt.iothubprovisioningservices.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.iothubprovisioningservices.models

    class azure.mgmt.iothubprovisioningservices.models.AccessRightsDescription(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEVICE_CONNECT = "DeviceConnect"
        ENROLLMENT_READ = "EnrollmentRead"
        ENROLLMENT_WRITE = "EnrollmentWrite"
        REGISTRATION_STATUS_READ = "RegistrationStatusRead"
        REGISTRATION_STATUS_WRITE = "RegistrationStatusWrite"
        SERVICE_CONFIG = "ServiceConfig"


    class azure.mgmt.iothubprovisioningservices.models.AllocationPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEO_LATENCY = "GeoLatency"
        HASHED = "Hashed"
        STATIC = "Static"


    class azure.mgmt.iothubprovisioningservices.models.AsyncOperationResult(_Model):
        error: Optional[ErrorMessage]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorMessage] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.CertificateProperties(_Model):
        certificate: Optional[bytes]
        created: Optional[datetime]
        expiry: Optional[datetime]
        is_verified: Optional[bool]
        subject: Optional[str]
        thumbprint: Optional[str]
        updated: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                certificate: Optional[bytes] = ..., 
                is_verified: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.CertificatePurpose(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT_AUTHENTICATION = "clientAuthentication"
        SERVER_AUTHENTICATION = "serverAuthentication"


    class azure.mgmt.iothubprovisioningservices.models.CertificateResponse(ProxyResource):
        etag: Optional[str]
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


    class azure.mgmt.iothubprovisioningservices.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.iothubprovisioningservices.models.DeviceRegistryNamespaceAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.iothubprovisioningservices.models.DeviceRegistryNamespaceDescription(_Model):
        authentication_type: Union[str, DeviceRegistryNamespaceAuthenticationType]
        resource_id: str
        selected_user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Union[str, DeviceRegistryNamespaceAuthenticationType], 
                resource_id: str, 
                selected_user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.iothubprovisioningservices.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.iothubprovisioningservices.models.ErrorDetails(_Model):
        code: Optional[int]
        details: Optional[str]
        http_status_code: Optional[str]
        message: Optional[str]


    class azure.mgmt.iothubprovisioningservices.models.ErrorMessage(_Model):
        code: Optional[str]
        details: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.GroupIdInformation(ProxyResource):
        id: str
        name: str
        properties: GroupIdInformationProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: GroupIdInformationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.GroupIdInformationProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                required_members: Optional[list[str]] = ..., 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.IotDpsPropertiesDescription(_Model):
        allocation_policy: Optional[Union[str, AllocationPolicy]]
        authorization_policies: Optional[list[SharedAccessSignatureAuthorizationRuleAccessRightsDescription]]
        device_provisioning_host_name: Optional[str]
        device_registry_namespace: Optional[DeviceRegistryNamespaceDescription]
        enable_data_residency: Optional[bool]
        id_scope: Optional[str]
        iot_hubs: Optional[list[IotHubDefinitionDescription]]
        ip_filter_rules: Optional[list[IpFilterRule]]
        portal_operations_host_name: Optional[str]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        service_operations_host_name: Optional[str]
        state: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                allocation_policy: Optional[Union[str, AllocationPolicy]] = ..., 
                authorization_policies: Optional[list[SharedAccessSignatureAuthorizationRuleAccessRightsDescription]] = ..., 
                device_registry_namespace: Optional[DeviceRegistryNamespaceDescription] = ..., 
                enable_data_residency: Optional[bool] = ..., 
                iot_hubs: Optional[list[IotHubDefinitionDescription]] = ..., 
                ip_filter_rules: Optional[list[IpFilterRule]] = ..., 
                portal_operations_host_name: Optional[str] = ..., 
                private_endpoint_connections: Optional[list[PrivateEndpointConnection]] = ..., 
                provisioning_state: Optional[str] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.IotDpsSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        S1 = "S1"


    class azure.mgmt.iothubprovisioningservices.models.IotDpsSkuDefinition(_Model):
        name: Optional[Union[str, IotDpsSku]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, IotDpsSku]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.IotDpsSkuInfo(_Model):
        capacity: Optional[int]
        name: Optional[Union[str, IotDpsSku]]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Optional[Union[str, IotDpsSku]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.IotHubDefinitionDescription(_Model):
        allocation_weight: Optional[int]
        apply_allocation_policy: Optional[bool]
        connection_string: str
        location: str
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allocation_weight: Optional[int] = ..., 
                apply_allocation_policy: Optional[bool] = ..., 
                connection_string: str, 
                location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.IpFilterActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPT = "Accept"
        REJECT = "Reject"


    class azure.mgmt.iothubprovisioningservices.models.IpFilterRule(_Model):
        action: Union[str, IpFilterActionType]
        filter_name: str
        ip_mask: str
        target: Optional[Union[str, IpFilterTargetType]]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, IpFilterActionType], 
                filter_name: str, 
                ip_mask: str, 
                target: Optional[Union[str, IpFilterTargetType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.IpFilterTargetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "all"
        DEVICE_API = "deviceApi"
        SERVICE_API = "serviceApi"


    class azure.mgmt.iothubprovisioningservices.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.iothubprovisioningservices.models.NameAvailabilityInfo(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, NameUnavailabilityReason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, NameUnavailabilityReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.NameUnavailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.iothubprovisioningservices.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.OperationDisplay(_Model):
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.iothubprovisioningservices.models.OperationInputs(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.iothubprovisioningservices.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: PrivateEndpointConnectionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.PrivateEndpointConnectionProperties(_Model):
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: str
        status: Union[str, PrivateLinkServiceConnectionStatus]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: str, 
                status: Union[str, PrivateLinkServiceConnectionStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.PrivateLinkServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.iothubprovisioningservices.models.ProvisioningServiceDescription(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: IotDpsPropertiesDescription
        resourcegroup: Optional[str]
        sku: IotDpsSkuInfo
        subscriptionid: Optional[str]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: IotDpsPropertiesDescription, 
                resourcegroup: Optional[str] = ..., 
                sku: IotDpsSkuInfo, 
                subscriptionid: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.iothubprovisioningservices.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.iothubprovisioningservices.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.iothubprovisioningservices.models.SharedAccessSignatureAuthorizationRuleAccessRightsDescription(_Model):
        key_name: str
        primary_key: Optional[str]
        rights: Union[str, AccessRightsDescription]
        secondary_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_name: str, 
                primary_key: Optional[str] = ..., 
                rights: Union[str, AccessRightsDescription], 
                secondary_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATING = "Activating"
        ACTIVATION_FAILED = "ActivationFailed"
        ACTIVE = "Active"
        DELETED = "Deleted"
        DELETING = "Deleting"
        DELETION_FAILED = "DeletionFailed"
        FAILING_OVER = "FailingOver"
        FAILOVER_FAILED = "FailoverFailed"
        RESUMING = "Resuming"
        SUSPENDED = "Suspended"
        SUSPENDING = "Suspending"
        TRANSITIONING = "Transitioning"


    class azure.mgmt.iothubprovisioningservices.models.SystemData(_Model):
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


    class azure.mgmt.iothubprovisioningservices.models.TagsResource(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.TrackedResource(Resource):
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


    class azure.mgmt.iothubprovisioningservices.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.iothubprovisioningservices.models.VerificationCodeRequest(_Model):
        certificate: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.VerificationCodeResponse(_Model):
        etag: Optional[str]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[VerificationCodeResponseProperties]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VerificationCodeResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothubprovisioningservices.models.VerificationCodeResponseProperties(_Model):
        certificate: Optional[bytes]
        created: Optional[str]
        expiry: Optional[str]
        is_verified: Optional[bool]
        subject: Optional[str]
        thumbprint: Optional[str]
        updated: Optional[str]
        verification_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate: Optional[bytes] = ..., 
                created: Optional[str] = ..., 
                expiry: Optional[str] = ..., 
                is_verified: Optional[bool] = ..., 
                subject: Optional[str] = ..., 
                thumbprint: Optional[str] = ..., 
                updated: Optional[str] = ..., 
                verification_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.iothubprovisioningservices.operations

    class azure.mgmt.iothubprovisioningservices.operations.DpsCertificateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                certificate_description: CertificateResponse, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateResponse: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                certificate_description: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateResponse: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                certificate_description: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateResponse: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                *, 
                certificate_created: Optional[datetime] = ..., 
                certificate_has_private_key: Optional[bool] = ..., 
                certificate_is_verified: Optional[bool] = ..., 
                certificate_last_updated: Optional[datetime] = ..., 
                certificate_name1: Optional[str] = ..., 
                certificate_nonce: Optional[str] = ..., 
                certificate_purpose: Optional[Union[str, CertificatePurpose]] = ..., 
                certificate_raw_bytes: Optional[bytes] = ..., 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def generate_verification_code(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                *, 
                certificate_created: Optional[datetime] = ..., 
                certificate_has_private_key: Optional[bool] = ..., 
                certificate_is_verified: Optional[bool] = ..., 
                certificate_last_updated: Optional[datetime] = ..., 
                certificate_name1: Optional[str] = ..., 
                certificate_nonce: Optional[str] = ..., 
                certificate_purpose: Optional[Union[str, CertificatePurpose]] = ..., 
                certificate_raw_bytes: Optional[bytes] = ..., 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> VerificationCodeResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CertificateResponse]: ...

        @overload
        def verify_certificate(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                request: VerificationCodeRequest, 
                *, 
                certificate_created: Optional[datetime] = ..., 
                certificate_has_private_key: Optional[bool] = ..., 
                certificate_is_verified: Optional[bool] = ..., 
                certificate_last_updated: Optional[datetime] = ..., 
                certificate_name1: Optional[str] = ..., 
                certificate_nonce: Optional[str] = ..., 
                certificate_purpose: Optional[Union[str, CertificatePurpose]] = ..., 
                certificate_raw_bytes: Optional[bytes] = ..., 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateResponse: ...

        @overload
        def verify_certificate(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                request: JSON, 
                *, 
                certificate_created: Optional[datetime] = ..., 
                certificate_has_private_key: Optional[bool] = ..., 
                certificate_is_verified: Optional[bool] = ..., 
                certificate_last_updated: Optional[datetime] = ..., 
                certificate_name1: Optional[str] = ..., 
                certificate_nonce: Optional[str] = ..., 
                certificate_purpose: Optional[Union[str, CertificatePurpose]] = ..., 
                certificate_raw_bytes: Optional[bytes] = ..., 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateResponse: ...

        @overload
        def verify_certificate(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                certificate_name: str, 
                request: IO[bytes], 
                *, 
                certificate_created: Optional[datetime] = ..., 
                certificate_has_private_key: Optional[bool] = ..., 
                certificate_is_verified: Optional[bool] = ..., 
                certificate_last_updated: Optional[datetime] = ..., 
                certificate_name1: Optional[str] = ..., 
                certificate_nonce: Optional[str] = ..., 
                certificate_purpose: Optional[Union[str, CertificatePurpose]] = ..., 
                certificate_raw_bytes: Optional[bytes] = ..., 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateResponse: ...


    class azure.mgmt.iothubprovisioningservices.operations.IotDpsResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                iot_dps_description: ProvisioningServiceDescription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProvisioningServiceDescription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                iot_dps_description: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProvisioningServiceDescription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                iot_dps_description: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProvisioningServiceDescription]: ...

        @overload
        def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                provisioning_service_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                provisioning_service_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProvisioningServiceDescription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                provisioning_service_tags: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProvisioningServiceDescription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                provisioning_service_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProvisioningServiceDescription]: ...

        @overload
        def check_provisioning_service_name_availability(
                self, 
                arguments: OperationInputs, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityInfo: ...

        @overload
        def check_provisioning_service_name_availability(
                self, 
                arguments: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityInfo: ...

        @overload
        def check_provisioning_service_name_availability(
                self, 
                arguments: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityInfo: ...

        @distributed_trace
        def get(
                self, 
                provisioning_service_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ProvisioningServiceDescription: ...

        @distributed_trace
        def get_operation_result(
                self, 
                operation_id: str, 
                resource_group_name: str, 
                provisioning_service_name: str, 
                *, 
                asyncinfo: str, 
                **kwargs: Any
            ) -> AsyncOperationResult: ...

        @distributed_trace
        def get_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def get_private_link_resources(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                group_id: str, 
                **kwargs: Any
            ) -> GroupIdInformation: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProvisioningServiceDescription]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ProvisioningServiceDescription]: ...

        @distributed_trace
        def list_keys(
                self, 
                provisioning_service_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SharedAccessSignatureAuthorizationRuleAccessRightsDescription]: ...

        @distributed_trace
        def list_keys_for_key_name(
                self, 
                provisioning_service_name: str, 
                key_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> SharedAccessSignatureAuthorizationRuleAccessRightsDescription: ...

        @distributed_trace
        def list_private_endpoint_connections(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> List[PrivateEndpointConnection]: ...

        @distributed_trace
        def list_private_link_resources(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GroupIdInformation]: ...

        @distributed_trace
        def list_valid_skus(
                self, 
                provisioning_service_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IotDpsSkuDefinition]: ...


    class azure.mgmt.iothubprovisioningservices.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


```