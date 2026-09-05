```py
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
                parameters: CheckNameAvailabilityParameters, 
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


    class azure.mgmt.batch.models.BatchAccount(TrackedResource):
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


    class azure.mgmt.batch.models.TrackedResource(Resource):
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
                parameters: CheckNameAvailabilityParameters, 
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


namespace azure.mgmt.batch.types

    class azure.mgmt.batch.types.ActivateApplicationPackageParameters(TypedDict, total=False):
        key "format": Required[str]
        format: str


    class azure.mgmt.batch.types.Application(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ApplicationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: ApplicationProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.batch.types.ApplicationPackage(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ApplicationPackageProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: ApplicationPackageProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.batch.types.ApplicationPackageProperties(TypedDict, total=False):
        key "format": str
        key "lastActivationTime": str
        key "state": Union[str, PackageState]
        key "storageUrl": str
        key "storageUrlExpiry": str
        format: str
        lastActivationTime: str
        state: Union[str, PackageState]
        storageUrl: str
        storageUrlExpiry: str


    class azure.mgmt.batch.types.ApplicationPackageReference(TypedDict, total=False):
        key "id": Required[str]
        key "version": str
        id: str
        version: str


    class azure.mgmt.batch.types.ApplicationProperties(TypedDict, total=False):
        key "allowUpdates": bool
        key "defaultVersion": str
        key "displayName": str
        allowUpdates: bool
        defaultVersion: str
        displayName: str


    class azure.mgmt.batch.types.AutoScaleRun(TypedDict, total=False):
        key "error": ForwardRef('AutoScaleRunError', module='types')
        key "evaluationTime": Required[str]
        key "results": str
        error: AutoScaleRunError
        evaluationTime: str
        results: str


    class azure.mgmt.batch.types.AutoScaleRunError(TypedDict, total=False):
        key "code": Required[str]
        key "message": Required[str]
        code: str
        details: list[AutoScaleRunError]
        message: str


    class azure.mgmt.batch.types.AutoScaleSettings(TypedDict, total=False):
        key "evaluationInterval": str
        key "formula": Required[str]
        evaluationInterval: str
        formula: str


    class azure.mgmt.batch.types.AutoStorageBaseProperties(TypedDict, total=False):
        key "authenticationMode": Union[str, AutoStorageAuthenticationMode]
        key "nodeIdentityReference": ForwardRef('ComputeNodeIdentityReference', module='types')
        key "storageAccountId": Required[str]
        authenticationMode: Union[str, AutoStorageAuthenticationMode]
        nodeIdentityReference: ComputeNodeIdentityReference
        storageAccountId: str


    class azure.mgmt.batch.types.AutoUserSpecification(TypedDict, total=False):
        key "elevationLevel": Union[str, ElevationLevel]
        key "scope": Union[str, AutoUserScope]
        elevationLevel: Union[str, ElevationLevel]
        scope: Union[str, AutoUserScope]


    class azure.mgmt.batch.types.AutomaticOSUpgradePolicy(TypedDict, total=False):
        key "disableAutomaticRollback": bool
        key "enableAutomaticOSUpgrade": bool
        key "osRollingUpgradeDeferral": bool
        key "useRollingUpgradePolicy": bool
        disableAutomaticRollback: bool
        enableAutomaticOSUpgrade: bool
        osRollingUpgradeDeferral: bool
        useRollingUpgradePolicy: bool


    class azure.mgmt.batch.types.AzureBlobFileSystemConfiguration(TypedDict, total=False):
        key "accountKey": str
        key "accountName": Required[str]
        key "blobfuseOptions": str
        key "containerName": Required[str]
        key "identityReference": ForwardRef('ComputeNodeIdentityReference', module='types')
        key "relativeMountPath": Required[str]
        key "sasKey": str
        accountKey: str
        accountName: str
        blobfuseOptions: str
        containerName: str
        identityReference: ComputeNodeIdentityReference
        relativeMountPath: str
        sasKey: str


    class azure.mgmt.batch.types.AzureFileShareConfiguration(TypedDict, total=False):
        key "accountKey": Required[str]
        key "accountName": Required[str]
        key "azureFileUrl": Required[str]
        key "mountOptions": str
        key "relativeMountPath": Required[str]
        accountKey: str
        accountName: str
        azureFileUrl: str
        mountOptions: str
        relativeMountPath: str


    class azure.mgmt.batch.types.BatchAccountCreateParameters(TypedDict, total=False):
        key "identity": ForwardRef('BatchAccountIdentity', module='types')
        key "location": Required[str]
        key "properties": ForwardRef('BatchAccountCreateProperties', module='types')
        identity: BatchAccountIdentity
        location: str
        properties: BatchAccountCreateProperties
        tags: dict[str, str]


    class azure.mgmt.batch.types.BatchAccountCreateProperties(TypedDict, total=False):
        key "allowedAuthenticationModes": Optional[list[Union[str, AuthenticationMode]]]
        key "autoStorage": ForwardRef('AutoStorageBaseProperties', module='types')
        key "encryption": ForwardRef('EncryptionProperties', module='types')
        key "keyVaultReference": ForwardRef('KeyVaultReference', module='types')
        key "networkProfile": ForwardRef('NetworkProfile', module='types')
        key "poolAllocationMode": Union[str, PoolAllocationMode]
        key "publicNetworkAccess": Union[str, PublicNetworkAccessType]
        allowedAuthenticationModes: list[Union[str, AuthenticationMode]]
        autoStorage: AutoStorageBaseProperties
        encryption: EncryptionProperties
        keyVaultReference: KeyVaultReference
        networkProfile: NetworkProfile
        poolAllocationMode: Union[str, PoolAllocationMode]
        publicNetworkAccess: Union[str, PublicNetworkAccessType]


    class azure.mgmt.batch.types.BatchAccountIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ResourceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentities]


    class azure.mgmt.batch.types.BatchAccountRegenerateKeyParameters(TypedDict, total=False):
        key "keyName": Required[Union[str, AccountKeyType]]
        keyName: Union[str, AccountKeyType]


    class azure.mgmt.batch.types.BatchAccountUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('BatchAccountIdentity', module='types')
        key "properties": ForwardRef('BatchAccountUpdateProperties', module='types')
        identity: BatchAccountIdentity
        properties: BatchAccountUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.batch.types.BatchAccountUpdateProperties(TypedDict, total=False):
        key "allowedAuthenticationModes": Optional[list[Union[str, AuthenticationMode]]]
        key "autoStorage": ForwardRef('AutoStorageBaseProperties', module='types')
        key "encryption": ForwardRef('EncryptionProperties', module='types')
        key "networkProfile": ForwardRef('NetworkProfile', module='types')
        key "publicNetworkAccess": Union[str, PublicNetworkAccessType]
        allowedAuthenticationModes: list[Union[str, AuthenticationMode]]
        autoStorage: AutoStorageBaseProperties
        encryption: EncryptionProperties
        networkProfile: NetworkProfile
        publicNetworkAccess: Union[str, PublicNetworkAccessType]


    class azure.mgmt.batch.types.BatchPoolIdentity(TypedDict, total=False):
        key "type": Required[Union[str, PoolIdentityType]]
        type: Union[str, PoolIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentities]


    class azure.mgmt.batch.types.CIFSMountConfiguration(TypedDict, total=False):
        key "mountOptions": str
        key "password": Required[str]
        key "relativeMountPath": Required[str]
        key "source": Required[str]
        key "userName": Required[str]
        mountOptions: str
        password: str
        relativeMountPath: str
        source: str
        userName: str


    class azure.mgmt.batch.types.CheckNameAvailabilityParameters(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, ResourceType]]
        name: str
        type: Union[str, ResourceType]


    class azure.mgmt.batch.types.ComputeNodeIdentityReference(TypedDict, total=False):
        key "resourceId": str
        resourceId: str


    class azure.mgmt.batch.types.ContainerConfiguration(TypedDict, total=False):
        key "type": Required[Union[str, ContainerType]]
        containerImageNames: list[str]
        containerRegistries: list[ContainerRegistry]
        type: Union[str, ContainerType]


    class azure.mgmt.batch.types.ContainerHostBatchBindMountEntry(TypedDict, total=False):
        key "isReadOnly": bool
        key "source": Union[str, ContainerHostDataPath]
        isReadOnly: bool
        source: Union[str, ContainerHostDataPath]


    class azure.mgmt.batch.types.ContainerRegistry(TypedDict, total=False):
        key "identityReference": ForwardRef('ComputeNodeIdentityReference', module='types')
        key "password": str
        key "registryServer": str
        key "username": str
        identityReference: ComputeNodeIdentityReference
        password: str
        registryServer: str
        username: str


    class azure.mgmt.batch.types.DataDisk(TypedDict, total=False):
        key "caching": Union[str, CachingType]
        key "diskSizeGB": Required[int]
        key "lun": Required[int]
        key "managedDisk": ForwardRef('ManagedDisk', module='types')
        caching: Union[str, CachingType]
        diskSizeGB: int
        lun: int
        managedDisk: ManagedDisk


    class azure.mgmt.batch.types.DeploymentConfiguration(TypedDict, total=False):
        key "virtualMachineConfiguration": ForwardRef('VirtualMachineConfiguration', module='types')
        virtualMachineConfiguration: VirtualMachineConfiguration


    class azure.mgmt.batch.types.DiffDiskSettings(TypedDict, total=False):
        key "placement": Union[str, DiffDiskPlacement]
        placement: Union[str, DiffDiskPlacement]


    class azure.mgmt.batch.types.DiskCustomerManagedKey(TypedDict, total=False):
        key "identityReference": ForwardRef('ComputeNodeIdentityReference', module='types')
        key "keyUrl": str
        key "rotationToLatestKeyVersionEnabled": bool
        identityReference: ComputeNodeIdentityReference
        keyUrl: str
        rotationToLatestKeyVersionEnabled: bool


    class azure.mgmt.batch.types.DiskEncryptionConfiguration(TypedDict, total=False):
        key "customerManagedKey": ForwardRef('DiskCustomerManagedKey', module='types')
        customerManagedKey: DiskCustomerManagedKey
        targets: list[Union[str, DiskEncryptionTarget]]


    class azure.mgmt.batch.types.DiskEncryptionSetParameters(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.batch.types.EncryptionProperties(TypedDict, total=False):
        key "keySource": Union[str, KeySource]
        key "keyVaultProperties": ForwardRef('KeyVaultProperties', module='types')
        keySource: Union[str, KeySource]
        keyVaultProperties: KeyVaultProperties


    class azure.mgmt.batch.types.EndpointAccessProfile(TypedDict, total=False):
        key "defaultAction": Required[Union[str, EndpointAccessDefaultAction]]
        defaultAction: Union[str, EndpointAccessDefaultAction]
        ipRules: list[IPRule]


    class azure.mgmt.batch.types.EnvironmentSetting(TypedDict, total=False):
        key "name": Required[str]
        key "value": str
        name: str
        value: str


    class azure.mgmt.batch.types.FixedScaleSettings(TypedDict, total=False):
        key "nodeDeallocationOption": Union[str, ComputeNodeDeallocationOption]
        key "resizeTimeout": str
        key "targetDedicatedNodes": int
        key "targetLowPriorityNodes": int
        nodeDeallocationOption: Union[str, ComputeNodeDeallocationOption]
        resizeTimeout: str
        targetDedicatedNodes: int
        targetLowPriorityNodes: int


    class azure.mgmt.batch.types.HostEndpointSettings(TypedDict, total=False):
        key "inVMAccessControlProfileReferenceId": str
        key "mode": Union[str, HostEndpointSettingsModeTypes]
        inVMAccessControlProfileReferenceId: str
        mode: Union[str, HostEndpointSettingsModeTypes]


    class azure.mgmt.batch.types.IPRule(TypedDict, total=False):
        key "action": Required[Union[str, IPRuleAction]]
        key "value": Required[str]
        action: Union[str, IPRuleAction]
        value: str


    class azure.mgmt.batch.types.IPTag(TypedDict, total=False):
        key "ipTagType": str
        key "tag": str
        ipTagType: str
        tag: str


    class azure.mgmt.batch.types.ImageReference(TypedDict, total=False):
        key "communityGalleryImageId": str
        key "id": str
        key "offer": str
        key "publisher": str
        key "sharedGalleryImageId": str
        key "sku": str
        key "version": str
        communityGalleryImageId: str
        id: str
        offer: str
        publisher: str
        sharedGalleryImageId: str
        sku: str
        version: str


    class azure.mgmt.batch.types.InboundNatPool(TypedDict, total=False):
        key "backendPort": Required[int]
        key "frontendPortRangeEnd": Required[int]
        key "frontendPortRangeStart": Required[int]
        key "name": Required[str]
        key "protocol": Required[Union[str, InboundEndpointProtocol]]
        backendPort: int
        frontendPortRangeEnd: int
        frontendPortRangeStart: int
        name: str
        networkSecurityGroupRules: list[NetworkSecurityGroupRule]
        protocol: Union[str, InboundEndpointProtocol]


    class azure.mgmt.batch.types.KeyVaultProperties(TypedDict, total=False):
        key "keyIdentifier": str
        keyIdentifier: str


    class azure.mgmt.batch.types.KeyVaultReference(TypedDict, total=False):
        key "id": Required[str]
        key "url": Required[str]
        id: str
        url: str


    class azure.mgmt.batch.types.LinuxUserConfiguration(TypedDict, total=False):
        key "gid": int
        key "sshPrivateKey": str
        key "uid": int
        gid: int
        sshPrivateKey: str
        uid: int


    class azure.mgmt.batch.types.ManagedDisk(TypedDict, total=False):
        key "diskEncryptionSet": ForwardRef('DiskEncryptionSetParameters', module='types')
        key "securityProfile": ForwardRef('VMDiskSecurityProfile', module='types')
        key "storageAccountType": Union[str, StorageAccountType]
        diskEncryptionSet: DiskEncryptionSetParameters
        securityProfile: VMDiskSecurityProfile
        storageAccountType: Union[str, StorageAccountType]


    class azure.mgmt.batch.types.MetadataItem(TypedDict, total=False):
        key "name": Required[str]
        key "value": Required[str]
        name: str
        value: str


    class azure.mgmt.batch.types.MountConfiguration(TypedDict, total=False):
        key "azureBlobFileSystemConfiguration": ForwardRef('AzureBlobFileSystemConfiguration', module='types')
        key "azureFileShareConfiguration": ForwardRef('AzureFileShareConfiguration', module='types')
        key "cifsMountConfiguration": ForwardRef('CIFSMountConfiguration', module='types')
        key "nfsMountConfiguration": ForwardRef('NFSMountConfiguration', module='types')
        azureBlobFileSystemConfiguration: AzureBlobFileSystemConfiguration
        azureFileShareConfiguration: AzureFileShareConfiguration
        cifsMountConfiguration: CIFSMountConfiguration
        nfsMountConfiguration: NFSMountConfiguration


    class azure.mgmt.batch.types.NFSMountConfiguration(TypedDict, total=False):
        key "mountOptions": str
        key "relativeMountPath": Required[str]
        key "source": Required[str]
        mountOptions: str
        relativeMountPath: str
        source: str


    class azure.mgmt.batch.types.NetworkConfiguration(TypedDict, total=False):
        key "dynamicVnetAssignmentScope": Union[str, DynamicVNetAssignmentScope]
        key "enableAcceleratedNetworking": bool
        key "endpointConfiguration": ForwardRef('PoolEndpointConfiguration', module='types')
        key "publicIPAddressConfiguration": ForwardRef('PublicIPAddressConfiguration', module='types')
        key "subnetId": str
        dynamicVnetAssignmentScope: Union[str, DynamicVNetAssignmentScope]
        enableAcceleratedNetworking: bool
        endpointConfiguration: PoolEndpointConfiguration
        publicIPAddressConfiguration: PublicIPAddressConfiguration
        subnetId: str


    class azure.mgmt.batch.types.NetworkProfile(TypedDict, total=False):
        key "accountAccess": ForwardRef('EndpointAccessProfile', module='types')
        key "nodeManagementAccess": ForwardRef('EndpointAccessProfile', module='types')
        accountAccess: EndpointAccessProfile
        nodeManagementAccess: EndpointAccessProfile


    class azure.mgmt.batch.types.NetworkSecurityGroupRule(TypedDict, total=False):
        key "access": Required[Union[str, NetworkSecurityGroupRuleAccess]]
        key "priority": Required[int]
        key "sourceAddressPrefix": Required[str]
        access: Union[str, NetworkSecurityGroupRuleAccess]
        priority: int
        sourceAddressPrefix: str
        sourcePortRanges: list[str]


    class azure.mgmt.batch.types.NodePlacementConfiguration(TypedDict, total=False):
        key "policy": Union[str, NodePlacementPolicyType]
        policy: Union[str, NodePlacementPolicyType]


    class azure.mgmt.batch.types.OSDisk(TypedDict, total=False):
        key "caching": Union[str, CachingType]
        key "diskSizeGB": int
        key "ephemeralOSDiskSettings": ForwardRef('DiffDiskSettings', module='types')
        key "managedDisk": ForwardRef('ManagedDisk', module='types')
        key "writeAcceleratorEnabled": bool
        caching: Union[str, CachingType]
        diskSizeGB: int
        ephemeralOSDiskSettings: DiffDiskSettings
        managedDisk: ManagedDisk
        writeAcceleratorEnabled: bool


    class azure.mgmt.batch.types.Pool(ProxyResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('BatchPoolIdentity', module='types')
        key "name": str
        key "properties": ForwardRef('PoolProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: BatchPoolIdentity
        name: str
        properties: PoolProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.batch.types.PoolEndpointConfiguration(TypedDict, total=False):
        key "inboundNatPools": Required[list[InboundNatPool]]
        inboundNatPools: list[InboundNatPool]


    class azure.mgmt.batch.types.PoolProperties(TypedDict, total=False):
        key "allocationState": Union[str, AllocationState]
        key "allocationStateTransitionTime": str
        key "autoScaleRun": ForwardRef('AutoScaleRun', module='types')
        key "creationTime": str
        key "currentDedicatedNodes": int
        key "currentLowPriorityNodes": int
        key "deploymentConfiguration": ForwardRef('DeploymentConfiguration', module='types')
        key "displayName": str
        key "interNodeCommunication": Union[str, InterNodeCommunicationState]
        key "lastModified": str
        key "networkConfiguration": ForwardRef('NetworkConfiguration', module='types')
        key "provisioningState": Union[str, PoolProvisioningState]
        key "provisioningStateTransitionTime": str
        key "resizeOperationStatus": ForwardRef('ResizeOperationStatus', module='types')
        key "scaleSettings": ForwardRef('ScaleSettings', module='types')
        key "startTask": ForwardRef('StartTask', module='types')
        key "taskSchedulingPolicy": ForwardRef('TaskSchedulingPolicy', module='types')
        key "taskSlotsPerNode": int
        key "upgradePolicy": ForwardRef('UpgradePolicy', module='types')
        key "vmSize": str
        allocationState: Union[str, AllocationState]
        allocationStateTransitionTime: str
        applicationPackages: list[ApplicationPackageReference]
        autoScaleRun: AutoScaleRun
        creationTime: str
        currentDedicatedNodes: int
        currentLowPriorityNodes: int
        deploymentConfiguration: DeploymentConfiguration
        displayName: str
        interNodeCommunication: Union[str, InterNodeCommunicationState]
        lastModified: str
        metadata: list[MetadataItem]
        mountConfiguration: list[MountConfiguration]
        networkConfiguration: NetworkConfiguration
        provisioningState: Union[str, PoolProvisioningState]
        provisioningStateTransitionTime: str
        resizeOperationStatus: ResizeOperationStatus
        scaleSettings: ScaleSettings
        startTask: StartTask
        taskSchedulingPolicy: TaskSchedulingPolicy
        taskSlotsPerNode: int
        upgradePolicy: UpgradePolicy
        userAccounts: list[UserAccount]
        vmSize: str


    class azure.mgmt.batch.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.batch.types.PrivateEndpointConnection(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.batch.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('PrivateLinkServiceConnectionState', module='types')
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.batch.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Required[Union[str, PrivateLinkServiceConnectionStatus]]
        actionsRequired: str
        description: str
        status: Union[str, PrivateLinkServiceConnectionStatus]


    class azure.mgmt.batch.types.ProxyAgentSettings(TypedDict, total=False):
        key "enabled": bool
        key "imds": ForwardRef('HostEndpointSettings', module='types')
        key "wireServer": ForwardRef('HostEndpointSettings', module='types')
        enabled: bool
        imds: HostEndpointSettings
        wireServer: HostEndpointSettings


    class azure.mgmt.batch.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.batch.types.PublicIPAddressConfiguration(TypedDict, total=False):
        key "provision": Union[str, IPAddressProvisioningType]
        ipAddressIds: list[str]
        ipFamilies: list[Union[str, IPFamily]]
        ipTags: list[IPTag]
        provision: Union[str, IPAddressProvisioningType]


    class azure.mgmt.batch.types.ResizeError(TypedDict, total=False):
        key "code": Required[str]
        key "message": Required[str]
        code: str
        details: list[ResizeError]
        message: str


    class azure.mgmt.batch.types.ResizeOperationStatus(TypedDict, total=False):
        key "nodeDeallocationOption": Union[str, ComputeNodeDeallocationOption]
        key "resizeTimeout": str
        key "startTime": str
        key "targetDedicatedNodes": int
        key "targetLowPriorityNodes": int
        errors: list[ResizeError]
        nodeDeallocationOption: Union[str, ComputeNodeDeallocationOption]
        resizeTimeout: str
        startTime: str
        targetDedicatedNodes: int
        targetLowPriorityNodes: int


    class azure.mgmt.batch.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.batch.types.ResourceFile(TypedDict, total=False):
        key "autoStorageContainerName": str
        key "blobPrefix": str
        key "fileMode": str
        key "filePath": str
        key "httpUrl": str
        key "identityReference": ForwardRef('ComputeNodeIdentityReference', module='types')
        key "storageContainerUrl": str
        autoStorageContainerName: str
        blobPrefix: str
        fileMode: str
        filePath: str
        httpUrl: str
        identityReference: ComputeNodeIdentityReference
        storageContainerUrl: str


    class azure.mgmt.batch.types.RollingUpgradePolicy(TypedDict, total=False):
        key "enableCrossZoneUpgrade": bool
        key "maxBatchInstancePercent": int
        key "maxUnhealthyInstancePercent": int
        key "maxUnhealthyUpgradedInstancePercent": int
        key "pauseTimeBetweenBatches": str
        key "prioritizeUnhealthyInstances": bool
        key "rollbackFailedInstancesOnPolicyBreach": bool
        enableCrossZoneUpgrade: bool
        maxBatchInstancePercent: int
        maxUnhealthyInstancePercent: int
        maxUnhealthyUpgradedInstancePercent: int
        pauseTimeBetweenBatches: str
        prioritizeUnhealthyInstances: bool
        rollbackFailedInstancesOnPolicyBreach: bool


    class azure.mgmt.batch.types.ScaleSettings(TypedDict, total=False):
        key "autoScale": ForwardRef('AutoScaleSettings', module='types')
        key "fixedScale": ForwardRef('FixedScaleSettings', module='types')
        autoScale: AutoScaleSettings
        fixedScale: FixedScaleSettings


    class azure.mgmt.batch.types.SecurityProfile(TypedDict, total=False):
        key "encryptionAtHost": bool
        key "proxyAgentSettings": ForwardRef('ProxyAgentSettings', module='types')
        key "securityType": Union[str, SecurityTypes]
        key "uefiSettings": ForwardRef('UefiSettings', module='types')
        encryptionAtHost: bool
        proxyAgentSettings: ProxyAgentSettings
        securityType: Union[str, SecurityTypes]
        uefiSettings: UefiSettings


    class azure.mgmt.batch.types.ServiceArtifactReference(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.batch.types.StartTask(TypedDict, total=False):
        key "commandLine": str
        key "containerSettings": ForwardRef('TaskContainerSettings', module='types')
        key "maxTaskRetryCount": int
        key "userIdentity": ForwardRef('UserIdentity', module='types')
        key "waitForSuccess": bool
        commandLine: str
        containerSettings: TaskContainerSettings
        environmentSettings: list[EnvironmentSetting]
        maxTaskRetryCount: int
        resourceFiles: list[ResourceFile]
        userIdentity: UserIdentity
        waitForSuccess: bool


    class azure.mgmt.batch.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.batch.types.TaskContainerSettings(TypedDict, total=False):
        key "containerRunOptions": str
        key "imageName": Required[str]
        key "registry": ForwardRef('ContainerRegistry', module='types')
        key "workingDirectory": Union[str, ContainerWorkingDirectory]
        containerHostBatchBindMounts: list[ContainerHostBatchBindMountEntry]
        containerRunOptions: str
        imageName: str
        registry: ContainerRegistry
        workingDirectory: Union[str, ContainerWorkingDirectory]


    class azure.mgmt.batch.types.TaskSchedulingPolicy(TypedDict, total=False):
        key "jobDefaultOrder": Union[str, JobDefaultOrder]
        key "nodeFillType": Required[Union[str, ComputeNodeFillType]]
        jobDefaultOrder: Union[str, JobDefaultOrder]
        nodeFillType: Union[str, ComputeNodeFillType]


    class azure.mgmt.batch.types.UefiSettings(TypedDict, total=False):
        key "secureBootEnabled": bool
        key "vTpmEnabled": bool
        secureBootEnabled: bool
        vTpmEnabled: bool


    class azure.mgmt.batch.types.UpgradePolicy(TypedDict, total=False):
        key "automaticOSUpgradePolicy": ForwardRef('AutomaticOSUpgradePolicy', module='types')
        key "mode": Required[Union[str, UpgradeMode]]
        key "rollingUpgradePolicy": ForwardRef('RollingUpgradePolicy', module='types')
        automaticOSUpgradePolicy: AutomaticOSUpgradePolicy
        mode: Union[str, UpgradeMode]
        rollingUpgradePolicy: RollingUpgradePolicy


    class azure.mgmt.batch.types.UserAccount(TypedDict, total=False):
        key "elevationLevel": Union[str, ElevationLevel]
        key "linuxUserConfiguration": ForwardRef('LinuxUserConfiguration', module='types')
        key "name": Required[str]
        key "password": Required[str]
        key "windowsUserConfiguration": ForwardRef('WindowsUserConfiguration', module='types')
        elevationLevel: Union[str, ElevationLevel]
        linuxUserConfiguration: LinuxUserConfiguration
        name: str
        password: str
        windowsUserConfiguration: WindowsUserConfiguration


    class azure.mgmt.batch.types.UserAssignedIdentities(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.batch.types.UserIdentity(TypedDict, total=False):
        key "autoUser": ForwardRef('AutoUserSpecification', module='types')
        key "userName": str
        autoUser: AutoUserSpecification
        userName: str


    class azure.mgmt.batch.types.VMDiskSecurityProfile(TypedDict, total=False):
        key "diskEncryptionSet": ForwardRef('DiskEncryptionSetParameters', module='types')
        key "securityEncryptionType": Union[str, SecurityEncryptionTypes]
        diskEncryptionSet: DiskEncryptionSetParameters
        securityEncryptionType: Union[str, SecurityEncryptionTypes]


    class azure.mgmt.batch.types.VMExtension(TypedDict, total=False):
        key "autoUpgradeMinorVersion": bool
        key "enableAutomaticUpgrade": bool
        key "name": Required[str]
        key "protectedSettings": Any
        key "publisher": Required[str]
        key "settings": Any
        key "type": Required[str]
        key "typeHandlerVersion": str
        autoUpgradeMinorVersion: bool
        enableAutomaticUpgrade: bool
        name: str
        protectedSettings: Any
        provisionAfterExtensions: list[str]
        publisher: str
        settings: Any
        type: str
        typeHandlerVersion: str


    class azure.mgmt.batch.types.VirtualMachineConfiguration(TypedDict, total=False):
        key "containerConfiguration": ForwardRef('ContainerConfiguration', module='types')
        key "diskEncryptionConfiguration": ForwardRef('DiskEncryptionConfiguration', module='types')
        key "imageReference": Required[ImageReference]
        key "licenseType": str
        key "nodeAgentSkuId": Required[str]
        key "nodePlacementConfiguration": ForwardRef('NodePlacementConfiguration', module='types')
        key "osDisk": ForwardRef('OSDisk', module='types')
        key "securityProfile": ForwardRef('SecurityProfile', module='types')
        key "serviceArtifactReference": ForwardRef('ServiceArtifactReference', module='types')
        key "windowsConfiguration": ForwardRef('WindowsConfiguration', module='types')
        containerConfiguration: ContainerConfiguration
        dataDisks: list[DataDisk]
        diskEncryptionConfiguration: DiskEncryptionConfiguration
        extensions: list[VMExtension]
        imageReference: ImageReference
        licenseType: str
        nodeAgentSkuId: str
        nodePlacementConfiguration: NodePlacementConfiguration
        osDisk: OSDisk
        securityProfile: SecurityProfile
        serviceArtifactReference: ServiceArtifactReference
        windowsConfiguration: WindowsConfiguration


    class azure.mgmt.batch.types.WindowsConfiguration(TypedDict, total=False):
        key "enableAutomaticUpdates": bool
        enableAutomaticUpdates: bool


    class azure.mgmt.batch.types.WindowsUserConfiguration(TypedDict, total=False):
        key "loginMode": Union[str, LoginMode]
        loginMode: Union[str, LoginMode]


```