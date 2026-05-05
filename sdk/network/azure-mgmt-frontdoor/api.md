```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                content_file_paths: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                check_front_door_name_availability_input: JSON, 
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
                check_front_door_name_availability_input: JSON, 
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
                front_door_parameters: JSON, 
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
                custom_domain_properties: JSON, 
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
                custom_https_configuration: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                rules_engine_parameters: JSON, 
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
        provisioning_state: Optional[str]
        rule_groups: Optional[list[ManagedRuleGroupDefinition]]
        rule_set_id: Optional[str]
        rule_set_type: Optional[str]
        rule_set_version: Optional[str]


    class azure.mgmt.frontdoor.models.ManagedRuleSetList(_Model):
        managed_rule_sets: Optional[list[ManagedRuleSet]]

        @overload
        def __init__(
                self, 
                *, 
                managed_rule_sets: Optional[list[ManagedRuleSet]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        REG_EX = "RegEx"
        SERVICE_TAG_MATCH = "ServiceTagMatch"


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
        GEO_LOCATION = "GeoLocation"
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
                content_file_paths: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                check_front_door_name_availability_input: JSON, 
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
                check_front_door_name_availability_input: JSON, 
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
                front_door_parameters: JSON, 
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
                custom_domain_properties: JSON, 
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
                custom_https_configuration: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                rules_engine_parameters: JSON, 
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


```