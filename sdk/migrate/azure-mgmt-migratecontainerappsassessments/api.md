```py
namespace azure.mgmt.migratecontainerappsassessments

    class azure.mgmt.migratecontainerappsassessments.MigrateContainerAppsAssessmentsMgmtClient: implements ContextManager 
        assessed_web_application_operations: AssessedWebApplicationOperationsOperations
        container_apps_assessment_operations: ContainerAppsAssessmentOperationsOperations
        container_apps_cost_detail_operations: ContainerAppsCostDetailOperationsOperations
        container_apps_managed_environment_operations: ContainerAppsManagedEnvironmentOperationsOperations
        container_apps_options_operations: ContainerAppsOptionsOperationsOperations
        container_apps_summary_operations: ContainerAppsSummaryOperationsOperations

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


namespace azure.mgmt.migratecontainerappsassessments.aio

    class azure.mgmt.migratecontainerappsassessments.aio.MigrateContainerAppsAssessmentsMgmtClient: implements AsyncContextManager 
        assessed_web_application_operations: AssessedWebApplicationOperationsOperations
        container_apps_assessment_operations: ContainerAppsAssessmentOperationsOperations
        container_apps_cost_detail_operations: ContainerAppsCostDetailOperationsOperations
        container_apps_managed_environment_operations: ContainerAppsManagedEnvironmentOperationsOperations
        container_apps_options_operations: ContainerAppsOptionsOperationsOperations
        container_apps_summary_operations: ContainerAppsSummaryOperationsOperations

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


namespace azure.mgmt.migratecontainerappsassessments.aio.operations

    class azure.mgmt.migratecontainerappsassessments.aio.operations.AssessedWebApplicationOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                assessed_workload: str, 
                **kwargs: Any
            ) -> AssessedWebApplication: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AssessedWebApplication]: ...


    class azure.mgmt.migratecontainerappsassessments.aio.operations.ContainerAppsAssessmentOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                resource: ContainerAppsAssessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerAppsAssessment]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                resource: ContainerAppsAssessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerAppsAssessment]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerAppsAssessment]: ...

        @distributed_trace_async
        async def begin_download_url(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[DownloadUrl]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> ContainerAppsAssessment: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerAppsAssessment]: ...


    class azure.mgmt.migratecontainerappsassessments.aio.operations.ContainerAppsCostDetailOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerAppsCostDetail]: ...


    class azure.mgmt.migratecontainerappsassessments.aio.operations.ContainerAppsManagedEnvironmentOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                managed_environment_name: str, 
                **kwargs: Any
            ) -> ContainerAppsManagedEnvironment: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerAppsManagedEnvironment]: ...


    class azure.mgmt.migratecontainerappsassessments.aio.operations.ContainerAppsOptionsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_options_name: str, 
                **kwargs: Any
            ) -> ContainerAppsAssessmentOptions: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerAppsAssessmentOptions]: ...


    class azure.mgmt.migratecontainerappsassessments.aio.operations.ContainerAppsSummaryOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                summary_name: str, 
                **kwargs: Any
            ) -> ContainerAppsSummary: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerAppsSummary]: ...


namespace azure.mgmt.migratecontainerappsassessments.models

    class azure.mgmt.migratecontainerappsassessments.models.AssessedWebApplication(ProxyResource):
        id: str
        name: str
        properties: Optional[AssessedWebApplicationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AssessedWebApplicationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.AssessedWebApplicationProperties(_Model):
        linkages: Optional[list[Linkages]]
        recommendation_result: RecommendationResult
        recommendations: Optional[list[RecommendationsMigrationIssuesMigrationSuitabilitySkus]]
        web_app_type: Union[str, WebServerType]
        workload_type: Optional[Union[str, MigrateWorkloadType]]

        @overload
        def __init__(
                self, 
                *, 
                recommendation_result: RecommendationResult, 
                web_app_type: Union[str, WebServerType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.AssessmentDetails(_Model):
        confidence_rating_in_percentage: Optional[float]
        created_timestamp: Optional[datetime]
        prices_timestamp: Optional[datetime]
        status: Optional[Union[str, AssessmentStatus]]
        updated_timestamp: Optional[datetime]


    class azure.mgmt.migratecontainerappsassessments.models.AssessmentSizingCriterion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AS_ON_PREMISES = "AsOnPremises"
        PERFORMANCE_BASED = "PerformanceBased"


    class azure.mgmt.migratecontainerappsassessments.models.AssessmentSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IIS = "IIS"
        MACHINE = "Machine"
        MY_SQL_SERVER = "MySQLServer"
        ORACLE_DATABASE = "OracleDatabase"
        ORACLE_SERVER = "OracleServer"
        SAP_INSTANCE = "SAPInstance"
        SPRINGBOOT_APPLICATION = "SpringbootApplication"
        SQL_DATABASE = "SqlDatabase"
        SQL_INSTANCE = "SqlInstance"
        TOM_CAT = "TomCat"
        UNKNOWN = "Unknown"
        WEB_APPS = "WebApps"


    class azure.mgmt.migratecontainerappsassessments.models.AssessmentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        CREATED = "Created"
        DELETED = "Deleted"
        FAILED = "Failed"
        INVALID = "Invalid"
        OUT_DATED = "OutDated"
        OUT_OF_SYNC = "OutOfSync"
        RUNNING = "Running"
        UPDATED = "Updated"


    class azure.mgmt.migratecontainerappsassessments.models.AzureCurrency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARS = "ARS"
        AUD = "AUD"
        BRL = "BRL"
        CAD = "CAD"
        CHF = "CHF"
        CNY = "CNY"
        DKK = "DKK"
        EUR = "EUR"
        GBP = "GBP"
        HKD = "HKD"
        IDR = "IDR"
        INR = "INR"
        JPY = "JPY"
        KRW = "KRW"
        MXN = "MXN"
        MYR = "MYR"
        NOK = "NOK"
        NZD = "NZD"
        RUB = "RUB"
        SAR = "SAR"
        SEK = "SEK"
        TRY = "TRY"
        TWD = "TWD"
        UNKNOWN = "Unknown"
        USD = "USD"
        ZAR = "ZAR"


    class azure.mgmt.migratecontainerappsassessments.models.AzureManagementOfferingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUM = "AUM"
        AZURE_BACKUP = "AzureBackup"
        AZ_MON = "AzMon"
        NO = "No"
        SCOMMI = "SCOMMI"


    class azure.mgmt.migratecontainerappsassessments.models.AzureOffer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EA = "EA"
        MSAZR0003_P = "MSAZR0003P"
        MSAZR0023_P = "MSAZR0023P"
        MSAZRUSGOV0003_P = "MSAZRUSGOV0003P"
        MSMCAZR0044_P = "MSMCAZR0044P"
        MSMCAZR0059_P = "MSMCAZR0059P"
        MSMCAZR0060_P = "MSMCAZR0060P"
        MSMCAZR0063_P = "MSMCAZR0063P"
        SAVINGS_PLAN1_YEAR = "SavingsPlan1Year"
        SAVINGS_PLAN3_YEAR = "SavingsPlan3Year"
        UNKNOWN = "Unknown"


    class azure.mgmt.migratecontainerappsassessments.models.AzureTarget(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AKS = "AKS"
        AVS = "Avs"
        AZURE_APP_SERVICE = "AzureAppService"
        AZURE_APP_SERVICE_CONTAINER = "AzureAppServiceContainer"
        AZURE_SPRING_APPS = "AzureSpringApps"
        AZURE_SQLVM = "AzureSQLVM"
        AZURE_VM = "AzureVM"
        CONTAINER_APPS = "ContainerApps"
        FLEX_SERVER_PG = "FlexServerPG"
        MY_SQL_AZURE_FLEX_SERVER = "MySQLAzureFlexServer"
        ORACLE_IAAS_VM = "OracleIaasVM"
        SAP_AZURE_INSTANCE = "SAPAzureInstance"
        SQL_DATABASE = "SqlDatabase"
        SQL_MI = "SqlMI"
        UNKNOWN = "Unknown"


    class azure.mgmt.migratecontainerappsassessments.models.BillingSettings(_Model):
        licensing_program: Optional[Union[str, LicensingProgram]]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                licensing_program: Optional[Union[str, LicensingProgram]] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.CloudSuitabilityCommon(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONDITIONALLY_SUITABLE = "ConditionallySuitable"
        NOT_SUITABLE = "NotSuitable"
        READINESS_UNKNOWN = "ReadinessUnknown"
        SUITABLE = "Suitable"
        SUITABLE_WITH_WARNINGS = "SuitableWithWarnings"
        UNKNOWN = "Unknown"


    class azure.mgmt.migratecontainerappsassessments.models.ComputeResource(_Model):
        cores: float
        memory: float


    class azure.mgmt.migratecontainerappsassessments.models.Configuration(_Model):
        azure_target: Optional[Union[str, AzureTarget]]
        sizing_criterion: Optional[Union[str, AssessmentSizingCriterion]]


    class azure.mgmt.migratecontainerappsassessments.models.ContainerApp(_Model):
        container_app_id: str
        container_app_name: str
        cores: Optional[float]
        environment_name: str
        memory_in_gib: Optional[float]
        monthly_cost: Optional[float]
        sku: Optional[Union[str, ContainerAppsWorkloadProfileSku]]
        workload_profile_type: Optional[Union[str, ContainerAppsWorkloadProfileType]]


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsAssessment(ProxyResource):
        id: str
        name: str
        properties: Optional[ContainerAppsAssessmentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ContainerAppsAssessmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsAssessmentOptions(ProxyResource):
        id: str
        name: str
        properties: Optional[ContainerAppsAssessmentOptionsProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ContainerAppsAssessmentOptionsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsAssessmentOptionsOutboundEdgeGroup(_Model):
        currencies: list[Union[str, AzureCurrency]]
        licensing_program: list[Union[str, LicensingProgram]]
        savings_options: list[Union[str, SavingsOptions]]
        sku: list[Union[str, ContainerAppsWorkloadProfileSku]]
        target_locations: list[str]
        workload_profile_types: list[Union[str, ContainerAppsWorkloadProfileType]]

        @overload
        def __init__(
                self, 
                *, 
                currencies: list[Union[str, AzureCurrency]], 
                licensing_program: list[Union[str, LicensingProgram]], 
                savings_options: list[Union[str, SavingsOptions]], 
                sku: list[Union[str, ContainerAppsWorkloadProfileSku]], 
                target_locations: list[str], 
                workload_profile_types: list[Union[str, ContainerAppsWorkloadProfileType]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsAssessmentOptionsProperties(_Model):
        edges: dict[str, ContainerAppsAssessmentOptionsOutboundEdgeGroup]


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsAssessmentProperties(_Model):
        details: Optional[AssessmentDetails]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        scope: Optional[Scope]
        settings: Optional[ContainerAppsAssessmentSettings]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[AssessmentDetails] = ..., 
                scope: Optional[Scope] = ..., 
                settings: Optional[ContainerAppsAssessmentSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsAssessmentSettings(_Model):
        azure_location: Optional[str]
        billing_settings: Optional[BillingSettings]
        currency: Optional[Union[str, AzureCurrency]]
        discount_percentage: Optional[float]
        environment_type: Optional[Union[str, EnvironmentType]]
        performance_data: Optional[PerformanceData]
        savings_settings: Optional[SavingsSettings]
        scaling_factor: Optional[float]
        sizing_criterion: Optional[Union[str, AssessmentSizingCriterion]]
        sku: Union[str, ContainerAppsWorkloadProfileSku]
        workload_profile_type: Union[str, ContainerAppsWorkloadProfileType]

        @overload
        def __init__(
                self, 
                *, 
                azure_location: Optional[str] = ..., 
                billing_settings: Optional[BillingSettings] = ..., 
                currency: Optional[Union[str, AzureCurrency]] = ..., 
                discount_percentage: Optional[float] = ..., 
                environment_type: Optional[Union[str, EnvironmentType]] = ..., 
                performance_data: Optional[PerformanceData] = ..., 
                savings_settings: Optional[SavingsSettings] = ..., 
                scaling_factor: Optional[float] = ..., 
                sizing_criterion: Optional[Union[str, AssessmentSizingCriterion]] = ..., 
                sku: Union[str, ContainerAppsWorkloadProfileSku], 
                workload_profile_type: Union[str, ContainerAppsWorkloadProfileType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsCostDetail(ProxyResource):
        id: str
        name: str
        properties: Optional[ContainerAppsCostDetailProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ContainerAppsCostDetailProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsCostDetailProperties(_Model):
        container_app_id: str
        container_app_name: str
        cores: Optional[float]
        environment_name: str
        memory_in_gib: Optional[float]
        monthly_cost: Optional[float]
        sku: Optional[Union[str, ContainerAppsWorkloadProfileSku]]
        workload_profile_type: Optional[Union[str, ContainerAppsWorkloadProfileType]]


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsManagedEnvironment(ProxyResource):
        id: str
        name: str
        properties: Optional[ContainerAppsManagedEnvironmentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ContainerAppsManagedEnvironmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsManagedEnvironmentProperties(_Model):
        container_apps: list[ContainerApp]
        cores: Optional[float]
        created_timestamp: Optional[datetime]
        management_fee_monthly_cost: Optional[float]
        memory_in_gib: Optional[float]
        monthly_cost: Optional[float]
        number_of_container_apps: Optional[int]
        region: Optional[str]
        updated_timestamp: Optional[datetime]
        workload_profile_type: Optional[Union[str, ContainerAppsWorkloadProfileType]]


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsSummary(ProxyResource):
        id: str
        name: str
        properties: Optional[ContainerAppsSummaryProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ContainerAppsSummaryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsSummaryProperties(_Model):
        cost_components: Optional[list[CostDetailsCommon]]
        machine_count: int
        savings_components: Optional[list[SavingsDetailsCommon]]
        sources: Optional[list[SourceDetails]]
        summary_name: Optional[str]
        summary_type: Optional[Union[str, SummaryType]]
        target_source_mapping: Optional[list[TargetSourcePair]]
        targets: Optional[list[TargetDetails]]
        web_app_count: int
        web_server_count: int


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsWorkloadProfileSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSUMPTION = "Consumption"
        CONSUMPTION_GPU_NC24_A100 = "Consumption-GPU-NC24-A100"
        CONSUMPTION_GPU_NC8_AS_T4 = "Consumption-GPU-NC8as-T4"
        DEDICATED_D16 = "Dedicated-D16"
        DEDICATED_D32 = "Dedicated-D32"
        DEDICATED_D4 = "Dedicated-D4"
        DEDICATED_D8 = "Dedicated-D8"
        DEDICATED_E16 = "Dedicated-E16"
        DEDICATED_E32 = "Dedicated-E32"
        DEDICATED_E4 = "Dedicated-E4"
        DEDICATED_E8 = "Dedicated-E8"
        DEDICATED_NC24_A100 = "Dedicated-NC24-A100"
        DEDICATED_NC48_A100 = "Dedicated-NC48-A100"
        DEDICATED_NC96_A100 = "Dedicated-NC96-A100"


    class azure.mgmt.migratecontainerappsassessments.models.ContainerAppsWorkloadProfileType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        CONSUMPTION = "Consumption"
        DEDICATED = "Dedicated"


    class azure.mgmt.migratecontainerappsassessments.models.CostDetailsCommon(_Model):
        cost_detail: Optional[list[NameValuePairCostType]]
        saving_options: Optional[Union[str, SavingsOptions]]


    class azure.mgmt.migratecontainerappsassessments.models.CostType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_PROTECTION_SERVICE = "DataProtectionService"
        MONITORING_SERVICE = "MonitoringService"
        MONTHLY_AVS_EXTERNAL_STORAGE_COST = "MonthlyAvsExternalStorageCost"
        MONTHLY_AVS_NETWORK_COST = "MonthlyAvsNetworkCost"
        MONTHLY_AVS_NODE_COST = "MonthlyAvsNodeCost"
        MONTHLY_AZURE_HYBRID_COST = "MonthlyAzureHybridCost"
        MONTHLY_BANDWIDTH_COST = "MonthlyBandwidthCost"
        MONTHLY_COMPUTE_COST = "MonthlyComputeCost"
        MONTHLY_LICENSING_COST = "MonthlyLicensingCost"
        MONTHLY_LINUX_AZURE_HYBRID_COST = "MonthlyLinuxAzureHybridCost"
        MONTHLY_MANAGEMENT_COST = "MonthlyManagementCost"
        MONTHLY_PREMIUM_STORAGE_COST = "MonthlyPremiumStorageCost"
        MONTHLY_PREMIUM_V2_STORAGE_COST = "MonthlyPremiumV2StorageCost"
        MONTHLY_SECURITY_COST = "MonthlySecurityCost"
        MONTHLY_STANDARD_HDD_STORAGE_COST = "MonthlyStandardHddStorageCost"
        MONTHLY_STANDARD_SSD_STORAGE_COST = "MonthlyStandardSsdStorageCost"
        MONTHLY_STORAGE_COST = "MonthlyStorageCost"
        MONTHLY_ULTRA_DISK_COST = "MonthlyUltraDiskCost"
        MONTHLY_ULTRA_STORAGE_COST = "MonthlyUltraStorageCost"
        PATCHING_SERVICE = "PatchingService"
        TOTAL_MONTHLY_COST = "TotalMonthlyCost"


    class azure.mgmt.migratecontainerappsassessments.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.migratecontainerappsassessments.models.DownloadUrl(_Model):
        assessment_report_url: str
        expiration_time: datetime


    class azure.mgmt.migratecontainerappsassessments.models.EnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEV_TEST = "DevTest"
        PRODUCTION = "Production"
        UNKNOWN = "Unknown"


    class azure.mgmt.migratecontainerappsassessments.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.migratecontainerappsassessments.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.migratecontainerappsassessments.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.LicensingProgram(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EA = "EA"
        MCA = "MCA"
        RETAIL = "Retail"
        UNKNOWN = "Unknown"


    class azure.mgmt.migratecontainerappsassessments.models.LinkageKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATABASE = "Database"
        INSTANCE = "Instance"
        MACHINE = "Machine"
        SERVER = "Server"
        UNKNOWN = "Unknown"
        WEB_APPLICATION = "WebApplication"
        WEB_SERVER = "WebServer"


    class azure.mgmt.migratecontainerappsassessments.models.LinkageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PARENT = "Parent"
        SOURCE = "Source"


    class azure.mgmt.migratecontainerappsassessments.models.Linkages(_Model):
        arm_id: Optional[str]
        kind: Optional[Union[str, LinkageKind]]
        linkage_type: Optional[Union[str, LinkageType]]
        workload_name: Optional[str]


    class azure.mgmt.migratecontainerappsassessments.models.ManagementDetails(_Model):
        name: Optional[Union[str, AzureManagementOfferingType]]
        readiness_summary: Optional[list[NameValuePairCloudSuitabilityCommon]]


    class azure.mgmt.migratecontainerappsassessments.models.MigrateWorkloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATABASE = "Database"
        HOST = "Host"
        INSTANCE = "Instance"
        MACHINE = "Machine"
        MANAGEMENT_SERVER = "ManagementServer"
        SERVER = "Server"
        UNKNOWN = "Unknown"
        WEB_APPLICATION = "WebApplication"
        WEB_SERVER = "WebServer"


    class azure.mgmt.migratecontainerappsassessments.models.MigrationDetails(_Model):
        migration_type: Optional[Union[str, MigrationType]]
        readiness_summary: Optional[list[NameValuePairCloudSuitabilityCommon]]


    class azure.mgmt.migratecontainerappsassessments.models.MigrationIssues(_Model):
        issue_category: Optional[Union[str, MigrationIssuesCategory]]
        issue_code: Optional[str]
        issue_description: Optional[str]
        more_information: Optional[list[MoreInformation]]
        possible_cause: Optional[str]
        recommended_actions: Optional[list[str]]


    class azure.mgmt.migratecontainerappsassessments.models.MigrationIssuesCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"
        ISSUE = "Issue"
        WARNING = "Warning"


    class azure.mgmt.migratecontainerappsassessments.models.MigrationPlatform(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IAA_S = "IaaS"
        PAA_S = "PaaS"
        SAA_S = "SaaS"
        UNKNOWN = "Unknown"


    class azure.mgmt.migratecontainerappsassessments.models.MigrationSuitability(_Model):
        readiness: Optional[Union[str, CloudSuitabilityCommon]]


    class azure.mgmt.migratecontainerappsassessments.models.MigrationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REARCHITECT = "Rearchitect"
        REHOST = "Rehost"
        REPLATFORM = "Replatform"
        RETAIN = "Retain"
        UNKNOWN = "Unknown"


    class azure.mgmt.migratecontainerappsassessments.models.MoreInformation(_Model):
        title: str
        url: str


    class azure.mgmt.migratecontainerappsassessments.models.NameValuePair(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.migratecontainerappsassessments.models.NameValuePairCloudSuitabilityCommon(_Model):
        name: Optional[Union[str, CloudSuitabilityCommon]]
        value: Optional[int]


    class azure.mgmt.migratecontainerappsassessments.models.NameValuePairCostType(_Model):
        name: Optional[Union[str, CostType]]
        value: Optional[float]


    class azure.mgmt.migratecontainerappsassessments.models.NameValuePairSavingsType(_Model):
        name: Optional[Union[str, SavingsType]]
        value: Optional[float]


    class azure.mgmt.migratecontainerappsassessments.models.Percentile(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERCENTILE50 = "Percentile50"
        PERCENTILE90 = "Percentile90"
        PERCENTILE95 = "Percentile95"
        PERCENTILE99 = "Percentile99"
        PERCENTILE_UNKNOWN = "PercentileUnknown"


    class azure.mgmt.migratecontainerappsassessments.models.PerformanceData(_Model):
        percentile: Optional[Union[str, Percentile]]
        perf_data_end_time: Optional[datetime]
        perf_data_start_time: Optional[datetime]
        time_range: Optional[Union[str, TimeRange]]

        @overload
        def __init__(
                self, 
                *, 
                percentile: Optional[Union[str, Percentile]] = ..., 
                perf_data_end_time: Optional[datetime] = ..., 
                perf_data_start_time: Optional[datetime] = ..., 
                time_range: Optional[Union[str, TimeRange]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.migratecontainerappsassessments.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.migratecontainerappsassessments.models.RecommendationResult(_Model):
        environment_name: str
        limit: ComputeResource
        max_replicas: int
        min_replicas: int
        request: ComputeResource
        workload_profile_type: Union[str, ContainerAppsWorkloadProfileType]


    class azure.mgmt.migratecontainerappsassessments.models.RecommendationsMigrationIssuesMigrationSuitabilitySkus(_Model):
        confidence_score: Optional[float]
        configuration: Optional[Configuration]
        migration_issues: Optional[list[MigrationIssues]]
        migration_platform: Optional[Union[str, MigrationPlatform]]
        migration_suitability: Optional[MigrationSuitability]
        recommended_for: Optional[RecommendedFor]
        security_suitability: Optional[SecuritySuitability]
        skus: Optional[list[SkusMigrationSuitability]]
        total_cost: Optional[list[CostDetailsCommon]]
        total_savings: Optional[list[SavingsDetailsCommon]]


    class azure.mgmt.migratecontainerappsassessments.models.RecommendedFor(_Model):
        strategies: Optional[list[Union[str, StrategyType]]]


    class azure.mgmt.migratecontainerappsassessments.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.migratecontainerappsassessments.models.SavingsDetailsCommon(_Model):
        saving_options: Optional[Union[str, SavingsOptions]]
        savings_detail: Optional[list[NameValuePairSavingsType]]


    class azure.mgmt.migratecontainerappsassessments.models.SavingsOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_AZURE_OFFER_CODE = "CustomAzureOfferCode"
        NONE = "None"
        RI1_YEAR = "RI1Year"
        RI3_YEAR = "RI3Year"
        SAVINGS_PLAN1_YEAR = "SavingsPlan1Year"
        SAVINGS_PLAN3_YEAR = "SavingsPlan3Year"


    class azure.mgmt.migratecontainerappsassessments.models.SavingsSettings(_Model):
        azure_offer_code: Optional[Union[str, AzureOffer]]
        savings_options: Optional[Union[str, SavingsOptions]]

        @overload
        def __init__(
                self, 
                *, 
                azure_offer_code: Optional[Union[str, AzureOffer]] = ..., 
                savings_options: Optional[Union[str, SavingsOptions]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.SavingsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTHLY_AHUB_SQL_COST_SAVINGS = "MonthlyAhubSqlCostSavings"
        MONTHLY_AZURE_HYBRID_COST_SAVINGS = "MonthlyAzureHybridCostSavings"
        MONTHLY_LINUX_AZURE_HYBRID_COST_SAVINGS = "MonthlyLinuxAzureHybridCostSavings"
        MONTHLY_VCF_BYOL_COST_DIFFERENCE = "MonthlyVcfByolCostDifference"


    class azure.mgmt.migratecontainerappsassessments.models.Scope(_Model):
        azure_resource_graph_query: Optional[str]
        scope_type: Optional[Union[str, ScopeType]]
        server_group_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_graph_query: Optional[str] = ..., 
                scope_type: Optional[Union[str, ScopeType]] = ..., 
                server_group_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migratecontainerappsassessments.models.ScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_RESOURCE_GRAPH_QUERY = "AzureResourceGraphQuery"
        SERVER_GROUP_ID = "ServerGroupId"


    class azure.mgmt.migratecontainerappsassessments.models.SecuritySuitability(_Model):
        readiness: Optional[Union[str, CloudSuitabilityCommon]]


    class azure.mgmt.migratecontainerappsassessments.models.SkuDetails(_Model):
        capabilities: Optional[list[NameValuePair]]
        sku_name: Optional[str]
        sku_type: Optional[Union[str, SkuType]]
        total_cost: Optional[list[CostDetailsCommon]]
        total_savings: Optional[list[SavingsDetailsCommon]]


    class azure.mgmt.migratecontainerappsassessments.models.SkuKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DETAILS = "Details"
        ENDPOINT = "Endpoint"


    class azure.mgmt.migratecontainerappsassessments.models.SkuType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP_SERVICE_PLAN = "AppServicePlan"
        AZURE_SPRING_APPS = "AzureSpringApps"
        COMPUTE = "Compute"
        NETWORK = "Network"
        STORAGE = "Storage"
        UNKNOWN = "Unknown"


    class azure.mgmt.migratecontainerappsassessments.models.SkusMigrationSuitability(_Model):
        details: Optional[SkuDetails]
        display_name: Optional[str]
        id: Optional[str]
        kind: Optional[Union[str, SkuKind]]
        resource_uri: Optional[str]
        sources: Optional[list[SourceRecommendationMigrationSuitability]]
        type: Optional[Union[str, SkuType]]


    class azure.mgmt.migratecontainerappsassessments.models.SourceDetails(_Model):
        count: Optional[int]
        platform: Optional[Union[str, MigrationPlatform]]
        source_name: Optional[Union[str, AssessmentSource]]
        source_type: Optional[Union[str, MigrateWorkloadType]]


    class azure.mgmt.migratecontainerappsassessments.models.SourceRecommendationMigrationSuitability(_Model):
        migration_suitability: Optional[MigrationSuitability]
        name: Optional[str]


    class azure.mgmt.migratecontainerappsassessments.models.StrategyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COST_OPTIMIZED = "CostOptimized"
        EFFORT_OPTIMIZED = "EffortOptimized"
        PAA_S_PREFERRED = "PaaSPreferred"


    class azure.mgmt.migratecontainerappsassessments.models.SummaryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STRATEGY = "Strategy"
        TARGET = "Target"
        UNKNOWN = "Unknown"


    class azure.mgmt.migratecontainerappsassessments.models.SystemData(_Model):
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


    class azure.mgmt.migratecontainerappsassessments.models.TargetDetails(_Model):
        count: Optional[int]
        platform: Optional[Union[str, MigrationPlatform]]
        target_name: Optional[Union[str, AzureTarget]]
        target_type: Optional[Union[str, MigrateWorkloadType]]


    class azure.mgmt.migratecontainerappsassessments.models.TargetSourcePair(_Model):
        confidence_score: Optional[float]
        cost_details: Optional[list[CostDetailsCommon]]
        management_details: Optional[list[ManagementDetails]]
        migration_details: Optional[MigrationDetails]
        savings_details: Optional[list[SavingsDetailsCommon]]
        source_count: Optional[int]
        source_ref: Optional[Union[str, AssessmentSource]]
        target_count: Optional[int]
        target_ref: Optional[Union[str, AzureTarget]]


    class azure.mgmt.migratecontainerappsassessments.models.TimeRange(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        DAY = "Day"
        MONTH = "Month"
        WEEK = "Week"


    class azure.mgmt.migratecontainerappsassessments.models.WebServerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IIS = "IIS"
        TOMCAT = "Tomcat"
        UNKNOWN = "Unknown"


namespace azure.mgmt.migratecontainerappsassessments.operations

    class azure.mgmt.migratecontainerappsassessments.operations.AssessedWebApplicationOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                assessed_workload: str, 
                **kwargs: Any
            ) -> AssessedWebApplication: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AssessedWebApplication]: ...


    class azure.mgmt.migratecontainerappsassessments.operations.ContainerAppsAssessmentOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                resource: ContainerAppsAssessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerAppsAssessment]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                resource: ContainerAppsAssessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerAppsAssessment]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerAppsAssessment]: ...

        @distributed_trace
        def begin_download_url(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> LROPoller[DownloadUrl]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> ContainerAppsAssessment: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ContainerAppsAssessment]: ...


    class azure.mgmt.migratecontainerappsassessments.operations.ContainerAppsCostDetailOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ContainerAppsCostDetail]: ...


    class azure.mgmt.migratecontainerappsassessments.operations.ContainerAppsManagedEnvironmentOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                managed_environment_name: str, 
                **kwargs: Any
            ) -> ContainerAppsManagedEnvironment: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ContainerAppsManagedEnvironment]: ...


    class azure.mgmt.migratecontainerappsassessments.operations.ContainerAppsOptionsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_options_name: str, 
                **kwargs: Any
            ) -> ContainerAppsAssessmentOptions: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ContainerAppsAssessmentOptions]: ...


    class azure.mgmt.migratecontainerappsassessments.operations.ContainerAppsSummaryOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                summary_name: str, 
                **kwargs: Any
            ) -> ContainerAppsSummary: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ContainerAppsSummary]: ...


namespace azure.mgmt.migratecontainerappsassessments.types

    class azure.mgmt.migratecontainerappsassessments.types.AssessmentDetails(TypedDict, total=False):
        key "confidenceRatingInPercentage": float
        key "createdTimestamp": str
        key "pricesTimestamp": str
        key "status": Union[str, AssessmentStatus]
        key "updatedTimestamp": str
        confidenceRatingInPercentage: float
        createdTimestamp: str
        pricesTimestamp: str
        status: Union[str, AssessmentStatus]
        updatedTimestamp: str


    class azure.mgmt.migratecontainerappsassessments.types.BillingSettings(TypedDict, total=False):
        key "licensingProgram": Union[str, LicensingProgram]
        key "subscriptionId": str
        licensingProgram: Union[str, LicensingProgram]
        subscriptionId: str


    class azure.mgmt.migratecontainerappsassessments.types.ContainerAppsAssessment(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ContainerAppsAssessmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ContainerAppsAssessmentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.migratecontainerappsassessments.types.ContainerAppsAssessmentProperties(TypedDict, total=False):
        key "details": ForwardRef('AssessmentDetails', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "scope": ForwardRef('Scope', module='types')
        key "settings": ForwardRef('ContainerAppsAssessmentSettings', module='types')
        details: AssessmentDetails
        provisioningState: Union[str, ProvisioningState]
        scope: Scope
        settings: ContainerAppsAssessmentSettings


    class azure.mgmt.migratecontainerappsassessments.types.ContainerAppsAssessmentSettings(TypedDict, total=False):
        key "azureLocation": str
        key "billingSettings": ForwardRef('BillingSettings', module='types')
        key "currency": Union[str, AzureCurrency]
        key "discountPercentage": float
        key "environmentType": Union[str, EnvironmentType]
        key "performanceData": ForwardRef('PerformanceData', module='types')
        key "savingsSettings": ForwardRef('SavingsSettings', module='types')
        key "scalingFactor": float
        key "sizingCriterion": Union[str, AssessmentSizingCriterion]
        key "sku": Required[Union[str, ContainerAppsWorkloadProfileSku]]
        key "workloadProfileType": Required[Union[str, ContainerAppsWorkloadProfileType]]
        azureLocation: str
        billingSettings: BillingSettings
        currency: Union[str, AzureCurrency]
        discountPercentage: float
        environmentType: Union[str, EnvironmentType]
        performanceData: PerformanceData
        savingsSettings: SavingsSettings
        scalingFactor: float
        sizingCriterion: Union[str, AssessmentSizingCriterion]
        sku: Union[str, ContainerAppsWorkloadProfileSku]
        workloadProfileType: Union[str, ContainerAppsWorkloadProfileType]


    class azure.mgmt.migratecontainerappsassessments.types.PerformanceData(TypedDict, total=False):
        key "percentile": Union[str, Percentile]
        key "perfDataEndTime": str
        key "perfDataStartTime": str
        key "timeRange": Union[str, TimeRange]
        percentile: Union[str, Percentile]
        perfDataEndTime: str
        perfDataStartTime: str
        timeRange: Union[str, TimeRange]


    class azure.mgmt.migratecontainerappsassessments.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.migratecontainerappsassessments.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.migratecontainerappsassessments.types.SavingsSettings(TypedDict, total=False):
        key "azureOfferCode": Union[str, AzureOffer]
        key "savingsOptions": Union[str, SavingsOptions]
        azureOfferCode: Union[str, AzureOffer]
        savingsOptions: Union[str, SavingsOptions]


    class azure.mgmt.migratecontainerappsassessments.types.Scope(TypedDict, total=False):
        key "azureResourceGraphQuery": str
        key "scopeType": Union[str, ScopeType]
        key "serverGroupId": str
        azureResourceGraphQuery: str
        scopeType: Union[str, ScopeType]
        serverGroupId: str


    class azure.mgmt.migratecontainerappsassessments.types.SystemData(TypedDict, total=False):
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


```