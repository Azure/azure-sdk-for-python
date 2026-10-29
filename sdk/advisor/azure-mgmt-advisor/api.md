```py
namespace azure.mgmt.advisor

    class azure.mgmt.advisor.AdvisorManagementClient(_AdvisorManagementClientOperationsMixin): implements ContextManager 
        advisor_scores: AdvisorScoresOperations
        assessment_types: AssessmentTypesOperations
        assessments: AssessmentsOperations
        configurations: ConfigurationsOperations
        operations: Operations
        recommendation_metadata: RecommendationMetadataOperations
        recommendations: RecommendationsOperations
        resiliency_reviews: resiliencyReviewsOperations
        suppressions: SuppressionsOperations
        workloads: WorkloadsOperations

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

        @overload
        def predict(
                self, 
                prediction_request: PredictionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PredictionResponse: ...

        @overload
        def predict(
                self, 
                prediction_request: PredictionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PredictionResponse: ...

        @overload
        def predict(
                self, 
                prediction_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PredictionResponse: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.advisor.aio

    class azure.mgmt.advisor.aio.AdvisorManagementClient(_AdvisorManagementClientOperationsMixin): implements AsyncContextManager 
        advisor_scores: AdvisorScoresOperations
        assessment_types: AssessmentTypesOperations
        assessments: AssessmentsOperations
        configurations: ConfigurationsOperations
        operations: Operations
        recommendation_metadata: RecommendationMetadataOperations
        recommendations: RecommendationsOperations
        resiliency_reviews: resiliencyReviewsOperations
        suppressions: SuppressionsOperations
        workloads: WorkloadsOperations

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

        @overload
        async def predict(
                self, 
                prediction_request: PredictionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PredictionResponse: ...

        @overload
        async def predict(
                self, 
                prediction_request: PredictionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PredictionResponse: ...

        @overload
        async def predict(
                self, 
                prediction_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PredictionResponse: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.advisor.aio.operations

    class azure.mgmt.advisor.aio.operations.AdvisorScoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AdvisorScoreEntity: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[AdvisorScoreEntity]: ...


    class azure.mgmt.advisor.aio.operations.AssessmentTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[AssessmentTypeResult]: ...


    class azure.mgmt.advisor.aio.operations.AssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                assessment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                assessment_name: str, 
                **kwargs: Any
            ) -> AssessmentResult: ...

        @distributed_trace
        def list(
                self, 
                *, 
                skiptoken: Optional[str] = ..., 
                top: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AssessmentResult]: ...

        @overload
        async def put(
                self, 
                assessment_name: str, 
                assessment_contract: AssessmentResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AssessmentResult: ...

        @overload
        async def put(
                self, 
                assessment_name: str, 
                assessment_contract: AssessmentResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AssessmentResult: ...

        @overload
        async def put(
                self, 
                assessment_name: str, 
                assessment_contract: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AssessmentResult: ...


    class azure.mgmt.advisor.aio.operations.ConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_in_resource_group(
                self, 
                configuration_name: Union[str, ConfigurationName], 
                resource_group: str, 
                config_contract: ConfigData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @overload
        async def create_in_resource_group(
                self, 
                configuration_name: Union[str, ConfigurationName], 
                resource_group: str, 
                config_contract: ConfigData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @overload
        async def create_in_resource_group(
                self, 
                configuration_name: Union[str, ConfigurationName], 
                resource_group: str, 
                config_contract: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @overload
        async def create_in_subscription(
                self, 
                configuration_name: Union[str, ConfigurationName], 
                config_contract: ConfigData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @overload
        async def create_in_subscription(
                self, 
                configuration_name: Union[str, ConfigurationName], 
                config_contract: ConfigData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @overload
        async def create_in_subscription(
                self, 
                configuration_name: Union[str, ConfigurationName], 
                config_contract: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConfigData]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ConfigData]: ...


    class azure.mgmt.advisor.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationEntity]: ...


    class azure.mgmt.advisor.aio.operations.RecommendationMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> MetadataEntity: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[MetadataEntity]: ...


    class azure.mgmt.advisor.aio.operations.RecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def generate(self, **kwargs: Any) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                **kwargs: Any
            ) -> ResourceRecommendationBase: ...

        @distributed_trace_async
        async def get_generate_status(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceRecommendationBase]: ...

        @distributed_trace
        def list_by_tenant(
                self, 
                resource_uri: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceRecommendationBase]: ...

        @overload
        async def update(
                self, 
                recommendation_id: str, 
                properties: RecommendationPatchPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceRecommendationBase: ...

        @overload
        async def update(
                self, 
                recommendation_id: str, 
                properties: RecommendationPatchPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceRecommendationBase: ...

        @overload
        async def update(
                self, 
                recommendation_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceRecommendationBase: ...


    class azure.mgmt.advisor.aio.operations.SuppressionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                name: str, 
                suppression_contract: SuppressionContract, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionContract: ...

        @overload
        async def create(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                name: str, 
                suppression_contract: SuppressionContract, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionContract: ...

        @overload
        async def create(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                name: str, 
                suppression_contract: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionContract: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                name: str, 
                **kwargs: Any
            ) -> SuppressionContract: ...

        @distributed_trace
        def list(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SuppressionContract]: ...


    class azure.mgmt.advisor.aio.operations.WorkloadsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[WorkloadResult]: ...


    class azure.mgmt.advisor.aio.operations.resiliencyReviewsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                review_id: str, 
                **kwargs: Any
            ) -> ResiliencyReview: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ResiliencyReview]: ...


namespace azure.mgmt.advisor.models

    class azure.mgmt.advisor.models.ARMErrorResponseBody(_Model):
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


    class azure.mgmt.advisor.models.AdvisorScoreEntity(ProxyResource):
        id: str
        name: str
        properties: Optional[AdvisorScoreEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AdvisorScoreEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.advisor.models.AdvisorScoreEntityProperties(_Model):
        last_refreshed_score: Optional[ScoreEntity]
        time_series: Optional[list[TimeSeriesEntity]]

        @overload
        def __init__(
                self, 
                *, 
                last_refreshed_score: Optional[ScoreEntity] = ..., 
                time_series: Optional[list[TimeSeriesEntity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.Aggregated(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAY = "day"
        MONTH = "month"
        WEEK = "week"


    class azure.mgmt.advisor.models.ArmErrorResponse(_Model):
        error: Optional[ARMErrorResponseBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ARMErrorResponseBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.AssessmentResult(ProxyResource):
        id: str
        name: str
        properties: Optional[AssessmentResultProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AssessmentResultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.advisor.models.AssessmentResultProperties(_Model):
        assessment_id: Optional[str]
        description: Optional[str]
        locale: Optional[str]
        score: Optional[int]
        state: Optional[str]
        type: Optional[str]
        type_id: Optional[str]
        type_version: Optional[str]
        workload_id: Optional[str]
        workload_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                locale: Optional[str] = ..., 
                type_id: Optional[str] = ..., 
                workload_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.AssessmentTypeResult(_Model):
        description: Optional[str]
        id: Optional[str]
        locale: Optional[str]
        title: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                locale: Optional[str] = ..., 
                title: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.Category(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COST = "Cost"
        HIGH_AVAILABILITY = "HighAvailability"
        OPERATIONAL_EXCELLENCE = "OperationalExcellence"
        PERFORMANCE = "Performance"
        SECURITY = "Security"


    class azure.mgmt.advisor.models.ConfigData(Resource):
        id: str
        name: str
        properties: Optional[ConfigDataProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConfigDataProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.advisor.models.ConfigDataProperties(_Model):
        digests: Optional[list[DigestConfig]]
        duration: Optional[Union[str, Duration]]
        exclude: Optional[bool]
        low_cpu_threshold: Optional[Union[str, CpuThreshold]]

        @overload
        def __init__(
                self, 
                *, 
                digests: Optional[list[DigestConfig]] = ..., 
                duration: Optional[Union[str, Duration]] = ..., 
                exclude: Optional[bool] = ..., 
                low_cpu_threshold: Optional[Union[str, CpuThreshold]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.ConfigurationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.advisor.models.Control(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS_CONTINUITY = "BusinessContinuity"
        DISASTER_RECOVERY = "DisasterRecovery"
        HIGH_AVAILABILITY = "HighAvailability"
        MONITORING_AND_ALERTING = "MonitoringAndAlerting"
        OTHER = "Other"
        PERSONALIZED = "Personalized"
        PRIORITIZED_RECOMMENDATIONS = "PrioritizedRecommendations"
        SCALABILITY = "Scalability"
        SERVICE_UPGRADE_AND_RETIREMENT = "ServiceUpgradeAndRetirement"


    class azure.mgmt.advisor.models.CpuThreshold(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIFTEEN = "15"
        FIVE = "5"
        TEN = "10"
        TWENTY = "20"


    class azure.mgmt.advisor.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.advisor.models.DigestConfig(_Model):
        action_group_resource_id: Optional[str]
        categories: Optional[list[Union[str, Category]]]
        frequency: Optional[int]
        language: Optional[str]
        name: Optional[str]
        state: Optional[Union[str, DigestConfigState]]

        @overload
        def __init__(
                self, 
                *, 
                action_group_resource_id: Optional[str] = ..., 
                categories: Optional[list[Union[str, Category]]] = ..., 
                frequency: Optional[int] = ..., 
                language: Optional[str] = ..., 
                name: Optional[str] = ..., 
                state: Optional[Union[str, DigestConfigState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.DigestConfigState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DISABLED = "Disabled"


    class azure.mgmt.advisor.models.Duration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENUM_14 = "14"
        ENUM_21 = "21"
        ENUM_30 = "30"
        ENUM_60 = "60"
        ENUM_7 = "7"
        ENUM_90 = "90"


    class azure.mgmt.advisor.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.advisor.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.advisor.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.advisor.models.Impact(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.advisor.models.MetadataEntity(ProxyResource):
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


    class azure.mgmt.advisor.models.MetadataEntityProperties(_Model):
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


    class azure.mgmt.advisor.models.MetadataSupportedValueDetail(_Model):
        display_name: Optional[str]
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.OperationDisplayInfo(_Model):
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


    class azure.mgmt.advisor.models.OperationEntity(_Model):
        display: Optional[OperationDisplayInfo]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplayInfo] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.PredictionRequest(_Model):
        properties: Optional[PredictionRequestProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PredictionRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.advisor.models.PredictionRequestProperties(_Model):
        extended_properties: Optional[Any]
        prediction_type: Optional[Union[str, PredictionType]]

        @overload
        def __init__(
                self, 
                *, 
                extended_properties: Optional[Any] = ..., 
                prediction_type: Optional[Union[str, PredictionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.PredictionResponse(_Model):
        properties: Optional[PredictionResponseProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PredictionResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.advisor.models.PredictionResponseProperties(_Model):
        category: Optional[Union[str, Category]]
        extended_properties: Optional[Any]
        impact: Optional[Union[str, Impact]]
        impacted_field: Optional[str]
        last_updated: Optional[datetime]
        prediction_type: Optional[Union[str, PredictionType]]
        short_description: Optional[ShortDescription]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, Category]] = ..., 
                extended_properties: Optional[Any] = ..., 
                impact: Optional[Union[str, Impact]] = ..., 
                impacted_field: Optional[str] = ..., 
                last_updated: Optional[datetime] = ..., 
                prediction_type: Optional[Union[str, PredictionType]] = ..., 
                short_description: Optional[ShortDescription] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.PredictionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREDICTIVE_RIGHTSIZING = "PredictiveRightsizing"


    class azure.mgmt.advisor.models.Priority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        HIGH = "High"
        INFORMATIONAL = "Informational"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.advisor.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.advisor.models.RecommendationDismissReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AN_ALTERNATIVE_SOLUTION_IS_ALREADY_IN_PLACE = "AnAlternativeSolutionIsAlreadyInPlace"
        EXCESSIVE_COST_INVESTMENT_REQUIRED = "ExcessiveCostInvestmentRequired"
        IMPLEMENTATION_STEPS_ARE_UNCLEAR = "ImplementationStepsAreUnclear"
        INCOMPATIBLE_WITH_THE_CURRENT_CONFIGURATION = "IncompatibleWithTheCurrentConfiguration"
        OTHER = "Other"
        RISK_IS_ACCEPTABLE = "RiskIsAcceptable"
        TOO_COMPLEX_OR_IMPRACTICAL_TO_IMPLEMENT = "TooComplexOrImpracticalToImplement"


    class azure.mgmt.advisor.models.RecommendationPatchPayload(_Model):
        properties: Optional[RecommendationStatePropertiesPayload]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RecommendationStatePropertiesPayload] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.RecommendationProperties(_Model):
        actions: Optional[list[dict[str, Any]]]
        category: Optional[Union[str, Category]]
        completion_type: Optional[str]
        control: Optional[Union[str, Control]]
        created_time: Optional[datetime]
        description: Optional[str]
        exposed_metadata_properties: Optional[dict[str, Any]]
        extended_properties: Optional[dict[str, str]]
        impact: Optional[Union[str, Impact]]
        impacted_field: Optional[str]
        impacted_value: Optional[str]
        label: Optional[str]
        last_refreshed: Optional[datetime]
        last_updated: Optional[datetime]
        learn_more_link: Optional[str]
        metadata: Optional[dict[str, Any]]
        notes: Optional[str]
        postponed_until_date_time: Optional[datetime]
        potential_benefits: Optional[str]
        recommendation_dismiss_reason: Optional[Union[str, RecommendationDismissReason]]
        recommendation_status: Optional[Union[str, RecommendationStatus]]
        recommendation_type_id: Optional[str]
        remediation: Optional[dict[str, Any]]
        resource_metadata: Optional[ResourceMetadata]
        resource_workload: Optional[RecommendationPropertiesResourceWorkload]
        review: Optional[RecommendationPropertiesReview]
        risk: Optional[Union[str, Risk]]
        short_description: Optional[ShortDescription]
        source_system: Optional[str]
        suppression_id: Optional[str]
        tracked_properties: Optional[TrackedRecommendationProperties]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[dict[str, Any]]] = ..., 
                category: Optional[Union[str, Category]] = ..., 
                completion_type: Optional[str] = ..., 
                control: Optional[Union[str, Control]] = ..., 
                created_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                exposed_metadata_properties: Optional[dict[str, Any]] = ..., 
                extended_properties: Optional[dict[str, str]] = ..., 
                impact: Optional[Union[str, Impact]] = ..., 
                impacted_field: Optional[str] = ..., 
                impacted_value: Optional[str] = ..., 
                label: Optional[str] = ..., 
                last_refreshed: Optional[datetime] = ..., 
                last_updated: Optional[datetime] = ..., 
                learn_more_link: Optional[str] = ..., 
                metadata: Optional[dict[str, Any]] = ..., 
                notes: Optional[str] = ..., 
                postponed_until_date_time: Optional[datetime] = ..., 
                potential_benefits: Optional[str] = ..., 
                recommendation_dismiss_reason: Optional[Union[str, RecommendationDismissReason]] = ..., 
                recommendation_status: Optional[Union[str, RecommendationStatus]] = ..., 
                recommendation_type_id: Optional[str] = ..., 
                remediation: Optional[dict[str, Any]] = ..., 
                resource_metadata: Optional[ResourceMetadata] = ..., 
                resource_workload: Optional[RecommendationPropertiesResourceWorkload] = ..., 
                review: Optional[RecommendationPropertiesReview] = ..., 
                risk: Optional[Union[str, Risk]] = ..., 
                short_description: Optional[ShortDescription] = ..., 
                source_system: Optional[str] = ..., 
                suppression_id: Optional[str] = ..., 
                tracked_properties: Optional[TrackedRecommendationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.RecommendationPropertiesResourceWorkload(_Model):
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


    class azure.mgmt.advisor.models.RecommendationPropertiesReview(_Model):
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


    class azure.mgmt.advisor.models.RecommendationStatePropertiesPayload(_Model):
        postponed_until_date_time: Optional[datetime]
        recommendation_dismiss_reason: Optional[Union[str, RecommendationDismissReason]]
        recommendation_status: Optional[Union[str, RecommendationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                postponed_until_date_time: Optional[datetime] = ..., 
                recommendation_dismiss_reason: Optional[Union[str, RecommendationDismissReason]] = ..., 
                recommendation_status: Optional[Union[str, RecommendationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.RecommendationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        DISMISSED = "Dismissed"
        NEW = "New"
        POSTPONED = "Postponed"


    class azure.mgmt.advisor.models.ResiliencyReview(ProxyResource):
        id: str
        name: str
        properties: Optional[ResiliencyReviewProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ResiliencyReviewProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.advisor.models.ResiliencyReviewProperties(_Model):
        published_at: Optional[str]
        recommendations_count: Optional[int]
        review_name: Optional[str]
        review_status: Optional[Union[str, ReviewStatus]]
        updated_at: Optional[str]
        workload_name: Optional[str]


    class azure.mgmt.advisor.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.advisor.models.ResourceMetadata(_Model):
        action: Optional[dict[str, Any]]
        plural: Optional[str]
        resource_id: Optional[str]
        singular: Optional[str]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[dict[str, Any]] = ..., 
                plural: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                singular: Optional[str] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.ResourceRecommendationBase(ExtensionResource):
        id: str
        name: str
        properties: Optional[RecommendationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RecommendationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.advisor.models.ReviewStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        IN_PROGRESS = "InProgress"
        NEW = "New"


    class azure.mgmt.advisor.models.Risk(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        NONE = "None"
        WARNING = "Warning"


    class azure.mgmt.advisor.models.Scenario(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS = "Alerts"


    class azure.mgmt.advisor.models.ScoreEntity(_Model):
        category_count: Optional[float]
        consumption_units: Optional[float]
        date: Optional[str]
        impacted_resource_count: Optional[float]
        potential_score_increase: Optional[float]
        score: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                consumption_units: Optional[float] = ..., 
                date: Optional[str] = ..., 
                impacted_resource_count: Optional[float] = ..., 
                potential_score_increase: Optional[float] = ..., 
                score: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.ShortDescription(_Model):
        problem: Optional[str]
        solution: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                problem: Optional[str] = ..., 
                solution: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.SuppressionContract(ExtensionResource):
        id: str
        name: str
        properties: Optional[SuppressionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SuppressionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.advisor.models.SuppressionProperties(_Model):
        expiration_time_stamp: Optional[datetime]
        suppression_id: Optional[str]
        ttl: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                suppression_id: Optional[str] = ..., 
                ttl: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.SystemData(_Model):
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


    class azure.mgmt.advisor.models.TimeSeriesEntity(_Model):
        aggregation_level: Optional[Union[str, Aggregated]]
        score_history: Optional[list[ScoreEntity]]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_level: Optional[Union[str, Aggregated]] = ..., 
                score_history: Optional[list[ScoreEntity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.TrackedRecommendationProperties(_Model):
        priority: Optional[Union[str, Priority]]

        @overload
        def __init__(
                self, 
                *, 
                priority: Optional[Union[str, Priority]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.advisor.models.WorkloadResult(_Model):
        id: Optional[str]
        name: Optional[str]
        subscription_id: Optional[str]
        subscription_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                subscription_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.advisor.operations

    class azure.mgmt.advisor.operations.AdvisorScoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AdvisorScoreEntity: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[AdvisorScoreEntity]: ...


    class azure.mgmt.advisor.operations.AssessmentTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[AssessmentTypeResult]: ...


    class azure.mgmt.advisor.operations.AssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                assessment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                assessment_name: str, 
                **kwargs: Any
            ) -> AssessmentResult: ...

        @distributed_trace
        def list(
                self, 
                *, 
                skiptoken: Optional[str] = ..., 
                top: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AssessmentResult]: ...

        @overload
        def put(
                self, 
                assessment_name: str, 
                assessment_contract: AssessmentResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AssessmentResult: ...

        @overload
        def put(
                self, 
                assessment_name: str, 
                assessment_contract: AssessmentResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AssessmentResult: ...

        @overload
        def put(
                self, 
                assessment_name: str, 
                assessment_contract: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AssessmentResult: ...


    class azure.mgmt.advisor.operations.ConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_in_resource_group(
                self, 
                configuration_name: Union[str, ConfigurationName], 
                resource_group: str, 
                config_contract: ConfigData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @overload
        def create_in_resource_group(
                self, 
                configuration_name: Union[str, ConfigurationName], 
                resource_group: str, 
                config_contract: ConfigData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @overload
        def create_in_resource_group(
                self, 
                configuration_name: Union[str, ConfigurationName], 
                resource_group: str, 
                config_contract: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @overload
        def create_in_subscription(
                self, 
                configuration_name: Union[str, ConfigurationName], 
                config_contract: ConfigData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @overload
        def create_in_subscription(
                self, 
                configuration_name: Union[str, ConfigurationName], 
                config_contract: ConfigData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @overload
        def create_in_subscription(
                self, 
                configuration_name: Union[str, ConfigurationName], 
                config_contract: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group: str, 
                **kwargs: Any
            ) -> ItemPaged[ConfigData]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ConfigData]: ...


    class azure.mgmt.advisor.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationEntity]: ...


    class azure.mgmt.advisor.operations.RecommendationMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> MetadataEntity: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[MetadataEntity]: ...


    class azure.mgmt.advisor.operations.RecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def generate(self, **kwargs: Any) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                **kwargs: Any
            ) -> ResourceRecommendationBase: ...

        @distributed_trace
        def get_generate_status(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ResourceRecommendationBase]: ...

        @distributed_trace
        def list_by_tenant(
                self, 
                resource_uri: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ResourceRecommendationBase]: ...

        @overload
        def update(
                self, 
                recommendation_id: str, 
                properties: RecommendationPatchPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceRecommendationBase: ...

        @overload
        def update(
                self, 
                recommendation_id: str, 
                properties: RecommendationPatchPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceRecommendationBase: ...

        @overload
        def update(
                self, 
                recommendation_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceRecommendationBase: ...


    class azure.mgmt.advisor.operations.SuppressionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                name: str, 
                suppression_contract: SuppressionContract, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionContract: ...

        @overload
        def create(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                name: str, 
                suppression_contract: SuppressionContract, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionContract: ...

        @overload
        def create(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                name: str, 
                suppression_contract: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionContract: ...

        @distributed_trace
        def delete(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                name: str, 
                **kwargs: Any
            ) -> SuppressionContract: ...

        @distributed_trace
        def list(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SuppressionContract]: ...


    class azure.mgmt.advisor.operations.WorkloadsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[WorkloadResult]: ...


    class azure.mgmt.advisor.operations.resiliencyReviewsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                review_id: str, 
                **kwargs: Any
            ) -> ResiliencyReview: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ResiliencyReview]: ...


namespace azure.mgmt.advisor.types

    class azure.mgmt.advisor.types.ARMErrorResponseBody(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.advisor.types.AdvisorScoreEntity(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AdvisorScoreEntityProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AdvisorScoreEntityProperties
        system_data: SystemData
        type: str


    class azure.mgmt.advisor.types.AdvisorScoreEntityProperties(TypedDict, total=False):
        key "lastRefreshedScore": ForwardRef('ScoreEntity', module='types')
        last_refreshed_score: ScoreEntity
        timeSeries: list[TimeSeriesEntity]
        time_series: list[TimeSeriesEntity]


    class azure.mgmt.advisor.types.ArmErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ARMErrorResponseBody', module='types')
        error: ARMErrorResponseBody


    class azure.mgmt.advisor.types.AssessmentResult(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AssessmentResultProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AssessmentResultProperties
        system_data: SystemData
        type: str


    class azure.mgmt.advisor.types.AssessmentResultProperties(TypedDict, total=False):
        key "assessmentId": str
        key "description": str
        key "locale": str
        key "score": int
        key "state": str
        key "type": str
        key "typeId": str
        key "typeVersion": str
        key "workloadId": str
        key "workloadName": str
        assessment_id: str
        description: str
        locale: str
        score: int
        state: str
        type: str
        type_id: str
        type_version: str
        workload_id: str
        workload_name: str


    class azure.mgmt.advisor.types.AssessmentTypeResult(TypedDict, total=False):
        key "description": str
        key "id": str
        key "locale": str
        key "title": str
        key "version": str
        description: str
        id: str
        locale: str
        title: str
        version: str


    class azure.mgmt.advisor.types.ConfigData(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ConfigDataProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ConfigDataProperties
        system_data: SystemData
        type: str


    class azure.mgmt.advisor.types.ConfigDataProperties(TypedDict, total=False):
        key "duration": Union[str, Duration]
        key "exclude": bool
        key "lowCpuThreshold": Union[str, CpuThreshold]
        digests: list[DigestConfig]
        duration: Union[str, Duration]
        exclude: bool
        low_cpu_threshold: Union[str, CpuThreshold]


    class azure.mgmt.advisor.types.DigestConfig(TypedDict, total=False):
        key "actionGroupResourceId": str
        key "frequency": int
        key "language": str
        key "name": str
        key "state": Union[str, DigestConfigState]
        action_group_resource_id: str
        categories: list[Union[str, Category]]
        frequency: int
        language: str
        name: str
        state: Union[str, DigestConfigState]


    class azure.mgmt.advisor.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.advisor.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.advisor.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.advisor.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.advisor.types.MetadataEntity(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('MetadataEntityProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MetadataEntityProperties
        system_data: SystemData
        type: str


    class azure.mgmt.advisor.types.MetadataEntityProperties(TypedDict, total=False):
        key "displayName": str
        applicableScenarios: list[Union[str, Scenario]]
        applicable_scenarios: list[Union[str, Scenario]]
        dependsOn: list[str]
        depends_on: list[str]
        display_name: str
        supportedValues: list[MetadataSupportedValueDetail]
        supported_values: list[MetadataSupportedValueDetail]


    class azure.mgmt.advisor.types.MetadataSupportedValueDetail(TypedDict, total=False):
        key "displayName": str
        key "id": str
        display_name: str
        id: str


    class azure.mgmt.advisor.types.OperationDisplayInfo(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.advisor.types.OperationEntity(TypedDict, total=False):
        key "display": ForwardRef('OperationDisplayInfo', module='types')
        key "name": str
        display: OperationDisplayInfo
        name: str


    class azure.mgmt.advisor.types.PredictionRequest(TypedDict, total=False):
        key "properties": ForwardRef('PredictionRequestProperties', module='types')
        properties: PredictionRequestProperties


    class azure.mgmt.advisor.types.PredictionRequestProperties(TypedDict, total=False):
        key "extendedProperties": Any
        key "predictionType": Union[str, PredictionType]
        extended_properties: Any
        prediction_type: Union[str, PredictionType]


    class azure.mgmt.advisor.types.PredictionResponse(TypedDict, total=False):
        key "properties": ForwardRef('PredictionResponseProperties', module='types')
        properties: PredictionResponseProperties


    class azure.mgmt.advisor.types.PredictionResponseProperties(TypedDict, total=False):
        key "category": Union[str, Category]
        key "extendedProperties": Any
        key "impact": Union[str, Impact]
        key "impactedField": str
        key "lastUpdated": str
        key "predictionType": Union[str, PredictionType]
        key "shortDescription": ForwardRef('ShortDescription', module='types')
        category: Union[str, Category]
        extended_properties: Any
        impact: Union[str, Impact]
        impacted_field: str
        last_updated: str
        prediction_type: Union[str, PredictionType]
        short_description: ShortDescription


    class azure.mgmt.advisor.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.advisor.types.RecommendationPatchPayload(TypedDict, total=False):
        key "properties": ForwardRef('RecommendationStatePropertiesPayload', module='types')
        properties: RecommendationStatePropertiesPayload


    class azure.mgmt.advisor.types.RecommendationProperties(TypedDict, total=False):
        key "category": Union[str, Category]
        key "completionType": str
        key "control": Union[str, Control]
        key "createdTime": str
        key "description": str
        key "impact": Union[str, Impact]
        key "impactedField": str
        key "impactedValue": str
        key "label": str
        key "lastRefreshed": str
        key "lastUpdated": str
        key "learnMoreLink": str
        key "notes": str
        key "postponedUntilDateTime": str
        key "potentialBenefits": str
        key "recommendationDismissReason": Union[str, RecommendationDismissReason]
        key "recommendationStatus": Union[str, RecommendationStatus]
        key "recommendationTypeId": str
        key "resourceMetadata": ForwardRef('ResourceMetadata', module='types')
        key "resourceWorkload": ForwardRef('RecommendationPropertiesResourceWorkload', module='types')
        key "review": ForwardRef('RecommendationPropertiesReview', module='types')
        key "risk": Union[str, Risk]
        key "shortDescription": ForwardRef('ShortDescription', module='types')
        key "sourceSystem": str
        key "suppressionId": str
        key "trackedProperties": ForwardRef('TrackedRecommendationProperties', module='types')
        actions: list[dict[str, Any]]
        category: Union[str, Category]
        completion_type: str
        control: Union[str, Control]
        created_time: str
        description: str
        exposedMetadataProperties: dict[str, Any]
        exposed_metadata_properties: dict[str, Any]
        extendedProperties: dict[str, str]
        extended_properties: dict[str, str]
        impact: Union[str, Impact]
        impacted_field: str
        impacted_value: str
        label: str
        last_refreshed: str
        last_updated: str
        learn_more_link: str
        metadata: dict[str, Any]
        notes: str
        postponed_until_date_time: str
        potential_benefits: str
        recommendation_dismiss_reason: Union[str, RecommendationDismissReason]
        recommendation_status: Union[str, RecommendationStatus]
        recommendation_type_id: str
        remediation: dict[str, Any]
        resource_metadata: ResourceMetadata
        resource_workload: RecommendationPropertiesResourceWorkload
        review: RecommendationPropertiesReview
        risk: Union[str, Risk]
        short_description: ShortDescription
        source_system: str
        suppression_id: str
        tracked_properties: TrackedRecommendationProperties


    class azure.mgmt.advisor.types.RecommendationPropertiesResourceWorkload(TypedDict, total=False):
        key "id": str
        key "name": str
        id: str
        name: str


    class azure.mgmt.advisor.types.RecommendationPropertiesReview(TypedDict, total=False):
        key "id": str
        key "name": str
        id: str
        name: str


    class azure.mgmt.advisor.types.RecommendationStatePropertiesPayload(TypedDict, total=False):
        key "postponedUntilDateTime": str
        key "recommendationDismissReason": Union[str, RecommendationDismissReason]
        key "recommendationStatus": Union[str, RecommendationStatus]
        postponed_until_date_time: str
        recommendation_dismiss_reason: Union[str, RecommendationDismissReason]
        recommendation_status: Union[str, RecommendationStatus]


    class azure.mgmt.advisor.types.ResiliencyReview(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ResiliencyReviewProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ResiliencyReviewProperties
        system_data: SystemData
        type: str


    class azure.mgmt.advisor.types.ResiliencyReviewProperties(TypedDict, total=False):
        key "publishedAt": str
        key "recommendationsCount": int
        key "reviewName": str
        key "reviewStatus": Union[str, ReviewStatus]
        key "updatedAt": str
        key "workloadName": str
        published_at: str
        recommendations_count: int
        review_name: str
        review_status: Union[str, ReviewStatus]
        updated_at: str
        workload_name: str


    class azure.mgmt.advisor.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.advisor.types.ResourceMetadata(TypedDict, total=False):
        key "plural": str
        key "resourceId": str
        key "singular": str
        key "source": str
        action: dict[str, Any]
        plural: str
        resource_id: str
        singular: str
        source: str


    class azure.mgmt.advisor.types.ResourceRecommendationBase(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RecommendationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RecommendationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.advisor.types.ScoreEntity(TypedDict, total=False):
        key "categoryCount": float
        key "consumptionUnits": float
        key "date": str
        key "impactedResourceCount": float
        key "potentialScoreIncrease": float
        key "score": float
        category_count: float
        consumption_units: float
        date: str
        impacted_resource_count: float
        potential_score_increase: float
        score: float


    class azure.mgmt.advisor.types.ShortDescription(TypedDict, total=False):
        key "problem": str
        key "solution": str
        problem: str
        solution: str


    class azure.mgmt.advisor.types.SuppressionContract(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SuppressionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SuppressionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.advisor.types.SuppressionProperties(TypedDict, total=False):
        key "expirationTimeStamp": str
        key "suppressionId": str
        key "ttl": str
        expiration_time_stamp: str
        suppression_id: str
        ttl: str


    class azure.mgmt.advisor.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.advisor.types.TimeSeriesEntity(TypedDict, total=False):
        key "aggregationLevel": Union[str, Aggregated]
        aggregation_level: Union[str, Aggregated]
        scoreHistory: list[ScoreEntity]
        score_history: list[ScoreEntity]


    class azure.mgmt.advisor.types.TrackedRecommendationProperties(TypedDict, total=False):
        key "priority": Union[str, Priority]
        priority: Union[str, Priority]


    class azure.mgmt.advisor.types.WorkloadResult(TypedDict, total=False):
        key "id": str
        key "name": str
        key "subscriptionId": str
        key "subscriptionName": str
        id: str
        name: str
        subscription_id: str
        subscription_name: str


```