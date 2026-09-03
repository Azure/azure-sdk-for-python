```py
namespace azure.ai.finetuning_sessions

    class azure.ai.finetuning_sessions.BatchTooLargeError(FineTuningSessionsError):

        def __init__(
                self, 
                message: str, 
                *, 
                actual_batch_size: Optional[int] = ..., 
                max_batch_size: Optional[int] = ..., 
                response: Any = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.finetuning_sessions.ContentionError(FineTuningSessionsError):

        def __init__(
                self, 
                message: str, 
                *, 
                reason: Optional[str] = ..., 
                response: Any = ..., 
                retry_after_sec: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.finetuning_sessions.EngineDeadError(FineTuningSessionsError):

        def __init__(
                self, 
                message: str, 
                *, 
                debug_ref: Optional[str] = ..., 
                error_code: Optional[str] = ..., 
                response: Any = ..., 
                session_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.finetuning_sessions.FineTuningSession:

        def __init__(
                self, 
                client: FineTuningSessionClient, 
                session_id: str
            ) -> None: ...

        @classmethod
        def create(
                cls, 
                client: FineTuningSessionClient, 
                *, 
                base_model: str, 
                from_checkpoint: Optional[FromCheckpoint] = ..., 
                lora_config: Optional[LoRAConfig] = ..., 
                timeout_sec: float = 600.0, 
                type: str = "training"
            ) -> FineTuningSession: ...

        @classmethod
        def create_from_checkpoint(
                cls, 
                client: FineTuningSessionClient, 
                *, 
                base_model: str, 
                checkpoint_path: str, 
                lora_config: Optional[LoRAConfig] = ..., 
                timeout_sec: float = 600.0, 
                type: str = "training"
            ) -> FineTuningSession: ...

        def close(self, **kwargs: Any) -> None: ...

        def forward(
                self, 
                batch: List[Datum], 
                *, 
                loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY, 
                loss_fn_config: Optional[LossFnConfig] = ..., 
                **kwargs: Any
            ) -> OperationResult: ...

        def forward_backward(
                self, 
                batch: List[Datum], 
                *, 
                loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY, 
                loss_fn_config: Optional[LossFnConfig] = ..., 
                **kwargs: Any
            ) -> OperationResult: ...

        def heartbeat(self, **kwargs: Any) -> Any: ...

        def optim_step(
                self, 
                adam_params: AdamParams, 
                **kwargs: Any
            ) -> OperationResult: ...

        def sample(
                self, 
                prompt_tokens: List[int], 
                sampling_params: SamplingParams, 
                *, 
                checkpoint_id: str, 
                num_samples: int = 1, 
                prompt_logprobs: bool = False, 
                prompt_token_ids: bool = False, 
                sampling_session_id: Optional[str] = ..., 
                seq_id: Optional[int] = ..., 
                topk_prompt_logprobs: int = 0, 
                **kwargs: Any
            ) -> OperationResult: ...

        def save_weights(
                self, 
                path: str, 
                **kwargs: Any
            ) -> OperationResult: ...

        def save_weights_for_sampler(
                self, 
                seq_id: int, 
                *, 
                path: Optional[str] = ..., 
                sampling_session_seq_id: Optional[int] = ..., 
                **kwargs: Any
            ) -> OperationResult: ...


    class azure.ai.finetuning_sessions.FineTuningSessionClient(FineTuningSessionClientGenerated): implements ContextManager 
        checkpoints: CheckpointsOperations
        operations: Operations
        sampling: SamplingOperations
        sessions: SessionsOperations
        training: TrainingOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                allow_insecure_http: bool = False, 
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


    class azure.ai.finetuning_sessions.FineTuningSessionsError(HttpResponseError):

        def __init__(
                self, 
                message: str, 
                *, 
                response: Any = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.finetuning_sessions.MalformedDatumError(FineTuningSessionsError):

        def __init__(
                self, 
                message: str, 
                *, 
                debug_ref: Optional[str] = ..., 
                error_code: Optional[str] = ..., 
                field: Optional[str] = ..., 
                response: Any = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.finetuning_sessions.NoCapacityError(FineTuningSessionsError):

        def __init__(
                self, 
                message: str, 
                *, 
                reason: Optional[str] = ..., 
                response: Any = ..., 
                retry_after_sec: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.finetuning_sessions.RequestValidationError(FineTuningSessionsError):

        def __init__(
                self, 
                message: str, 
                *, 
                debug_ref: Optional[str] = ..., 
                error_code: Optional[str] = ..., 
                field: Optional[str] = ..., 
                response: Any = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.finetuning_sessions.TrainingEngineError(FineTuningSessionsError):

        def __init__(
                self, 
                message: str, 
                *, 
                debug_ref: Optional[str] = ..., 
                error_code: Optional[str] = ..., 
                response: Any = ..., 
                session_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


namespace azure.ai.finetuning_sessions.aio

    class azure.ai.finetuning_sessions.aio.FineTuningSessionClient: implements AsyncContextManager 
        checkpoints: CheckpointsOperations
        operations: Operations
        sampling: SamplingOperations
        sessions: SessionsOperations
        training: TrainingOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        async def close_session(self: FineTuningSessionClient, session_id: str) -> None: ...

        async def create_session(
                self: FineTuningSessionClient, 
                *, 
                base_model: str, 
                from_checkpoint: Optional[FromCheckpoint] = ..., 
                lora_config: Optional[LoRAConfig] = ..., 
                timeout_sec: float = 600.0, 
                type: str = "training"
            ) -> str: ...

        async def create_session_from_checkpoint(
                self: FineTuningSessionClient, 
                *, 
                base_model: str, 
                checkpoint_path: str, 
                lora_config: Optional[LoRAConfig] = ..., 
                timeout_sec: float = 600.0, 
                type: str = "training"
            ) -> str: ...

        async def forward(
                self: FineTuningSessionClient, 
                session_id: str, 
                batch: List[Datum], 
                *, 
                loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY, 
                loss_fn_config: Optional[LossFnConfig] = ...
            ) -> OperationResult: ...

        async def forward_async(
                self: FineTuningSessionClient, 
                session_id: str, 
                batch: List[Datum], 
                *, 
                loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY, 
                loss_fn_config: Optional[LossFnConfig] = ...
            ) -> Task[OperationResult]: ...

        async def forward_backward(
                self: FineTuningSessionClient, 
                session_id: str, 
                batch: List[Datum], 
                *, 
                loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY, 
                loss_fn_config: Optional[LossFnConfig] = ...
            ) -> OperationResult: ...

        async def forward_backward_async(
                self: FineTuningSessionClient, 
                session_id: str, 
                batch: List[Datum], 
                *, 
                loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY, 
                loss_fn_config: Optional[LossFnConfig] = ...
            ) -> Task[OperationResult]: ...

        async def forward_backward_post(
                self: FineTuningSessionClient, 
                session_id: str, 
                batch: List[Datum], 
                *, 
                loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY, 
                loss_fn_config: Optional[LossFnConfig] = ...
            ) -> PendingRequests: ...

        async def forward_post(
                self: FineTuningSessionClient, 
                session_id: str, 
                batch: List[Datum], 
                *, 
                loss_fn: Union[str, LossFn] = LossFn.CROSS_ENTROPY, 
                loss_fn_config: Optional[LossFnConfig] = ...
            ) -> PendingRequests: ...

        async def optim_step(
                self: FineTuningSessionClient, 
                session_id: str, 
                adam_params: AdamParams
            ) -> OperationResult: ...

        async def optim_step_async(
                self: FineTuningSessionClient, 
                session_id: str, 
                adam_params: AdamParams
            ) -> Task[OperationResult]: ...

        async def optim_step_post(
                self: FineTuningSessionClient, 
                session_id: str, 
                adam_params: AdamParams
            ) -> PendingRequests: ...

        async def sample(
                self: FineTuningSessionClient, 
                session_id: str, 
                prompt_tokens: List[int], 
                sampling_params: SamplingParams, 
                *, 
                checkpoint_id: str, 
                num_samples: int = 1, 
                prompt_logprobs: bool = False, 
                prompt_token_ids: bool = False, 
                sampling_session_id: Optional[str] = ..., 
                seq_id: Optional[int] = ..., 
                topk_prompt_logprobs: int = 0
            ) -> OperationResult: ...

        async def save_weights(
                self: FineTuningSessionClient, 
                session_id: str, 
                path: str
            ) -> OperationResult: ...

        async def save_weights_and_get_sampling_client_async(
                self: FineTuningSessionClient, 
                session_id: str, 
                name: str
            ) -> Task[OperationResult]: ...

        async def save_weights_async(
                self: FineTuningSessionClient, 
                session_id: str, 
                path: str, 
                *, 
                metrics: Optional[Dict[str, Any]] = ..., 
                step_number: Optional[int] = ...
            ) -> Task[OperationResult]: ...

        async def save_weights_for_sampler_async(
                self: FineTuningSessionClient, 
                session_id: str, 
                name: str
            ) -> Task[OperationResult]: ...

        async def save_weights_post(
                self: FineTuningSessionClient, 
                session_id: str, 
                path: str, 
                *, 
                metrics: Optional[Dict[str, Any]] = ..., 
                step_number: Optional[int] = ...
            ) -> PendingRequests: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.ai.finetuning_sessions.aio.operations

    class azure.ai.finetuning_sessions.aio.operations.CheckpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_save(
                self, 
                session_id: str, 
                body: SaveCheckpointRequest, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_save(
                self, 
                session_id: str, 
                body: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_save(
                self, 
                session_id: str, 
                body: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_save_sampler_weights(
                self, 
                session_id: str, 
                body: SaveSamplerWeightsRequest, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_save_sampler_weights(
                self, 
                session_id: str, 
                body: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_save_sampler_weights(
                self, 
                session_id: str, 
                body: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        async def get(
                self, 
                session_id: str, 
                checkpoint_id: str, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> CheckpointInfo: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        async def list(
                self, 
                session_id: str, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> CheckpointList: ...


    class azure.ai.finetuning_sessions.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        async def get(
                self, 
                session_id: str, 
                operation_id: str, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> OperationResult: ...


    class azure.ai.finetuning_sessions.aio.operations.SamplingOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_sample(
                self, 
                session_id: str, 
                body: SampleRequest, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_sample(
                self, 
                session_id: str, 
                body: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_sample(
                self, 
                session_id: str, 
                body: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...


    class azure.ai.finetuning_sessions.aio.operations.SessionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                body: CreateSessionRequest, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_create(
                self, 
                body: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_create(
                self, 
                body: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        async def begin_unload(
                self, 
                session_id: str, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        async def create(
                self, 
                body: Union[CreateSessionRequest, JSON, IO[bytes]], 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        async def get(
                self, 
                session_id: str, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> Session: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        async def heartbeat(
                self, 
                session_id: str, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> HeartbeatResponse: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        async def list(
                self, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                **kwargs: Any
            ) -> SessionList: ...


    class azure.ai.finetuning_sessions.aio.operations.TrainingOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_forward_backward(
                self, 
                session_id: str, 
                body: ForwardBackwardRequest, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_forward_backward(
                self, 
                session_id: str, 
                body: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_forward_backward(
                self, 
                session_id: str, 
                body: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_optim_step(
                self, 
                session_id: str, 
                body: OptimStepRequest, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_optim_step(
                self, 
                session_id: str, 
                body: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...

        @overload
        async def begin_optim_step(
                self, 
                session_id: str, 
                body: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResult]: ...


namespace azure.ai.finetuning_sessions.models

    class azure.ai.finetuning_sessions.models.AdamParams(_Model):
        beta1: float
        beta2: float
        eps: float
        learning_rate: float
        weight_decay: float

        @overload
        def __init__(
                self, 
                *, 
                beta1: float, 
                beta2: float, 
                eps: float, 
                learning_rate: float, 
                weight_decay: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.ApiError(_Model):
        additional_info: Optional[dict[str, Any]]
        code: str
        debug_info: Optional[dict[str, Any]]
        details: Optional[list[ApiError]]
        message: str
        param: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[dict[str, Any]] = ..., 
                code: str, 
                debug_info: Optional[dict[str, Any]] = ..., 
                details: Optional[list[ApiError]] = ..., 
                message: str, 
                param: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.ApiErrorResponse(_Model):
        error: ApiError

        @overload
        def __init__(
                self, 
                *, 
                error: ApiError
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.Checkpoint(_Model):
        checkpoint_id: str
        checkpoint_type: Union[str, CheckpointType]
        time: datetime


    class azure.ai.finetuning_sessions.models.CheckpointInfo(_Model):
        base_model: str
        is_lora: bool
        lora_rank: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                base_model: str, 
                is_lora: bool, 
                lora_rank: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.CheckpointList(_Model):
        checkpoints: list[Checkpoint]

        @overload
        def __init__(
                self, 
                *, 
                checkpoints: list[Checkpoint]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.CheckpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SAMPLER = "sampler"
        TRAINING = "training"


    class azure.ai.finetuning_sessions.models.CreateSessionRequest(_Model):
        base_model: str
        ejectable: Optional[bool]
        lora_config: Optional[LoRAConfig]
        type: Union[str, SessionType]
        user_metadata: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                base_model: str, 
                ejectable: Optional[bool] = ..., 
                lora_config: Optional[LoRAConfig] = ..., 
                type: Union[str, SessionType], 
                user_metadata: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.Cursor(_Model):
        limit: int
        offset: int
        total_count: int

        @overload
        def __init__(
                self, 
                *, 
                limit: int, 
                offset: int, 
                total_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.Datum(_Model):
        loss_fn_inputs: LossFnInputs
        model_input: ModelInput

        @overload
        def __init__(
                self, 
                *, 
                loss_fn_inputs: LossFnInputs, 
                model_input: ModelInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.ForwardBackwardInput(_Model):
        data: list[Datum]
        loss_fn: Union[str, LossFn]
        loss_fn_config: Optional[LossFnConfig]

        @overload
        def __init__(
                self, 
                *, 
                data: list[Datum], 
                loss_fn: Union[str, LossFn], 
                loss_fn_config: Optional[LossFnConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.ForwardBackwardOperationResult(OperationResult, discriminator='forward_backward'):
        metrics: Optional[dict[str, float]]
        operation_id: str
        per_datum_logprobs: Optional[list[TensorData]]
        status: Union[str, OperationStatus]
        total_loss: float
        type: Literal[OperationType.FORWARD_BACKWARD]

        @overload
        def __init__(
                self, 
                *, 
                metrics: Optional[dict[str, float]] = ..., 
                per_datum_logprobs: Optional[list[TensorData]] = ..., 
                total_loss: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.ForwardBackwardRequest(_Model):
        forward_backward_input: ForwardBackwardInput

        @overload
        def __init__(
                self, 
                *, 
                forward_backward_input: ForwardBackwardInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.ForwardInput(ForwardBackwardInput):

        @overload
        def __init__(
                self, 
                *, 
                data: list[Datum], 
                loss_fn: Union[str, LossFn], 
                loss_fn_config: Optional[LossFnConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.ForwardRequest(_Model):
        forward_input: ForwardInput

        @overload
        def __init__(
                self, 
                *, 
                forward_input: ForwardInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.FoundryFeaturesOptInKeys(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVALUATIONS_V1_PREVIEW = "Evaluations=V1Preview"
        FINETUNING_SESSIONS_V1_PREVIEW = "FineTuningSessions=V1Preview"
        INSIGHTS_V1_PREVIEW = "Insights=V1Preview"
        MEMORY_STORES_V1_PREVIEW = "MemoryStores=V1Preview"
        RED_TEAMS_V1_PREVIEW = "RedTeams=V1Preview"
        SCHEDULES_V1_PREVIEW = "Schedules=V1Preview"


    class azure.ai.finetuning_sessions.models.FromCheckpoint(_Model):
        checkpoint_id: str
        source_session_id: str

        @overload
        def __init__(
                self, 
                *, 
                checkpoint_id: str, 
                source_session_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.HeartbeatResponse(_Model):
        session_id: str

        @overload
        def __init__(
                self, 
                *, 
                session_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.LoRAConfig(_Model):
        alpha: Optional[float]
        rank: Optional[int]
        seed: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                alpha: Optional[float] = ..., 
                rank: Optional[int] = ..., 
                seed: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.LossFn(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CISPO = "cispo"
        CROSS_ENTROPY = "cross_entropy"
        IMPORTANCE_SAMPLING = "importance_sampling"
        PPO = "ppo"
        SAPO = "sapo"


    class azure.ai.finetuning_sessions.models.LossFnConfig(_Model):
        clip_high_threshold: Optional[float]
        clip_low_threshold: Optional[float]
        tau_neg: Optional[float]
        tau_pos: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                clip_high_threshold: Optional[float] = ..., 
                clip_low_threshold: Optional[float] = ..., 
                tau_neg: Optional[float] = ..., 
                tau_pos: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.LossFnInputs(_Model):
        advantages: Optional[TensorData]
        logprobs: Optional[TensorData]
        target_tokens: TensorData
        weights: TensorData

        @overload
        def __init__(
                self, 
                *, 
                advantages: Optional[TensorData] = ..., 
                logprobs: Optional[TensorData] = ..., 
                target_tokens: TensorData, 
                weights: TensorData
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.ModelInput(_Model):
        chunks: list[ModelInputChunk]

        @overload
        def __init__(
                self, 
                *, 
                chunks: list[ModelInputChunk]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.ModelInputChunk(_Model):
        tokens: list[int]

        @overload
        def __init__(
                self, 
                *, 
                tokens: list[int]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.OperationResult(_Model):
        operation_id: str
        status: Union[str, OperationStatus]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "failed"
        RUNNING = "running"
        SUCCEEDED = "succeeded"


    class azure.ai.finetuning_sessions.models.OperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FORWARD_BACKWARD = "forward_backward"
        OPTIM_STEP = "optim_step"
        SAMPLE = "sample"
        SAVE_CHECKPOINT = "save_checkpoint"
        SAVE_SAMPLER_WEIGHTS = "save_sampler_weights"


    class azure.ai.finetuning_sessions.models.OptimStepOperationResult(OperationResult, discriminator='optim_step'):
        grad_norm: float
        metrics: Optional[dict[str, float]]
        operation_id: str
        status: Union[str, OperationStatus]
        step_count: int
        type: Literal[OperationType.OPTIM_STEP]

        @overload
        def __init__(
                self, 
                *, 
                grad_norm: float, 
                metrics: Optional[dict[str, float]] = ..., 
                step_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.OptimStepRequest(_Model):
        adam_params: AdamParams

        @overload
        def __init__(
                self, 
                *, 
                adam_params: AdamParams
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.SampleOperationResult(OperationResult, discriminator='sample'):
        operation_id: str
        prompt_token_ids: Optional[list[int]]
        sequences: list[SampledSequence]
        status: Union[str, OperationStatus]
        type: Literal[OperationType.SAMPLE]

        @overload
        def __init__(
                self, 
                *, 
                prompt_token_ids: Optional[list[int]] = ..., 
                sequences: list[SampledSequence]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.SampleRequest(_Model):
        num_samples: int
        prompt: ModelInput
        prompt_logprobs: Optional[bool]
        prompt_token_ids: Optional[bool]
        sampling_params: SamplingParams
        sampling_session_id: Optional[str]
        seq_id: Optional[int]
        topk_prompt_logprobs: int

        @overload
        def __init__(
                self, 
                *, 
                num_samples: int, 
                prompt: ModelInput, 
                prompt_logprobs: Optional[bool] = ..., 
                prompt_token_ids: Optional[bool] = ..., 
                sampling_params: SamplingParams, 
                sampling_session_id: Optional[str] = ..., 
                seq_id: Optional[int] = ..., 
                topk_prompt_logprobs: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.SampledSequence(_Model):
        logprobs: Optional[list[float]]
        prompt_logprobs: Optional[list[float]]
        text: Optional[str]
        tokens: list[int]

        @overload
        def __init__(
                self, 
                *, 
                logprobs: Optional[list[float]] = ..., 
                prompt_logprobs: Optional[list[float]] = ..., 
                text: Optional[str] = ..., 
                tokens: list[int]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.SamplingParams(_Model):
        max_tokens: int
        seed: Optional[int]
        stop_criteria: Optional[StopCriteria]
        temperature: float
        top_k: int
        top_p: float

        @overload
        def __init__(
                self, 
                *, 
                max_tokens: int, 
                seed: Optional[int] = ..., 
                stop_criteria: Optional[StopCriteria] = ..., 
                temperature: float, 
                top_k: int, 
                top_p: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.SaveCheckpointOperationResult(OperationResult, discriminator='save_checkpoint'):
        checkpoint_id: str
        operation_id: str
        path: str
        status: Union[str, OperationStatus]
        type: Literal[OperationType.SAVE_CHECKPOINT]

        @overload
        def __init__(
                self, 
                *, 
                checkpoint_id: str, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.SaveCheckpointRequest(_Model):
        metrics: Optional[dict[str, Any]]
        path: str
        step_number: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                metrics: Optional[dict[str, Any]] = ..., 
                path: str, 
                step_number: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.SaveSamplerWeightsOperationResult(OperationResult, discriminator='save_sampler_weights'):
        checkpoint_id: str
        operation_id: str
        sampling_session_id: str
        status: Union[str, OperationStatus]
        type: Literal[OperationType.SAVE_SAMPLER_WEIGHTS]

        @overload
        def __init__(
                self, 
                *, 
                checkpoint_id: str, 
                sampling_session_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.SaveSamplerWeightsRequest(_Model):
        path: Optional[str]
        sampling_session_seq_id: Optional[int]
        seq_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                path: Optional[str] = ..., 
                sampling_session_seq_id: Optional[int] = ..., 
                seq_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.Session(_Model):
        model_data: SessionModelData
        session_id: str
        status: Union[str, SessionStatus]
        type: Union[str, SessionType]

        @overload
        def __init__(
                self, 
                *, 
                model_data: SessionModelData, 
                type: Union[str, SessionType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.SessionList(_Model):
        cursor: Cursor
        data: list[SessionSummary]

        @overload
        def __init__(
                self, 
                *, 
                cursor: Cursor, 
                data: list[SessionSummary]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.SessionModelData(_Model):
        base_model: str
        lora_config: Optional[LoRAConfig]
        model_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                base_model: str, 
                lora_config: Optional[LoRAConfig] = ..., 
                model_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.SessionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "failed"
        QUEUED = "queued"
        RUNNING = "running"
        SUCCEEDED = "succeeded"


    class azure.ai.finetuning_sessions.models.SessionSummary(_Model):
        base_model: str
        corrupted: bool
        is_lora: bool
        last_request_time: datetime
        lora_rank: Optional[int]
        session_id: str
        status: Union[str, SessionStatus]

        @overload
        def __init__(
                self, 
                *, 
                base_model: str, 
                corrupted: bool, 
                is_lora: bool, 
                lora_rank: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.finetuning_sessions.models.SessionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TRAINING = "training"


    class azure.ai.finetuning_sessions.models.TensorData(_Model):
        data: list[float]

        @overload
        def __init__(
                self, 
                *, 
                data: list[float]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.ai.finetuning_sessions.operations

    class azure.ai.finetuning_sessions.operations.CheckpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_save(
                self, 
                session_id: str, 
                body: SaveCheckpointRequest, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_save(
                self, 
                session_id: str, 
                body: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_save(
                self, 
                session_id: str, 
                body: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_save_sampler_weights(
                self, 
                session_id: str, 
                body: SaveSamplerWeightsRequest, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_save_sampler_weights(
                self, 
                session_id: str, 
                body: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_save_sampler_weights(
                self, 
                session_id: str, 
                body: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        def get(
                self, 
                session_id: str, 
                checkpoint_id: str, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> CheckpointInfo: ...

        @distributed_trace
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        def list(
                self, 
                session_id: str, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> CheckpointList: ...


    class azure.ai.finetuning_sessions.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        def get(
                self, 
                session_id: str, 
                operation_id: str, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> OperationResult: ...


    class azure.ai.finetuning_sessions.operations.SamplingOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_sample(
                self, 
                session_id: str, 
                body: SampleRequest, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_sample(
                self, 
                session_id: str, 
                body: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_sample(
                self, 
                session_id: str, 
                body: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...


    class azure.ai.finetuning_sessions.operations.SessionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                body: CreateSessionRequest, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_create(
                self, 
                body: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_create(
                self, 
                body: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        def begin_unload(
                self, 
                session_id: str, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        def create(
                self, 
                body: Union[CreateSessionRequest, JSON, IO[bytes]], 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        def get(
                self, 
                session_id: str, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> Session: ...

        @distributed_trace
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        def heartbeat(
                self, 
                session_id: str, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> HeartbeatResponse: ...

        @distributed_trace
        @api_version_validation(params_added_on={'virtual-public-preview': ['foundry_features', 'api_version']})
        def list(
                self, 
                *, 
                api_version: str, 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                **kwargs: Any
            ) -> SessionList: ...


    class azure.ai.finetuning_sessions.operations.TrainingOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_forward_backward(
                self, 
                session_id: str, 
                body: ForwardBackwardRequest, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_forward_backward(
                self, 
                session_id: str, 
                body: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_forward_backward(
                self, 
                session_id: str, 
                body: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_optim_step(
                self, 
                session_id: str, 
                body: OptimStepRequest, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_optim_step(
                self, 
                session_id: str, 
                body: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...

        @overload
        def begin_optim_step(
                self, 
                session_id: str, 
                body: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW], 
                **kwargs: Any
            ) -> LROPoller[OperationResult]: ...


```