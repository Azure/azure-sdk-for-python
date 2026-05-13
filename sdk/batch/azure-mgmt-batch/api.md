```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.batch

    class azure.mgmt.batch.BatchManagementClient: implements ContextManager 
        application: ApplicationOperations
        application_package: ApplicationPackageOperations
        batch_account: BatchAccountOperations
        location: LocationOperations
        network_security_perimeter: NetworkSecurityPerimeterOperations
        operations: Operations
        pool: PoolOperations
        private_endpoint_connection: PrivateEndpointConnectionOperations
        private_link_resource: PrivateLinkResourceOperations

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


namespace azure.mgmt.batch.aio

    class azure.mgmt.batch.aio.BatchManagementClient: implements AsyncContextManager 
        application: ApplicationOperations
        application_package: ApplicationPackageOperations
        batch_account: BatchAccountOperations
        location: LocationOperations
        network_security_perimeter: NetworkSecurityPerimeterOperations
        operations: Operations
        pool: PoolOperations
        private_endpoint_connection: PrivateEndpointConnectionOperations
        private_link_resource: PrivateLinkResourceOperations

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


namespace azure.mgmt.batch.aio.operations

    class azure.mgmt.batch.aio.operations.ApplicationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                parameters: Optional[Application] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> Application: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                maxresults: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Application]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                parameters: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...


    class azure.mgmt.batch.aio.operations.ApplicationPackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def activate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                parameters: ActivateApplicationPackageParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @overload
        async def activate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @overload
        async def activate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                parameters: Optional[ApplicationPackage] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                *, 
                maxresults: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ApplicationPackage]: ...


    class azure.mgmt.batch.aio.operations.BatchAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BatchAccountCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BatchAccount]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BatchAccount]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BatchAccount]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> BatchAccount: ...

        @distributed_trace_async
        async def get_detector(
                self, 
                resource_group_name: str, 
                account_name: str, 
                detector_id: str, 
                **kwargs: Any
            ) -> DetectorResponse: ...

        @distributed_trace_async
        async def get_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> BatchAccountKeys: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[BatchAccount]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchAccount]: ...

        @distributed_trace
        def list_detectors(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DetectorResponse]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OutboundEnvironmentEndpoint]: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BatchAccountRegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchAccountKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchAccountKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchAccountKeys: ...

        @distributed_trace_async
        async def synchronize_auto_storage_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BatchAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchAccount: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchAccount: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchAccount: ...


    class azure.mgmt.batch.aio.operations.LocationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_name_availability(
                self, 
                location_name: str, 
                parameters: CheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                location_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                location_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace_async
        async def get_quotas(
                self, 
                location_name: str, 
                **kwargs: Any
            ) -> BatchLocationQuota: ...

        @distributed_trace
        def list_supported_virtual_machine_skus(
                self, 
                location_name: str, 
                *, 
                filter: Optional[str] = ..., 
                maxresults: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SupportedSku]: ...


    class azure.mgmt.batch.aio.operations.NetworkSecurityPerimeterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_reconcile_configuration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_configuration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list_configurations(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.batch.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.batch.aio.operations.PoolOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                parameters: Pool, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Pool: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Pool: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace_async
        async def disable_auto_scale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace
        def list_by_batch_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                maxresults: Optional[int] = ..., 
                select: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Pool]: ...

        @distributed_trace_async
        async def stop_resize(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                parameters: Pool, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Pool: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Pool: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Pool: ...


    class azure.mgmt.batch.aio.operations.PrivateEndpointConnectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_batch_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                maxresults: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.batch.aio.operations.PrivateLinkResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_batch_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                maxresults: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


namespace azure.mgmt.batch.models

    class azure.mgmt.batch.models.AccessRule(_Model):
        name: Optional[str]
        properties: Optional[AccessRuleProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[AccessRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.batch.models.AccessRuleProperties(_Model):
        address_prefixes: Optional[list[str]]
        direction: Optional[Union[str, AccessRuleDirection]]
        email_addresses: Optional[list[str]]
        fully_qualified_domain_names: Optional[list[str]]
        network_security_perimeters: Optional[list[NetworkSecurityPerimeter]]
        phone_numbers: Optional[list[str]]
        subscriptions: Optional[list[AccessRulePropertiesSubscription]]

        @overload
        def __init__(
                self, 
                *, 
                address_prefixes: Optional[list[str]] = ..., 
                direction: Optional[Union[str, AccessRuleDirection]] = ..., 
                email_addresses: Optional[list[str]] = ..., 
                fully_qualified_domain_names: Optional[list[str]] = ..., 
                network_security_perimeters: Optional[list[NetworkSecurityPerimeter]] = ..., 
                phone_numbers: Optional[list[str]] = ..., 
                subscriptions: Optional[list[AccessRulePropertiesSubscription]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AccessRulePropertiesSubscription(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AccountKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.batch.models.ActivateApplicationPackageParameters(_Model):
        format: str

        @overload
        def __init__(
                self, 
                *, 
                format: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AllocationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESIZING = "Resizing"
        STEADY = "Steady"
        STOPPING = "Stopping"


    class azure.mgmt.batch.models.Application(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[ApplicationProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ApplicationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.batch.models.ApplicationPackage(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[ApplicationPackageProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ApplicationPackageProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.batch.models.ApplicationPackageProperties(_Model):
        format: Optional[str]
        last_activation_time: Optional[datetime]
        state: Optional[Union[str, PackageState]]
        storage_url: Optional[str]
        storage_url_expiry: Optional[datetime]


    class azure.mgmt.batch.models.ApplicationPackageReference(_Model):
        id: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ApplicationProperties(_Model):
        allow_updates: Optional[bool]
        default_version: Optional[str]
        display_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allow_updates: Optional[bool] = ..., 
                default_version: Optional[str] = ..., 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AuthenticationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD = "AAD"
        SHARED_KEY = "SharedKey"
        TASK_AUTHENTICATION_TOKEN = "TaskAuthenticationToken"


    class azure.mgmt.batch.models.AutoScaleRun(_Model):
        error: Optional[AutoScaleRunError]
        evaluation_time: datetime
        results: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[AutoScaleRunError] = ..., 
                evaluation_time: datetime, 
                results: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AutoScaleRunError(_Model):
        code: str
        details: Optional[list[AutoScaleRunError]]
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[list[AutoScaleRunError]] = ..., 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AutoScaleSettings(_Model):
        evaluation_interval: Optional[timedelta]
        formula: str

        @overload
        def __init__(
                self, 
                *, 
                evaluation_interval: Optional[timedelta] = ..., 
                formula: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AutoStorageAuthenticationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BATCH_ACCOUNT_MANAGED_IDENTITY = "BatchAccountManagedIdentity"
        STORAGE_KEYS = "StorageKeys"


    class azure.mgmt.batch.models.AutoStorageBaseProperties(_Model):
        authentication_mode: Optional[Union[str, AutoStorageAuthenticationMode]]
        node_identity_reference: Optional[ComputeNodeIdentityReference]
        storage_account_id: str

        @overload
        def __init__(
                self, 
                *, 
                authentication_mode: Optional[Union[str, AutoStorageAuthenticationMode]] = ..., 
                node_identity_reference: Optional[ComputeNodeIdentityReference] = ..., 
                storage_account_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AutoStorageProperties(AutoStorageBaseProperties):
        authentication_mode: Union[str, AutoStorageAuthenticationMode]
        last_key_sync: datetime
        node_identity_reference: ComputeNodeIdentityReference
        storage_account_id: str

        @overload
        def __init__(
                self, 
                *, 
                authentication_mode: Optional[Union[str, AutoStorageAuthenticationMode]] = ..., 
                last_key_sync: datetime, 
                node_identity_reference: Optional[ComputeNodeIdentityReference] = ..., 
                storage_account_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AutoUserScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POOL = "Pool"
        TASK = "Task"


    class azure.mgmt.batch.models.AutoUserSpecification(_Model):
        elevation_level: Optional[Union[str, ElevationLevel]]
        scope: Optional[Union[str, AutoUserScope]]

        @overload
        def __init__(
                self, 
                *, 
                elevation_level: Optional[Union[str, ElevationLevel]] = ..., 
                scope: Optional[Union[str, AutoUserScope]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AutomaticOSUpgradePolicy(_Model):
        disable_automatic_rollback: Optional[bool]
        enable_automatic_os_upgrade: Optional[bool]
        os_rolling_upgrade_deferral: Optional[bool]
        use_rolling_upgrade_policy: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disable_automatic_rollback: Optional[bool] = ..., 
                enable_automatic_os_upgrade: Optional[bool] = ..., 
                os_rolling_upgrade_deferral: Optional[bool] = ..., 
                use_rolling_upgrade_policy: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AzureBlobFileSystemConfiguration(_Model):
        account_key: Optional[str]
        account_name: str
        blobfuse_options: Optional[str]
        container_name: str
        identity_reference: Optional[ComputeNodeIdentityReference]
        relative_mount_path: str
        sas_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_key: Optional[str] = ..., 
                account_name: str, 
                blobfuse_options: Optional[str] = ..., 
                container_name: str, 
                identity_reference: Optional[ComputeNodeIdentityReference] = ..., 
                relative_mount_path: str, 
                sas_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AzureFileShareConfiguration(_Model):
        account_key: str
        account_name: str
        azure_file_url: str
        mount_options: Optional[str]
        relative_mount_path: str

        @overload
        def __init__(
                self, 
                *, 
                account_key: str, 
                account_name: str, 
                azure_file_url: str, 
                mount_options: Optional[str] = ..., 
                relative_mount_path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.AzureResource(Resource):
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


    class azure.mgmt.batch.models.BatchAccount(AzureResource):
        id: str
        identity: Optional[BatchAccountIdentity]
        location: str
        name: str
        properties: Optional[BatchAccountProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[BatchAccountIdentity] = ..., 
                location: str, 
                properties: Optional[BatchAccountProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.batch.models.BatchAccountCreateParameters(_Model):
        identity: Optional[BatchAccountIdentity]
        location: str
        properties: Optional[BatchAccountCreateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[BatchAccountIdentity] = ..., 
                location: str, 
                properties: Optional[BatchAccountCreateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.batch.models.BatchAccountCreateProperties(_Model):
        allowed_authentication_modes: Optional[list[Union[str, AuthenticationMode]]]
        auto_storage: Optional[AutoStorageBaseProperties]
        encryption: Optional[EncryptionProperties]
        key_vault_reference: Optional[KeyVaultReference]
        network_profile: Optional[NetworkProfile]
        pool_allocation_mode: Optional[Union[str, PoolAllocationMode]]
        public_network_access: Optional[Union[str, PublicNetworkAccessType]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_authentication_modes: Optional[list[Union[str, AuthenticationMode]]] = ..., 
                auto_storage: Optional[AutoStorageBaseProperties] = ..., 
                encryption: Optional[EncryptionProperties] = ..., 
                key_vault_reference: Optional[KeyVaultReference] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                pool_allocation_mode: Optional[Union[str, PoolAllocationMode]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccessType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.BatchAccountIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ResourceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentities]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ResourceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentities]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.BatchAccountKeys(_Model):
        account_name: Optional[str]
        primary: Optional[str]
        secondary: Optional[str]


    class azure.mgmt.batch.models.BatchAccountProperties(_Model):
        account_endpoint: Optional[str]
        active_job_and_job_schedule_quota: Optional[int]
        allowed_authentication_modes: Optional[list[Union[str, AuthenticationMode]]]
        auto_storage: Optional[AutoStorageProperties]
        dedicated_core_quota: Optional[int]
        dedicated_core_quota_per_vm_family: Optional[list[VirtualMachineFamilyCoreQuota]]
        dedicated_core_quota_per_vm_family_enforced: Optional[bool]
        encryption: Optional[EncryptionProperties]
        key_vault_reference: Optional[KeyVaultReference]
        low_priority_core_quota: Optional[int]
        network_profile: Optional[NetworkProfile]
        node_management_endpoint: Optional[str]
        pool_allocation_mode: Optional[Union[str, PoolAllocationMode]]
        pool_quota: Optional[int]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccessType]]

        @overload
        def __init__(
                self, 
                *, 
                network_profile: Optional[NetworkProfile] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccessType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.BatchAccountRegenerateKeyParameters(_Model):
        key_name: Union[str, AccountKeyType]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Union[str, AccountKeyType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.BatchAccountUpdateParameters(_Model):
        identity: Optional[BatchAccountIdentity]
        properties: Optional[BatchAccountUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[BatchAccountIdentity] = ..., 
                properties: Optional[BatchAccountUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.batch.models.BatchAccountUpdateProperties(_Model):
        allowed_authentication_modes: Optional[list[Union[str, AuthenticationMode]]]
        auto_storage: Optional[AutoStorageBaseProperties]
        encryption: Optional[EncryptionProperties]
        network_profile: Optional[NetworkProfile]
        public_network_access: Optional[Union[str, PublicNetworkAccessType]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_authentication_modes: Optional[list[Union[str, AuthenticationMode]]] = ..., 
                auto_storage: Optional[AutoStorageBaseProperties] = ..., 
                encryption: Optional[EncryptionProperties] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccessType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.BatchLocationQuota(_Model):
        account_quota: Optional[int]


    class azure.mgmt.batch.models.BatchPoolIdentity(_Model):
        type: Union[str, PoolIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentities]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, PoolIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentities]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.CIFSMountConfiguration(_Model):
        mount_options: Optional[str]
        password: str
        relative_mount_path: str
        source: str
        user_name: str

        @overload
        def __init__(
                self, 
                *, 
                mount_options: Optional[str] = ..., 
                password: str, 
                relative_mount_path: str, 
                source: str, 
                user_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.CachingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.batch.models.CheckNameAvailabilityParameters(_Model):
        name: str
        type: Union[str, ResourceType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, ResourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.CheckNameAvailabilityResult(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, NameAvailabilityReason]]


    class azure.mgmt.batch.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.CloudErrorBody(_Model):
        code: Optional[str]
        details: Optional[list[CloudErrorBody]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ComputeNodeDeallocationOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REQUEUE = "Requeue"
        RETAINED_DATA = "RetainedData"
        TASK_COMPLETION = "TaskCompletion"
        TERMINATE = "Terminate"


    class azure.mgmt.batch.models.ComputeNodeFillType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PACK = "Pack"
        SPREAD = "Spread"


    class azure.mgmt.batch.models.ComputeNodeIdentityReference(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ContainerConfiguration(_Model):
        container_image_names: Optional[list[str]]
        container_registries: Optional[list[ContainerRegistry]]
        type: Union[str, ContainerType]

        @overload
        def __init__(
                self, 
                *, 
                container_image_names: Optional[list[str]] = ..., 
                container_registries: Optional[list[ContainerRegistry]] = ..., 
                type: Union[str, ContainerType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ContainerHostBatchBindMountEntry(_Model):
        is_read_only: Optional[bool]
        source: Optional[Union[str, ContainerHostDataPath]]

        @overload
        def __init__(
                self, 
                *, 
                is_read_only: Optional[bool] = ..., 
                source: Optional[Union[str, ContainerHostDataPath]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ContainerHostDataPath(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATIONS = "Applications"
        JOB_PREP = "JobPrep"
        SHARED = "Shared"
        STARTUP = "Startup"
        TASK = "Task"
        VFS_MOUNTS = "VfsMounts"


    class azure.mgmt.batch.models.ContainerRegistry(_Model):
        identity_reference: Optional[ComputeNodeIdentityReference]
        password: Optional[str]
        registry_server: Optional[str]
        user_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_reference: Optional[ComputeNodeIdentityReference] = ..., 
                password: Optional[str] = ..., 
                registry_server: Optional[str] = ..., 
                user_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ContainerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRI_COMPATIBLE = "CriCompatible"
        DOCKER_COMPATIBLE = "DockerCompatible"


    class azure.mgmt.batch.models.ContainerWorkingDirectory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_IMAGE_DEFAULT = "ContainerImageDefault"
        TASK_WORKING_DIRECTORY = "TaskWorkingDirectory"


    class azure.mgmt.batch.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.batch.models.DataDisk(_Model):
        caching: Optional[Union[str, CachingType]]
        disk_size_gb: int
        lun: int
        managed_disk: Optional[ManagedDisk]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, CachingType]] = ..., 
                disk_size_gb: int, 
                lun: int, 
                managed_disk: Optional[ManagedDisk] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.DeploymentConfiguration(_Model):
        virtual_machine_configuration: Optional[VirtualMachineConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                virtual_machine_configuration: Optional[VirtualMachineConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.DetectorResponse(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[DetectorResponseProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DetectorResponseProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.batch.models.DetectorResponseProperties(_Model):
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.DiffDiskPlacement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CACHE_DISK = "CacheDisk"


    class azure.mgmt.batch.models.DiffDiskSettings(_Model):
        placement: Optional[Union[str, DiffDiskPlacement]]

        @overload
        def __init__(
                self, 
                *, 
                placement: Optional[Union[str, DiffDiskPlacement]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.DiskCustomerManagedKey(_Model):
        identity_reference: Optional[ComputeNodeIdentityReference]
        key_url: Optional[str]
        rotation_to_latest_key_version_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                identity_reference: Optional[ComputeNodeIdentityReference] = ..., 
                key_url: Optional[str] = ..., 
                rotation_to_latest_key_version_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.DiskEncryptionConfiguration(_Model):
        customer_managed_key: Optional[DiskCustomerManagedKey]
        targets: Optional[list[Union[str, DiskEncryptionTarget]]]

        @overload
        def __init__(
                self, 
                *, 
                customer_managed_key: Optional[DiskCustomerManagedKey] = ..., 
                targets: Optional[list[Union[str, DiskEncryptionTarget]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.DiskEncryptionSetParameters(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.DiskEncryptionTarget(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OS_DISK = "OsDisk"
        TEMPORARY_DISK = "TemporaryDisk"


    class azure.mgmt.batch.models.DynamicVNetAssignmentScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JOB = "job"
        NONE = "none"


    class azure.mgmt.batch.models.ElevationLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMIN = "Admin"
        NON_ADMIN = "NonAdmin"


    class azure.mgmt.batch.models.EncryptionProperties(_Model):
        key_source: Optional[Union[str, KeySource]]
        key_vault_properties: Optional[KeyVaultProperties]

        @overload
        def __init__(
                self, 
                *, 
                key_source: Optional[Union[str, KeySource]] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.EndpointAccessDefaultAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.batch.models.EndpointAccessProfile(_Model):
        default_action: Union[str, EndpointAccessDefaultAction]
        ip_rules: Optional[list[IPRule]]

        @overload
        def __init__(
                self, 
                *, 
                default_action: Union[str, EndpointAccessDefaultAction], 
                ip_rules: Optional[list[IPRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.EndpointDependency(_Model):
        description: Optional[str]
        domain_name: Optional[str]
        endpoint_details: Optional[list[EndpointDetail]]


    class azure.mgmt.batch.models.EndpointDetail(_Model):
        port: Optional[int]


    class azure.mgmt.batch.models.EnvironmentSetting(_Model):
        name: str
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.batch.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.batch.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.FixedScaleSettings(_Model):
        node_deallocation_option: Optional[Union[str, ComputeNodeDeallocationOption]]
        resize_timeout: Optional[timedelta]
        target_dedicated_nodes: Optional[int]
        target_low_priority_nodes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                node_deallocation_option: Optional[Union[str, ComputeNodeDeallocationOption]] = ..., 
                resize_timeout: Optional[timedelta] = ..., 
                target_dedicated_nodes: Optional[int] = ..., 
                target_low_priority_nodes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.HostEndpointSettings(_Model):
        in_vm_access_control_profile_reference_id: Optional[str]
        mode: Optional[Union[str, HostEndpointSettingsModeTypes]]

        @overload
        def __init__(
                self, 
                *, 
                in_vm_access_control_profile_reference_id: Optional[str] = ..., 
                mode: Optional[Union[str, HostEndpointSettingsModeTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.HostEndpointSettingsModeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCE = "Enforce"


    class azure.mgmt.batch.models.IPAddressProvisioningType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BATCH_MANAGED = "BatchManaged"
        NO_PUBLIC_IP_ADDRESSES = "NoPublicIPAddresses"
        USER_MANAGED = "UserManaged"


    class azure.mgmt.batch.models.IPFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.batch.models.IPRule(_Model):
        action: Union[str, IPRuleAction]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, IPRuleAction], 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.IPRuleAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"


    class azure.mgmt.batch.models.IPTag(_Model):
        ip_tag_type: Optional[str]
        tag: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_tag_type: Optional[str] = ..., 
                tag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ImageReference(_Model):
        community_gallery_image_id: Optional[str]
        id: Optional[str]
        offer: Optional[str]
        publisher: Optional[str]
        shared_gallery_image_id: Optional[str]
        sku: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                community_gallery_image_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                offer: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                shared_gallery_image_id: Optional[str] = ..., 
                sku: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.InboundEndpointProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.batch.models.InboundNatPool(_Model):
        backend_port: int
        frontend_port_range_end: int
        frontend_port_range_start: int
        name: str
        network_security_group_rules: Optional[list[NetworkSecurityGroupRule]]
        protocol: Union[str, InboundEndpointProtocol]

        @overload
        def __init__(
                self, 
                *, 
                backend_port: int, 
                frontend_port_range_end: int, 
                frontend_port_range_start: int, 
                name: str, 
                network_security_group_rules: Optional[list[NetworkSecurityGroupRule]] = ..., 
                protocol: Union[str, InboundEndpointProtocol]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.InterNodeCommunicationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.batch.models.IssueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_PROPAGATION_FAILURE = "ConfigurationPropagationFailure"
        MISSING_IDENTITY_CONFIGURATION = "MissingIdentityConfiguration"
        MISSING_PERIMETER_CONFIGURATION = "MissingPerimeterConfiguration"
        UNKNOWN = "Unknown"


    class azure.mgmt.batch.models.JobDefaultOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATION_TIME = "CreationTime"
        NONE = "None"


    class azure.mgmt.batch.models.KeySource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_BATCH = "Microsoft.Batch"
        MICROSOFT_KEY_VAULT = "Microsoft.KeyVault"


    class azure.mgmt.batch.models.KeyVaultProperties(_Model):
        key_identifier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_identifier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.KeyVaultReference(_Model):
        id: str
        url: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.LinuxUserConfiguration(_Model):
        gid: Optional[int]
        ssh_private_key: Optional[str]
        uid: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                gid: Optional[int] = ..., 
                ssh_private_key: Optional[str] = ..., 
                uid: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.LoginMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BATCH = "Batch"
        INTERACTIVE = "Interactive"


    class azure.mgmt.batch.models.ManagedDisk(_Model):
        disk_encryption_set: Optional[DiskEncryptionSetParameters]
        security_profile: Optional[VMDiskSecurityProfile]
        storage_account_type: Optional[Union[str, StorageAccountType]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set: Optional[DiskEncryptionSetParameters] = ..., 
                security_profile: Optional[VMDiskSecurityProfile] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.MetadataItem(_Model):
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.MountConfiguration(_Model):
        azure_blob_file_system_configuration: Optional[AzureBlobFileSystemConfiguration]
        azure_file_share_configuration: Optional[AzureFileShareConfiguration]
        cifs_mount_configuration: Optional[CIFSMountConfiguration]
        nfs_mount_configuration: Optional[NFSMountConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                azure_blob_file_system_configuration: Optional[AzureBlobFileSystemConfiguration] = ..., 
                azure_file_share_configuration: Optional[AzureFileShareConfiguration] = ..., 
                cifs_mount_configuration: Optional[CIFSMountConfiguration] = ..., 
                nfs_mount_configuration: Optional[NFSMountConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.NFSMountConfiguration(_Model):
        mount_options: Optional[str]
        relative_mount_path: str
        source: str

        @overload
        def __init__(
                self, 
                *, 
                mount_options: Optional[str] = ..., 
                relative_mount_path: str, 
                source: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.NameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.batch.models.NetworkConfiguration(_Model):
        dynamic_vnet_assignment_scope: Optional[Union[str, DynamicVNetAssignmentScope]]
        enable_accelerated_networking: Optional[bool]
        endpoint_configuration: Optional[PoolEndpointConfiguration]
        public_ip_address_configuration: Optional[PublicIPAddressConfiguration]
        subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_vnet_assignment_scope: Optional[Union[str, DynamicVNetAssignmentScope]] = ..., 
                enable_accelerated_networking: Optional[bool] = ..., 
                endpoint_configuration: Optional[PoolEndpointConfiguration] = ..., 
                public_ip_address_configuration: Optional[PublicIPAddressConfiguration] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.NetworkProfile(_Model):
        account_access: Optional[EndpointAccessProfile]
        node_management_access: Optional[EndpointAccessProfile]

        @overload
        def __init__(
                self, 
                *, 
                account_access: Optional[EndpointAccessProfile] = ..., 
                node_management_access: Optional[EndpointAccessProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.NetworkSecurityGroupRule(_Model):
        access: Union[str, NetworkSecurityGroupRuleAccess]
        priority: int
        source_address_prefix: str
        source_port_ranges: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                access: Union[str, NetworkSecurityGroupRuleAccess], 
                priority: int, 
                source_address_prefix: str, 
                source_port_ranges: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.NetworkSecurityGroupRuleAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.batch.models.NetworkSecurityPerimeter(_Model):
        id: Optional[str]
        location: Optional[str]
        perimeter_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                perimeter_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.NetworkSecurityPerimeterConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[NetworkSecurityPerimeterConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkSecurityPerimeterConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.NetworkSecurityPerimeterConfigurationProperties(_Model):
        network_security_perimeter: Optional[NetworkSecurityPerimeter]
        profile: Optional[NetworkSecurityProfile]
        provisioning_issues: Optional[list[ProvisioningIssue]]
        provisioning_state: Optional[Union[str, NetworkSecurityPerimeterConfigurationProvisioningState]]
        resource_association: Optional[ResourceAssociation]

        @overload
        def __init__(
                self, 
                *, 
                network_security_perimeter: Optional[NetworkSecurityPerimeter] = ..., 
                profile: Optional[NetworkSecurityProfile] = ..., 
                resource_association: Optional[ResourceAssociation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.NetworkSecurityPerimeterConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.batch.models.NetworkSecurityProfile(_Model):
        access_rules: Optional[list[AccessRule]]
        access_rules_version: Optional[int]
        diagnostic_settings_version: Optional[int]
        enabled_log_categories: Optional[list[str]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_rules: Optional[list[AccessRule]] = ..., 
                access_rules_version: Optional[int] = ..., 
                diagnostic_settings_version: Optional[int] = ..., 
                enabled_log_categories: Optional[list[str]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.NodePlacementConfiguration(_Model):
        policy: Optional[Union[str, NodePlacementPolicyType]]

        @overload
        def __init__(
                self, 
                *, 
                policy: Optional[Union[str, NodePlacementPolicyType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.NodePlacementPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGIONAL = "Regional"
        ZONAL = "Zonal"


    class azure.mgmt.batch.models.OSDisk(_Model):
        caching: Optional[Union[str, CachingType]]
        disk_size_gb: Optional[int]
        ephemeral_os_disk_settings: Optional[DiffDiskSettings]
        managed_disk: Optional[ManagedDisk]
        write_accelerator_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, CachingType]] = ..., 
                disk_size_gb: Optional[int] = ..., 
                ephemeral_os_disk_settings: Optional[DiffDiskSettings] = ..., 
                managed_disk: Optional[ManagedDisk] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.OperationDisplay(_Model):
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


    class azure.mgmt.batch.models.OutboundEnvironmentEndpoint(_Model):
        category: Optional[str]
        endpoints: Optional[list[EndpointDependency]]


    class azure.mgmt.batch.models.PackageState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        PENDING = "Pending"


    class azure.mgmt.batch.models.Pool(ProxyResource):
        etag: Optional[str]
        id: str
        identity: Optional[BatchPoolIdentity]
        name: str
        properties: Optional[PoolProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[BatchPoolIdentity] = ..., 
                properties: Optional[PoolProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.batch.models.PoolAllocationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BATCH_SERVICE = "BatchService"
        USER_SUBSCRIPTION = "UserSubscription"


    class azure.mgmt.batch.models.PoolEndpointConfiguration(_Model):
        inbound_nat_pools: list[InboundNatPool]

        @overload
        def __init__(
                self, 
                *, 
                inbound_nat_pools: list[InboundNatPool]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.PoolIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.batch.models.PoolProperties(_Model):
        allocation_state: Optional[Union[str, AllocationState]]
        allocation_state_transition_time: Optional[datetime]
        application_packages: Optional[list[ApplicationPackageReference]]
        auto_scale_run: Optional[AutoScaleRun]
        creation_time: Optional[datetime]
        current_dedicated_nodes: Optional[int]
        current_low_priority_nodes: Optional[int]
        deployment_configuration: Optional[DeploymentConfiguration]
        display_name: Optional[str]
        inter_node_communication: Optional[Union[str, InterNodeCommunicationState]]
        last_modified: Optional[datetime]
        metadata: Optional[list[MetadataItem]]
        mount_configuration: Optional[list[MountConfiguration]]
        network_configuration: Optional[NetworkConfiguration]
        provisioning_state: Optional[Union[str, PoolProvisioningState]]
        provisioning_state_transition_time: Optional[datetime]
        resize_operation_status: Optional[ResizeOperationStatus]
        scale_settings: Optional[ScaleSettings]
        start_task: Optional[StartTask]
        task_scheduling_policy: Optional[TaskSchedulingPolicy]
        task_slots_per_node: Optional[int]
        upgrade_policy: Optional[UpgradePolicy]
        user_accounts: Optional[list[UserAccount]]
        vm_size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_packages: Optional[list[ApplicationPackageReference]] = ..., 
                deployment_configuration: Optional[DeploymentConfiguration] = ..., 
                display_name: Optional[str] = ..., 
                inter_node_communication: Optional[Union[str, InterNodeCommunicationState]] = ..., 
                metadata: Optional[list[MetadataItem]] = ..., 
                mount_configuration: Optional[list[MountConfiguration]] = ..., 
                network_configuration: Optional[NetworkConfiguration] = ..., 
                scale_settings: Optional[ScaleSettings] = ..., 
                start_task: Optional[StartTask] = ..., 
                task_scheduling_policy: Optional[TaskSchedulingPolicy] = ..., 
                task_slots_per_node: Optional[int] = ..., 
                upgrade_policy: Optional[UpgradePolicy] = ..., 
                user_accounts: Optional[list[UserAccount]] = ..., 
                vm_size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.PoolProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.batch.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.batch.models.PrivateEndpointConnection(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.batch.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState]
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.batch.models.PrivateLinkResource(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.batch.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]


    class azure.mgmt.batch.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Union[str, PrivateLinkServiceConnectionStatus]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                status: Union[str, PrivateLinkServiceConnectionStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.PrivateLinkServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.batch.models.ProvisioningIssue(_Model):
        name: Optional[str]
        properties: Optional[ProvisioningIssueProperties]


    class azure.mgmt.batch.models.ProvisioningIssueProperties(_Model):
        description: Optional[str]
        issue_type: Optional[Union[str, IssueType]]
        severity: Optional[Union[str, Severity]]
        suggested_access_rules: Optional[list[AccessRule]]
        suggested_resource_ids: Optional[list[str]]


    class azure.mgmt.batch.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        INVALID = "Invalid"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.batch.models.ProxyAgentSettings(_Model):
        enabled: Optional[bool]
        imds: Optional[HostEndpointSettings]
        wire_server: Optional[HostEndpointSettings]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                imds: Optional[HostEndpointSettings] = ..., 
                wire_server: Optional[HostEndpointSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.batch.models.PublicIPAddressConfiguration(_Model):
        ip_address_ids: Optional[list[str]]
        ip_families: Optional[list[Union[str, IPFamily]]]
        ip_tags: Optional[list[IPTag]]
        provision: Optional[Union[str, IPAddressProvisioningType]]

        @overload
        def __init__(
                self, 
                *, 
                ip_address_ids: Optional[list[str]] = ..., 
                ip_families: Optional[list[Union[str, IPFamily]]] = ..., 
                ip_tags: Optional[list[IPTag]] = ..., 
                provision: Optional[Union[str, IPAddressProvisioningType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.PublicNetworkAccessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.batch.models.ResizeError(_Model):
        code: str
        details: Optional[list[ResizeError]]
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[list[ResizeError]] = ..., 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ResizeOperationStatus(_Model):
        errors: Optional[list[ResizeError]]
        node_deallocation_option: Optional[Union[str, ComputeNodeDeallocationOption]]
        resize_timeout: Optional[timedelta]
        start_time: Optional[datetime]
        target_dedicated_nodes: Optional[int]
        target_low_priority_nodes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                errors: Optional[list[ResizeError]] = ..., 
                node_deallocation_option: Optional[Union[str, ComputeNodeDeallocationOption]] = ..., 
                resize_timeout: Optional[timedelta] = ..., 
                start_time: Optional[datetime] = ..., 
                target_dedicated_nodes: Optional[int] = ..., 
                target_low_priority_nodes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.batch.models.ResourceAssociation(_Model):
        access_mode: Optional[Union[str, ResourceAssociationAccessMode]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, ResourceAssociationAccessMode]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ResourceAssociationAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCED = "Enforced"
        LEARNING = "Learning"


    class azure.mgmt.batch.models.ResourceFile(_Model):
        auto_storage_container_name: Optional[str]
        blob_prefix: Optional[str]
        file_mode: Optional[str]
        file_path: Optional[str]
        http_url: Optional[str]
        identity_reference: Optional[ComputeNodeIdentityReference]
        storage_container_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_storage_container_name: Optional[str] = ..., 
                blob_prefix: Optional[str] = ..., 
                file_mode: Optional[str] = ..., 
                file_path: Optional[str] = ..., 
                http_url: Optional[str] = ..., 
                identity_reference: Optional[ComputeNodeIdentityReference] = ..., 
                storage_container_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.batch.models.ResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_BATCH_BATCH_ACCOUNTS = "Microsoft.Batch/batchAccounts"


    class azure.mgmt.batch.models.RollingUpgradePolicy(_Model):
        enable_cross_zone_upgrade: Optional[bool]
        max_batch_instance_percent: Optional[int]
        max_unhealthy_instance_percent: Optional[int]
        max_unhealthy_upgraded_instance_percent: Optional[int]
        pause_time_between_batches: Optional[str]
        prioritize_unhealthy_instances: Optional[bool]
        rollback_failed_instances_on_policy_breach: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_cross_zone_upgrade: Optional[bool] = ..., 
                max_batch_instance_percent: Optional[int] = ..., 
                max_unhealthy_instance_percent: Optional[int] = ..., 
                max_unhealthy_upgraded_instance_percent: Optional[int] = ..., 
                pause_time_between_batches: Optional[str] = ..., 
                prioritize_unhealthy_instances: Optional[bool] = ..., 
                rollback_failed_instances_on_policy_breach: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.ScaleSettings(_Model):
        auto_scale: Optional[AutoScaleSettings]
        fixed_scale: Optional[FixedScaleSettings]

        @overload
        def __init__(
                self, 
                *, 
                auto_scale: Optional[AutoScaleSettings] = ..., 
                fixed_scale: Optional[FixedScaleSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.SecurityEncryptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK_WITH_VM_GUEST_STATE = "DiskWithVMGuestState"
        NON_PERSISTED_TPM = "NonPersistedTPM"
        VM_GUEST_STATE_ONLY = "VMGuestStateOnly"


    class azure.mgmt.batch.models.SecurityProfile(_Model):
        encryption_at_host: Optional[bool]
        proxy_agent_settings: Optional[ProxyAgentSettings]
        security_type: Optional[Union[str, SecurityTypes]]
        uefi_settings: Optional[UefiSettings]

        @overload
        def __init__(
                self, 
                *, 
                encryption_at_host: Optional[bool] = ..., 
                proxy_agent_settings: Optional[ProxyAgentSettings] = ..., 
                security_type: Optional[Union[str, SecurityTypes]] = ..., 
                uefi_settings: Optional[UefiSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.SecurityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL_VM = "confidentialVM"
        TRUSTED_LAUNCH = "trustedLaunch"


    class azure.mgmt.batch.models.ServiceArtifactReference(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        WARNING = "Warning"


    class azure.mgmt.batch.models.SkuCapability(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.batch.models.StartTask(_Model):
        command_line: Optional[str]
        container_settings: Optional[TaskContainerSettings]
        environment_settings: Optional[list[EnvironmentSetting]]
        max_task_retry_count: Optional[int]
        resource_files: Optional[list[ResourceFile]]
        user_identity: Optional[UserIdentity]
        wait_for_success: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                command_line: Optional[str] = ..., 
                container_settings: Optional[TaskContainerSettings] = ..., 
                environment_settings: Optional[list[EnvironmentSetting]] = ..., 
                max_task_retry_count: Optional[int] = ..., 
                resource_files: Optional[list[ResourceFile]] = ..., 
                user_identity: Optional[UserIdentity] = ..., 
                wait_for_success: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.StorageAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSD_LRS = "StandardSSD_LRS"


    class azure.mgmt.batch.models.SupportedSku(_Model):
        batch_support_end_of_life: Optional[datetime]
        capabilities: Optional[list[SkuCapability]]
        family_name: Optional[str]
        name: Optional[str]


    class azure.mgmt.batch.models.SystemData(_Model):
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


    class azure.mgmt.batch.models.TaskContainerSettings(_Model):
        container_host_batch_bind_mounts: Optional[list[ContainerHostBatchBindMountEntry]]
        container_run_options: Optional[str]
        image_name: str
        registry: Optional[ContainerRegistry]
        working_directory: Optional[Union[str, ContainerWorkingDirectory]]

        @overload
        def __init__(
                self, 
                *, 
                container_host_batch_bind_mounts: Optional[list[ContainerHostBatchBindMountEntry]] = ..., 
                container_run_options: Optional[str] = ..., 
                image_name: str, 
                registry: Optional[ContainerRegistry] = ..., 
                working_directory: Optional[Union[str, ContainerWorkingDirectory]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.TaskSchedulingPolicy(_Model):
        job_default_order: Optional[Union[str, JobDefaultOrder]]
        node_fill_type: Union[str, ComputeNodeFillType]

        @overload
        def __init__(
                self, 
                *, 
                job_default_order: Optional[Union[str, JobDefaultOrder]] = ..., 
                node_fill_type: Union[str, ComputeNodeFillType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.UefiSettings(_Model):
        secure_boot_enabled: Optional[bool]
        v_tpm_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                secure_boot_enabled: Optional[bool] = ..., 
                v_tpm_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.UpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "automatic"
        MANUAL = "manual"
        ROLLING = "rolling"


    class azure.mgmt.batch.models.UpgradePolicy(_Model):
        automatic_os_upgrade_policy: Optional[AutomaticOSUpgradePolicy]
        mode: Union[str, UpgradeMode]
        rolling_upgrade_policy: Optional[RollingUpgradePolicy]

        @overload
        def __init__(
                self, 
                *, 
                automatic_os_upgrade_policy: Optional[AutomaticOSUpgradePolicy] = ..., 
                mode: Union[str, UpgradeMode], 
                rolling_upgrade_policy: Optional[RollingUpgradePolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.UserAccount(_Model):
        elevation_level: Optional[Union[str, ElevationLevel]]
        linux_user_configuration: Optional[LinuxUserConfiguration]
        name: str
        password: str
        windows_user_configuration: Optional[WindowsUserConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                elevation_level: Optional[Union[str, ElevationLevel]] = ..., 
                linux_user_configuration: Optional[LinuxUserConfiguration] = ..., 
                name: str, 
                password: str, 
                windows_user_configuration: Optional[WindowsUserConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.UserAssignedIdentities(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.batch.models.UserIdentity(_Model):
        auto_user: Optional[AutoUserSpecification]
        user_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_user: Optional[AutoUserSpecification] = ..., 
                user_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.VMDiskSecurityProfile(_Model):
        disk_encryption_set: Optional[DiskEncryptionSetParameters]
        security_encryption_type: Optional[Union[str, SecurityEncryptionTypes]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set: Optional[DiskEncryptionSetParameters] = ..., 
                security_encryption_type: Optional[Union[str, SecurityEncryptionTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.VMExtension(_Model):
        auto_upgrade_minor_version: Optional[bool]
        enable_automatic_upgrade: Optional[bool]
        name: str
        protected_settings: Optional[Any]
        provision_after_extensions: Optional[list[str]]
        publisher: str
        settings: Optional[Any]
        type: str
        type_handler_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_minor_version: Optional[bool] = ..., 
                enable_automatic_upgrade: Optional[bool] = ..., 
                name: str, 
                protected_settings: Optional[Any] = ..., 
                provision_after_extensions: Optional[list[str]] = ..., 
                publisher: str, 
                settings: Optional[Any] = ..., 
                type: str, 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.VirtualMachineConfiguration(_Model):
        container_configuration: Optional[ContainerConfiguration]
        data_disks: Optional[list[DataDisk]]
        disk_encryption_configuration: Optional[DiskEncryptionConfiguration]
        extensions: Optional[list[VMExtension]]
        image_reference: ImageReference
        license_type: Optional[str]
        node_agent_sku_id: str
        node_placement_configuration: Optional[NodePlacementConfiguration]
        os_disk: Optional[OSDisk]
        security_profile: Optional[SecurityProfile]
        service_artifact_reference: Optional[ServiceArtifactReference]
        windows_configuration: Optional[WindowsConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                container_configuration: Optional[ContainerConfiguration] = ..., 
                data_disks: Optional[list[DataDisk]] = ..., 
                disk_encryption_configuration: Optional[DiskEncryptionConfiguration] = ..., 
                extensions: Optional[list[VMExtension]] = ..., 
                image_reference: ImageReference, 
                license_type: Optional[str] = ..., 
                node_agent_sku_id: str, 
                node_placement_configuration: Optional[NodePlacementConfiguration] = ..., 
                os_disk: Optional[OSDisk] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                service_artifact_reference: Optional[ServiceArtifactReference] = ..., 
                windows_configuration: Optional[WindowsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.VirtualMachineFamilyCoreQuota(_Model):
        core_quota: Optional[int]
        name: Optional[str]


    class azure.mgmt.batch.models.WindowsConfiguration(_Model):
        enable_automatic_updates: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_automatic_updates: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.batch.models.WindowsUserConfiguration(_Model):
        login_mode: Optional[Union[str, LoginMode]]

        @overload
        def __init__(
                self, 
                *, 
                login_mode: Optional[Union[str, LoginMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.batch.operations

    class azure.mgmt.batch.operations.ApplicationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                parameters: Optional[Application] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> Application: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                maxresults: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Application]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                parameters: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...


    class azure.mgmt.batch.operations.ApplicationPackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def activate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                parameters: ActivateApplicationPackageParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @overload
        def activate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @overload
        def activate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                parameters: Optional[ApplicationPackage] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> ApplicationPackage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                application_name: str, 
                *, 
                maxresults: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ApplicationPackage]: ...


    class azure.mgmt.batch.operations.BatchAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BatchAccountCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BatchAccount]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BatchAccount]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BatchAccount]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> BatchAccount: ...

        @distributed_trace
        def get_detector(
                self, 
                resource_group_name: str, 
                account_name: str, 
                detector_id: str, 
                **kwargs: Any
            ) -> DetectorResponse: ...

        @distributed_trace
        def get_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> BatchAccountKeys: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[BatchAccount]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BatchAccount]: ...

        @distributed_trace
        def list_detectors(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DetectorResponse]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OutboundEnvironmentEndpoint]: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BatchAccountRegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchAccountKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchAccountKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchAccountKeys: ...

        @distributed_trace
        def synchronize_auto_storage_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BatchAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchAccount: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchAccount: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchAccount: ...


    class azure.mgmt.batch.operations.LocationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_name_availability(
                self, 
                location_name: str, 
                parameters: CheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                location_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                location_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace
        def get_quotas(
                self, 
                location_name: str, 
                **kwargs: Any
            ) -> BatchLocationQuota: ...

        @distributed_trace
        def list_supported_virtual_machine_skus(
                self, 
                location_name: str, 
                *, 
                filter: Optional[str] = ..., 
                maxresults: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SupportedSku]: ...


    class azure.mgmt.batch.operations.NetworkSecurityPerimeterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_reconcile_configuration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_configuration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list_configurations(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.batch.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.batch.operations.PoolOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                parameters: Pool, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Pool: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Pool: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace
        def disable_auto_scale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace
        def list_by_batch_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                maxresults: Optional[int] = ..., 
                select: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Pool]: ...

        @distributed_trace
        def stop_resize(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                parameters: Pool, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Pool: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Pool: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Pool: ...


    class azure.mgmt.batch.operations.PrivateEndpointConnectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_batch_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                maxresults: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.batch.operations.PrivateLinkResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_batch_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                maxresults: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


```