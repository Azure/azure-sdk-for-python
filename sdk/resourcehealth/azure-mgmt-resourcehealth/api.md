```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


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
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AvailabilityStatus: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AvailabilityStatus]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AvailabilityStatus]: ...

        @distributed_trace
        def list_by_subscription_id(
                self, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AvailabilityStatus]: ...


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
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AvailabilityStatus: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AvailabilityStatus]: ...


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
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AvailabilityStatus]: ...


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
        def list(self, **kwargs: Any) -> AsyncIterable[EmergingIssuesGetResult]: ...


    class azure.mgmt.resourcehealth.aio.operations.EventOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                filter: Optional[str] = None, 
                query_start_time: Optional[str] = None, 
                **kwargs: Any
            ) -> Event: ...

        @distributed_trace_async
        async def get_by_tenant_id_and_tracking_id(
                self, 
                event_tracking_id: str, 
                filter: Optional[str] = None, 
                query_start_time: Optional[str] = None, 
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
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Event]: ...

        @distributed_trace
        def list_by_subscription_id(
                self, 
                filter: Optional[str] = None, 
                query_start_time: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Event]: ...

        @distributed_trace
        def list_by_tenant_id(
                self, 
                filter: Optional[str] = None, 
                query_start_time: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Event]: ...


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
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[EventImpactedResource]: ...

        @distributed_trace
        def list_by_tenant_id_and_event_id(
                self, 
                event_tracking_id: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[EventImpactedResource]: ...


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
        def list(self, **kwargs: Any) -> AsyncIterable[MetadataEntity]: ...


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
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[EventImpactedResource]: ...

        @distributed_trace
        def list_by_tenant_id_and_event_id(
                self, 
                event_tracking_id: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[EventImpactedResource]: ...


namespace azure.mgmt.resourcehealth.models

    class azure.mgmt.resourcehealth.models.AvailabilityStateValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        DEGRADED = "Degraded"
        UNAVAILABLE = "Unavailable"
        UNKNOWN = "Unknown"


    class azure.mgmt.resourcehealth.models.AvailabilityStatus(Model):
        id: str
        location: str
        name: str
        properties: AvailabilityStatusProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[AvailabilityStatusProperties] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.AvailabilityStatusListResult(Model):
        next_link: str
        value: list[AvailabilityStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[AvailabilityStatus], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.AvailabilityStatusProperties(Model):
        article_id: str
        availability_state: Union[str, AvailabilityStateValues]
        category: str
        context: str
        detailed_status: str
        health_event_category: str
        health_event_cause: str
        health_event_id: str
        health_event_type: str
        occured_time: datetime
        reason_chronicity: Union[str, ReasonChronicityTypes]
        reason_type: str
        recently_resolved: AvailabilityStatusPropertiesRecentlyResolved
        recommended_actions: list[RecommendedAction]
        reported_time: datetime
        resolution_eta: datetime
        root_cause_attribution_time: datetime
        service_impacting_events: list[ServiceImpactingEvent]
        summary: str
        title: str

        def __eq__(self, other: Any) -> bool: ...

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
                recommended_actions: Optional[List[RecommendedAction]] = ..., 
                reported_time: Optional[datetime] = ..., 
                resolution_eta: Optional[datetime] = ..., 
                root_cause_attribution_time: Optional[datetime] = ..., 
                service_impacting_events: Optional[List[ServiceImpactingEvent]] = ..., 
                summary: Optional[str] = ..., 
                title: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.AvailabilityStatusPropertiesRecentlyResolved(Model):
        resolved_time: datetime
        unavailable_occured_time: datetime
        unavailable_summary: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resolved_time: Optional[datetime] = ..., 
                unavailable_occured_time: Optional[datetime] = ..., 
                unavailable_summary: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resourcehealth.models.EmergingIssueImpact(Model):
        id: str
        name: str
        regions: list[ImpactedRegion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                regions: Optional[List[ImpactedRegion]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.EmergingIssueListResult(Model):
        next_link: str
        value: list[EmergingIssuesGetResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[EmergingIssuesGetResult]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.EmergingIssuesGetResult(ProxyResource):
        id: str
        name: str
        refresh_timestamp: datetime
        status_active_events: list[StatusActiveEvent]
        status_banners: list[StatusBanner]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                refresh_timestamp: Optional[datetime] = ..., 
                status_active_events: Optional[List[StatusActiveEvent]] = ..., 
                status_banners: Optional[List[StatusBanner]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.ErrorResponse(Model):
        code: str
        details: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.Event(ProxyResource):
        additional_information: EventPropertiesAdditionalInformation
        arg_query: str
        article: EventPropertiesArticle
        description: str
        duration: int
        enable_chat_with_us: bool
        enable_microsoft_support: bool
        event_level: Union[str, EventLevelValues]
        event_source: Union[str, EventSourceValues]
        event_sub_type: Union[str, EventSubTypeValues]
        event_type: Union[str, EventTypeValues]
        external_incident_id: str
        faqs: list[Faq]
        header: str
        hir_stage: str
        id: str
        impact: list[Impact]
        impact_mitigation_time: datetime
        impact_start_time: datetime
        impact_type: str
        is_hir: bool
        last_update_time: datetime
        level: Union[str, LevelValues]
        links: list[Link]
        maintenance_id: str
        maintenance_type: str
        name: str
        platform_initiated: bool
        priority: int
        reason: str
        recommended_actions: EventPropertiesRecommendedActions
        status: Union[str, EventStatusValues]
        summary: str
        system_data: SystemData
        title: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_information: Optional[EventPropertiesAdditionalInformation] = ..., 
                arg_query: Optional[str] = ..., 
                article: Optional[EventPropertiesArticle] = ..., 
                description: Optional[str] = ..., 
                duration: Optional[int] = ..., 
                enable_chat_with_us: Optional[bool] = ..., 
                enable_microsoft_support: Optional[bool] = ..., 
                event_level: Optional[Union[str, EventLevelValues]] = ..., 
                event_source: Optional[Union[str, EventSourceValues]] = ..., 
                event_sub_type: Optional[Union[str, EventSubTypeValues]] = ..., 
                event_type: Optional[Union[str, EventTypeValues]] = ..., 
                external_incident_id: Optional[str] = ..., 
                faqs: Optional[List[Faq]] = ..., 
                header: Optional[str] = ..., 
                hir_stage: Optional[str] = ..., 
                impact: Optional[List[Impact]] = ..., 
                impact_mitigation_time: Optional[datetime] = ..., 
                impact_start_time: Optional[datetime] = ..., 
                impact_type: Optional[str] = ..., 
                is_hir: Optional[bool] = ..., 
                last_update_time: Optional[datetime] = ..., 
                level: Optional[Union[str, LevelValues]] = ..., 
                links: Optional[List[Link]] = ..., 
                maintenance_id: Optional[str] = ..., 
                maintenance_type: Optional[str] = ..., 
                platform_initiated: Optional[bool] = ..., 
                priority: Optional[int] = ..., 
                reason: Optional[str] = ..., 
                recommended_actions: Optional[EventPropertiesRecommendedActions] = ..., 
                status: Optional[Union[str, EventStatusValues]] = ..., 
                summary: Optional[str] = ..., 
                title: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.EventImpactedResource(ProxyResource):
        id: str
        info: list[KeyValueItem]
        maintenance_end_time: str
        maintenance_start_time: str
        name: str
        resource_group: str
        resource_name: str
        status: str
        system_data: SystemData
        target_region: str
        target_resource_id: str
        target_resource_type: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                info: Optional[List[KeyValueItem]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.EventImpactedResourceListResult(Model):
        next_link: str
        value: list[EventImpactedResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[EventImpactedResource], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.EventLevelValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        ERROR = "Error"
        INFORMATIONAL = "Informational"
        WARNING = "Warning"


    class azure.mgmt.resourcehealth.models.EventPropertiesAdditionalInformation(Model):
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.EventPropertiesArticle(Model):
        article_content: str
        article_id: str
        parameters: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                article_content: Optional[str] = ..., 
                article_id: Optional[str] = ..., 
                parameters: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.EventPropertiesRecommendedActions(Model):
        actions: list[EventPropertiesRecommendedActionsItem]
        locale_code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: Optional[List[EventPropertiesRecommendedActionsItem]] = ..., 
                locale_code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.EventPropertiesRecommendedActionsItem(Model):
        action_text: str
        group_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_text: Optional[str] = ..., 
                group_id: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.EventSourceValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESOURCE_HEALTH = "ResourceHealth"
        SERVICE_HEALTH = "ServiceHealth"


    class azure.mgmt.resourcehealth.models.EventStatusValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        RESOLVED = "Resolved"


    class azure.mgmt.resourcehealth.models.EventSubTypeValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RETIREMENT = "Retirement"


    class azure.mgmt.resourcehealth.models.EventTypeValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMERGING_ISSUES = "EmergingIssues"
        HEALTH_ADVISORY = "HealthAdvisory"
        PLANNED_MAINTENANCE = "PlannedMaintenance"
        RCA = "RCA"
        SECURITY_ADVISORY = "SecurityAdvisory"
        SERVICE_ISSUE = "ServiceIssue"


    class azure.mgmt.resourcehealth.models.Events(Model):
        next_link: str
        value: list[Event]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Event], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.Faq(Model):
        answer: str
        locale_code: str
        question: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                answer: Optional[str] = ..., 
                locale_code: Optional[str] = ..., 
                question: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.Impact(Model):
        impacted_regions: list[ImpactedServiceRegion]
        impacted_service: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                impacted_regions: Optional[List[ImpactedServiceRegion]] = ..., 
                impacted_service: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.ImpactedRegion(Model):
        id: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.ImpactedResourceStatus(ProxyResource):
        availability_state: Union[str, AvailabilityStateValues]
        id: str
        name: str
        occurred_time: datetime
        reason_type: Union[str, ReasonTypeValues]
        summary: str
        system_data: SystemData
        title: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                availability_state: Optional[Union[str, AvailabilityStateValues]] = ..., 
                occurred_time: Optional[datetime] = ..., 
                reason_type: Optional[Union[str, ReasonTypeValues]] = ..., 
                summary: Optional[str] = ..., 
                title: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.ImpactedServiceRegion(Model):
        impacted_region: str
        impacted_subscriptions: list[str]
        impacted_tenants: list[str]
        last_update_time: datetime
        status: Union[str, EventStatusValues]
        updates: list[Update]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                impacted_region: Optional[str] = ..., 
                impacted_subscriptions: Optional[List[str]] = ..., 
                impacted_tenants: Optional[List[str]] = ..., 
                last_update_time: Optional[datetime] = ..., 
                status: Optional[Union[str, EventStatusValues]] = ..., 
                updates: Optional[List[Update]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.IssueNameParameter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.resourcehealth.models.KeyValueItem(Model):
        key: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.LevelValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        WARNING = "Warning"


    class azure.mgmt.resourcehealth.models.Link(Model):
        blade_name: str
        display_text: LinkDisplayText
        extension_name: str
        parameters: JSON
        type: Union[str, LinkTypeValues]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blade_name: Optional[str] = ..., 
                display_text: Optional[LinkDisplayText] = ..., 
                extension_name: Optional[str] = ..., 
                parameters: Optional[JSON] = ..., 
                type: Optional[Union[str, LinkTypeValues]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.LinkDisplayText(Model):
        localized_value: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.LinkTypeValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUTTON = "Button"
        HYPERLINK = "Hyperlink"


    class azure.mgmt.resourcehealth.models.MetadataEntity(ProxyResource):
        applicable_scenarios: Union[list[str, Scenario]]
        depends_on: list[str]
        display_name: str
        id: str
        name: str
        supported_values: list[MetadataSupportedValueDetail]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                applicable_scenarios: Optional[List[Union[str, Scenario]]] = ..., 
                depends_on: Optional[List[str]] = ..., 
                display_name: Optional[str] = ..., 
                supported_values: Optional[List[MetadataSupportedValueDetail]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.MetadataEntityListResult(Model):
        next_link: str
        value: list[MetadataEntity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[MetadataEntity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.MetadataSupportedValueDetail(Model):
        display_name: str
        id: str
        resource_types: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                resource_types: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.Operation(Model):
        display: OperationDisplay
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.OperationListResult(Model):
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[Operation], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.ReasonChronicityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERSISTENT = "Persistent"
        TRANSIENT = "Transient"


    class azure.mgmt.resourcehealth.models.ReasonTypeValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PLANNED = "Planned"
        UNPLANNED = "Unplanned"
        USER_INITIATED = "UserInitiated"


    class azure.mgmt.resourcehealth.models.RecommendedAction(Model):
        action: str
        action_url: str
        action_url_comment: str
        action_url_text: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Optional[str] = ..., 
                action_url: Optional[str] = ..., 
                action_url_comment: Optional[str] = ..., 
                action_url_text: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.Resource(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.Scenario(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS = "Alerts"


    class azure.mgmt.resourcehealth.models.ServiceImpactingEvent(Model):
        correlation_id: str
        event_start_time: datetime
        event_status_last_modified_time: datetime
        incident_properties: ServiceImpactingEventIncidentProperties
        status: ServiceImpactingEventStatus

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                correlation_id: Optional[str] = ..., 
                event_start_time: Optional[datetime] = ..., 
                event_status_last_modified_time: Optional[datetime] = ..., 
                incident_properties: Optional[ServiceImpactingEventIncidentProperties] = ..., 
                status: Optional[ServiceImpactingEventStatus] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.ServiceImpactingEventIncidentProperties(Model):
        incident_type: str
        region: str
        service: str
        title: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                incident_type: Optional[str] = ..., 
                region: Optional[str] = ..., 
                service: Optional[str] = ..., 
                title: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.ServiceImpactingEventStatus(Model):
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.SeverityValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFORMATION = "Information"
        WARNING = "Warning"


    class azure.mgmt.resourcehealth.models.StageValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        ARCHIVED = "Archived"
        RESOLVE = "Resolve"


    class azure.mgmt.resourcehealth.models.StatusActiveEvent(Model):
        cloud: str
        description: str
        impacts: list[EmergingIssueImpact]
        last_modified_time: datetime
        published: bool
        severity: Union[str, SeverityValues]
        stage: Union[str, StageValues]
        start_time: datetime
        title: str
        tracking_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud: Optional[str] = ..., 
                description: Optional[str] = ..., 
                impacts: Optional[List[EmergingIssueImpact]] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                published: Optional[bool] = ..., 
                severity: Optional[Union[str, SeverityValues]] = ..., 
                stage: Optional[Union[str, StageValues]] = ..., 
                start_time: Optional[datetime] = ..., 
                title: Optional[str] = ..., 
                tracking_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.StatusBanner(Model):
        cloud: str
        last_modified_time: datetime
        message: str
        title: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                title: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcehealth.models.Update(Model):
        summary: str
        update_date_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                summary: Optional[str] = ..., 
                update_date_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.mgmt.resourcehealth.operations

    class azure.mgmt.resourcehealth.operations.AvailabilityStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_by_resource(
                self, 
                resource_uri: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AvailabilityStatus: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[AvailabilityStatus]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[AvailabilityStatus]: ...

        @distributed_trace
        def list_by_subscription_id(
                self, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[AvailabilityStatus]: ...


    class azure.mgmt.resourcehealth.operations.ChildAvailabilityStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_by_resource(
                self, 
                resource_uri: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> AvailabilityStatus: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[AvailabilityStatus]: ...


    class azure.mgmt.resourcehealth.operations.ChildResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[AvailabilityStatus]: ...


    class azure.mgmt.resourcehealth.operations.EmergingIssuesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                issue_name: Union[str, IssueNameParameter], 
                **kwargs: Any
            ) -> EmergingIssuesGetResult: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[EmergingIssuesGetResult]: ...


    class azure.mgmt.resourcehealth.operations.EventOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                filter: Optional[str] = None, 
                query_start_time: Optional[str] = None, 
                **kwargs: Any
            ) -> Event: ...

        @distributed_trace
        def get_by_tenant_id_and_tracking_id(
                self, 
                event_tracking_id: str, 
                filter: Optional[str] = None, 
                query_start_time: Optional[str] = None, 
                **kwargs: Any
            ) -> Event: ...


    class azure.mgmt.resourcehealth.operations.EventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_single_resource(
                self, 
                resource_uri: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Event]: ...

        @distributed_trace
        def list_by_subscription_id(
                self, 
                filter: Optional[str] = None, 
                query_start_time: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Event]: ...

        @distributed_trace
        def list_by_tenant_id(
                self, 
                filter: Optional[str] = None, 
                query_start_time: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Event]: ...


    class azure.mgmt.resourcehealth.operations.ImpactedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[EventImpactedResource]: ...

        @distributed_trace
        def list_by_tenant_id_and_event_id(
                self, 
                event_tracking_id: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[EventImpactedResource]: ...


    class azure.mgmt.resourcehealth.operations.MetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_entity(
                self, 
                name: str, 
                **kwargs: Any
            ) -> MetadataEntity: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[MetadataEntity]: ...


    class azure.mgmt.resourcehealth.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> OperationListResult: ...


    class azure.mgmt.resourcehealth.operations.SecurityAdvisoryImpactedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_subscription_id_and_event_id(
                self, 
                event_tracking_id: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[EventImpactedResource]: ...

        @distributed_trace
        def list_by_tenant_id_and_event_id(
                self, 
                event_tracking_id: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[EventImpactedResource]: ...


```