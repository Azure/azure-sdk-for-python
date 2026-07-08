```py
namespace azure.mgmt.elastic

    class azure.mgmt.elastic.ElasticMgmtClient: implements ContextManager 
        all_traffic_filters: AllTrafficFiltersOperations
        associate_traffic_filter: AssociateTrafficFilterOperations
        billing_info: BillingInfoOperations
        connected_partner_resources: ConnectedPartnerResourcesOperations
        create_and_associate_ip_filter: CreateAndAssociateIPFilterOperations
        create_and_associate_pl_filter: CreateAndAssociatePLFilterOperations
        deployment_info: DeploymentInfoOperations
        detach_and_delete_traffic_filter: DetachAndDeleteTrafficFilterOperations
        detach_traffic_filter: DetachTrafficFilterOperations
        elastic_versions: ElasticVersionsOperations
        external_user: ExternalUserOperations
        list_associated_traffic_filters: ListAssociatedTrafficFiltersOperations
        monitor: MonitorOperations
        monitored_resources: MonitoredResourcesOperations
        monitored_subscriptions: MonitoredSubscriptionsOperations
        monitors: MonitorsOperations
        open_ai: OpenAIOperations
        operations: Operations
        organizations: OrganizationsOperations
        tag_rules: TagRulesOperations
        traffic_filters: TrafficFiltersOperations
        upgradable_versions: UpgradableVersionsOperations
        vm_collection: VMCollectionOperations
        vm_host: VMHostOperations
        vm_ingestion: VMIngestionOperations

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


namespace azure.mgmt.elastic.aio

    class azure.mgmt.elastic.aio.ElasticMgmtClient: implements AsyncContextManager 
        all_traffic_filters: AllTrafficFiltersOperations
        associate_traffic_filter: AssociateTrafficFilterOperations
        billing_info: BillingInfoOperations
        connected_partner_resources: ConnectedPartnerResourcesOperations
        create_and_associate_ip_filter: CreateAndAssociateIPFilterOperations
        create_and_associate_pl_filter: CreateAndAssociatePLFilterOperations
        deployment_info: DeploymentInfoOperations
        detach_and_delete_traffic_filter: DetachAndDeleteTrafficFilterOperations
        detach_traffic_filter: DetachTrafficFilterOperations
        elastic_versions: ElasticVersionsOperations
        external_user: ExternalUserOperations
        list_associated_traffic_filters: ListAssociatedTrafficFiltersOperations
        monitor: MonitorOperations
        monitored_resources: MonitoredResourcesOperations
        monitored_subscriptions: MonitoredSubscriptionsOperations
        monitors: MonitorsOperations
        open_ai: OpenAIOperations
        operations: Operations
        organizations: OrganizationsOperations
        tag_rules: TagRulesOperations
        traffic_filters: TrafficFiltersOperations
        upgradable_versions: UpgradableVersionsOperations
        vm_collection: VMCollectionOperations
        vm_host: VMHostOperations
        vm_ingestion: VMIngestionOperations

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


namespace azure.mgmt.elastic.aio.operations

    class azure.mgmt.elastic.aio.operations.AllTrafficFiltersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ElasticTrafficFilterResponse: ...


    class azure.mgmt.elastic.aio.operations.AssociateTrafficFilterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_associate(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                ruleset_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.elastic.aio.operations.BillingInfoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> BillingInfoResponse: ...


    class azure.mgmt.elastic.aio.operations.ConnectedPartnerResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConnectedPartnerResourcesListFormat]: ...


    class azure.mgmt.elastic.aio.operations.CreateAndAssociateIPFilterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                ips: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.elastic.aio.operations.CreateAndAssociatePLFilterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                name: Optional[str] = ..., 
                private_endpoint_guid: Optional[str] = ..., 
                private_endpoint_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.elastic.aio.operations.DeploymentInfoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> DeploymentInfoResponse: ...


    class azure.mgmt.elastic.aio.operations.DetachAndDeleteTrafficFilterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                ruleset_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.elastic.aio.operations.DetachTrafficFilterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                ruleset_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.elastic.aio.operations.ElasticVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                region: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ElasticVersionListFormat]: ...


    class azure.mgmt.elastic.aio.operations.ExternalUserOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ExternalUserInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExternalUserCreationResponse: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ExternalUserInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExternalUserCreationResponse: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExternalUserCreationResponse: ...


    class azure.mgmt.elastic.aio.operations.ListAssociatedTrafficFiltersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ElasticTrafficFilterResponse: ...


    class azure.mgmt.elastic.aio.operations.MonitorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ElasticMonitorUpgrade] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ElasticMonitorUpgrade] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.elastic.aio.operations.MonitoredResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitoredResource]: ...


    class azure.mgmt.elastic.aio.operations.MonitoredSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_createor_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        async def begin_createor_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        async def begin_createor_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> MonitoredSubscriptionProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitoredSubscriptionProperties]: ...


    class azure.mgmt.elastic.aio.operations.MonitorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ElasticMonitorResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticMonitorResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ElasticMonitorResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticMonitorResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticMonitorResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ElasticMonitorResourceUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticMonitorResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ElasticMonitorResourceUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticMonitorResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticMonitorResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ElasticMonitorResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ElasticMonitorResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ElasticMonitorResource]: ...


    class azure.mgmt.elastic.aio.operations.OpenAIOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                integration_name: str, 
                body: Optional[OpenAIIntegrationRPModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OpenAIIntegrationRPModel: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                integration_name: str, 
                body: Optional[OpenAIIntegrationRPModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OpenAIIntegrationRPModel: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                integration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OpenAIIntegrationRPModel: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                integration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                integration_name: str, 
                **kwargs: Any
            ) -> OpenAIIntegrationRPModel: ...

        @distributed_trace_async
        async def get_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                integration_name: str, 
                **kwargs: Any
            ) -> OpenAIIntegrationStatusResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OpenAIIntegrationRPModel]: ...


    class azure.mgmt.elastic.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationResult]: ...


    class azure.mgmt.elastic.aio.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ResubscribeProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticMonitorResource]: ...

        @overload
        async def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ResubscribeProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticMonitorResource]: ...

        @overload
        async def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticMonitorResource]: ...

        @overload
        async def get_api_key(
                self, 
                body: Optional[UserEmailId] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserApiKeyResponse: ...

        @overload
        async def get_api_key(
                self, 
                body: Optional[UserEmailId] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserApiKeyResponse: ...

        @overload
        async def get_api_key(
                self, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserApiKeyResponse: ...

        @distributed_trace_async
        async def get_elastic_to_azure_subscription_mapping(self, **kwargs: Any) -> ElasticOrganizationToAzureSubscriptionMappingResponse: ...


    class azure.mgmt.elastic.aio.operations.TagRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                body: Optional[MonitoringTagRules] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                body: Optional[MonitoringTagRules] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitoringTagRules]: ...


    class azure.mgmt.elastic.aio.operations.TrafficFiltersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                ruleset_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.elastic.aio.operations.UpgradableVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def details(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> UpgradableVersionsList: ...


    class azure.mgmt.elastic.aio.operations.VMCollectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[VMCollectionUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[VMCollectionUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.elastic.aio.operations.VMHostOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VMResources]: ...


    class azure.mgmt.elastic.aio.operations.VMIngestionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def details(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> VMIngestionDetailsResponse: ...


namespace azure.mgmt.elastic.models

    class azure.mgmt.elastic.models.BillingInfoResponse(_Model):
        marketplace_saas_info: Optional[MarketplaceSaaSInfo]
        partner_billing_entity: Optional[PartnerBillingEntity]

        @overload
        def __init__(
                self, 
                *, 
                marketplace_saas_info: Optional[MarketplaceSaaSInfo] = ..., 
                partner_billing_entity: Optional[PartnerBillingEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.CompanyInfo(_Model):
        business: Optional[str]
        country: Optional[str]
        domain: Optional[str]
        employees_number: Optional[str]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                business: Optional[str] = ..., 
                country: Optional[str] = ..., 
                domain: Optional[str] = ..., 
                employees_number: Optional[str] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GENERAL_PURPOSE = "GeneralPurpose"
        NOT_APPLICABLE = "NotApplicable"
        TIME_SERIES = "TimeSeries"
        VECTOR = "Vector"


    class azure.mgmt.elastic.models.ConnectedPartnerResourceProperties(_Model):
        azure_resource_id: Optional[str]
        location: Optional[str]
        partner_deployment_name: Optional[str]
        partner_deployment_uri: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                partner_deployment_name: Optional[str] = ..., 
                partner_deployment_uri: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ConnectedPartnerResourcesListFormat(_Model):
        properties: Optional[ConnectedPartnerResourceProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectedPartnerResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.elastic.models.DeploymentInfoResponse(_Model):
        configuration_type: Optional[str]
        deployment_url: Optional[str]
        disk_capacity: Optional[str]
        elasticsearch_end_point: Optional[str]
        marketplace_saas_info: Optional[MarketplaceSaaSInfo]
        memory_capacity: Optional[str]
        project_type: Optional[str]
        status: Optional[Union[str, ElasticDeploymentStatus]]
        version: Optional[str]


    class azure.mgmt.elastic.models.ElasticCloudDeployment(_Model):
        azure_subscription_id: Optional[str]
        deployment_id: Optional[str]
        elasticsearch_region: Optional[str]
        elasticsearch_service_url: Optional[str]
        kibana_service_url: Optional[str]
        kibana_sso_url: Optional[str]
        name: Optional[str]


    class azure.mgmt.elastic.models.ElasticCloudUser(_Model):
        elastic_cloud_sso_default_url: Optional[str]
        email_address: Optional[str]
        id: Optional[str]


    class azure.mgmt.elastic.models.ElasticDeploymentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.elastic.models.ElasticMonitorResource(TrackedResource):
        id: str
        identity: Optional[IdentityProperties]
        kind: Optional[str]
        location: str
        name: str
        properties: Optional[MonitorProperties]
        sku: Optional[ResourceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                properties: Optional[MonitorProperties] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ElasticMonitorResourceUpdateParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ElasticMonitorUpgrade(_Model):
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ElasticOrganizationToAzureSubscriptionMappingResponse(_Model):
        properties: Optional[ElasticOrganizationToAzureSubscriptionMappingResponseProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ElasticOrganizationToAzureSubscriptionMappingResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ElasticOrganizationToAzureSubscriptionMappingResponseProperties(_Model):
        billed_azure_subscription_id: Optional[str]
        elastic_organization_id: Optional[str]
        elastic_organization_name: Optional[str]
        marketplace_saas_info: Optional[MarketplaceSaaSInfo]

        @overload
        def __init__(
                self, 
                *, 
                billed_azure_subscription_id: Optional[str] = ..., 
                elastic_organization_id: Optional[str] = ..., 
                elastic_organization_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ElasticProperties(_Model):
        elastic_cloud_deployment: Optional[ElasticCloudDeployment]
        elastic_cloud_user: Optional[ElasticCloudUser]

        @overload
        def __init__(
                self, 
                *, 
                elastic_cloud_deployment: Optional[ElasticCloudDeployment] = ..., 
                elastic_cloud_user: Optional[ElasticCloudUser] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ElasticTrafficFilter(_Model):
        description: Optional[str]
        id: Optional[str]
        include_by_default: Optional[bool]
        name: Optional[str]
        region: Optional[str]
        rules: Optional[list[ElasticTrafficFilterRule]]
        type: Optional[Union[str, Type]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                include_by_default: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                region: Optional[str] = ..., 
                rules: Optional[list[ElasticTrafficFilterRule]] = ..., 
                type: Optional[Union[str, Type]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ElasticTrafficFilterResponse(_Model):
        rulesets: Optional[list[ElasticTrafficFilter]]

        @overload
        def __init__(
                self, 
                *, 
                rulesets: Optional[list[ElasticTrafficFilter]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ElasticTrafficFilterRule(_Model):
        azure_endpoint_guid: Optional[str]
        azure_endpoint_name: Optional[str]
        description: Optional[str]
        id: Optional[str]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_endpoint_guid: Optional[str] = ..., 
                azure_endpoint_name: Optional[str] = ..., 
                description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ElasticVersionListFormat(_Model):
        properties: Optional[ElasticVersionListProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ElasticVersionListProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ElasticVersionListProperties(_Model):
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.elastic.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.elastic.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ErrorResponseBody(_Model):
        code: Optional[str]
        details: Optional[list[ErrorResponseBody]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[ErrorResponseBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ExternalUserCreationResponse(_Model):
        created: Optional[bool]


    class azure.mgmt.elastic.models.ExternalUserInfo(_Model):
        email_id: Optional[str]
        full_name: Optional[str]
        password: Optional[str]
        roles: Optional[list[str]]
        user_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                email_id: Optional[str] = ..., 
                full_name: Optional[str] = ..., 
                password: Optional[str] = ..., 
                roles: Optional[list[str]] = ..., 
                user_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.FilteringTag(_Model):
        action: Optional[Union[str, TagAction]]
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, TagAction]] = ..., 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.HostingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HOSTED = "Hosted"
        SERVERLESS = "Serverless"


    class azure.mgmt.elastic.models.IdentityProperties(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ManagedIdentityTypes]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedIdentityTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.LiftrResourceCategories(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONITOR_LOGS = "MonitorLogs"
        UNKNOWN = "Unknown"


    class azure.mgmt.elastic.models.LogRules(_Model):
        filtering_tags: Optional[list[FilteringTag]]
        send_aad_logs: Optional[bool]
        send_activity_logs: Optional[bool]
        send_subscription_logs: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                filtering_tags: Optional[list[FilteringTag]] = ..., 
                send_aad_logs: Optional[bool] = ..., 
                send_activity_logs: Optional[bool] = ..., 
                send_subscription_logs: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ManagedIdentityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.elastic.models.MarketplaceSaaSInfo(_Model):
        billed_azure_subscription_id: Optional[str]
        marketplace_name: Optional[str]
        marketplace_resource_id: Optional[str]
        marketplace_status: Optional[str]
        marketplace_subscription: Optional[MarketplaceSaaSInfoMarketplaceSubscription]
        subscribed: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                billed_azure_subscription_id: Optional[str] = ..., 
                marketplace_name: Optional[str] = ..., 
                marketplace_resource_id: Optional[str] = ..., 
                marketplace_status: Optional[str] = ..., 
                marketplace_subscription: Optional[MarketplaceSaaSInfoMarketplaceSubscription] = ..., 
                subscribed: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.MarketplaceSaaSInfoMarketplaceSubscription(_Model):
        id: Optional[str]
        offer_id: Optional[str]
        publisher_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                offer_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.MonitorProperties(_Model):
        elastic_properties: Optional[ElasticProperties]
        generate_api_key: Optional[bool]
        hosting_type: Optional[Union[str, HostingType]]
        liftr_resource_category: Optional[Union[str, LiftrResourceCategories]]
        liftr_resource_preference: Optional[int]
        monitoring_status: Optional[Union[str, MonitoringStatus]]
        plan_details: Optional[PlanDetails]
        project_details: Optional[ProjectDetails]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        saa_s_azure_subscription_status: Optional[str]
        source_campaign_id: Optional[str]
        source_campaign_name: Optional[str]
        subscription_state: Optional[str]
        user_info: Optional[UserInfo]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                elastic_properties: Optional[ElasticProperties] = ..., 
                generate_api_key: Optional[bool] = ..., 
                hosting_type: Optional[Union[str, HostingType]] = ..., 
                monitoring_status: Optional[Union[str, MonitoringStatus]] = ..., 
                plan_details: Optional[PlanDetails] = ..., 
                project_details: Optional[ProjectDetails] = ..., 
                saa_s_azure_subscription_status: Optional[str] = ..., 
                source_campaign_id: Optional[str] = ..., 
                source_campaign_name: Optional[str] = ..., 
                subscription_state: Optional[str] = ..., 
                user_info: Optional[UserInfo] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.MonitoredResource(_Model):
        id: Optional[str]
        reason_for_logs_status: Optional[str]
        sending_logs: Optional[Union[str, SendingLogs]]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                reason_for_logs_status: Optional[str] = ..., 
                sending_logs: Optional[Union[str, SendingLogs]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.MonitoredSubscription(_Model):
        error: Optional[str]
        status: Optional[Union[str, Status]]
        subscription_id: str
        tag_rules: Optional[MonitoringTagRulesProperties]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                subscription_id: str, 
                tag_rules: Optional[MonitoringTagRulesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.MonitoredSubscriptionProperties(ProxyResource):
        id: str
        name: str
        properties: Optional[SubscriptionList]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.MonitoringStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.elastic.models.MonitoringTagRules(ProxyResource):
        id: str
        name: str
        properties: Optional[MonitoringTagRulesProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MonitoringTagRulesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.MonitoringTagRulesProperties(_Model):
        log_rules: Optional[LogRules]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                log_rules: Optional[LogRules] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.OpenAIIntegrationProperties(_Model):
        key: Optional[str]
        last_refresh_at: Optional[datetime]
        open_ai_connector_id: Optional[str]
        open_ai_resource_endpoint: Optional[str]
        open_ai_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                open_ai_connector_id: Optional[str] = ..., 
                open_ai_resource_endpoint: Optional[str] = ..., 
                open_ai_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.OpenAIIntegrationRPModel(ProxyResource):
        id: str
        name: str
        properties: Optional[OpenAIIntegrationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OpenAIIntegrationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.OpenAIIntegrationStatusResponse(_Model):
        properties: Optional[OpenAIIntegrationStatusResponseProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OpenAIIntegrationStatusResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.OpenAIIntegrationStatusResponseProperties(_Model):
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.Operation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        ADD_BEGIN = "AddBegin"
        ADD_COMPLETE = "AddComplete"
        DELETE_BEGIN = "DeleteBegin"
        DELETE_COMPLETE = "DeleteComplete"


    class azure.mgmt.elastic.models.OperationDisplay(_Model):
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


    class azure.mgmt.elastic.models.OperationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD = "Add"
        DELETE = "Delete"


    class azure.mgmt.elastic.models.OperationResult(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.PartnerBillingEntity(_Model):
        id: Optional[str]
        name: Optional[str]
        partner_entity_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                partner_entity_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.PlanDetails(_Model):
        offer_id: Optional[str]
        plan_id: Optional[str]
        plan_name: Optional[str]
        publisher_id: Optional[str]
        term_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                offer_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                plan_name: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                term_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ProjectDetails(_Model):
        configuration_type: Optional[Union[str, ConfigurationType]]
        project_type: Optional[Union[str, ProjectType]]

        @overload
        def __init__(
                self, 
                *, 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                project_type: Optional[Union[str, ProjectType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ProjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ELASTICSEARCH = "Elasticsearch"
        NOT_APPLICABLE = "NotApplicable"
        OBSERVABILITY = "Observability"
        SECURITY = "Security"


    class azure.mgmt.elastic.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.elastic.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.elastic.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.elastic.models.ResourceProviderDefaultErrorResponse(_Model):
        error: Optional[ErrorResponseBody]


    class azure.mgmt.elastic.models.ResourceSku(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.ResubscribeProperties(_Model):
        organization_id: Optional[str]
        plan_id: Optional[str]
        resource_group: Optional[str]
        subscription_id: Optional[str]
        term: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                organization_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                term: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.SendingLogs(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.elastic.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.elastic.models.SubscriptionList(_Model):
        monitored_subscription_list: Optional[list[MonitoredSubscription]]
        operation: Optional[Union[str, Operation]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                monitored_subscription_list: Optional[list[MonitoredSubscription]] = ..., 
                operation: Optional[Union[str, Operation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.SystemData(_Model):
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


    class azure.mgmt.elastic.models.TagAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDE = "Exclude"
        INCLUDE = "Include"


    class azure.mgmt.elastic.models.TrackedResource(Resource):
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


    class azure.mgmt.elastic.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_PRIVATE_ENDPOINT = "azure_private_endpoint"
        IP = "ip"


    class azure.mgmt.elastic.models.UpgradableVersionsList(_Model):
        current_version: Optional[str]
        upgradable_versions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                current_version: Optional[str] = ..., 
                upgradable_versions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.UserApiKeyResponse(_Model):
        properties: Optional[UserApiKeyResponseProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UserApiKeyResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.UserApiKeyResponseProperties(_Model):
        api_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.UserEmailId(_Model):
        email_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                email_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.UserInfo(_Model):
        company_info: Optional[CompanyInfo]
        company_name: Optional[str]
        email_address: Optional[str]
        first_name: Optional[str]
        last_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                company_info: Optional[CompanyInfo] = ..., 
                company_name: Optional[str] = ..., 
                email_address: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                last_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.VMCollectionUpdate(_Model):
        operation_name: Optional[Union[str, OperationName]]
        vm_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                operation_name: Optional[Union[str, OperationName]] = ..., 
                vm_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.VMIngestionDetailsResponse(_Model):
        cloud_id: Optional[str]
        ingestion_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud_id: Optional[str] = ..., 
                ingestion_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elastic.models.VMResources(_Model):
        vm_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                vm_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.elastic.operations

    class azure.mgmt.elastic.operations.AllTrafficFiltersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ElasticTrafficFilterResponse: ...


    class azure.mgmt.elastic.operations.AssociateTrafficFilterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_associate(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                ruleset_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.elastic.operations.BillingInfoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> BillingInfoResponse: ...


    class azure.mgmt.elastic.operations.ConnectedPartnerResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ConnectedPartnerResourcesListFormat]: ...


    class azure.mgmt.elastic.operations.CreateAndAssociateIPFilterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                ips: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.elastic.operations.CreateAndAssociatePLFilterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                name: Optional[str] = ..., 
                private_endpoint_guid: Optional[str] = ..., 
                private_endpoint_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.elastic.operations.DeploymentInfoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> DeploymentInfoResponse: ...


    class azure.mgmt.elastic.operations.DetachAndDeleteTrafficFilterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                ruleset_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.elastic.operations.DetachTrafficFilterOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                ruleset_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.elastic.operations.ElasticVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                region: str, 
                **kwargs: Any
            ) -> ItemPaged[ElasticVersionListFormat]: ...


    class azure.mgmt.elastic.operations.ExternalUserOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ExternalUserInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExternalUserCreationResponse: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ExternalUserInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExternalUserCreationResponse: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExternalUserCreationResponse: ...


    class azure.mgmt.elastic.operations.ListAssociatedTrafficFiltersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ElasticTrafficFilterResponse: ...


    class azure.mgmt.elastic.operations.MonitorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ElasticMonitorUpgrade] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ElasticMonitorUpgrade] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.elastic.operations.MonitoredResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MonitoredResource]: ...


    class azure.mgmt.elastic.operations.MonitoredSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_createor_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        def begin_createor_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        def begin_createor_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> MonitoredSubscriptionProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MonitoredSubscriptionProperties]: ...


    class azure.mgmt.elastic.operations.MonitorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ElasticMonitorResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticMonitorResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ElasticMonitorResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticMonitorResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticMonitorResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ElasticMonitorResourceUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticMonitorResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ElasticMonitorResourceUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticMonitorResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticMonitorResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ElasticMonitorResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ElasticMonitorResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ElasticMonitorResource]: ...


    class azure.mgmt.elastic.operations.OpenAIOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                integration_name: str, 
                body: Optional[OpenAIIntegrationRPModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OpenAIIntegrationRPModel: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                integration_name: str, 
                body: Optional[OpenAIIntegrationRPModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OpenAIIntegrationRPModel: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                integration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OpenAIIntegrationRPModel: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                integration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                integration_name: str, 
                **kwargs: Any
            ) -> OpenAIIntegrationRPModel: ...

        @distributed_trace
        def get_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                integration_name: str, 
                **kwargs: Any
            ) -> OpenAIIntegrationStatusResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OpenAIIntegrationRPModel]: ...


    class azure.mgmt.elastic.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationResult]: ...


    class azure.mgmt.elastic.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ResubscribeProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticMonitorResource]: ...

        @overload
        def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ResubscribeProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticMonitorResource]: ...

        @overload
        def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticMonitorResource]: ...

        @overload
        def get_api_key(
                self, 
                body: Optional[UserEmailId] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserApiKeyResponse: ...

        @overload
        def get_api_key(
                self, 
                body: Optional[UserEmailId] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserApiKeyResponse: ...

        @overload
        def get_api_key(
                self, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserApiKeyResponse: ...

        @distributed_trace
        def get_elastic_to_azure_subscription_mapping(self, **kwargs: Any) -> ElasticOrganizationToAzureSubscriptionMappingResponse: ...


    class azure.mgmt.elastic.operations.TagRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                body: Optional[MonitoringTagRules] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                body: Optional[MonitoringTagRules] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MonitoringTagRules]: ...


    class azure.mgmt.elastic.operations.TrafficFiltersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                ruleset_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.elastic.operations.UpgradableVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def details(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> UpgradableVersionsList: ...


    class azure.mgmt.elastic.operations.VMCollectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[VMCollectionUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[VMCollectionUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.elastic.operations.VMHostOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VMResources]: ...


    class azure.mgmt.elastic.operations.VMIngestionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def details(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> VMIngestionDetailsResponse: ...


namespace azure.mgmt.elastic.types

    class azure.mgmt.elastic.types.BillingInfoResponse(TypedDict, total=False):
        key "marketplaceSaasInfo": ForwardRef('MarketplaceSaaSInfo', module='types')
        key "partnerBillingEntity": ForwardRef('PartnerBillingEntity', module='types')
        marketplace_saas_info: MarketplaceSaaSInfo
        partner_billing_entity: PartnerBillingEntity


    class azure.mgmt.elastic.types.CompanyInfo(TypedDict, total=False):
        key "business": str
        key "country": str
        key "domain": str
        key "employeesNumber": str
        key "state": str
        business: str
        country: str
        domain: str
        employees_number: str
        state: str


    class azure.mgmt.elastic.types.ConnectedPartnerResourceProperties(TypedDict, total=False):
        key "azureResourceId": str
        key "location": str
        key "partnerDeploymentName": str
        key "partnerDeploymentUri": str
        key "type": str
        azure_resource_id: str
        location: str
        partner_deployment_name: str
        partner_deployment_uri: str
        type: str


    class azure.mgmt.elastic.types.ConnectedPartnerResourcesListFormat(TypedDict, total=False):
        key "properties": ForwardRef('ConnectedPartnerResourceProperties', module='types')
        properties: ConnectedPartnerResourceProperties


    class azure.mgmt.elastic.types.DeploymentInfoResponse(TypedDict, total=False):
        key "configurationType": str
        key "deploymentUrl": str
        key "diskCapacity": str
        key "elasticsearchEndPoint": str
        key "marketplaceSaasInfo": ForwardRef('MarketplaceSaaSInfo', module='types')
        key "memoryCapacity": str
        key "projectType": str
        key "status": Union[str, ElasticDeploymentStatus]
        key "version": str
        configuration_type: str
        deployment_url: str
        disk_capacity: str
        elasticsearch_end_point: str
        marketplace_saas_info: MarketplaceSaaSInfo
        memory_capacity: str
        project_type: str
        status: Union[str, ElasticDeploymentStatus]
        version: str


    class azure.mgmt.elastic.types.ElasticCloudDeployment(TypedDict, total=False):
        key "azureSubscriptionId": str
        key "deploymentId": str
        key "elasticsearchRegion": str
        key "elasticsearchServiceUrl": str
        key "kibanaServiceUrl": str
        key "kibanaSsoUrl": str
        key "name": str
        azure_subscription_id: str
        deployment_id: str
        elasticsearch_region: str
        elasticsearch_service_url: str
        kibana_service_url: str
        kibana_sso_url: str
        name: str


    class azure.mgmt.elastic.types.ElasticCloudUser(TypedDict, total=False):
        key "elasticCloudSsoDefaultUrl": str
        key "emailAddress": str
        key "id": str
        elastic_cloud_sso_default_url: str
        email_address: str
        id: str


    class azure.mgmt.elastic.types.ElasticMonitorResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "kind": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('MonitorProperties', module='types')
        key "sku": ForwardRef('ResourceSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityProperties
        kind: str
        location: str
        name: str
        properties: MonitorProperties
        sku: ResourceSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.elastic.types.ElasticMonitorResourceUpdateParameters(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.elastic.types.ElasticMonitorUpgrade(TypedDict, total=False):
        key "version": str
        version: str


    class azure.mgmt.elastic.types.ElasticOrganizationToAzureSubscriptionMappingResponse(TypedDict, total=False):
        key "properties": ForwardRef('ElasticOrganizationToAzureSubscriptionMappingResponseProperties', module='types')
        properties: ElasticOrganizationToAzureSubscriptionMappingResponseProperties


    class azure.mgmt.elastic.types.ElasticOrganizationToAzureSubscriptionMappingResponseProperties(TypedDict, total=False):
        key "billedAzureSubscriptionId": str
        key "elasticOrganizationId": str
        key "elasticOrganizationName": str
        key "marketplaceSaasInfo": ForwardRef('MarketplaceSaaSInfo', module='types')
        billed_azure_subscription_id: str
        elastic_organization_id: str
        elastic_organization_name: str
        marketplace_saas_info: MarketplaceSaaSInfo


    class azure.mgmt.elastic.types.ElasticProperties(TypedDict, total=False):
        key "elasticCloudDeployment": ForwardRef('ElasticCloudDeployment', module='types')
        key "elasticCloudUser": ForwardRef('ElasticCloudUser', module='types')
        elastic_cloud_deployment: ElasticCloudDeployment
        elastic_cloud_user: ElasticCloudUser


    class azure.mgmt.elastic.types.ElasticTrafficFilter(TypedDict, total=False):
        key "description": str
        key "id": str
        key "includeByDefault": bool
        key "name": str
        key "region": str
        key "type": Union[str, Type]
        description: str
        id: str
        include_by_default: bool
        name: str
        region: str
        rules: list[ElasticTrafficFilterRule]
        type: Union[str, Type]


    class azure.mgmt.elastic.types.ElasticTrafficFilterResponse(TypedDict, total=False):
        rulesets: list[ElasticTrafficFilter]


    class azure.mgmt.elastic.types.ElasticTrafficFilterRule(TypedDict, total=False):
        key "azureEndpointGuid": str
        key "azureEndpointName": str
        key "description": str
        key "id": str
        key "source": str
        azure_endpoint_guid: str
        azure_endpoint_name: str
        description: str
        id: str
        source: str


    class azure.mgmt.elastic.types.ElasticVersionListFormat(TypedDict, total=False):
        key "properties": ForwardRef('ElasticVersionListProperties', module='types')
        properties: ElasticVersionListProperties


    class azure.mgmt.elastic.types.ElasticVersionListProperties(TypedDict, total=False):
        key "version": str
        version: str


    class azure.mgmt.elastic.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.elastic.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.elastic.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.elastic.types.ErrorResponseBody(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        code: str
        details: list[ErrorResponseBody]
        message: str
        target: str


    class azure.mgmt.elastic.types.ExternalUserCreationResponse(TypedDict, total=False):
        key "created": bool
        created: bool


    class azure.mgmt.elastic.types.ExternalUserInfo(TypedDict, total=False):
        key "emailId": str
        key "fullName": str
        key "password": str
        key "userName": str
        email_id: str
        full_name: str
        password: str
        roles: list[str]
        user_name: str


    class azure.mgmt.elastic.types.FilteringTag(TypedDict, total=False):
        key "action": Union[str, TagAction]
        key "name": str
        key "value": str
        action: Union[str, TagAction]
        name: str
        value: str


    class azure.mgmt.elastic.types.IdentityProperties(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ManagedIdentityTypes]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedIdentityTypes]


    class azure.mgmt.elastic.types.LogRules(TypedDict, total=False):
        key "sendAadLogs": bool
        key "sendActivityLogs": bool
        key "sendSubscriptionLogs": bool
        filteringTags: list[FilteringTag]
        filtering_tags: list[FilteringTag]
        send_aad_logs: bool
        send_activity_logs: bool
        send_subscription_logs: bool


    class azure.mgmt.elastic.types.MarketplaceSaaSInfo(TypedDict, total=False):
        key "billedAzureSubscriptionId": str
        key "marketplaceName": str
        key "marketplaceResourceId": str
        key "marketplaceStatus": str
        key "marketplaceSubscription": ForwardRef('MarketplaceSaaSInfoMarketplaceSubscription', module='types')
        key "subscribed": bool
        billed_azure_subscription_id: str
        marketplace_name: str
        marketplace_resource_id: str
        marketplace_status: str
        marketplace_subscription: MarketplaceSaaSInfoMarketplaceSubscription
        subscribed: bool


    class azure.mgmt.elastic.types.MarketplaceSaaSInfoMarketplaceSubscription(TypedDict, total=False):
        key "id": str
        key "offerId": str
        key "publisherId": str
        id: str
        offer_id: str
        publisher_id: str


    class azure.mgmt.elastic.types.MonitorProperties(TypedDict, total=False):
        key "elasticProperties": ForwardRef('ElasticProperties', module='types')
        key "generateApiKey": bool
        key "hostingType": Union[str, HostingType]
        key "liftrResourceCategory": Union[str, LiftrResourceCategories]
        key "liftrResourcePreference": int
        key "monitoringStatus": Union[str, MonitoringStatus]
        key "planDetails": ForwardRef('PlanDetails', module='types')
        key "projectDetails": ForwardRef('ProjectDetails', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "saaSAzureSubscriptionStatus": str
        key "sourceCampaignId": str
        key "sourceCampaignName": str
        key "subscriptionState": str
        key "userInfo": ForwardRef('UserInfo', module='types')
        key "version": str
        elastic_properties: ElasticProperties
        generate_api_key: bool
        hosting_type: Union[str, HostingType]
        liftr_resource_category: Union[str, LiftrResourceCategories]
        liftr_resource_preference: int
        monitoring_status: Union[str, MonitoringStatus]
        plan_details: PlanDetails
        project_details: ProjectDetails
        provisioning_state: Union[str, ProvisioningState]
        saa_s_azure_subscription_status: str
        source_campaign_id: str
        source_campaign_name: str
        subscription_state: str
        user_info: UserInfo
        version: str


    class azure.mgmt.elastic.types.MonitoredResource(TypedDict, total=False):
        key "id": str
        key "reasonForLogsStatus": str
        key "sendingLogs": Union[str, SendingLogs]
        id: str
        reason_for_logs_status: str
        sending_logs: Union[str, SendingLogs]


    class azure.mgmt.elastic.types.MonitoredSubscription(TypedDict, total=False):
        key "error": str
        key "status": Union[str, Status]
        key "subscriptionId": Required[str]
        key "tagRules": ForwardRef('MonitoringTagRulesProperties', module='types')
        error: str
        status: Union[str, Status]
        subscription_id: str
        tag_rules: MonitoringTagRulesProperties


    class azure.mgmt.elastic.types.MonitoredSubscriptionProperties(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SubscriptionList', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SubscriptionList
        system_data: SystemData
        type: str


    class azure.mgmt.elastic.types.MonitoringTagRules(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('MonitoringTagRulesProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MonitoringTagRulesProperties
        system_data: SystemData
        type: str


    class azure.mgmt.elastic.types.MonitoringTagRulesProperties(TypedDict, total=False):
        key "logRules": ForwardRef('LogRules', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        log_rules: LogRules
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.elastic.types.OpenAIIntegrationProperties(TypedDict, total=False):
        key "key": str
        key "lastRefreshAt": str
        key "openAIConnectorId": str
        key "openAIResourceEndpoint": str
        key "openAIResourceId": str
        key: str
        last_refresh_at: str
        open_ai_connector_id: str
        open_ai_resource_endpoint: str
        open_ai_resource_id: str


    class azure.mgmt.elastic.types.OpenAIIntegrationRPModel(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('OpenAIIntegrationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: OpenAIIntegrationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.elastic.types.OpenAIIntegrationStatusResponse(TypedDict, total=False):
        key "properties": ForwardRef('OpenAIIntegrationStatusResponseProperties', module='types')
        properties: OpenAIIntegrationStatusResponseProperties


    class azure.mgmt.elastic.types.OpenAIIntegrationStatusResponseProperties(TypedDict, total=False):
        key "status": str
        status: str


    class azure.mgmt.elastic.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.elastic.types.OperationResult(TypedDict, total=False):
        key "display": ForwardRef('OperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        key "origin": str
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: str


    class azure.mgmt.elastic.types.PartnerBillingEntity(TypedDict, total=False):
        key "id": str
        key "name": str
        key "partnerEntityUri": str
        id: str
        name: str
        partner_entity_uri: str


    class azure.mgmt.elastic.types.PlanDetails(TypedDict, total=False):
        key "offerID": str
        key "planID": str
        key "planName": str
        key "publisherID": str
        key "termID": str
        offer_id: str
        plan_id: str
        plan_name: str
        publisher_id: str
        term_id: str


    class azure.mgmt.elastic.types.ProjectDetails(TypedDict, total=False):
        key "configurationType": Union[str, ConfigurationType]
        key "projectType": Union[str, ProjectType]
        configuration_type: Union[str, ConfigurationType]
        project_type: Union[str, ProjectType]


    class azure.mgmt.elastic.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.elastic.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.elastic.types.ResourceProviderDefaultErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorResponseBody', module='types')
        error: ErrorResponseBody


    class azure.mgmt.elastic.types.ResourceSku(TypedDict, total=False):
        key "name": Required[str]
        name: str


    class azure.mgmt.elastic.types.ResubscribeProperties(TypedDict, total=False):
        key "organizationId": str
        key "planId": str
        key "resourceGroup": str
        key "subscriptionId": str
        key "term": str
        organization_id: str
        plan_id: str
        resource_group: str
        subscription_id: str
        term: str


    class azure.mgmt.elastic.types.SubscriptionList(TypedDict, total=False):
        key "operation": Union[str, Operation]
        key "provisioningState": Union[str, ProvisioningState]
        monitoredSubscriptionList: list[MonitoredSubscription]
        monitored_subscription_list: list[MonitoredSubscription]
        operation: Union[str, Operation]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.elastic.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.elastic.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.elastic.types.UpgradableVersionsList(TypedDict, total=False):
        key "currentVersion": str
        current_version: str
        upgradableVersions: list[str]
        upgradable_versions: list[str]


    class azure.mgmt.elastic.types.UserApiKeyResponse(TypedDict, total=False):
        key "properties": ForwardRef('UserApiKeyResponseProperties', module='types')
        properties: UserApiKeyResponseProperties


    class azure.mgmt.elastic.types.UserApiKeyResponseProperties(TypedDict, total=False):
        key "apiKey": str
        api_key: str


    class azure.mgmt.elastic.types.UserEmailId(TypedDict, total=False):
        key "emailId": str
        email_id: str


    class azure.mgmt.elastic.types.UserInfo(TypedDict, total=False):
        key "companyInfo": ForwardRef('CompanyInfo', module='types')
        key "companyName": str
        key "emailAddress": str
        key "firstName": str
        key "lastName": str
        company_info: CompanyInfo
        company_name: str
        email_address: str
        first_name: str
        last_name: str


    class azure.mgmt.elastic.types.VMCollectionUpdate(TypedDict, total=False):
        key "operationName": Union[str, OperationName]
        key "vmResourceId": str
        operation_name: Union[str, OperationName]
        vm_resource_id: str


    class azure.mgmt.elastic.types.VMIngestionDetailsResponse(TypedDict, total=False):
        key "cloudId": str
        key "ingestionKey": str
        cloud_id: str
        ingestion_key: str


    class azure.mgmt.elastic.types.VMResources(TypedDict, total=False):
        key "vmResourceId": str
        vm_resource_id: str


```