```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.timeseriesinsights

    class azure.mgmt.timeseriesinsights.TimeSeriesInsightsClient: implements ContextManager 
        access_policies: AccessPoliciesOperations
        environments: EnvironmentsOperations
        event_sources: EventSourcesOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        reference_data_sets: ReferenceDataSetsOperations

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


namespace azure.mgmt.timeseriesinsights.aio

    class azure.mgmt.timeseriesinsights.aio.TimeSeriesInsightsClient: implements AsyncContextManager 
        access_policies: AccessPoliciesOperations
        environments: EnvironmentsOperations
        event_sources: EventSourcesOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        reference_data_sets: ReferenceDataSetsOperations

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


namespace azure.mgmt.timeseriesinsights.aio.operations

    class azure.mgmt.timeseriesinsights.aio.operations.AccessPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                access_policy_name: str, 
                parameters: AccessPolicyCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessPolicyResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                access_policy_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessPolicyResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                access_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                access_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AccessPolicyResource: ...

        @distributed_trace_async
        async def list_by_environment(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AccessPolicyListResponse: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                access_policy_name: str, 
                access_policy_update_parameters: AccessPolicyUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessPolicyResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                access_policy_name: str, 
                access_policy_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessPolicyResource: ...


    class azure.mgmt.timeseriesinsights.aio.operations.EnvironmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                parameters: EnvironmentCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnvironmentResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnvironmentResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_update_parameters: EnvironmentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnvironmentResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnvironmentResource]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentResource: ...

        @distributed_trace_async
        async def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentListResponse: ...

        @distributed_trace_async
        async def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentListResponse: ...


    class azure.mgmt.timeseriesinsights.aio.operations.EventSourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                event_source_name: str, 
                parameters: EventSourceCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventSourceResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                event_source_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventSourceResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                event_source_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                event_source_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EventSourceResource: ...

        @distributed_trace_async
        async def list_by_environment(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EventSourceListResponse: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                event_source_name: str, 
                event_source_update_parameters: EventSourceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventSourceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                event_source_name: str, 
                event_source_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventSourceResource: ...


    class azure.mgmt.timeseriesinsights.aio.operations.Operations:

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
            ) -> AsyncIterable[Operation]: ...


    class azure.mgmt.timeseriesinsights.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def list_by_environment(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateEndpointConnectionListResult: ...


    class azure.mgmt.timeseriesinsights.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_supported(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PrivateLinkResource]: ...


    class azure.mgmt.timeseriesinsights.aio.operations.ReferenceDataSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                reference_data_set_name: str, 
                parameters: ReferenceDataSetCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReferenceDataSetResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                reference_data_set_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReferenceDataSetResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                reference_data_set_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                reference_data_set_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ReferenceDataSetResource: ...

        @distributed_trace_async
        async def list_by_environment(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ReferenceDataSetListResponse: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                reference_data_set_name: str, 
                reference_data_set_update_parameters: ReferenceDataSetUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReferenceDataSetResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                reference_data_set_name: str, 
                reference_data_set_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReferenceDataSetResource: ...


namespace azure.mgmt.timeseriesinsights.models

    class azure.mgmt.timeseriesinsights.models.AccessPolicyCreateOrUpdateParameters(Model):
        description: str
        principal_object_id: str
        roles: Union[list[str, AccessPolicyRole]]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                principal_object_id: Optional[str] = ..., 
                roles: Optional[List[Union[str, AccessPolicyRole]]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.AccessPolicyListResponse(Model):
        value: list[AccessPolicyResource]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[AccessPolicyResource]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.AccessPolicyResource(Resource):
        description: str
        id: str
        name: str
        principal_object_id: str
        roles: Union[list[str, AccessPolicyRole]]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                principal_object_id: Optional[str] = ..., 
                roles: Optional[List[Union[str, AccessPolicyRole]]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.AccessPolicyRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTRIBUTOR = "Contributor"
        READER = "Reader"


    class azure.mgmt.timeseriesinsights.models.AccessPolicyUpdateParameters(Model):
        description: str
        roles: Union[list[str, AccessPolicyRole]]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                roles: Optional[List[Union[str, AccessPolicyRole]]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.AzureEventSourceProperties(EventSourceCommonProperties):
        creation_time: datetime
        event_source_resource_id: str
        local_timestamp: LocalTimestamp
        provisioning_state: Union[str, ProvisioningState]
        time: str
        timestamp_property_name: str
        type: Union[str, IngressStartAtType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                event_source_resource_id: str, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
                time: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
                type: Optional[Union[str, IngressStartAtType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.CloudErrorBody(Model):
        code: str
        details: list[CloudErrorBody]
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.CreateOrUpdateTrackedResourceProperties(Model):
        location: str
        tags: dict[str, str]

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


    class azure.mgmt.timeseriesinsights.models.DataStringComparisonBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ORDINAL = "Ordinal"
        ORDINAL_IGNORE_CASE = "OrdinalIgnoreCase"


    class azure.mgmt.timeseriesinsights.models.Dimension(Model):
        display_name: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EnvironmentCreateOrUpdateParameters(CreateOrUpdateTrackedResourceProperties):
        kind: Union[str, EnvironmentKind]
        location: str
        sku: Sku
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                sku: Sku, 
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


    class azure.mgmt.timeseriesinsights.models.EnvironmentKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEN1 = "Gen1"
        GEN2 = "Gen2"


    class azure.mgmt.timeseriesinsights.models.EnvironmentListResponse(Model):
        value: list[EnvironmentResource]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[EnvironmentResource]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EnvironmentResource(TrackedResource):
        id: str
        kind: Union[str, EnvironmentResourceKind]
        location: str
        name: str
        sku: Sku
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                sku: Sku, 
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


    class azure.mgmt.timeseriesinsights.models.EnvironmentResourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEN1 = "Gen1"
        GEN2 = "Gen2"


    class azure.mgmt.timeseriesinsights.models.EnvironmentResourceProperties(ResourceProperties):
        creation_time: datetime
        data_access_fqdn: str
        data_access_id: str
        provisioning_state: Union[str, ProvisioningState]
        status: EnvironmentStatus

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


    class azure.mgmt.timeseriesinsights.models.EnvironmentStateDetails(Model):
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


    class azure.mgmt.timeseriesinsights.models.EnvironmentStatus(Model):
        ingress: IngressEnvironmentStatus
        warm_storage: WarmStorageEnvironmentStatus

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


    class azure.mgmt.timeseriesinsights.models.EnvironmentUpdateParameters(Model):
        kind: Union[str, EnvironmentKind]
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.timeseriesinsights.models.EventHubEventSourceCommonProperties(AzureEventSourceProperties):
        consumer_group_name: str
        creation_time: datetime
        event_hub_name: str
        event_source_resource_id: str
        key_name: str
        local_timestamp: LocalTimestamp
        provisioning_state: Union[str, ProvisioningState]
        service_bus_namespace: str
        time: str
        timestamp_property_name: str
        type: Union[str, IngressStartAtType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                consumer_group_name: str, 
                event_hub_name: str, 
                event_source_resource_id: str, 
                key_name: str, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
                service_bus_namespace: str, 
                time: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
                type: Optional[Union[str, IngressStartAtType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EventHubEventSourceCreateOrUpdateParameters(EventSourceCreateOrUpdateParameters):
        consumer_group_name: str
        creation_time: datetime
        event_hub_name: str
        event_source_resource_id: str
        key_name: str
        kind: Union[str, EventSourceKind]
        local_timestamp: LocalTimestamp
        local_timestamp_properties_local_timestamp: LocalTimestamp
        location: str
        provisioning_state: Union[str, ProvisioningState]
        service_bus_namespace: str
        shared_access_key: str
        tags: dict[str, str]
        time: str
        timestamp_property_name: str
        type: Union[str, IngressStartAtType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                consumer_group_name: str, 
                event_hub_name: str, 
                event_source_resource_id: str, 
                key_name: str, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
                local_timestamp_properties_local_timestamp: Optional[LocalTimestamp] = ..., 
                location: str, 
                service_bus_namespace: str, 
                shared_access_key: str, 
                tags: Optional[Dict[str, str]] = ..., 
                time: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
                type: Optional[Union[str, IngressStartAtType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EventHubEventSourceCreationProperties(EventHubEventSourceCommonProperties):
        consumer_group_name: str
        creation_time: datetime
        event_hub_name: str
        event_source_resource_id: str
        key_name: str
        local_timestamp: LocalTimestamp
        provisioning_state: Union[str, ProvisioningState]
        service_bus_namespace: str
        shared_access_key: str
        time: str
        timestamp_property_name: str
        type: Union[str, IngressStartAtType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                consumer_group_name: str, 
                event_hub_name: str, 
                event_source_resource_id: str, 
                key_name: str, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
                service_bus_namespace: str, 
                shared_access_key: str, 
                time: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
                type: Optional[Union[str, IngressStartAtType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EventHubEventSourceMutableProperties(EventSourceMutableProperties):
        shared_access_key: str
        timestamp_property_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                shared_access_key: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EventHubEventSourceResource(EventSourceResource):
        consumer_group_name: str
        creation_time: datetime
        event_hub_name: str
        event_source_resource_id: str
        id: str
        key_name: str
        kind: Union[str, EventSourceResourceKind]
        local_timestamp: LocalTimestamp
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        service_bus_namespace: str
        tags: dict[str, str]
        time: str
        timestamp_property_name: str
        type: str
        type_properties_ingress_start_at_type: Union[str, IngressStartAtType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                consumer_group_name: str, 
                event_hub_name: str, 
                event_source_resource_id: str, 
                key_name: str, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
                location: str, 
                service_bus_namespace: str, 
                tags: Optional[Dict[str, str]] = ..., 
                time: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
                type_properties_ingress_start_at_type: Optional[Union[str, IngressStartAtType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EventHubEventSourceResourceProperties(EventHubEventSourceCommonProperties):
        consumer_group_name: str
        creation_time: datetime
        event_hub_name: str
        event_source_resource_id: str
        key_name: str
        local_timestamp: LocalTimestamp
        provisioning_state: Union[str, ProvisioningState]
        service_bus_namespace: str
        time: str
        timestamp_property_name: str
        type: Union[str, IngressStartAtType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                consumer_group_name: str, 
                event_hub_name: str, 
                event_source_resource_id: str, 
                key_name: str, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
                service_bus_namespace: str, 
                time: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
                type: Optional[Union[str, IngressStartAtType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EventHubEventSourceUpdateParameters(EventSourceUpdateParameters):
        kind: Union[str, EventSourceKind]
        shared_access_key: str
        tags: dict[str, str]
        timestamp_property_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                shared_access_key: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                timestamp_property_name: Optional[str] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EventSourceCommonProperties(ResourceProperties):
        creation_time: datetime
        local_timestamp: LocalTimestamp
        provisioning_state: Union[str, ProvisioningState]
        time: str
        timestamp_property_name: str
        type: Union[str, IngressStartAtType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
                time: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
                type: Optional[Union[str, IngressStartAtType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EventSourceCreateOrUpdateParameters(CreateOrUpdateTrackedResourceProperties):
        kind: Union[str, EventSourceKind]
        local_timestamp: LocalTimestamp
        location: str
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EventSourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_EVENT_HUB = "Microsoft.EventHub"
        MICROSOFT_IO_T_HUB = "Microsoft.IoTHub"


    class azure.mgmt.timeseriesinsights.models.EventSourceListResponse(Model):
        value: list[EventSourceResource]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[EventSourceResource]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EventSourceMutableProperties(Model):
        timestamp_property_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                timestamp_property_name: Optional[str] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.EventSourceResource(TrackedResource):
        id: str
        kind: Union[str, EventSourceResourceKind]
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


    class azure.mgmt.timeseriesinsights.models.EventSourceResourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_EVENT_HUB = "Microsoft.EventHub"
        MICROSOFT_IO_T_HUB = "Microsoft.IoTHub"


    class azure.mgmt.timeseriesinsights.models.EventSourceUpdateParameters(Model):
        kind: Union[str, EventSourceKind]
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.timeseriesinsights.models.Gen1EnvironmentCreateOrUpdateParameters(EnvironmentCreateOrUpdateParameters):
        data_retention_time: timedelta
        kind: Union[str, EnvironmentKind]
        location: str
        partition_key_properties: list[TimeSeriesIdProperty]
        sku: Sku
        storage_limit_exceeded_behavior: Union[str, StorageLimitExceededBehavior]
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_retention_time: timedelta, 
                location: str, 
                partition_key_properties: Optional[List[TimeSeriesIdProperty]] = ..., 
                sku: Sku, 
                storage_limit_exceeded_behavior: Optional[Union[str, StorageLimitExceededBehavior]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.Gen1EnvironmentCreationProperties(Model):
        data_retention_time: timedelta
        partition_key_properties: list[TimeSeriesIdProperty]
        storage_limit_exceeded_behavior: Union[str, StorageLimitExceededBehavior]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_retention_time: timedelta, 
                partition_key_properties: Optional[List[TimeSeriesIdProperty]] = ..., 
                storage_limit_exceeded_behavior: Optional[Union[str, StorageLimitExceededBehavior]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.Gen1EnvironmentResource(EnvironmentResource):
        creation_time: datetime
        data_access_fqdn: str
        data_access_id: str
        data_retention_time: timedelta
        id: str
        kind: Union[str, EnvironmentResourceKind]
        location: str
        name: str
        partition_key_properties: list[TimeSeriesIdProperty]
        provisioning_state: Union[str, ProvisioningState]
        sku: Sku
        status: EnvironmentStatus
        storage_limit_exceeded_behavior: Union[str, StorageLimitExceededBehavior]
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_retention_time: timedelta, 
                location: str, 
                partition_key_properties: Optional[List[TimeSeriesIdProperty]] = ..., 
                sku: Sku, 
                storage_limit_exceeded_behavior: Optional[Union[str, StorageLimitExceededBehavior]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.Gen1EnvironmentResourceProperties(Gen1EnvironmentCreationProperties, EnvironmentResourceProperties):
        creation_time: datetime
        data_access_fqdn: str
        data_access_id: str
        data_retention_time: timedelta
        partition_key_properties: list[TimeSeriesIdProperty]
        provisioning_state: Union[str, ProvisioningState]
        status: EnvironmentStatus
        storage_limit_exceeded_behavior: Union[str, StorageLimitExceededBehavior]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_retention_time: timedelta, 
                partition_key_properties: Optional[List[TimeSeriesIdProperty]] = ..., 
                storage_limit_exceeded_behavior: Optional[Union[str, StorageLimitExceededBehavior]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.Gen1EnvironmentUpdateParameters(EnvironmentUpdateParameters):
        data_retention_time: timedelta
        kind: Union[str, EnvironmentKind]
        sku: Sku
        storage_limit_exceeded_behavior: Union[str, StorageLimitExceededBehavior]
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_retention_time: Optional[timedelta] = ..., 
                sku: Optional[Sku] = ..., 
                storage_limit_exceeded_behavior: Optional[Union[str, StorageLimitExceededBehavior]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.Gen2EnvironmentCreateOrUpdateParameters(EnvironmentCreateOrUpdateParameters):
        kind: Union[str, EnvironmentKind]
        location: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        public_network_access: Union[str, PublicNetworkAccess]
        sku: Sku
        storage_configuration: Gen2StorageConfigurationInput
        tags: dict[str, str]
        time_series_id_properties: list[TimeSeriesIdProperty]
        warm_store_configuration: WarmStoreConfigurationProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: Sku, 
                storage_configuration: Gen2StorageConfigurationInput, 
                tags: Optional[Dict[str, str]] = ..., 
                time_series_id_properties: List[TimeSeriesIdProperty], 
                warm_store_configuration: Optional[WarmStoreConfigurationProperties] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.Gen2EnvironmentResource(EnvironmentResource):
        creation_time: datetime
        data_access_fqdn: str
        data_access_id: str
        id: str
        kind: Union[str, EnvironmentResourceKind]
        location: str
        name: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        sku: Sku
        status: EnvironmentStatus
        storage_configuration: Gen2StorageConfigurationOutput
        tags: dict[str, str]
        time_series_id_properties: list[TimeSeriesIdProperty]
        type: str
        warm_store_configuration: WarmStoreConfigurationProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: Sku, 
                storage_configuration: Gen2StorageConfigurationOutput, 
                tags: Optional[Dict[str, str]] = ..., 
                time_series_id_properties: List[TimeSeriesIdProperty], 
                warm_store_configuration: Optional[WarmStoreConfigurationProperties] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.Gen2EnvironmentResourceProperties(EnvironmentResourceProperties):
        creation_time: datetime
        data_access_fqdn: str
        data_access_id: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        status: EnvironmentStatus
        storage_configuration: Gen2StorageConfigurationOutput
        time_series_id_properties: list[TimeSeriesIdProperty]
        warm_store_configuration: WarmStoreConfigurationProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                storage_configuration: Gen2StorageConfigurationOutput, 
                time_series_id_properties: List[TimeSeriesIdProperty], 
                warm_store_configuration: Optional[WarmStoreConfigurationProperties] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.Gen2EnvironmentUpdateParameters(EnvironmentUpdateParameters):
        kind: Union[str, EnvironmentKind]
        storage_configuration: Gen2StorageConfigurationMutableProperties
        tags: dict[str, str]
        warm_store_configuration: WarmStoreConfigurationProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                storage_configuration: Optional[Gen2StorageConfigurationMutableProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                warm_store_configuration: Optional[WarmStoreConfigurationProperties] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.Gen2StorageConfigurationInput(Model):
        account_name: str
        management_key: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                account_name: str, 
                management_key: str, 
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


    class azure.mgmt.timeseriesinsights.models.Gen2StorageConfigurationMutableProperties(Model):
        management_key: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                management_key: str, 
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


    class azure.mgmt.timeseriesinsights.models.Gen2StorageConfigurationOutput(Model):
        account_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                account_name: str, 
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


    class azure.mgmt.timeseriesinsights.models.IngressEnvironmentStatus(Model):
        state: Union[str, IngressState]
        state_details: EnvironmentStateDetails

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Optional[Union[str, IngressState]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.IngressStartAtType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_ENQUEUED_TIME = "CustomEnqueuedTime"
        EARLIEST_AVAILABLE = "EarliestAvailable"
        EVENT_SOURCE_CREATION_TIME = "EventSourceCreationTime"


    class azure.mgmt.timeseriesinsights.models.IngressState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        PAUSED = "Paused"
        READY = "Ready"
        RUNNING = "Running"
        UNKNOWN = "Unknown"


    class azure.mgmt.timeseriesinsights.models.IoTHubEventSourceCommonProperties(AzureEventSourceProperties):
        consumer_group_name: str
        creation_time: datetime
        event_source_resource_id: str
        iot_hub_name: str
        key_name: str
        local_timestamp: LocalTimestamp
        provisioning_state: Union[str, ProvisioningState]
        time: str
        timestamp_property_name: str
        type: Union[str, IngressStartAtType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                consumer_group_name: str, 
                event_source_resource_id: str, 
                iot_hub_name: str, 
                key_name: str, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
                time: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
                type: Optional[Union[str, IngressStartAtType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.IoTHubEventSourceCreateOrUpdateParameters(EventSourceCreateOrUpdateParameters):
        consumer_group_name: str
        creation_time: datetime
        event_source_resource_id: str
        iot_hub_name: str
        key_name: str
        kind: Union[str, EventSourceKind]
        local_timestamp: LocalTimestamp
        local_timestamp_properties_local_timestamp: LocalTimestamp
        location: str
        provisioning_state: Union[str, ProvisioningState]
        shared_access_key: str
        tags: dict[str, str]
        time: str
        timestamp_property_name: str
        type: Union[str, IngressStartAtType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                consumer_group_name: str, 
                event_source_resource_id: str, 
                iot_hub_name: str, 
                key_name: str, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
                local_timestamp_properties_local_timestamp: Optional[LocalTimestamp] = ..., 
                location: str, 
                shared_access_key: str, 
                tags: Optional[Dict[str, str]] = ..., 
                time: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
                type: Optional[Union[str, IngressStartAtType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.IoTHubEventSourceCreationProperties(IoTHubEventSourceCommonProperties):
        consumer_group_name: str
        creation_time: datetime
        event_source_resource_id: str
        iot_hub_name: str
        key_name: str
        local_timestamp: LocalTimestamp
        provisioning_state: Union[str, ProvisioningState]
        shared_access_key: str
        time: str
        timestamp_property_name: str
        type: Union[str, IngressStartAtType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                consumer_group_name: str, 
                event_source_resource_id: str, 
                iot_hub_name: str, 
                key_name: str, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
                shared_access_key: str, 
                time: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
                type: Optional[Union[str, IngressStartAtType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.IoTHubEventSourceMutableProperties(EventSourceMutableProperties):
        shared_access_key: str
        timestamp_property_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                shared_access_key: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.IoTHubEventSourceResource(EventSourceResource):
        consumer_group_name: str
        creation_time: datetime
        event_source_resource_id: str
        id: str
        iot_hub_name: str
        key_name: str
        kind: Union[str, EventSourceResourceKind]
        local_timestamp: LocalTimestamp
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        tags: dict[str, str]
        time: str
        timestamp_property_name: str
        type: str
        type_properties_ingress_start_at_type: Union[str, IngressStartAtType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                consumer_group_name: str, 
                event_source_resource_id: str, 
                iot_hub_name: str, 
                key_name: str, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                time: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
                type_properties_ingress_start_at_type: Optional[Union[str, IngressStartAtType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.IoTHubEventSourceResourceProperties(IoTHubEventSourceCommonProperties):
        consumer_group_name: str
        creation_time: datetime
        event_source_resource_id: str
        iot_hub_name: str
        key_name: str
        local_timestamp: LocalTimestamp
        provisioning_state: Union[str, ProvisioningState]
        time: str
        timestamp_property_name: str
        type: Union[str, IngressStartAtType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                consumer_group_name: str, 
                event_source_resource_id: str, 
                iot_hub_name: str, 
                key_name: str, 
                local_timestamp: Optional[LocalTimestamp] = ..., 
                time: Optional[str] = ..., 
                timestamp_property_name: Optional[str] = ..., 
                type: Optional[Union[str, IngressStartAtType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.IoTHubEventSourceUpdateParameters(EventSourceUpdateParameters):
        kind: Union[str, EventSourceKind]
        shared_access_key: str
        tags: dict[str, str]
        timestamp_property_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                shared_access_key: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                timestamp_property_name: Optional[str] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.LocalTimestamp(Model):
        format: Union[str, LocalTimestampFormat]
        time_zone_offset: LocalTimestampTimeZoneOffset

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                format: Optional[Union[str, LocalTimestampFormat]] = ..., 
                time_zone_offset: Optional[LocalTimestampTimeZoneOffset] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.LocalTimestampFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMBEDDED = "Embedded"


    class azure.mgmt.timeseriesinsights.models.LocalTimestampTimeZoneOffset(Model):
        property_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                property_name: Optional[str] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.LogSpecification(Model):
        display_name: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.MetricAvailability(Model):
        blob_duration: str
        time_grain: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                time_grain: Optional[str] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.MetricSpecification(Model):
        aggregation_type: str
        availabilities: list[MetricAvailability]
        category: str
        dimensions: list[Dimension]
        display_description: str
        display_name: str
        name: str
        resource_id_dimension_name_override: str
        unit: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                availabilities: Optional[List[MetricAvailability]] = ..., 
                category: Optional[str] = ..., 
                dimensions: Optional[List[Dimension]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                resource_id_dimension_name_override: Optional[str] = ..., 
                unit: Optional[str] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.Operation(Model):
        display: OperationDisplay
        name: str
        origin: str
        service_specification: ServiceSpecification

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                origin: Optional[str] = ..., 
                service_specification: Optional[ServiceSpecification] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

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


    class azure.mgmt.timeseriesinsights.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

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


    class azure.mgmt.timeseriesinsights.models.PrivateEndpoint(Model):
        id: str

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


    class azure.mgmt.timeseriesinsights.models.PrivateEndpointConnection(Resource):
        group_ids: list[str]
        id: str
        name: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                group_ids: Optional[List[str]] = ..., 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.PrivateEndpointConnectionListResult(Model):
        value: list[PrivateEndpointConnection]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateEndpointConnection]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.timeseriesinsights.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.timeseriesinsights.models.PrivateLinkResource(Resource):
        group_id: str
        id: str
        name: str
        required_members: list[str]
        required_zone_names: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                required_zone_names: Optional[List[str]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.PrivateLinkResourceListResult(Model):
        value: list[PrivateLinkResource]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateLinkResource]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.PrivateLinkServiceConnectionState(Model):
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.PropertyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STRING = "String"


    class azure.mgmt.timeseriesinsights.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.timeseriesinsights.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.timeseriesinsights.models.ReferenceDataKeyPropertyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL = "Bool"
        DATE_TIME = "DateTime"
        DOUBLE = "Double"
        STRING = "String"


    class azure.mgmt.timeseriesinsights.models.ReferenceDataSetCreateOrUpdateParameters(CreateOrUpdateTrackedResourceProperties):
        data_string_comparison_behavior: Union[str, DataStringComparisonBehavior]
        key_properties: list[ReferenceDataSetKeyProperty]
        location: str
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_string_comparison_behavior: Optional[Union[str, DataStringComparisonBehavior]] = ..., 
                key_properties: List[ReferenceDataSetKeyProperty], 
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


    class azure.mgmt.timeseriesinsights.models.ReferenceDataSetCreationProperties(Model):
        data_string_comparison_behavior: Union[str, DataStringComparisonBehavior]
        key_properties: list[ReferenceDataSetKeyProperty]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_string_comparison_behavior: Optional[Union[str, DataStringComparisonBehavior]] = ..., 
                key_properties: List[ReferenceDataSetKeyProperty], 
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


    class azure.mgmt.timeseriesinsights.models.ReferenceDataSetKeyProperty(Model):
        name: str
        type: Union[str, ReferenceDataKeyPropertyType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, ReferenceDataKeyPropertyType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.ReferenceDataSetListResponse(Model):
        value: list[ReferenceDataSetResource]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ReferenceDataSetResource]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.ReferenceDataSetResource(TrackedResource):
        creation_time: datetime
        data_string_comparison_behavior: Union[str, DataStringComparisonBehavior]
        id: str
        key_properties: list[ReferenceDataSetKeyProperty]
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_string_comparison_behavior: Optional[Union[str, DataStringComparisonBehavior]] = ..., 
                key_properties: Optional[List[ReferenceDataSetKeyProperty]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.ReferenceDataSetResourceProperties(ReferenceDataSetCreationProperties, ResourceProperties):
        creation_time: datetime
        data_string_comparison_behavior: Union[str, DataStringComparisonBehavior]
        key_properties: list[ReferenceDataSetKeyProperty]
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_string_comparison_behavior: Optional[Union[str, DataStringComparisonBehavior]] = ..., 
                key_properties: List[ReferenceDataSetKeyProperty], 
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


    class azure.mgmt.timeseriesinsights.models.ReferenceDataSetUpdateParameters(Model):
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.timeseriesinsights.models.Resource(Model):
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


    class azure.mgmt.timeseriesinsights.models.ResourceProperties(Model):
        creation_time: datetime
        provisioning_state: Union[str, ProvisioningState]

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


    class azure.mgmt.timeseriesinsights.models.ServiceSpecification(Model):
        log_specifications: list[LogSpecification]
        metric_specifications: list[MetricSpecification]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                log_specifications: Optional[List[LogSpecification]] = ..., 
                metric_specifications: Optional[List[MetricSpecification]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.Sku(Model):
        capacity: int
        name: Union[str, SkuName]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity: int, 
                name: Union[str, SkuName], 
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


    class azure.mgmt.timeseriesinsights.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        L1 = "L1"
        P1 = "P1"
        S1 = "S1"
        S2 = "S2"


    class azure.mgmt.timeseriesinsights.models.StorageLimitExceededBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PAUSE_INGRESS = "PauseIngress"
        PURGE_OLD_DATA = "PurgeOldData"


    class azure.mgmt.timeseriesinsights.models.TimeSeriesIdProperty(Model):
        name: str
        type: Union[str, PropertyType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, PropertyType]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.TrackedResource(Resource):
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


    class azure.mgmt.timeseriesinsights.models.WarmStorageEnvironmentStatus(Model):
        current_count: int
        max_count: int
        state: Union[str, WarmStoragePropertiesState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                current_count: Optional[int] = ..., 
                max_count: Optional[int] = ..., 
                state: Optional[Union[str, WarmStoragePropertiesState]] = ..., 
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


    class azure.mgmt.timeseriesinsights.models.WarmStoragePropertiesState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        OK = "Ok"
        UNKNOWN = "Unknown"


    class azure.mgmt.timeseriesinsights.models.WarmStoreConfigurationProperties(Model):
        data_retention: timedelta

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_retention: timedelta, 
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


namespace azure.mgmt.timeseriesinsights.operations

    class azure.mgmt.timeseriesinsights.operations.AccessPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                access_policy_name: str, 
                parameters: AccessPolicyCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessPolicyResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                access_policy_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessPolicyResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                access_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                access_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AccessPolicyResource: ...

        @distributed_trace
        def list_by_environment(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AccessPolicyListResponse: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                access_policy_name: str, 
                access_policy_update_parameters: AccessPolicyUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessPolicyResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                access_policy_name: str, 
                access_policy_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessPolicyResource: ...


    class azure.mgmt.timeseriesinsights.operations.EnvironmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                parameters: EnvironmentCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnvironmentResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnvironmentResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_update_parameters: EnvironmentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnvironmentResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnvironmentResource]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentListResponse: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentListResponse: ...


    class azure.mgmt.timeseriesinsights.operations.EventSourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                event_source_name: str, 
                parameters: EventSourceCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventSourceResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                event_source_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventSourceResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                event_source_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                event_source_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EventSourceResource: ...

        @distributed_trace
        def list_by_environment(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EventSourceListResponse: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                event_source_name: str, 
                event_source_update_parameters: EventSourceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventSourceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                event_source_name: str, 
                event_source_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventSourceResource: ...


    class azure.mgmt.timeseriesinsights.operations.Operations:

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
            ) -> Iterable[Operation]: ...


    class azure.mgmt.timeseriesinsights.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_environment(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateEndpointConnectionListResult: ...


    class azure.mgmt.timeseriesinsights.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_supported(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PrivateLinkResource]: ...


    class azure.mgmt.timeseriesinsights.operations.ReferenceDataSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                reference_data_set_name: str, 
                parameters: ReferenceDataSetCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReferenceDataSetResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                reference_data_set_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReferenceDataSetResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                reference_data_set_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                reference_data_set_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ReferenceDataSetResource: ...

        @distributed_trace
        def list_by_environment(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ReferenceDataSetListResponse: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                reference_data_set_name: str, 
                reference_data_set_update_parameters: ReferenceDataSetUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReferenceDataSetResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                reference_data_set_name: str, 
                reference_data_set_update_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReferenceDataSetResource: ...


```