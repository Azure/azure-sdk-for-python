```py
namespace azure.mgmt.aiinfraoptimization

    class azure.mgmt.aiinfraoptimization.AIInfraOptimizationMgmtClient: implements ContextManager 
        operations: Operations
        recommendations: RecommendationsOperations

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


namespace azure.mgmt.aiinfraoptimization.aio

    class azure.mgmt.aiinfraoptimization.aio.AIInfraOptimizationMgmtClient: implements AsyncContextManager 
        operations: Operations
        recommendations: RecommendationsOperations

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


namespace azure.mgmt.aiinfraoptimization.aio.operations

    class azure.mgmt.aiinfraoptimization.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.aiinfraoptimization.aio.operations.RecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def recommend_vm_sku(
                self, 
                location: str, 
                body: RecommendVmSkuRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecommendVmSkuResponse: ...

        @overload
        async def recommend_vm_sku(
                self, 
                location: str, 
                body: RecommendVmSkuRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecommendVmSkuResponse: ...

        @overload
        async def recommend_vm_sku(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecommendVmSkuResponse: ...


namespace azure.mgmt.aiinfraoptimization.models

    class azure.mgmt.aiinfraoptimization.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.aiinfraoptimization.models.BenchmarkLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BENCHMARKED = "Benchmarked"
        TOPOLOGY_MATCHED = "TopologyMatched"


    class azure.mgmt.aiinfraoptimization.models.ContextLengthSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        REQUEST = "Request"


    class azure.mgmt.aiinfraoptimization.models.CostSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_RETAIL = "AzureRetail"
        AZURE_SUBSCRIPTION = "AzureSubscription"
        STATIC_PREVIEW = "StaticPreview"


    class azure.mgmt.aiinfraoptimization.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.aiinfraoptimization.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.aiinfraoptimization.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.ModelWeightsCalculation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARTIFACT_SIZE = "ArtifactSize"
        ESTIMATED_FROM_PARAMETER_COUNT = "EstimatedFromParameterCount"


    class azure.mgmt.aiinfraoptimization.models.Operation(_Model):
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


    class azure.mgmt.aiinfraoptimization.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.aiinfraoptimization.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.aiinfraoptimization.models.ParameterCountSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HUGGING_FACE = "HuggingFace"
        REQUEST = "Request"


    class azure.mgmt.aiinfraoptimization.models.PlacementStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVALUATED = "Evaluated"
        FAILED = "Failed"
        NOT_EVALUATED = "NotEvaluated"
        UNSUPPORTED = "Unsupported"


    class azure.mgmt.aiinfraoptimization.models.ProcurementOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ON_DEMAND = "OnDemand"
        SPOT = "Spot"


    class azure.mgmt.aiinfraoptimization.models.QuotaStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        UNAVAILABLE = "Unavailable"
        UNKNOWN = "Unknown"


    class azure.mgmt.aiinfraoptimization.models.RankingPreference(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COST = "Cost"
        LATENCY = "Latency"


    class azure.mgmt.aiinfraoptimization.models.ReadinessStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QUOTA_INCREASE_REQUIRED = "QuotaIncreaseRequired"
        READY_TO_ATTEMPT = "ReadyToAttempt"
        UNAVAILABLE = "Unavailable"
        VERIFICATION_REQUIRED = "VerificationRequired"


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuAccelerator(_Model):
        count_per_vm: int
        memory_gi_b_per_accelerator: int
        model: str

        @overload
        def __init__(
                self, 
                *, 
                count_per_vm: int, 
                memory_gi_b_per_accelerator: int, 
                model: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuBenchmark(_Model):
        benchmark_model: Optional[str]
        level: Union[str, BenchmarkLevel]
        model_class: str
        operating_system: Optional[str]
        p99_tpot_ms: Optional[float]
        p99_ttft_ms: Optional[float]
        scenario: str
        software: Optional[str]
        submission_id: Optional[str]
        submitter: Optional[str]
        submitter_count: int
        system: Optional[str]
        throughput: Optional[float]
        throughput_unit: Optional[str]
        weight_data_types: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                benchmark_model: Optional[str] = ..., 
                level: Union[str, BenchmarkLevel], 
                model_class: str, 
                operating_system: Optional[str] = ..., 
                p99_tpot_ms: Optional[float] = ..., 
                p99_ttft_ms: Optional[float] = ..., 
                scenario: str, 
                software: Optional[str] = ..., 
                submission_id: Optional[str] = ..., 
                submitter: Optional[str] = ..., 
                submitter_count: int, 
                system: Optional[str] = ..., 
                throughput: Optional[float] = ..., 
                throughput_unit: Optional[str] = ..., 
                weight_data_types: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuCost(_Model):
        currency_code: str
        deployment_hourly: float
        error: Optional[RecommendVmSkuStageError]
        price_as_of: Optional[datetime]
        source: Union[str, CostSource]
        vm_hourly: float

        @overload
        def __init__(
                self, 
                *, 
                currency_code: str, 
                deployment_hourly: float, 
                error: Optional[RecommendVmSkuStageError] = ..., 
                price_as_of: Optional[datetime] = ..., 
                source: Union[str, CostSource], 
                vm_hourly: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuDeployment(_Model):
        procurement_option: Optional[Union[str, ProcurementOption]]
        replica_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                procurement_option: Optional[Union[str, ProcurementOption]] = ..., 
                replica_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuHourlyCost(_Model):
        amount: Optional[float]
        currency_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuMemory(_Model):
        kv_cache_gi_b_per_request: float
        kv_cache_gi_b_total: float
        model_and_kv_cache_gi_b: float
        model_weights_gi_b: float

        @overload
        def __init__(
                self, 
                *, 
                kv_cache_gi_b_per_request: float, 
                kv_cache_gi_b_total: float, 
                model_and_kv_cache_gi_b: float, 
                model_weights_gi_b: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuModel(_Model):
        head_dim: Optional[int]
        hugging_face_model_id: Optional[str]
        max_context_length: Optional[int]
        num_key_value_heads: Optional[int]
        num_layers: Optional[int]
        parameter_count: Optional[int]
        weight_precision: Optional[Union[str, WeightPrecision]]

        @overload
        def __init__(
                self, 
                *, 
                head_dim: Optional[int] = ..., 
                hugging_face_model_id: Optional[str] = ..., 
                max_context_length: Optional[int] = ..., 
                num_key_value_heads: Optional[int] = ..., 
                num_layers: Optional[int] = ..., 
                parameter_count: Optional[int] = ..., 
                weight_precision: Optional[Union[str, WeightPrecision]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuOptimization(_Model):
        max_deployment_cost_per_hour: Optional[RecommendVmSkuHourlyCost]
        ranking_preference: Optional[Union[str, RankingPreference]]

        @overload
        def __init__(
                self, 
                *, 
                max_deployment_cost_per_hour: Optional[RecommendVmSkuHourlyCost] = ..., 
                ranking_preference: Optional[Union[str, RankingPreference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuOption(_Model):
        azure_ml_recommended: Optional[bool]
        benchmark: Optional[RecommendVmSkuBenchmark]
        cost: RecommendVmSkuCost
        documentation_url: Optional[str]
        performance_estimate: Optional[RecommendVmSkuPerformanceEstimate]
        placement: Optional[RecommendVmSkuPlacement]
        quota: Optional[RecommendVmSkuQuota]
        readiness: RecommendVmSkuReadiness
        recommendation_rank: int
        topology: RecommendVmSkuTopology
        vm_size: str

        @overload
        def __init__(
                self, 
                *, 
                azure_ml_recommended: Optional[bool] = ..., 
                benchmark: Optional[RecommendVmSkuBenchmark] = ..., 
                cost: RecommendVmSkuCost, 
                documentation_url: Optional[str] = ..., 
                performance_estimate: Optional[RecommendVmSkuPerformanceEstimate] = ..., 
                placement: Optional[RecommendVmSkuPlacement] = ..., 
                quota: Optional[RecommendVmSkuQuota] = ..., 
                readiness: RecommendVmSkuReadiness, 
                recommendation_rank: int, 
                topology: RecommendVmSkuTopology, 
                vm_size: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuPerformanceEstimate(_Model):
        deployment_output_tokens_per_second: float
        ttft_ms: float

        @overload
        def __init__(
                self, 
                *, 
                deployment_output_tokens_per_second: float, 
                ttft_ms: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuPlacement(_Model):
        error: Optional[RecommendVmSkuStageError]
        reason: Optional[str]
        recommended_availability_zones: Optional[list[str]]
        status: Union[str, PlacementStatus]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[RecommendVmSkuStageError] = ..., 
                reason: Optional[str] = ..., 
                recommended_availability_zones: Optional[list[str]] = ..., 
                status: Union[str, PlacementStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuQuota(_Model):
        error: Optional[RecommendVmSkuStageError]
        increase: Optional[RecommendVmSkuQuotaIncrease]
        max_available_replica_count: Optional[int]
        reason: Optional[str]
        status: Union[str, QuotaStatus]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[RecommendVmSkuStageError] = ..., 
                increase: Optional[RecommendVmSkuQuotaIncrease] = ..., 
                max_available_replica_count: Optional[int] = ..., 
                reason: Optional[str] = ..., 
                status: Union[str, QuotaStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuQuotaIncrease(_Model):
        limits: list[RecommendVmSkuQuotaLimit]
        portal_url: str

        @overload
        def __init__(
                self, 
                *, 
                limits: list[RecommendVmSkuQuotaLimit], 
                portal_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuQuotaLimit(_Model):
        current_limit: int
        current_usage: int
        name: str
        required_limit: int

        @overload
        def __init__(
                self, 
                *, 
                current_limit: int, 
                current_usage: int, 
                name: str, 
                required_limit: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuReadiness(_Model):
        reason: str
        status: Union[str, ReadinessStatus]

        @overload
        def __init__(
                self, 
                *, 
                reason: str, 
                status: Union[str, ReadinessStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuRequest(_Model):
        deployment: Optional[RecommendVmSkuDeployment]
        model: Optional[RecommendVmSkuModel]
        optimization: Optional[RecommendVmSkuOptimization]
        subscription_options: Optional[RecommendVmSkuSubscriptionOptions]
        target_vm_sizes: Optional[list[str]]
        workload: Optional[RecommendVmSkuWorkload]

        @overload
        def __init__(
                self, 
                *, 
                deployment: Optional[RecommendVmSkuDeployment] = ..., 
                model: Optional[RecommendVmSkuModel] = ..., 
                optimization: Optional[RecommendVmSkuOptimization] = ..., 
                subscription_options: Optional[RecommendVmSkuSubscriptionOptions] = ..., 
                target_vm_sizes: Optional[list[str]] = ..., 
                workload: Optional[RecommendVmSkuWorkload] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuResponse(_Model):
        options: list[RecommendVmSkuOption]
        sizing: RecommendVmSkuSizing

        @overload
        def __init__(
                self, 
                *, 
                options: list[RecommendVmSkuOption], 
                sizing: RecommendVmSkuSizing
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuSizing(_Model):
        basis: RecommendVmSkuSizingBasis
        memory: RecommendVmSkuMemory
        model: RecommendVmSkuSizingModel
        workload: RecommendVmSkuSizingWorkload

        @overload
        def __init__(
                self, 
                *, 
                basis: RecommendVmSkuSizingBasis, 
                memory: RecommendVmSkuMemory, 
                model: RecommendVmSkuSizingModel, 
                workload: RecommendVmSkuSizingWorkload
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuSizingBasis(_Model):
        context_length_source: Union[str, ContextLengthSource]
        model_weights_calculation: Union[str, ModelWeightsCalculation]
        parameter_count_source: Union[str, ParameterCountSource]

        @overload
        def __init__(
                self, 
                *, 
                context_length_source: Union[str, ContextLengthSource], 
                model_weights_calculation: Union[str, ModelWeightsCalculation], 
                parameter_count_source: Union[str, ParameterCountSource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuSizingModel(_Model):
        hugging_face_model_id: Optional[str]
        parameter_count: int
        weight_precision: Union[str, WeightPrecision]

        @overload
        def __init__(
                self, 
                *, 
                hugging_face_model_id: Optional[str] = ..., 
                parameter_count: int, 
                weight_precision: Union[str, WeightPrecision]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuSizingWorkload(_Model):
        context_length: int
        max_concurrent_requests_per_replica: int

        @overload
        def __init__(
                self, 
                *, 
                context_length: int, 
                max_concurrent_requests_per_replica: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuStageError(_Model):
        code: Union[str, StageErrorCode]
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, StageErrorCode], 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuSubscriptionOptions(_Model):
        include_placement: Optional[bool]
        include_pricing: Optional[bool]
        include_quota: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                include_placement: Optional[bool] = ..., 
                include_pricing: Optional[bool] = ..., 
                include_quota: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuTokenBudget(_Model):
        max_output_tokens: Optional[int]
        prompt_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_output_tokens: Optional[int] = ..., 
                prompt_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuTopology(_Model):
        accelerator: RecommendVmSkuAccelerator
        estimated_node_count_per_replica: int
        estimated_total_node_count: int

        @overload
        def __init__(
                self, 
                *, 
                accelerator: RecommendVmSkuAccelerator, 
                estimated_node_count_per_replica: int, 
                estimated_total_node_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.RecommendVmSkuWorkload(_Model):
        max_concurrent_requests_per_replica: Optional[int]
        token_budget: Optional[RecommendVmSkuTokenBudget]

        @overload
        def __init__(
                self, 
                *, 
                max_concurrent_requests_per_replica: Optional[int] = ..., 
                token_budget: Optional[RecommendVmSkuTokenBudget] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aiinfraoptimization.models.StageErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_UNAVAILABLE = "DataUnavailable"
        DEPENDENCY_ERROR = "DependencyError"
        EVALUATION_BUDGET_EXCEEDED = "EvaluationBudgetExceeded"
        PARTITION_CAPACITY_EXCEEDED = "PartitionCapacityExceeded"
        THROTTLED = "Throttled"
        TIMED_OUT = "TimedOut"


    class azure.mgmt.aiinfraoptimization.models.WeightPrecision(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BF16 = "BF16"
        FP16 = "FP16"
        FP32 = "FP32"
        FP4 = "FP4"
        FP8 = "FP8"
        INT4 = "INT4"
        INT8 = "INT8"


namespace azure.mgmt.aiinfraoptimization.operations

    class azure.mgmt.aiinfraoptimization.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.aiinfraoptimization.operations.RecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def recommend_vm_sku(
                self, 
                location: str, 
                body: RecommendVmSkuRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecommendVmSkuResponse: ...

        @overload
        def recommend_vm_sku(
                self, 
                location: str, 
                body: RecommendVmSkuRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecommendVmSkuResponse: ...

        @overload
        def recommend_vm_sku(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecommendVmSkuResponse: ...


namespace azure.mgmt.aiinfraoptimization.types

    class azure.mgmt.aiinfraoptimization.types.RecommendVmSkuDeployment(TypedDict, total=False):
        key "procurementOption": Union[str, ProcurementOption]
        key "replicaCount": int
        procurementOption: Union[str, ProcurementOption]
        replicaCount: int


    class azure.mgmt.aiinfraoptimization.types.RecommendVmSkuHourlyCost(TypedDict, total=False):
        key "amount": float
        key "currencyCode": str
        amount: float
        currencyCode: str


    class azure.mgmt.aiinfraoptimization.types.RecommendVmSkuModel(TypedDict, total=False):
        key "headDim": int
        key "huggingFaceModelId": str
        key "maxContextLength": int
        key "numKeyValueHeads": int
        key "numLayers": int
        key "parameterCount": int
        key "weightPrecision": Union[str, WeightPrecision]
        headDim: int
        huggingFaceModelId: str
        maxContextLength: int
        numKeyValueHeads: int
        numLayers: int
        parameterCount: int
        weightPrecision: Union[str, WeightPrecision]


    class azure.mgmt.aiinfraoptimization.types.RecommendVmSkuOptimization(TypedDict, total=False):
        key "maxDeploymentCostPerHour": ForwardRef('RecommendVmSkuHourlyCost', module='types')
        key "rankingPreference": Union[str, RankingPreference]
        maxDeploymentCostPerHour: RecommendVmSkuHourlyCost
        rankingPreference: Union[str, RankingPreference]


    class azure.mgmt.aiinfraoptimization.types.RecommendVmSkuRequest(TypedDict, total=False):
        key "deployment": ForwardRef('RecommendVmSkuDeployment', module='types')
        key "model": ForwardRef('RecommendVmSkuModel', module='types')
        key "optimization": ForwardRef('RecommendVmSkuOptimization', module='types')
        key "subscriptionOptions": ForwardRef('RecommendVmSkuSubscriptionOptions', module='types')
        key "workload": ForwardRef('RecommendVmSkuWorkload', module='types')
        deployment: RecommendVmSkuDeployment
        model: RecommendVmSkuModel
        optimization: RecommendVmSkuOptimization
        subscriptionOptions: RecommendVmSkuSubscriptionOptions
        targetVmSizes: list[str]
        workload: RecommendVmSkuWorkload


    class azure.mgmt.aiinfraoptimization.types.RecommendVmSkuSubscriptionOptions(TypedDict, total=False):
        key "includePlacement": bool
        key "includePricing": bool
        key "includeQuota": bool
        includePlacement: bool
        includePricing: bool
        includeQuota: bool


    class azure.mgmt.aiinfraoptimization.types.RecommendVmSkuTokenBudget(TypedDict, total=False):
        key "maxOutputTokens": int
        key "promptTokens": int
        maxOutputTokens: int
        promptTokens: int


    class azure.mgmt.aiinfraoptimization.types.RecommendVmSkuWorkload(TypedDict, total=False):
        key "maxConcurrentRequestsPerReplica": int
        key "tokenBudget": ForwardRef('RecommendVmSkuTokenBudget', module='types')
        maxConcurrentRequestsPerReplica: int
        tokenBudget: RecommendVmSkuTokenBudget


```