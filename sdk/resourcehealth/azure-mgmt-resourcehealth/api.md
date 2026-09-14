```py
namespace azure.mgmt.resourcehealth

    class azure.mgmt.resourcehealth.ResourceHealthMgmtClient: implements ContextManager 
        availability_statuses: AvailabilityStatusesOperations
        child_availability_statuses: ChildAvailabilityStatusesOperations
        child_resources: ChildResourcesOperations
        emerging_issues: EmergingIssuesOperations
        event: EventOperations
        events: EventsOperations
        impacted_resources: ImpactedResourcesOperations
        metadata: MetadataOperations
        operations: Operations
        security_advisory_impacted_resources: SecurityAdvisoryImpactedResourcesOperations

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


namespace azure.mgmt.resourcehealth.aio

    class azure.mgmt.resourcehealth.aio.ResourceHealthMgmtClient: implements AsyncContextManager 
        availability_statuses: AvailabilityStatusesOperations
        child_availability_statuses: ChildAvailabilityStatusesOperations
        child_resources: ChildResourcesOperations
        emerging_issues: EmergingIssuesOperations
        event: EventOperations
        events: EventsOperations
        impacted_resources: ImpactedResourcesOperations
        metadata: MetadataOperations
        operations: Operations
        security_advisory_impacted_resources: SecurityAdvisoryImpactedResourcesOperations

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


namespace azure.mgmt.resourcehealth.aio.operations

    class azure.mgmt.resourcehealth.aio.operations.AvailabilityStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_resource(
                self, 
                resource_uri: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AvailabilityStatus: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AvailabilityStatus]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AvailabilityStatus]: ...

        @distributed_trace
        def list_by_subscription_id(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AvailabilityStatus]: ...


    class azure.mgmt.resourcehealth.aio.operations.ChildAvailabilityStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_resource(
                self, 
                resource_uri: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AvailabilityStatus: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AvailabilityStatus]: ...


    class azure.mgmt.resourcehealth.aio.operations.ChildResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AvailabilityStatus]: ...


    class azure.mgmt.resourcehealth.aio.operations.EmergingIssuesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                issue_name: Union[str, IssueNameParameter], 
                **kwargs: Any
            ) -> EmergingIssuesGetResult: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[EmergingIssuesGetResult]: ...


    class azure.mgmt.resourcehealth.aio.operations.EventOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def fetch_billling_communication_details_by_subscription_id_and_tracking_id(
                self, 
                event_tracking_id: str, 
                **kwargs: Any
            ) -> Event: ...

        @distributed_trace_async
        async def fetch_details_by_subscription_id_and_tracking_id(
                self, 
                event_tracking_id: str, 
                **kwargs: Any
            ) -> Event: ...

        @distributed_trace_async
        async def fetch_details_by_tenant_id_and_tracking_id(
                self, 
                event_tracking_id: str, 
                **kwargs: Any
            ) -> Event: ...

        @distributed_trace_async
        async def get_by_subscription_id_and_tracking_id(
                self, 
                event_tracking_id: str, 
                *, 
                filter: Optional[str] = ..., 
                query_start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> Event: ...

        @distributed_trace_async
        async def get_by_tenant_id_and_tracking_id(
                self, 
                event_tracking_id: str, 
                *, 
                filter: Optional[str] = ..., 
                query_start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> Event: ...


    class azure.mgmt.resourcehealth.aio.operations.EventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_single_resource(
                self, 
                resource_uri: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Event]: ...

        @distributed_trace
        def list_by_subscription_id(
                self, 
                *, 
                filter: Optional[str] = ..., 
                query_start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Event]: ...

        @distributed_trace
        def list_by_tenant_id(
                self, 
                *, 
                filter: Optional[str] = ..., 
                query_start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Event]: ...


    class azure.mgmt.resourcehealth.aio.operations.ImpactedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                event_tracking_id: str, 
                impacted_resource_name: str, 
                **kwargs: Any
            ) -> EventImpactedResource: ...

        @distributed_trace_async
        async def get_by_tenant_id(
                self, 
                event_tracking_id: str, 
                impacted_resource_name: str, 
                **kwargs: Any
            ) -> EventImpactedResource: ...

        @distributed_trace
        def list_by_subscription_id_and_event_id(
                self, 
                event_tracking_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventImpactedResource]: ...

        @distributed_trace
        def list_by_tenant_id_and_event_id(
                self, 
                event_tracking_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventImpactedResource]: ...


    class azure.mgmt.resourcehealth.aio.operations.MetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_entity(
                self, 
                name: str, 
                **kwargs: Any
            ) -> MetadataEntity: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[MetadataEntity]: ...


    class azure.mgmt.resourcehealth.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(self, **kwargs: Any) -> OperationListResult: ...


    class azure.mgmt.resourcehealth.aio.operations.SecurityAdvisoryImpactedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_subscription_id_and_event_id(
                self, 
                event_tracking_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventImpactedResource]: ...

        @distributed_trace
        def list_by_tenant_id_and_event_id(
                self, 
                event_tracking_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventImpactedResource]: ...


namespace azure.mgmt.resourcehealth.models

    class azure.mgmt.resourcehealth.models.AvailabilityStateValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        DEGRADED = "Degraded"
        UNAVAILABLE = "Unavailable"
        UNKNOWN = "Unknown"


    class azure.mgmt.resourcehealth.models.AvailabilityStatus(ProxyResourceAutoGenerated):
        id: str
        location: str
        name: str
        properties: Optional[AvailabilityStatusProperties]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[AvailabilityStatusProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.AvailabilityStatusProperties(_Model):
        article_id: Optional[str]
        availability_state: Optional[Union[str, AvailabilityStateValues]]
        category: Optional[str]
        context: Optional[str]
        detailed_status: Optional[str]
        health_event_category: Optional[str]
        health_event_cause: Optional[str]
        health_event_id: Optional[str]
        health_event_type: Optional[str]
        occured_time: Optional[datetime]
        reason_chronicity: Optional[Union[str, ReasonChronicityTypes]]
        reason_type: Optional[str]
        recently_resolved: Optional[AvailabilityStatusPropertiesRecentlyResolved]
        recommended_actions: Optional[list[RecommendedAction]]
        reported_time: Optional[datetime]
        resolution_eta: Optional[datetime]
        root_cause_attribution_time: Optional[datetime]
        service_impacting_events: Optional[list[ServiceImpactingEvent]]
        summary: Optional[str]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                article_id: Optional[str] = ..., 
                availability_state: Optional[Union[str, AvailabilityStateValues]] = ..., 
                category: Optional[str] = ..., 
                context: Optional[str] = ..., 
                detailed_status: Optional[str] = ..., 
                health_event_category: Optional[str] = ..., 
                health_event_cause: Optional[str] = ..., 
                health_event_id: Optional[str] = ..., 
                health_event_type: Optional[str] = ..., 
                occured_time: Optional[datetime] = ..., 
                reason_chronicity: Optional[Union[str, ReasonChronicityTypes]] = ..., 
                reason_type: Optional[str] = ..., 
                recently_resolved: Optional[AvailabilityStatusPropertiesRecentlyResolved] = ..., 
                recommended_actions: Optional[list[RecommendedAction]] = ..., 
                reported_time: Optional[datetime] = ..., 
                resolution_eta: Optional[datetime] = ..., 
                root_cause_attribution_time: Optional[datetime] = ..., 
                service_impacting_events: Optional[list[ServiceImpactingEvent]] = ..., 
                summary: Optional[str] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.AvailabilityStatusPropertiesRecentlyResolved(_Model):
        resolved_time: Optional[datetime]
        unavailable_occured_time: Optional[datetime]
        unavailable_summary: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resolved_time: Optional[datetime] = ..., 
                unavailable_occured_time: Optional[datetime] = ..., 
                unavailable_summary: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resourcehealth.models.EmergingIssue(_Model):
        refresh_timestamp: Optional[datetime]
        status_active_events: Optional[list[StatusActiveEvent]]
        status_banners: Optional[list[StatusBanner]]

        @overload
        def __init__(
                self, 
                *, 
                refresh_timestamp: Optional[datetime] = ..., 
                status_active_events: Optional[list[StatusActiveEvent]] = ..., 
                status_banners: Optional[list[StatusBanner]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.EmergingIssueImpact(_Model):
        id: Optional[str]
        name: Optional[str]
        regions: Optional[list[ImpactedRegion]]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                regions: Optional[list[ImpactedRegion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.EmergingIssuesGetResult(ProxyResource):
        id: str
        name: str
        properties: Optional[EmergingIssue]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EmergingIssue] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resourcehealth.models.ErrorResponse(_Model):
        code: Optional[str]
        details: Optional[str]
        message: Optional[str]


    class azure.mgmt.resourcehealth.models.Event(ProxyResource):
        id: str
        name: str
        properties: Optional[EventProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EventProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resourcehealth.models.EventImpactedResource(ProxyResource):
        id: str
        name: str
        properties: Optional[EventImpactedResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EventImpactedResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resourcehealth.models.EventImpactedResourceProperties(_Model):
        info: Optional[list[KeyValueItem]]
        target_region: Optional[str]
        target_resource_id: Optional[str]
        target_resource_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                info: Optional[list[KeyValueItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.EventLevelValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        ERROR = "Error"
        INFORMATIONAL = "Informational"
        WARNING = "Warning"


    class azure.mgmt.resourcehealth.models.EventProperties(_Model):
        additional_information: Optional[EventPropertiesAdditionalInformation]
        article: Optional[EventPropertiesArticle]
        billing_id: Optional[str]
        currency_type: Optional[str]
        description: Optional[str]
        duration: Optional[int]
        enable_chat_with_us: Optional[bool]
        enable_microsoft_support: Optional[bool]
        event_level: Optional[Union[str, EventLevelValues]]
        event_source: Optional[Union[str, EventSourceValues]]
        event_sub_type: Optional[Union[str, EventSubTypeValues]]
        event_tags: Optional[list[str]]
        event_type: Optional[Union[str, EventTypeValues]]
        external_incident_id: Optional[str]
        faqs: Optional[list[Faq]]
        header: Optional[str]
        hir_stage: Optional[str]
        impact: Optional[list[Impact]]
        impact_mitigation_time: Optional[datetime]
        impact_start_time: Optional[datetime]
        impact_type: Optional[str]
        is_event_sensitive: Optional[bool]
        is_hir: Optional[bool]
        last_update_time: Optional[datetime]
        level: Optional[Union[str, LevelValues]]
        links: Optional[list[Link]]
        new_rate: Optional[float]
        old_rate: Optional[float]
        platform_initiated: Optional[bool]
        priority: Optional[int]
        reason: Optional[str]
        recommended_actions: Optional[EventPropertiesRecommendedActions]
        status: Optional[Union[str, EventStatusValues]]
        summary: Optional[str]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_information: Optional[EventPropertiesAdditionalInformation] = ..., 
                article: Optional[EventPropertiesArticle] = ..., 
                billing_id: Optional[str] = ..., 
                currency_type: Optional[str] = ..., 
                description: Optional[str] = ..., 
                duration: Optional[int] = ..., 
                enable_chat_with_us: Optional[bool] = ..., 
                enable_microsoft_support: Optional[bool] = ..., 
                event_level: Optional[Union[str, EventLevelValues]] = ..., 
                event_source: Optional[Union[str, EventSourceValues]] = ..., 
                event_sub_type: Optional[Union[str, EventSubTypeValues]] = ..., 
                event_tags: Optional[list[str]] = ..., 
                event_type: Optional[Union[str, EventTypeValues]] = ..., 
                external_incident_id: Optional[str] = ..., 
                faqs: Optional[list[Faq]] = ..., 
                header: Optional[str] = ..., 
                hir_stage: Optional[str] = ..., 
                impact: Optional[list[Impact]] = ..., 
                impact_mitigation_time: Optional[datetime] = ..., 
                impact_start_time: Optional[datetime] = ..., 
                impact_type: Optional[str] = ..., 
                is_event_sensitive: Optional[bool] = ..., 
                is_hir: Optional[bool] = ..., 
                last_update_time: Optional[datetime] = ..., 
                level: Optional[Union[str, LevelValues]] = ..., 
                links: Optional[list[Link]] = ..., 
                new_rate: Optional[float] = ..., 
                old_rate: Optional[float] = ..., 
                platform_initiated: Optional[bool] = ..., 
                priority: Optional[int] = ..., 
                reason: Optional[str] = ..., 
                recommended_actions: Optional[EventPropertiesRecommendedActions] = ..., 
                status: Optional[Union[str, EventStatusValues]] = ..., 
                summary: Optional[str] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.EventPropertiesAdditionalInformation(_Model):
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.EventPropertiesArticle(_Model):
        article_content: Optional[str]
        article_id: Optional[str]
        parameters: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                article_content: Optional[str] = ..., 
                article_id: Optional[str] = ..., 
                parameters: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.EventPropertiesRecommendedActions(_Model):
        actions: Optional[list[EventPropertiesRecommendedActionsItem]]
        locale_code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[EventPropertiesRecommendedActionsItem]] = ..., 
                locale_code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.EventPropertiesRecommendedActionsItem(_Model):
        action_text: Optional[str]
        group_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                action_text: Optional[str] = ..., 
                group_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.EventSourceValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESOURCE_HEALTH = "ResourceHealth"
        SERVICE_HEALTH = "ServiceHealth"


    class azure.mgmt.resourcehealth.models.EventStatusValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        RESOLVED = "Resolved"


    class azure.mgmt.resourcehealth.models.EventSubTypeValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOREIGN_EXCHANGE_RATE_CHANGE = "ForeignExchangeRateChange"
        METER_ID_CHANGES = "MeterIDChanges"
        OVERBILLING = "Overbilling"
        PRICE_CHANGES = "PriceChanges"
        RETIREMENT = "Retirement"
        TAX_CHANGES = "TaxChanges"
        UNAUTHORIZED_PARTY_ABUSE = "UnauthorizedPartyAbuse"
        UNDERBILLING = "Underbilling"


    class azure.mgmt.resourcehealth.models.EventTypeValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BILLING = "Billing"
        EMERGING_ISSUES = "EmergingIssues"
        HEALTH_ADVISORY = "HealthAdvisory"
        PLANNED_MAINTENANCE = "PlannedMaintenance"
        RCA = "RCA"
        SECURITY_ADVISORY = "SecurityAdvisory"
        SERVICE_ISSUE = "ServiceIssue"


    class azure.mgmt.resourcehealth.models.Faq(_Model):
        answer: Optional[str]
        locale_code: Optional[str]
        question: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                answer: Optional[str] = ..., 
                locale_code: Optional[str] = ..., 
                question: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.Impact(_Model):
        impacted_regions: Optional[list[ImpactedServiceRegion]]
        impacted_service: Optional[str]
        impacted_service_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                impacted_regions: Optional[list[ImpactedServiceRegion]] = ..., 
                impacted_service: Optional[str] = ..., 
                impacted_service_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.ImpactedRegion(_Model):
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.ImpactedServiceRegion(_Model):
        impacted_region: Optional[str]
        impacted_subscriptions: Optional[list[str]]
        impacted_tenants: Optional[list[str]]
        last_update_time: Optional[datetime]
        status: Optional[Union[str, EventStatusValues]]
        updates: Optional[list[Update]]

        @overload
        def __init__(
                self, 
                *, 
                impacted_region: Optional[str] = ..., 
                impacted_subscriptions: Optional[list[str]] = ..., 
                impacted_tenants: Optional[list[str]] = ..., 
                last_update_time: Optional[datetime] = ..., 
                status: Optional[Union[str, EventStatusValues]] = ..., 
                updates: Optional[list[Update]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.IssueNameParameter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.resourcehealth.models.KeyValueItem(_Model):
        key: Optional[str]
        value: Optional[str]


    class azure.mgmt.resourcehealth.models.LevelValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        WARNING = "Warning"


    class azure.mgmt.resourcehealth.models.Link(_Model):
        blade_name: Optional[str]
        display_text: Optional[LinkDisplayText]
        extension_name: Optional[str]
        parameters: Optional[Any]
        type: Optional[Union[str, LinkTypeValues]]

        @overload
        def __init__(
                self, 
                *, 
                blade_name: Optional[str] = ..., 
                display_text: Optional[LinkDisplayText] = ..., 
                extension_name: Optional[str] = ..., 
                parameters: Optional[Any] = ..., 
                type: Optional[Union[str, LinkTypeValues]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.LinkDisplayText(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.LinkTypeValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUTTON = "Button"
        HYPERLINK = "Hyperlink"


    class azure.mgmt.resourcehealth.models.MetadataEntity(ProxyResource):
        id: str
        name: str
        properties: Optional[MetadataEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MetadataEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resourcehealth.models.MetadataEntityProperties(_Model):
        applicable_scenarios: Optional[list[Union[str, Scenario]]]
        depends_on: Optional[list[str]]
        display_name: Optional[str]
        supported_values: Optional[list[MetadataSupportedValueDetail]]

        @overload
        def __init__(
                self, 
                *, 
                applicable_scenarios: Optional[list[Union[str, Scenario]]] = ..., 
                depends_on: Optional[list[str]] = ..., 
                display_name: Optional[str] = ..., 
                supported_values: Optional[list[MetadataSupportedValueDetail]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.MetadataSupportedValueDetail(_Model):
        display_name: Optional[str]
        id: Optional[str]
        previous_id: Optional[str]
        priority: Optional[int]
        resource_types: Optional[list[str]]
        service_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                previous_id: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                resource_types: Optional[list[str]] = ..., 
                service_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.OperationDisplay(_Model):
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


    class azure.mgmt.resourcehealth.models.OperationListResult(_Model):
        value: list[Operation]

        @overload
        def __init__(
                self, 
                *, 
                value: list[Operation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.resourcehealth.models.ProxyResourceAutoGenerated(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.ReasonChronicityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERSISTENT = "Persistent"
        TRANSIENT = "Transient"


    class azure.mgmt.resourcehealth.models.RecommendedAction(_Model):
        action: Optional[str]
        action_url: Optional[str]
        action_url_comment: Optional[str]
        action_url_text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[str] = ..., 
                action_url: Optional[str] = ..., 
                action_url_comment: Optional[str] = ..., 
                action_url_text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.resourcehealth.models.Scenario(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS = "Alerts"


    class azure.mgmt.resourcehealth.models.ServiceImpactingEvent(_Model):
        correlation_id: Optional[str]
        event_start_time: Optional[datetime]
        event_status_last_modified_time: Optional[datetime]
        incident_properties: Optional[ServiceImpactingEventIncidentProperties]
        status: Optional[ServiceImpactingEventStatus]

        @overload
        def __init__(
                self, 
                *, 
                correlation_id: Optional[str] = ..., 
                event_start_time: Optional[datetime] = ..., 
                event_status_last_modified_time: Optional[datetime] = ..., 
                incident_properties: Optional[ServiceImpactingEventIncidentProperties] = ..., 
                status: Optional[ServiceImpactingEventStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.ServiceImpactingEventIncidentProperties(_Model):
        incident_type: Optional[str]
        region: Optional[str]
        service: Optional[str]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                incident_type: Optional[str] = ..., 
                region: Optional[str] = ..., 
                service: Optional[str] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.ServiceImpactingEventStatus(_Model):
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.SeverityValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFORMATION = "Information"
        WARNING = "Warning"


    class azure.mgmt.resourcehealth.models.StageValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        ARCHIVED = "Archived"
        RESOLVE = "Resolve"


    class azure.mgmt.resourcehealth.models.StatusActiveEvent(_Model):
        cloud: Optional[str]
        description: Optional[str]
        impacts: Optional[list[EmergingIssueImpact]]
        last_modified_time: Optional[datetime]
        published: Optional[bool]
        severity: Optional[Union[str, SeverityValues]]
        stage: Optional[Union[str, StageValues]]
        start_time: Optional[datetime]
        title: Optional[str]
        tracking_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud: Optional[str] = ..., 
                description: Optional[str] = ..., 
                impacts: Optional[list[EmergingIssueImpact]] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                published: Optional[bool] = ..., 
                severity: Optional[Union[str, SeverityValues]] = ..., 
                stage: Optional[Union[str, StageValues]] = ..., 
                start_time: Optional[datetime] = ..., 
                title: Optional[str] = ..., 
                tracking_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.StatusBanner(_Model):
        cloud: Optional[str]
        last_modified_time: Optional[datetime]
        message: Optional[str]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcehealth.models.SystemData(_Model):
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


    class azure.mgmt.resourcehealth.models.Update(_Model):
        event_tags: Optional[list[str]]
        summary: Optional[str]
        update_date_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                event_tags: Optional[list[str]] = ..., 
                summary: Optional[str] = ..., 
                update_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.resourcehealth.operations

    class azure.mgmt.resourcehealth.operations.AvailabilityStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_resource(
                self, 
                resource_uri: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AvailabilityStatus: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AvailabilityStatus]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AvailabilityStatus]: ...

        @distributed_trace
        def list_by_subscription_id(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AvailabilityStatus]: ...


    class azure.mgmt.resourcehealth.operations.ChildAvailabilityStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_resource(
                self, 
                resource_uri: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AvailabilityStatus: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AvailabilityStatus]: ...


    class azure.mgmt.resourcehealth.operations.ChildResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AvailabilityStatus]: ...


    class azure.mgmt.resourcehealth.operations.EmergingIssuesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                issue_name: Union[str, IssueNameParameter], 
                **kwargs: Any
            ) -> EmergingIssuesGetResult: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[EmergingIssuesGetResult]: ...


    class azure.mgmt.resourcehealth.operations.EventOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def fetch_billling_communication_details_by_subscription_id_and_tracking_id(
                self, 
                event_tracking_id: str, 
                **kwargs: Any
            ) -> Event: ...

        @distributed_trace
        def fetch_details_by_subscription_id_and_tracking_id(
                self, 
                event_tracking_id: str, 
                **kwargs: Any
            ) -> Event: ...

        @distributed_trace
        def fetch_details_by_tenant_id_and_tracking_id(
                self, 
                event_tracking_id: str, 
                **kwargs: Any
            ) -> Event: ...

        @distributed_trace
        def get_by_subscription_id_and_tracking_id(
                self, 
                event_tracking_id: str, 
                *, 
                filter: Optional[str] = ..., 
                query_start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> Event: ...

        @distributed_trace
        def get_by_tenant_id_and_tracking_id(
                self, 
                event_tracking_id: str, 
                *, 
                filter: Optional[str] = ..., 
                query_start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> Event: ...


    class azure.mgmt.resourcehealth.operations.EventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_single_resource(
                self, 
                resource_uri: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Event]: ...

        @distributed_trace
        def list_by_subscription_id(
                self, 
                *, 
                filter: Optional[str] = ..., 
                query_start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Event]: ...

        @distributed_trace
        def list_by_tenant_id(
                self, 
                *, 
                filter: Optional[str] = ..., 
                query_start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Event]: ...


    class azure.mgmt.resourcehealth.operations.ImpactedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                event_tracking_id: str, 
                impacted_resource_name: str, 
                **kwargs: Any
            ) -> EventImpactedResource: ...

        @distributed_trace
        def get_by_tenant_id(
                self, 
                event_tracking_id: str, 
                impacted_resource_name: str, 
                **kwargs: Any
            ) -> EventImpactedResource: ...

        @distributed_trace
        def list_by_subscription_id_and_event_id(
                self, 
                event_tracking_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventImpactedResource]: ...

        @distributed_trace
        def list_by_tenant_id_and_event_id(
                self, 
                event_tracking_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventImpactedResource]: ...


    class azure.mgmt.resourcehealth.operations.MetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_entity(
                self, 
                name: str, 
                **kwargs: Any
            ) -> MetadataEntity: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[MetadataEntity]: ...


    class azure.mgmt.resourcehealth.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> OperationListResult: ...


    class azure.mgmt.resourcehealth.operations.SecurityAdvisoryImpactedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_subscription_id_and_event_id(
                self, 
                event_tracking_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventImpactedResource]: ...

        @distributed_trace
        def list_by_tenant_id_and_event_id(
                self, 
                event_tracking_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventImpactedResource]: ...


```