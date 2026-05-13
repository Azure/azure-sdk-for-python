```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.10.20


namespace azure.mgmt.advisor

    class azure.mgmt.advisor.AdvisorManagementClient: implements ContextManager 
        configurations: ConfigurationsOperations
        operations: Operations
        recommendation_metadata: RecommendationMetadataOperations
        recommendations: RecommendationsOperations
        suppressions: SuppressionsOperations

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


namespace azure.mgmt.advisor.aio

    class azure.mgmt.advisor.aio.AdvisorManagementClient: implements AsyncContextManager 
        configurations: ConfigurationsOperations
        operations: Operations
        recommendation_metadata: RecommendationMetadataOperations
        recommendations: RecommendationsOperations
        suppressions: SuppressionsOperations

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


namespace azure.mgmt.advisor.aio.operations

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
                config_contract: IO, 
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
                config_contract: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigData]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigData]: ...


    class azure.mgmt.advisor.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[OperationEntity]: ...


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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MetadataEntity: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[MetadataEntity]: ...


    class azure.mgmt.advisor.aio.operations.RecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def generate(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ResourceRecommendationBase: ...

        @distributed_trace_async
        async def get_generate_status(
                self, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ResourceRecommendationBase]: ...


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
                suppression_contract: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SuppressionContract: ...

        @distributed_trace
        def list(
                self, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SuppressionContract]: ...


namespace azure.mgmt.advisor.models

    class azure.mgmt.advisor.models.ARMErrorResponseBody(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.ArmErrorResponse(Model):
        error: ARMErrorResponseBody

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ARMErrorResponseBody] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.Category(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COST = "Cost"
        HIGH_AVAILABILITY = "HighAvailability"
        OPERATIONAL_EXCELLENCE = "OperationalExcellence"
        PERFORMANCE = "Performance"
        SECURITY = "Security"


    class azure.mgmt.advisor.models.ConfigData(Resource):
        digests: list[DigestConfig]
        exclude: bool
        id: str
        low_cpu_threshold: Union[str, CpuThreshold]
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                digests: Optional[List[DigestConfig]] = ..., 
                exclude: Optional[bool] = ..., 
                low_cpu_threshold: Optional[Union[str, CpuThreshold]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.ConfigurationListResult(Model):
        next_link: str
        value: list[ConfigData]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ConfigData]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.ConfigurationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.advisor.models.CpuThreshold(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIFTEEN = "15"
        FIVE = "5"
        TEN = "10"
        TWENTY = "20"


    class azure.mgmt.advisor.models.DigestConfig(Model):
        action_group_resource_id: str
        categories: Union[list[str, Category]]
        frequency: int
        language: str
        name: str
        state: Union[str, DigestConfigState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                action_group_resource_id: Optional[str] = ..., 
                categories: Optional[List[Union[str, Category]]] = ..., 
                frequency: Optional[int] = ..., 
                language: Optional[str] = ..., 
                name: Optional[str] = ..., 
                state: Optional[Union[str, DigestConfigState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.DigestConfigState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DISABLED = "Disabled"


    class azure.mgmt.advisor.models.Impact(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.advisor.models.MetadataEntity(Model):
        applicable_scenarios: Union[list[str, Scenario]]
        depends_on: list[str]
        display_name: str
        id: str
        name: str
        supported_values: list[MetadataSupportedValueDetail]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                applicable_scenarios: Optional[List[Union[str, Scenario]]] = ..., 
                depends_on: Optional[List[str]] = ..., 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                supported_values: Optional[List[MetadataSupportedValueDetail]] = ..., 
                type: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.MetadataEntityListResult(Model):
        next_link: str
        value: list[MetadataEntity]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[MetadataEntity]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.MetadataSupportedValueDetail(Model):
        display_name: str
        id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.OperationDisplayInfo(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.OperationEntity(Model):
        display: OperationDisplayInfo
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplayInfo] = ..., 
                name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.OperationEntityListResult(Model):
        next_link: str
        value: list[OperationEntity]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[OperationEntity]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.Resource(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.ResourceMetadata(Model):
        action: dict[str, JSON]
        plural: str
        resource_id: str
        singular: str
        source: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                action: Optional[Dict[str, JSON]] = ..., 
                plural: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                singular: Optional[str] = ..., 
                source: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.ResourceRecommendationBase(Resource):
        actions: list[dict[str, JSON]]
        category: Union[str, Category]
        description: str
        exposed_metadata_properties: dict[str, JSON]
        extended_properties: dict[str, str]
        id: str
        impact: Union[str, Impact]
        impacted_field: str
        impacted_value: str
        label: str
        last_updated: datetime
        learn_more_link: str
        metadata: dict[str, JSON]
        name: str
        potential_benefits: str
        recommendation_type_id: str
        remediation: dict[str, JSON]
        resource_metadata: ResourceMetadata
        short_description: ShortDescription
        suppression_ids: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                actions: Optional[List[Dict[str, JSON]]] = ..., 
                category: Optional[Union[str, Category]] = ..., 
                description: Optional[str] = ..., 
                exposed_metadata_properties: Optional[Dict[str, JSON]] = ..., 
                extended_properties: Optional[Dict[str, str]] = ..., 
                impact: Optional[Union[str, Impact]] = ..., 
                impacted_field: Optional[str] = ..., 
                impacted_value: Optional[str] = ..., 
                label: Optional[str] = ..., 
                last_updated: Optional[datetime] = ..., 
                learn_more_link: Optional[str] = ..., 
                metadata: Optional[Dict[str, JSON]] = ..., 
                potential_benefits: Optional[str] = ..., 
                recommendation_type_id: Optional[str] = ..., 
                remediation: Optional[Dict[str, JSON]] = ..., 
                resource_metadata: Optional[ResourceMetadata] = ..., 
                short_description: Optional[ShortDescription] = ..., 
                suppression_ids: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.ResourceRecommendationBaseListResult(Model):
        next_link: str
        value: list[ResourceRecommendationBase]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ResourceRecommendationBase]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.Scenario(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS = "Alerts"


    class azure.mgmt.advisor.models.ShortDescription(Model):
        problem: str
        solution: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                problem: Optional[str] = ..., 
                solution: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.SuppressionContract(Resource):
        expiration_time_stamp: datetime
        id: str
        name: str
        suppression_id: str
        ttl: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                suppression_id: Optional[str] = ..., 
                ttl: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.advisor.models.SuppressionContractListResult(Model):
        next_link: str
        value: list[SuppressionContract]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SuppressionContract]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


namespace azure.mgmt.advisor.operations

    class azure.mgmt.advisor.operations.ConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                config_contract: IO, 
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
                config_contract: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigData: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigData]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigData]: ...


    class azure.mgmt.advisor.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[OperationEntity]: ...


    class azure.mgmt.advisor.operations.RecommendationMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MetadataEntity: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[MetadataEntity]: ...


    class azure.mgmt.advisor.operations.RecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def generate(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ResourceRecommendationBase: ...

        @distributed_trace
        def get_generate_status(
                self, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ResourceRecommendationBase]: ...


    class azure.mgmt.advisor.operations.SuppressionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                suppression_contract: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                recommendation_id: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SuppressionContract: ...

        @distributed_trace
        def list(
                self, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SuppressionContract]: ...


```