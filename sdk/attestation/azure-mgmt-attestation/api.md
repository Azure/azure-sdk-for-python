```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.attestation

    class azure.mgmt.attestation.AttestationManagementClient: implements ContextManager 
        attestation_providers: AttestationProvidersOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.attestation.aio

    class azure.mgmt.attestation.aio.AttestationManagementClient: implements AsyncContextManager 
        attestation_providers: AttestationProvidersOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.attestation.aio.operations

    class azure.mgmt.attestation.aio.operations.AttestationProvidersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                creation_params: AttestationServiceCreationParams, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                creation_params: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                creation_params: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @distributed_trace_async
        async def get_default_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @distributed_trace_async
        async def list(self, **kwargs: Any) -> AttestationProviderListResult: ...

        @distributed_trace_async
        async def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AttestationProviderListResult: ...

        @distributed_trace_async
        async def list_default(self, **kwargs: Any) -> AttestationProviderListResult: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                update_params: AttestationServicePatchParams, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                update_params: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                update_params: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttestationProvider: ...


    class azure.mgmt.attestation.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationsDefinition]: ...


    class azure.mgmt.attestation.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                private_endpoint_connection_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.attestation.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_by_provider(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


namespace azure.mgmt.attestation.models

    class azure.mgmt.attestation.models.AttestationProvider(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[StatusResult]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[StatusResult] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.attestation.models.AttestationProviderListResult(_Model):
        system_data: Optional[SystemData]
        value: Optional[list[AttestationProvider]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[AttestationProvider]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.AttestationServiceCreationParams(_Model):
        location: str
        properties: AttestationServiceCreationSpecificParams
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: AttestationServiceCreationSpecificParams, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.AttestationServiceCreationSpecificParams(_Model):
        policy_signing_certificates: Optional[JSONWebKeySet]
        public_network_access: Optional[Union[str, PublicNetworkAccessType]]
        tpm_attestation_authentication: Optional[Union[str, TpmAttestationAuthenticationType]]

        @overload
        def __init__(
                self, 
                *, 
                policy_signing_certificates: Optional[JSONWebKeySet] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccessType]] = ..., 
                tpm_attestation_authentication: Optional[Union[str, TpmAttestationAuthenticationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.AttestationServicePatchParams(_Model):
        properties: Optional[AttestationServicePatchSpecificParams]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AttestationServicePatchSpecificParams] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.AttestationServicePatchSpecificParams(_Model):
        public_network_access: Optional[Union[str, PublicNetworkAccessType]]
        tpm_attestation_authentication: Optional[Union[str, TpmAttestationAuthenticationType]]

        @overload
        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, PublicNetworkAccessType]] = ..., 
                tpm_attestation_authentication: Optional[Union[str, TpmAttestationAuthenticationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.AttestationServiceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        NOT_READY = "NotReady"
        READY = "Ready"


    class azure.mgmt.attestation.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.CloudErrorBody(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.attestation.models.JSONWebKey(_Model):
        alg: Optional[str]
        crv: Optional[str]
        d: Optional[str]
        dp: Optional[str]
        dq: Optional[str]
        e: Optional[str]
        k: Optional[str]
        kid: Optional[str]
        kty: str
        n: Optional[str]
        p: Optional[str]
        q: Optional[str]
        qi: Optional[str]
        use: Optional[str]
        x: Optional[str]
        x5_c: Optional[list[str]]
        y: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                alg: Optional[str] = ..., 
                crv: Optional[str] = ..., 
                d: Optional[str] = ..., 
                dp: Optional[str] = ..., 
                dq: Optional[str] = ..., 
                e: Optional[str] = ..., 
                k: Optional[str] = ..., 
                kid: Optional[str] = ..., 
                kty: str, 
                n: Optional[str] = ..., 
                p: Optional[str] = ..., 
                q: Optional[str] = ..., 
                qi: Optional[str] = ..., 
                use: Optional[str] = ..., 
                x: Optional[str] = ..., 
                x5_c: Optional[list[str]] = ..., 
                y: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.JSONWebKeySet(_Model):
        keys_property: Optional[list[JSONWebKey]]

        @overload
        def __init__(
                self, 
                *, 
                keys_property: Optional[list[JSONWebKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.LogSpecification(_Model):
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.OperationProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.OperationsDefinition(_Model):
        display: Optional[OperationsDisplayDefinition]
        name: Optional[str]
        properties: Optional[OperationProperties]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationsDisplayDefinition] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[OperationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.OperationsDisplayDefinition(_Model):
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


    class azure.mgmt.attestation.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.attestation.models.PrivateEndpointConnection(Resource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.attestation.models.PrivateEndpointConnectionProperties(_Model):
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.attestation.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.attestation.models.PrivateLinkResource(Resource):
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


    class azure.mgmt.attestation.models.PrivateLinkResourceListResult(_Model):
        next_link: Optional[str]
        value: list[PrivateLinkResource]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PrivateLinkResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.PublicNetworkAccessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.attestation.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.attestation.models.ServiceSpecification(_Model):
        log_specifications: Optional[list[LogSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[LogSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.StatusResult(_Model):
        attest_uri: Optional[str]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        public_network_access: Optional[Union[str, PublicNetworkAccessType]]
        status: Optional[Union[str, AttestationServiceStatus]]
        tpm_attestation_authentication: Optional[Union[str, TpmAttestationAuthenticationType]]
        trust_model: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                attest_uri: Optional[str] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccessType]] = ..., 
                status: Optional[Union[str, AttestationServiceStatus]] = ..., 
                tpm_attestation_authentication: Optional[Union[str, TpmAttestationAuthenticationType]] = ..., 
                trust_model: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.attestation.models.SystemData(_Model):
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


    class azure.mgmt.attestation.models.TpmAttestationAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.attestation.models.TrackedResource(Resource):
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


namespace azure.mgmt.attestation.operations

    class azure.mgmt.attestation.operations.AttestationProvidersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                creation_params: AttestationServiceCreationParams, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                creation_params: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                creation_params: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @distributed_trace
        def get_default_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AttestationProviderListResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AttestationProviderListResult: ...

        @distributed_trace
        def list_default(self, **kwargs: Any) -> AttestationProviderListResult: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                update_params: AttestationServicePatchParams, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                update_params: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttestationProvider: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                update_params: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttestationProvider: ...


    class azure.mgmt.attestation.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationsDefinition]: ...


    class azure.mgmt.attestation.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                private_endpoint_connection_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.attestation.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_provider(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


```