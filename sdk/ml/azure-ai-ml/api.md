```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.ml

    def azure.ai.ml.command(
            *, 
            code: Optional[Union[str, PathLike]] = ..., 
            command: Optional[str] = ..., 
            compute: Optional[str] = ..., 
            description: Optional[str] = ..., 
            display_name: Optional[str] = ..., 
            distribution: Optional[Union[Dict, MpiDistribution, TensorFlowDistribution, PyTorchDistribution, RayDistribution, DistributionConfiguration]] = ..., 
            docker_args: Optional[Union[str, List[str]]] = ..., 
            environment: Optional[Union[str, Environment]] = ..., 
            environment_variables: Optional[Dict] = ..., 
            experiment_name: Optional[str] = ..., 
            identity: Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]] = ..., 
            inputs: Optional[Dict] = ..., 
            instance_count: Optional[int] = ..., 
            instance_type: Optional[str] = ..., 
            is_deterministic: bool = True, 
            job_tier: Optional[str] = ..., 
            locations: Optional[List[str]] = ..., 
            name: Optional[str] = ..., 
            outputs: Optional[Dict] = ..., 
            parent_job_name: Optional[str] = ..., 
            priority: Optional[str] = ..., 
            properties: Optional[Dict] = ..., 
            services: Optional[Dict[str, Union[JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService]]] = ..., 
            shm_size: Optional[str] = ..., 
            tags: Optional[Dict] = ..., 
            timeout: Optional[int] = ..., 
            **kwargs: Any
        ) -> Command: ...


    def azure.ai.ml.load_batch_deployment(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> BatchDeployment: ...


    def azure.ai.ml.load_batch_endpoint(
            source: Union[str, PathLike, IO[AnyStr]], 
            relative_origin: Optional[str] = None, 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            **kwargs: Any
        ) -> BatchEndpoint: ...


    def azure.ai.ml.load_capability_host(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> CapabilityHost: ...


    def azure.ai.ml.load_component(
            source: Optional[Union[str, PathLike, IO[AnyStr]]] = None, 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> Union[CommandComponent, ParallelComponent, PipelineComponent]: ...


    def azure.ai.ml.load_compute(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict[str, str]]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> Compute: ...


    def azure.ai.ml.load_connection(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> WorkspaceConnection: ...


    def azure.ai.ml.load_data(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> Data: ...


    def azure.ai.ml.load_datastore(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> Datastore: ...


    @experimental
    def azure.ai.ml.load_deployment_template(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> DeploymentTemplate: ...


    def azure.ai.ml.load_environment(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> Environment: ...


    def azure.ai.ml.load_feature_set(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> FeatureSet: ...


    def azure.ai.ml.load_feature_store(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> FeatureStore: ...


    def azure.ai.ml.load_feature_store_entity(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> FeatureStoreEntity: ...


    @experimental
    def azure.ai.ml.load_index(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> Index: ...


    def azure.ai.ml.load_job(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> Job: ...


    @experimental
    def azure.ai.ml.load_marketplace_subscription(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> MarketplaceSubscription: ...


    def azure.ai.ml.load_model(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> Model: ...


    @experimental
    def azure.ai.ml.load_model_package(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> ModelPackage: ...


    def azure.ai.ml.load_online_deployment(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> OnlineDeployment: ...


    def azure.ai.ml.load_online_endpoint(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> OnlineEndpoint: ...


    def azure.ai.ml.load_registry(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> Registry: ...


    @experimental
    def azure.ai.ml.load_serverless_endpoint(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> ServerlessEndpoint: ...


    def azure.ai.ml.load_workspace(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            params_override: Optional[List[Dict]] = ..., 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> Workspace: ...


    def azure.ai.ml.load_workspace_connection(
            source: Union[str, PathLike, IO[AnyStr]], 
            *, 
            relative_origin: Optional[str] = ..., 
            **kwargs: Any
        ) -> WorkspaceConnection: ...


    def azure.ai.ml.spark(
            *, 
            archives: Optional[List[str]] = ..., 
            args: Optional[str] = ..., 
            code: Optional[Union[str, PathLike]] = ..., 
            compute: Optional[str] = ..., 
            conf: Optional[Dict[str, str]] = ..., 
            description: Optional[str] = ..., 
            display_name: Optional[str] = ..., 
            driver_cores: Optional[int] = ..., 
            driver_memory: Optional[str] = ..., 
            dynamic_allocation_enabled: Optional[bool] = ..., 
            dynamic_allocation_max_executors: Optional[int] = ..., 
            dynamic_allocation_min_executors: Optional[int] = ..., 
            entry: Union[Dict[str, str], SparkJobEntry, None] = ..., 
            environment: Optional[Union[str, Environment]] = ..., 
            executor_cores: Optional[int] = ..., 
            executor_instances: Optional[int] = ..., 
            executor_memory: Optional[str] = ..., 
            experiment_name: Optional[str] = ..., 
            files: Optional[List[str]] = ..., 
            identity: Optional[Union[Dict[str, str], ManagedIdentity, AmlToken, UserIdentity]] = ..., 
            inputs: Optional[Dict] = ..., 
            jars: Optional[List[str]] = ..., 
            name: Optional[str] = ..., 
            outputs: Optional[Dict] = ..., 
            py_files: Optional[List[str]] = ..., 
            resources: Optional[Union[Dict, SparkResourceConfiguration]] = ..., 
            tags: Optional[Dict] = ..., 
            **kwargs: Any
        ) -> Spark: ...


    class azure.ai.ml.Input(_InputOutputBase): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        @overload
        def __init__(
                self, 
                *, 
                datastore: str = ..., 
                default: Union[str, int, float, bool] = ..., 
                description: Optional[str] = ..., 
                intellectual_property: IntellectualProperty = ..., 
                max: Union[int, float] = ..., 
                min: Union[int, float] = ..., 
                mode: Optional[str] = ..., 
                optional: Optional[bool] = ..., 
                path: Optional[str] = ..., 
                path_on_compute: Optional[str] = ..., 
                type: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def __init__(
                self, 
                *, 
                datastore: str = ..., 
                default: Optional[float] = ..., 
                description: Optional[str] = ..., 
                intellectual_property: IntellectualProperty = ..., 
                max: Optional[float] = ..., 
                min: Optional[float] = ..., 
                mode: Optional[str] = ..., 
                optional: Optional[bool] = ..., 
                path: Optional[str] = ..., 
                path_on_compute: Optional[str] = ..., 
                type: Literal["number"] = "number", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def __init__(
                self, 
                *, 
                datastore: str = ..., 
                default: Optional[int] = ..., 
                description: Optional[str] = ..., 
                intellectual_property: IntellectualProperty = ..., 
                max: Optional[int] = ..., 
                min: Optional[int] = ..., 
                mode: Optional[str] = ..., 
                optional: Optional[bool] = ..., 
                path: Optional[str] = ..., 
                path_on_compute: Optional[str] = ..., 
                type: Literal["integer"] = "integer", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def __init__(
                self, 
                *, 
                datastore: str = ..., 
                default: Optional[str] = ..., 
                description: Optional[str] = ..., 
                intellectual_property: IntellectualProperty = ..., 
                max: Union[int, float] = ..., 
                min: Union[int, float] = ..., 
                mode: Optional[str] = ..., 
                optional: Optional[bool] = ..., 
                path: Optional[str] = ..., 
                path_on_compute: Optional[str] = ..., 
                type: Literal["string"] = "string", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def __init__(
                self, 
                *, 
                datastore: str = ..., 
                default: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                intellectual_property: IntellectualProperty = ..., 
                max: Union[int, float] = ..., 
                min: Union[int, float] = ..., 
                mode: Optional[str] = ..., 
                optional: Optional[bool] = ..., 
                path: Optional[str] = ..., 
                path_on_compute: Optional[str] = ..., 
                type: Literal["boolean"] = "boolean", 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.MLClient:
        property azure_openai_deployments: AzureOpenAIDeploymentOperations    # Read-only
        property batch_deployments: BatchDeploymentOperations    # Read-only
        property batch_endpoints: BatchEndpointOperations    # Read-only
        property capability_hosts: CapabilityHostsOperations    # Read-only
        property components: ComponentOperations    # Read-only
        property compute: ComputeOperations    # Read-only
        property connections: WorkspaceConnectionsOperations    # Read-only
        property data: DataOperations    # Read-only
        property datastores: DatastoreOperations    # Read-only
        property deployment_templates: DeploymentTemplateOperations    # Read-only
        property environments: EnvironmentOperations    # Read-only
        property evaluators: EvaluatorOperations    # Read-only
        property feature_sets: FeatureSetOperations    # Read-only
        property feature_store_entities: FeatureStoreEntityOperations    # Read-only
        property feature_stores: FeatureStoreOperations    # Read-only
        property indexes: IndexOperations    # Read-only
        property jobs: JobOperations    # Read-only
        property marketplace_subscriptions: MarketplaceSubscriptionOperations    # Read-only
        property models: ModelOperations    # Read-only
        property online_deployments: OnlineDeploymentOperations    # Read-only
        property online_endpoints: OnlineEndpointOperations    # Read-only
        property registries: RegistryOperations    # Read-only
        property resource_group_name: str    # Read-only
        property schedules: ScheduleOperations    # Read-only
        property serverless_endpoints: ServerlessEndpointOperations    # Read-only
        property subscription_id: str    # Read-only
        property workspace_name: Optional[str]    # Read-only
        property workspace_outbound_rules: WorkspaceOutboundRuleOperations    # Read-only
        property workspaces: WorkspaceOperations    # Read-only

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: Optional[str] = None, 
                resource_group_name: Optional[str] = None, 
                workspace_name: Optional[str] = None, 
                registry_name: Optional[str] = None, 
                *, 
                cloud: Optional[str] = ..., 
                enable_telemetry: Optional[bool] = ..., 
                show_progress: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_config(
                cls, 
                credential: TokenCredential, 
                *, 
                cloud: Optional[str] = ..., 
                file_name: Optional[str] = ..., 
                path: Optional[Union[PathLike, str]] = ..., 
                **kwargs
            ) -> MLClient: ...

        def begin_create_or_update(
                self, 
                entity: R, 
                **kwargs
            ) -> LROPoller[R]: ...

        def create_or_update(
                self, 
                entity: T, 
                **kwargs
            ) -> T: ...


    class azure.ai.ml.MpiDistribution(DistributionConfiguration):
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                process_count_per_instance: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.Output(_InputOutputBase): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[str] = ..., 
                path: Optional[str] = ..., 
                type: str, 
                **kwargs: Any
            ): ...

        @overload
        def __init__(
                self, 
                type: Literal["uri_file"] = "uri_file", 
                path: Optional[str] = None, 
                mode: Optional[str] = None, 
                description: Optional[str] = None
            ): ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.PyTorchDistribution(DistributionConfiguration):
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                process_count_per_instance: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.RayDistribution(DistributionConfiguration):
        address: str
        dashboard_port: int
        head_node_additional_args: str
        include_dashboard: bool
        port: int
        type: str
        worker_node_additional_args: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                dashboard_port: Optional[int] = ..., 
                head_node_additional_args: Optional[str] = ..., 
                include_dashboard: Optional[bool] = ..., 
                port: Optional[int] = ..., 
                worker_node_additional_args: Optional[str] = ..., 
                **kwargs: Any
            ): ...


    class azure.ai.ml.TensorFlowDistribution(DistributionConfiguration):
        parameter_server_count: int
        type: str
        worker_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameter_server_count: Optional[int] = 0, 
                worker_count: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


namespace azure.ai.ml.automl

    @pipeline_node_decorator
    def azure.ai.ml.automl.classification(
            *, 
            cv_split_column_names: Optional[List[str]] = ..., 
            enable_model_explainability: Optional[bool] = ..., 
            n_cross_validations: Optional[Union[str, int]] = ..., 
            primary_metric: Optional[str] = ..., 
            target_column_name: str, 
            test_data: Optional[Input] = ..., 
            test_data_size: Optional[float] = ..., 
            training_data: Input, 
            validation_data: Optional[Input] = ..., 
            validation_data_size: Optional[float] = ..., 
            weight_column_name: Optional[str] = ..., 
            **kwargs
        ) -> ClassificationJob: ...


    @pipeline_node_decorator
    def azure.ai.ml.automl.forecasting(
            *, 
            cv_split_column_names: Optional[List[str]] = ..., 
            enable_model_explainability: Optional[bool] = ..., 
            forecasting_settings: Optional[ForecastingSettings] = ..., 
            n_cross_validations: Optional[Union[str, int]] = ..., 
            primary_metric: Optional[str] = ..., 
            target_column_name: str, 
            test_data: Optional[Input] = ..., 
            test_data_size: Optional[float] = ..., 
            training_data: Input, 
            validation_data: Optional[Input] = ..., 
            validation_data_size: Optional[float] = ..., 
            weight_column_name: Optional[str] = ..., 
            **kwargs
        ) -> ForecastingJob: ...


    @pipeline_node_decorator
    def azure.ai.ml.automl.image_classification(
            *, 
            primary_metric: Optional[Union[str, ClassificationPrimaryMetrics]] = ..., 
            target_column_name: str, 
            training_data: Input, 
            validation_data: Optional[Input] = ..., 
            validation_data_size: Optional[float] = ..., 
            **kwargs
        ) -> ImageClassificationJob: ...


    @pipeline_node_decorator
    def azure.ai.ml.automl.image_classification_multilabel(
            *, 
            primary_metric: Optional[Union[str, ClassificationMultilabelPrimaryMetrics]] = ..., 
            target_column_name: str, 
            training_data: Input, 
            validation_data: Optional[Input] = ..., 
            validation_data_size: Optional[float] = ..., 
            **kwargs
        ) -> ImageClassificationMultilabelJob: ...


    @pipeline_node_decorator
    def azure.ai.ml.automl.image_instance_segmentation(
            *, 
            primary_metric: Optional[Union[str, InstanceSegmentationPrimaryMetrics]] = ..., 
            target_column_name: str, 
            training_data: Input, 
            validation_data: Optional[Input] = ..., 
            validation_data_size: Optional[float] = ..., 
            **kwargs
        ) -> ImageInstanceSegmentationJob: ...


    @pipeline_node_decorator
    def azure.ai.ml.automl.image_object_detection(
            *, 
            primary_metric: Optional[Union[str, ObjectDetectionPrimaryMetrics]] = ..., 
            target_column_name: str, 
            training_data: Input, 
            validation_data: Optional[Input] = ..., 
            validation_data_size: Optional[float] = ..., 
            **kwargs
        ) -> ImageObjectDetectionJob: ...


    @pipeline_node_decorator
    def azure.ai.ml.automl.regression(
            *, 
            cv_split_column_names: Optional[List[str]] = ..., 
            enable_model_explainability: Optional[bool] = ..., 
            n_cross_validations: Optional[Union[str, int]] = ..., 
            primary_metric: Optional[str] = ..., 
            target_column_name: str, 
            test_data: Optional[Input] = ..., 
            test_data_size: Optional[float] = ..., 
            training_data: Input, 
            validation_data: Optional[Input] = ..., 
            validation_data_size: Optional[float] = ..., 
            weight_column_name: Optional[str] = ..., 
            **kwargs
        ) -> RegressionJob: ...


    @pipeline_node_decorator
    def azure.ai.ml.automl.text_classification(
            *, 
            log_verbosity: Optional[str] = ..., 
            primary_metric: Optional[str] = ..., 
            target_column_name: str, 
            training_data: Input, 
            validation_data: Input, 
            **kwargs
        ) -> TextClassificationJob: ...


    @pipeline_node_decorator
    def azure.ai.ml.automl.text_classification_multilabel(
            *, 
            log_verbosity: Optional[str] = ..., 
            primary_metric: Optional[str] = ..., 
            target_column_name: str, 
            training_data: Input, 
            validation_data: Input, 
            **kwargs
        ) -> TextClassificationMultilabelJob: ...


    @pipeline_node_decorator
    def azure.ai.ml.automl.text_ner(
            *, 
            log_verbosity: Optional[str] = ..., 
            primary_metric: Optional[str] = ..., 
            training_data: Input, 
            validation_data: Input, 
            **kwargs
        ) -> TextNerJob: ...


    class azure.ai.ml.automl.BlockedTransformers(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAT_TARGET_ENCODER = "CatTargetEncoder"
        COUNT_VECTORIZER = "CountVectorizer"
        HASH_ONE_HOT_ENCODER = "HashOneHotEncoder"
        LABEL_ENCODER = "LabelEncoder"
        NAIVE_BAYES = "NaiveBayes"
        ONE_HOT_ENCODER = "OneHotEncoder"
        TEXT_TARGET_ENCODER = "TextTargetEncoder"
        TF_IDF = "TfIdf"
        WORD_EMBEDDING = "WordEmbedding"
        WO_E_TARGET_ENCODER = "WoETargetEncoder"


    class azure.ai.ml.automl.ClassificationJob(AutoMLTabular):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property featurization: Optional[TabularFeaturizationSettings]
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property limits: Optional[TabularLimitSettings]
        property log_files: Optional[Dict[str, str]]    # Read-only
        property log_verbosity: LogVerbosity
        property outputs: Dict[str, Output]
        property primary_metric: Union[str, ClassificationPrimaryMetrics]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property task_type: str
        property test_data: Input
        property training: ClassificationTrainingSettings
        property training_data: Input
        property type: Optional[str]    # Read-only
        property validation_data: Input

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                featurization: Optional[TabularFeaturizationSettings] = ..., 
                limits: Optional[TabularLimitSettings] = ..., 
                positive_label: Optional[str] = ..., 
                primary_metric: Optional[str] = ..., 
                training: Optional[TrainingSettings] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def set_data(
                self, 
                *, 
                cv_split_column_names: Optional[List[str]] = ..., 
                n_cross_validations: Optional[Union[str, int]] = ..., 
                target_column_name: str, 
                test_data: Optional[Input] = ..., 
                test_data_size: Optional[float] = ..., 
                training_data: Input, 
                validation_data: Optional[Input] = ..., 
                validation_data_size: Optional[float] = ..., 
                weight_column_name: Optional[str] = ...
            ) -> None: ...

        def set_featurization(
                self, 
                *, 
                blocked_transformers: Optional[List[Union[BlockedTransformers, str]]] = ..., 
                column_name_and_types: Optional[Dict[str, str]] = ..., 
                dataset_language: Optional[str] = ..., 
                enable_dnn_featurization: Optional[bool] = ..., 
                mode: Optional[str] = ..., 
                transformer_params: Optional[Dict[str, List[ColumnTransformer]]] = ...
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                enable_early_termination: Optional[bool] = ..., 
                exit_score: Optional[float] = ..., 
                max_concurrent_trials: Optional[int] = ..., 
                max_cores_per_trial: Optional[int] = ..., 
                max_nodes: Optional[int] = ..., 
                max_trials: Optional[int] = ..., 
                timeout_minutes: Optional[int] = ..., 
                trial_timeout_minutes: Optional[int] = ...
            ) -> None: ...

        def set_training(
                self, 
                *, 
                allowed_training_algorithms: Optional[List[str]] = ..., 
                blocked_training_algorithms: Optional[List[str]] = ..., 
                enable_dnn_training: Optional[bool] = ..., 
                enable_model_explainability: Optional[bool] = ..., 
                enable_onnx_compatible_models: Optional[bool] = ..., 
                enable_stack_ensemble: Optional[bool] = ..., 
                enable_vote_ensemble: Optional[bool] = ..., 
                ensemble_model_download_timeout: Optional[int] = ..., 
                stack_ensemble_settings: Optional[StackEnsembleSettings] = ..., 
                training_mode: Optional[Union[str, TabularTrainingMode]] = ...
            ) -> None: ...


    class azure.ai.ml.automl.ClassificationModels(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BERNOULLI_NAIVE_BAYES = "BernoulliNaiveBayes"
        DECISION_TREE = "DecisionTree"
        EXTREME_RANDOM_TREES = "ExtremeRandomTrees"
        GRADIENT_BOOSTING = "GradientBoosting"
        KNN = "KNN"
        LIGHT_GBM = "LightGBM"
        LINEAR_SVM = "LinearSVM"
        LOGISTIC_REGRESSION = "LogisticRegression"
        MULTINOMIAL_NAIVE_BAYES = "MultinomialNaiveBayes"
        RANDOM_FOREST = "RandomForest"
        SGD = "SGD"
        SVM = "SVM"
        XG_BOOST_CLASSIFIER = "XGBoostClassifier"


    class azure.ai.ml.automl.ClassificationMultilabelPrimaryMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCURACY = "Accuracy"
        AUC_WEIGHTED = "AUCWeighted"
        AVERAGE_PRECISION_SCORE_WEIGHTED = "AveragePrecisionScoreWeighted"
        IOU = "IOU"
        NORM_MACRO_RECALL = "NormMacroRecall"
        PRECISION_SCORE_WEIGHTED = "PrecisionScoreWeighted"


    class azure.ai.ml.automl.ClassificationPrimaryMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCURACY = "Accuracy"
        AUC_WEIGHTED = "AUCWeighted"
        AVERAGE_PRECISION_SCORE_WEIGHTED = "AveragePrecisionScoreWeighted"
        NORM_MACRO_RECALL = "NormMacroRecall"
        PRECISION_SCORE_WEIGHTED = "PrecisionScoreWeighted"


    class azure.ai.ml.automl.ColumnTransformer(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                fields: Optional[List[str]] = ..., 
                parameters: Optional[Dict[str, Union[str, float]]] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.FeaturizationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        CUSTOM = "Custom"
        OFF = "Off"


    class azure.ai.ml.automl.ForecastHorizonMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        CUSTOM = "Custom"


    class azure.ai.ml.automl.ForecastingJob(AutoMLTabular):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property featurization: Optional[TabularFeaturizationSettings]
        property forecasting_settings: Optional[ForecastingSettings]    # Read-only
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property limits: Optional[TabularLimitSettings]
        property log_files: Optional[Dict[str, str]]    # Read-only
        property log_verbosity: LogVerbosity
        property outputs: Dict[str, Output]
        property primary_metric: Optional[str]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property task_type: str
        property test_data: Input
        property training: ForecastingTrainingSettings
        property training_data: Input
        property type: Optional[str]    # Read-only
        property validation_data: Input

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                forecasting_settings: Optional[ForecastingSettings] = ..., 
                primary_metric: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def set_data(
                self, 
                *, 
                cv_split_column_names: Optional[List[str]] = ..., 
                n_cross_validations: Optional[Union[str, int]] = ..., 
                target_column_name: str, 
                test_data: Optional[Input] = ..., 
                test_data_size: Optional[float] = ..., 
                training_data: Input, 
                validation_data: Optional[Input] = ..., 
                validation_data_size: Optional[float] = ..., 
                weight_column_name: Optional[str] = ...
            ) -> None: ...

        def set_featurization(
                self, 
                *, 
                blocked_transformers: Optional[List[Union[BlockedTransformers, str]]] = ..., 
                column_name_and_types: Optional[Dict[str, str]] = ..., 
                dataset_language: Optional[str] = ..., 
                enable_dnn_featurization: Optional[bool] = ..., 
                mode: Optional[str] = ..., 
                transformer_params: Optional[Dict[str, List[ColumnTransformer]]] = ...
            ) -> None: ...

        def set_forecast_settings(
                self, 
                *, 
                country_or_region_for_holidays: Optional[str] = ..., 
                cv_step_size: Optional[int] = ..., 
                feature_lags: Optional[str] = ..., 
                features_unknown_at_forecast_time: Optional[Union[str, List[str]]] = ..., 
                forecast_horizon: Optional[Union[str, int]] = ..., 
                frequency: Optional[str] = ..., 
                seasonality: Optional[Union[str, int]] = ..., 
                short_series_handling_config: Optional[str] = ..., 
                target_aggregate_function: Optional[str] = ..., 
                target_lags: Optional[Union[str, int, List[int]]] = ..., 
                target_rolling_window_size: Optional[Union[str, int]] = ..., 
                time_column_name: Optional[str] = ..., 
                time_series_id_column_names: Optional[Union[str, List[str]]] = ..., 
                use_stl: Optional[str] = ...
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                enable_early_termination: Optional[bool] = ..., 
                exit_score: Optional[float] = ..., 
                max_concurrent_trials: Optional[int] = ..., 
                max_cores_per_trial: Optional[int] = ..., 
                max_nodes: Optional[int] = ..., 
                max_trials: Optional[int] = ..., 
                timeout_minutes: Optional[int] = ..., 
                trial_timeout_minutes: Optional[int] = ...
            ) -> None: ...

        def set_training(
                self, 
                *, 
                allowed_training_algorithms: Optional[List[str]] = ..., 
                blocked_training_algorithms: Optional[List[str]] = ..., 
                enable_dnn_training: Optional[bool] = ..., 
                enable_model_explainability: Optional[bool] = ..., 
                enable_onnx_compatible_models: Optional[bool] = ..., 
                enable_stack_ensemble: Optional[bool] = ..., 
                enable_vote_ensemble: Optional[bool] = ..., 
                ensemble_model_download_timeout: Optional[int] = ..., 
                stack_ensemble_settings: Optional[StackEnsembleSettings] = ..., 
                training_mode: Optional[Union[str, TabularTrainingMode]] = ...
            ) -> None: ...


    class azure.ai.ml.automl.ForecastingModels(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARIMAX = "Arimax"
        AUTO_ARIMA = "AutoArima"
        AVERAGE = "Average"
        DECISION_TREE = "DecisionTree"
        ELASTIC_NET = "ElasticNet"
        EXPONENTIAL_SMOOTHING = "ExponentialSmoothing"
        EXTREME_RANDOM_TREES = "ExtremeRandomTrees"
        GRADIENT_BOOSTING = "GradientBoosting"
        KNN = "KNN"
        LASSO_LARS = "LassoLars"
        LIGHT_GBM = "LightGBM"
        NAIVE = "Naive"
        PROPHET = "Prophet"
        RANDOM_FOREST = "RandomForest"
        SEASONAL_AVERAGE = "SeasonalAverage"
        SEASONAL_NAIVE = "SeasonalNaive"
        SGD = "SGD"
        TCN_FORECASTER = "TCNForecaster"
        XG_BOOST_REGRESSOR = "XGBoostRegressor"


    class azure.ai.ml.automl.ForecastingPrimaryMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NORMALIZED_MEAN_ABSOLUTE_ERROR = "NormalizedMeanAbsoluteError"
        NORMALIZED_ROOT_MEAN_SQUARED_ERROR = "NormalizedRootMeanSquaredError"
        R2_SCORE = "R2Score"
        SPEARMAN_CORRELATION = "SpearmanCorrelation"


    class azure.ai.ml.automl.ForecastingSettings(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                country_or_region_for_holidays: Optional[str] = ..., 
                cv_step_size: Optional[int] = ..., 
                feature_lags: Optional[str] = ..., 
                features_unknown_at_forecast_time: Optional[Union[str, List[str]]] = ..., 
                forecast_horizon: Optional[Union[str, int]] = ..., 
                frequency: Optional[str] = ..., 
                seasonality: Optional[Union[str, int]] = ..., 
                short_series_handling_config: Optional[str] = ..., 
                target_aggregate_function: Optional[str] = ..., 
                target_lags: Optional[Union[str, int, List[int]]] = ..., 
                target_rolling_window_size: Optional[Union[str, int]] = ..., 
                time_column_name: Optional[str] = ..., 
                time_series_id_column_names: Optional[Union[str, List[str]]] = ..., 
                use_stl: Optional[str] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.ImageClassificationJob(AutoMLImageClassificationBase):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property limits: ImageLimitSettings
        property log_files: Optional[Dict[str, str]]    # Read-only
        property log_verbosity: LogVerbosity
        property outputs: Dict[str, Output]
        property primary_metric: Optional[Union[str, ClassificationPrimaryMetrics]]
        property search_space: Optional[List[ImageClassificationSearchSpace]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property sweep: Optional[ImageSweepSettings]
        property task_type: str
        property test_data: Input
        property training_data: Input
        property training_parameters: Optional[ImageModelSettingsClassification]
        property type: Optional[str]    # Read-only
        property validation_data: Input

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                primary_metric: Optional[Union[str, ClassificationPrimaryMetrics]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def extend_search_space(self, value: Union[SearchSpace, List[SearchSpace]]) -> None: ...

        def set_data(
                self, 
                *, 
                target_column_name: str, 
                training_data: Input, 
                validation_data: Optional[Input] = ..., 
                validation_data_size: Optional[float] = ...
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                max_concurrent_trials: Optional[int] = ..., 
                max_trials: Optional[int] = ..., 
                timeout_minutes: Optional[int] = ...
            ) -> None: ...

        def set_sweep(
                self, 
                *, 
                early_termination: Optional[Union[BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy]] = ..., 
                sampling_algorithm: Union[str, SamplingAlgorithmType.RANDOM, SamplingAlgorithmType.GRID, SamplingAlgorithmType.BAYESIAN]
            ) -> None: ...

        def set_training_parameters(
                self, 
                *, 
                advanced_settings: Optional[str] = ..., 
                ams_gradient: Optional[bool] = ..., 
                beta1: Optional[float] = ..., 
                beta2: Optional[float] = ..., 
                checkpoint_frequency: Optional[int] = ..., 
                checkpoint_run_id: Optional[str] = ..., 
                distributed: Optional[bool] = ..., 
                early_stopping: Optional[bool] = ..., 
                early_stopping_delay: Optional[int] = ..., 
                early_stopping_patience: Optional[int] = ..., 
                enable_onnx_normalization: Optional[bool] = ..., 
                evaluation_frequency: Optional[int] = ..., 
                gradient_accumulation_step: Optional[int] = ..., 
                layers_to_freeze: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[Union[str, LearningRateScheduler]] = ..., 
                model_name: Optional[str] = ..., 
                momentum: Optional[float] = ..., 
                nesterov: Optional[bool] = ..., 
                number_of_epochs: Optional[int] = ..., 
                number_of_workers: Optional[int] = ..., 
                optimizer: Optional[Union[str, StochasticOptimizer]] = ..., 
                random_seed: Optional[int] = ..., 
                step_lr_gamma: Optional[float] = ..., 
                step_lr_step_size: Optional[int] = ..., 
                training_batch_size: Optional[int] = ..., 
                training_crop_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                validation_crop_size: Optional[int] = ..., 
                validation_resize_size: Optional[int] = ..., 
                warmup_cosine_lr_cycles: Optional[float] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[int] = ..., 
                weight_decay: Optional[float] = ..., 
                weighted_loss: Optional[int] = ...
            ) -> None: ...


    class azure.ai.ml.automl.ImageClassificationMultilabelJob(AutoMLImageClassificationBase):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property limits: ImageLimitSettings
        property log_files: Optional[Dict[str, str]]    # Read-only
        property log_verbosity: LogVerbosity
        property outputs: Dict[str, Output]
        property primary_metric: Union[str, ClassificationMultilabelPrimaryMetrics]
        property search_space: Optional[List[ImageClassificationSearchSpace]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property sweep: Optional[ImageSweepSettings]
        property task_type: str
        property test_data: Input
        property training_data: Input
        property training_parameters: Optional[ImageModelSettingsClassification]
        property type: Optional[str]    # Read-only
        property validation_data: Input

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                primary_metric: Optional[Union[str, ClassificationMultilabelPrimaryMetrics]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def extend_search_space(self, value: Union[SearchSpace, List[SearchSpace]]) -> None: ...

        def set_data(
                self, 
                *, 
                target_column_name: str, 
                training_data: Input, 
                validation_data: Optional[Input] = ..., 
                validation_data_size: Optional[float] = ...
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                max_concurrent_trials: Optional[int] = ..., 
                max_trials: Optional[int] = ..., 
                timeout_minutes: Optional[int] = ...
            ) -> None: ...

        def set_sweep(
                self, 
                *, 
                early_termination: Optional[Union[BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy]] = ..., 
                sampling_algorithm: Union[str, SamplingAlgorithmType.RANDOM, SamplingAlgorithmType.GRID, SamplingAlgorithmType.BAYESIAN]
            ) -> None: ...

        def set_training_parameters(
                self, 
                *, 
                advanced_settings: Optional[str] = ..., 
                ams_gradient: Optional[bool] = ..., 
                beta1: Optional[float] = ..., 
                beta2: Optional[float] = ..., 
                checkpoint_frequency: Optional[int] = ..., 
                checkpoint_run_id: Optional[str] = ..., 
                distributed: Optional[bool] = ..., 
                early_stopping: Optional[bool] = ..., 
                early_stopping_delay: Optional[int] = ..., 
                early_stopping_patience: Optional[int] = ..., 
                enable_onnx_normalization: Optional[bool] = ..., 
                evaluation_frequency: Optional[int] = ..., 
                gradient_accumulation_step: Optional[int] = ..., 
                layers_to_freeze: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[Union[str, LearningRateScheduler]] = ..., 
                model_name: Optional[str] = ..., 
                momentum: Optional[float] = ..., 
                nesterov: Optional[bool] = ..., 
                number_of_epochs: Optional[int] = ..., 
                number_of_workers: Optional[int] = ..., 
                optimizer: Optional[Union[str, StochasticOptimizer]] = ..., 
                random_seed: Optional[int] = ..., 
                step_lr_gamma: Optional[float] = ..., 
                step_lr_step_size: Optional[int] = ..., 
                training_batch_size: Optional[int] = ..., 
                training_crop_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                validation_crop_size: Optional[int] = ..., 
                validation_resize_size: Optional[int] = ..., 
                warmup_cosine_lr_cycles: Optional[float] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[int] = ..., 
                weight_decay: Optional[float] = ..., 
                weighted_loss: Optional[int] = ...
            ) -> None: ...


    class azure.ai.ml.automl.ImageClassificationSearchSpace(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                ams_gradient: Optional[Union[bool, SweepDistribution]] = ..., 
                beta1: Optional[Union[float, SweepDistribution]] = ..., 
                beta2: Optional[Union[float, SweepDistribution]] = ..., 
                distributed: Optional[Union[bool, SweepDistribution]] = ..., 
                early_stopping: Optional[Union[bool, SweepDistribution]] = ..., 
                early_stopping_delay: Optional[Union[int, SweepDistribution]] = ..., 
                early_stopping_patience: Optional[Union[int, SweepDistribution]] = ..., 
                enable_onnx_normalization: Optional[Union[bool, SweepDistribution]] = ..., 
                evaluation_frequency: Optional[Union[int, SweepDistribution]] = ..., 
                gradient_accumulation_step: Optional[Union[int, SweepDistribution]] = ..., 
                layers_to_freeze: Optional[Union[int, SweepDistribution]] = ..., 
                learning_rate: Optional[Union[float, SweepDistribution]] = ..., 
                learning_rate_scheduler: Optional[Union[str, SweepDistribution]] = ..., 
                model_name: Optional[Union[str, SweepDistribution]] = ..., 
                momentum: Optional[Union[float, SweepDistribution]] = ..., 
                nesterov: Optional[Union[bool, SweepDistribution]] = ..., 
                number_of_epochs: Optional[Union[int, SweepDistribution]] = ..., 
                number_of_workers: Optional[Union[int, SweepDistribution]] = ..., 
                optimizer: Optional[Union[str, SweepDistribution]] = ..., 
                random_seed: Optional[Union[int, SweepDistribution]] = ..., 
                step_lr_gamma: Optional[Union[float, SweepDistribution]] = ..., 
                step_lr_step_size: Optional[Union[int, SweepDistribution]] = ..., 
                training_batch_size: Optional[Union[int, SweepDistribution]] = ..., 
                training_crop_size: Optional[Union[int, SweepDistribution]] = ..., 
                validation_batch_size: Optional[Union[int, SweepDistribution]] = ..., 
                validation_crop_size: Optional[Union[int, SweepDistribution]] = ..., 
                validation_resize_size: Optional[Union[int, SweepDistribution]] = ..., 
                warmup_cosine_lr_cycles: Optional[Union[float, SweepDistribution]] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[Union[int, SweepDistribution]] = ..., 
                weight_decay: Optional[Union[float, SweepDistribution]] = ..., 
                weighted_loss: Optional[Union[int, SweepDistribution]] = ...
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.ImageInstanceSegmentationJob(AutoMLImageObjectDetectionBase):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property limits: ImageLimitSettings
        property log_files: Optional[Dict[str, str]]    # Read-only
        property log_verbosity: LogVerbosity
        property outputs: Dict[str, Output]
        property primary_metric: Union[str, InstanceSegmentationPrimaryMetrics]
        property search_space: Optional[List[ImageObjectDetectionSearchSpace]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property sweep: Optional[ImageSweepSettings]
        property task_type: str
        property test_data: Input
        property training_data: Input
        property training_parameters: Optional[ImageModelSettingsObjectDetection]
        property type: Optional[str]    # Read-only
        property validation_data: Input

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                primary_metric: Optional[Union[str, InstanceSegmentationPrimaryMetrics]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def extend_search_space(self, value: Union[SearchSpace, List[SearchSpace]]) -> None: ...

        def set_data(
                self, 
                *, 
                target_column_name: str, 
                training_data: Input, 
                validation_data: Optional[Input] = ..., 
                validation_data_size: Optional[float] = ...
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                max_concurrent_trials: Optional[int] = ..., 
                max_trials: Optional[int] = ..., 
                timeout_minutes: Optional[int] = ...
            ) -> None: ...

        def set_sweep(
                self, 
                *, 
                early_termination: Optional[Union[BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy]] = ..., 
                sampling_algorithm: Union[str, SamplingAlgorithmType.RANDOM, SamplingAlgorithmType.GRID, SamplingAlgorithmType.BAYESIAN]
            ) -> None: ...

        def set_training_parameters(
                self, 
                *, 
                advanced_settings: Optional[str] = ..., 
                ams_gradient: Optional[bool] = ..., 
                beta1: Optional[float] = ..., 
                beta2: Optional[float] = ..., 
                box_detections_per_image: Optional[int] = ..., 
                box_score_threshold: Optional[float] = ..., 
                checkpoint_frequency: Optional[int] = ..., 
                checkpoint_run_id: Optional[str] = ..., 
                distributed: Optional[bool] = ..., 
                early_stopping: Optional[bool] = ..., 
                early_stopping_delay: Optional[int] = ..., 
                early_stopping_patience: Optional[int] = ..., 
                enable_onnx_normalization: Optional[bool] = ..., 
                evaluation_frequency: Optional[int] = ..., 
                gradient_accumulation_step: Optional[int] = ..., 
                image_size: Optional[int] = ..., 
                layers_to_freeze: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[Union[str, LearningRateScheduler]] = ..., 
                log_training_metrics: Optional[Union[str, LogTrainingMetrics]] = ..., 
                log_validation_loss: Optional[Union[str, LogValidationLoss]] = ..., 
                max_size: Optional[int] = ..., 
                min_size: Optional[int] = ..., 
                model_name: Optional[str] = ..., 
                model_size: Optional[Union[str, ModelSize]] = ..., 
                momentum: Optional[float] = ..., 
                multi_scale: Optional[bool] = ..., 
                nesterov: Optional[bool] = ..., 
                nms_iou_threshold: Optional[float] = ..., 
                number_of_epochs: Optional[int] = ..., 
                number_of_workers: Optional[int] = ..., 
                optimizer: Optional[Union[str, StochasticOptimizer]] = ..., 
                random_seed: Optional[int] = ..., 
                step_lr_gamma: Optional[float] = ..., 
                step_lr_step_size: Optional[int] = ..., 
                tile_grid_size: Optional[str] = ..., 
                tile_overlap_ratio: Optional[float] = ..., 
                tile_predictions_nms_threshold: Optional[float] = ..., 
                training_batch_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                validation_iou_threshold: Optional[float] = ..., 
                validation_metric_type: Optional[Union[str, ValidationMetricType]] = ..., 
                warmup_cosine_lr_cycles: Optional[float] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[int] = ..., 
                weight_decay: Optional[float] = ...
            ) -> None: ...


    class azure.ai.ml.automl.ImageLimitSettings(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                max_concurrent_trials: Optional[int] = ..., 
                max_trials: Optional[int] = ..., 
                timeout_minutes: Optional[int] = ...
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.ImageModelSettingsClassification(ImageModelDistributionSettings):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                advanced_settings: Optional[str] = ..., 
                ams_gradient: Optional[bool] = ..., 
                beta1: Optional[float] = ..., 
                beta2: Optional[float] = ..., 
                checkpoint_frequency: Optional[int] = ..., 
                checkpoint_run_id: Optional[str] = ..., 
                distributed: Optional[bool] = ..., 
                early_stopping: Optional[bool] = ..., 
                early_stopping_delay: Optional[int] = ..., 
                early_stopping_patience: Optional[int] = ..., 
                enable_onnx_normalization: Optional[bool] = ..., 
                evaluation_frequency: Optional[int] = ..., 
                gradient_accumulation_step: Optional[int] = ..., 
                layers_to_freeze: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[LearningRateScheduler] = ..., 
                model_name: Optional[str] = ..., 
                momentum: Optional[float] = ..., 
                nesterov: Optional[bool] = ..., 
                number_of_epochs: Optional[int] = ..., 
                number_of_workers: Optional[int] = ..., 
                optimizer: Optional[StochasticOptimizer] = ..., 
                random_seed: Optional[int] = ..., 
                step_lr_gamma: Optional[float] = ..., 
                step_lr_step_size: Optional[int] = ..., 
                training_batch_size: Optional[int] = ..., 
                training_crop_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                validation_crop_size: Optional[int] = ..., 
                validation_resize_size: Optional[int] = ..., 
                warmup_cosine_lr_cycles: Optional[float] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[int] = ..., 
                weight_decay: Optional[float] = ..., 
                weighted_loss: Optional[int] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.ImageModelSettingsObjectDetection(ImageModelDistributionSettings):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                advanced_settings: Optional[str] = ..., 
                ams_gradient: Optional[bool] = ..., 
                beta1: Optional[float] = ..., 
                beta2: Optional[float] = ..., 
                box_detections_per_image: Optional[int] = ..., 
                box_score_threshold: Optional[float] = ..., 
                checkpoint_frequency: Optional[int] = ..., 
                checkpoint_run_id: Optional[str] = ..., 
                distributed: Optional[bool] = ..., 
                early_stopping: Optional[bool] = ..., 
                early_stopping_delay: Optional[int] = ..., 
                early_stopping_patience: Optional[int] = ..., 
                enable_onnx_normalization: Optional[bool] = ..., 
                evaluation_frequency: Optional[int] = ..., 
                gradient_accumulation_step: Optional[int] = ..., 
                image_size: Optional[int] = ..., 
                layers_to_freeze: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[LearningRateScheduler] = ..., 
                log_training_metrics: Optional[LogTrainingMetrics] = ..., 
                log_validation_loss: Optional[LogValidationLoss] = ..., 
                max_size: Optional[int] = ..., 
                min_size: Optional[int] = ..., 
                model_name: Optional[str] = ..., 
                model_size: Optional[ModelSize] = ..., 
                momentum: Optional[float] = ..., 
                multi_scale: Optional[bool] = ..., 
                nesterov: Optional[bool] = ..., 
                nms_iou_threshold: Optional[float] = ..., 
                number_of_epochs: Optional[int] = ..., 
                number_of_workers: Optional[int] = ..., 
                optimizer: Optional[StochasticOptimizer] = ..., 
                random_seed: Optional[int] = ..., 
                step_lr_gamma: Optional[float] = ..., 
                step_lr_step_size: Optional[int] = ..., 
                tile_grid_size: Optional[str] = ..., 
                tile_overlap_ratio: Optional[float] = ..., 
                tile_predictions_nms_threshold: Optional[float] = ..., 
                training_batch_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                validation_iou_threshold: Optional[float] = ..., 
                validation_metric_type: Optional[ValidationMetricType] = ..., 
                warmup_cosine_lr_cycles: Optional[float] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[int] = ..., 
                weight_decay: Optional[float] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.ImageObjectDetectionJob(AutoMLImageObjectDetectionBase):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property limits: ImageLimitSettings
        property log_files: Optional[Dict[str, str]]    # Read-only
        property log_verbosity: LogVerbosity
        property outputs: Dict[str, Output]
        property primary_metric: Union[str, ObjectDetectionPrimaryMetrics]
        property search_space: Optional[List[ImageObjectDetectionSearchSpace]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property sweep: Optional[ImageSweepSettings]
        property task_type: str
        property test_data: Input
        property training_data: Input
        property training_parameters: Optional[ImageModelSettingsObjectDetection]
        property type: Optional[str]    # Read-only
        property validation_data: Input

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                primary_metric: Optional[Union[str, ObjectDetectionPrimaryMetrics]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def extend_search_space(self, value: Union[SearchSpace, List[SearchSpace]]) -> None: ...

        def set_data(
                self, 
                *, 
                target_column_name: str, 
                training_data: Input, 
                validation_data: Optional[Input] = ..., 
                validation_data_size: Optional[float] = ...
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                max_concurrent_trials: Optional[int] = ..., 
                max_trials: Optional[int] = ..., 
                timeout_minutes: Optional[int] = ...
            ) -> None: ...

        def set_sweep(
                self, 
                *, 
                early_termination: Optional[Union[BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy]] = ..., 
                sampling_algorithm: Union[str, SamplingAlgorithmType.RANDOM, SamplingAlgorithmType.GRID, SamplingAlgorithmType.BAYESIAN]
            ) -> None: ...

        def set_training_parameters(
                self, 
                *, 
                advanced_settings: Optional[str] = ..., 
                ams_gradient: Optional[bool] = ..., 
                beta1: Optional[float] = ..., 
                beta2: Optional[float] = ..., 
                box_detections_per_image: Optional[int] = ..., 
                box_score_threshold: Optional[float] = ..., 
                checkpoint_frequency: Optional[int] = ..., 
                checkpoint_run_id: Optional[str] = ..., 
                distributed: Optional[bool] = ..., 
                early_stopping: Optional[bool] = ..., 
                early_stopping_delay: Optional[int] = ..., 
                early_stopping_patience: Optional[int] = ..., 
                enable_onnx_normalization: Optional[bool] = ..., 
                evaluation_frequency: Optional[int] = ..., 
                gradient_accumulation_step: Optional[int] = ..., 
                image_size: Optional[int] = ..., 
                layers_to_freeze: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[Union[str, LearningRateScheduler]] = ..., 
                log_training_metrics: Optional[Union[str, LogTrainingMetrics]] = ..., 
                log_validation_loss: Optional[Union[str, LogValidationLoss]] = ..., 
                max_size: Optional[int] = ..., 
                min_size: Optional[int] = ..., 
                model_name: Optional[str] = ..., 
                model_size: Optional[Union[str, ModelSize]] = ..., 
                momentum: Optional[float] = ..., 
                multi_scale: Optional[bool] = ..., 
                nesterov: Optional[bool] = ..., 
                nms_iou_threshold: Optional[float] = ..., 
                number_of_epochs: Optional[int] = ..., 
                number_of_workers: Optional[int] = ..., 
                optimizer: Optional[Union[str, StochasticOptimizer]] = ..., 
                random_seed: Optional[int] = ..., 
                step_lr_gamma: Optional[float] = ..., 
                step_lr_step_size: Optional[int] = ..., 
                tile_grid_size: Optional[str] = ..., 
                tile_overlap_ratio: Optional[float] = ..., 
                tile_predictions_nms_threshold: Optional[float] = ..., 
                training_batch_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                validation_iou_threshold: Optional[float] = ..., 
                validation_metric_type: Optional[Union[str, ValidationMetricType]] = ..., 
                warmup_cosine_lr_cycles: Optional[float] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[int] = ..., 
                weight_decay: Optional[float] = ...
            ) -> None: ...


    class azure.ai.ml.automl.ImageObjectDetectionSearchSpace(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                ams_gradient: Optional[Union[bool, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                beta1: Optional[Union[float, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                beta2: Optional[Union[float, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                box_detections_per_image: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                box_score_threshold: Optional[Union[float, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                distributed: Optional[Union[bool, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                early_stopping: Optional[Union[bool, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                early_stopping_delay: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                early_stopping_patience: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                enable_onnx_normalization: Optional[Union[bool, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                evaluation_frequency: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                gradient_accumulation_step: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                image_size: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                layers_to_freeze: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                learning_rate: Optional[Union[float, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                learning_rate_scheduler: Optional[Union[str, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                max_size: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                min_size: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                model_name: Optional[Union[str, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                model_size: Optional[Union[str, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                momentum: Optional[Union[float, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                multi_scale: Optional[Union[bool, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                nesterov: Optional[Union[bool, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                nms_iou_threshold: Optional[Union[float, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                number_of_epochs: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                number_of_workers: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                optimizer: Optional[Union[str, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                random_seed: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                step_lr_gamma: Optional[Union[float, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                step_lr_step_size: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                tile_grid_size: Optional[Union[str, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                tile_overlap_ratio: Optional[Union[float, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                tile_predictions_nms_threshold: Optional[Union[float, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                training_batch_size: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                validation_batch_size: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                validation_iou_threshold: Optional[Union[float, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                validation_metric_type: Optional[Union[str, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                warmup_cosine_lr_cycles: Optional[Union[float, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[Union[int, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ..., 
                weight_decay: Optional[Union[float, Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]] = ...
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.ImageSweepSettings(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                early_termination: Optional[Union[EarlyTerminationPolicy, BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy]] = ..., 
                sampling_algorithm: Union[str, SamplingAlgorithmType.GRID, SamplingAlgorithmType.BAYESIAN, SamplingAlgorithmType.RANDOM]
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.InstanceSegmentationPrimaryMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MEAN_AVERAGE_PRECISION = "MeanAveragePrecision"


    class azure.ai.ml.automl.LearningRateScheduler(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        STEP = "Step"
        WARMUP_COSINE = "WarmupCosine"


    class azure.ai.ml.automl.LogTrainingMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.ai.ml.automl.LogValidationLoss(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.ai.ml.automl.NCrossValidationsMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        CUSTOM = "Custom"


    class azure.ai.ml.automl.NlpFeaturizationSettings(FeaturizationSettings):
        type: str = "nlp"

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                dataset_language: Optional[str] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.NlpFixedParameters(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                gradient_accumulation_steps: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[str] = ..., 
                model_name: Optional[str] = ..., 
                number_of_epochs: Optional[int] = ..., 
                training_batch_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                warmup_ratio: Optional[float] = ..., 
                weight_decay: Optional[float] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.NlpLimitSettings(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                max_concurrent_trials: Optional[int] = ..., 
                max_nodes: int = 1, 
                max_trials: int = 1, 
                timeout_minutes: Optional[int] = ..., 
                trial_timeout_minutes: Optional[int] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.NlpSearchSpace(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                gradient_accumulation_steps: Optional[Union[int, SweepDistribution]] = ..., 
                learning_rate: Optional[Union[float, SweepDistribution]] = ..., 
                learning_rate_scheduler: Optional[Union[str, SweepDistribution]] = ..., 
                model_name: Optional[Union[str, SweepDistribution]] = ..., 
                number_of_epochs: Optional[Union[int, SweepDistribution]] = ..., 
                training_batch_size: Optional[Union[int, SweepDistribution]] = ..., 
                validation_batch_size: Optional[Union[int, SweepDistribution]] = ..., 
                warmup_ratio: Optional[Union[float, SweepDistribution]] = ..., 
                weight_decay: Optional[Union[float, SweepDistribution]] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.NlpSweepSettings(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                early_termination: Optional[EarlyTerminationPolicy] = ..., 
                sampling_algorithm: Union[str, SamplingAlgorithmType]
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.ObjectDetectionPrimaryMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MEAN_AVERAGE_PRECISION = "MeanAveragePrecision"


    class azure.ai.ml.automl.RegressionJob(AutoMLTabular):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property featurization: Optional[TabularFeaturizationSettings]
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property limits: Optional[TabularLimitSettings]
        property log_files: Optional[Dict[str, str]]    # Read-only
        property log_verbosity: LogVerbosity
        property outputs: Dict[str, Output]
        property primary_metric: Union[str, RegressionPrimaryMetrics]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property task_type: str
        property test_data: Input
        property training: RegressionTrainingSettings
        property training_data: Input
        property type: Optional[str]    # Read-only
        property validation_data: Input

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                primary_metric: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def set_data(
                self, 
                *, 
                cv_split_column_names: Optional[List[str]] = ..., 
                n_cross_validations: Optional[Union[str, int]] = ..., 
                target_column_name: str, 
                test_data: Optional[Input] = ..., 
                test_data_size: Optional[float] = ..., 
                training_data: Input, 
                validation_data: Optional[Input] = ..., 
                validation_data_size: Optional[float] = ..., 
                weight_column_name: Optional[str] = ...
            ) -> None: ...

        def set_featurization(
                self, 
                *, 
                blocked_transformers: Optional[List[Union[BlockedTransformers, str]]] = ..., 
                column_name_and_types: Optional[Dict[str, str]] = ..., 
                dataset_language: Optional[str] = ..., 
                enable_dnn_featurization: Optional[bool] = ..., 
                mode: Optional[str] = ..., 
                transformer_params: Optional[Dict[str, List[ColumnTransformer]]] = ...
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                enable_early_termination: Optional[bool] = ..., 
                exit_score: Optional[float] = ..., 
                max_concurrent_trials: Optional[int] = ..., 
                max_cores_per_trial: Optional[int] = ..., 
                max_nodes: Optional[int] = ..., 
                max_trials: Optional[int] = ..., 
                timeout_minutes: Optional[int] = ..., 
                trial_timeout_minutes: Optional[int] = ...
            ) -> None: ...

        def set_training(
                self, 
                *, 
                allowed_training_algorithms: Optional[List[str]] = ..., 
                blocked_training_algorithms: Optional[List[str]] = ..., 
                enable_dnn_training: Optional[bool] = ..., 
                enable_model_explainability: Optional[bool] = ..., 
                enable_onnx_compatible_models: Optional[bool] = ..., 
                enable_stack_ensemble: Optional[bool] = ..., 
                enable_vote_ensemble: Optional[bool] = ..., 
                ensemble_model_download_timeout: Optional[int] = ..., 
                stack_ensemble_settings: Optional[StackEnsembleSettings] = ..., 
                training_mode: Optional[Union[str, TabularTrainingMode]] = ...
            ) -> None: ...


    class azure.ai.ml.automl.RegressionModels(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DECISION_TREE = "DecisionTree"
        ELASTIC_NET = "ElasticNet"
        EXTREME_RANDOM_TREES = "ExtremeRandomTrees"
        GRADIENT_BOOSTING = "GradientBoosting"
        KNN = "KNN"
        LASSO_LARS = "LassoLars"
        LIGHT_GBM = "LightGBM"
        RANDOM_FOREST = "RandomForest"
        SGD = "SGD"
        XG_BOOST_REGRESSOR = "XGBoostRegressor"


    class azure.ai.ml.automl.RegressionPrimaryMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NORMALIZED_MEAN_ABSOLUTE_ERROR = "NormalizedMeanAbsoluteError"
        NORMALIZED_ROOT_MEAN_SQUARED_ERROR = "NormalizedRootMeanSquaredError"
        R2_SCORE = "R2Score"
        SPEARMAN_CORRELATION = "SpearmanCorrelation"


    class azure.ai.ml.automl.SamplingAlgorithmType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BAYESIAN = "Bayesian"
        GRID = "Grid"
        RANDOM = "Random"


    class azure.ai.ml.automl.SearchSpace:

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.ai.ml.automl.ShortSeriesHandlingConfiguration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        DROP = "Drop"
        NONE = "None"
        PAD = "Pad"


    class azure.ai.ml.automl.StackEnsembleSettings(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                stack_meta_learner_k_wargs: Optional[Any] = ..., 
                stack_meta_learner_train_percentage: float = 0.2, 
                stack_meta_learner_type: Optional[StackMetaLearnerType] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.StochasticOptimizer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADAM = "Adam"
        ADAMW = "Adamw"
        NONE = "None"
        SGD = "Sgd"


    class azure.ai.ml.automl.TabularFeaturizationSettings(FeaturizationSettings):
        property blocked_transformers: Optional[List[Union[BlockedTransformers, str]]]
        property transformer_params: Optional[Dict[str, List[ColumnTransformer]]]

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                blocked_transformers: Optional[List[Union[BlockedTransformers, str]]] = ..., 
                column_name_and_types: Optional[Dict[str, str]] = ..., 
                dataset_language: Optional[str] = ..., 
                enable_dnn_featurization: Optional[bool] = ..., 
                mode: Optional[str] = ..., 
                transformer_params: Optional[Dict[str, List[ColumnTransformer]]] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.TabularLimitSettings(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                enable_early_termination: Optional[bool] = ..., 
                exit_score: Optional[float] = ..., 
                max_concurrent_trials: Optional[int] = ..., 
                max_cores_per_trial: Optional[int] = ..., 
                max_nodes: Optional[int] = ..., 
                max_trials: Optional[int] = ..., 
                timeout_minutes: Optional[int] = ..., 
                trial_timeout_minutes: Optional[int] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.TargetAggregationFunction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAX = "Max"
        MEAN = "Mean"
        MIN = "Min"
        NONE = "None"
        SUM = "Sum"


    class azure.ai.ml.automl.TargetLagsMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        CUSTOM = "Custom"


    class azure.ai.ml.automl.TargetRollingWindowSizeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        CUSTOM = "Custom"


    class azure.ai.ml.automl.TextClassificationJob(AutoMLNLPJob):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property featurization: Optional[NlpFeaturizationSettings]
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property limits: NlpLimitSettings
        property log_files: Optional[Dict[str, str]]    # Read-only
        property log_verbosity: LogVerbosity
        property outputs: Dict[str, Output]
        property primary_metric: Union[str, ClassificationPrimaryMetrics]
        property search_space: Optional[List[NlpSearchSpace]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property sweep: Optional[NlpSweepSettings]
        property task_type: str
        property test_data: Input
        property training_data: Input
        property training_parameters: Optional[NlpFixedParameters]
        property type: Optional[str]    # Read-only
        property validation_data: Input

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                log_verbosity: Optional[str] = ..., 
                primary_metric: Optional[ClassificationPrimaryMetrics] = ..., 
                target_column_name: Optional[str] = ..., 
                training_data: Optional[Input] = ..., 
                validation_data: Optional[Input] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def extend_search_space(self, value: Union[SearchSpace, List[SearchSpace]]) -> None: ...

        def set_data(
                self, 
                *, 
                target_column_name: str, 
                training_data: Input, 
                validation_data: Input
            ) -> None: ...

        def set_featurization(
                self, 
                *, 
                dataset_language: Optional[str] = ...
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                max_concurrent_trials: int = 1, 
                max_nodes: int = 1, 
                max_trials: int = 1, 
                timeout_minutes: Optional[int] = ..., 
                trial_timeout_minutes: Optional[int] = ...
            ) -> None: ...

        def set_sweep(
                self, 
                *, 
                early_termination: Optional[EarlyTerminationPolicy] = ..., 
                sampling_algorithm: Union[str, SamplingAlgorithmType]
            ) -> None: ...

        def set_training_parameters(
                self, 
                *, 
                gradient_accumulation_steps: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[Union[str, NlpLearningRateScheduler]] = ..., 
                model_name: Optional[str] = ..., 
                number_of_epochs: Optional[int] = ..., 
                training_batch_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                warmup_ratio: Optional[float] = ..., 
                weight_decay: Optional[float] = ...
            ) -> None: ...


    class azure.ai.ml.automl.TextClassificationMultilabelJob(AutoMLNLPJob):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property featurization: Optional[NlpFeaturizationSettings]
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property limits: NlpLimitSettings
        property log_files: Optional[Dict[str, str]]    # Read-only
        property log_verbosity: LogVerbosity
        property outputs: Dict[str, Output]
        property primary_metric: Union[str, ClassificationMultilabelPrimaryMetrics]
        property search_space: Optional[List[NlpSearchSpace]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property sweep: Optional[NlpSweepSettings]
        property task_type: str
        property test_data: Input
        property training_data: Input
        property training_parameters: Optional[NlpFixedParameters]
        property type: Optional[str]    # Read-only
        property validation_data: Input

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                log_verbosity: Optional[str] = ..., 
                primary_metric: Optional[str] = ..., 
                target_column_name: Optional[str] = ..., 
                training_data: Optional[Input] = ..., 
                validation_data: Optional[Input] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def extend_search_space(self, value: Union[SearchSpace, List[SearchSpace]]) -> None: ...

        def set_data(
                self, 
                *, 
                target_column_name: str, 
                training_data: Input, 
                validation_data: Input
            ) -> None: ...

        def set_featurization(
                self, 
                *, 
                dataset_language: Optional[str] = ...
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                max_concurrent_trials: int = 1, 
                max_nodes: int = 1, 
                max_trials: int = 1, 
                timeout_minutes: Optional[int] = ..., 
                trial_timeout_minutes: Optional[int] = ...
            ) -> None: ...

        def set_sweep(
                self, 
                *, 
                early_termination: Optional[EarlyTerminationPolicy] = ..., 
                sampling_algorithm: Union[str, SamplingAlgorithmType]
            ) -> None: ...

        def set_training_parameters(
                self, 
                *, 
                gradient_accumulation_steps: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[Union[str, NlpLearningRateScheduler]] = ..., 
                model_name: Optional[str] = ..., 
                number_of_epochs: Optional[int] = ..., 
                training_batch_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                warmup_ratio: Optional[float] = ..., 
                weight_decay: Optional[float] = ...
            ) -> None: ...


    class azure.ai.ml.automl.TextNerJob(AutoMLNLPJob):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property featurization: Optional[NlpFeaturizationSettings]
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property limits: NlpLimitSettings
        property log_files: Optional[Dict[str, str]]    # Read-only
        property log_verbosity: LogVerbosity
        property outputs: Dict[str, Output]
        property primary_metric: Union[str, ClassificationPrimaryMetrics]
        property search_space: Optional[List[NlpSearchSpace]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property sweep: Optional[NlpSweepSettings]
        property task_type: str
        property test_data: Input
        property training_data: Input
        property training_parameters: Optional[NlpFixedParameters]
        property type: Optional[str]    # Read-only
        property validation_data: Input

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                log_verbosity: Optional[str] = ..., 
                primary_metric: Optional[str] = ..., 
                training_data: Optional[Input] = ..., 
                validation_data: Optional[Input] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def extend_search_space(self, value: Union[SearchSpace, List[SearchSpace]]) -> None: ...

        def set_data(
                self, 
                *, 
                target_column_name: str, 
                training_data: Input, 
                validation_data: Input
            ) -> None: ...

        def set_featurization(
                self, 
                *, 
                dataset_language: Optional[str] = ...
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                max_concurrent_trials: int = 1, 
                max_nodes: int = 1, 
                max_trials: int = 1, 
                timeout_minutes: Optional[int] = ..., 
                trial_timeout_minutes: Optional[int] = ...
            ) -> None: ...

        def set_sweep(
                self, 
                *, 
                early_termination: Optional[EarlyTerminationPolicy] = ..., 
                sampling_algorithm: Union[str, SamplingAlgorithmType]
            ) -> None: ...

        def set_training_parameters(
                self, 
                *, 
                gradient_accumulation_steps: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[Union[str, NlpLearningRateScheduler]] = ..., 
                model_name: Optional[str] = ..., 
                number_of_epochs: Optional[int] = ..., 
                training_batch_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                warmup_ratio: Optional[float] = ..., 
                weight_decay: Optional[float] = ...
            ) -> None: ...


    class azure.ai.ml.automl.TrainingSettings(RestTranslatableMixin):
        property allowed_training_algorithms: Optional[List[str]]
        property blocked_training_algorithms: Optional[List[str]]
        property training_mode: Optional[TabularTrainingMode]

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_training_algorithms: Optional[List[str]] = ..., 
                blocked_training_algorithms: Optional[List[str]] = ..., 
                enable_dnn_training: Optional[bool] = ..., 
                enable_model_explainability: Optional[bool] = ..., 
                enable_onnx_compatible_models: Optional[bool] = ..., 
                enable_stack_ensemble: Optional[bool] = ..., 
                enable_vote_ensemble: Optional[bool] = ..., 
                ensemble_model_download_timeout: Optional[int] = ..., 
                stack_ensemble_settings: Optional[StackEnsembleSettings] = ..., 
                training_mode: Optional[Union[str, TabularTrainingMode]] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.automl.UseStl(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SEASON = "Season"
        SEASON_TREND = "SeasonTrend"


    class azure.ai.ml.automl.ValidationMetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COCO = "Coco"
        COCO_VOC = "CocoVoc"
        NONE = "None"
        VOC = "Voc"


namespace azure.ai.ml.constants

    class azure.ai.ml.constants.AcrAccountSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM = "premium"


    class azure.ai.ml.constants.AssetTypes:
        CUSTOM_MODEL = custom_model
        MLFLOW_MODEL = mlflow_model
        MLTABLE = mltable
        TRITON_MODEL = triton_model
        URI_FILE = uri_file
        URI_FOLDER = uri_folder


    class azure.ai.ml.constants.BatchDeploymentOutputAction:
        APPEND_ROW = append_row
        SUMMARY_ONLY = summary_only


    class azure.ai.ml.constants.DataGenerationTaskType:
        CONVERSATION = CONVERSATION
        MATH = MATH
        NLI = NLI
        NLU_QA = NLU_QA
        SUMMARIZATION = SUMMARIZATION


    class azure.ai.ml.constants.DataGenerationType:
        DATA_GENERATION = data_generation
        LABEL_GENERATION = label_generation


    class azure.ai.ml.constants.DistributionType:
        MPI = mpi
        PYTORCH = pytorch
        RAY = ray
        TENSORFLOW = tensorflow


    @experimental
    class azure.ai.ml.constants.IPProtectionLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "all"
        NONE = "none"


    class azure.ai.ml.constants.ImageClassificationModelNames(Enum):
        MOBILENETV2 = "mobilenetv2"
        RESNEST101 = "resnest101"
        RESNEST50 = "resnest50"
        RESNET101 = "resnet101"
        RESNET152 = "resnet152"
        RESNET18 = "resnet18"
        RESNET34 = "resnet34"
        RESNET50 = "resnet50"
        SERESNEXT = "seresnext"
        VITB16R224 = "vitb16r224"
        VITL16R224 = "vitl16r224"
        VITS16R224 = "vits16r224"


    class azure.ai.ml.constants.ImageInstanceSegmentationModelNames(Enum):
        MASKRCNN_RESNET101_FPN = "maskrcnn_resnet101_fpn"
        MASKRCNN_RESNET152_FPN = "maskrcnn_resnet152_fpn"
        MASKRCNN_RESNET18_FPN = "maskrcnn_resnet18_fpn"
        MASKRCNN_RESNET34_FPN = "maskrcnn_resnet34_fpn"
        MASKRCNN_RESNET50_FPN = "maskrcnn_resnet50_fpn"


    class azure.ai.ml.constants.ImageObjectDetectionModelNames(Enum):
        FASTERRCNN_RESNET101_FPN = "fasterrcnn_resnet101_fpn"
        FASTERRCNN_RESNET152_FPN = "fasterrcnn_resnet152_fpn"
        FASTERRCNN_RESNET18_FPN = "fasterrcnn_resnet18_fpn"
        FASTERRCNN_RESNET34_FPN = "fasterrcnn_resnet34_fpn"
        FASTERRCNN_RESNET50_FPN = "fasterrcnn_resnet50_fpn"
        RETINANET_RESNET50_FPN = "retinanet_resnet50_fpn"
        YOLOV5 = "yolov5"


    class azure.ai.ml.constants.ImportSourceType:
        AZURESQLDB = azuresqldb
        AZURESYNAPSEANALYTICS = azuresynapseanalytics
        S3 = s3
        SNOWFLAKE = snowflake


    class azure.ai.ml.constants.InputOutputModes:
        DIRECT = direct
        DOWNLOAD = download
        EVAL_DOWNLOAD = eval_download
        EVAL_MOUNT = eval_mount
        MOUNT = mount
        RO_MOUNT = ro_mount
        RW_MOUNT = rw_mount
        UPLOAD = upload


    class azure.ai.ml.constants.InputTypes:
        BOOLEAN = boolean
        INTEGER = integer
        NUMBER = number
        STRING = string


    class azure.ai.ml.constants.JobType:
        AUTOML = automl
        BASE = base
        COMMAND = command
        COMPONENT = component
        DATA_TRANSFER = data_transfer
        DISTILLATION = distillation
        FINE_TUNING = finetuning
        IMPORT = import
        PARALLEL = parallel
        PIPELINE = pipeline
        SPARK = spark
        SWEEP = sweep


    class azure.ai.ml.constants.ListViewType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_ONLY = "ActiveOnly"
        ALL = "All"
        ARCHIVED_ONLY = "ArchivedOnly"


    class azure.ai.ml.constants.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.ai.ml.constants.ModelType:
        CUSTOM = CustomModel
        MLFLOW = MLFlowModel
        TRITON = TritonModel


    @experimental
    class azure.ai.ml.constants.MonitorDatasetContext(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUND_TRUTH_DATA = "ground_truth"
        MODEL_INPUTS = "model_inputs"
        MODEL_OUTPUTS = "model_outputs"
        TEST = "test"
        TRAINING = "training"
        VALIDATION = "validation"


    @experimental
    class azure.ai.ml.constants.MonitorFeatureType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_FEATURE_TYPES = "all_feature_types"
        CATEGORICAL = "categorical"
        NOT_APPLICABLE = "not_applicable"
        NUMERICAL = "numerical"


    @experimental
    class azure.ai.ml.constants.MonitorMetricName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCURACY = "accuracy"
        DATA_TYPE_ERROR_RATE = "data_type_error_rate"
        F1_SCORE = "f1_score"
        JENSEN_SHANNON_DISTANCE = "jensen_shannon_distance"
        MAE = "MAE"
        MSE = "MSE"
        NORMALIZED_DISCOUNTED_CUMULATIVE_GAIN = "normalized_discounted_cumulative_gain"
        NORMALIZED_WASSERSTEIN_DISTANCE = "normalized_wasserstein_distance"
        NULL_VALUE_RATE = "null_value_rate"
        OUT_OF_BOUND_RATE = "out_of_bounds_rate"
        PEARSONS_CHI_SQUARED_TEST = "pearsons_chi_squared_test"
        POPULATION_STABILITY_INDEX = "population_stability_index"
        PRECISION = "precision"
        RECALL = "recall"
        RMSE = "RMSE"
        TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST = "two_sample_kolmogorov_smirnov_test"


    @experimental
    class azure.ai.ml.constants.MonitorModelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLASSIFICATION = "classification"
        REGRESSION = "regression"


    @experimental
    class azure.ai.ml.constants.MonitorSignalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "custom"
        DATA_DRIFT = "data_drift"
        DATA_QUALITY = "data_quality"
        FEATURE_ATTRIBUTION_DRIFT = "feature_attribution_drift"
        GENERATION_SAFETY_QUALITY = "generation_safety_quality"
        GENERATION_TOKEN_STATISTICS = "generation_token_statistics"
        MODEL_PERFORMANCE = "model_performance"
        PREDICTION_DRIFT = "prediction_drift"


    class azure.ai.ml.constants.MonitorTargetTasks(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLASSIFICATION = "Classification"
        QUESTION_ANSWERING = "QuestionAnswering"
        REGRESSION = "Regression"


    class azure.ai.ml.constants.NlpLearningRateScheduler(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSTANT = "Constant"
        CONSTANT_WITH_WARMUP = "ConstantWithWarmup"
        COSINE = "Cosine"
        COSINE_WITH_RESTARTS = "CosineWithRestarts"
        LINEAR = "Linear"
        NONE = "None"
        POLYNOMIAL = "Polynomial"


    class azure.ai.ml.constants.NlpModels(Enum):
        BERT_BASE_CASED = "bert-base-cased"
        BERT_BASE_GERMAN_CASED = "bert-base-german-cased"
        BERT_BASE_MULTILINGUAL_CASED = "bert-base-multilingual-cased"
        BERT_BASE_UNCASED = "bert-base-uncased"
        BERT_LARGE_CASED = "bert-large-cased"
        BERT_LARGE_UNCASED = "bert-large-uncased"
        DISTILBERT_BASE_CASED = "distilbert-base-cased"
        DISTILBERT_BASE_UNCASED = "distilbert-base-uncased"
        DISTILROBERTA_BASE = "distilroberta-base"
        ROBERTA_BASE = "roberta-base"
        ROBERTA_LARGE = "roberta-large"
        XLM_ROBERTA_BASE = "xlm-roberta-base"
        XLM_ROBERTA_LARGE = "xlm-roberta-large"
        XLNET_BASE_CASED = "xlnet-base-cased"
        XLNET_LARGE_CASED = "xlnet-large-cased"


    class azure.ai.ml.constants.ParallelTaskType:
        FUNCTION = function
        MODEL = model
        RUN_FUNCTION = run_function


    class azure.ai.ml.constants.Scope:
        RESOURCE_GROUP = resource_group
        SUBSCRIPTION = subscription


    class azure.ai.ml.constants.StorageAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "premium_lrs"
        PREMIUM_ZRS = "premium_zrs"
        STANDARD_GRS = "standard_grs"
        STANDARD_GZRS = "standard_gzrs"
        STANDARD_LRS = "standard_lrs"
        STANDARD_RAGRS = "standard_ragrs"
        STANDARD_RAGZRS = "standard_ragzrs"
        STANDARD_ZRS = "standard_zrs"


    class azure.ai.ml.constants.TabularTrainingMode(str, Enum):
        AUTO = "Auto"
        DISTRIBUTED = "Distributed"
        NON_DISTRIBUTED = "NonDistributed"


    class azure.ai.ml.constants.TimeZone(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFGHANISTANA_STANDARD_TIME = "Afghanistan Standard Time"
        ALASKAN_STANDARD_TIME = "Alaskan Standard Time"
        ALEUTIAN_STANDARD_TIME = "Aleutian Standard Time"
        ALTAI_STANDARD_TIME = "Altai Standard Time"
        ARABIAN_STANDARD_TIME = "Arabian Standard Time"
        ARABIC_STANDARD_TIME = "Arabic Standard Time"
        ARAB_STANDARD_TIME = "Arab Standard Time"
        ARGENTINA_STANDARD_TIME = "Argentina Standard Time"
        ASTRAKHAN_STANDARD_TIME = "Astrakhan Standard Time"
        ATLANTIC_STANDARD_TIME = "Atlantic Standard Time"
        AUS_CENTRAL_STANDARD_TIME = "AUS Central Standard Time"
        AUS_CENTRAL_W_STANDARD_TIME = "Aus Central W. Standard Time"
        AUS_EASTERN_STANDARD_TIME = "AUS Eastern Standard Time"
        AZERBAIJAN_STANDARD_TIME = "Azerbaijan Standard Time"
        AZORES_STANDARD_TIME = "Azores Standard Time"
        BAHIA_STANDARD_TIME = "Bahia Standard Time"
        BANGLADESH_STANDARD_TIME = "Bangladesh Standard Time"
        BELARUS_STANDARD_TIME = "Belarus Standard Time"
        BOUGAINVILLE_STANDARD_TIME = "Bougainville Standard Time"
        CANADA_CENTRAL_STANDARD_TIME = "Canada Central Standard Time"
        CAPE_VERDE_STANDARD_TIME = "Cape Verde Standard Time"
        CAUCASUS_STANDARD_TIME = "Caucasus Standard Time"
        CENTRAL_AMERICA_STANDARD_TIME = "Central America Standard Time"
        CENTRAL_ASIA_STANDARD_TIME = "Central Asia Standard Time"
        CENTRAL_BRAZILIAN_STANDARD_TIME = "Central Brazilian Standard Time"
        CENTRAL_EUROPEAN_STANDARD_TIME = "Central European Standard Time"
        CENTRAL_EUROPE_STANDARD_TIME = "Central Europe Standard Time"
        CENTRAL_PACIFIC_STANDARD_TIME = "Central Pacific Standard Time"
        CENTRAL_STANDARD_TIME = "Central Standard Time"
        CENTRAL_STANDARD_TIME_MEXICO = "Central Standard Time (Mexico)"
        CEN_AUSTRALIA_STANDARD_TIME = "Cen. Australia Standard Time"
        CHATHAM_ISLANDS_STANDARD_TIME = "Chatham Islands Standard Time"
        CHINA_STANDARD_TIME = "China Standard Time"
        CUBA_STANDARD_TIME = "Cuba Standard Time"
        DATELINE_STANDARD_TIME = "Dateline Standard Time"
        EASTERN_STANDARD_TIME = "Eastern Standard Time"
        EASTERN_STANDARD_TIME_MEXICO = "Eastern Standard Time (Mexico)"
        EASTER_ISLAND_STANDARD_TIME = "Easter Island Standard Time"
        EGYPT_STANDARD_TIME = "Egypt Standard Time"
        EKATERINBURG_STANDARD_TIME = "Ekaterinburg Standard Time"
        E_AFRICA_STANDARD_TIME = "E. Africa Standard Time"
        E_AUSTRALIAN_STANDARD_TIME = "E. Australia Standard Time"
        E_EUROPE_STANDARD_TIME = "E. Europe Standard Time"
        E_SOUTH_AMERICAN_STANDARD_TIME = "E. South America Standard Time"
        FIJI_STANDARD_TIME = "Fiji Standard Time"
        FLE_STANDARD_TIME = "FLE Standard Time"
        GEORGIAN_STANDARD_TIME = "Georgian Standard Time"
        GMT_STANDARD_TIME = "GMT Standard Time"
        GREENLAND_STANDARD_TIME = "Greenland Standard Time"
        GREENWICH_STANDARD_TIME = "Greenwich Standard Time"
        GTB_STANDARD_TIME = "GTB Standard Time"
        HAITI_STANDARD_TIME = "Haiti Standard Time"
        HAWAIIAN_STANDARD_TIME = "Hawaiian Standard Time"
        INDIA_STANDARD_TIME = "India Standard Time"
        IRAN_STANDARD_TIME = "Iran Standard Time"
        ISRAEL_STANDARD_TIME = "Israel Standard Time"
        JORDAN_STANDARD_TIME = "Jordan Standard Time"
        KALININGRAD_STANDARD_TIME = "Kaliningrad Standard Time"
        KAMCHATKA_STANDARD_TIME = "Kamchatka Standard Time"
        KOREA_STANDARD_TIME = "Korea Standard Time"
        LIBYA_STANDARD_TIME = "Libya Standard Time"
        LINE_ISLANDS_STANDARD_TIME = "Line Islands Standard Time"
        LORD_HOWE_STANDARD_TIME = "Lord Howe Standard Time"
        MAGADAN_STANDARD_TIME = "Magadan Standard Time"
        MARQUESAS_STANDARD_TIME = "Marquesas Standard Time"
        MAURITIUS_STANDARD_TIME = "Mauritius Standard Time"
        MIDDLE_EAST_STANDARD_TIME = "Middle East Standard Time"
        MID_ATLANTIC_STANDARD_TIME = "Mid-Atlantic Standard Time"
        MONTEVIDEO_STANDARD_TIME = "Montevideo Standard Time"
        MOROCCO_STANDARD_TIME = "Morocco Standard Time"
        MOUNTAIN_STANDARD_TIME = "Mountain Standard Time"
        MOUNTAIN_STANDARD_TIME_MEXICO = "Mountain Standard Time (Mexico)"
        MYANMAR_STANDARD_TIME = "Myanmar Standard Time"
        NAMIBIA_STANDARD_TIME = "Namibia Standard Time"
        NEPAL_STANDARD_TIME = "Nepal Standard Time"
        NEWFOUNDLAND_STANDARD_TIME = "Newfoundland Standard Time"
        NEW_ZEALAND_STANDARD_TIME = "New Zealand Standard Time"
        NORFOLK_STANDARD_TIME = "Norfolk Standard Time"
        NORTH_ASIA_EAST_STANDARD_TIME = "North Asia East Standard Time"
        NORTH_ASIA_STANDARD_TIME = "North Asia Standard Time"
        NORTH_KOREA_STANDARD_TIME = "North Korea Standard Time"
        N_CENTRAL_ASIA_STANDARD_TIME = "N. Central Asia Standard Time"
        PACIFIC_SA_STANDARD_TIME = "Pacific SA Standard Time"
        PACIFIC_STANDARD_TIME = "Pacific Standard Time"
        PACIFIC_STANDARD_TIME_MEXICO = "Pacific Standard Time (Mexico)"
        PAKISTAN_STANDARD_TIME = "Pakistan Standard Time"
        PARAGUAY_STANDARD_TIME = "Paraguay Standard Time"
        ROMANCE_STANDARD_TIME = "Romance Standard Time"
        RUSSIAN_STANDARD_TIME = "Russian Standard Time"
        RUSSIA_TIME_ZONE_10 = "Russia Time Zone 10"
        RUSSIA_TIME_ZONE_11 = "Russia Time Zone 11"
        RUSSIA_TIME_ZONE_3 = "Russia Time Zone 3"
        SAINT_PIERRE_STANDARD_TIME = "Saint Pierre Standard Time"
        SAKHALIN_STANDARD_TIME = "Sakhalin Standard Time"
        SAMOA_STANDARD_TIME = "Samoa Standard Time"
        SA_EASTERN_STANDARD_TIME = "SA Eastern Standard Time"
        SA_PACIFIC_STANDARD_TIME = "SA Pacific Standard Time"
        SA_WESTERN_STANDARD_TIME = "SA Western Standard Time"
        SE_ASIA_STANDARD_TIME = "SE Asia Standard Time"
        SINGAPORE_STANDARD_TIME = "Singapore Standard Time"
        SOUTH_AFRICA_STANDARD_TIME = "South Africa Standard Time"
        SRI_LANKA_STANDARD_TIME = "Sri Lanka Standard Time"
        SYRIA_STANDARD_TIME = "Syria Standard Time"
        TAIPEI_STANDARD_TIME = "Taipei Standard Time"
        TASMANIA_STANDARD_TIME = "Tasmania Standard Time"
        TOCANTINS_STANDARD_TIME = "Tocantins Standard Time"
        TOKYO_STANDARD_TIME = "Tokyo Standard Time"
        TOMSK_STANDARD_TIME = "Tomsk Standard Time"
        TONGA__STANDARD_TIME = "Tonga Standard Time"
        TRANSBAIKAL_STANDARD_TIME = "Transbaikal Standard Time"
        TURKEY_STANDARD_TIME = "Turkey Standard Time"
        TURKS_AND_CAICOS_STANDARD_TIME = "Turks And Caicos Standard Time"
        ULAANBAATAR_STANDARD_TIME = "Ulaanbaatar Standard Time"
        US_EASTERN_STANDARD_TIME = "US Eastern Standard Time"
        US_MOUNTAIN_STANDARD_TIME = "US Mountain Standard Time"
        UTC = "UTC"
        UTC_02 = "UTC-02"
        UTC_08 = "UTC-08"
        UTC_09 = "UTC-09"
        UTC_11 = "UTC-11"
        UTC_12 = "UTC+12"
        VENEZUELA_STANDARD_TIME = "Venezuela Standard Time"
        VLADIVOSTOK_STANDARD_TIME = "Vladivostok Standard Time"
        WEST_ASIA_STANDARD_TIME = "West Asia Standard Time"
        WEST_BANK_STANDARD_TIME = "West Bank Standard Time"
        WEST_PACIFIC_STANDARD_TIME = "West Pacific Standard Time"
        W_AUSTRALIA_STANDARD_TIME = "W. Australia Standard Time"
        W_CENTEAL_AFRICA_STANDARD_TIME = "W. Central Africa Standard Time"
        W_EUROPE_STANDARD_TIME = "W. Europe Standard Time"
        W_MONGOLIA_STANDARD_TIME = "W. Mongolia Standard Time"
        YAKUTSK_STANDARD_TIME = "Yakutsk Standard Time"


    class azure.ai.ml.constants.WorkspaceKind:
        DEFAULT = default
        FEATURE_STORE = featurestore
        HUB = hub
        PROJECT = project


namespace azure.ai.ml.data_transfer

    @experimental
    def azure.ai.ml.data_transfer.copy_data(
            *, 
            compute: Optional[str] = ..., 
            data_copy_mode: Optional[str] = ..., 
            description: Optional[str] = ..., 
            display_name: Optional[str] = ..., 
            experiment_name: Optional[str] = ..., 
            inputs: Optional[Dict] = ..., 
            is_deterministic: bool = True, 
            name: Optional[str] = ..., 
            outputs: Optional[Dict] = ..., 
            tags: Optional[Dict] = ..., 
            **kwargs: Any
        ) -> DataTransferCopy: ...


    @experimental
    @pipeline_node_decorator
    def azure.ai.ml.data_transfer.export_data(
            *, 
            compute: Optional[str] = ..., 
            description: Optional[str] = ..., 
            display_name: Optional[str] = ..., 
            experiment_name: Optional[str] = ..., 
            inputs: Optional[Dict] = ..., 
            name: Optional[str] = ..., 
            sink: Optional[Union[Dict, Database, FileSystem]] = ..., 
            tags: Optional[Dict] = ..., 
            **kwargs: Any
        ) -> DataTransferExport: ...


    @experimental
    @pipeline_node_decorator
    def azure.ai.ml.data_transfer.import_data(
            *, 
            compute: Optional[str] = ..., 
            description: Optional[str] = ..., 
            display_name: Optional[str] = ..., 
            experiment_name: Optional[str] = ..., 
            name: Optional[str] = ..., 
            outputs: Optional[Dict] = ..., 
            source: Optional[Union[Dict, Database, FileSystem]] = ..., 
            tags: Optional[Dict] = ..., 
            **kwargs: Any
        ) -> DataTransferImport: ...


    @experimental
    class azure.ai.ml.data_transfer.DataTransferCopy(DataTransfer):
        property base_path: str    # Read-only
        property component: Union[str, DataTransferComponent]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property log_files: Optional[Dict[str, str]]    # Read-only
        property name: Optional[str]
        property outputs: Dict    # Read-only
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __bool__(self) -> bool: ...

        def __call__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> DataTransferCopy: ...

        def __dir__(self) -> List: ...

        def __getattr__(self, key: Any) -> Any: ...

        def __getitem__(self, item: V) -> Any: ...

        def __hash__(self) -> int: ...

        def __help__(self) -> Any: ...

        def __init__(
                self, 
                *, 
                component: Union[str, DataTransferCopyComponent], 
                compute: Optional[str] = ..., 
                data_copy_mode: Optional[str] = ..., 
                inputs: Optional[Dict[str, Union[NodeOutput, Input, str]]] = ..., 
                outputs: Optional[Dict[str, Union[str, Output]]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __setitem__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.data_transfer.DataTransferCopyComponent(DataTransferComponent):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property data_copy_mode: Optional[str]    # Read-only
        property display_name: Optional[str]
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property is_deterministic: Optional[bool]    # Read-only
        property outputs: Dict    # Read-only
        property task: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only
        property version: Optional[str]

        def __call__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> BaseNode: ...

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_copy_mode: Optional[str] = ..., 
                inputs: Optional[Dict] = ..., 
                outputs: Optional[Dict] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.data_transfer.DataTransferExport(DataTransfer):
        property base_path: str    # Read-only
        property component: Union[str, DataTransferComponent]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property log_files: Optional[Dict[str, str]]    # Read-only
        property name: Optional[str]
        property outputs: Dict    # Read-only
        property sink: Optional[Union[Dict, Database, FileSystem]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __bool__(self) -> bool: ...

        def __dir__(self) -> List: ...

        def __getattr__(self, key: Any) -> Any: ...

        def __getitem__(self, item: V) -> Any: ...

        def __hash__(self) -> int: ...

        def __help__(self) -> Any: ...

        def __init__(
                self, 
                *, 
                component: Union[str, DataTransferCopyComponent, DataTransferImportComponent], 
                compute: Optional[str] = ..., 
                inputs: Optional[Dict[str, Union[NodeOutput, Input, str]]] = ..., 
                sink: Optional[Union[Dict, Database, FileSystem]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __setitem__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.data_transfer.DataTransferExportComponent(DataTransferComponent):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property display_name: Optional[str]
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property is_deterministic: Optional[bool]    # Read-only
        property outputs: Dict    # Read-only
        property task: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only
        property version: Optional[str]

        def __call__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> NoReturn: ...

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                inputs: Optional[Dict] = ..., 
                sink: Optional[Dict] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.data_transfer.DataTransferImport(DataTransfer):
        property base_path: str    # Read-only
        property component: Union[str, DataTransferComponent]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property log_files: Optional[Dict[str, str]]    # Read-only
        property name: Optional[str]
        property outputs: Dict    # Read-only
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __bool__(self) -> bool: ...

        def __dir__(self) -> List: ...

        def __getattr__(self, key: Any) -> Any: ...

        def __getitem__(self, item: V) -> Any: ...

        def __hash__(self) -> int: ...

        def __help__(self) -> Any: ...

        def __init__(
                self, 
                *, 
                component: Union[str, DataTransferImportComponent], 
                compute: Optional[str] = ..., 
                outputs: Optional[Dict[str, Union[str, Output]]] = ..., 
                source: Optional[Union[Dict, Database, FileSystem]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __setitem__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.data_transfer.DataTransferImportComponent(DataTransferComponent):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property display_name: Optional[str]
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property is_deterministic: Optional[bool]    # Read-only
        property outputs: Dict    # Read-only
        property task: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only
        property version: Optional[str]

        def __call__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> NoReturn: ...

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                outputs: Optional[Dict] = ..., 
                source: Optional[Dict] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.data_transfer.Database(DictMixin, RestTranslatableMixin): implements Collection , Mapping 
        property stored_procedure_params: Optional[List]

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                connection: Optional[str] = ..., 
                query: Optional[str] = ..., 
                stored_procedure: Optional[str] = ..., 
                stored_procedure_params: Optional[List[Dict]] = ..., 
                table_name: Optional[str] = ...
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.data_transfer.FileSystem(DictMixin, RestTranslatableMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                connection: Optional[str] = ..., 
                path: Optional[str] = ...
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


namespace azure.ai.ml.dsl

    @overload
    def azure.ai.ml.dsl.pipeline(
            func: None, 
            *, 
            description: Optional[str] = ..., 
            display_name: Optional[str] = ..., 
            experiment_name: Optional[str] = ..., 
            name: Optional[str] = ..., 
            tags: Optional[Dict[str, str]] = ..., 
            version: Optional[str] = ..., 
            **kwargs: Any
        ) -> Callable[[Callable[P, T]], Callable[P, PipelineJob]]: ...


    @overload
    def azure.ai.ml.dsl.pipeline(
            func: Callable[P, T], 
            *, 
            description: Optional[str] = ..., 
            display_name: Optional[str] = ..., 
            experiment_name: Optional[str] = ..., 
            name: Optional[str] = ..., 
            tags: Optional[Dict[str, str]] = ..., 
            version: Optional[str] = ..., 
            **kwargs: Any
        ) -> Callable[P, PipelineJob]: ...


namespace azure.ai.ml.entities

    @experimental
    class azure.ai.ml.entities.APIKeyConnection(ApiOrAadConnection):
        property api_base: Optional[str]    # Read-only
        property api_key: Optional[str]
        property azure_endpoint: Optional[str]    # Read-only
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration]    # Read-only
        property endpoint: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property is_shared: bool
        property metadata: Optional[Dict[str, Any]]
        property tags: Optional[Dict[str, Any]]
        property target: Optional[str]    # Read-only
        property type: Optional[str]
        property url: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                api_base: str, 
                api_key: Optional[str] = ..., 
                metadata: Optional[Dict[Any, Any]] = ..., 
                **kwargs
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.AadCredentialConfiguration(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(self) -> None: ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.entities.AccessKeyConfiguration(RestTranslatableMixin, DictMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                access_key_id: Optional[str], 
                secret_access_key: Optional[str]
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.AccountKeyConfiguration(RestTranslatableMixin, DictMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                account_key: Optional[str]
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.AlertNotification(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                emails: Optional[List[str]] = ...
            ) -> None: ...


    class azure.ai.ml.entities.AmlCompute(Compute):
        property base_path: str    # Read-only
        property created_on: Optional[str]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property provisioning_errors: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                enable_node_public_ip: bool = True, 
                identity: Optional[IdentityConfiguration] = ..., 
                idle_time_before_scale_down: Optional[int] = 120, 
                max_instances: Optional[int] = 4, 
                min_instances: Optional[int] = 0, 
                name: str, 
                network_settings: Optional[NetworkSettings] = ..., 
                size: Optional[str] = ..., 
                ssh_public_access_enabled: Optional[bool] = ..., 
                ssh_settings: Optional[AmlComputeSshSettings] = ..., 
                tags: Optional[dict] = ..., 
                tier: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.AmlComputeNodeInfo:
        property current_job_name: Optional[str]

        def __init__(self) -> None: ...


    class azure.ai.ml.entities.AmlComputeSshSettings:

        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                admin_username: str, 
                ssh_key_value: Optional[str] = ...
            ) -> None: ...


    class azure.ai.ml.entities.AmlTokenConfiguration(_BaseIdentityConfiguration): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(self) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.ApiKeyConfiguration(RestTranslatableMixin, DictMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                key: Optional[str]
            ): ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.Asset(Resource):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property version: Optional[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                name: Optional[str] = None, 
                version: Optional[str] = None, 
                description: Optional[str] = None, 
                tags: Optional[Dict] = None, 
                properties: Optional[Dict] = None, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.AssignedUserConfiguration(DictMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                user_object_id: str, 
                user_tenant_id: str
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.AutoPauseSettings:

        def __init__(
                self, 
                *, 
                delay_in_minutes: Optional[int] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...


    class azure.ai.ml.entities.AutoScaleSettings:

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                max_node_count: Optional[int] = ..., 
                min_node_count: Optional[int] = ...
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.AzureAISearchConfig:

        def __init__(
                self, 
                *, 
                connection_id: Optional[str] = ..., 
                index_name: Optional[str] = ...
            ) -> None: ...


    class azure.ai.ml.entities.AzureAISearchConnection(ApiOrAadConnection):
        property api_base: Optional[str]    # Read-only
        property api_key: Optional[str]
        property azure_endpoint: Optional[str]    # Read-only
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration]    # Read-only
        property endpoint: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property is_shared: bool
        property metadata: Optional[Dict[str, Any]]
        property tags: Optional[Dict[str, Any]]
        property target: Optional[str]    # Read-only
        property type: Optional[str]
        property url: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                endpoint: str, 
                metadata: Optional[Dict[Any, Any]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.AzureAIServicesConnection(ApiOrAadConnection):
        property ai_services_resource_id: Optional[str]
        property api_base: Optional[str]    # Read-only
        property api_key: Optional[str]
        property azure_endpoint: Optional[str]    # Read-only
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration]    # Read-only
        property endpoint: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property is_shared: bool
        property metadata: Optional[Dict[str, Any]]
        property tags: Optional[Dict[str, Any]]
        property target: Optional[str]    # Read-only
        property type: Optional[str]
        property url: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                ai_services_resource_id: str, 
                api_key: Optional[str] = ..., 
                endpoint: str, 
                metadata: Optional[Dict[Any, Any]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.AzureBlobDatastore(Datastore):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property type: str    # Read-only

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_name: str, 
                container_name: str, 
                credentials: Optional[Union[AccountKeyConfiguration, SasTokenConfiguration]] = ..., 
                description: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                name: str, 
                properties: Optional[Dict] = ..., 
                protocol: str = HTTPS, 
                tags: Optional[Dict] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.AzureBlobStoreConnection(WorkspaceConnection):
        property account_name: Optional[str]
        property api_base: Optional[str]    # Read-only
        property azure_endpoint: Optional[str]    # Read-only
        property base_path: str    # Read-only
        property container_name: Optional[str]
        property creation_context: Optional[SystemData]    # Read-only
        property credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration]    # Read-only
        property endpoint: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property is_shared: bool
        property metadata: Optional[Dict[str, Any]]
        property tags: Optional[Dict[str, Any]]
        property target: Optional[str]    # Read-only
        property type: Optional[str]
        property url: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                account_name: str, 
                container_name: str, 
                metadata: Optional[Dict[Any, Any]] = ..., 
                url: str, 
                **kwargs
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.AzureContentSafetyConnection(ApiOrAadConnection):
        property api_base: Optional[str]    # Read-only
        property api_key: Optional[str]
        property azure_endpoint: Optional[str]    # Read-only
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration]    # Read-only
        property endpoint: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property is_shared: bool
        property metadata: Optional[Dict[str, Any]]
        property tags: Optional[Dict[str, Any]]
        property target: Optional[str]    # Read-only
        property type: Optional[str]
        property url: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                endpoint: str, 
                metadata: Optional[Dict[Any, Any]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.AzureDataLakeGen1Datastore(Datastore):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property type: str    # Read-only

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                credentials: Optional[Union[CertificateConfiguration, ServicePrincipalConfiguration]] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                properties: Optional[Dict] = ..., 
                store_name: str, 
                tags: Optional[Dict] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.AzureDataLakeGen2Datastore(Datastore):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property type: str    # Read-only

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_name: str, 
                credentials: Optional[Union[ServicePrincipalConfiguration, CertificateConfiguration]] = ..., 
                description: Optional[str] = ..., 
                endpoint: str = _get_storage_endpoint_from_metadata(), 
                filesystem: str, 
                name: str, 
                properties: Optional[Dict] = ..., 
                protocol: str = HTTPS, 
                tags: Optional[Dict] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.AzureFileDatastore(Datastore):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property type: str    # Read-only

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_name: str, 
                credentials: Optional[Union[AccountKeyConfiguration, SasTokenConfiguration]] = ..., 
                description: Optional[str] = ..., 
                endpoint: str = _get_storage_endpoint_from_metadata(), 
                file_share_name: str, 
                name: str, 
                properties: Optional[Dict] = ..., 
                protocol: str = HTTPS, 
                tags: Optional[Dict] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.AzureMLBatchInferencingServer:
        type

        def __init__(
                self, 
                *, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                **kwargs: Any
            ): ...


    @experimental
    class azure.ai.ml.entities.AzureMLOnlineInferencingServer:
        type

        def __init__(
                self, 
                *, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                **kwargs: Any
            ): ...


    @experimental
    class azure.ai.ml.entities.AzureOpenAIConnection(ApiOrAadConnection):
        property api_base: Optional[str]    # Read-only
        property api_key: Optional[str]
        property api_version: Optional[str]
        property azure_endpoint: Optional[str]    # Read-only
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration]    # Read-only
        property endpoint: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property is_shared: bool
        property metadata: Optional[Dict[str, Any]]
        property open_ai_resource_id: Optional[str]
        property tags: Optional[Dict[str, Any]]
        property target: Optional[str]    # Read-only
        property type: Optional[str]
        property url: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                api_type: str = "Azure", 
                api_version: Optional[str] = ..., 
                azure_endpoint: str, 
                metadata: Optional[Dict[Any, Any]] = ..., 
                open_ai_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.AzureOpenAIDeployment(_AzureOpenAIDeployment):
        connection_name: str
        id: str
        model_name: str
        model_version: str
        name: str
        properties: dict[str, str]
        system_data: Optional[SystemData]
        tags: dict[str, str]
        target_url: str

        def as_dict(
                self, 
                *, 
                exclude_readonly: bool = False
            ) -> Dict[str, Any]: ...


    class azure.ai.ml.entities.AzureSpeechServicesConnection(ApiOrAadConnection):
        property api_base: Optional[str]    # Read-only
        property api_key: Optional[str]
        property azure_endpoint: Optional[str]    # Read-only
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration]    # Read-only
        property endpoint: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property is_shared: bool
        property metadata: Optional[Dict[str, Any]]
        property tags: Optional[Dict[str, Any]]
        property target: Optional[str]    # Read-only
        property type: Optional[str]
        property url: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                endpoint: str, 
                metadata: Optional[Dict[Any, Any]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.BaseEnvironment:

        def __init__(
                self, 
                type: str, 
                resource_id: Optional[str] = None
            ): ...


    class azure.ai.ml.entities.BaselineDataRange:

        def __init__(
                self, 
                *, 
                lookback_window_offset: Optional[str] = ..., 
                lookback_window_size: Optional[str] = ..., 
                window_end: Optional[str] = ..., 
                window_start: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.BatchDeployment(Deployment):
        property base_path: str    # Read-only
        property code_path: Optional[Union[str, PathLike]]
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property instance_count: Optional[int]
        property provisioning_state: Optional[str]    # Read-only
        property scoring_script: Optional[Union[str, PathLike]]
        property type: Optional[str]    # Read-only

        def __getattr__(self, name: str) -> Optional[Any]: ...

        def __init__(
                self, 
                *, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                code_path: Optional[Union[str, PathLike]] = ..., 
                compute: Optional[str] = ..., 
                description: Optional[str] = ..., 
                endpoint_name: Optional[str] = ..., 
                environment: Optional[Union[str, Environment]] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                error_threshold: Optional[int] = ..., 
                instance_count: Optional[int] = ..., 
                logging_level: Optional[str] = ..., 
                max_concurrency_per_instance: Optional[int] = ..., 
                mini_batch_size: Optional[int] = ..., 
                model: Optional[Union[str, Model]] = ..., 
                name: str, 
                output_action: Optional[Union[BatchDeploymentOutputAction, str]] = ..., 
                output_file_name: Optional[str] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                resources: Optional[ResourceConfiguration] = ..., 
                retry_settings: Optional[BatchRetrySettings] = ..., 
                scoring_script: Optional[Union[str, PathLike]] = ..., 
                tags: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                name, 
                value
            ): ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.BatchEndpoint(Endpoint):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property openapi_uri: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property scoring_uri: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                auth_mode: str = AAD_TOKEN_YAML, 
                default_deployment_name: Optional[str] = ..., 
                defaults: Optional[Dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                openapi_uri: Optional[str] = ..., 
                properties: Optional[Dict] = ..., 
                scoring_uri: Optional[str] = ..., 
                tags: Optional[Dict] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Optional[Union[str, PathLike, IO[AnyStr]]] = None, 
                **kwargs: Any
            ) -> Dict[str, Any]: ...


    class azure.ai.ml.entities.BatchJob:

        def __init__(self, **kwargs: Any): ...


    class azure.ai.ml.entities.BatchRetrySettings(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                max_retries: Optional[int] = ..., 
                timeout: Optional[int] = ...
            ): ...


    class azure.ai.ml.entities.BuildContext:

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dockerfile_path: Optional[str] = ..., 
                path: Optional[Union[str, PathLike]] = ...
            ): ...

        def __ne__(self, other: Any) -> bool: ...


    @experimental
    class azure.ai.ml.entities.CapabilityHost(Resource):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                ai_services_connections: Optional[List[str]] = ..., 
                capability_host_kind: Union[str, CapabilityHostKind] = CapabilityHostKind.AGENTS, 
                description: Optional[str] = ..., 
                name: str, 
                storage_connections: Optional[List[str]] = ..., 
                thread_storage_connections: Optional[List[str]] = ..., 
                vector_store_connections: Optional[List[str]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Optional[Union[str, PathLike, IO[AnyStr]]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.CapabilityHostKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENTS = "Agents"


    class azure.ai.ml.entities.CategoricalDriftMetrics(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                jensen_shannon_distance: Optional[float] = ..., 
                pearsons_chi_squared_test: Optional[float] = ..., 
                population_stability_index: Optional[float] = ...
            ): ...


    class azure.ai.ml.entities.CertificateConfiguration(BaseTenantCredentials): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                certificate: Optional[str] = None, 
                thumbprint: Optional[str] = None, 
                **kwargs: str
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.CodeConfiguration(DictMixin): implements Collection , Mapping 
        property scoring_script: Optional[Union[str, PathLike]]    # Read-only

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                code: Optional[Union[str, PathLike]] = None, 
                scoring_script: Optional[Union[str, PathLike]] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.Command(BaseNode, NodeWithGroupInputMixin):
        property base_path: str    # Read-only
        property code: Optional[Union[str, PathLike]]
        property command: Optional[str]
        property component: Union[str, CommandComponent]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property distribution: Optional[Union[Dict, MpiDistribution, TensorFlowDistribution, PyTorchDistribution, RayDistribution, DistributionConfiguration]]
        property id: Optional[str]    # Read-only
        property identity: Optional[Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]]
        property inputs: Dict    # Read-only
        property log_files: Optional[Dict[str, str]]    # Read-only
        property name: Optional[str]
        property outputs: Dict    # Read-only
        property parameters: Dict[str, str]    # Read-only
        property queue_settings: Optional[QueueSettings]
        property resources: JobResourceConfiguration
        property services: Optional[Dict[str, Union[JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService]]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __bool__(self) -> bool: ...

        def __call__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> Command: ...

        def __dir__(self) -> List: ...

        def __getattr__(self, key: Any) -> Any: ...

        def __getitem__(self, item: V) -> Any: ...

        def __hash__(self) -> int: ...

        def __help__(self) -> Any: ...

        def __init__(
                self, 
                *, 
                component: Union[str, CommandComponent], 
                compute: Optional[str] = ..., 
                distribution: Optional[Union[Dict, MpiDistribution, TensorFlowDistribution, PyTorchDistribution, RayDistribution, DistributionConfiguration]] = ..., 
                environment: Optional[Union[Environment, str]] = ..., 
                environment_variables: Optional[Dict] = ..., 
                identity: Optional[Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]] = ..., 
                inputs: Optional[Dict[str, Union[Input, str, bool, int, float, Enum]]] = ..., 
                limits: Optional[CommandJobLimits] = ..., 
                outputs: Optional[Dict[str, Union[str, Output]]] = ..., 
                parent_job_name: Optional[str] = ..., 
                queue_settings: Optional[QueueSettings] = ..., 
                resources: Optional[JobResourceConfiguration] = ..., 
                services: Optional[Dict[str, Union[JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __setitem__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                timeout: int, 
                **kwargs: Any
            ) -> None: ...

        def set_queue_settings(
                self, 
                *, 
                job_tier: Optional[str] = ..., 
                priority: Optional[str] = ...
            ) -> None: ...

        def set_resources(
                self, 
                *, 
                docker_args: Optional[Union[str, List[str]]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_type: Optional[Union[str, List[str]]] = ..., 
                locations: Optional[List[str]] = ..., 
                properties: Optional[Dict] = ..., 
                shm_size: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def sweep(
                self, 
                *, 
                compute: Optional[str] = ..., 
                early_termination_policy: Optional[Union[EarlyTerminationPolicy, str]] = ..., 
                goal: str, 
                identity: Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]] = ..., 
                job_tier: Optional[str] = ..., 
                max_concurrent_trials: Optional[int] = ..., 
                max_total_trials: Optional[int] = ..., 
                primary_metric: str, 
                priority: Optional[str] = ..., 
                queue_settings: Optional[QueueSettings] = ..., 
                sampling_algorithm: str = "random", 
                search_space: Optional[Dict[str, Union[Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]]] = ..., 
                timeout: Optional[int] = ..., 
                trial_timeout: Optional[int] = ...
            ) -> Sweep: ...


    class azure.ai.ml.entities.CommandComponent(Component, ParameterizedCommand, AdditionalIncludesMixin):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property display_name: Optional[str]
        property distribution: Optional[Union[dict, MpiDistribution, TensorFlowDistribution, PyTorchDistribution, RayDistribution, DistributionConfiguration]]
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property instance_count: Optional[int]
        property is_deterministic: Optional[bool]    # Read-only
        property outputs: Dict    # Read-only
        property resources: JobResourceConfiguration
        property type: Optional[str]    # Read-only
        property version: Optional[str]

        def __call__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> BaseNode: ...

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_includes: Optional[List] = ..., 
                code: Optional[Union[str, PathLike]] = ..., 
                command: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                distribution: Optional[Union[Dict, MpiDistribution, TensorFlowDistribution, PyTorchDistribution, RayDistribution, DistributionConfiguration]] = ..., 
                environment: Optional[Union[str, Environment]] = ..., 
                inputs: Optional[Dict] = ..., 
                instance_count: Optional[int] = ..., 
                is_deterministic: bool = True, 
                name: Optional[str] = ..., 
                outputs: Optional[Dict] = ..., 
                properties: Optional[Dict] = ..., 
                resources: Optional[JobResourceConfiguration] = ..., 
                tags: Optional[Dict] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.CommandJob(Job, ParameterizedCommand, JobIOMixin):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property distribution: Optional[Union[dict, MpiDistribution, TensorFlowDistribution, PyTorchDistribution, RayDistribution, DistributionConfiguration]]
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property log_files: Optional[Dict[str, str]]    # Read-only
        property outputs: Dict[str, Output]
        property parameters: Dict[str, str]    # Read-only
        property resources: JobResourceConfiguration
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                identity: Optional[Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]] = ..., 
                inputs: Optional[Dict[str, Union[Input, str, bool, int, float]]] = ..., 
                limits: Optional[CommandJobLimits] = ..., 
                outputs: Optional[Dict[str, Output]] = ..., 
                parent_job_name: Optional[str] = ..., 
                services: Optional[Dict[str, Union[JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.CommandJobLimits(JobLimits):

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                timeout: Optional[Union[int, str]] = ...
            ) -> None: ...


    class azure.ai.ml.entities.Component(Asset, RemoteValidatableMixin, TelemetryMixin, YamlTranslatableMixin, PathAwareSchemaValidatableMixin, LocalizableMixin):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property display_name: Optional[str]
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property is_deterministic: Optional[bool]    # Read-only
        property outputs: Dict    # Read-only
        property type: Optional[str]    # Read-only
        property version: Optional[str]

        def __call__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> BaseNode: ...

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                _schema: Optional[str] = ..., 
                creation_context: Optional[SystemData] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                inputs: Optional[Dict] = ..., 
                is_deterministic: bool = True, 
                name: Optional[str] = ..., 
                outputs: Optional[Dict] = ..., 
                properties: Optional[Dict] = ..., 
                tags: Optional[Dict] = ..., 
                type: Optional[str] = ..., 
                version: Optional[str] = ..., 
                yaml_str: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.Compute(Resource, RestTranslatableMixin):
        property base_path: str    # Read-only
        property created_on: Optional[str]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property provisioning_errors: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                name: str, 
                location: Optional[str] = None, 
                description: Optional[str] = None, 
                resource_id: Optional[str] = None, 
                tags: Optional[Dict] = None, 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ComputeConfiguration(RestTranslatableMixin, DictMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                deserialize_properties: bool = False, 
                instance_count: Optional[int] = ..., 
                instance_type: Optional[str] = ..., 
                is_local: Optional[bool] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[Dict[str, Any]] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ComputeInstance(Compute):
        property base_path: str    # Read-only
        property created_on: Optional[str]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property last_operation: Dict[str, str]    # Read-only
        property os_image_metadata: ImageMetadata    # Read-only
        property provisioning_errors: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property services: List[Dict[str, str]]    # Read-only
        property state: str    # Read-only
        property type: Optional[str]    # Read-only
        applications
        last_operation
        state

        def __init__(
                self, 
                *, 
                create_on_behalf_of: Optional[AssignedUserConfiguration] = ..., 
                custom_applications: Optional[List[CustomApplications]] = ..., 
                description: Optional[str] = ..., 
                enable_node_public_ip: bool = True, 
                enable_os_patching: bool = False, 
                enable_root_access: bool = True, 
                enable_sso: bool = True, 
                identity: Optional[IdentityConfiguration] = ..., 
                idle_time_before_shutdown: Optional[str] = ..., 
                idle_time_before_shutdown_minutes: Optional[int] = ..., 
                name: str, 
                network_settings: Optional[NetworkSettings] = ..., 
                release_quota_on_stop: bool = False, 
                schedules: Optional[ComputeSchedules] = ..., 
                setup_scripts: Optional[SetupScripts] = ..., 
                size: Optional[str] = ..., 
                ssh_public_access_enabled: Optional[bool] = ..., 
                ssh_settings: Optional[ComputeInstanceSshSettings] = ..., 
                tags: Optional[dict] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ComputeInstanceSshSettings:
        property admin_username: str    # Read-only
        property ssh_port: str    # Read-only

        def __init__(
                self, 
                *, 
                ssh_key_value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ComputePowerAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        START = "Start"
        STOP = "Stop"


    class azure.ai.ml.entities.ComputeRuntime(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                spark_runtime_version: Optional[str] = ...
            ) -> None: ...


    class azure.ai.ml.entities.ComputeSchedules(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                compute_start_stop: Optional[List[ComputeStartStopSchedule]] = ...
            ) -> None: ...


    class azure.ai.ml.entities.ComputeStartStopSchedule(RestTranslatableMixin):
        property provisioning_state: Optional[str]    # Read-only
        property schedule_id: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                action: Optional[ComputePowerAction] = ..., 
                state: ScheduleState = ScheduleState.ENABLED, 
                trigger: Optional[Union[CronTrigger, RecurrenceTrigger]] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ContainerRegistryCredential:

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                passwords: Optional[List[str]] = ..., 
                username: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.ai.ml.entities.CronTrigger(TriggerBase):

        def __init__(
                self, 
                *, 
                end_time: Optional[Union[str, datetime]] = ..., 
                expression: str, 
                start_time: Optional[Union[str, datetime]] = ..., 
                time_zone: Union[str, TimeZone] = TimeZone.UTC
            ) -> None: ...


    class azure.ai.ml.entities.CustomApplications:

        def __init__(
                self, 
                *, 
                bind_mounts: Optional[List[VolumeSettings]] = ..., 
                endpoints: List[EndpointsSettings], 
                environment_variables: Optional[Dict] = ..., 
                image: ImageSettings, 
                name: str, 
                type: str = CustomApplicationDefaults.DOCKER, 
                **kwargs: Any
            ): ...


    @experimental
    class azure.ai.ml.entities.CustomInferencingServer:
        type

        def __init__(
                self, 
                *, 
                inference_configuration: Optional[OnlineInferenceConfiguration] = ..., 
                **kwargs: Any
            ): ...


    @experimental
    class azure.ai.ml.entities.CustomModelFineTuningJob(FineTuningVertical):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property hyperparameters: Dict[str, str]
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property log_files: Optional[Dict[str, str]]    # Read-only
        property model: Optional[Input]
        property model_provider: Optional[str]
        property outputs: Dict[str, Output]
        property queue_settings: Optional[QueueSettings]
        property resources: Optional[JobResources]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property task: str
        property training_data: Input
        property type: Optional[str]    # Read-only
        property validation_data: Optional[Input]

        def __eq__(self, other: object) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.CustomMonitoringMetricThreshold(MetricThreshold):

        def __init__(
                self, 
                *, 
                metric_name: Optional[str], 
                threshold: Optional[float] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.CustomMonitoringSignal(RestTranslatableMixin):
        type: str

        def __init__(
                self, 
                *, 
                alert_enabled: bool = False, 
                component_id: str, 
                connection: Optional[Connection] = ..., 
                input_data: Optional[Dict[str, ReferenceData]] = ..., 
                inputs: Optional[Dict[str, Input]] = ..., 
                metric_thresholds: List[CustomMonitoringMetricThreshold], 
                properties: Optional[Dict[str, str]] = ...
            ): ...


    class azure.ai.ml.entities.CustomerManagedKey:

        def __init__(
                self, 
                key_vault: Optional[str] = None, 
                key_uri: Optional[str] = None, 
                cosmosdb_id: Optional[str] = None, 
                storage_id: Optional[str] = None, 
                search_id: Optional[str] = None
            ): ...


    class azure.ai.ml.entities.Data(Artifact):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property path: Optional[Union[Path, str, PathLike]]
        property version: Optional[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                path: Optional[str] = ..., 
                properties: Optional[Dict] = ..., 
                tags: Optional[Dict] = ..., 
                type: str = AssetTypes.URI_FOLDER, 
                version: Optional[str] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.DataAsset:

        def __init__(
                self, 
                *, 
                data_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                path: Optional[str] = ..., 
                version: Optional[int] = ...
            ): ...


    class azure.ai.ml.entities.DataAvailabilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        INCOMPLETE = "Incomplete"
        NONE = "None"
        PENDING = "Pending"


    @experimental
    class azure.ai.ml.entities.DataCollector:

        def __init__(
                self, 
                collections: Dict[str, DeploymentCollection], 
                *, 
                request_logging: Optional[RequestLogging] = ..., 
                rolling_rate: Optional[str] = ..., 
                sampling_rate: Optional[float] = ..., 
                **kwargs: Any
            ): ...


    class azure.ai.ml.entities.DataColumn(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                name: str, 
                type: Optional[Union[str, DataColumnType]] = ..., 
                **kwargs: Any
            ): ...


    class azure.ai.ml.entities.DataColumnType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BINARY = "binary"
        BOOLEAN = "boolean"
        DATETIME = "datetime"
        DOUBLE = "double"
        FLOAT = "float"
        INTEGER = "integer"
        LONG = "long"
        STRING = "string"


    class azure.ai.ml.entities.DataDriftMetricThreshold(MetricThreshold):

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                categorical: Optional[CategoricalDriftMetrics] = ..., 
                data_type: Optional[MonitorFeatureType] = ..., 
                metric: Optional[str] = ..., 
                numerical: Optional[NumericalDriftMetrics] = ..., 
                threshold: Optional[float] = ...
            ): ...


    class azure.ai.ml.entities.DataDriftSignal(DataSignal):
        type: str

        def __init__(
                self, 
                *, 
                alert_enabled: bool = False, 
                data_segment: Optional[DataSegment] = ..., 
                feature_type_override: Optional[Dict[str, Union[str, MonitorFeatureDataType]]] = ..., 
                features: Optional[Union[List[str], MonitorFeatureFilter, Literal[all_features]]] = ..., 
                metric_thresholds: Optional[Union[DataDriftMetricThreshold, List[MetricThreshold]]] = ..., 
                production_data: Optional[ProductionData] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                reference_data: Optional[ReferenceData] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.DataImport(Data):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property path: Optional[Union[Path, str, PathLike]]
        property version: Optional[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                path: str, 
                properties: Optional[Dict] = ..., 
                source: Union[Database, FileSystem], 
                tags: Optional[Dict] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.DataQualityMetricThreshold(MetricThreshold):

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                categorical: Optional[DataQualityMetricsCategorical] = ..., 
                data_type: Optional[MonitorFeatureType] = ..., 
                metric_name: Optional[str] = ..., 
                numerical: Optional[DataQualityMetricsNumerical] = ..., 
                threshold: Optional[float] = ...
            ): ...


    class azure.ai.ml.entities.DataQualityMetricsCategorical(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                data_type_error_rate: Optional[float] = ..., 
                null_value_rate: Optional[float] = ..., 
                out_of_bounds_rate: Optional[float] = ...
            ): ...


    class azure.ai.ml.entities.DataQualityMetricsNumerical(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                data_type_error_rate: Optional[float] = ..., 
                null_value_rate: Optional[float] = ..., 
                out_of_bounds_rate: Optional[float] = ...
            ): ...


    class azure.ai.ml.entities.DataQualitySignal(DataSignal):
        type: str

        def __init__(
                self, 
                *, 
                alert_enabled: bool = False, 
                feature_type_override: Optional[Dict[str, Union[str, MonitorFeatureDataType]]] = ..., 
                features: Optional[Union[List[str], MonitorFeatureFilter, Literal[all_features]]] = ..., 
                metric_thresholds: Optional[Union[MetricThreshold, List[MetricThreshold]]] = ..., 
                production_data: Optional[ProductionData] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                reference_data: Optional[ReferenceData] = ...
            ): ...


    class azure.ai.ml.entities.DataSegment(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                feature_name: Optional[str] = ..., 
                feature_values: Optional[List[str]] = ...
            ) -> None: ...


    class azure.ai.ml.entities.Datastore(Resource, RestTranslatableMixin, ABC):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property type: str    # Read-only

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                credentials: Optional[Union[ServicePrincipalConfiguration, CertificateConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, SasTokenConfiguration]], 
                name: Optional[str] = None, 
                description: Optional[str] = None, 
                tags: Optional[Dict] = None, 
                properties: Optional[Dict] = None, 
                **kwargs: Any
            ): ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.DefaultActionType:
        ALLOW = Allow
        DENY = Deny


    @experimental
    class azure.ai.ml.entities.DefaultDeploymentTemplate:

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                asset_id: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...


    class azure.ai.ml.entities.DefaultScaleSettings(OnlineScaleSettings):
        type: str

        def __eq__(self, other: object) -> bool: ...

        def __init__(self, **kwargs: Any): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.entities.Deployment(Resource, RestTranslatableMixin):
        property base_path: str    # Read-only
        property code_path: Optional[Union[str, PathLike]]
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property scoring_script: Optional[Union[str, PathLike]]
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                name: Optional[str] = None, 
                *, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                code_path: Optional[Union[str, PathLike]] = ..., 
                description: Optional[str] = ..., 
                endpoint_name: Optional[str] = ..., 
                environment: Optional[Union[str, Environment]] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                model: Optional[Union[str, Model]] = ..., 
                properties: Optional[Dict[str, Any]] = ..., 
                scoring_script: Optional[Union[str, PathLike]] = ..., 
                tags: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.DeploymentCollection:

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                data: Optional[Union[str, DataAsset]] = ..., 
                enabled: Optional[str] = ..., 
                **kwargs: Any
            ): ...


    @experimental
    class azure.ai.ml.entities.DeploymentTemplate(Resource, RestTranslatableMixin):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property liveness_probe_initial_delay: Optional[int]
        property liveness_probe_period: Optional[int]
        property liveness_probe_timeout: Optional[int]
        property readiness_probe_initial_delay: Optional[int]
        property readiness_probe_period: Optional[int]
        property readiness_probe_timeout: Optional[int]
        property request_timeout: Optional[int]

        def __init__(
                self, 
                name: str, 
                version: str, 
                *, 
                allowed_instance_types: Optional[List[str]] = ..., 
                app_insights_enabled: Optional[bool] = ..., 
                code_configuration: Optional[Dict[str, Any]] = ..., 
                default_instance_type: Optional[str] = ..., 
                deployment_template_type: Optional[str] = ..., 
                description: Optional[str] = ..., 
                environment: Optional[Union[Environment, str]] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_type: Optional[str] = ..., 
                liveness_probe: Optional[ProbeSettings] = ..., 
                model: Optional[str] = ..., 
                model_mount_path: Optional[str] = ..., 
                readiness_probe: Optional[ProbeSettings] = ..., 
                request_settings: Optional[OnlineRequestSettings] = ..., 
                scoring_path: Optional[str] = ..., 
                scoring_port: Optional[int] = ..., 
                stage: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]] = None, 
                **kwargs: Any
            ) -> Dict[str, Any]: ...


    class azure.ai.ml.entities.DiagnoseRequestProperties:

        def __init__(
                self, 
                *, 
                application_insights: Optional[Dict[str, Any]] = ..., 
                container_registry: Optional[Dict[str, Any]] = ..., 
                dns_resolution: Optional[Dict[str, Any]] = ..., 
                key_vault: Optional[Dict[str, Any]] = ..., 
                nsg: Optional[Dict[str, Any]] = ..., 
                others: Optional[Dict[str, Any]] = ..., 
                resource_lock: Optional[Dict[str, Any]] = ..., 
                storage_account: Optional[Dict[str, Any]] = ..., 
                udr: Optional[Dict[str, Any]] = ...
            ): ...


    class azure.ai.ml.entities.DiagnoseResponseResult:

        def __init__(
                self, 
                *, 
                value: Optional[DiagnoseResponseResultValue] = ...
            ): ...


    class azure.ai.ml.entities.DiagnoseResponseResultValue:

        def __init__(
                self, 
                *, 
                application_insights_results: Optional[List[DiagnoseResult]] = ..., 
                container_registry_results: Optional[List[DiagnoseResult]] = ..., 
                dns_resolution_results: Optional[List[DiagnoseResult]] = ..., 
                key_vault_results: Optional[List[DiagnoseResult]] = ..., 
                network_security_rule_results: Optional[List[DiagnoseResult]] = ..., 
                other_results: Optional[List[DiagnoseResult]] = ..., 
                resource_lock_results: Optional[List[DiagnoseResult]] = ..., 
                storage_account_results: Optional[List[DiagnoseResult]] = ..., 
                user_defined_route_results: Optional[List[DiagnoseResult]] = ...
            ): ...

        def __json__(self): ...

        def __str__(self) -> str: ...


    class azure.ai.ml.entities.DiagnoseResult:

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                level: Optional[str] = ..., 
                message: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.DiagnoseWorkspaceParameters:

        def __init__(
                self, 
                *, 
                value: Optional[DiagnoseRequestProperties] = ...
            ): ...


    class azure.ai.ml.entities.Endpoint(Resource):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property openapi_uri: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property scoring_uri: Optional[str]    # Read-only

        def __init__(
                self, 
                auth_mode: Optional[str] = None, 
                location: Optional[str] = None, 
                name: Optional[str] = None, 
                tags: Optional[Dict[str, str]] = None, 
                properties: Optional[Dict[str, Any]] = None, 
                description: Optional[str] = None, 
                *, 
                openapi_uri: Optional[str] = ..., 
                provisioning_state: Optional[str] = ..., 
                scoring_uri: Optional[str] = ..., 
                traffic: Optional[Dict[str, int]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        @abstractmethod
        def dump(
                self, 
                dest: Optional[Union[str, PathLike, IO[AnyStr]]] = None, 
                **kwargs: Any
            ) -> Dict: ...


    class azure.ai.ml.entities.EndpointAadToken:
        access_token: str
        expiry_time_utc: float

        def __init__(self, obj: AccessToken): ...


    class azure.ai.ml.entities.EndpointAuthKeys(RestTranslatableMixin):
        primary_key: str
        secondary_key: str

        def __init__(
                self, 
                *, 
                primary_key: str = ..., 
                secondary_key: str = ..., 
                **kwargs: Any
            ): ...


    class azure.ai.ml.entities.EndpointAuthToken(RestTranslatableMixin):
        access_token: str
        expiry_time_utc: float
        refresh_after_time_utc: float
        token_type: str

        def __init__(
                self, 
                *, 
                access_token: str = ..., 
                expiry_time_utc: float = ..., 
                refresh_after_time_utc: float = ..., 
                token_type: str = ..., 
                **kwargs: Any
            ): ...


    class azure.ai.ml.entities.EndpointConnection:

        def __init__(
                self, 
                subscription_id: str, 
                resource_group: str, 
                vnet_name: str, 
                subnet_name: str, 
                location: Optional[str] = None
            ): ...


    class azure.ai.ml.entities.EndpointsSettings:

        def __init__(
                self, 
                *, 
                published: int, 
                target: int
            ): ...


    class azure.ai.ml.entities.Environment(Asset, LocalizableMixin):
        property base_path: str    # Read-only
        property conda_file: Optional[Union[str, PathLike, Dict]]
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property version: Optional[str]

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                build: Optional[BuildContext] = ..., 
                conda_file: Optional[Union[str, PathLike, Dict]] = ..., 
                datastore: Optional[str] = ..., 
                description: Optional[str] = ..., 
                image: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[Dict] = ..., 
                tags: Optional[Dict] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def validate(self) -> None: ...


    @experimental
    class azure.ai.ml.entities.FADProductionData(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                data_column_names: Optional[Dict[str, str]] = ..., 
                data_context: Optional[MonitorDatasetContext] = ..., 
                data_window: Optional[BaselineDataRange] = ..., 
                input_data: Input, 
                pre_processing_component: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.Feature(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                data_type: DataColumnType, 
                description: Optional[str] = ..., 
                name: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ): ...


    @experimental
    class azure.ai.ml.entities.FeatureAttributionDriftMetricThreshold(MetricThreshold):

        def __init__(
                self, 
                *, 
                normalized_discounted_cumulative_gain: Optional[float] = ..., 
                threshold: Optional[float] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.FeatureAttributionDriftSignal(RestTranslatableMixin):
        type: str

        def __init__(
                self, 
                *, 
                alert_enabled: bool = False, 
                metric_thresholds: FeatureAttributionDriftMetricThreshold, 
                production_data: Optional[List[FADProductionData]] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                reference_data: ReferenceData
            ): ...


    class azure.ai.ml.entities.FeatureSet(Artifact):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property path: Optional[Union[str, PathLike]]
        property version: Optional[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                entities: List[str], 
                materialization_settings: Optional[MaterializationSettings] = ..., 
                name: str, 
                specification: Optional[FeatureSetSpecification], 
                stage: Optional[str] = "Development", 
                tags: Optional[Dict] = ..., 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.FeatureSetBackfillMetadata(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                job_ids: Optional[List[str]] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.FeatureSetBackfillRequest(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                data_status: Optional[List[str]] = ..., 
                description: Optional[str] = ..., 
                feature_window: Optional[FeatureWindow] = ..., 
                job_id: Optional[str] = ..., 
                name: str, 
                resource: Optional[MaterializationComputeResource] = ..., 
                spark_configuration: Optional[Dict[str, str]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                version: str, 
                **kwargs: Any
            ): ...


    class azure.ai.ml.entities.FeatureSetMaterializationMetadata(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                creation_context: Optional[SystemData], 
                display_name: Optional[str], 
                duration: Optional[timedelta], 
                feature_window_end_time: Optional[datetime], 
                feature_window_start_time: Optional[datetime], 
                name: Optional[str], 
                status: Optional[str], 
                tags: Optional[Dict[str, str]], 
                type: Optional[MaterializationType], 
                **kwargs: Any
            ): ...


    class azure.ai.ml.entities.FeatureSetSpecification(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                path: Optional[Union[PathLike, str]] = ..., 
                **kwargs: Any
            ): ...


    class azure.ai.ml.entities.FeatureStore(Workspace):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property discovery_url: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property mlflow_tracking_uri: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                application_insights: Optional[str] = ..., 
                compute_runtime: Optional[ComputeRuntime] = ..., 
                container_registry: Optional[str] = ..., 
                customer_managed_key: Optional[CustomerManagedKey] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                hbi_workspace: bool = False, 
                identity: Optional[IdentityConfiguration] = ..., 
                image_build_compute: Optional[str] = ..., 
                key_vault: Optional[str] = ..., 
                location: Optional[str] = ..., 
                managed_network: Optional[ManagedNetwork] = ..., 
                materialization_identity: Optional[ManagedIdentityConfiguration] = ..., 
                name: str, 
                offline_store: Optional[MaterializationStore] = ..., 
                online_store: Optional[MaterializationStore] = ..., 
                primary_user_assigned_identity: Optional[str] = ..., 
                public_network_access: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                storage_account: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.FeatureStoreEntity(Asset):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property version: Optional[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                index_columns: List[DataColumn], 
                name: str, 
                stage: Optional[str] = "Development", 
                tags: Optional[Dict[str, str]] = ..., 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.FeatureStoreSettings(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                compute_runtime: Optional[ComputeRuntime] = ..., 
                offline_store_connection_name: Optional[str] = ..., 
                online_store_connection_name: Optional[str] = ...
            ) -> None: ...


    class azure.ai.ml.entities.FeatureWindow(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                feature_window_end: datetime, 
                feature_window_start: datetime, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.FixedInputData(MonitorInputData):
        type

        def __init__(
                self, 
                *, 
                data_context: Optional[MonitorDatasetContext] = ..., 
                job_type: Optional[str] = ..., 
                target_columns: Optional[Dict] = ..., 
                uri: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.FqdnDestination(OutboundRule):
        type: str

        def __init__(
                self, 
                *, 
                destination: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.GenerationSafetyQualityMonitoringMetricThreshold(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                coherence: Optional[Dict[str, float]] = ..., 
                fluency: Optional[Dict[str, float]] = ..., 
                groundedness: Optional[Dict[str, float]] = ..., 
                relevance: Optional[Dict[str, float]] = ..., 
                similarity: Optional[Dict[str, float]] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.GenerationSafetyQualitySignal(RestTranslatableMixin):
        type: str

        def __init__(
                self, 
                *, 
                alert_enabled: bool = False, 
                connection_id: Optional[str] = ..., 
                metric_thresholds: GenerationSafetyQualityMonitoringMetricThreshold, 
                production_data: Optional[List[LlmData]] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                sampling_rate: Optional[float] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.GenerationTokenStatisticsMonitorMetricThreshold(RestTranslatableMixin):
        metric: Union[str, GenerationTokenStatisticsMetric]
        threshold: MonitoringThreshold

        def __init__(
                self, 
                *, 
                totaltoken: Optional[Dict[str, float]] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.GenerationTokenStatisticsSignal(RestTranslatableMixin):
        type: str

        def __init__(
                self, 
                *, 
                alert_enabled: bool = False, 
                metric_thresholds: Optional[GenerationTokenStatisticsMonitorMetricThreshold] = ..., 
                production_data: Optional[LlmData] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                sampling_rate: Optional[float] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.GitSource(IndexDataSource):

        def __init__(
                self, 
                *, 
                branch_name: str, 
                connection_id: str, 
                url: str
            ): ...


    class azure.ai.ml.entities.Hub(Workspace):
        property associated_workspaces: Optional[List[str]]    # Read-only
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property default_resource_group: Optional[str]
        property discovery_url: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property mlflow_tracking_uri: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                associated_workspaces: Optional[List[str]] = ..., 
                container_registry: Optional[str] = ..., 
                customer_managed_key: Optional[CustomerManagedKey] = ..., 
                default_resource_group: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enable_data_isolation: bool = False, 
                identity: Optional[IdentityConfiguration] = ..., 
                key_vault: Optional[str] = ..., 
                location: Optional[str] = ..., 
                managed_network: Optional[ManagedNetwork] = ..., 
                name: str, 
                network_acls: Optional[NetworkAcls] = ..., 
                primary_user_assigned_identity: Optional[str] = ..., 
                public_network_access: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                storage_account: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.IPRule(RestTranslatableMixin):

        def __init__(self, value: Optional[str]): ...

        def __repr__(self): ...


    class azure.ai.ml.entities.IdentityConfiguration(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                type: str, 
                user_assigned_identities: Optional[List[ManagedIdentityConfiguration]] = ..., 
                **kwargs: dict
            ) -> None: ...


    class azure.ai.ml.entities.ImageMetadata:
        property current_image_version: Optional[str]    # Read-only
        property is_latest_os_image_version: Optional[bool]    # Read-only
        property latest_image_version: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                current_image_version: Optional[str], 
                is_latest_os_image_version: Optional[bool], 
                latest_image_version: Optional[str]
            ) -> None: ...


    class azure.ai.ml.entities.ImageSettings:

        def __init__(
                self, 
                *, 
                reference: str
            ): ...


    @experimental
    class azure.ai.ml.entities.ImportDataSchedule(Schedule):
        property base_path: str    # Read-only
        property create_job: Any
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property is_enabled: bool    # Read-only
        property provisioning_state: str    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                import_data: DataImport, 
                name: str, 
                properties: Optional[Dict] = ..., 
                tags: Optional[Dict] = ..., 
                trigger: Optional[Union[CronTrigger, RecurrenceTrigger]], 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.Index(Artifact):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property path: Optional[Union[str, PathLike]]
        property version: Optional[str]
        description: Optional[str]
        id: str
        name: str
        path: Optional[Union[str, PathLike]]
        properties: Optional[dict[str, str]]
        stage: str
        tags: Optional[dict[str, str]]
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                datastore: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                path: Optional[Union[str, PathLike]] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                stage: str = "Development", 
                tags: Optional[Dict[str, str]] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.IndexDataSource:

        def __init__(
                self, 
                *, 
                input_type: Union[str, IndexInputType]
            ): ...


    @dataclass(eq = True, frozen = False, init = True, order = False, repr = True, unsafe_hash = False)
    @experimental
    class azure.ai.ml.entities.IndexModelConfiguration:
        api_base: Optional[str]
        api_key: Optional[str]
        api_version: Optional[str]
        connection_name: Optional[str]
        connection_type: Optional[str]
        deployment_name: Optional[str]
        model_kwargs: Dict[str, Any]
        model_name: Optional[str]

        def __eq__() -> None: ...

        def __init__(
                self, 
                *, 
                api_base: Optional[str], 
                api_key: Optional[str], 
                api_version: Optional[str], 
                connection_name: Optional[str], 
                connection_type: Optional[str], 
                deployment_name: Optional[str], 
                model_kwargs: Dict[str, Any], 
                model_name: Optional[str]
            ): ...

        def __repr__() -> None: ...

        @staticmethod
        def from_connection(
                connection: WorkspaceConnection, 
                model_name: Optional[str] = None, 
                deployment_name: Optional[str] = None, 
                **kwargs
            ) -> ModelConfiguration: ...


    class azure.ai.ml.entities.InputPort:

        def __init__(
                self, 
                *, 
                default: Optional[str] = ..., 
                optional: Optional[bool] = False, 
                type_string: str
            ): ...


    @experimental
    class azure.ai.ml.entities.IntellectualProperty(RestTranslatableMixin):

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                protection_level: IPProtectionLevel = IPProtectionLevel.ALL, 
                publisher: Optional[str] = ...
            ) -> None: ...


    class azure.ai.ml.entities.IsolationMode:
        ALLOW_INTERNET_OUTBOUND = AllowInternetOutbound
        ALLOW_ONLY_APPROVED_OUTBOUND = AllowOnlyApprovedOutbound
        DISABLED = Disabled


    class azure.ai.ml.entities.Job(Resource, ComponentTranslatableMixin, TelemetryMixin):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property log_files: Optional[Dict[str, str]]    # Read-only
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                name: Optional[str] = None, 
                display_name: Optional[str] = None, 
                description: Optional[str] = None, 
                tags: Optional[Dict] = None, 
                properties: Optional[Dict] = None, 
                experiment_name: Optional[str] = None, 
                compute: Optional[str] = None, 
                services: Optional[Dict[str, JobService]] = None, 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.JobResourceConfiguration(RestTranslatableMixin, DictMixin): implements Collection , Mapping 
        property properties: Optional[Union[Properties, Dict]]

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                docker_args: Optional[Union[str, List[str]]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_type: Optional[Union[str, List]] = ..., 
                locations: Optional[List[str]] = ..., 
                max_instance_count: Optional[int] = ..., 
                properties: Optional[Union[Properties, Dict]] = ..., 
                shm_size: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.JobResources(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_types: List[str]
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.entities.JobSchedule(RestTranslatableMixin, Schedule, TelemetryMixin):
        property base_path: str    # Read-only
        property create_job: Union[Job, str]
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property is_enabled: bool    # Read-only
        property provisioning_state: str    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                create_job: Union[Job, str], 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: str, 
                properties: Optional[Dict] = ..., 
                tags: Optional[Dict] = ..., 
                trigger: Optional[Union[CronTrigger, RecurrenceTrigger]], 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.JobService(JobServiceBase): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
                nodes: Optional[Literal[all]] = ..., 
                port: Optional[int] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                status: Optional[str] = ..., 
                type: Optional[Literal[jupyter_lab, ssh, tensor_board, vs_code]] = ..., 
                **kwargs: Dict
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.JupyterLabJobService(JobServiceBase): implements Collection , Mapping 
        type: str

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
                nodes: Optional[Literal[all]] = ..., 
                port: Optional[int] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                status: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.KubernetesCompute(Compute):
        property base_path: str    # Read-only
        property created_on: Optional[str]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property provisioning_errors: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                identity: Optional[IdentityConfiguration] = ..., 
                namespace: str = "default", 
                properties: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.KubernetesOnlineDeployment(OnlineDeployment):
        property base_path: str    # Read-only
        property code_path: Optional[Union[str, PathLike]]
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property scoring_script: Optional[Union[str, PathLike]]
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                app_insights_enabled: bool = False, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                code_path: Optional[Union[str, PathLike]] = ..., 
                description: Optional[str] = ..., 
                endpoint_name: Optional[str] = ..., 
                environment: Optional[Union[str, Environment]] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_type: Optional[str] = ..., 
                liveness_probe: Optional[ProbeSettings] = ..., 
                model: Optional[Union[str, Model]] = ..., 
                name: str, 
                properties: Optional[Dict[str, Any]] = ..., 
                readiness_probe: Optional[ProbeSettings] = ..., 
                request_settings: Optional[OnlineRequestSettings] = ..., 
                resources: Optional[ResourceRequirementsSettings] = ..., 
                scale_settings: Optional[Union[DefaultScaleSettings, TargetUtilizationScaleSettings]] = ..., 
                scoring_script: Optional[Union[str, PathLike]] = ..., 
                tags: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.KubernetesOnlineEndpoint(OnlineEndpoint):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property openapi_uri: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property scoring_uri: Optional[str]    # Read-only

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: str = KEY, 
                compute: Optional[str] = ..., 
                description: Optional[str] = ..., 
                identity: Optional[IdentityConfiguration] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                mirror_traffic: Optional[Dict[str, int]] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[Dict[str, Any]] = ..., 
                tags: Optional[Dict[str, Any]] = ..., 
                traffic: Optional[Dict[str, int]] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Optional[Union[str, PathLike, IO[AnyStr]]] = None, 
                **kwargs: Any
            ) -> Dict[str, Any]: ...


    @experimental
    class azure.ai.ml.entities.LlmData(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                data_column_names: Optional[Dict[str, str]] = ..., 
                data_window: Optional[BaselineDataRange] = ..., 
                input_data: Input
            ): ...


    @experimental
    class azure.ai.ml.entities.LocalSource(IndexDataSource):

        def __init__(
                self, 
                *, 
                input_data: str
            ): ...


    class azure.ai.ml.entities.ManagedIdentityConfiguration(_BaseIdentityConfiguration): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
                principal_id: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ManagedNetwork:

        def __init__(
                self, 
                *, 
                firewall_sku: Optional[str] = ..., 
                isolation_mode: str = IsolationMode.DISABLED, 
                network_id: Optional[str] = ..., 
                outbound_rules: Optional[List[OutboundRule]] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ManagedNetworkProvisionStatus:

        def __init__(
                self, 
                *, 
                spark_ready: Optional[bool] = ..., 
                status: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.ManagedOnlineDeployment(OnlineDeployment):
        property base_path: str    # Read-only
        property code_path: Optional[Union[str, PathLike]]
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property scoring_script: Optional[Union[str, PathLike]]
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                app_insights_enabled: bool = False, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                code_path: Optional[Union[str, PathLike]] = ..., 
                data_collector: Optional[DataCollector] = ..., 
                description: Optional[str] = ..., 
                egress_public_network_access: Optional[str] = ..., 
                endpoint_name: Optional[str] = ..., 
                environment: Optional[Union[str, Environment]] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_type: Optional[str] = ..., 
                liveness_probe: Optional[ProbeSettings] = ..., 
                model: Optional[Union[str, Model]] = ..., 
                name: str, 
                properties: Optional[Dict[str, Any]] = ..., 
                readiness_probe: Optional[ProbeSettings] = ..., 
                request_settings: Optional[OnlineRequestSettings] = ..., 
                scale_settings: Optional[Union[DefaultScaleSettings, TargetUtilizationScaleSettings]] = ..., 
                scoring_script: Optional[Union[str, PathLike]] = ..., 
                tags: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ManagedOnlineEndpoint(OnlineEndpoint):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property openapi_uri: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property scoring_uri: Optional[str]    # Read-only

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: str = KEY, 
                description: Optional[str] = ..., 
                identity: Optional[IdentityConfiguration] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                mirror_traffic: Optional[Dict[str, int]] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[Dict[str, Any]] = ..., 
                public_network_access: Optional[str] = ..., 
                tags: Optional[Dict[str, Any]] = ..., 
                traffic: Optional[Dict[str, int]] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Optional[Union[str, PathLike, IO[AnyStr]]] = None, 
                **kwargs: Any
            ) -> Dict[str, Any]: ...


    @experimental
    class azure.ai.ml.entities.MarketplacePlan(_MarketplacePlan):


    @experimental
    class azure.ai.ml.entities.MarketplaceSubscription(_MarketplaceSubscription, ValidationMixin):
        id: str
        marketplace_plan: MarketplacePlan
        model_id: str
        name: str
        provisioning_state: str
        status: str
        system_data: Optional[SystemData]

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def as_dict(
                self, 
                *, 
                exclude_readonly: bool = False
            ) -> Dict[str, Any]: ...


    class azure.ai.ml.entities.MaterializationComputeResource(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                instance_type: str, 
                **kwargs: Any
            ): ...


    class azure.ai.ml.entities.MaterializationSettings(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                notification: Optional[Notification] = ..., 
                offline_enabled: Optional[bool] = ..., 
                online_enabled: Optional[bool] = ..., 
                resource: Optional[MaterializationComputeResource] = ..., 
                schedule: Optional[RecurrenceTrigger] = ..., 
                spark_configuration: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.MaterializationStore:
        property target: str

        def __init__(
                self, 
                type: str, 
                target: str
            ) -> None: ...


    class azure.ai.ml.entities.MaterializationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKFILL_MATERIALIZATION = "2"
        RECURRENT_MATERIALIZATION = "1"


    class azure.ai.ml.entities.MicrosoftOneLakeConnection(WorkspaceConnection):
        property api_base: Optional[str]    # Read-only
        property azure_endpoint: Optional[str]    # Read-only
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration]    # Read-only
        property endpoint: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property is_shared: bool
        property metadata: Optional[Dict[str, Any]]
        property tags: Optional[Dict[str, Any]]
        property target: Optional[str]    # Read-only
        property type: Optional[str]
        property url: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                artifact: Optional[OneLakeConnectionArtifact] = ..., 
                endpoint: str, 
                metadata: Optional[Dict[Any, Any]] = ..., 
                one_lake_workspace_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.Model(Artifact):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property path: Optional[Union[str, PathLike]]
        property version: Optional[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_deployment_template: Optional[DefaultDeploymentTemplate] = ..., 
                description: Optional[str] = ..., 
                flavors: Optional[Dict[str, Dict[str, Any]]] = ..., 
                name: Optional[str] = ..., 
                path: Optional[Union[str, PathLike]] = ..., 
                properties: Optional[Dict] = ..., 
                stage: Optional[str] = ..., 
                tags: Optional[Dict] = ..., 
                type: Optional[str] = ..., 
                utc_time_created: Optional[str] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ModelBatchDeployment(BatchDeployment):
        property base_path: str    # Read-only
        property code_path: Optional[Union[str, PathLike]]
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property instance_count: Optional[int]
        property provisioning_state: Optional[str]    # Read-only
        property scoring_script: Optional[Union[str, PathLike]]
        property settings: ModelBatchDeploymentSettings
        property type: Optional[str]    # Read-only

        def __getattr__(self, name: str) -> Optional[Any]: ...

        def __init__(
                self, 
                *, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                code_path: Optional[Union[str, PathLike]] = ..., 
                compute: Optional[str] = ..., 
                description: Optional[str] = ..., 
                endpoint_name: Optional[str] = ..., 
                environment: Optional[Union[str, Environment]] = ..., 
                model: Optional[Union[str, Model]] = ..., 
                name: str, 
                properties: Optional[Dict[str, str]] = ..., 
                resources: Optional[ResourceConfiguration] = ..., 
                scoring_script: Optional[Union[str, PathLike]] = ..., 
                settings: Optional[ModelBatchDeploymentSettings] = ..., 
                tags: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                name, 
                value
            ): ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ModelBatchDeploymentSettings:

        def __init__(
                self, 
                *, 
                environment_variables: Optional[Dict[str, str]] = ..., 
                error_threshold: Optional[int] = ..., 
                instance_count: Optional[int] = ..., 
                logging_level: Optional[str] = ..., 
                max_concurrency_per_instance: Optional[int] = ..., 
                mini_batch_size: Optional[int], 
                output_action: Optional[Union[BatchDeploymentOutputAction, str]] = ..., 
                output_file_name: Optional[str] = ..., 
                retry_settings: Optional[BatchRetrySettings] = ..., 
                **kwargs: Any
            ): ...


    @experimental
    class azure.ai.ml.entities.ModelConfiguration:

        def __init__(
                self, 
                *, 
                mode: Optional[str] = ..., 
                mount_path: Optional[str] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.ModelPackage(Resource, PackageRequest):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                base_environment_source: Optional[BaseEnvironment] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                inferencing_server: Union[AzureMLOnlineInferencingServer, AzureMLBatchInferencingServer], 
                inputs: Optional[List[ModelPackageInput]] = ..., 
                model_configuration: Optional[ModelConfiguration] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_environment: Union[str, Dict[str, str]], 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.ModelPackageInput:

        def __init__(
                self, 
                *, 
                mode: Optional[str] = ..., 
                mount_path: Optional[str] = ..., 
                path: Optional[Union[PackageInputPathId, PackageInputPathUrl, PackageInputPathVersion]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.ModelPerformanceClassificationThresholds(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                accuracy: Optional[float] = ..., 
                precision: Optional[float] = ..., 
                recall: Optional[float] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.ModelPerformanceMetricThreshold(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                classification: Optional[ModelPerformanceClassificationThresholds] = ..., 
                regression: Optional[ModelPerformanceRegressionThresholds] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.ModelPerformanceRegressionThresholds(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                mean_absolute_error: Optional[float] = ..., 
                mean_squared_error: Optional[float] = ..., 
                root_mean_squared_error: Optional[float] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.ModelPerformanceSignal(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                alert_enabled: bool = False, 
                baseline_dataset: MonitorInputData = ..., 
                data_segment: Optional[DataSegment] = ..., 
                metric_thresholds: ModelPerformanceMetricThreshold, 
                model_type: MonitorModelType = ..., 
                production_data: ProductionData, 
                properties: Optional[Dict[str, str]] = ..., 
                reference_data: ReferenceData
            ) -> None: ...


    class azure.ai.ml.entities.MonitorDefinition(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                alert_notification: Optional[Union[Literal[azmonitoring], AlertNotification]] = ..., 
                compute: ServerlessSparkCompute, 
                monitoring_signals: Dict[str, Union[DataDriftSignal, DataQualitySignal, PredictionDriftSignal, FeatureAttributionDriftSignal, CustomMonitoringSignal, GenerationSafetyQualitySignal, GenerationTokenStatisticsSignal]] = ..., 
                monitoring_target: Optional[MonitoringTarget] = ...
            ) -> None: ...


    class azure.ai.ml.entities.MonitorFeatureFilter(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                top_n_feature_importance: int = 10
            ) -> None: ...


    class azure.ai.ml.entities.MonitorInputData(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                data_context: Optional[MonitorDatasetContext] = ..., 
                dataset_context: Optional[Union[str, MonitorDatasetContext]] = ..., 
                input_dataset: Optional[Input] = ..., 
                job_type: Optional[str] = ..., 
                pre_processing_component: Optional[str] = ..., 
                target_column_name: Optional[str] = ..., 
                target_columns: Optional[Dict] = ..., 
                type: Optional[MonitorInputDataType] = ..., 
                uri: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.MonitorSchedule(Schedule, RestTranslatableMixin):
        property base_path: str    # Read-only
        property create_job: Any
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property is_enabled: bool    # Read-only
        property provisioning_state: str    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                create_monitor: MonitorDefinition, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: str, 
                properties: Optional[Dict] = ..., 
                tags: Optional[Dict] = ..., 
                trigger: Optional[Union[CronTrigger, RecurrenceTrigger]], 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.MonitoringTarget:

        def __init__(
                self, 
                *, 
                endpoint_deployment_id: Optional[str] = ..., 
                ml_task: Optional[Union[str, MonitorTargetTasks]] = ..., 
                model_id: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.NetworkAcls(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                default_action: str = DefaultActionType.ALLOW, 
                ip_rules: Optional[List[IPRule]] = ...
            ): ...

        def __repr__(self): ...


    class azure.ai.ml.entities.NetworkSettings:
        property private_ip_address: str    # Read-only
        property public_ip_address: str    # Read-only

        def __init__(
                self, 
                *, 
                subnet: Optional[str] = ..., 
                vnet_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.NoneCredentialConfiguration(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(self) -> None: ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.entities.NotebookAccessKeys:

        def __init__(
                self, 
                *, 
                primary_access_key: Optional[str] = ..., 
                secondary_access_key: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.Notification(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                email_on: Optional[List[str]] = ..., 
                emails: Optional[List[str]] = ...
            ) -> None: ...


    class azure.ai.ml.entities.NumericalDriftMetrics(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                jensen_shannon_distance: Optional[float] = ..., 
                metric: Optional[str] = ..., 
                metric_threshold: Optional[float] = ..., 
                normalized_wasserstein_distance: Optional[float] = ..., 
                population_stability_index: Optional[float] = ..., 
                two_sample_kolmogorov_smirnov_test: Optional[float] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.OneLakeArtifact(RestTranslatableMixin, DictMixin, ABC): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                name: str, 
                type: Optional[str] = ...
            ): ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.OneLakeConnectionArtifact:

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ): ...


    @experimental
    class azure.ai.ml.entities.OneLakeDatastore(Datastore):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property type: str    # Read-only

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact: OneLakeArtifact, 
                credentials: Optional[Union[NoneCredentialConfiguration, ServicePrincipalConfiguration]] = ..., 
                description: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                name: str, 
                one_lake_workspace_name: str, 
                properties: Optional[Dict] = ..., 
                tags: Optional[Dict] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.OnlineDeployment(Deployment):
        property base_path: str    # Read-only
        property code_path: Optional[Union[str, PathLike]]
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property scoring_script: Optional[Union[str, PathLike]]
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                name: str, 
                *, 
                app_insights_enabled: Optional[bool] = False, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                code_path: Optional[Union[str, PathLike]] = ..., 
                data_collector: Optional[DataCollector] = ..., 
                description: Optional[str] = ..., 
                endpoint_name: Optional[str] = ..., 
                environment: Optional[Union[str, Environment]] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_type: Optional[str] = ..., 
                liveness_probe: Optional[ProbeSettings] = ..., 
                model: Optional[Union[str, Model]] = ..., 
                model_mount_path: Optional[str] = ..., 
                properties: Optional[Dict[str, Any]] = ..., 
                readiness_probe: Optional[ProbeSettings] = ..., 
                request_settings: Optional[OnlineRequestSettings] = ..., 
                scale_settings: Optional[OnlineScaleSettings] = ..., 
                scoring_script: Optional[Union[str, PathLike]] = ..., 
                tags: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.OnlineEndpoint(Endpoint):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property openapi_uri: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property scoring_uri: Optional[str]    # Read-only

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: str = KEY, 
                description: Optional[str] = ..., 
                identity: Optional[IdentityConfiguration] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                mirror_traffic: Optional[Dict[str, int]] = ..., 
                name: Optional[str] = ..., 
                openapi_uri: Optional[str] = ..., 
                properties: Optional[Dict[str, Any]] = ..., 
                provisioning_state: Optional[str] = ..., 
                scoring_uri: Optional[str] = ..., 
                tags: Optional[Dict[str, Any]] = ..., 
                traffic: Optional[Dict[str, int]] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: object) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        @abstractmethod
        def dump(
                self, 
                dest: Optional[Union[str, PathLike, IO[AnyStr]]] = None, 
                **kwargs: Any
            ) -> Dict: ...


    class azure.ai.ml.entities.OnlineRequestSettings(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                max_concurrent_requests_per_instance: Optional[int] = None, 
                request_timeout_ms: Optional[int] = None, 
                max_queue_wait_ms: Optional[int] = None
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.entities.OnlineScaleSettings(RestTranslatableMixin):

        def __init__(
                self, 
                type: str, 
                **kwargs: Any
            ): ...


    @experimental
    class azure.ai.ml.entities.OpenAIConnection(ApiOrAadConnection):
        property api_base: Optional[str]    # Read-only
        property api_key: Optional[str]
        property azure_endpoint: Optional[str]    # Read-only
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration]    # Read-only
        property endpoint: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property is_shared: bool
        property metadata: Optional[Dict[str, Any]]
        property tags: Optional[Dict[str, Any]]
        property target: Optional[str]    # Read-only
        property type: Optional[str]
        property url: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                metadata: Optional[Dict[Any, Any]] = ..., 
                **kwargs
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.OutboundRule(ABC):
        type: str

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.PackageInputPathId:

        def __init__(
                self, 
                *, 
                input_path_type: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.PackageInputPathUrl:

        def __init__(
                self, 
                *, 
                input_path_type: Optional[str] = ..., 
                url: Optional[str] = ...
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.PackageInputPathVersion:

        def __init__(
                self, 
                *, 
                input_path_type: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                resource_version: Optional[str] = ...
            ) -> None: ...


    class azure.ai.ml.entities.Parallel(BaseNode, NodeWithGroupInputMixin):
        property base_path: str    # Read-only
        property component: Union[str, ParallelComponent]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property identity: Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration, Dict]]
        property inputs: Dict    # Read-only
        property log_files: Optional[Dict[str, str]]    # Read-only
        property name: Optional[str]
        property outputs: Dict    # Read-only
        property resources: Optional[JobResourceConfiguration]
        property retry_settings: RetrySettings
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property task: Optional[ParallelTask]
        property type: Optional[str]    # Read-only

        def __bool__(self) -> bool: ...

        def __call__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> Parallel: ...

        def __dir__(self) -> List: ...

        def __getattr__(self, key: Any) -> Any: ...

        def __getitem__(self, item: V) -> Any: ...

        def __hash__(self) -> int: ...

        def __help__(self) -> Any: ...

        def __init__(
                self, 
                *, 
                component: Union[ParallelComponent, str], 
                compute: Optional[str] = ..., 
                environment_variables: Optional[Dict] = ..., 
                error_threshold: Optional[int] = ..., 
                identity: Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration, Dict]] = ..., 
                input_data: Optional[str] = ..., 
                inputs: Optional[Dict[str, Union[NodeOutput, Input, str, bool, int, float, Enum]]] = ..., 
                logging_level: Optional[str] = ..., 
                max_concurrency_per_instance: Optional[int] = ..., 
                mini_batch_error_threshold: Optional[int] = ..., 
                mini_batch_size: Optional[Union[str, int]] = ..., 
                outputs: Optional[Dict[str, Union[str, Output, Output]]] = ..., 
                partition_keys: Optional[List] = ..., 
                resources: Optional[JobResourceConfiguration] = ..., 
                retry_settings: Optional[Union[RetrySettings, Dict[str, str]]] = ..., 
                task: Optional[Union[ParallelTask, RunFunction, Dict]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __setitem__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def set_resources(
                self, 
                *, 
                docker_args: Optional[str] = ..., 
                instance_count: Optional[int] = ..., 
                instance_type: Optional[Union[str, List[str]]] = ..., 
                properties: Optional[Dict] = ..., 
                shm_size: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ParallelComponent(Component, ParameterizedParallel, ComponentCodeMixin):
        property base_path: str    # Read-only
        property code: Optional[str]
        property creation_context: Optional[SystemData]    # Read-only
        property display_name: Optional[str]
        property environment: Optional[str]
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property instance_count: Optional[int]
        property is_deterministic: Optional[bool]    # Read-only
        property outputs: Dict    # Read-only
        property resources: Optional[Union[dict, JobResourceConfiguration]]
        property retry_settings: Optional[RetrySettings]
        property task: Optional[ParallelTask]
        property type: Optional[str]    # Read-only
        property version: Optional[str]

        def __call__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> BaseNode: ...

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                error_threshold: Optional[int] = ..., 
                input_data: Optional[str] = ..., 
                inputs: Optional[Dict] = ..., 
                instance_count: Optional[int] = ..., 
                is_deterministic: bool = True, 
                logging_level: Optional[str] = ..., 
                max_concurrency_per_instance: Optional[int] = ..., 
                mini_batch_error_threshold: Optional[int] = ..., 
                mini_batch_size: Optional[str] = ..., 
                name: Optional[str] = ..., 
                outputs: Optional[Dict] = ..., 
                partition_keys: Optional[List] = ..., 
                resources: Optional[JobResourceConfiguration] = ..., 
                retry_settings: Optional[RetrySettings] = ..., 
                tags: Optional[Dict[str, Any]] = ..., 
                task: Optional[ParallelTask] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ParallelTask(RestTranslatableMixin, DictMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                append_row_to: Optional[str] = ..., 
                code: Optional[str] = ..., 
                entry_script: Optional[str] = ..., 
                environment: Optional[Union[Environment, str]] = ..., 
                model: Optional[str] = ..., 
                program_arguments: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ParameterizedCommand:
        property distribution: Optional[Union[dict, MpiDistribution, TensorFlowDistribution, PyTorchDistribution, RayDistribution, DistributionConfiguration]]
        property resources: JobResourceConfiguration

        def __init__(
                self, 
                command: Optional[str] = "", 
                resources: Optional[Union[dict, JobResourceConfiguration]] = None, 
                code: Optional[Union[str, PathLike]] = None, 
                environment_variables: Optional[Dict] = None, 
                distribution: Optional[Union[Dict, MpiDistribution, TensorFlowDistribution, PyTorchDistribution, RayDistribution, DistributionConfiguration]] = None, 
                environment: Optional[Union[Environment, str]] = None, 
                queue_settings: Optional[QueueSettings] = None, 
                **kwargs: Dict
            ) -> None: ...


    class azure.ai.ml.entities.PatTokenConfiguration(RestTranslatableMixin, DictMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                pat: Optional[str]
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.Pipeline(BaseNode):
        property base_path: str    # Read-only
        property component: Optional[Union[str, Component]]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property log_files: Optional[Dict[str, str]]    # Read-only
        property name: Optional[str]
        property outputs: Dict    # Read-only
        property settings: Optional[PipelineJobSettings]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __bool__(self) -> bool: ...

        def __dir__(self) -> List: ...

        def __getattr__(self, key: Any) -> Any: ...

        def __getitem__(self, item: V) -> Any: ...

        def __hash__(self) -> int: ...

        def __help__(self) -> Any: ...

        def __init__(
                self, 
                *, 
                component: Union[Component, str], 
                inputs: Optional[Dict[str, Union[Input, str, bool, int, float, Enum, Input]]] = ..., 
                outputs: Optional[Dict[str, Union[str, Output, Output]]] = ..., 
                settings: Optional[PipelineJobSettings] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __setitem__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.PipelineComponent(Component):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property display_name: Optional[str]
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property is_deterministic: Optional[bool]    # Read-only
        property jobs: Dict[str, BaseNode]    # Read-only
        property outputs: Dict    # Read-only
        property type: Optional[str]    # Read-only
        property version: Optional[str]

        def __call__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> BaseNode: ...

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                inputs: Optional[Dict] = ..., 
                is_deterministic: Optional[bool] = ..., 
                jobs: Optional[Dict[str, BaseNode]] = ..., 
                name: Optional[str] = ..., 
                outputs: Optional[Dict] = ..., 
                tags: Optional[Dict] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.PipelineComponentBatchDeployment(BatchDeployment):
        property base_path: str    # Read-only
        property code_path: Optional[Union[str, PathLike]]
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property instance_count: Optional[int]
        property provisioning_state: Optional[str]    # Read-only
        property scoring_script: Optional[Union[str, PathLike]]
        property type: Optional[str]    # Read-only

        def __getattr__(self, name: str) -> Optional[Any]: ...

        def __init__(
                self, 
                *, 
                component: Optional[Union[Component, str]] = ..., 
                description: Optional[str] = ..., 
                endpoint_name: Optional[str] = ..., 
                job_definition: Optional[Dict[str, BaseNode]] = ..., 
                name: str, 
                settings: Optional[Dict[str, str]] = ..., 
                tags: Optional[Dict] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                name, 
                value
            ): ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.PipelineJob(Job, YamlTranslatableMixin, PipelineJobIOMixin, PathAwareSchemaValidatableMixin):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property jobs: Dict    # Read-only
        property log_files: Optional[Dict[str, str]]    # Read-only
        property outputs: Dict[str, Union[str, Output]]    # Read-only
        property settings: Optional[PipelineJobSettings]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                component: Optional[Union[str, PipelineComponent, Component]] = ..., 
                compute: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                experiment_name: Optional[str] = ..., 
                identity: Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]] = ..., 
                inputs: Optional[Dict[str, Union[Input, str, bool, int, float]]] = ..., 
                jobs: Optional[Dict[str, BaseNode]] = ..., 
                name: Optional[str] = ..., 
                outputs: Optional[Dict[str, Output]] = ..., 
                settings: Optional[PipelineJobSettings] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.PipelineJobSettings(_AttrDict):

        def __bool__(self) -> bool: ...

        def __dir__(self) -> List: ...

        def __getattr__(self, key: Any) -> Any: ...

        def __getitem__(self, item: V) -> Any: ...

        def __init__(
                self, 
                default_datastore: Optional[str] = None, 
                default_compute: Optional[str] = None, 
                continue_on_step_failure: Optional[bool] = None, 
                force_rerun: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        def __setattr__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __setitem__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...


    class azure.ai.ml.entities.PredictionDriftMetricThreshold(MetricThreshold):

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                categorical: Optional[CategoricalDriftMetrics] = ..., 
                data_type: Optional[MonitorFeatureType] = ..., 
                numerical: Optional[NumericalDriftMetrics] = ..., 
                threshold: Optional[float] = ...
            ): ...


    class azure.ai.ml.entities.PredictionDriftSignal(MonitoringSignal):
        type: str

        def __init__(
                self, 
                *, 
                alert_enabled: bool = False, 
                metric_thresholds: PredictionDriftMetricThreshold, 
                production_data: Optional[ProductionData] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                reference_data: Optional[ReferenceData] = ...
            ): ...


    class azure.ai.ml.entities.PrivateEndpoint:

        def __init__(
                self, 
                approval_type: Optional[str] = None, 
                connections: Optional[Dict[str, EndpointConnection]] = None
            ): ...


    class azure.ai.ml.entities.PrivateEndpointDestination(OutboundRule):
        type: str

        def __init__(
                self, 
                *, 
                fqdns: Optional[List[str]] = ..., 
                name: str, 
                service_resource_id: str, 
                spark_enabled: bool = False, 
                subresource_target: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ProbeSettings(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                failure_threshold: Optional[int] = ..., 
                initial_delay: Optional[int] = ..., 
                period: Optional[int] = ..., 
                success_threshold: Optional[int] = ..., 
                timeout: Optional[int] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.entities.ProductionData(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                data_column_names: Optional[Dict[str, str]] = ..., 
                data_context: Optional[MonitorDatasetContext] = ..., 
                data_window: Optional[BaselineDataRange] = ..., 
                input_data: Input, 
                pre_processing_component: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.Project(Workspace):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property discovery_url: Optional[str]    # Read-only
        property hub_id: str
        property id: Optional[str]    # Read-only
        property mlflow_tracking_uri: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                hub_id: str, 
                location: Optional[str] = ..., 
                name: str, 
                resource_group: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.QueueSettings(RestTranslatableMixin, DictMixin): implements Collection , Mapping 
        job_tier: Union[str, JobTier]
        priority: str

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                job_tier: Optional[str] = ..., 
                priority: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.RecurrencePattern(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                hours: Union[int, List[int]], 
                minutes: Union[int, List[int]], 
                month_days: Optional[Union[int, List[int]]] = ..., 
                week_days: Optional[Union[str, List[str]]] = ...
            ) -> None: ...


    class azure.ai.ml.entities.RecurrenceTrigger(TriggerBase):

        def __init__(
                self, 
                *, 
                end_time: Optional[Union[str, datetime]] = ..., 
                frequency: str, 
                interval: int, 
                schedule: Optional[RecurrencePattern] = ..., 
                start_time: Optional[Union[str, datetime]] = ..., 
                time_zone: Union[str, TimeZone] = TimeZone.UTC
            ) -> None: ...


    class azure.ai.ml.entities.ReferenceData(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                data_column_names: Optional[Dict[str, str]] = ..., 
                data_context: Optional[MonitorDatasetContext] = ..., 
                data_window: Optional[BaselineDataRange] = ..., 
                input_data: Input, 
                pre_processing_component: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.Registry(Resource):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                discovery_url: Optional[str] = ..., 
                identity: Optional[IdentityConfiguration] = ..., 
                intellectual_property: Optional[IntellectualProperty] = ..., 
                location: str, 
                managed_resource_group: Optional[str] = ..., 
                mlflow_registry_uri: Optional[str] = ..., 
                name: str, 
                public_network_access: Optional[str] = ..., 
                replication_locations: Optional[List[RegistryRegionDetails]], 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.RegistryRegionDetails:

        def __init__(
                self, 
                *, 
                acr_config: Optional[List[Union[str, SystemCreatedAcrAccount]]] = ..., 
                location: Optional[str] = ..., 
                storage_config: Optional[Union[List[str], SystemCreatedStorageAccount]] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.RequestLogging:

        def __init__(
                self, 
                *, 
                capture_headers: Optional[List[str]] = ..., 
                **kwargs: Any
            ): ...


    class azure.ai.ml.entities.Resource(abc.ABC):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only

        def __init__(
                self, 
                name: Optional[str], 
                description: Optional[str] = None, 
                tags: Optional[Dict] = None, 
                properties: Optional[Dict] = None, 
                *, 
                print_as_yaml: bool = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        @abc.abstractmethod
        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> Any: ...


    class azure.ai.ml.entities.ResourceConfiguration(RestTranslatableMixin, DictMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                instance_type: Optional[str] = ..., 
                properties: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ResourceRequirementsSettings(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                requests: Optional[ResourceSettings] = None, 
                limits: Optional[ResourceSettings] = None
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.entities.ResourceSettings(RestTranslatableMixin):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                cpu: Optional[str] = None, 
                memory: Optional[str] = None, 
                gpu: Optional[str] = None
            ) -> None: ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.entities.RetrySettings(RestTranslatableMixin, DictMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                max_retries: Optional[Union[int, str]] = ..., 
                timeout: Optional[Union[int, str]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.Route:

        def __init__(
                self, 
                *, 
                path: Optional[str] = ..., 
                port: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.SasTokenConfiguration(RestTranslatableMixin, DictMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                sas_token: Optional[str]
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.Schedule(YamlTranslatableMixin, PathAwareSchemaValidatableMixin, Resource):
        property base_path: str    # Read-only
        property create_job: Any
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property is_enabled: bool    # Read-only
        property provisioning_state: str    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: str, 
                properties: Optional[Dict] = ..., 
                tags: Optional[Dict] = ..., 
                trigger: Optional[Union[CronTrigger, RecurrenceTrigger]], 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ScheduleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.ai.ml.entities.ScheduleTriggerResult:
        job_name: str
        schedule_action_type: str

        def __init__(self, **kwargs): ...


    class azure.ai.ml.entities.ScriptReference(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                command: Optional[str] = ..., 
                path: Optional[str] = ..., 
                timeout_minutes: Optional[int] = ...
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.SerpConnection(ApiOrAadConnection):
        property api_base: Optional[str]    # Read-only
        property api_key: Optional[str]
        property azure_endpoint: Optional[str]    # Read-only
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration]    # Read-only
        property endpoint: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property is_shared: bool
        property metadata: Optional[Dict[str, Any]]
        property tags: Optional[Dict[str, Any]]
        property target: Optional[str]    # Read-only
        property type: Optional[str]
        property url: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                metadata: Optional[Dict[Any, Any]] = ..., 
                **kwargs
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ServerlessComputeSettings:
        custom_subnet: Optional[ArmId]
        no_public_ip: bool = False

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_subnet: Optional[Union[str, ArmId]] = ..., 
                no_public_ip: bool = False
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.ServerlessConnection(ApiOrAadConnection):
        property api_base: Optional[str]    # Read-only
        property api_key: Optional[str]
        property azure_endpoint: Optional[str]    # Read-only
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration]    # Read-only
        property endpoint: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property is_shared: bool
        property metadata: Optional[Dict[str, Any]]
        property tags: Optional[Dict[str, Any]]
        property target: Optional[str]    # Read-only
        property type: Optional[str]
        property url: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                endpoint: str, 
                metadata: Optional[Dict[Any, Any]] = ..., 
                **kwargs
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.ServerlessEndpoint(_ServerlessEndpoint, ValidationMixin):
        auth_mode: str
        description: str
        headers
        id: dict[str, str]
        location: str
        model_id: str
        name: str
        properties: dict[str, str]
        provisioning_state: str
        scoring_uri: str
        system_data: Optional[SystemData]
        tags: dict[str, str]

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def as_dict(
                self, 
                *, 
                exclude_readonly: bool = False
            ) -> Dict[str, Any]: ...


    class azure.ai.ml.entities.ServerlessSparkCompute:

        def __init__(
                self, 
                *, 
                instance_type: str, 
                runtime_version: str
            ): ...


    class azure.ai.ml.entities.ServiceInstance(RestTranslatableMixin, DictMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
                error: Optional[str] = ..., 
                port: Optional[int] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                status: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ServicePrincipalConfiguration(BaseTenantCredentials): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                client_secret: Optional[str], 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ServiceTagDestination(OutboundRule):
        type: str

        def __init__(
                self, 
                *, 
                address_prefixes: Optional[List[str]] = ..., 
                name: str, 
                port_ranges: str, 
                protocol: str, 
                service_tag: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.SetupScripts(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                creation_script: Optional[ScriptReference] = ..., 
                startup_script: Optional[ScriptReference] = ...
            ) -> None: ...


    class azure.ai.ml.entities.Spark(BaseNode, SparkJobEntryMixin):
        property base_path: str    # Read-only
        property code: Optional[Union[str, PathLike]]
        property component: Union[str, SparkComponent]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property entry: Optional[Union[Dict[str, str], SparkJobEntry]]
        property id: Optional[str]    # Read-only
        property identity: Optional[Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]]
        property inputs: Dict    # Read-only
        property log_files: Optional[Dict[str, str]]    # Read-only
        property name: Optional[str]
        property outputs: Dict    # Read-only
        property resources: Optional[Union[Dict, SparkResourceConfiguration]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __bool__(self) -> bool: ...

        def __call__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> Spark: ...

        def __dir__(self) -> List: ...

        def __getattr__(self, key: Any) -> Any: ...

        def __getitem__(self, item: V) -> Any: ...

        def __hash__(self) -> int: ...

        def __help__(self) -> Any: ...

        def __init__(
                self, 
                *, 
                archives: Optional[List[str]] = ..., 
                args: Optional[str] = ..., 
                component: Union[str, SparkComponent], 
                compute: Optional[str] = ..., 
                conf: Optional[Dict[str, str]] = ..., 
                driver_cores: Optional[Union[int, str]] = ..., 
                driver_memory: Optional[str] = ..., 
                dynamic_allocation_enabled: Optional[Union[bool, str]] = ..., 
                dynamic_allocation_max_executors: Optional[Union[int, str]] = ..., 
                dynamic_allocation_min_executors: Optional[Union[int, str]] = ..., 
                entry: Union[Dict[str, str], SparkJobEntry, None] = ..., 
                executor_cores: Optional[Union[int, str]] = ..., 
                executor_instances: Optional[Union[int, str]] = ..., 
                executor_memory: Optional[str] = ..., 
                files: Optional[List[str]] = ..., 
                identity: Optional[Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]] = ..., 
                inputs: Optional[Dict[str, Union[NodeOutput, Input, str, bool, int, float, Enum, Input]]] = ..., 
                jars: Optional[List[str]] = ..., 
                outputs: Optional[Dict[str, Union[str, Output, Output]]] = ..., 
                py_files: Optional[List[str]] = ..., 
                resources: Optional[Union[Dict, SparkResourceConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __setitem__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.SparkComponent(Component, ParameterizedSpark, SparkJobEntryMixin, AdditionalIncludesMixin):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property display_name: Optional[str]
        property entry: Optional[Union[Dict[str, str], SparkJobEntry]]
        property environment: Optional[Union[str, Environment]]
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property is_deterministic: Optional[bool]    # Read-only
        property outputs: Dict    # Read-only
        property type: Optional[str]    # Read-only
        property version: Optional[str]

        def __call__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> BaseNode: ...

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_includes: Optional[List] = ..., 
                archives: Optional[List[str]] = ..., 
                args: Optional[str] = ..., 
                code: Optional[Union[str, PathLike]] = ".", 
                conf: Optional[Dict[str, str]] = ..., 
                driver_cores: Optional[Union[int, str]] = ..., 
                driver_memory: Optional[str] = ..., 
                dynamic_allocation_enabled: Optional[Union[bool, str]] = ..., 
                dynamic_allocation_max_executors: Optional[Union[int, str]] = ..., 
                dynamic_allocation_min_executors: Optional[Union[int, str]] = ..., 
                entry: Optional[Union[Dict[str, str], SparkJobEntry]] = ..., 
                environment: Optional[Union[str, Environment]] = ..., 
                executor_cores: Optional[Union[int, str]] = ..., 
                executor_instances: Optional[Union[int, str]] = ..., 
                executor_memory: Optional[str] = ..., 
                files: Optional[List[str]] = ..., 
                inputs: Optional[Dict] = ..., 
                jars: Optional[List[str]] = ..., 
                outputs: Optional[Dict] = ..., 
                py_files: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.SparkJob(Job, ParameterizedSpark, JobIOMixin, SparkJobEntryMixin):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property entry: Optional[Union[Dict[str, str], SparkJobEntry]]
        property environment: Optional[Union[str, Environment]]
        property id: Optional[str]    # Read-only
        property identity: Optional[Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]]
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property log_files: Optional[Dict[str, str]]    # Read-only
        property outputs: Dict[str, Output]
        property resources: Optional[Union[Dict, SparkResourceConfiguration]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                compute: Optional[str] = ..., 
                driver_cores: Optional[Union[int, str]] = ..., 
                driver_memory: Optional[str] = ..., 
                dynamic_allocation_enabled: Optional[Union[bool, str]] = ..., 
                dynamic_allocation_max_executors: Optional[Union[int, str]] = ..., 
                dynamic_allocation_min_executors: Optional[Union[int, str]] = ..., 
                executor_cores: Optional[Union[int, str]] = ..., 
                executor_instances: Optional[Union[int, str]] = ..., 
                executor_memory: Optional[str] = ..., 
                identity: Optional[Union[Dict[str, str], ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]] = ..., 
                inputs: Optional[Dict[str, Union[Input, str, bool, int, float]]] = ..., 
                outputs: Optional[Dict[str, Output]] = ..., 
                resources: Optional[Union[Dict, SparkResourceConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def filter_conf_fields(self) -> Dict[str, str]: ...


    class azure.ai.ml.entities.SparkJobEntry(RestTranslatableMixin):

        def __init__(
                self, 
                *, 
                entry: str, 
                type: str = SparkJobEntryType.SPARK_JOB_FILE_ENTRY
            ) -> None: ...


    class azure.ai.ml.entities.SparkJobEntryType:
        SPARK_JOB_CLASS_ENTRY = SparkJobScalaEntry
        SPARK_JOB_FILE_ENTRY = SparkJobPythonEntry


    class azure.ai.ml.entities.SparkResourceConfiguration(RestTranslatableMixin, DictMixin): implements Collection , Mapping 
        instance_type_list = ['standard_e4s_v3', 'standard_e8s_v3', 'standard_e16s_v3', 'standard_e32s_v3', 'standard_e64s_v3']

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                instance_type: Optional[str] = ..., 
                runtime_version: Optional[str] = ...
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.SshJobService(JobServiceBase): implements Collection , Mapping 
        type: str

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
                nodes: Optional[Literal[all]] = ..., 
                port: Optional[int] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                ssh_public_keys: Optional[str] = ..., 
                status: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.StaticInputData(MonitorInputData):
        type

        def __init__(
                self, 
                *, 
                data_context: Optional[MonitorDatasetContext] = ..., 
                job_type: Optional[str] = ..., 
                pre_processing_component_id: Optional[str] = ..., 
                target_columns: Optional[Dict] = ..., 
                uri: Optional[str] = ..., 
                window_end: Optional[str] = ..., 
                window_start: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.Sweep(ParameterizedSweep, BaseNode):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property early_termination: Optional[Union[str, EarlyTerminationPolicy]]
        property id: Optional[str]    # Read-only
        property inputs: Dict    # Read-only
        property limits: Optional[SweepJobLimits]
        property log_files: Optional[Dict[str, str]]    # Read-only
        property name: Optional[str]
        property outputs: Dict    # Read-only
        property resources: Optional[Union[dict, JobResourceConfiguration]]
        property sampling_algorithm: Optional[Union[str, SamplingAlgorithm]]
        property search_space: Optional[Dict[str, Union[Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property trial: CommandComponent    # Read-only
        property type: Optional[str]    # Read-only

        def __bool__(self) -> bool: ...

        def __dir__(self) -> List: ...

        def __getattr__(self, key: Any) -> Any: ...

        def __getitem__(self, item: V) -> Any: ...

        def __hash__(self) -> int: ...

        def __help__(self) -> Any: ...

        def __init__(
                self, 
                *, 
                compute: Optional[str] = ..., 
                early_termination: Optional[Union[BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy, EarlyTerminationPolicy, str]] = ..., 
                identity: Optional[Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]] = ..., 
                inputs: Optional[Dict[str, Union[Input, str, bool, int, float]]] = ..., 
                limits: Optional[SweepJobLimits] = ..., 
                objective: Optional[Objective] = ..., 
                outputs: Optional[Dict[str, Union[str, Output]]] = ..., 
                queue_settings: Optional[QueueSettings] = ..., 
                resources: Optional[Union[dict, JobResourceConfiguration]] = ..., 
                sampling_algorithm: Optional[Union[str, SamplingAlgorithm]] = ..., 
                search_space: Optional[Dict[str, Union[Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]]] = ..., 
                trial: Optional[Union[CommandComponent, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                key: Any, 
                value: Any
            ) -> None: ...

        def __setitem__(
                self, 
                key: Any, 
                value: V
            ) -> None: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                max_concurrent_trials: Optional[int] = ..., 
                max_total_trials: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                trial_timeout: Optional[int] = ...
            ) -> None: ...

        def set_objective(
                self, 
                *, 
                goal: Optional[str] = ..., 
                primary_metric: Optional[str] = ...
            ) -> None: ...

        def set_resources(
                self, 
                *, 
                docker_args: Optional[str] = ..., 
                instance_count: Optional[int] = ..., 
                instance_type: Optional[Union[str, List[str]]] = ..., 
                locations: Optional[List[str]] = ..., 
                properties: Optional[Dict] = ..., 
                shm_size: Optional[str] = ...
            ) -> None: ...


    @experimental
    class azure.ai.ml.entities.SynapseSparkCompute(Compute):
        property base_path: str    # Read-only
        property created_on: Optional[str]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property provisioning_errors: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                auto_pause_settings: Optional[AutoPauseSettings] = ..., 
                description: Optional[str] = ..., 
                identity: Optional[IdentityConfiguration] = ..., 
                name: str, 
                node_count: Optional[int] = ..., 
                node_family: Optional[str] = ..., 
                node_size: Optional[str] = ..., 
                scale_settings: Optional[AutoScaleSettings] = ..., 
                spark_version: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.SystemCreatedAcrAccount:

        def __init__(
                self, 
                *, 
                acr_account_sku: str, 
                arm_resource_id: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.SystemCreatedStorageAccount:

        def __init__(
                self, 
                *, 
                arm_resource_id: Optional[str] = ..., 
                replicated_ids: Optional[List[str]] = ..., 
                replication_count: int = 1, 
                storage_account_hns: bool, 
                storage_account_type: Optional[StorageAccountType]
            ): ...


    class azure.ai.ml.entities.SystemData(RestTranslatableMixin):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __init__(
                self, 
                *, 
                created_at: datetime = ..., 
                created_by: str = ..., 
                created_by_type: Union[str, CreatedByType] = ..., 
                last_modified_at: datetime = ..., 
                last_modified_by: str = ..., 
                last_modified_by_type: Union[str, CreatedByType] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.TargetUtilizationScaleSettings(OnlineScaleSettings):
        type: str

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                max_instances: Optional[int] = ..., 
                min_instances: Optional[int] = ..., 
                polling_interval: Optional[int] = ..., 
                target_utilization_percentage: Optional[int] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: object) -> bool: ...


    class azure.ai.ml.entities.TensorBoardJobService(JobServiceBase): implements Collection , Mapping 
        type: str

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
                log_dir: Optional[str] = ..., 
                nodes: Optional[Literal[all]] = ..., 
                port: Optional[int] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                status: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.TrailingInputData(MonitorInputData):
        type

        def __init__(
                self, 
                *, 
                data_context: Optional[MonitorDatasetContext] = ..., 
                job_type: Optional[str] = ..., 
                pre_processing_component_id: Optional[str] = ..., 
                target_columns: Optional[Dict] = ..., 
                uri: Optional[str] = ..., 
                window_offset: Optional[str] = ..., 
                window_size: Optional[str] = ...
            ): ...


    @experimental
    class azure.ai.ml.entities.TritonInferencingServer:
        type

        def __init__(
                self, 
                *, 
                inference_configuration: Optional[CodeConfiguration] = ..., 
                **kwargs: Any
            ): ...


    class azure.ai.ml.entities.UnsupportedCompute(Compute):
        property base_path: str    # Read-only
        property created_on: Optional[str]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property provisioning_errors: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.Usage(RestTranslatableMixin):

        def __init__(
                self, 
                id: Optional[str] = None, 
                aml_workspace_location: Optional[str] = None, 
                type: Optional[str] = None, 
                unit: Optional[Union[str, UsageUnit]] = None, 
                current_value: Optional[int] = None, 
                limit: Optional[int] = None, 
                name: Optional[UsageName] = None
            ) -> None: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.UsageName:

        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...


    class azure.ai.ml.entities.UsageUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "Count"


    class azure.ai.ml.entities.UserIdentityConfiguration(_BaseIdentityConfiguration): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(self) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.UsernamePasswordConfiguration(RestTranslatableMixin, DictMixin): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                password: Optional[str], 
                username: Optional[str]
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.ValidationResult:
        property error_messages: Dict    # Read-only
        property passed: bool    # Read-only

        def __init__(self) -> None: ...

        def __repr__(self) -> str: ...


    class azure.ai.ml.entities.VirtualMachineCompute(Compute):
        property base_path: str    # Read-only
        property created_on: Optional[str]    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property provisioning_errors: Optional[str]    # Read-only
        property provisioning_state: Optional[str]    # Read-only
        property public_key_data: str    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                resource_id: str, 
                ssh_settings: Optional[VirtualMachineSshSettings] = ..., 
                tags: Optional[dict] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.VirtualMachineSshSettings:

        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                admin_username: Optional[str], 
                ssh_port: Optional[int] = 22, 
                ssh_private_key_file: Optional[str] = ...
            ) -> None: ...


    class azure.ai.ml.entities.VmSize(RestTranslatableMixin):

        def __init__(
                self, 
                name: Optional[str] = None, 
                family: Optional[str] = None, 
                v_cp_us: Optional[int] = None, 
                gpus: Optional[int] = None, 
                os_vhd_size_mb: Optional[int] = None, 
                max_resource_volume_mb: Optional[int] = None, 
                memory_gb: Optional[float] = None, 
                low_priority_capable: Optional[bool] = None, 
                premium_io: Optional[bool] = None, 
                supported_compute_types: Optional[List[str]] = None
            ) -> None: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.VolumeSettings:

        def __init__(
                self, 
                *, 
                source: str, 
                target: str
            ): ...


    class azure.ai.ml.entities.VsCodeJobService(JobServiceBase): implements Collection , Mapping 
        type: str

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
                nodes: Optional[Literal[all]] = ..., 
                port: Optional[int] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                status: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.Workspace(Resource):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property discovery_url: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property mlflow_tracking_uri: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                allow_roleassignment_on_rg: Optional[bool] = ..., 
                application_insights: Optional[str] = ..., 
                container_registry: Optional[str] = ..., 
                customer_managed_key: Optional[CustomerManagedKey] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enable_data_isolation: bool = False, 
                hbi_workspace: bool = False, 
                hub_id: Optional[str] = ..., 
                identity: Optional[IdentityConfiguration] = ..., 
                image_build_compute: Optional[str] = ..., 
                key_vault: Optional[str] = ..., 
                location: Optional[str] = ..., 
                managed_network: Optional[ManagedNetwork] = ..., 
                name: str, 
                network_acls: Optional[NetworkAcls] = ..., 
                primary_user_assigned_identity: Optional[str] = ..., 
                provision_network_now: Optional[bool] = ..., 
                public_network_access: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                serverless_compute: Optional[ServerlessComputeSettings] = ..., 
                storage_account: Optional[str] = ..., 
                system_datastores_auth_mode: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                workspace_hub: Optional[str] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.WorkspaceConnection(Resource):
        property api_base: Optional[str]    # Read-only
        property azure_endpoint: Optional[str]    # Read-only
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration]    # Read-only
        property endpoint: Optional[str]    # Read-only
        property id: Optional[str]    # Read-only
        property is_shared: bool
        property metadata: Optional[Dict[str, Any]]
        property tags: Optional[Dict[str, Any]]
        property target: Optional[str]    # Read-only
        property type: Optional[str]
        property url: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                credentials: Union[PatTokenConfiguration, SasTokenConfiguration, UsernamePasswordConfiguration, ManagedIdentityConfiguration, ServicePrincipalConfiguration, AccessKeyConfiguration, ApiKeyConfiguration, NoneCredentialConfiguration, AccountKeyConfiguration, AadCredentialConfiguration], 
                is_shared: bool = True, 
                metadata: Optional[Dict[str, Any]] = ..., 
                type: str, 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.entities.WorkspaceKeys:

        def __init__(
                self, 
                *, 
                app_insights_instrumentation_key: Optional[str] = ..., 
                container_registry_credentials: Optional[ContainerRegistryCredential] = ..., 
                notebook_access_keys: Optional[NotebookAccessKeys] = ..., 
                user_storage_key: Optional[str] = ..., 
                user_storage_resource_id: Optional[str] = ...
            ): ...


    class azure.ai.ml.entities.WorkspaceModelReference(Asset):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property version: Optional[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                asset_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[Dict] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ): ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


namespace azure.ai.ml.exceptions

    class azure.ai.ml.exceptions.AssetException(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message: str, 
                no_personal_data_message: str, 
                *args, 
                *, 
                error_category: ErrorCategory = ErrorCategory.UNKNOWN, 
                target: ErrorTarget = ErrorTarget.UNKNOWN, 
                **kwargs
            ): ...


    class azure.ai.ml.exceptions.AssetPathException(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message: str, 
                no_personal_data_message: str, 
                *args, 
                *, 
                error_category: ErrorCategory = ErrorCategory.UNKNOWN, 
                target: ErrorTarget = ErrorTarget.UNKNOWN, 
                **kwargs
            ): ...


    class azure.ai.ml.exceptions.CannotSetAttributeError(UserErrorException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(self, object_name): ...


    class azure.ai.ml.exceptions.CloudArtifactsNotSupportedError(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                endpoint_name: str, 
                invalid_artifact: str, 
                deployment_name: Optional[str] = None, 
                error_category = ErrorCategory.USER_ERROR
            ): ...


    class azure.ai.ml.exceptions.ComponentException(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message: str, 
                no_personal_data_message: str, 
                *args, 
                *, 
                error_category: ErrorCategory = ErrorCategory.UNKNOWN, 
                target: ErrorTarget = ErrorTarget.UNKNOWN, 
                **kwargs
            ): ...


    class azure.ai.ml.exceptions.DeploymentException(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message: str, 
                no_personal_data_message: str, 
                *args, 
                *, 
                error_category: ErrorCategory = ErrorCategory.UNKNOWN, 
                target: ErrorTarget = ErrorTarget.UNKNOWN, 
                **kwargs
            ): ...


    class azure.ai.ml.exceptions.DockerEngineNotAvailableError(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(self, error_category = ErrorCategory.UNKNOWN): ...


    class azure.ai.ml.exceptions.EmptyDirectoryError(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message: str, 
                no_personal_data_message: str, 
                target: ErrorTarget = ErrorTarget.UNKNOWN, 
                error_category: ErrorCategory = ErrorCategory.UNKNOWN
            ): ...


    class azure.ai.ml.exceptions.ErrorCategory:
        SYSTEM_ERROR = SystemError
        UNKNOWN = Unknown
        USER_ERROR = UserError


    class azure.ai.ml.exceptions.ErrorTarget:
        ARM_DEPLOYMENT = ArmDeployment
        ARM_RESOURCE = ArmResource
        ARTIFACT = Artifact
        ASSET = Asset
        AUTOML = AutoML
        BATCH_DEPLOYMENT = BatchDeployment
        BATCH_ENDPOINT = BatchEndpoint
        BLOB_DATASTORE = BlobDatastore
        CAPABILITY_HOST = CapabilityHost
        CODE = Code
        COMMAND_JOB = CommandJob
        COMPONENT = Component
        COMPUTE = Compute
        DATA = Data
        DATASTORE = Datastore
        DATA_TRANSFER_JOB = DataTransferJob
        DEPLOYMENT = Deployment
        ENDPOINT = Endpoint
        ENVIRONMENT = Environment
        FEATURE_SET = FeatureSet
        FEATURE_STORE_ENTITY = FeatureStoreEntity
        FILE_DATASTORE = FileDatastore
        FINETUNING = FineTuning
        GEN1_DATASTORE = Gen1Datastore
        GEN2_DATASTORE = Gen2Datastore
        GENERAL = General
        IDENTITY = Identity
        INDEX = Index
        JOB = Job
        LOCAL_ENDPOINT = LocalEndpoint
        LOCAL_JOB = LocalJob
        MODEL = Model
        MODEL_MONITORING = ModelMonitoring
        ONLINE_DEPLOYMENT = OnlineDeployment
        ONLINE_ENDPOINT = OnlineEndpoint
        PIPELINE = Pipeline
        REGISTRY = Registry
        SCHEDULE = Schedule
        SERVERLESS_ENDPOINT = ServerlessEndpoint
        SPARK_JOB = SparkJob
        SWEEP_JOB = SweepJob
        UNKNOWN = Unknown
        WORKSPACE = Workspace


    class azure.ai.ml.exceptions.InvalidLocalEndpointError(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message: str, 
                no_personal_data_message: str, 
                error_category = ErrorCategory.USER_ERROR
            ): ...


    class azure.ai.ml.exceptions.InvalidVSCodeRequestError(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                error_category = ErrorCategory.USER_ERROR, 
                msg = None
            ): ...


    class azure.ai.ml.exceptions.JobException(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message: str, 
                no_personal_data_message: str, 
                *args, 
                *, 
                error_category: ErrorCategory = ErrorCategory.UNKNOWN, 
                target: ErrorTarget = ErrorTarget.UNKNOWN, 
                **kwargs
            ): ...


    class azure.ai.ml.exceptions.JobParsingError(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                error_category, 
                no_personal_data_message, 
                message, 
                *args, 
                **kwargs
            ): ...


    class azure.ai.ml.exceptions.KeywordError(UserErrorException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message, 
                no_personal_data_message = None
            ): ...


    class azure.ai.ml.exceptions.LocalDeploymentGPUNotAvailable(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                error_category = ErrorCategory.USER_ERROR, 
                msg = None
            ): ...


    class azure.ai.ml.exceptions.LocalEndpointImageBuildError(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                error: Union[str, Exception], 
                error_category = ErrorCategory.UNKNOWN
            ): ...


    class azure.ai.ml.exceptions.LocalEndpointInFailedStateError(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                endpoint_name, 
                deployment_name = None, 
                error_category = ErrorCategory.UNKNOWN
            ): ...


    class azure.ai.ml.exceptions.LocalEndpointNotFoundError(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                endpoint_name: str, 
                deployment_name: Optional[str] = None, 
                error_category = ErrorCategory.USER_ERROR
            ): ...


    class azure.ai.ml.exceptions.MissingPositionalArgsError(KeywordError):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                func_name, 
                missing_args
            ): ...


    class azure.ai.ml.exceptions.MlException(AzureError):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message: str, 
                no_personal_data_message: str, 
                *args, 
                *, 
                error_category: ErrorCategory = ErrorCategory.UNKNOWN, 
                target: ErrorTarget = ErrorTarget.UNKNOWN, 
                **kwargs
            ): ...


    class azure.ai.ml.exceptions.ModelException(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message: str, 
                no_personal_data_message: str, 
                *args, 
                *, 
                error_category: ErrorCategory = ErrorCategory.UNKNOWN, 
                target: ErrorTarget = ErrorTarget.UNKNOWN, 
                **kwargs
            ): ...


    class azure.ai.ml.exceptions.MultipleLocalDeploymentsFoundError(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                endpoint_name: str, 
                error_category = ErrorCategory.UNKNOWN
            ): ...


    class azure.ai.ml.exceptions.MultipleValueError(KeywordError):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                func_name, 
                keyword
            ): ...


    class azure.ai.ml.exceptions.ParamValueNotExistsError(KeywordError):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                func_name, 
                keywords
            ): ...


    class azure.ai.ml.exceptions.PipelineChildJobError(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget
        ERROR_MESSAGE_TEMPLATE = az ml job {command} is not supported on pipeline child job, {prompt_message}.
        PROMPT_PARENT_MESSAGE = please use this command on pipeline parent job
        PROMPT_STUDIO_UI_MESSAGE = please go to studio UI to do related actions{url}

        def __init__(
                self, 
                job_id: str, 
                command: str = "parse", 
                prompt_studio_ui: bool = False
            ): ...


    class azure.ai.ml.exceptions.RequiredLocalArtifactsNotFoundError(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                endpoint_name: str, 
                required_artifact: str, 
                required_artifact_type: str, 
                deployment_name: Optional[str] = None, 
                error_category = ErrorCategory.USER_ERROR
            ): ...


    class azure.ai.ml.exceptions.ScheduleException(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message: str, 
                no_personal_data_message: str, 
                *args, 
                *, 
                error_category: ErrorCategory = ErrorCategory.UNKNOWN, 
                target: ErrorTarget = ErrorTarget.UNKNOWN, 
                **kwargs
            ): ...


    class azure.ai.ml.exceptions.TooManyPositionalArgsError(KeywordError):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                func_name, 
                min_number, 
                max_number, 
                given_number
            ): ...


    class azure.ai.ml.exceptions.UnexpectedAttributeError(KeywordError, AttributeError):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                keyword, 
                keywords = None
            ): ...


    class azure.ai.ml.exceptions.UnexpectedKeywordError(KeywordError):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                func_name, 
                keyword, 
                keywords = None
            ): ...


    class azure.ai.ml.exceptions.UnsupportedOperationError(UserErrorException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(self, operation_name): ...


    class azure.ai.ml.exceptions.UnsupportedParameterKindError(UserErrorException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                func_name, 
                parameter_kind = None
            ): ...


    class azure.ai.ml.exceptions.UserErrorException(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message, 
                no_personal_data_message = None, 
                error_category = ErrorCategory.USER_ERROR, 
                target: ErrorTarget = ErrorTarget.PIPELINE
            ): ...


    class azure.ai.ml.exceptions.VSCodeCommandNotFound(MlException):
        property error_category: ErrorCategory
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                output = None, 
                error_category = ErrorCategory.USER_ERROR
            ): ...


    class azure.ai.ml.exceptions.ValidationErrorType(Enum):
        CANNOT_PARSE = "CANNOT PARSE"
        CANNOT_SERIALIZE = "CANNOT DUMP"
        FILE_OR_FOLDER_NOT_FOUND = "FILE OR FOLDER NOT FOUND"
        GENERIC = "GENERIC"
        INVALID_VALUE = "INVALID VALUE"
        MISSING_FIELD = "MISSING FIELD"
        RESOURCE_NOT_FOUND = "RESOURCE NOT FOUND"
        UNKNOWN_FIELD = "UNKNOWN FIELD"


    class azure.ai.ml.exceptions.ValidationException(MlException):
        property error_category: ErrorCategory
        property error_type: ValidationErrorType
        property no_personal_data_message: str
        property target: ErrorTarget

        def __init__(
                self, 
                message: str, 
                no_personal_data_message: str, 
                *args, 
                *, 
                error_category: ErrorCategory = ErrorCategory.USER_ERROR, 
                error_type: ValidationErrorType = ValidationErrorType.GENERIC, 
                target: ErrorTarget = ErrorTarget.UNKNOWN, 
                **kwargs
            ): ...


namespace azure.ai.ml.finetuning

    @experimental
    def azure.ai.ml.finetuning.create_finetuning_job(
            *, 
            compute: Optional[str] = ..., 
            hyperparameters: Optional[Dict[str, str]] = ..., 
            instance_types: Optional[List[str]] = ..., 
            job_tier: Optional[str] = ..., 
            model: str, 
            output_model_name_prefix: str, 
            task: str, 
            training_data: str, 
            validation_data: Optional[str] = ..., 
            **kwargs
        ) -> CustomModelFineTuningJob: ...


    class azure.ai.ml.finetuning.FineTuningTaskType:
        CHAT_COMPLETION = ChatCompletion
        IMAGE_CLASSIFICATION = ImageClassification
        IMAGE_INSTANCE_SEGMENTATION = ImageInstanceSegmentation
        IMAGE_OBJECT_DETECTION = ImageObjectDetection
        QUESTION_ANSWERING = QuestionAnswering
        TEXT_CLASSIFICATION = TextClassification
        TEXT_COMPLETION = TextCompletion
        TEXT_SUMMARIZATION = TextSummarization
        TEXT_TRANSLATION = TextTranslation
        TOKEN_CLASSIFICATION = TokenClassification
        VIDEO_MULTI_OBJECT_TRACKING = VideoMultiObjectTracking


namespace azure.ai.ml.identity

    class azure.ai.ml.identity.AzureMLOnBehalfOfCredential: implements ContextManager 

        def __init__(self, **kwargs: Any): ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                **kwargs: Any
            ) -> AccessToken: ...


    class azure.ai.ml.identity.CredentialUnavailableError(ClientAuthenticationError):


namespace azure.ai.ml.model_customization

    @experimental
    def azure.ai.ml.model_customization.distillation(
            *, 
            data_generation_task_type: str, 
            data_generation_type: str, 
            experiment_name: str, 
            hyperparameters: Optional[Dict] = ..., 
            prompt_settings: Optional[PromptSettings] = ..., 
            resources: Optional[ResourceConfiguration] = ..., 
            student_model: Union[Input, str], 
            teacher_model_endpoint_connection: WorkspaceConnection, 
            teacher_model_settings: Optional[TeacherModelSettings] = ..., 
            training_data: Optional[Union[Input, str]] = ..., 
            validation_data: Optional[Union[Input, str]] = ..., 
            **kwargs: Any
        ) -> DistillationJob: ...


    @experimental
    class azure.ai.ml.model_customization.EndpointRequestSettings:
        property min_endpoint_success_ratio: Optional[float]
        property request_batch_size: Optional[int]

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                min_endpoint_success_ratio: Optional[float] = ..., 
                request_batch_size: Optional[int] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...

        def items(self): ...


    @experimental
    class azure.ai.ml.model_customization.PromptSettings:
        property enable_chain_of_density: bool
        property enable_chain_of_thought: bool
        property max_len_summary: Optional[int]

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                enable_chain_of_density: bool = False, 
                enable_chain_of_thought: bool = False, 
                max_len_summary: Optional[int] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...

        def items(self): ...


    @experimental
    class azure.ai.ml.model_customization.TeacherModelSettings:
        property endpoint_request_settings: Optional[EndpointRequestSettings]
        property inference_parameters: Optional[Dict]

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint_request_settings: Optional[EndpointRequestSettings] = ..., 
                inference_parameters: Optional[Dict] = ...
            ): ...

        def __ne__(self, other: object) -> bool: ...

        def items(self): ...


namespace azure.ai.ml.operations

    class azure.ai.ml.operations.AzureOpenAIDeploymentOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client: ServiceClient2020404Preview, 
                connections_operations: WorkspaceConnectionsOperations
            ): ...

        def list(
                self, 
                connection_name: str, 
                **kwargs
            ) -> Iterable[AzureOpenAIDeployment]: ...


    class azure.ai.ml.operations.BatchDeploymentOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client_01_2024_preview: ServiceClient012024Preview, 
                all_operations: OperationsContainer, 
                credentials: Optional[TokenCredential] = None, 
                **kwargs: Any
            ): ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'BatchDeployment.BeginCreateOrUpdate', ActivityType.PUBLICAPI)
        def begin_create_or_update(
                self, 
                deployment: DeploymentType, 
                *, 
                skip_script_validation: bool = False, 
                **kwargs: Any
            ) -> LROPoller[DeploymentType]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'BatchDeployment.BeginDelete', ActivityType.PUBLICAPI)
        def begin_delete(
                self, 
                name: str, 
                endpoint_name: str
            ) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'BatchDeployment.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                endpoint_name: str
            ) -> BatchDeployment: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'BatchDeployment.List', ActivityType.PUBLICAPI)
        def list(self, endpoint_name: str) -> ItemPaged[BatchDeployment]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'BatchDeployment.ListJobs', ActivityType.PUBLICAPI)
        def list_jobs(
                self, 
                endpoint_name: str, 
                *, 
                name: Optional[str] = ...
            ) -> ItemPaged[BatchJob]: ...


    class azure.ai.ml.operations.BatchEndpointOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client_10_2023: ServiceClient102023, 
                all_operations: OperationsContainer, 
                credentials: Optional[TokenCredential] = None, 
                **kwargs: Any
            ): ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'BatchEndpoint.BeginCreateOrUpdate', ActivityType.PUBLICAPI)
        def begin_create_or_update(self, endpoint: BatchEndpoint) -> LROPoller[BatchEndpoint]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'BatchEndpoint.BeginDelete', ActivityType.PUBLICAPI)
        def begin_delete(self, name: str) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'BatchEndpoint.Get', ActivityType.PUBLICAPI)
        def get(self, name: str) -> BatchEndpoint: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'BatchEndpoint.Invoke', ActivityType.PUBLICAPI)
        def invoke(
                self, 
                endpoint_name: str, 
                *, 
                deployment_name: Optional[str] = ..., 
                inputs: Optional[Dict[str, Input]] = ..., 
                **kwargs: Any
            ) -> BatchJob: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'BatchEndpoint.List', ActivityType.PUBLICAPI)
        def list(self) -> ItemPaged[BatchEndpoint]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'BatchEndpoint.ListJobs', ActivityType.PUBLICAPI)
        def list_jobs(self, endpoint_name: str) -> ItemPaged[BatchJob]: ...


    class azure.ai.ml.operations.CapabilityHostsOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client_01_2025: ServiceClient012025Preview, 
                all_operations: OperationsContainer, 
                credentials: TokenCredential, 
                **kwargs: Any
            ): ...

        @experimental
        @monitor_with_activity(ops_logger, 'CapabilityHost.BeginCreateOrUpdate', ActivityType.PUBLICAPI)
        @distributed_trace
        def begin_create_or_update(
                self, 
                capability_host: CapabilityHost, 
                **kwargs: Any
            ) -> LROPoller[CapabilityHost]: ...

        @experimental
        @distributed_trace
        @monitor_with_activity(ops_logger, 'CapabilityHost.Delete', ActivityType.PUBLICAPI)
        def begin_delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @experimental
        @monitor_with_activity(ops_logger, 'CapabilityHost.Get', ActivityType.PUBLICAPI)
        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> CapabilityHost: ...


    class azure.ai.ml.operations.ComponentOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client: Union[ServiceClient012024, ServiceClient102021Dataplane], 
                all_operations: OperationsContainer, 
                preflight_operation: Optional[DeploymentsOperations] = None, 
                **kwargs: Dict
            ) -> None: ...

        @monitor_with_telemetry_mixin(ops_logger, 'Component.Archive', ActivityType.PUBLICAPI)
        def archive(
                self, 
                name: str, 
                version: Optional[str] = None, 
                label: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @monitor_with_telemetry_mixin(logger, 'Component.CreateOrUpdate', ActivityType.PUBLICAPI, extra_keys=['is_anonymous'])
        def create_or_update(
                self, 
                component: Component, 
                version: Optional[str] = None, 
                *, 
                skip_validation: bool = False, 
                **kwargs: Any
            ) -> Component: ...

        @experimental
        @monitor_with_telemetry_mixin(ops_logger, 'Component.Download', ActivityType.PUBLICAPI)
        def download(
                self, 
                name: str, 
                download_path: Union[PathLike, str] = ".", 
                *, 
                version: Optional[str] = ...
            ) -> None: ...

        @monitor_with_telemetry_mixin(ops_logger, 'Component.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                version: Optional[str] = None, 
                label: Optional[str] = None
            ) -> Component: ...

        @monitor_with_activity(ops_logger, 'Component.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                name: Union[str, None] = None, 
                *, 
                list_view_type: ListViewType = ListViewType.ACTIVE_ONLY
            ) -> Iterable[Component]: ...

        @experimental
        def prepare_for_sign(self, component: Component) -> None: ...

        @monitor_with_telemetry_mixin(ops_logger, 'Component.Restore', ActivityType.PUBLICAPI)
        def restore(
                self, 
                name: str, 
                version: Optional[str] = None, 
                label: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @experimental
        @monitor_with_telemetry_mixin(ops_logger, 'Component.Validate', ActivityType.PUBLICAPI)
        def validate(
                self, 
                component: Union[Component, FunctionType], 
                raise_on_failure: bool = False, 
                **kwargs: Any
            ) -> ValidationResult: ...


    class azure.ai.ml.operations.ComputeOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client: ServiceClient022023Preview, 
                service_client_2024: ServiceClient042024Preview, 
                **kwargs: Dict
            ) -> None: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.Attach', ActivityType.PUBLICAPI)
        def begin_attach(
                self, 
                compute: Compute, 
                **kwargs: Any
            ) -> LROPoller[Compute]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.BeginCreateOrUpdate', ActivityType.PUBLICAPI)
        def begin_create_or_update(self, compute: Compute) -> LROPoller[Compute]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.BeginDelete', ActivityType.PUBLICAPI)
        def begin_delete(
                self, 
                name: str, 
                *, 
                action: str = "Delete"
            ) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.BeginRestart', ActivityType.PUBLICAPI)
        def begin_restart(self, name: str) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.BeginStart', ActivityType.PUBLICAPI)
        def begin_start(self, name: str) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.BeginStop', ActivityType.PUBLICAPI)
        def begin_stop(self, name: str) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.BeginUpdate', ActivityType.PUBLICAPI)
        def begin_update(self, compute: Compute) -> LROPoller[Compute]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.enablesso', ActivityType.PUBLICAPI)
        @experimental
        def enable_sso(
                self, 
                *, 
                enable_sso: bool = True, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.Get', ActivityType.PUBLICAPI)
        def get(self, name: str) -> Compute: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                *, 
                compute_type: Optional[str] = ...
            ) -> Iterable[Compute]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.ListNodes', ActivityType.PUBLICAPI)
        def list_nodes(self, name: str) -> Iterable[AmlComputeNodeInfo]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.ListSizes', ActivityType.PUBLICAPI)
        def list_sizes(
                self, 
                *, 
                compute_type: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> Iterable[VmSize]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Compute.ListUsage', ActivityType.PUBLICAPI)
        def list_usage(
                self, 
                *, 
                location: Optional[str] = ...
            ) -> Iterable[Usage]: ...


    class azure.ai.ml.operations.DataOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client: Union[ServiceClient042023_preview, ServiceClient102021Dataplane], 
                service_client_012024_preview: ServiceClient012024_preview, 
                datastore_operations: DatastoreOperations, 
                **kwargs: Any
            ): ...

        @monitor_with_activity(ops_logger, 'Data.Archive', ActivityType.PUBLICAPI)
        def archive(
                self, 
                name: str, 
                version: Optional[str] = None, 
                label: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @monitor_with_activity(ops_logger, 'Data.CreateOrUpdate', ActivityType.PUBLICAPI)
        def create_or_update(self, data: Data) -> Data: ...

        @monitor_with_activity(ops_logger, 'Data.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                version: Optional[str] = None, 
                label: Optional[str] = None
            ) -> Data: ...

        @monitor_with_activity(ops_logger, 'Data.ImportData', ActivityType.PUBLICAPI)
        @experimental
        def import_data(
                self, 
                data_import: DataImport, 
                **kwargs: Any
            ) -> PipelineJob: ...

        @monitor_with_activity(ops_logger, 'Data.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                name: Optional[str] = None, 
                *, 
                list_view_type: ListViewType = ListViewType.ACTIVE_ONLY
            ) -> ItemPaged[Data]: ...

        @monitor_with_activity(ops_logger, 'Data.ListMaterializationStatus', ActivityType.PUBLICAPI)
        def list_materialization_status(
                self, 
                name: str, 
                *, 
                list_view_type: ListViewType = ListViewType.ACTIVE_ONLY, 
                **kwargs: Any
            ) -> Iterable[PipelineJob]: ...

        @monitor_with_activity(ops_logger, 'data.Mount', ActivityType.PUBLICAPI)
        @experimental
        def mount(
                self, 
                path: str, 
                *, 
                debug: bool = False, 
                mode: str = "ro_mount", 
                mount_point: Optional[str] = ..., 
                persistent: bool = False, 
                **kwargs
            ) -> None: ...

        @monitor_with_activity(ops_logger, 'Data.Restore', ActivityType.PUBLICAPI)
        def restore(
                self, 
                name: str, 
                version: Optional[str] = None, 
                label: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @monitor_with_activity(ops_logger, 'data.Share', ActivityType.PUBLICAPI)
        @experimental
        def share(
                self, 
                name: str, 
                version: str, 
                *, 
                registry_name: str, 
                share_with_name: str, 
                share_with_version: str, 
                **kwargs: Any
            ) -> Data: ...


    class azure.ai.ml.operations.DatastoreOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                serviceclient_2024_01_01_preview: ServiceClient012024Preview, 
                serviceclient_2024_07_01_preview: ServiceClient072024Preview, 
                **kwargs: Dict
            ): ...

        @monitor_with_activity(ops_logger, 'Datastore.CreateOrUpdate', ActivityType.PUBLICAPI)
        def create_or_update(self, datastore: Datastore) -> Datastore: ...

        @monitor_with_activity(ops_logger, 'Datastore.Delete', ActivityType.PUBLICAPI)
        def delete(self, name: str) -> None: ...

        @monitor_with_activity(ops_logger, 'Datastore.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                *, 
                include_secrets: bool = False
            ) -> Datastore: ...

        @monitor_with_activity(ops_logger, 'Datastore.GetDefault', ActivityType.PUBLICAPI)
        def get_default(
                self, 
                *, 
                include_secrets: bool = False
            ) -> Datastore: ...

        @monitor_with_activity(ops_logger, 'Datastore.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                *, 
                include_secrets: bool = False
            ) -> Iterable[Datastore]: ...

        @monitor_with_activity(ops_logger, 'Datastore.Mount', ActivityType.PUBLICAPI)
        @experimental
        def mount(
                self, 
                path: str, 
                *, 
                debug: bool = False, 
                mode: str = "ro_mount", 
                mount_point: Optional[str] = ..., 
                persistent: bool = False, 
                **kwargs
            ) -> None: ...


    class azure.ai.ml.operations.DeploymentTemplateOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client_04_2024_dataplanepreview, 
                **kwargs: Dict[str, Any]
            ): ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'DeploymentTemplate.Archive', ActivityType.PUBLICAPI)
        @experimental
        def archive(
                self, 
                name: str, 
                version: Optional[str] = None, 
                **kwargs: Any
            ) -> DeploymentTemplate: ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'DeploymentTemplate.CreateOrUpdate', ActivityType.PUBLICAPI)
        @experimental
        def create_or_update(
                self, 
                deployment_template: DeploymentTemplate, 
                **kwargs: Any
            ) -> DeploymentTemplate: ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'DeploymentTemplate.Delete', ActivityType.PUBLICAPI)
        @experimental
        def delete(
                self, 
                name: str, 
                version: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'DeploymentTemplate.Get', ActivityType.PUBLICAPI)
        @experimental
        def get(
                self, 
                name: str, 
                version: Optional[str] = None, 
                **kwargs: Any
            ) -> DeploymentTemplate: ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'DeploymentTemplate.List', ActivityType.PUBLICAPI)
        @experimental
        def list(
                self, 
                *, 
                count: Optional[int] = ..., 
                list_view_type: str = "ActiveOnly", 
                name: Optional[str] = ..., 
                stage: Optional[str] = ..., 
                tags: Optional[str] = ..., 
                **kwargs: Any
            ) -> Iterable[DeploymentTemplate]: ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'DeploymentTemplate.Restore', ActivityType.PUBLICAPI)
        @experimental
        def restore(
                self, 
                name: str, 
                version: Optional[str] = None, 
                **kwargs: Any
            ) -> DeploymentTemplate: ...


    class azure.ai.ml.operations.EnvironmentOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client: Union[ServiceClient042023Preview, ServiceClient102021Dataplane], 
                all_operations: OperationsContainer, 
                **kwargs: Any
            ): ...

        @monitor_with_activity(ops_logger, 'Environment.Delete', ActivityType.PUBLICAPI)
        def archive(
                self, 
                name: str, 
                version: Optional[str] = None, 
                label: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @monitor_with_activity(ops_logger, 'Environment.CreateOrUpdate', ActivityType.PUBLICAPI)
        def create_or_update(self, environment: Environment) -> Environment: ...

        @monitor_with_activity(ops_logger, 'Environment.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                version: Optional[str] = None, 
                label: Optional[str] = None
            ) -> Environment: ...

        @monitor_with_activity(ops_logger, 'Environment.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                name: Optional[str] = None, 
                *, 
                list_view_type: ListViewType = ListViewType.ACTIVE_ONLY
            ) -> Iterable[Environment]: ...

        @monitor_with_activity(ops_logger, 'Environment.Restore', ActivityType.PUBLICAPI)
        def restore(
                self, 
                name: str, 
                version: Optional[str] = None, 
                label: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @monitor_with_activity(ops_logger, 'Environment.Share', ActivityType.PUBLICAPI)
        @experimental
        def share(
                self, 
                name: str, 
                version: str, 
                *, 
                registry_name: str, 
                share_with_name: str, 
                share_with_version: str
            ) -> Environment: ...


    class azure.ai.ml.operations.EvaluatorOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client: Union[ServiceClient082023Preview, ServiceClient102021Dataplane], 
                datastore_operations: DatastoreOperations, 
                all_operations: Optional[OperationsContainer] = None, 
                **kwargs: dict
            ): ...

        @monitor_with_activity(ops_logger, 'Evaluator.CreateOrUpdate', ActivityType.PUBLICAPI)
        def create_or_update(
                self, 
                model: Union[Model, WorkspaceAssetReference], 
                **kwargs: Any
            ) -> Model: ...

        @monitor_with_activity(ops_logger, 'Evaluator.Download', ActivityType.PUBLICAPI)
        def download(
                self, 
                name: str, 
                version: str, 
                download_path: Union[PathLike, str] = ".", 
                **kwargs: Any
            ) -> None: ...

        @monitor_with_activity(ops_logger, 'Evaluator.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                *, 
                label: Optional[str] = ..., 
                version: Optional[str] = ..., 
                **kwargs
            ) -> Model: ...

        @monitor_with_activity(ops_logger, 'Evaluator.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                name: str, 
                stage: Optional[str] = None, 
                *, 
                list_view_type: ListViewType = ListViewType.ACTIVE_ONLY, 
                **kwargs: Any
            ) -> Iterable[Model]: ...


    class azure.ai.ml.operations.FeatureSetOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client: ServiceClient102023, 
                service_client_for_jobs: ServiceClient082023Preview, 
                datastore_operations: DatastoreOperations, 
                **kwargs: Dict
            ): ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureSet.Archive', ActivityType.PUBLICAPI)
        def archive(
                self, 
                name: str, 
                version: str, 
                **kwargs: Dict
            ) -> None: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureSet.BeginBackFill', ActivityType.PUBLICAPI)
        def begin_backfill(
                self, 
                *, 
                compute_resource: Optional[MaterializationComputeResource] = ..., 
                data_status: Optional[List[Union[str, DataAvailabilityStatus]]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                feature_window_end_time: Optional[datetime] = ..., 
                feature_window_start_time: Optional[datetime] = ..., 
                job_id: Optional[str] = ..., 
                name: str, 
                spark_configuration: Optional[Dict[str, str]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                version: str, 
                **kwargs: Dict
            ) -> LROPoller[FeatureSetBackfillMetadata]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureSet.BeginCreateOrUpdate', ActivityType.PUBLICAPI)
        def begin_create_or_update(
                self, 
                featureset: FeatureSet, 
                **kwargs: Dict
            ) -> LROPoller[FeatureSet]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureSet.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Dict
            ) -> FeatureSet: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureSet.GetFeature', ActivityType.PUBLICAPI)
        def get_feature(
                self, 
                feature_set_name: str, 
                version: str, 
                *, 
                feature_name: str, 
                **kwargs: Dict
            ) -> Optional[Feature]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureSet.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                name: Optional[str] = None, 
                *, 
                list_view_type: ListViewType = ListViewType.ACTIVE_ONLY, 
                **kwargs: Dict
            ) -> ItemPaged[FeatureSet]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureSet.ListFeatures', ActivityType.PUBLICAPI)
        def list_features(
                self, 
                feature_set_name: str, 
                version: str, 
                *, 
                description: Optional[str] = ..., 
                feature_name: Optional[str] = ..., 
                tags: Optional[str] = ..., 
                **kwargs: Dict
            ) -> ItemPaged[Feature]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureSet.ListMaterializationOperation', ActivityType.PUBLICAPI)
        def list_materialization_operations(
                self, 
                name: str, 
                version: str, 
                *, 
                feature_window_end_time: Optional[Union[str, datetime]] = ..., 
                feature_window_start_time: Optional[Union[str, datetime]] = ..., 
                filters: Optional[str] = ..., 
                **kwargs: Dict
            ) -> ItemPaged[FeatureSetMaterializationMetadata]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureSet.Restore', ActivityType.PUBLICAPI)
        def restore(
                self, 
                name: str, 
                version: str, 
                **kwargs: Dict
            ) -> None: ...


    class azure.ai.ml.operations.FeatureStoreEntityOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client: ServiceClient102023, 
                **kwargs: Dict
            ): ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureStoreEntity.Archive', ActivityType.PUBLICAPI)
        def archive(
                self, 
                name: str, 
                version: str, 
                **kwargs: Dict
            ) -> None: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureStoreEntity.BeginCreateOrUpdate', ActivityType.PUBLICAPI)
        def begin_create_or_update(
                self, 
                feature_store_entity: FeatureStoreEntity, 
                **kwargs: Dict
            ) -> LROPoller[FeatureStoreEntity]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureStoreEntity.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Dict
            ) -> FeatureStoreEntity: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureStoreEntity.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                name: Optional[str] = None, 
                *, 
                list_view_type: ListViewType = ListViewType.ACTIVE_ONLY, 
                **kwargs: Dict
            ) -> ItemPaged[FeatureStoreEntity]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureStoreEntity.Restore', ActivityType.PUBLICAPI)
        def restore(
                self, 
                name: str, 
                version: str, 
                **kwargs: Dict
            ) -> None: ...


    class azure.ai.ml.operations.FeatureStoreOperations(WorkspaceOperationsBase):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                service_client: ServiceClient102024Preview, 
                all_operations: OperationsContainer, 
                credentials: Optional[TokenCredential] = None, 
                **kwargs: Dict
            ): ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureStore.BeginCreate', ActivityType.PUBLICAPI)
        def begin_create(
                self, 
                feature_store: FeatureStore, 
                *, 
                grant_materialization_permissions: bool = True, 
                update_dependent_resources: bool = False, 
                **kwargs: Dict
            ) -> LROPoller[FeatureStore]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureStore.BeginDelete', ActivityType.PUBLICAPI)
        def begin_delete(
                self, 
                name: str, 
                *, 
                delete_dependent_resources: bool = False, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureStore.BeginProvisionNetwork', ActivityType.PUBLICAPI)
        def begin_provision_network(
                self, 
                *, 
                feature_store_name: Optional[str] = ..., 
                include_spark: bool = False, 
                **kwargs: Any
            ) -> LROPoller[ManagedNetworkProvisionStatus]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureStore.BeginUpdate', ActivityType.PUBLICAPI)
        def begin_update(
                self, 
                feature_store: FeatureStore, 
                *, 
                application_insights: Optional[str] = ..., 
                container_registry: Optional[str] = ..., 
                grant_materialization_permissions: bool = True, 
                update_dependent_resources: bool = False, 
                **kwargs: Any
            ) -> LROPoller[FeatureStore]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureStore.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> FeatureStore: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'FeatureStore.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                *, 
                scope: str = Scope.RESOURCE_GROUP, 
                **kwargs: Dict
            ) -> Iterable[FeatureStore]: ...


    class azure.ai.ml.operations.IndexOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                *, 
                all_operations: OperationsContainer, 
                credential: TokenCredential, 
                datastore_operations: DatastoreOperations, 
                operation_config: OperationConfig, 
                operation_scope: OperationScope, 
                **kwargs: Any
            ): ...

        def build_index(
                self, 
                *, 
                data_source_citation_url: Optional[str] = ..., 
                document_path_replacement_regex: Optional[str] = ..., 
                embeddings_model_config: ModelConfiguration, 
                index_config: Optional[AzureAISearchConfig] = ..., 
                input_glob: Optional[str] = ..., 
                input_source: Union[IndexDataSource, str], 
                input_source_credential: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]] = ..., 
                name: str, 
                token_overlap_across_chunks: Optional[int] = ..., 
                tokens_per_chunk: Optional[int] = ...
            ) -> Union[Index, Job]: ...

        @monitor_with_activity(ops_logger, 'Index.CreateOrUpdate', ActivityType.PUBLICAPI)
        def create_or_update(
                self, 
                index: Index, 
                **kwargs
            ) -> Index: ...

        @monitor_with_activity(ops_logger, 'Index.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                *, 
                label: Optional[str] = ..., 
                version: Optional[str] = ..., 
                **kwargs
            ) -> Index: ...

        @monitor_with_activity(ops_logger, 'Index.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                name: Optional[str] = None, 
                *, 
                list_view_type: ListViewType = ListViewType.ACTIVE_ONLY, 
                **kwargs
            ) -> Iterable[Index]: ...


    class azure.ai.ml.operations.JobOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client_02_2023_preview: ServiceClient022023Preview, 
                all_operations: OperationsContainer, 
                credential: TokenCredential, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'Job.Archive', ActivityType.PUBLICAPI)
        def archive(self, name: str) -> None: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Job.Cancel', ActivityType.PUBLICAPI)
        def begin_cancel(
                self, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'Job.CreateOrUpdate', ActivityType.PUBLICAPI)
        def create_or_update(
                self, 
                job: Job, 
                *, 
                compute: Optional[str] = ..., 
                description: Optional[str] = ..., 
                experiment_name: Optional[str] = ..., 
                skip_validation: bool = False, 
                tags: Optional[dict] = ..., 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Job.Download', ActivityType.PUBLICAPI)
        def download(
                self, 
                name: str, 
                *, 
                all: bool = False, 
                download_path: Union[PathLike, str] = ".", 
                output_name: Optional[str] = ...
            ) -> None: ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'Job.Get', ActivityType.PUBLICAPI)
        def get(self, name: str) -> Job: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Job.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                *, 
                list_view_type: ListViewType = ListViewType.ACTIVE_ONLY, 
                parent_job_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> Iterable[Job]: ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'Job.Restore', ActivityType.PUBLICAPI)
        def restore(self, name: str) -> None: ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'Job.ShowServices', ActivityType.PUBLICAPI)
        def show_services(
                self, 
                name: str, 
                node_index: int = 0
            ) -> Optional[Dict[str, ServiceInstance]]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Job.Stream', ActivityType.PUBLICAPI)
        def stream(self, name: str) -> None: ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'Job.Validate', ActivityType.PUBLICAPI)
        def validate(
                self, 
                job: Job, 
                *, 
                raise_on_failure: bool = False, 
                **kwargs: Any
            ) -> ValidationResult: ...


    class azure.ai.ml.operations.MarketplaceSubscriptionOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client: ServiceClient202401Preview
            ): ...

        @experimental
        @monitor_with_activity(ops_logger, 'MarketplaceSubscription.BeginCreateOrUpdate', ActivityType.PUBLICAPI)
        def begin_create_or_update(
                self, 
                marketplace_subscription: MarketplaceSubscription, 
                **kwargs
            ) -> LROPoller[MarketplaceSubscription]: ...

        @experimental
        @monitor_with_activity(ops_logger, 'MarketplaceSubscription.BeginDelete', ActivityType.PUBLICAPI)
        def begin_delete(
                self, 
                name: str, 
                **kwargs
            ) -> LROPoller[None]: ...

        @experimental
        @monitor_with_activity(ops_logger, 'MarketplaceSubscription.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                **kwargs
            ) -> MarketplaceSubscription: ...

        @experimental
        @monitor_with_activity(ops_logger, 'MarketplaceSubscription.List', ActivityType.PUBLICAPI)
        def list(self, **kwargs) -> Iterable[MarketplaceSubscription]: ...


    class azure.ai.ml.operations.ModelOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client: Union[ServiceClient082023Preview, ServiceClient102021Dataplane], 
                datastore_operations: DatastoreOperations, 
                service_client_model_dataplane: ServiceClientModelDataPlane = None, 
                all_operations: Optional[OperationsContainer] = None, 
                **kwargs
            ): ...

        @monitor_with_activity(ops_logger, 'Model.Archive', ActivityType.PUBLICAPI)
        def archive(
                self, 
                name: str, 
                version: Optional[str] = None, 
                label: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @monitor_with_activity(ops_logger, 'Model.CreateOrUpdate', ActivityType.PUBLICAPI)
        def create_or_update(self, model: Union[Model, WorkspaceAssetReference]) -> Model: ...

        @monitor_with_activity(ops_logger, 'Model.Download', ActivityType.PUBLICAPI)
        def download(
                self, 
                name: str, 
                version: str, 
                download_path: Union[PathLike, str] = "."
            ) -> None: ...

        @monitor_with_activity(ops_logger, 'Model.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                version: Optional[str] = None, 
                label: Optional[str] = None
            ) -> Model: ...

        @monitor_with_activity(ops_logger, 'Model.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                name: Optional[str] = None, 
                stage: Optional[str] = None, 
                *, 
                list_view_type: ListViewType = ListViewType.ACTIVE_ONLY
            ) -> Iterable[Model]: ...

        @experimental
        @monitor_with_activity(ops_logger, 'Model.Package', ActivityType.PUBLICAPI)
        def package(
                self, 
                name: str, 
                version: str, 
                package_request: ModelPackage, 
                **kwargs: Any
            ) -> Environment: ...

        @monitor_with_activity(ops_logger, 'Model.Restore', ActivityType.PUBLICAPI)
        def restore(
                self, 
                name: str, 
                version: Optional[str] = None, 
                label: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @monitor_with_activity(ops_logger, 'Model.Share', ActivityType.PUBLICAPI)
        @experimental
        def share(
                self, 
                name: str, 
                version: str, 
                *, 
                registry_name: str, 
                share_with_name: str, 
                share_with_version: str
            ) -> Model: ...


    class azure.ai.ml.operations.OnlineDeploymentOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client_04_2023_preview: ServiceClient042023Preview, 
                all_operations: OperationsContainer, 
                local_deployment_helper: _LocalDeploymentHelper, 
                credentials: Optional[TokenCredential] = None, 
                **kwargs: Dict
            ): ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'OnlineDeployment.BeginCreateOrUpdate', ActivityType.PUBLICAPI)
        def begin_create_or_update(
                self, 
                deployment: OnlineDeployment, 
                *, 
                local: bool = False, 
                local_enable_gpu: bool = False, 
                skip_script_validation: bool = False, 
                vscode_debug: bool = False, 
                **kwargs: Any
            ) -> LROPoller[OnlineDeployment]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'OnlineDeployment.Delete', ActivityType.PUBLICAPI)
        def begin_delete(
                self, 
                name: str, 
                endpoint_name: str, 
                *, 
                local: Optional[bool] = False
            ) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'OnlineDeployment.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                endpoint_name: str, 
                *, 
                local: Optional[bool] = False
            ) -> OnlineDeployment: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'OnlineDeployment.GetLogs', ActivityType.PUBLICAPI)
        def get_logs(
                self, 
                name: str, 
                endpoint_name: str, 
                lines: int, 
                *, 
                container_type: Optional[str] = ..., 
                local: bool = False
            ) -> str: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'OnlineDeployment.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                endpoint_name: str, 
                *, 
                local: bool = False
            ) -> ItemPaged[OnlineDeployment]: ...


    class azure.ai.ml.operations.OnlineEndpointOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client_02_2022_preview: ServiceClient022022Preview, 
                all_operations: OperationsContainer, 
                local_endpoint_helper: _LocalEndpointHelper, 
                credentials: Optional[TokenCredential] = None, 
                **kwargs: Dict
            ): ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'OnlineEndpoint.BeginDeleteOrUpdate', ActivityType.PUBLICAPI)
        def begin_create_or_update(
                self, 
                endpoint: OnlineEndpoint, 
                *, 
                local: bool = False
            ) -> LROPoller[OnlineEndpoint]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'OnlineEndpoint.BeginDelete', ActivityType.PUBLICAPI)
        def begin_delete(
                self, 
                name: Optional[str] = None, 
                *, 
                local: bool = False
            ) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'OnlineEndpoint.BeginGenerateKeys', ActivityType.PUBLICAPI)
        def begin_regenerate_keys(
                self, 
                name: str, 
                *, 
                key_type: str = EndpointKeyType.PRIMARY_KEY_TYPE
            ) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'OnlineEndpoint.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                *, 
                local: bool = False
            ) -> OnlineEndpoint: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'OnlineEndpoint.ListKeys', ActivityType.PUBLICAPI)
        def get_keys(self, name: str) -> Union[EndpointAuthKeys, EndpointAuthToken, EndpointAadToken]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'OnlineEndpoint.Invoke', ActivityType.PUBLICAPI)
        def invoke(
                self, 
                endpoint_name: str, 
                *, 
                deployment_name: Optional[str] = ..., 
                input_data: Optional[Union[str, Data]] = ..., 
                local: bool = False, 
                params_override: Any = ..., 
                request_file: Optional[str] = ..., 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'OnlineEndpoint.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                *, 
                local: bool = False
            ) -> ItemPaged[OnlineEndpoint]: ...


    class azure.ai.ml.operations.RegistryOperations:

        def __init__(
                self, 
                operation_scope: OperationScope, 
                service_client: ServiceClient102022, 
                all_operations: OperationsContainer, 
                credentials: Optional[TokenCredential] = None, 
                **kwargs: Dict
            ): ...

        @monitor_with_activity(ops_logger, 'Registry.BeginCreate', ActivityType.PUBLICAPI)
        def begin_create(
                self, 
                registry: Registry, 
                **kwargs: Dict
            ) -> LROPoller[Registry]: ...

        @monitor_with_activity(ops_logger, 'Registry.BeginDelete', ActivityType.PUBLICAPI)
        def begin_delete(
                self, 
                *, 
                name: str, 
                **kwargs: Dict
            ) -> LROPoller[None]: ...

        @monitor_with_activity(ops_logger, 'Registry.Get', ActivityType.PUBLICAPI)
        def get(self, name: Optional[str] = None) -> Registry: ...

        @monitor_with_activity(ops_logger, 'Registry.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                *, 
                scope: str = Scope.RESOURCE_GROUP
            ) -> Iterable[Registry]: ...


    class azure.ai.ml.operations.ScheduleOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client_06_2023_preview: ServiceClient062023Preview, 
                service_client_01_2024_preview: ServiceClient012024Preview, 
                all_operations: OperationsContainer, 
                credential: TokenCredential, 
                **kwargs: Any
            ): ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'Schedule.CreateOrUpdate', ActivityType.PUBLICAPI)
        def begin_create_or_update(
                self, 
                schedule: Schedule, 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Schedule.Delete', ActivityType.PUBLICAPI)
        def begin_delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Schedule.Disable', ActivityType.PUBLICAPI)
        def begin_disable(
                self, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Schedule.Enable', ActivityType.PUBLICAPI)
        def begin_enable(
                self, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @distributed_trace
        @monitor_with_telemetry_mixin(ops_logger, 'Schedule.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Schedule.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                *, 
                list_view_type: ScheduleListViewType = ScheduleListViewType.ENABLED_ONLY, 
                **kwargs: Any
            ) -> Iterable[Schedule]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Schedule.Trigger', ActivityType.PUBLICAPI)
        def trigger(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ScheduleTriggerResult: ...


    class azure.ai.ml.operations.ServerlessEndpointOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client: ServiceClient202401Preview, 
                all_operations: OperationsContainer
            ): ...

        @experimental
        @monitor_with_activity(ops_logger, 'ServerlessEndpoint.BeginCreateOrUpdate', ActivityType.PUBLICAPI)
        def begin_create_or_update(
                self, 
                endpoint: ServerlessEndpoint, 
                **kwargs
            ) -> LROPoller[ServerlessEndpoint]: ...

        @experimental
        @monitor_with_activity(ops_logger, 'ServerlessEndpoint.BeginDelete', ActivityType.PUBLICAPI)
        def begin_delete(
                self, 
                name: str, 
                **kwargs
            ) -> LROPoller[None]: ...

        @experimental
        @monitor_with_activity(ops_logger, 'ServerlessEndpoint.BeginRegenerateKeys', ActivityType.PUBLICAPI)
        def begin_regenerate_keys(
                self, 
                name: str, 
                *, 
                key_type: str = EndpointKeyType.PRIMARY_KEY_TYPE, 
                **kwargs
            ) -> LROPoller[EndpointAuthKeys]: ...

        @experimental
        @monitor_with_activity(ops_logger, 'ServerlessEndpoint.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                **kwargs
            ) -> ServerlessEndpoint: ...

        @experimental
        @monitor_with_activity(ops_logger, 'ServerlessEndpoint.GetKeys', ActivityType.PUBLICAPI)
        def get_keys(
                self, 
                name: str, 
                **kwargs
            ) -> EndpointAuthKeys: ...

        @experimental
        @monitor_with_activity(ops_logger, 'ServerlessEndpoint.list', ActivityType.PUBLICAPI)
        def list(self, **kwargs) -> Iterable[ServerlessEndpoint]: ...


    class azure.ai.ml.operations.WorkspaceConnectionsOperations(_ScopeDependentOperations):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                operation_config: OperationConfig, 
                service_client: ServiceClient082023Preview, 
                all_operations: OperationsContainer, 
                credentials: Optional[TokenCredential] = None, 
                **kwargs: Dict
            ): ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'WorkspaceConnections.CreateOrUpdate', ActivityType.PUBLICAPI)
        def create_or_update(
                self, 
                workspace_connection: WorkspaceConnection, 
                *, 
                populate_secrets: bool = False, 
                **kwargs: Any
            ) -> WorkspaceConnection: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'WorkspaceConnections.Delete', ActivityType.PUBLICAPI)
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'WorkspaceConnections.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                name: str, 
                *, 
                populate_secrets: bool = False, 
                **kwargs: Dict
            ) -> WorkspaceConnection: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'WorkspaceConnections.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                connection_type: Optional[str] = None, 
                *, 
                include_data_connections: bool = False, 
                populate_secrets: bool = False, 
                **kwargs: Any
            ) -> Iterable[WorkspaceConnection]: ...


    class azure.ai.ml.operations.WorkspaceOperations(WorkspaceOperationsBase):

        def __init__(
                self, 
                operation_scope: OperationScope, 
                service_client: ServiceClient102024Preview, 
                all_operations: OperationsContainer, 
                credentials: Optional[TokenCredential] = None, 
                **kwargs: Any
            ): ...

        @monitor_with_activity(ops_logger, 'Workspace.BeginCreate', ActivityType.PUBLICAPI)
        @distributed_trace
        def begin_create(
                self, 
                workspace: Workspace, 
                update_dependent_resources: bool = False, 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @monitor_with_activity(ops_logger, 'Workspace.BeginDelete', ActivityType.PUBLICAPI)
        @distributed_trace
        def begin_delete(
                self, 
                name: str, 
                *, 
                delete_dependent_resources: bool, 
                permanently_delete: bool = False, 
                **kwargs: Dict
            ) -> LROPoller[None]: ...

        @distributed_trace
        @monitor_with_activity(ops_logger, 'Workspace.BeginDiagnose', ActivityType.PUBLICAPI)
        def begin_diagnose(
                self, 
                name: str, 
                **kwargs: Dict
            ) -> LROPoller[DiagnoseResponseResultValue]: ...

        @monitor_with_activity(ops_logger, 'Workspace.BeginProvisionNetwork', ActivityType.PUBLICAPI)
        @distributed_trace
        def begin_provision_network(
                self, 
                *, 
                include_spark: bool = False, 
                workspace_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[ManagedNetworkProvisionStatus]: ...

        @monitor_with_activity(ops_logger, 'Workspace.BeginSyncKeys', ActivityType.PUBLICAPI)
        @distributed_trace
        def begin_sync_keys(self, name: Optional[str] = None) -> LROPoller[None]: ...

        @monitor_with_activity(ops_logger, 'Workspace.BeginUpdate', ActivityType.PUBLICAPI)
        @distributed_trace
        def begin_update(
                self, 
                workspace: Workspace, 
                *, 
                update_dependent_resources: bool = False, 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @monitor_with_activity(ops_logger, 'Workspace.Get', ActivityType.PUBLICAPI)
        @distributed_trace
        def get(
                self, 
                name: Optional[str] = None, 
                **kwargs: Dict
            ) -> Optional[Workspace]: ...

        @monitor_with_activity(ops_logger, 'Workspace.Get_Keys', ActivityType.PUBLICAPI)
        @distributed_trace
        def get_keys(self, name: Optional[str] = None) -> Optional[WorkspaceKeys]: ...

        @monitor_with_activity(ops_logger, 'Workspace.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                *, 
                filtered_kinds: Optional[Union[str, List[str]]] = ..., 
                scope: str = Scope.RESOURCE_GROUP
            ) -> Iterable[Workspace]: ...


    class azure.ai.ml.operations.WorkspaceOutboundRuleOperations:

        def __init__(
                self, 
                operation_scope: OperationScope, 
                service_client: ServiceClient102024Preview, 
                all_operations: OperationsContainer, 
                credentials: TokenCredential = None, 
                **kwargs: Dict
            ): ...

        @monitor_with_activity(ops_logger, 'WorkspaceOutboundRule.BeginCreate', ActivityType.PUBLICAPI)
        def begin_create(
                self, 
                workspace_name: str, 
                rule: OutboundRule, 
                **kwargs: Any
            ) -> LROPoller[OutboundRule]: ...

        @monitor_with_activity(ops_logger, 'WorkspaceOutboundRule.Remove', ActivityType.PUBLICAPI)
        def begin_remove(
                self, 
                workspace_name: str, 
                outbound_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @monitor_with_activity(ops_logger, 'WorkspaceOutboundRule.BeginUpdate', ActivityType.PUBLICAPI)
        def begin_update(
                self, 
                workspace_name: str, 
                rule: OutboundRule, 
                **kwargs: Any
            ) -> LROPoller[OutboundRule]: ...

        @monitor_with_activity(ops_logger, 'WorkspaceOutboundRule.Get', ActivityType.PUBLICAPI)
        def get(
                self, 
                workspace_name: str, 
                outbound_rule_name: str, 
                **kwargs: Any
            ) -> OutboundRule: ...

        @monitor_with_activity(ops_logger, 'WorkspaceOutboundRule.List', ActivityType.PUBLICAPI)
        def list(
                self, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Iterable[OutboundRule]: ...


namespace azure.ai.ml.parallel

    def azure.ai.ml.parallel.parallel_run_function(
            *, 
            compute: Optional[str] = ..., 
            description: Optional[str] = ..., 
            display_name: Optional[str] = ..., 
            docker_args: Optional[str] = ..., 
            environment_variables: Optional[Dict] = ..., 
            error_threshold: Optional[int] = ..., 
            experiment_name: Optional[str] = ..., 
            identity: Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]] = ..., 
            input_data: Optional[str] = ..., 
            inputs: Optional[Dict] = ..., 
            instance_count: Optional[int] = ..., 
            instance_type: Optional[str] = ..., 
            is_deterministic: bool = True, 
            logging_level: Optional[str] = ..., 
            max_concurrency_per_instance: Optional[int] = ..., 
            mini_batch_error_threshold: Optional[int] = ..., 
            mini_batch_size: Optional[str] = ..., 
            name: Optional[str] = ..., 
            outputs: Optional[Dict] = ..., 
            partition_keys: Optional[List] = ..., 
            properties: Optional[Dict] = ..., 
            retry_settings: Optional[BatchRetrySettings] = ..., 
            shm_size: Optional[str] = ..., 
            tags: Optional[Dict] = ..., 
            task: Optional[RunFunction] = ..., 
            **kwargs: Any
        ) -> Parallel: ...


    class azure.ai.ml.parallel.ParallelJob(Job, ParameterizedParallel, JobIOMixin):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property log_files: Optional[Dict[str, str]]    # Read-only
        property outputs: Dict[str, Output]
        property resources: Optional[Union[dict, JobResourceConfiguration]]
        property retry_settings: Optional[RetrySettings]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property task: Optional[ParallelTask]
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                identity: Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration, Dict]] = ..., 
                inputs: Optional[Dict[str, Union[Input, str, bool, int, float]]] = ..., 
                outputs: Optional[Dict[str, Output]] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.parallel.RunFunction(ParallelTask): implements Collection , Mapping 

        def __delitem__(self, key: Any) -> None: ...

        def __init__(
                self, 
                *, 
                append_row_to: Optional[str] = ..., 
                code: Optional[str] = ..., 
                entry_script: Optional[str] = ..., 
                environment: Optional[Union[Environment, str]] = ..., 
                model: Optional[str] = ..., 
                program_arguments: Optional[str] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: Any, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def has_key(self, k: Any) -> bool: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


namespace azure.ai.ml.sweep

    class azure.ai.ml.sweep.BanditPolicy(EarlyTerminationPolicy):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                delay_evaluation: int = 0, 
                evaluation_interval: int = 0, 
                slack_amount: float = 0, 
                slack_factor: float = 0
            ) -> None: ...


    class azure.ai.ml.sweep.BayesianSamplingAlgorithm(SamplingAlgorithm):

        def __init__(self) -> None: ...


    class azure.ai.ml.sweep.Choice(SweepDistribution):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                values: Optional[List[Union[float, str, dict]]] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.sweep.GridSamplingAlgorithm(SamplingAlgorithm):

        def __init__(self) -> None: ...


    class azure.ai.ml.sweep.LogNormal(Normal):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                mu: Optional[float] = None, 
                sigma: Optional[float] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.sweep.LogUniform(Uniform):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                min_value: Optional[float] = None, 
                max_value: Optional[float] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.sweep.MedianStoppingPolicy(EarlyTerminationPolicy):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                delay_evaluation: int = 0, 
                evaluation_interval: int = 1
            ) -> None: ...


    class azure.ai.ml.sweep.Normal(SweepDistribution):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                mu: Optional[float] = None, 
                sigma: Optional[float] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.sweep.Objective(RestTranslatableMixin):

        def __init__(
                self, 
                goal: Optional[str], 
                primary_metric: Optional[str] = None
            ) -> None: ...


    class azure.ai.ml.sweep.QLogNormal(QNormal):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                mu: Optional[float] = None, 
                sigma: Optional[float] = None, 
                q: Optional[int] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.sweep.QLogUniform(QUniform):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                min_value: Optional[float] = None, 
                max_value: Optional[float] = None, 
                q: Optional[int] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.sweep.QNormal(Normal):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                mu: Optional[float] = None, 
                sigma: Optional[float] = None, 
                q: Optional[int] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.sweep.QUniform(Uniform):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                min_value: Optional[Union[int, float]] = None, 
                max_value: Optional[Union[int, float]] = None, 
                q: Optional[int] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.sweep.Randint(SweepDistribution):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                upper: Optional[int] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.ml.sweep.RandomSamplingAlgorithm(SamplingAlgorithm):

        def __init__(
                self, 
                *, 
                logbase: Optional[Union[float, str]] = ..., 
                rule: Optional[str] = ..., 
                seed: Optional[int] = ...
            ) -> None: ...


    class azure.ai.ml.sweep.SamplingAlgorithm(ABC, RestTranslatableMixin):

        def __init__(self) -> None: ...


    class azure.ai.ml.sweep.SweepJob(Job, ParameterizedSweep, JobIOMixin):
        property base_path: str    # Read-only
        property creation_context: Optional[SystemData]    # Read-only
        property early_termination: Optional[Union[str, EarlyTerminationPolicy]]
        property id: Optional[str]    # Read-only
        property inputs: Dict[str, Union[Input, str, bool, int, float]]
        property limits: Optional[SweepJobLimits]
        property log_files: Optional[Dict[str, str]]    # Read-only
        property outputs: Dict[str, Output]
        property resources: Optional[Union[dict, JobResourceConfiguration]]
        property sampling_algorithm: Optional[Union[str, SamplingAlgorithm]]
        property status: Optional[str]    # Read-only
        property studio_url: Optional[str]    # Read-only
        property type: Optional[str]    # Read-only

        def __init__(
                self, 
                *, 
                compute: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                early_termination: Optional[Union[EarlyTerminationPolicy, BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy]] = ..., 
                experiment_name: Optional[str] = ..., 
                identity: Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]] = ..., 
                inputs: Optional[Dict[str, Union[Input, str, bool, int, float]]] = ..., 
                limits: Optional[SweepJobLimits] = ..., 
                name: Optional[str] = ..., 
                objective: Optional[Objective] = ..., 
                outputs: Optional[Dict] = ..., 
                properties: dict[str, str] = ..., 
                queue_settings: Optional[QueueSettings] = ..., 
                resources: Optional[Union[dict, JobResourceConfiguration]] = ..., 
                sampling_algorithm: Optional[Union[str, SamplingAlgorithm]] = ..., 
                search_space: Optional[Dict[str, Union[Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform]]] = ..., 
                tags: Optional[Dict] = ..., 
                trial: Optional[Union[CommandJob, CommandComponent]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        def dump(
                self, 
                dest: Union[str, PathLike, IO[AnyStr]], 
                **kwargs: Any
            ) -> None: ...

        def set_limits(
                self, 
                *, 
                max_concurrent_trials: Optional[int] = ..., 
                max_total_trials: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                trial_timeout: Optional[int] = ...
            ) -> None: ...

        def set_objective(
                self, 
                *, 
                goal: Optional[str] = ..., 
                primary_metric: Optional[str] = ...
            ) -> None: ...

        def set_resources(
                self, 
                *, 
                docker_args: Optional[str] = ..., 
                instance_count: Optional[int] = ..., 
                instance_type: Optional[Union[str, List[str]]] = ..., 
                locations: Optional[List[str]] = ..., 
                properties: Optional[Dict] = ..., 
                shm_size: Optional[str] = ...
            ) -> None: ...


    class azure.ai.ml.sweep.SweepJobLimits(JobLimits):
        property timeout: Optional[Union[int, str]]
        property trial_timeout: Optional[Union[int, str]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_concurrent_trials: Optional[int] = ..., 
                max_total_trials: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                trial_timeout: Optional[Union[int, str]] = ...
            ) -> None: ...


    class azure.ai.ml.sweep.TruncationSelectionPolicy(EarlyTerminationPolicy):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                delay_evaluation: int = 0, 
                evaluation_interval: int = 0, 
                truncation_percentage: int = 0
            ) -> None: ...


    class azure.ai.ml.sweep.Uniform(SweepDistribution):

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                min_value: Optional[float] = None, 
                max_value: Optional[float] = None, 
                **kwargs: Any
            ) -> None: ...


```