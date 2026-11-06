```py
namespace azure.mgmt.frontdoor

    class azure.mgmt.frontdoor.FrontDoorManagementClient: implements ContextManager 
        endpoints: EndpointsOperations
        experiments: ExperimentsOperations
        front_door_name_availability: FrontDoorNameAvailabilityOperations
        front_door_name_availability_with_subscription: FrontDoorNameAvailabilityWithSubscriptionOperations
        front_doors: FrontDoorsOperations
        frontend_endpoints: FrontendEndpointsOperations
        managed_rule_sets: ManagedRuleSetsOperations
        network_experiment_profiles: NetworkExperimentProfilesOperations
        policies: PoliciesOperations
        preconfigured_endpoints: PreconfiguredEndpointsOperations
        reports: ReportsOperations
        rules_engines: RulesEnginesOperations

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


namespace azure.mgmt.frontdoor.aio

    class azure.mgmt.frontdoor.aio.FrontDoorManagementClient: implements AsyncContextManager 
        endpoints: EndpointsOperations
        experiments: ExperimentsOperations
        front_door_name_availability: FrontDoorNameAvailabilityOperations
        front_door_name_availability_with_subscription: FrontDoorNameAvailabilityWithSubscriptionOperations
        front_doors: FrontDoorsOperations
        frontend_endpoints: FrontendEndpointsOperations
        managed_rule_sets: ManagedRuleSetsOperations
        network_experiment_profiles: NetworkExperimentProfilesOperations
        policies: PoliciesOperations
        preconfigured_endpoints: PreconfiguredEndpointsOperations
        reports: ReportsOperations
        rules_engines: RulesEnginesOperations

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


namespace azure.mgmt.frontdoor.aio.operations

    class azure.mgmt.frontdoor.aio.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_purge_content(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                content_file_paths: PurgeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_purge_content(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                content_file_paths: PurgeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_purge_content(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                content_file_paths: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.frontdoor.aio.operations.ExperimentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                parameters: Experiment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Experiment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                parameters: Experiment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Experiment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Experiment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                parameters: ExperimentUpdateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Experiment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                parameters: ExperimentUpdateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Experiment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Experiment]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> Experiment: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Experiment]: ...


    class azure.mgmt.frontdoor.aio.operations.FrontDoorNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check(
                self, 
                check_front_door_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check(
                self, 
                check_front_door_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check(
                self, 
                check_front_door_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...


    class azure.mgmt.frontdoor.aio.operations.FrontDoorNameAvailabilityWithSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check(
                self, 
                check_front_door_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check(
                self, 
                check_front_door_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check(
                self, 
                check_front_door_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...


    class azure.mgmt.frontdoor.aio.operations.FrontDoorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                front_door_parameters: FrontDoor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FrontDoor]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                front_door_parameters: FrontDoor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FrontDoor]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                front_door_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FrontDoor]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                **kwargs: Any
            ) -> FrontDoor: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[FrontDoor]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FrontDoor]: ...

        @overload
        async def validate_custom_domain(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                custom_domain_properties: ValidateCustomDomainInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...

        @overload
        async def validate_custom_domain(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                custom_domain_properties: ValidateCustomDomainInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...

        @overload
        async def validate_custom_domain(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                custom_domain_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...


    class azure.mgmt.frontdoor.aio.operations.FrontendEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_disable_https(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                frontend_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_enable_https(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                frontend_endpoint_name: str, 
                custom_https_configuration: CustomHttpsConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_enable_https(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                frontend_endpoint_name: str, 
                custom_https_configuration: CustomHttpsConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_enable_https(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                frontend_endpoint_name: str, 
                custom_https_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                frontend_endpoint_name: str, 
                **kwargs: Any
            ) -> FrontendEndpoint: ...

        @distributed_trace
        def list_by_front_door(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FrontendEndpoint]: ...


    class azure.mgmt.frontdoor.aio.operations.ManagedRuleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ManagedRuleSetDefinition]: ...


    class azure.mgmt.frontdoor.aio.operations.NetworkExperimentProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                profile_name: str, 
                resource_group_name: str, 
                parameters: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Profile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                profile_name: str, 
                resource_group_name: str, 
                parameters: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Profile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                profile_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Profile]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: ProfileUpdateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Profile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: ProfileUpdateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Profile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Profile]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Profile: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Profile]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Profile]: ...


    class azure.mgmt.frontdoor.aio.operations.PoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: WebApplicationFirewallPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebApplicationFirewallPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: WebApplicationFirewallPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebApplicationFirewallPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebApplicationFirewallPolicy]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebApplicationFirewallPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebApplicationFirewallPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebApplicationFirewallPolicy]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> WebApplicationFirewallPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WebApplicationFirewallPolicy]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[WebApplicationFirewallPolicy]: ...


    class azure.mgmt.frontdoor.aio.operations.PreconfiguredEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PreconfiguredEndpoint]: ...


    class azure.mgmt.frontdoor.aio.operations.ReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_latency_scorecards(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                *, 
                aggregation_interval: Union[str, LatencyScorecardAggregationInterval], 
                country: Optional[str] = ..., 
                end_date_time_utc: Optional[str] = ..., 
                **kwargs: Any
            ) -> LatencyScorecard: ...

        @distributed_trace_async
        async def get_timeseries(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                *, 
                aggregation_interval: Union[str, TimeseriesAggregationInterval], 
                country: Optional[str] = ..., 
                end_date_time_utc: datetime, 
                endpoint: Optional[str] = ..., 
                start_date_time_utc: datetime, 
                timeseries_type: Union[str, TimeseriesType], 
                **kwargs: Any
            ) -> Timeseries: ...


    class azure.mgmt.frontdoor.aio.operations.RulesEnginesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                rules_engine_name: str, 
                rules_engine_parameters: RulesEngine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RulesEngine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                rules_engine_name: str, 
                rules_engine_parameters: RulesEngine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RulesEngine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                rules_engine_name: str, 
                rules_engine_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RulesEngine]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                rules_engine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                rules_engine_name: str, 
                **kwargs: Any
            ) -> RulesEngine: ...

        @distributed_trace
        def list_by_front_door(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RulesEngine]: ...


namespace azure.mgmt.frontdoor.models

    class azure.mgmt.frontdoor.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        ANOMALY_SCORING = "AnomalyScoring"
        BLOCK = "Block"
        CAPTCHA = "CAPTCHA"
        JS_CHALLENGE = "JSChallenge"
        LOG = "Log"
        REDIRECT = "Redirect"


    class azure.mgmt.frontdoor.models.AggregationInterval(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        HOURLY = "Hourly"


    class azure.mgmt.frontdoor.models.Availability(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.frontdoor.models.Backend(_Model):
        address: Optional[str]
        backend_host_header: Optional[str]
        enabled_state: Optional[Union[str, BackendEnabledState]]
        http_port: Optional[int]
        https_port: Optional[int]
        priority: Optional[int]
        private_endpoint_status: Optional[Union[str, PrivateEndpointStatus]]
        private_link_alias: Optional[str]
        private_link_approval_message: Optional[str]
        private_link_location: Optional[str]
        private_link_resource_id: Optional[str]
        weight: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                backend_host_header: Optional[str] = ..., 
                enabled_state: Optional[Union[str, BackendEnabledState]] = ..., 
                http_port: Optional[int] = ..., 
                https_port: Optional[int] = ..., 
                priority: Optional[int] = ..., 
                private_link_alias: Optional[str] = ..., 
                private_link_approval_message: Optional[str] = ..., 
                private_link_location: Optional[str] = ..., 
                private_link_resource_id: Optional[str] = ..., 
                weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.BackendEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.BackendPool(SubResource):
        id: str
        name: Optional[str]
        properties: Optional[BackendPoolProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[BackendPoolProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.BackendPoolProperties(BackendPoolUpdateParameters):
        backends: list[Backend]
        health_probe_settings: SubResource
        load_balancing_settings: SubResource
        resource_state: Optional[Union[str, FrontDoorResourceState]]

        @overload
        def __init__(
                self, 
                *, 
                backends: Optional[list[Backend]] = ..., 
                health_probe_settings: Optional[SubResource] = ..., 
                load_balancing_settings: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.BackendPoolUpdateParameters(_Model):
        backends: Optional[list[Backend]]
        health_probe_settings: Optional[SubResource]
        load_balancing_settings: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                backends: Optional[list[Backend]] = ..., 
                health_probe_settings: Optional[SubResource] = ..., 
                load_balancing_settings: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.BackendPoolsSettings(_Model):
        enforce_certificate_name_check: Optional[Union[str, EnforceCertificateNameCheckEnabledState]]
        send_recv_timeout_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enforce_certificate_name_check: Optional[Union[str, EnforceCertificateNameCheckEnabledState]] = ..., 
                send_recv_timeout_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.BasicResource(_Model):
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]


    class azure.mgmt.frontdoor.models.BasicResourceWithSettableIDName(_Model):
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.CacheConfiguration(_Model):
        cache_duration: Optional[timedelta]
        dynamic_compression: Optional[Union[str, DynamicCompressionEnabled]]
        query_parameter_strip_directive: Optional[Union[str, FrontDoorQuery]]
        query_parameters: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cache_duration: Optional[timedelta] = ..., 
                dynamic_compression: Optional[Union[str, DynamicCompressionEnabled]] = ..., 
                query_parameter_strip_directive: Optional[Union[str, FrontDoorQuery]] = ..., 
                query_parameters: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.CheckNameAvailabilityInput(_Model):
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


    class azure.mgmt.frontdoor.models.CheckNameAvailabilityOutput(_Model):
        message: Optional[str]
        name_availability: Optional[Union[str, Availability]]
        reason: Optional[str]


    class azure.mgmt.frontdoor.models.CustomHttpsConfiguration(_Model):
        certificate_source: Union[str, FrontDoorCertificateSource]
        front_door_certificate_source_parameters: Optional[FrontDoorCertificateSourceParameters]
        key_vault_certificate_source_parameters: Optional[KeyVaultCertificateSourceParameters]
        minimum_tls_version: Union[str, MinimumTLSVersion]
        protocol_type: Union[str, FrontDoorTlsProtocolType]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                certificate_source: Union[str, FrontDoorCertificateSource], 
                front_door_certificate_source_parameters: Optional[FrontDoorCertificateSourceParameters] = ..., 
                key_vault_certificate_source_parameters: Optional[KeyVaultCertificateSourceParameters] = ..., 
                minimum_tls_version: Union[str, MinimumTLSVersion], 
                protocol_type: Union[str, FrontDoorTlsProtocolType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.CustomHttpsProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        DISABLING = "Disabling"
        ENABLED = "Enabled"
        ENABLING = "Enabling"
        FAILED = "Failed"


    class azure.mgmt.frontdoor.models.CustomHttpsProvisioningSubstate(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CERTIFICATE_DELETED = "CertificateDeleted"
        CERTIFICATE_DEPLOYED = "CertificateDeployed"
        DELETING_CERTIFICATE = "DeletingCertificate"
        DEPLOYING_CERTIFICATE = "DeployingCertificate"
        DOMAIN_CONTROL_VALIDATION_REQUEST_APPROVED = "DomainControlValidationRequestApproved"
        DOMAIN_CONTROL_VALIDATION_REQUEST_REJECTED = "DomainControlValidationRequestRejected"
        DOMAIN_CONTROL_VALIDATION_REQUEST_TIMED_OUT = "DomainControlValidationRequestTimedOut"
        ISSUING_CERTIFICATE = "IssuingCertificate"
        PENDING_DOMAIN_CONTROL_VALIDATION_R_EQUEST_APPROVAL = "PendingDomainControlValidationREquestApproval"
        SUBMITTING_DOMAIN_CONTROL_VALIDATION_REQUEST = "SubmittingDomainControlValidationRequest"


    class azure.mgmt.frontdoor.models.CustomRule(_Model):
        action: Union[str, ActionType]
        enabled_state: Optional[Union[str, CustomRuleEnabledState]]
        group_by: Optional[list[GroupByVariable]]
        match_conditions: list[MatchCondition]
        name: Optional[str]
        priority: int
        rate_limit_duration_in_minutes: Optional[int]
        rate_limit_threshold: Optional[int]
        rule_type: Union[str, RuleType]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, ActionType], 
                enabled_state: Optional[Union[str, CustomRuleEnabledState]] = ..., 
                group_by: Optional[list[GroupByVariable]] = ..., 
                match_conditions: list[MatchCondition], 
                name: Optional[str] = ..., 
                priority: int, 
                rate_limit_duration_in_minutes: Optional[int] = ..., 
                rate_limit_threshold: Optional[int] = ..., 
                rule_type: Union[str, RuleType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.CustomRuleEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.CustomRuleList(_Model):
        rules: Optional[list[CustomRule]]

        @overload
        def __init__(
                self, 
                *, 
                rules: Optional[list[CustomRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.DefaultErrorResponse(_Model):
        error: Optional[DefaultErrorResponseError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[DefaultErrorResponseError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.DefaultErrorResponseError(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.frontdoor.models.DynamicCompressionEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.Endpoint(_Model):
        endpoint: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.EndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFD = "AFD"
        ATM = "ATM"
        AZURE_REGION = "AzureRegion"
        CDN = "CDN"


    class azure.mgmt.frontdoor.models.EnforceCertificateNameCheckEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.ErrorResponse(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.frontdoor.models.ExceptionMatchVariable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REQUEST_HEADER_NAMES = "RequestHeaderNames"
        REQUEST_URI = "RequestUri"
        SOCKET_ADDR = "SocketAddr"


    class azure.mgmt.frontdoor.models.ExceptionSelectorMatchOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "Equals"


    class azure.mgmt.frontdoor.models.ExceptionValueMatchOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUALS = "Equals"
        EQUALS_ANY = "EqualsAny"
        IP_MATCH = "IPMatch"
        STARTS_WITH = "StartsWith"


    class azure.mgmt.frontdoor.models.Experiment(Resource):
        id: str
        location: str
        name: str
        properties: Optional[ExperimentProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ExperimentProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.ExperimentProperties(_Model):
        description: Optional[str]
        enabled_state: Optional[Union[str, State]]
        endpoint_a: Optional[Endpoint]
        endpoint_b: Optional[Endpoint]
        resource_state: Optional[Union[str, NetworkExperimentResourceState]]
        script_file_uri: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                enabled_state: Optional[Union[str, State]] = ..., 
                endpoint_a: Optional[Endpoint] = ..., 
                endpoint_b: Optional[Endpoint] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ExperimentUpdateModel(_Model):
        properties: Optional[ExperimentUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExperimentUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.ExperimentUpdateProperties(_Model):
        description: Optional[str]
        enabled_state: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                enabled_state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ForwardingConfiguration(RouteConfiguration, discriminator='#Microsoft.Azure.FrontDoor.Models.FrontdoorForwardingConfiguration'):
        backend_pool: Optional[SubResource]
        cache_configuration: Optional[CacheConfiguration]
        custom_forwarding_path: Optional[str]
        forwarding_protocol: Optional[Union[str, FrontDoorForwardingProtocol]]
        odata_type: Literal["#FrontdoorForwardingConfiguration"]

        @overload
        def __init__(
                self, 
                *, 
                backend_pool: Optional[SubResource] = ..., 
                cache_configuration: Optional[CacheConfiguration] = ..., 
                custom_forwarding_path: Optional[str] = ..., 
                forwarding_protocol: Optional[Union[str, FrontDoorForwardingProtocol]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.FrontDoor(Resource):
        id: str
        location: str
        name: str
        properties: Optional[FrontDoorProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[FrontDoorProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.FrontDoorCertificateSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT = "AzureKeyVault"
        FRONT_DOOR = "FrontDoor"


    class azure.mgmt.frontdoor.models.FrontDoorCertificateSourceParameters(_Model):
        certificate_type: Optional[Union[str, FrontDoorCertificateType]]

        @overload
        def __init__(
                self, 
                *, 
                certificate_type: Optional[Union[str, FrontDoorCertificateType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.FrontDoorCertificateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEDICATED = "Dedicated"


    class azure.mgmt.frontdoor.models.FrontDoorEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.FrontDoorForwardingProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTPS_ONLY = "HttpsOnly"
        HTTP_ONLY = "HttpOnly"
        MATCH_REQUEST = "MatchRequest"


    class azure.mgmt.frontdoor.models.FrontDoorHealthProbeMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GET = "GET"
        HEAD = "HEAD"


    class azure.mgmt.frontdoor.models.FrontDoorProperties(FrontDoorUpdateParameters):
        backend_pools: list[BackendPool]
        backend_pools_settings: BackendPoolsSettings
        cname: Optional[str]
        enabled_state: Union[str, FrontDoorEnabledState]
        extended_properties: Optional[dict[str, str]]
        friendly_name: str
        frontdoor_id: Optional[str]
        frontend_endpoints: list[FrontendEndpoint]
        health_probe_settings: list[HealthProbeSettingsModel]
        load_balancing_settings: list[LoadBalancingSettingsModel]
        provisioning_state: Optional[str]
        resource_state: Optional[Union[str, FrontDoorResourceState]]
        routing_rules: list[RoutingRule]
        rules_engines: Optional[list[RulesEngine]]

        @overload
        def __init__(
                self, 
                *, 
                backend_pools: Optional[list[BackendPool]] = ..., 
                backend_pools_settings: Optional[BackendPoolsSettings] = ..., 
                enabled_state: Optional[Union[str, FrontDoorEnabledState]] = ..., 
                friendly_name: Optional[str] = ..., 
                frontend_endpoints: Optional[list[FrontendEndpoint]] = ..., 
                health_probe_settings: Optional[list[HealthProbeSettingsModel]] = ..., 
                load_balancing_settings: Optional[list[LoadBalancingSettingsModel]] = ..., 
                routing_rules: Optional[list[RoutingRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.FrontDoorProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "Http"
        HTTPS = "Https"


    class azure.mgmt.frontdoor.models.FrontDoorQuery(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STRIP_ALL = "StripAll"
        STRIP_ALL_EXCEPT = "StripAllExcept"
        STRIP_NONE = "StripNone"
        STRIP_ONLY = "StripOnly"


    class azure.mgmt.frontdoor.models.FrontDoorRedirectProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTPS_ONLY = "HttpsOnly"
        HTTP_ONLY = "HttpOnly"
        MATCH_REQUEST = "MatchRequest"


    class azure.mgmt.frontdoor.models.FrontDoorRedirectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOUND = "Found"
        MOVED = "Moved"
        PERMANENT_REDIRECT = "PermanentRedirect"
        TEMPORARY_REDIRECT = "TemporaryRedirect"


    class azure.mgmt.frontdoor.models.FrontDoorResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        DISABLED = "Disabled"
        DISABLING = "Disabling"
        ENABLED = "Enabled"
        ENABLING = "Enabling"
        MIGRATED = "Migrated"
        MIGRATING = "Migrating"


    class azure.mgmt.frontdoor.models.FrontDoorTlsProtocolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVER_NAME_INDICATION = "ServerNameIndication"


    class azure.mgmt.frontdoor.models.FrontDoorUpdateParameters(_Model):
        backend_pools: Optional[list[BackendPool]]
        backend_pools_settings: Optional[BackendPoolsSettings]
        enabled_state: Optional[Union[str, FrontDoorEnabledState]]
        friendly_name: Optional[str]
        frontend_endpoints: Optional[list[FrontendEndpoint]]
        health_probe_settings: Optional[list[HealthProbeSettingsModel]]
        load_balancing_settings: Optional[list[LoadBalancingSettingsModel]]
        routing_rules: Optional[list[RoutingRule]]

        @overload
        def __init__(
                self, 
                *, 
                backend_pools: Optional[list[BackendPool]] = ..., 
                backend_pools_settings: Optional[BackendPoolsSettings] = ..., 
                enabled_state: Optional[Union[str, FrontDoorEnabledState]] = ..., 
                friendly_name: Optional[str] = ..., 
                frontend_endpoints: Optional[list[FrontendEndpoint]] = ..., 
                health_probe_settings: Optional[list[HealthProbeSettingsModel]] = ..., 
                load_balancing_settings: Optional[list[LoadBalancingSettingsModel]] = ..., 
                routing_rules: Optional[list[RoutingRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.FrontendEndpoint(BasicResourceWithSettableIDName):
        id: str
        name: str
        properties: Optional[FrontendEndpointProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[FrontendEndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.FrontendEndpointLink(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.FrontendEndpointProperties(FrontendEndpointUpdateParameters):
        custom_https_configuration: Optional[CustomHttpsConfiguration]
        custom_https_provisioning_state: Optional[Union[str, CustomHttpsProvisioningState]]
        custom_https_provisioning_substate: Optional[Union[str, CustomHttpsProvisioningSubstate]]
        host_name: str
        resource_state: Optional[Union[str, FrontDoorResourceState]]
        session_affinity_enabled_state: Union[str, SessionAffinityEnabledState]
        session_affinity_ttl_seconds: int
        web_application_firewall_policy_link: FrontendEndpointUpdateParametersWebApplicationFirewallPolicyLink

        @overload
        def __init__(
                self, 
                *, 
                host_name: Optional[str] = ..., 
                session_affinity_enabled_state: Optional[Union[str, SessionAffinityEnabledState]] = ..., 
                session_affinity_ttl_seconds: Optional[int] = ..., 
                web_application_firewall_policy_link: Optional[FrontendEndpointUpdateParametersWebApplicationFirewallPolicyLink] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.FrontendEndpointUpdateParameters(_Model):
        host_name: Optional[str]
        session_affinity_enabled_state: Optional[Union[str, SessionAffinityEnabledState]]
        session_affinity_ttl_seconds: Optional[int]
        web_application_firewall_policy_link: Optional[FrontendEndpointUpdateParametersWebApplicationFirewallPolicyLink]

        @overload
        def __init__(
                self, 
                *, 
                host_name: Optional[str] = ..., 
                session_affinity_enabled_state: Optional[Union[str, SessionAffinityEnabledState]] = ..., 
                session_affinity_ttl_seconds: Optional[int] = ..., 
                web_application_firewall_policy_link: Optional[FrontendEndpointUpdateParametersWebApplicationFirewallPolicyLink] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.FrontendEndpointUpdateParametersWebApplicationFirewallPolicyLink(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.GroupByVariable(_Model):
        variable_name: Union[str, VariableName]

        @overload
        def __init__(
                self, 
                *, 
                variable_name: Union[str, VariableName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.HeaderAction(_Model):
        header_action_type: Union[str, HeaderActionType]
        header_name: str
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                header_action_type: Union[str, HeaderActionType], 
                header_name: str, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.HeaderActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPEND = "Append"
        DELETE = "Delete"
        OVERWRITE = "Overwrite"


    class azure.mgmt.frontdoor.models.HealthProbeEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.HealthProbeSettingsModel(SubResource):
        id: str
        name: Optional[str]
        properties: Optional[HealthProbeSettingsProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[HealthProbeSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.HealthProbeSettingsProperties(HealthProbeSettingsUpdateParameters):
        enabled_state: Union[str, HealthProbeEnabled]
        health_probe_method: Union[str, FrontDoorHealthProbeMethod]
        interval_in_seconds: int
        path: str
        protocol: Union[str, FrontDoorProtocol]
        resource_state: Optional[Union[str, FrontDoorResourceState]]

        @overload
        def __init__(
                self, 
                *, 
                enabled_state: Optional[Union[str, HealthProbeEnabled]] = ..., 
                health_probe_method: Optional[Union[str, FrontDoorHealthProbeMethod]] = ..., 
                interval_in_seconds: Optional[int] = ..., 
                path: Optional[str] = ..., 
                protocol: Optional[Union[str, FrontDoorProtocol]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.HealthProbeSettingsUpdateParameters(_Model):
        enabled_state: Optional[Union[str, HealthProbeEnabled]]
        health_probe_method: Optional[Union[str, FrontDoorHealthProbeMethod]]
        interval_in_seconds: Optional[int]
        path: Optional[str]
        protocol: Optional[Union[str, FrontDoorProtocol]]

        @overload
        def __init__(
                self, 
                *, 
                enabled_state: Optional[Union[str, HealthProbeEnabled]] = ..., 
                health_probe_method: Optional[Union[str, FrontDoorHealthProbeMethod]] = ..., 
                interval_in_seconds: Optional[int] = ..., 
                path: Optional[str] = ..., 
                protocol: Optional[Union[str, FrontDoorProtocol]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.KeyVaultCertificateSourceParameters(_Model):
        secret_name: Optional[str]
        secret_version: Optional[str]
        vault: Optional[KeyVaultCertificateSourceParametersVault]

        @overload
        def __init__(
                self, 
                *, 
                secret_name: Optional[str] = ..., 
                secret_version: Optional[str] = ..., 
                vault: Optional[KeyVaultCertificateSourceParametersVault] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.KeyVaultCertificateSourceParametersVault(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.LatencyMetric(_Model):
        a_c_lower95_ci: Optional[float]
        a_h_upper95_ci: Optional[float]
        a_value: Optional[float]
        b_c_lower95_ci: Optional[float]
        b_upper95_ci: Optional[float]
        b_value: Optional[float]
        delta: Optional[float]
        delta_percent: Optional[float]
        end_date_time_utc: Optional[str]
        name: Optional[str]


    class azure.mgmt.frontdoor.models.LatencyScorecard(Resource):
        id: str
        location: str
        name: str
        properties: Optional[LatencyScorecardProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[LatencyScorecardProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.LatencyScorecardAggregationInterval(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        MONTHLY = "Monthly"
        WEEKLY = "Weekly"


    class azure.mgmt.frontdoor.models.LatencyScorecardProperties(_Model):
        country: Optional[str]
        description: Optional[str]
        end_date_time_utc: Optional[datetime]
        endpoint_a: Optional[str]
        endpoint_b: Optional[str]
        id: Optional[str]
        latency_metrics: Optional[list[LatencyMetric]]
        name: Optional[str]
        start_date_time_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                latency_metrics: Optional[list[LatencyMetric]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.LoadBalancingSettingsModel(SubResource):
        id: str
        name: Optional[str]
        properties: Optional[LoadBalancingSettingsProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[LoadBalancingSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.LoadBalancingSettingsProperties(LoadBalancingSettingsUpdateParameters):
        additional_latency_milliseconds: int
        resource_state: Optional[Union[str, FrontDoorResourceState]]
        sample_size: int
        successful_samples_required: int

        @overload
        def __init__(
                self, 
                *, 
                additional_latency_milliseconds: Optional[int] = ..., 
                sample_size: Optional[int] = ..., 
                successful_samples_required: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.LoadBalancingSettingsUpdateParameters(_Model):
        additional_latency_milliseconds: Optional[int]
        sample_size: Optional[int]
        successful_samples_required: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                additional_latency_milliseconds: Optional[int] = ..., 
                sample_size: Optional[int] = ..., 
                successful_samples_required: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ManagedRuleDefinition(_Model):
        default_action: Optional[Union[str, ActionType]]
        default_sensitivity: Optional[Union[str, SensitivityType]]
        default_state: Optional[Union[str, ManagedRuleEnabledState]]
        description: Optional[str]
        paranoia_level: Optional[Union[str, ParanoiaLevel]]
        rule_id: Optional[str]


    class azure.mgmt.frontdoor.models.ManagedRuleEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.ManagedRuleExclusion(_Model):
        match_variable: Union[str, ManagedRuleExclusionMatchVariable]
        selector: str
        selector_match_operator: Union[str, ManagedRuleExclusionSelectorMatchOperator]

        @overload
        def __init__(
                self, 
                *, 
                match_variable: Union[str, ManagedRuleExclusionMatchVariable], 
                selector: str, 
                selector_match_operator: Union[str, ManagedRuleExclusionSelectorMatchOperator]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ManagedRuleExclusionMatchVariable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QUERY_STRING_ARG_NAMES = "QueryStringArgNames"
        REQUEST_BODY_JSON_ARG_NAMES = "RequestBodyJsonArgNames"
        REQUEST_BODY_POST_ARG_NAMES = "RequestBodyPostArgNames"
        REQUEST_COOKIE_NAMES = "RequestCookieNames"
        REQUEST_HEADER_NAMES = "RequestHeaderNames"


    class azure.mgmt.frontdoor.models.ManagedRuleExclusionSelectorMatchOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUALS = "Equals"
        EQUALS_ANY = "EqualsAny"
        STARTS_WITH = "StartsWith"


    class azure.mgmt.frontdoor.models.ManagedRuleGroupDefinition(_Model):
        description: Optional[str]
        rule_group_name: Optional[str]
        rules: Optional[list[ManagedRuleDefinition]]


    class azure.mgmt.frontdoor.models.ManagedRuleGroupOverride(_Model):
        exclusions: Optional[list[ManagedRuleExclusion]]
        rule_group_name: str
        rules: Optional[list[ManagedRuleOverride]]

        @overload
        def __init__(
                self, 
                *, 
                exclusions: Optional[list[ManagedRuleExclusion]] = ..., 
                rule_group_name: str, 
                rules: Optional[list[ManagedRuleOverride]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ManagedRuleOverride(_Model):
        action: Optional[Union[str, ActionType]]
        enabled_state: Optional[Union[str, ManagedRuleEnabledState]]
        exclusions: Optional[list[ManagedRuleExclusion]]
        rule_id: str
        sensitivity: Optional[Union[str, SensitivityType]]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, ActionType]] = ..., 
                enabled_state: Optional[Union[str, ManagedRuleEnabledState]] = ..., 
                exclusions: Optional[list[ManagedRuleExclusion]] = ..., 
                rule_id: str, 
                sensitivity: Optional[Union[str, SensitivityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ManagedRuleSet(_Model):
        exclusions: Optional[list[ManagedRuleExclusion]]
        rule_group_overrides: Optional[list[ManagedRuleGroupOverride]]
        rule_set_action: Optional[Union[str, ManagedRuleSetActionType]]
        rule_set_type: str
        rule_set_version: str

        @overload
        def __init__(
                self, 
                *, 
                exclusions: Optional[list[ManagedRuleExclusion]] = ..., 
                rule_group_overrides: Optional[list[ManagedRuleGroupOverride]] = ..., 
                rule_set_action: Optional[Union[str, ManagedRuleSetActionType]] = ..., 
                rule_set_type: str, 
                rule_set_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ManagedRuleSetActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCK = "Block"
        LOG = "Log"
        REDIRECT = "Redirect"


    class azure.mgmt.frontdoor.models.ManagedRuleSetDefinition(Resource):
        id: str
        location: str
        name: str
        properties: Optional[ManagedRuleSetDefinitionProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ManagedRuleSetDefinitionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.ManagedRuleSetDefinitionProperties(_Model):
        display_name: Optional[str]
        provisioning_state: Optional[str]
        rule_groups: Optional[list[ManagedRuleGroupDefinition]]
        rule_set_id: Optional[str]
        rule_set_type: Optional[str]
        rule_set_version: Optional[str]
        status: Optional[Union[str, ManagedRuleSetStatus]]


    class azure.mgmt.frontdoor.models.ManagedRuleSetException(_Model):
        match_values: list[str]
        match_variable: Union[str, ExceptionMatchVariable]
        scopes: list[ManagedRuleSetScope]
        selector: Optional[str]
        selector_match_operator: Optional[Union[str, ExceptionSelectorMatchOperator]]
        value_match_operator: Union[str, ExceptionValueMatchOperator]

        @overload
        def __init__(
                self, 
                *, 
                match_values: list[str], 
                match_variable: Union[str, ExceptionMatchVariable], 
                scopes: list[ManagedRuleSetScope], 
                selector: Optional[str] = ..., 
                selector_match_operator: Optional[Union[str, ExceptionSelectorMatchOperator]] = ..., 
                value_match_operator: Union[str, ExceptionValueMatchOperator]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ManagedRuleSetExceptionList(_Model):
        exceptions: Optional[list[ManagedRuleSetException]]

        @overload
        def __init__(
                self, 
                *, 
                exceptions: Optional[list[ManagedRuleSetException]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ManagedRuleSetList(_Model):
        exceptions_list: Optional[ManagedRuleSetExceptionList]
        managed_rule_sets: Optional[list[ManagedRuleSet]]

        @overload
        def __init__(
                self, 
                *, 
                exceptions_list: Optional[ManagedRuleSetExceptionList] = ..., 
                managed_rule_sets: Optional[list[ManagedRuleSet]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ManagedRuleSetScope(_Model):
        rule_group_scopes: Optional[list[RuleGroupScope]]
        rule_set_type: str
        rule_set_version: str

        @overload
        def __init__(
                self, 
                *, 
                rule_group_scopes: Optional[list[RuleGroupScope]] = ..., 
                rule_set_type: str, 
                rule_set_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ManagedRuleSetStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPRECATED = "Deprecated"
        GA = "GA"
        PREVIEW = "Preview"
        SUPPORTED = "Supported"


    class azure.mgmt.frontdoor.models.MatchCondition(_Model):
        match_value: list[str]
        match_variable: Union[str, MatchVariable]
        negate_condition: Optional[bool]
        operator: Union[str, Operator]
        selector: Optional[str]
        transforms: Optional[list[Union[str, TransformType]]]

        @overload
        def __init__(
                self, 
                *, 
                match_value: list[str], 
                match_variable: Union[str, MatchVariable], 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, Operator], 
                selector: Optional[str] = ..., 
                transforms: Optional[list[Union[str, TransformType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.MatchProcessingBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUE_ENUM = "Continue"
        STOP = "Stop"


    class azure.mgmt.frontdoor.models.MatchVariable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COOKIES = "Cookies"
        JA4 = "JA4"
        POST_ARGS = "PostArgs"
        QUERY_STRING = "QueryString"
        REMOTE_ADDR = "RemoteAddr"
        REQUEST_BODY = "RequestBody"
        REQUEST_HEADER = "RequestHeader"
        REQUEST_METHOD = "RequestMethod"
        REQUEST_URI = "RequestUri"
        SOCKET_ADDR = "SocketAddr"


    class azure.mgmt.frontdoor.models.MinimumTLSVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE0 = "1.0"
        ONE2 = "1.2"


    class azure.mgmt.frontdoor.models.NetworkExperimentResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        DISABLED = "Disabled"
        DISABLING = "Disabling"
        ENABLED = "Enabled"
        ENABLING = "Enabling"


    class azure.mgmt.frontdoor.models.Operator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        ASN_MATCH = "AsnMatch"
        BEGINS_WITH = "BeginsWith"
        CLIENT_FINGERPRINT = "ClientFingerprint"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GEO_MATCH = "GeoMatch"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        IP_MATCH = "IPMatch"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"
        SERVICE_TAG_MATCH = "ServiceTagMatch"


    class azure.mgmt.frontdoor.models.ParanoiaLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PL1 = "PL1"
        PL2 = "PL2"
        PL3 = "PL3"
        PL4 = "PL4"


    class azure.mgmt.frontdoor.models.PolicyEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.PolicyMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DETECTION = "Detection"
        PREVENTION = "Prevention"


    class azure.mgmt.frontdoor.models.PolicyRequestBodyCheck(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.PolicyResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        DISABLED = "Disabled"
        DISABLING = "Disabling"
        ENABLED = "Enabled"
        ENABLING = "Enabling"


    class azure.mgmt.frontdoor.models.PolicySettings(_Model):
        captcha_expiration_in_minutes: Optional[int]
        custom_block_response_body: Optional[str]
        custom_block_response_status_code: Optional[int]
        enabled_state: Optional[Union[str, PolicyEnabledState]]
        javascript_challenge_expiration_in_minutes: Optional[int]
        log_scrubbing: Optional[PolicySettingsLogScrubbing]
        mode: Optional[Union[str, PolicyMode]]
        redirect_url: Optional[str]
        request_body_check: Optional[Union[str, PolicyRequestBodyCheck]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                captcha_expiration_in_minutes: Optional[int] = ..., 
                custom_block_response_body: Optional[str] = ..., 
                custom_block_response_status_code: Optional[int] = ..., 
                enabled_state: Optional[Union[str, PolicyEnabledState]] = ..., 
                javascript_challenge_expiration_in_minutes: Optional[int] = ..., 
                log_scrubbing: Optional[PolicySettingsLogScrubbing] = ..., 
                mode: Optional[Union[str, PolicyMode]] = ..., 
                redirect_url: Optional[str] = ..., 
                request_body_check: Optional[Union[str, PolicyRequestBodyCheck]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.PolicySettingsLogScrubbing(_Model):
        scrubbing_rules: Optional[list[WebApplicationFirewallScrubbingRules]]
        state: Optional[Union[str, WebApplicationFirewallScrubbingState]]

        @overload
        def __init__(
                self, 
                *, 
                scrubbing_rules: Optional[list[WebApplicationFirewallScrubbingRules]] = ..., 
                state: Optional[Union[str, WebApplicationFirewallScrubbingState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.PreconfiguredEndpoint(ResourcewithSettableName):
        id: str
        location: str
        name: str
        properties: Optional[PreconfiguredEndpointProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[PreconfiguredEndpointProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.PreconfiguredEndpointProperties(_Model):
        backend: Optional[str]
        description: Optional[str]
        endpoint: Optional[str]
        endpoint_type: Optional[Union[str, EndpointType]]

        @overload
        def __init__(
                self, 
                *, 
                backend: Optional[str] = ..., 
                description: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                endpoint_type: Optional[Union[str, EndpointType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.PrivateEndpointStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"
        TIMEOUT = "Timeout"


    class azure.mgmt.frontdoor.models.Profile(ResourcewithSettableName):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[ProfileProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ProfileProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.ProfileProperties(_Model):
        enabled_state: Optional[Union[str, State]]
        resource_state: Optional[Union[str, NetworkExperimentResourceState]]

        @overload
        def __init__(
                self, 
                *, 
                enabled_state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ProfileUpdateModel(_Model):
        properties: Optional[ProfileUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProfileUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.ProfileUpdateProperties(_Model):
        enabled_state: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                enabled_state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.PurgeParameters(_Model):
        content_paths: list[str]

        @overload
        def __init__(
                self, 
                *, 
                content_paths: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RedirectConfiguration(RouteConfiguration, discriminator='#Microsoft.Azure.FrontDoor.Models.FrontdoorRedirectConfiguration'):
        custom_fragment: Optional[str]
        custom_host: Optional[str]
        custom_path: Optional[str]
        custom_query_string: Optional[str]
        odata_type: Literal["#FrontdoorRedirectConfiguration"]
        redirect_protocol: Optional[Union[str, FrontDoorRedirectProtocol]]
        redirect_type: Optional[Union[str, FrontDoorRedirectType]]

        @overload
        def __init__(
                self, 
                *, 
                custom_fragment: Optional[str] = ..., 
                custom_host: Optional[str] = ..., 
                custom_path: Optional[str] = ..., 
                custom_query_string: Optional[str] = ..., 
                redirect_protocol: Optional[Union[str, FrontDoorRedirectProtocol]] = ..., 
                redirect_type: Optional[Union[str, FrontDoorRedirectType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.Resource(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_NETWORK_FRONT_DOORS = "Microsoft.Network/frontDoors"
        MICROSOFT_NETWORK_FRONT_DOORS_FRONTEND_ENDPOINTS = "Microsoft.Network/frontDoors/frontendEndpoints"


    class azure.mgmt.frontdoor.models.ResourcewithSettableName(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RouteConfiguration(_Model):
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RoutingRule(SubResource):
        id: str
        name: Optional[str]
        properties: Optional[RoutingRuleProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[RoutingRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.RoutingRuleEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.RoutingRuleLink(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RoutingRuleProperties(RoutingRuleUpdateParameters):
        accepted_protocols: Union[list[str, FrontDoorProtocol]]
        enabled_state: Union[str, RoutingRuleEnabledState]
        frontend_endpoints: list[SubResource]
        patterns_to_match: list[str]
        resource_state: Optional[Union[str, FrontDoorResourceState]]
        route_configuration: RouteConfiguration
        rules_engine: SubResource
        web_application_firewall_policy_link: RoutingRuleUpdateParametersWebApplicationFirewallPolicyLink

        @overload
        def __init__(
                self, 
                *, 
                accepted_protocols: Optional[list[Union[str, FrontDoorProtocol]]] = ..., 
                enabled_state: Optional[Union[str, RoutingRuleEnabledState]] = ..., 
                frontend_endpoints: Optional[list[SubResource]] = ..., 
                patterns_to_match: Optional[list[str]] = ..., 
                route_configuration: Optional[RouteConfiguration] = ..., 
                rules_engine: Optional[SubResource] = ..., 
                web_application_firewall_policy_link: Optional[RoutingRuleUpdateParametersWebApplicationFirewallPolicyLink] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RoutingRuleUpdateParameters(_Model):
        accepted_protocols: Optional[list[Union[str, FrontDoorProtocol]]]
        enabled_state: Optional[Union[str, RoutingRuleEnabledState]]
        frontend_endpoints: Optional[list[SubResource]]
        patterns_to_match: Optional[list[str]]
        route_configuration: Optional[RouteConfiguration]
        rules_engine: Optional[SubResource]
        web_application_firewall_policy_link: Optional[RoutingRuleUpdateParametersWebApplicationFirewallPolicyLink]

        @overload
        def __init__(
                self, 
                *, 
                accepted_protocols: Optional[list[Union[str, FrontDoorProtocol]]] = ..., 
                enabled_state: Optional[Union[str, RoutingRuleEnabledState]] = ..., 
                frontend_endpoints: Optional[list[SubResource]] = ..., 
                patterns_to_match: Optional[list[str]] = ..., 
                route_configuration: Optional[RouteConfiguration] = ..., 
                rules_engine: Optional[SubResource] = ..., 
                web_application_firewall_policy_link: Optional[RoutingRuleUpdateParametersWebApplicationFirewallPolicyLink] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RoutingRuleUpdateParametersWebApplicationFirewallPolicyLink(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RuleGroupScope(_Model):
        rule_group_name: str
        rule_scopes: Optional[list[RuleScope]]

        @overload
        def __init__(
                self, 
                *, 
                rule_group_name: str, 
                rule_scopes: Optional[list[RuleScope]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RuleScope(_Model):
        rule_id: str

        @overload
        def __init__(
                self, 
                *, 
                rule_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MATCH_RULE = "MatchRule"
        RATE_LIMIT_RULE = "RateLimitRule"


    class azure.mgmt.frontdoor.models.RulesEngine(BasicResource):
        id: str
        name: str
        properties: Optional[RulesEngineProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RulesEngineProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.RulesEngineAction(_Model):
        request_header_actions: Optional[list[HeaderAction]]
        response_header_actions: Optional[list[HeaderAction]]
        route_configuration_override: Optional[RouteConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                request_header_actions: Optional[list[HeaderAction]] = ..., 
                response_header_actions: Optional[list[HeaderAction]] = ..., 
                route_configuration_override: Optional[RouteConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RulesEngineMatchCondition(_Model):
        negate_condition: Optional[bool]
        rules_engine_match_value: list[str]
        rules_engine_match_variable: Union[str, RulesEngineMatchVariable]
        rules_engine_operator: Union[str, RulesEngineOperator]
        selector: Optional[str]
        transforms: Optional[list[Union[str, Transform]]]

        @overload
        def __init__(
                self, 
                *, 
                negate_condition: Optional[bool] = ..., 
                rules_engine_match_value: list[str], 
                rules_engine_match_variable: Union[str, RulesEngineMatchVariable], 
                rules_engine_operator: Union[str, RulesEngineOperator], 
                selector: Optional[str] = ..., 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RulesEngineMatchVariable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IS_MOBILE = "IsMobile"
        POST_ARGS = "PostArgs"
        QUERY_STRING = "QueryString"
        REMOTE_ADDR = "RemoteAddr"
        REQUEST_BODY = "RequestBody"
        REQUEST_FILENAME = "RequestFilename"
        REQUEST_FILENAME_EXTENSION = "RequestFilenameExtension"
        REQUEST_HEADER = "RequestHeader"
        REQUEST_METHOD = "RequestMethod"
        REQUEST_PATH = "RequestPath"
        REQUEST_SCHEME = "RequestScheme"
        REQUEST_URI = "RequestUri"


    class azure.mgmt.frontdoor.models.RulesEngineOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GEO_MATCH = "GeoMatch"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        IP_MATCH = "IPMatch"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"


    class azure.mgmt.frontdoor.models.RulesEngineProperties(RulesEngineUpdateParameters):
        resource_state: Optional[Union[str, FrontDoorResourceState]]
        rules: list[RulesEngineRule]

        @overload
        def __init__(
                self, 
                *, 
                rules: Optional[list[RulesEngineRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RulesEngineRule(_Model):
        action: RulesEngineAction
        match_conditions: Optional[list[RulesEngineMatchCondition]]
        match_processing_behavior: Optional[Union[str, MatchProcessingBehavior]]
        name: str
        priority: int

        @overload
        def __init__(
                self, 
                *, 
                action: RulesEngineAction, 
                match_conditions: Optional[list[RulesEngineMatchCondition]] = ..., 
                match_processing_behavior: Optional[Union[str, MatchProcessingBehavior]] = ..., 
                name: str, 
                priority: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.RulesEngineUpdateParameters(_Model):
        rules: Optional[list[RulesEngineRule]]

        @overload
        def __init__(
                self, 
                *, 
                rules: Optional[list[RulesEngineRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ScrubbingRuleEntryMatchOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "Equals"
        EQUALS_ANY = "EqualsAny"


    class azure.mgmt.frontdoor.models.ScrubbingRuleEntryMatchVariable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QUERY_STRING_ARG_NAMES = "QueryStringArgNames"
        REQUEST_BODY_JSON_ARG_NAMES = "RequestBodyJsonArgNames"
        REQUEST_BODY_POST_ARG_NAMES = "RequestBodyPostArgNames"
        REQUEST_COOKIE_NAMES = "RequestCookieNames"
        REQUEST_HEADER_NAMES = "RequestHeaderNames"
        REQUEST_IP_ADDRESS = "RequestIPAddress"
        REQUEST_URI = "RequestUri"


    class azure.mgmt.frontdoor.models.ScrubbingRuleEntryState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.SecurityPolicyLink(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.SensitivityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.frontdoor.models.SessionAffinityEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.Sku(_Model):
        name: Optional[Union[str, SkuName]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, SkuName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLASSIC_AZURE_FRONT_DOOR = "Classic_AzureFrontDoor"
        PREMIUM_AZURE_FRONT_DOOR = "Premium_AzureFrontDoor"
        STANDARD_AZURE_FRONT_DOOR = "Standard_AzureFrontDoor"


    class azure.mgmt.frontdoor.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.frontdoor.models.SubResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.TagsObject(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.Timeseries(Resource):
        id: str
        location: str
        name: str
        properties: Optional[TimeseriesProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[TimeseriesProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.TimeseriesAggregationInterval(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        HOURLY = "Hourly"


    class azure.mgmt.frontdoor.models.TimeseriesDataPoint(_Model):
        date_time_utc: Optional[str]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                date_time_utc: Optional[str] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.TimeseriesProperties(_Model):
        aggregation_interval: Optional[Union[str, AggregationInterval]]
        country: Optional[str]
        end_date_time_utc: Optional[str]
        endpoint: Optional[str]
        start_date_time_utc: Optional[str]
        timeseries_data: Optional[list[TimeseriesDataPoint]]
        timeseries_type: Optional[Union[str, TimeseriesType]]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_interval: Optional[Union[str, AggregationInterval]] = ..., 
                country: Optional[str] = ..., 
                end_date_time_utc: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                start_date_time_utc: Optional[str] = ..., 
                timeseries_data: Optional[list[TimeseriesDataPoint]] = ..., 
                timeseries_type: Optional[Union[str, TimeseriesType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.TimeseriesType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LATENCY_P50 = "LatencyP50"
        LATENCY_P75 = "LatencyP75"
        LATENCY_P95 = "LatencyP95"
        MEASUREMENT_COUNTS = "MeasurementCounts"


    class azure.mgmt.frontdoor.models.Transform(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOWERCASE = "Lowercase"
        REMOVE_NULLS = "RemoveNulls"
        TRIM = "Trim"
        UPPERCASE = "Uppercase"
        URL_DECODE = "UrlDecode"
        URL_ENCODE = "UrlEncode"


    class azure.mgmt.frontdoor.models.TransformType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOWERCASE = "Lowercase"
        REMOVE_NULLS = "RemoveNulls"
        TRIM = "Trim"
        UPPERCASE = "Uppercase"
        URL_DECODE = "UrlDecode"
        URL_ENCODE = "UrlEncode"


    class azure.mgmt.frontdoor.models.ValidateCustomDomainInput(_Model):
        host_name: str

        @overload
        def __init__(
                self, 
                *, 
                host_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.ValidateCustomDomainOutput(_Model):
        custom_domain_validated: Optional[bool]
        message: Optional[str]
        reason: Optional[str]


    class azure.mgmt.frontdoor.models.VariableName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASN = "Asn"
        GEO_LOCATION = "GeoLocation"
        JA4 = "Ja4"
        NONE = "None"
        SOCKET_ADDR = "SocketAddr"


    class azure.mgmt.frontdoor.models.WebApplicationFirewallPolicy(Resource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[WebApplicationFirewallPolicyProperties]
        sku: Optional[Sku]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[WebApplicationFirewallPolicyProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.frontdoor.models.WebApplicationFirewallPolicyProperties(_Model):
        custom_rules: Optional[CustomRuleList]
        frontend_endpoint_links: Optional[list[FrontendEndpointLink]]
        managed_rules: Optional[ManagedRuleSetList]
        policy_settings: Optional[PolicySettings]
        provisioning_state: Optional[str]
        resource_state: Optional[Union[str, PolicyResourceState]]
        routing_rule_links: Optional[list[RoutingRuleLink]]
        security_policy_links: Optional[list[SecurityPolicyLink]]

        @overload
        def __init__(
                self, 
                *, 
                custom_rules: Optional[CustomRuleList] = ..., 
                managed_rules: Optional[ManagedRuleSetList] = ..., 
                policy_settings: Optional[PolicySettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.WebApplicationFirewallScrubbingRules(_Model):
        match_variable: Union[str, ScrubbingRuleEntryMatchVariable]
        selector: Optional[str]
        selector_match_operator: Union[str, ScrubbingRuleEntryMatchOperator]
        state: Optional[Union[str, ScrubbingRuleEntryState]]

        @overload
        def __init__(
                self, 
                *, 
                match_variable: Union[str, ScrubbingRuleEntryMatchVariable], 
                selector: Optional[str] = ..., 
                selector_match_operator: Union[str, ScrubbingRuleEntryMatchOperator], 
                state: Optional[Union[str, ScrubbingRuleEntryState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.frontdoor.models.WebApplicationFirewallScrubbingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


namespace azure.mgmt.frontdoor.operations

    class azure.mgmt.frontdoor.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_purge_content(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                content_file_paths: PurgeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_purge_content(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                content_file_paths: PurgeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_purge_content(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                content_file_paths: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.frontdoor.operations.ExperimentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                parameters: Experiment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Experiment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                parameters: Experiment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Experiment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Experiment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                parameters: ExperimentUpdateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Experiment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                parameters: ExperimentUpdateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Experiment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Experiment]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> Experiment: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Experiment]: ...


    class azure.mgmt.frontdoor.operations.FrontDoorNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check(
                self, 
                check_front_door_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check(
                self, 
                check_front_door_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check(
                self, 
                check_front_door_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...


    class azure.mgmt.frontdoor.operations.FrontDoorNameAvailabilityWithSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check(
                self, 
                check_front_door_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check(
                self, 
                check_front_door_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check(
                self, 
                check_front_door_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...


    class azure.mgmt.frontdoor.operations.FrontDoorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                front_door_parameters: FrontDoor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FrontDoor]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                front_door_parameters: FrontDoor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FrontDoor]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                front_door_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FrontDoor]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                **kwargs: Any
            ) -> FrontDoor: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[FrontDoor]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FrontDoor]: ...

        @overload
        def validate_custom_domain(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                custom_domain_properties: ValidateCustomDomainInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...

        @overload
        def validate_custom_domain(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                custom_domain_properties: ValidateCustomDomainInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...

        @overload
        def validate_custom_domain(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                custom_domain_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...


    class azure.mgmt.frontdoor.operations.FrontendEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_disable_https(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                frontend_endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_enable_https(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                frontend_endpoint_name: str, 
                custom_https_configuration: CustomHttpsConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_enable_https(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                frontend_endpoint_name: str, 
                custom_https_configuration: CustomHttpsConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_enable_https(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                frontend_endpoint_name: str, 
                custom_https_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                frontend_endpoint_name: str, 
                **kwargs: Any
            ) -> FrontendEndpoint: ...

        @distributed_trace
        def list_by_front_door(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FrontendEndpoint]: ...


    class azure.mgmt.frontdoor.operations.ManagedRuleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ManagedRuleSetDefinition]: ...


    class azure.mgmt.frontdoor.operations.NetworkExperimentProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                profile_name: str, 
                resource_group_name: str, 
                parameters: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Profile]: ...

        @overload
        def begin_create_or_update(
                self, 
                profile_name: str, 
                resource_group_name: str, 
                parameters: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Profile]: ...

        @overload
        def begin_create_or_update(
                self, 
                profile_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Profile]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: ProfileUpdateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Profile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: ProfileUpdateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Profile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Profile]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Profile: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Profile]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Profile]: ...


    class azure.mgmt.frontdoor.operations.PoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: WebApplicationFirewallPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebApplicationFirewallPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: WebApplicationFirewallPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebApplicationFirewallPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebApplicationFirewallPolicy]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebApplicationFirewallPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebApplicationFirewallPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebApplicationFirewallPolicy]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> WebApplicationFirewallPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WebApplicationFirewallPolicy]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[WebApplicationFirewallPolicy]: ...


    class azure.mgmt.frontdoor.operations.PreconfiguredEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PreconfiguredEndpoint]: ...


    class azure.mgmt.frontdoor.operations.ReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_latency_scorecards(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                *, 
                aggregation_interval: Union[str, LatencyScorecardAggregationInterval], 
                country: Optional[str] = ..., 
                end_date_time_utc: Optional[str] = ..., 
                **kwargs: Any
            ) -> LatencyScorecard: ...

        @distributed_trace
        def get_timeseries(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                experiment_name: str, 
                *, 
                aggregation_interval: Union[str, TimeseriesAggregationInterval], 
                country: Optional[str] = ..., 
                end_date_time_utc: datetime, 
                endpoint: Optional[str] = ..., 
                start_date_time_utc: datetime, 
                timeseries_type: Union[str, TimeseriesType], 
                **kwargs: Any
            ) -> Timeseries: ...


    class azure.mgmt.frontdoor.operations.RulesEnginesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                rules_engine_name: str, 
                rules_engine_parameters: RulesEngine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RulesEngine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                rules_engine_name: str, 
                rules_engine_parameters: RulesEngine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RulesEngine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                rules_engine_name: str, 
                rules_engine_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RulesEngine]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                rules_engine_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                rules_engine_name: str, 
                **kwargs: Any
            ) -> RulesEngine: ...

        @distributed_trace
        def list_by_front_door(
                self, 
                resource_group_name: str, 
                front_door_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RulesEngine]: ...


namespace azure.mgmt.frontdoor.types

    class azure.mgmt.frontdoor.types.Backend(TypedDict, total=False):
        key "address": str
        key "backendHostHeader": str
        key "enabledState": Union[str, BackendEnabledState]
        key "httpPort": int
        key "httpsPort": int
        key "priority": int
        key "privateEndpointStatus": Union[str, PrivateEndpointStatus]
        key "privateLinkAlias": str
        key "privateLinkApprovalMessage": str
        key "privateLinkLocation": str
        key "privateLinkResourceId": str
        key "weight": int
        address: str
        backendHostHeader: str
        enabledState: Union[str, BackendEnabledState]
        httpPort: int
        httpsPort: int
        priority: int
        privateEndpointStatus: Union[str, PrivateEndpointStatus]
        privateLinkAlias: str
        privateLinkApprovalMessage: str
        privateLinkLocation: str
        privateLinkResourceId: str
        weight: int


    class azure.mgmt.frontdoor.types.BackendPool(SubResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('BackendPoolProperties', module='types')
        key "type": str
        id: str
        name: str
        properties: BackendPoolProperties
        type: str


    class azure.mgmt.frontdoor.types.BackendPoolProperties(BackendPoolUpdateParameters):
        key "healthProbeSettings": ForwardRef('SubResource', module='types')
        key "loadBalancingSettings": ForwardRef('SubResource', module='types')
        key "resourceState": Union[str, FrontDoorResourceState]
        backends: list[Backend]
        healthProbeSettings: SubResource
        loadBalancingSettings: SubResource
        resourceState: Union[str, FrontDoorResourceState]


    class azure.mgmt.frontdoor.types.BackendPoolUpdateParameters(TypedDict, total=False):
        key "healthProbeSettings": ForwardRef('SubResource', module='types')
        key "loadBalancingSettings": ForwardRef('SubResource', module='types')
        backends: list[Backend]
        healthProbeSettings: SubResource
        loadBalancingSettings: SubResource


    class azure.mgmt.frontdoor.types.BackendPoolsSettings(TypedDict, total=False):
        key "enforceCertificateNameCheck": Union[str, EnforceCertificateNameCheckEnabledState]
        key "sendRecvTimeoutSeconds": int
        enforceCertificateNameCheck: Union[str, EnforceCertificateNameCheckEnabledState]
        sendRecvTimeoutSeconds: int


    class azure.mgmt.frontdoor.types.BasicResource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "type": str
        id: str
        name: str
        type: str


    class azure.mgmt.frontdoor.types.BasicResourceWithSettableIDName(TypedDict, total=False):
        key "id": str
        key "name": str
        key "type": str
        id: str
        name: str
        type: str


    class azure.mgmt.frontdoor.types.CacheConfiguration(TypedDict, total=False):
        key "cacheDuration": str
        key "dynamicCompression": Union[str, DynamicCompressionEnabled]
        key "queryParameterStripDirective": Union[str, FrontDoorQuery]
        key "queryParameters": str
        cacheDuration: str
        dynamicCompression: Union[str, DynamicCompressionEnabled]
        queryParameterStripDirective: Union[str, FrontDoorQuery]
        queryParameters: str


    class azure.mgmt.frontdoor.types.CheckNameAvailabilityInput(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, ResourceType]]
        name: str
        type: Union[str, ResourceType]


    class azure.mgmt.frontdoor.types.CustomHttpsConfiguration(TypedDict, total=False):
        key "certificateSource": Required[Union[str, FrontDoorCertificateSource]]
        key "frontDoorCertificateSourceParameters": ForwardRef('FrontDoorCertificateSourceParameters', module='types')
        key "keyVaultCertificateSourceParameters": ForwardRef('KeyVaultCertificateSourceParameters', module='types')
        key "minimumTlsVersion": Required[Union[str, MinimumTLSVersion]]
        key "protocolType": Required[Union[str, FrontDoorTlsProtocolType]]
        certificateSource: Union[str, FrontDoorCertificateSource]
        frontDoorCertificateSourceParameters: FrontDoorCertificateSourceParameters
        keyVaultCertificateSourceParameters: KeyVaultCertificateSourceParameters
        minimumTlsVersion: Union[str, MinimumTLSVersion]
        protocolType: Union[str, FrontDoorTlsProtocolType]


    class azure.mgmt.frontdoor.types.CustomRule(TypedDict, total=False):
        key "action": Required[Union[str, ActionType]]
        key "enabledState": Union[str, CustomRuleEnabledState]
        key "matchConditions": Required[list[MatchCondition]]
        key "name": str
        key "priority": Required[int]
        key "rateLimitDurationInMinutes": int
        key "rateLimitThreshold": int
        key "ruleType": Required[Union[str, RuleType]]
        action: Union[str, ActionType]
        enabledState: Union[str, CustomRuleEnabledState]
        groupBy: list[GroupByVariable]
        matchConditions: list[MatchCondition]
        name: str
        priority: int
        rateLimitDurationInMinutes: int
        rateLimitThreshold: int
        ruleType: Union[str, RuleType]


    class azure.mgmt.frontdoor.types.CustomRuleList(TypedDict, total=False):
        rules: list[CustomRule]


    class azure.mgmt.frontdoor.types.Endpoint(TypedDict, total=False):
        key "endpoint": str
        key "name": str
        endpoint: str
        name: str


    class azure.mgmt.frontdoor.types.Experiment(Resource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('ExperimentProperties', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ExperimentProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.frontdoor.types.ExperimentProperties(TypedDict, total=False):
        key "description": str
        key "enabledState": Union[str, State]
        key "endpointA": ForwardRef('Endpoint', module='types')
        key "endpointB": ForwardRef('Endpoint', module='types')
        key "resourceState": Union[str, NetworkExperimentResourceState]
        key "scriptFileUri": str
        key "status": str
        description: str
        enabledState: Union[str, State]
        endpointA: Endpoint
        endpointB: Endpoint
        resourceState: Union[str, NetworkExperimentResourceState]
        scriptFileUri: str
        status: str


    class azure.mgmt.frontdoor.types.ExperimentUpdateModel(TypedDict, total=False):
        key "properties": ForwardRef('ExperimentUpdateProperties', module='types')
        properties: ExperimentUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.frontdoor.types.ExperimentUpdateProperties(TypedDict, total=False):
        key "description": str
        key "enabledState": Union[str, State]
        description: str
        enabledState: Union[str, State]


    class azure.mgmt.frontdoor.types.ForwardingConfiguration(TypedDict):
        key "@odata.type": Required[Literal["#FrontdoorForwardingConfiguration"]]
        key "backendPool": ForwardRef('SubResource', module='types')
        key "cacheConfiguration": ForwardRef('CacheConfiguration', module='types')
        key "customForwardingPath": str
        key "forwardingProtocol": Union[str, FrontDoorForwardingProtocol]
        ``@odata.type``: Literal[#FrontdoorForwardingConfiguration]
        backendPool: SubResource
        cacheConfiguration: CacheConfiguration
        customForwardingPath: str
        forwardingProtocol: Union[str, FrontDoorForwardingProtocol]


    class azure.mgmt.frontdoor.types.FrontDoor(Resource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('FrontDoorProperties', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: FrontDoorProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.frontdoor.types.FrontDoorCertificateSourceParameters(TypedDict, total=False):
        key "certificateType": Union[str, FrontDoorCertificateType]
        certificateType: Union[str, FrontDoorCertificateType]


    class azure.mgmt.frontdoor.types.FrontDoorProperties(FrontDoorUpdateParameters):
        key "backendPoolsSettings": ForwardRef('BackendPoolsSettings', module='types')
        key "cname": str
        key "enabledState": Union[str, FrontDoorEnabledState]
        key "friendlyName": str
        key "frontdoorId": str
        key "provisioningState": str
        key "resourceState": Union[str, FrontDoorResourceState]
        backendPools: list[BackendPool]
        backendPoolsSettings: BackendPoolsSettings
        cname: str
        enabledState: Union[str, FrontDoorEnabledState]
        extendedProperties: dict[str, str]
        friendlyName: str
        frontdoorId: str
        frontendEndpoints: list[FrontendEndpoint]
        healthProbeSettings: list[HealthProbeSettingsModel]
        loadBalancingSettings: list[LoadBalancingSettingsModel]
        provisioningState: str
        resourceState: Union[str, FrontDoorResourceState]
        routingRules: list[RoutingRule]
        rulesEngines: list[RulesEngine]


    class azure.mgmt.frontdoor.types.FrontDoorUpdateParameters(TypedDict, total=False):
        key "backendPoolsSettings": ForwardRef('BackendPoolsSettings', module='types')
        key "enabledState": Union[str, FrontDoorEnabledState]
        key "friendlyName": str
        backendPools: list[BackendPool]
        backendPoolsSettings: BackendPoolsSettings
        enabledState: Union[str, FrontDoorEnabledState]
        friendlyName: str
        frontendEndpoints: list[FrontendEndpoint]
        healthProbeSettings: list[HealthProbeSettingsModel]
        loadBalancingSettings: list[LoadBalancingSettingsModel]
        routingRules: list[RoutingRule]


    class azure.mgmt.frontdoor.types.FrontendEndpoint(BasicResourceWithSettableIDName):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FrontendEndpointProperties', module='types')
        key "type": str
        id: str
        name: str
        properties: FrontendEndpointProperties
        type: str


    class azure.mgmt.frontdoor.types.FrontendEndpointLink(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.frontdoor.types.FrontendEndpointProperties(FrontendEndpointUpdateParameters):
        key "customHttpsConfiguration": ForwardRef('CustomHttpsConfiguration', module='types')
        key "customHttpsProvisioningState": Union[str, CustomHttpsProvisioningState]
        key "customHttpsProvisioningSubstate": Union[str, CustomHttpsProvisioningSubstate]
        key "hostName": str
        key "resourceState": Union[str, FrontDoorResourceState]
        key "sessionAffinityEnabledState": Union[str, SessionAffinityEnabledState]
        key "sessionAffinityTtlSeconds": int
        key "webApplicationFirewallPolicyLink": ForwardRef('FrontendEndpointUpdateParametersWebApplicationFirewallPolicyLink', module='types')
        customHttpsConfiguration: CustomHttpsConfiguration
        customHttpsProvisioningState: Union[str, CustomHttpsProvisioningState]
        customHttpsProvisioningSubstate: Union[str, CustomHttpsProvisioningSubstate]
        hostName: str
        resourceState: Union[str, FrontDoorResourceState]
        sessionAffinityEnabledState: Union[str, SessionAffinityEnabledState]
        sessionAffinityTtlSeconds: int
        webApplicationFirewallPolicyLink: FrontendEndpointUpdateParametersWebApplicationFirewallPolicyLink


    class azure.mgmt.frontdoor.types.FrontendEndpointUpdateParameters(TypedDict, total=False):
        key "hostName": str
        key "sessionAffinityEnabledState": Union[str, SessionAffinityEnabledState]
        key "sessionAffinityTtlSeconds": int
        key "webApplicationFirewallPolicyLink": ForwardRef('FrontendEndpointUpdateParametersWebApplicationFirewallPolicyLink', module='types')
        hostName: str
        sessionAffinityEnabledState: Union[str, SessionAffinityEnabledState]
        sessionAffinityTtlSeconds: int
        webApplicationFirewallPolicyLink: FrontendEndpointUpdateParametersWebApplicationFirewallPolicyLink


    class azure.mgmt.frontdoor.types.FrontendEndpointUpdateParametersWebApplicationFirewallPolicyLink(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.frontdoor.types.GroupByVariable(TypedDict, total=False):
        key "variableName": Required[Union[str, VariableName]]
        variableName: Union[str, VariableName]


    class azure.mgmt.frontdoor.types.HeaderAction(TypedDict, total=False):
        key "headerActionType": Required[Union[str, HeaderActionType]]
        key "headerName": Required[str]
        key "value": str
        headerActionType: Union[str, HeaderActionType]
        headerName: str
        value: str


    class azure.mgmt.frontdoor.types.HealthProbeSettingsModel(SubResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('HealthProbeSettingsProperties', module='types')
        key "type": str
        id: str
        name: str
        properties: HealthProbeSettingsProperties
        type: str


    class azure.mgmt.frontdoor.types.HealthProbeSettingsProperties(HealthProbeSettingsUpdateParameters):
        key "enabledState": Union[str, HealthProbeEnabled]
        key "healthProbeMethod": Union[str, FrontDoorHealthProbeMethod]
        key "intervalInSeconds": int
        key "path": str
        key "protocol": Union[str, FrontDoorProtocol]
        key "resourceState": Union[str, FrontDoorResourceState]
        enabledState: Union[str, HealthProbeEnabled]
        healthProbeMethod: Union[str, FrontDoorHealthProbeMethod]
        intervalInSeconds: int
        path: str
        protocol: Union[str, FrontDoorProtocol]
        resourceState: Union[str, FrontDoorResourceState]


    class azure.mgmt.frontdoor.types.HealthProbeSettingsUpdateParameters(TypedDict, total=False):
        key "enabledState": Union[str, HealthProbeEnabled]
        key "healthProbeMethod": Union[str, FrontDoorHealthProbeMethod]
        key "intervalInSeconds": int
        key "path": str
        key "protocol": Union[str, FrontDoorProtocol]
        enabledState: Union[str, HealthProbeEnabled]
        healthProbeMethod: Union[str, FrontDoorHealthProbeMethod]
        intervalInSeconds: int
        path: str
        protocol: Union[str, FrontDoorProtocol]


    class azure.mgmt.frontdoor.types.KeyVaultCertificateSourceParameters(TypedDict, total=False):
        key "secretName": str
        key "secretVersion": str
        key "vault": ForwardRef('KeyVaultCertificateSourceParametersVault', module='types')
        secretName: str
        secretVersion: str
        vault: KeyVaultCertificateSourceParametersVault


    class azure.mgmt.frontdoor.types.KeyVaultCertificateSourceParametersVault(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.frontdoor.types.LoadBalancingSettingsModel(SubResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('LoadBalancingSettingsProperties', module='types')
        key "type": str
        id: str
        name: str
        properties: LoadBalancingSettingsProperties
        type: str


    class azure.mgmt.frontdoor.types.LoadBalancingSettingsProperties(LoadBalancingSettingsUpdateParameters):
        key "additionalLatencyMilliseconds": int
        key "resourceState": Union[str, FrontDoorResourceState]
        key "sampleSize": int
        key "successfulSamplesRequired": int
        additionalLatencyMilliseconds: int
        resourceState: Union[str, FrontDoorResourceState]
        sampleSize: int
        successfulSamplesRequired: int


    class azure.mgmt.frontdoor.types.LoadBalancingSettingsUpdateParameters(TypedDict, total=False):
        key "additionalLatencyMilliseconds": int
        key "sampleSize": int
        key "successfulSamplesRequired": int
        additionalLatencyMilliseconds: int
        sampleSize: int
        successfulSamplesRequired: int


    class azure.mgmt.frontdoor.types.ManagedRuleExclusion(TypedDict, total=False):
        key "matchVariable": Required[Union[str, ManagedRuleExclusionMatchVariable]]
        key "selector": Required[str]
        key "selectorMatchOperator": Required[Union[str, ManagedRuleExclusionSelectorMatchOperator]]
        matchVariable: Union[str, ManagedRuleExclusionMatchVariable]
        selector: str
        selectorMatchOperator: Union[str, ManagedRuleExclusionSelectorMatchOperator]


    class azure.mgmt.frontdoor.types.ManagedRuleGroupOverride(TypedDict, total=False):
        key "ruleGroupName": Required[str]
        exclusions: list[ManagedRuleExclusion]
        ruleGroupName: str
        rules: list[ManagedRuleOverride]


    class azure.mgmt.frontdoor.types.ManagedRuleOverride(TypedDict, total=False):
        key "action": Union[str, ActionType]
        key "enabledState": Union[str, ManagedRuleEnabledState]
        key "ruleId": Required[str]
        key "sensitivity": Union[str, SensitivityType]
        action: Union[str, ActionType]
        enabledState: Union[str, ManagedRuleEnabledState]
        exclusions: list[ManagedRuleExclusion]
        ruleId: str
        sensitivity: Union[str, SensitivityType]


    class azure.mgmt.frontdoor.types.ManagedRuleSet(TypedDict, total=False):
        key "ruleSetAction": Union[str, ManagedRuleSetActionType]
        key "ruleSetType": Required[str]
        key "ruleSetVersion": Required[str]
        exclusions: list[ManagedRuleExclusion]
        ruleGroupOverrides: list[ManagedRuleGroupOverride]
        ruleSetAction: Union[str, ManagedRuleSetActionType]
        ruleSetType: str
        ruleSetVersion: str


    class azure.mgmt.frontdoor.types.ManagedRuleSetException(TypedDict, total=False):
        key "matchValues": Required[list[str]]
        key "matchVariable": Required[Union[str, ExceptionMatchVariable]]
        key "scopes": Required[list[ManagedRuleSetScope]]
        key "selector": str
        key "selectorMatchOperator": Union[str, ExceptionSelectorMatchOperator]
        key "valueMatchOperator": Required[Union[str, ExceptionValueMatchOperator]]
        matchValues: list[str]
        matchVariable: Union[str, ExceptionMatchVariable]
        scopes: list[ManagedRuleSetScope]
        selector: str
        selectorMatchOperator: Union[str, ExceptionSelectorMatchOperator]
        valueMatchOperator: Union[str, ExceptionValueMatchOperator]


    class azure.mgmt.frontdoor.types.ManagedRuleSetExceptionList(TypedDict, total=False):
        exceptions: list[ManagedRuleSetException]


    class azure.mgmt.frontdoor.types.ManagedRuleSetList(TypedDict, total=False):
        key "exceptionsList": ForwardRef('ManagedRuleSetExceptionList', module='types')
        exceptionsList: ManagedRuleSetExceptionList
        managedRuleSets: list[ManagedRuleSet]


    class azure.mgmt.frontdoor.types.ManagedRuleSetScope(TypedDict, total=False):
        key "ruleSetType": Required[str]
        key "ruleSetVersion": Required[str]
        ruleGroupScopes: list[RuleGroupScope]
        ruleSetType: str
        ruleSetVersion: str


    class azure.mgmt.frontdoor.types.MatchCondition(TypedDict, total=False):
        key "matchValue": Required[list[str]]
        key "matchVariable": Required[Union[str, MatchVariable]]
        key "negateCondition": bool
        key "operator": Required[Union[str, Operator]]
        key "selector": str
        matchValue: list[str]
        matchVariable: Union[str, MatchVariable]
        negateCondition: bool
        operator: Union[str, Operator]
        selector: str
        transforms: list[Union[str, TransformType]]


    class azure.mgmt.frontdoor.types.PolicySettings(TypedDict, total=False):
        key "captchaExpirationInMinutes": int
        key "customBlockResponseBody": str
        key "customBlockResponseStatusCode": int
        key "enabledState": Union[str, PolicyEnabledState]
        key "javascriptChallengeExpirationInMinutes": int
        key "logScrubbing": ForwardRef('PolicySettingsLogScrubbing', module='types')
        key "mode": Union[str, PolicyMode]
        key "redirectUrl": str
        key "requestBodyCheck": Union[str, PolicyRequestBodyCheck]
        captchaExpirationInMinutes: int
        customBlockResponseBody: str
        customBlockResponseStatusCode: int
        enabledState: Union[str, PolicyEnabledState]
        javascriptChallengeExpirationInMinutes: int
        logScrubbing: PolicySettingsLogScrubbing
        mode: Union[str, PolicyMode]
        redirectUrl: str
        requestBodyCheck: Union[str, PolicyRequestBodyCheck]


    class azure.mgmt.frontdoor.types.PolicySettingsLogScrubbing(TypedDict, total=False):
        key "state": Union[str, WebApplicationFirewallScrubbingState]
        scrubbingRules: list[WebApplicationFirewallScrubbingRules]
        state: Union[str, WebApplicationFirewallScrubbingState]


    class azure.mgmt.frontdoor.types.Profile(ResourcewithSettableName):
        key "etag": str
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('ProfileProperties', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: ProfileProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.frontdoor.types.ProfileProperties(TypedDict, total=False):
        key "enabledState": Union[str, State]
        key "resourceState": Union[str, NetworkExperimentResourceState]
        enabledState: Union[str, State]
        resourceState: Union[str, NetworkExperimentResourceState]


    class azure.mgmt.frontdoor.types.ProfileUpdateModel(TypedDict, total=False):
        key "properties": ForwardRef('ProfileUpdateProperties', module='types')
        properties: ProfileUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.frontdoor.types.ProfileUpdateProperties(TypedDict, total=False):
        key "enabledState": Union[str, State]
        enabledState: Union[str, State]


    class azure.mgmt.frontdoor.types.PurgeParameters(TypedDict, total=False):
        key "contentPaths": Required[list[str]]
        contentPaths: list[str]


    class azure.mgmt.frontdoor.types.RedirectConfiguration(TypedDict):
        key "@odata.type": Required[Literal["#FrontdoorRedirectConfiguration"]]
        key "customFragment": str
        key "customHost": str
        key "customPath": str
        key "customQueryString": str
        key "redirectProtocol": Union[str, FrontDoorRedirectProtocol]
        key "redirectType": Union[str, FrontDoorRedirectType]
        ``@odata.type``: Literal[#FrontdoorRedirectConfiguration]
        customFragment: str
        customHost: str
        customPath: str
        customQueryString: str
        redirectProtocol: Union[str, FrontDoorRedirectProtocol]
        redirectType: Union[str, FrontDoorRedirectType]


    class azure.mgmt.frontdoor.types.Resource(TypedDict, total=False):
        key "id": str
        key "location": str
        key "name": str
        key "type": str
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str


    class azure.mgmt.frontdoor.types.ResourcewithSettableName(TypedDict, total=False):
        key "id": str
        key "location": str
        key "name": str
        key "type": str
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str


    class azure.mgmt.frontdoor.types.RoutingRule(SubResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RoutingRuleProperties', module='types')
        key "type": str
        id: str
        name: str
        properties: RoutingRuleProperties
        type: str


    class azure.mgmt.frontdoor.types.RoutingRuleLink(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.frontdoor.types.RoutingRuleProperties(RoutingRuleUpdateParameters):
        key "enabledState": Union[str, RoutingRuleEnabledState]
        key "resourceState": Union[str, FrontDoorResourceState]
        key "routeConfiguration": ForwardRef('RouteConfiguration', module='types')
        key "rulesEngine": ForwardRef('SubResource', module='types')
        key "webApplicationFirewallPolicyLink": ForwardRef('RoutingRuleUpdateParametersWebApplicationFirewallPolicyLink', module='types')
        acceptedProtocols: list[Union[str, FrontDoorProtocol]]
        enabledState: Union[str, RoutingRuleEnabledState]
        frontendEndpoints: list[SubResource]
        patternsToMatch: list[str]
        resourceState: Union[str, FrontDoorResourceState]
        routeConfiguration: RouteConfiguration
        rulesEngine: SubResource
        webApplicationFirewallPolicyLink: RoutingRuleUpdateParametersWebApplicationFirewallPolicyLink


    class azure.mgmt.frontdoor.types.RoutingRuleUpdateParameters(TypedDict, total=False):
        key "enabledState": Union[str, RoutingRuleEnabledState]
        key "routeConfiguration": ForwardRef('RouteConfiguration', module='types')
        key "rulesEngine": ForwardRef('SubResource', module='types')
        key "webApplicationFirewallPolicyLink": ForwardRef('RoutingRuleUpdateParametersWebApplicationFirewallPolicyLink', module='types')
        acceptedProtocols: list[Union[str, FrontDoorProtocol]]
        enabledState: Union[str, RoutingRuleEnabledState]
        frontendEndpoints: list[SubResource]
        patternsToMatch: list[str]
        routeConfiguration: RouteConfiguration
        rulesEngine: SubResource
        webApplicationFirewallPolicyLink: RoutingRuleUpdateParametersWebApplicationFirewallPolicyLink


    class azure.mgmt.frontdoor.types.RoutingRuleUpdateParametersWebApplicationFirewallPolicyLink(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.frontdoor.types.RuleGroupScope(TypedDict, total=False):
        key "ruleGroupName": Required[str]
        ruleGroupName: str
        ruleScopes: list[RuleScope]


    class azure.mgmt.frontdoor.types.RuleScope(TypedDict, total=False):
        key "ruleId": Required[str]
        ruleId: str


    class azure.mgmt.frontdoor.types.RulesEngine(BasicResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RulesEngineProperties', module='types')
        key "type": str
        id: str
        name: str
        properties: RulesEngineProperties
        type: str


    class azure.mgmt.frontdoor.types.RulesEngineAction(TypedDict, total=False):
        key "routeConfigurationOverride": ForwardRef('RouteConfiguration', module='types')
        requestHeaderActions: list[HeaderAction]
        responseHeaderActions: list[HeaderAction]
        routeConfigurationOverride: RouteConfiguration


    class azure.mgmt.frontdoor.types.RulesEngineMatchCondition(TypedDict, total=False):
        key "negateCondition": bool
        key "rulesEngineMatchValue": Required[list[str]]
        key "rulesEngineMatchVariable": Required[Union[str, RulesEngineMatchVariable]]
        key "rulesEngineOperator": Required[Union[str, RulesEngineOperator]]
        key "selector": str
        negateCondition: bool
        rulesEngineMatchValue: list[str]
        rulesEngineMatchVariable: Union[str, RulesEngineMatchVariable]
        rulesEngineOperator: Union[str, RulesEngineOperator]
        selector: str
        transforms: list[Union[str, Transform]]


    class azure.mgmt.frontdoor.types.RulesEngineProperties(RulesEngineUpdateParameters):
        key "resourceState": Union[str, FrontDoorResourceState]
        resourceState: Union[str, FrontDoorResourceState]
        rules: list[RulesEngineRule]


    class azure.mgmt.frontdoor.types.RulesEngineRule(TypedDict, total=False):
        key "action": Required[RulesEngineAction]
        key "matchProcessingBehavior": Union[str, MatchProcessingBehavior]
        key "name": Required[str]
        key "priority": Required[int]
        action: RulesEngineAction
        matchConditions: list[RulesEngineMatchCondition]
        matchProcessingBehavior: Union[str, MatchProcessingBehavior]
        name: str
        priority: int


    class azure.mgmt.frontdoor.types.RulesEngineUpdateParameters(TypedDict, total=False):
        rules: list[RulesEngineRule]


    class azure.mgmt.frontdoor.types.SecurityPolicyLink(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.frontdoor.types.Sku(TypedDict, total=False):
        key "name": Union[str, SkuName]
        name: Union[str, SkuName]


    class azure.mgmt.frontdoor.types.SubResource(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.frontdoor.types.TagsObject(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.frontdoor.types.ValidateCustomDomainInput(TypedDict, total=False):
        key "hostName": Required[str]
        hostName: str


    class azure.mgmt.frontdoor.types.WebApplicationFirewallPolicy(Resource):
        key "etag": str
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('WebApplicationFirewallPolicyProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: WebApplicationFirewallPolicyProperties
        sku: Sku
        tags: dict[str, str]
        type: str


    class azure.mgmt.frontdoor.types.WebApplicationFirewallPolicyProperties(TypedDict, total=False):
        key "customRules": ForwardRef('CustomRuleList', module='types')
        key "managedRules": ForwardRef('ManagedRuleSetList', module='types')
        key "policySettings": ForwardRef('PolicySettings', module='types')
        key "provisioningState": str
        key "resourceState": Union[str, PolicyResourceState]
        customRules: CustomRuleList
        frontendEndpointLinks: list[FrontendEndpointLink]
        managedRules: ManagedRuleSetList
        policySettings: PolicySettings
        provisioningState: str
        resourceState: Union[str, PolicyResourceState]
        routingRuleLinks: list[RoutingRuleLink]
        securityPolicyLinks: list[SecurityPolicyLink]


    class azure.mgmt.frontdoor.types.WebApplicationFirewallScrubbingRules(TypedDict, total=False):
        key "matchVariable": Required[Union[str, ScrubbingRuleEntryMatchVariable]]
        key "selector": str
        key "selectorMatchOperator": Required[Union[str, ScrubbingRuleEntryMatchOperator]]
        key "state": Union[str, ScrubbingRuleEntryState]
        matchVariable: Union[str, ScrubbingRuleEntryMatchVariable]
        selector: str
        selectorMatchOperator: Union[str, ScrubbingRuleEntryMatchOperator]
        state: Union[str, ScrubbingRuleEntryState]


```