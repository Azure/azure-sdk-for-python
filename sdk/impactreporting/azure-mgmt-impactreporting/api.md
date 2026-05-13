```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.impactreporting

    class azure.mgmt.impactreporting.ImpactReportingMgmtClient: implements ContextManager 
        connectors: ConnectorsOperations
        impact_categories: ImpactCategoriesOperations
        insights: InsightsOperations
        operations: Operations
        workload_impacts: WorkloadImpactsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
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


namespace azure.mgmt.impactreporting.aio

    class azure.mgmt.impactreporting.aio.ImpactReportingMgmtClient: implements AsyncContextManager 
        connectors: ConnectorsOperations
        impact_categories: ImpactCategoriesOperations
        insights: InsightsOperations
        operations: Operations
        workload_impacts: WorkloadImpactsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
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


namespace azure.mgmt.impactreporting.aio.operations

    class azure.mgmt.impactreporting.aio.operations.ConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                connector_name: str, 
                resource: Connector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                connector_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                connector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connector]: ...

        @distributed_trace_async
        async def delete(
                self, 
                connector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                connector_name: str, 
                **kwargs: Any
            ) -> Connector: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[Connector]: ...

        @overload
        async def update(
                self, 
                connector_name: str, 
                properties: ConnectorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connector: ...

        @overload
        async def update(
                self, 
                connector_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connector: ...

        @overload
        async def update(
                self, 
                connector_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connector: ...


    class azure.mgmt.impactreporting.aio.operations.ImpactCategoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                impact_category_name: str, 
                **kwargs: Any
            ) -> ImpactCategory: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                category_name: Optional[str] = ..., 
                resource_type: str, 
                **kwargs: Any
            ) -> AsyncIterable[ImpactCategory]: ...


    class azure.mgmt.impactreporting.aio.operations.InsightsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                workload_impact_name: str, 
                insight_name: str, 
                resource: Insight, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @overload
        async def create(
                self, 
                workload_impact_name: str, 
                insight_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @overload
        async def create(
                self, 
                workload_impact_name: str, 
                insight_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @distributed_trace_async
        async def delete(
                self, 
                workload_impact_name: str, 
                insight_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                workload_impact_name: str, 
                insight_name: str, 
                **kwargs: Any
            ) -> Insight: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                workload_impact_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Insight]: ...


    class azure.mgmt.impactreporting.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.impactreporting.aio.operations.WorkloadImpactsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                workload_impact_name: str, 
                resource: WorkloadImpact, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadImpact]: ...

        @overload
        async def begin_create(
                self, 
                workload_impact_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadImpact]: ...

        @overload
        async def begin_create(
                self, 
                workload_impact_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadImpact]: ...

        @distributed_trace_async
        async def delete(
                self, 
                workload_impact_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                workload_impact_name: str, 
                **kwargs: Any
            ) -> WorkloadImpact: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[WorkloadImpact]: ...


namespace azure.mgmt.impactreporting.models

    class azure.mgmt.impactreporting.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.impactreporting.models.ClientIncidentDetails(Model):
        client_incident_id: Optional[str]
        client_incident_source: Optional[Union[str, IncidentSource]]

        @overload
        def __init__(
                self, 
                *, 
                client_incident_id: Optional[str] = ..., 
                client_incident_source: Optional[Union[str, IncidentSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.ConfidenceLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.impactreporting.models.Connectivity(Model):
        port: Optional[int]
        protocol: Optional[Union[str, Protocol]]
        source: Optional[SourceOrTarget]
        target: Optional[SourceOrTarget]

        @overload
        def __init__(
                self, 
                *, 
                port: Optional[int] = ..., 
                protocol: Optional[Union[str, Protocol]] = ..., 
                source: Optional[SourceOrTarget] = ..., 
                target: Optional[SourceOrTarget] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.Connector(ProxyResource):
        id: str
        name: str
        properties: Optional[ConnectorProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.ConnectorProperties(Model):
        connector_id: str
        connector_type: Union[str, Platform]
        last_run_time_stamp: datetime
        provisioning_state: Optional[Union[str, ProvisioningState]]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                connector_type: Union[str, Platform]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.ConnectorUpdate(Model):
        properties: Optional[ConnectorUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectorUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.ConnectorUpdateProperties(Model):
        connector_type: Optional[Union[str, Platform]]

        @overload
        def __init__(
                self, 
                *, 
                connector_type: Optional[Union[str, Platform]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.Content(Model):
        description: str
        title: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.impactreporting.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.impactreporting.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.impactreporting.models.ErrorDetailProperties(Model):
        error_code: Optional[str]
        error_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.ErrorResponse(Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.ExpectedValueRange(Model):
        max: float
        min: float

        @overload
        def __init__(
                self, 
                *, 
                max: float, 
                min: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.ImpactCategory(ProxyResource):
        id: str
        name: str
        properties: Optional[ImpactCategoryProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ImpactCategoryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.ImpactCategoryProperties(Model):
        category_id: str
        description: Optional[str]
        parent_category_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        required_impact_properties: Optional[List[RequiredImpactProperties]]

        @overload
        def __init__(
                self, 
                *, 
                category_id: str, 
                description: Optional[str] = ..., 
                parent_category_id: Optional[str] = ..., 
                required_impact_properties: Optional[List[RequiredImpactProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.ImpactDetails(Model):
        end_time: Optional[datetime]
        impact_id: str
        impacted_resource_id: str
        start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                impact_id: str, 
                impacted_resource_id: str, 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.IncidentSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DEVOPS = "AzureDevops"
        ICM = "ICM"
        JIRA = "Jira"
        OTHER = "Other"
        SERVICE_NOW = "ServiceNow"


    class azure.mgmt.impactreporting.models.Insight(ProxyResource):
        id: str
        name: str
        properties: Optional[InsightProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[InsightProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.InsightProperties(Model):
        additional_details: Optional[Any]
        category: str
        content: Content
        event_id: Optional[str]
        event_time: Optional[datetime]
        group_id: Optional[str]
        impact: ImpactDetails
        insight_unique_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_details: Optional[Any] = ..., 
                category: str, 
                content: Content, 
                event_id: Optional[str] = ..., 
                event_time: Optional[datetime] = ..., 
                group_id: Optional[str] = ..., 
                impact: ImpactDetails, 
                insight_unique_id: str, 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.MetricUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        BYTE_SECONDS = "ByteSeconds"
        CORES = "Cores"
        COUNT = "Count"
        COUNT_PER_SECOND = "CountPerSecond"
        MILLI_CORES = "MilliCores"
        MILLI_SECONDS = "MilliSeconds"
        NANO_CORES = "NanoCores"
        OTHER = "Other"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.mgmt.impactreporting.models.Operation(Model):
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


    class azure.mgmt.impactreporting.models.OperationDisplay(Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.impactreporting.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.impactreporting.models.Performance(Model):
        actual: Optional[float]
        expected: Optional[float]
        expected_value_range: Optional[ExpectedValueRange]
        metric_name: Optional[str]
        unit: Optional[Union[str, MetricUnit]]

        @overload
        def __init__(
                self, 
                *, 
                actual: Optional[float] = ..., 
                expected: Optional[float] = ..., 
                expected_value_range: Optional[ExpectedValueRange] = ..., 
                metric_name: Optional[str] = ..., 
                unit: Optional[Union[str, MetricUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.Platform(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_MONITOR = "AzureMonitor"


    class azure.mgmt.impactreporting.models.Protocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FTP = "FTP"
        HTTP = "HTTP"
        HTTPS = "HTTPS"
        OTHER = "Other"
        RDP = "RDP"
        SSH = "SSH"
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.impactreporting.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.impactreporting.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.impactreporting.models.RequiredImpactProperties(Model):
        allowed_values: Optional[List[str]]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                allowed_values: Optional[List[str]] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.Resource(Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.impactreporting.models.SourceOrTarget(Model):
        azure_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.SystemData(Model):
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


    class azure.mgmt.impactreporting.models.Toolset(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANSIBLE = "Ansible"
        ARM = "ARM"
        CHEF = "Chef"
        OTHER = "Other"
        PORTAL = "Portal"
        PUPPET = "Puppet"
        SDK = "SDK"
        SHELL = "Shell"
        TERRAFORM = "Terraform"


    class azure.mgmt.impactreporting.models.Workload(Model):
        context: Optional[str]
        toolset: Optional[Union[str, Toolset]]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                toolset: Optional[Union[str, Toolset]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.WorkloadImpact(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkloadImpactProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadImpactProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.impactreporting.models.WorkloadImpactProperties(Model):
        additional_properties: Optional[Any]
        arm_correlation_ids: Optional[List[str]]
        client_incident_details: Optional[ClientIncidentDetails]
        confidence_level: Optional[Union[str, ConfidenceLevel]]
        connectivity: Optional[Connectivity]
        end_date_time: Optional[datetime]
        error_details: Optional[ErrorDetailProperties]
        impact_category: str
        impact_description: Optional[str]
        impact_group_id: Optional[str]
        impact_unique_id: Optional[str]
        impacted_resource_id: str
        performance: Optional[List[Performance]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reported_time_utc: Optional[datetime]
        start_date_time: datetime
        workload: Optional[Workload]

        @overload
        def __init__(
                self, 
                *, 
                additional_properties: Optional[Any] = ..., 
                arm_correlation_ids: Optional[List[str]] = ..., 
                client_incident_details: Optional[ClientIncidentDetails] = ..., 
                confidence_level: Optional[Union[str, ConfidenceLevel]] = ..., 
                connectivity: Optional[Connectivity] = ..., 
                end_date_time: Optional[datetime] = ..., 
                error_details: Optional[ErrorDetailProperties] = ..., 
                impact_category: str, 
                impact_description: Optional[str] = ..., 
                impact_group_id: Optional[str] = ..., 
                impacted_resource_id: str, 
                performance: Optional[List[Performance]] = ..., 
                start_date_time: datetime, 
                workload: Optional[Workload] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.impactreporting.operations

    class azure.mgmt.impactreporting.operations.ConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                connector_name: str, 
                resource: Connector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connector]: ...

        @overload
        def begin_create_or_update(
                self, 
                connector_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connector]: ...

        @overload
        def begin_create_or_update(
                self, 
                connector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connector]: ...

        @distributed_trace
        def delete(
                self, 
                connector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                connector_name: str, 
                **kwargs: Any
            ) -> Connector: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[Connector]: ...

        @overload
        def update(
                self, 
                connector_name: str, 
                properties: ConnectorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connector: ...

        @overload
        def update(
                self, 
                connector_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connector: ...

        @overload
        def update(
                self, 
                connector_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connector: ...


    class azure.mgmt.impactreporting.operations.ImpactCategoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                impact_category_name: str, 
                **kwargs: Any
            ) -> ImpactCategory: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                category_name: Optional[str] = ..., 
                resource_type: str, 
                **kwargs: Any
            ) -> Iterable[ImpactCategory]: ...


    class azure.mgmt.impactreporting.operations.InsightsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                workload_impact_name: str, 
                insight_name: str, 
                resource: Insight, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @overload
        def create(
                self, 
                workload_impact_name: str, 
                insight_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @overload
        def create(
                self, 
                workload_impact_name: str, 
                insight_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @distributed_trace
        def delete(
                self, 
                workload_impact_name: str, 
                insight_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                workload_impact_name: str, 
                insight_name: str, 
                **kwargs: Any
            ) -> Insight: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                workload_impact_name: str, 
                **kwargs: Any
            ) -> Iterable[Insight]: ...


    class azure.mgmt.impactreporting.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.impactreporting.operations.WorkloadImpactsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                workload_impact_name: str, 
                resource: WorkloadImpact, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadImpact]: ...

        @overload
        def begin_create(
                self, 
                workload_impact_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadImpact]: ...

        @overload
        def begin_create(
                self, 
                workload_impact_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadImpact]: ...

        @distributed_trace
        def delete(
                self, 
                workload_impact_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                workload_impact_name: str, 
                **kwargs: Any
            ) -> WorkloadImpact: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[WorkloadImpact]: ...


```