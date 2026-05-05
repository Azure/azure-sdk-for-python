```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.deploymentmanager

    class azure.mgmt.deploymentmanager.AzureDeploymentManager: implements ContextManager 
        artifact_sources: ArtifactSourcesOperations
        operations: Operations
        rollouts: RolloutsOperations
        service_topologies: ServiceTopologiesOperations
        service_units: ServiceUnitsOperations
        services: ServicesOperations
        steps: StepsOperations

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


namespace azure.mgmt.deploymentmanager.aio

    class azure.mgmt.deploymentmanager.aio.AzureDeploymentManager: implements AsyncContextManager 
        artifact_sources: ArtifactSourcesOperations
        operations: Operations
        rollouts: RolloutsOperations
        service_topologies: ServiceTopologiesOperations
        service_units: ServiceUnitsOperations
        services: ServicesOperations
        steps: StepsOperations

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


namespace azure.mgmt.deploymentmanager.aio.operations

    class azure.mgmt.deploymentmanager.aio.operations.ArtifactSourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                artifact_source_name: str, 
                artifact_source_info: Optional[ArtifactSource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactSource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                artifact_source_name: str, 
                artifact_source_info: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactSource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                artifact_source_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                artifact_source_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ArtifactSource: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[ArtifactSource]: ...


    class azure.mgmt.deploymentmanager.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OperationsList: ...


    class azure.mgmt.deploymentmanager.aio.operations.RolloutsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                rollout_name: str, 
                rollout_request: Optional[RolloutRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RolloutRequest]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                rollout_name: str, 
                rollout_request: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RolloutRequest]: ...

        @distributed_trace_async
        async def cancel(
                self, 
                resource_group_name: str, 
                rollout_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Rollout: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                rollout_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                rollout_name: str, 
                retry_attempt: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Rollout: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[Rollout]: ...

        @distributed_trace_async
        async def restart(
                self, 
                resource_group_name: str, 
                rollout_name: str, 
                skip_succeeded: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Rollout: ...


    class azure.mgmt.deploymentmanager.aio.operations.ServiceTopologiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_topology_info: ServiceTopologyResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceTopologyResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_topology_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceTopologyResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServiceTopologyResource: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[ServiceTopologyResource]: ...


    class azure.mgmt.deploymentmanager.aio.operations.ServiceUnitsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                service_unit_name: str, 
                service_unit_info: ServiceUnitResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceUnitResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                service_unit_name: str, 
                service_unit_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceUnitResource]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                service_unit_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                service_unit_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServiceUnitResource: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[ServiceUnitResource]: ...


    class azure.mgmt.deploymentmanager.aio.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                service_info: ServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                service_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[ServiceResource]: ...


    class azure.mgmt.deploymentmanager.aio.operations.StepsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                step_name: str, 
                step_info: Optional[StepResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StepResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                step_name: str, 
                step_info: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StepResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                step_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                step_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> StepResource: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[StepResource]: ...


namespace azure.mgmt.deploymentmanager.models

    class azure.mgmt.deploymentmanager.models.ApiKeyAuthentication(RestRequestAuthentication):
        in_property: Union[str, RestAuthLocation]
        name: str
        type: Union[str, RestAuthType]
        value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                in_property: Union[str, RestAuthLocation], 
                name: str, 
                value: str, 
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


    class azure.mgmt.deploymentmanager.models.ArtifactSource(TrackedResource):
        artifact_root: str
        authentication: Authentication
        id: str
        location: str
        name: str
        source_type: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifact_root: Optional[str] = ..., 
                authentication: Optional[Authentication] = ..., 
                location: str, 
                source_type: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.deploymentmanager.models.ArtifactSourceProperties(ArtifactSourcePropertiesAutoGenerated):
        artifact_root: str
        authentication: Authentication
        source_type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifact_root: Optional[str] = ..., 
                authentication: Authentication, 
                source_type: str, 
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


    class azure.mgmt.deploymentmanager.models.ArtifactSourcePropertiesAutoGenerated(Model):
        artifact_root: str
        authentication: Authentication
        source_type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifact_root: Optional[str] = ..., 
                authentication: Authentication, 
                source_type: str, 
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


    class azure.mgmt.deploymentmanager.models.Authentication(Model):
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


    class azure.mgmt.deploymentmanager.models.CloudErrorBody(Model):
        code: str
        details: list[CloudErrorBody]
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                details: Optional[List[CloudErrorBody]] = ..., 
                target: Optional[str] = ..., 
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


    class azure.mgmt.deploymentmanager.models.DeploymentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        INCREMENTAL = "Incremental"


    class azure.mgmt.deploymentmanager.models.HealthCheckStepAttributes(Model):
        healthy_state_duration: str
        max_elastic_duration: str
        type: str
        wait_duration: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                healthy_state_duration: str, 
                max_elastic_duration: Optional[str] = ..., 
                wait_duration: Optional[str] = ..., 
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


    class azure.mgmt.deploymentmanager.models.HealthCheckStepProperties(StepProperties):
        attributes: HealthCheckStepAttributes
        step_type: Union[str, StepType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                attributes: HealthCheckStepAttributes, 
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


    class azure.mgmt.deploymentmanager.models.Identity(Model):
        identity_ids: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                identity_ids: List[str], 
                type: str, 
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


    class azure.mgmt.deploymentmanager.models.Message(Model):
        message: str
        time_stamp: datetime

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


    class azure.mgmt.deploymentmanager.models.Operation(Model):
        display: OperationDetail
        name: str
        origin: str
        properties: JSON

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDetail] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
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


    class azure.mgmt.deploymentmanager.models.OperationDetail(Model):
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


    class azure.mgmt.deploymentmanager.models.OperationsList(Model):
        value: Operation

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[Operation] = ..., 
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


    class azure.mgmt.deploymentmanager.models.PrePostStep(Model):
        step_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                step_id: str, 
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


    class azure.mgmt.deploymentmanager.models.Resource(Model):
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


    class azure.mgmt.deploymentmanager.models.ResourceOperation(Model):
        operation_id: str
        provisioning_state: str
        resource_name: str
        resource_type: str
        status_code: str
        status_message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                resource_name: Optional[str] = ..., 
                resource_type: Optional[str] = ..., 
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


    class azure.mgmt.deploymentmanager.models.RestAuthLocation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEADER = "Header"
        QUERY = "Query"


    class azure.mgmt.deploymentmanager.models.RestAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        API_KEY = "ApiKey"
        ROLLOUT_IDENTITY = "RolloutIdentity"


    class azure.mgmt.deploymentmanager.models.RestHealthCheck(Model):
        name: str
        request: RestRequest
        response: RestResponse

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: str, 
                request: RestRequest, 
                response: Optional[RestResponse] = ..., 
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


    class azure.mgmt.deploymentmanager.models.RestHealthCheckStepAttributes(HealthCheckStepAttributes):
        health_checks: list[RestHealthCheck]
        healthy_state_duration: str
        max_elastic_duration: str
        type: str
        wait_duration: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                health_checks: Optional[List[RestHealthCheck]] = ..., 
                healthy_state_duration: str, 
                max_elastic_duration: Optional[str] = ..., 
                wait_duration: Optional[str] = ..., 
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


    class azure.mgmt.deploymentmanager.models.RestMatchQuantifier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        ANY = "Any"


    class azure.mgmt.deploymentmanager.models.RestRequest(Model):
        authentication: RestRequestAuthentication
        method: Union[str, RestRequestMethod]
        uri: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                authentication: RestRequestAuthentication, 
                method: Union[str, RestRequestMethod], 
                uri: str, 
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


    class azure.mgmt.deploymentmanager.models.RestRequestAuthentication(Model):
        type: Union[str, RestAuthType]

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


    class azure.mgmt.deploymentmanager.models.RestRequestMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GET = "GET"
        POST = "POST"


    class azure.mgmt.deploymentmanager.models.RestResponse(Model):
        regex: RestResponseRegex
        success_status_codes: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                regex: Optional[RestResponseRegex] = ..., 
                success_status_codes: Optional[List[str]] = ..., 
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


    class azure.mgmt.deploymentmanager.models.RestResponseRegex(Model):
        match_quantifier: Union[str, RestMatchQuantifier]
        matches: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                match_quantifier: Optional[Union[str, RestMatchQuantifier]] = ..., 
                matches: Optional[List[str]] = ..., 
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


    class azure.mgmt.deploymentmanager.models.Rollout(TrackedResource):
        artifact_source_id: str
        build_version: str
        id: str
        identity: Identity
        location: str
        name: str
        operation_info: RolloutOperationInfo
        services: list[Service]
        status: str
        step_groups: list[StepGroup]
        tags: dict[str, str]
        target_service_topology_id: str
        total_retry_attempts: int
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifact_source_id: Optional[str] = ..., 
                build_version: Optional[str] = ..., 
                identity: Optional[Identity] = ..., 
                location: str, 
                step_groups: Optional[List[StepGroup]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_service_topology_id: Optional[str] = ..., 
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


    class azure.mgmt.deploymentmanager.models.RolloutIdentityAuthentication(RestRequestAuthentication):
        type: Union[str, RestAuthType]

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


    class azure.mgmt.deploymentmanager.models.RolloutOperationInfo(Model):
        end_time: datetime
        error: CloudErrorBody
        retry_attempt: int
        skip_succeeded_on_retry: bool
        start_time: datetime

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


    class azure.mgmt.deploymentmanager.models.RolloutProperties(RolloutRequestProperties, RolloutPropertiesAutoGenerated):
        artifact_source_id: str
        build_version: str
        operation_info: RolloutOperationInfo
        services: list[Service]
        status: str
        step_groups: list[StepGroup]
        target_service_topology_id: str
        total_retry_attempts: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifact_source_id: Optional[str] = ..., 
                build_version: str, 
                step_groups: List[StepGroup], 
                target_service_topology_id: str, 
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


    class azure.mgmt.deploymentmanager.models.RolloutPropertiesAutoGenerated(Model):
        operation_info: RolloutOperationInfo
        services: list[Service]
        status: str
        total_retry_attempts: int

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


    class azure.mgmt.deploymentmanager.models.RolloutRequest(TrackedResource):
        artifact_source_id: str
        build_version: str
        id: str
        identity: Identity
        location: str
        name: str
        step_groups: list[StepGroup]
        tags: dict[str, str]
        target_service_topology_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifact_source_id: Optional[str] = ..., 
                build_version: str, 
                identity: Identity, 
                location: str, 
                step_groups: List[StepGroup], 
                tags: Optional[Dict[str, str]] = ..., 
                target_service_topology_id: str, 
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


    class azure.mgmt.deploymentmanager.models.RolloutRequestProperties(Model):
        artifact_source_id: str
        build_version: str
        step_groups: list[StepGroup]
        target_service_topology_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifact_source_id: Optional[str] = ..., 
                build_version: str, 
                step_groups: List[StepGroup], 
                target_service_topology_id: str, 
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


    class azure.mgmt.deploymentmanager.models.RolloutStep(Model):
        messages: list[Message]
        name: str
        operation_info: StepOperationInfo
        resource_operations: list[ResourceOperation]
        status: str
        step_group: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: str, 
                step_group: Optional[str] = ..., 
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


    class azure.mgmt.deploymentmanager.models.SasAuthentication(Authentication):
        sas_uri: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                sas_uri: Optional[str] = ..., 
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


    class azure.mgmt.deploymentmanager.models.Service(ServiceProperties):
        name: str
        service_units: list[ServiceUnit]
        target_location: str
        target_subscription_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                service_units: Optional[List[ServiceUnit]] = ..., 
                target_location: str, 
                target_subscription_id: str, 
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


    class azure.mgmt.deploymentmanager.models.ServiceProperties(Model):
        target_location: str
        target_subscription_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                target_location: str, 
                target_subscription_id: str, 
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


    class azure.mgmt.deploymentmanager.models.ServiceResource(TrackedResource):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        target_location: str
        target_subscription_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                target_location: str, 
                target_subscription_id: str, 
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


    class azure.mgmt.deploymentmanager.models.ServiceResourceProperties(ServiceProperties):
        target_location: str
        target_subscription_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                target_location: str, 
                target_subscription_id: str, 
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


    class azure.mgmt.deploymentmanager.models.ServiceTopologyProperties(Model):
        artifact_source_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifact_source_id: Optional[str] = ..., 
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


    class azure.mgmt.deploymentmanager.models.ServiceTopologyResource(TrackedResource):
        artifact_source_id: str
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifact_source_id: Optional[str] = ..., 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.deploymentmanager.models.ServiceTopologyResourceProperties(ServiceTopologyProperties):
        artifact_source_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifact_source_id: Optional[str] = ..., 
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


    class azure.mgmt.deploymentmanager.models.ServiceUnit(ServiceUnitProperties):
        artifacts: ServiceUnitArtifacts
        deployment_mode: Union[str, DeploymentMode]
        name: str
        steps: list[RolloutStep]
        target_resource_group: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifacts: Optional[ServiceUnitArtifacts] = ..., 
                deployment_mode: Union[str, DeploymentMode], 
                name: Optional[str] = ..., 
                steps: Optional[List[RolloutStep]] = ..., 
                target_resource_group: str, 
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


    class azure.mgmt.deploymentmanager.models.ServiceUnitArtifacts(Model):
        parameters_artifact_source_relative_path: str
        parameters_uri: str
        template_artifact_source_relative_path: str
        template_uri: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                parameters_artifact_source_relative_path: Optional[str] = ..., 
                parameters_uri: Optional[str] = ..., 
                template_artifact_source_relative_path: Optional[str] = ..., 
                template_uri: Optional[str] = ..., 
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


    class azure.mgmt.deploymentmanager.models.ServiceUnitProperties(Model):
        artifacts: ServiceUnitArtifacts
        deployment_mode: Union[str, DeploymentMode]
        target_resource_group: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifacts: Optional[ServiceUnitArtifacts] = ..., 
                deployment_mode: Union[str, DeploymentMode], 
                target_resource_group: str, 
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


    class azure.mgmt.deploymentmanager.models.ServiceUnitResource(TrackedResource):
        artifacts: ServiceUnitArtifacts
        deployment_mode: Union[str, DeploymentMode]
        id: str
        location: str
        name: str
        tags: dict[str, str]
        target_resource_group: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifacts: Optional[ServiceUnitArtifacts] = ..., 
                deployment_mode: Union[str, DeploymentMode], 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                target_resource_group: str, 
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


    class azure.mgmt.deploymentmanager.models.ServiceUnitResourceProperties(ServiceUnitProperties):
        artifacts: ServiceUnitArtifacts
        deployment_mode: Union[str, DeploymentMode]
        target_resource_group: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                artifacts: Optional[ServiceUnitArtifacts] = ..., 
                deployment_mode: Union[str, DeploymentMode], 
                target_resource_group: str, 
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


    class azure.mgmt.deploymentmanager.models.StepGroup(Model):
        depends_on_step_groups: list[str]
        deployment_target_id: str
        name: str
        post_deployment_steps: list[PrePostStep]
        pre_deployment_steps: list[PrePostStep]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                depends_on_step_groups: Optional[List[str]] = ..., 
                deployment_target_id: str, 
                name: str, 
                post_deployment_steps: Optional[List[PrePostStep]] = ..., 
                pre_deployment_steps: Optional[List[PrePostStep]] = ..., 
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


    class azure.mgmt.deploymentmanager.models.StepOperationInfo(Model):
        correlation_id: str
        deployment_name: str
        end_time: datetime
        error: CloudErrorBody
        last_updated_time: datetime
        start_time: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ..., 
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


    class azure.mgmt.deploymentmanager.models.StepProperties(Model):
        step_type: Union[str, StepType]

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


    class azure.mgmt.deploymentmanager.models.StepResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: StepProperties
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: StepProperties, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.deploymentmanager.models.StepType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTH_CHECK = "HealthCheck"
        WAIT = "Wait"


    class azure.mgmt.deploymentmanager.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.deploymentmanager.models.WaitStepAttributes(Model):
        duration: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                duration: str, 
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


    class azure.mgmt.deploymentmanager.models.WaitStepProperties(StepProperties):
        attributes: WaitStepAttributes
        step_type: Union[str, StepType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                attributes: WaitStepAttributes, 
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


namespace azure.mgmt.deploymentmanager.operations

    class azure.mgmt.deploymentmanager.operations.ArtifactSourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                artifact_source_name: str, 
                artifact_source_info: Optional[ArtifactSource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactSource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                artifact_source_name: str, 
                artifact_source_info: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactSource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                artifact_source_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                artifact_source_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ArtifactSource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[ArtifactSource]: ...


    class azure.mgmt.deploymentmanager.operations.Operations:

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
            ) -> OperationsList: ...


    class azure.mgmt.deploymentmanager.operations.RolloutsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                rollout_name: str, 
                rollout_request: Optional[RolloutRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RolloutRequest]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                rollout_name: str, 
                rollout_request: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RolloutRequest]: ...

        @distributed_trace
        def cancel(
                self, 
                resource_group_name: str, 
                rollout_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Rollout: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                rollout_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                rollout_name: str, 
                retry_attempt: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Rollout: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[Rollout]: ...

        @distributed_trace
        def restart(
                self, 
                resource_group_name: str, 
                rollout_name: str, 
                skip_succeeded: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Rollout: ...


    class azure.mgmt.deploymentmanager.operations.ServiceTopologiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_topology_info: ServiceTopologyResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceTopologyResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_topology_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceTopologyResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServiceTopologyResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[ServiceTopologyResource]: ...


    class azure.mgmt.deploymentmanager.operations.ServiceUnitsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                service_unit_name: str, 
                service_unit_info: ServiceUnitResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceUnitResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                service_unit_name: str, 
                service_unit_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceUnitResource]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                service_unit_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                service_unit_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServiceUnitResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[ServiceUnitResource]: ...


    class azure.mgmt.deploymentmanager.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                service_info: ServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                service_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                service_topology_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[ServiceResource]: ...


    class azure.mgmt.deploymentmanager.operations.StepsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                step_name: str, 
                step_info: Optional[StepResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StepResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                step_name: str, 
                step_info: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StepResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                step_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                step_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> StepResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[StepResource]: ...


```