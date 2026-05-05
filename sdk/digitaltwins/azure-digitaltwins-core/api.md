```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.digitaltwins.core

    class azure.digitaltwins.core.DigitalTwinsClient:

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def create_models(
                self, 
                dtdl_models: List[MutableMapping[str, Any]], 
                **kwargs: Any
            ) -> List[DigitalTwinsModelData]: ...

        @distributed_trace
        def decommission_model(
                self, 
                model_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_digital_twin(
                self, 
                digital_twin_id: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_event_route(
                self, 
                event_route_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_model(
                self, 
                model_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_relationship(
                self, 
                digital_twin_id: str, 
                relationship_id: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_component(
                self, 
                digital_twin_id: str, 
                component_name: str, 
                **kwargs: Any
            ) -> MutableMapping[str, Any]: ...

        @distributed_trace
        def get_digital_twin(
                self, 
                digital_twin_id: str, 
                **kwargs: Any
            ) -> MutableMapping[str, Any]: ...

        @distributed_trace
        def get_event_route(
                self, 
                event_route_id: str, 
                **kwargs: Any
            ) -> DigitalTwinsEventRoute: ...

        @distributed_trace
        def get_model(
                self, 
                model_id: str, 
                *, 
                include_model_definition: Optional[bool] = ..., 
                **kwargs: Any
            ) -> DigitalTwinsModelData: ...

        @distributed_trace
        def get_relationship(
                self, 
                digital_twin_id: str, 
                relationship_id: str, 
                **kwargs: Any
            ) -> MutableMapping[str, Any]: ...

        @distributed_trace
        def list_event_routes(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DigitalTwinsEventRoute]: ...

        @distributed_trace
        def list_incoming_relationships(
                self, 
                digital_twin_id: str, 
                **kwargs: Any
            ) -> ItemPaged[IncomingRelationship]: ...

        @distributed_trace
        def list_models(
                self, 
                dependencies_for: Optional[List[str]] = None, 
                *, 
                include_model_definition: Optional[bool] = ..., 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DigitalTwinsModelData]: ...

        @distributed_trace
        def list_relationships(
                self, 
                digital_twin_id: str, 
                relationship_id: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[MutableMapping[str, Any]]: ...

        @distributed_trace
        def publish_component_telemetry(
                self, 
                digital_twin_id: str, 
                component_name: str, 
                telemetry: MutableMapping[str, Any], 
                *, 
                message_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def publish_telemetry(
                self, 
                digital_twin_id: str, 
                telemetry: MutableMapping[str, Any], 
                *, 
                message_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def query_twins(
                self, 
                query_expression: str, 
                **kwargs: Any
            ) -> ItemPaged[MutableMapping[str, Any]]: ...

        @distributed_trace
        def update_component(
                self, 
                digital_twin_id: str, 
                component_name: str, 
                json_patch: Sequence[MutableMapping[str, Any]], 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_digital_twin(
                self, 
                digital_twin_id: str, 
                json_patch: Sequence[MutableMapping[str, Any]], 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_relationship(
                self, 
                digital_twin_id: str, 
                relationship_id: str, 
                json_patch: Sequence[MutableMapping[str, Any]], 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def upsert_digital_twin(
                self, 
                digital_twin_id: str, 
                digital_twin: Dict[str, object], 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> MutableMapping[str, Any]: ...

        @distributed_trace
        def upsert_event_route(
                self, 
                event_route_id: str, 
                event_route: DigitalTwinsEventRoute, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def upsert_relationship(
                self, 
                digital_twin_id: str, 
                relationship_id: str, 
                relationship: Dict[str, object], 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> MutableMapping[str, Any]: ...


    class azure.digitaltwins.core.DigitalTwinsEventRoute(Model):
        endpoint_name: str
        filter: str
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint_name: str, 
                filter: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.digitaltwins.core.DigitalTwinsModelData(Model):
        decommissioned: bool
        description: dict[str, str]
        display_name: dict[str, str]
        id: str
        model: JSON
        upload_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                decommissioned: bool = False, 
                description: Optional[Dict[str, str]] = ..., 
                display_name: Optional[Dict[str, str]] = ..., 
                id: str, 
                model: Optional[JSON] = ..., 
                upload_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


    class azure.digitaltwins.core.IncomingRelationship(Model):
        relationship_id: str
        relationship_link: str
        relationship_name: str
        source_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                relationship_id: Optional[str] = ..., 
                relationship_link: Optional[str] = ..., 
                relationship_name: Optional[str] = ..., 
                source_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

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


namespace azure.digitaltwins.core.aio

    class azure.digitaltwins.core.aio.DigitalTwinsClient: implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                **kwargs
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_models(
                self, 
                dtdl_models: List[MutableMapping[str, Any]], 
                **kwargs
            ) -> List[DigitalTwinsModelData]: ...

        @distributed_trace_async
        async def decommission_model(
                self, 
                model_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete_digital_twin(
                self, 
                digital_twin_id: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete_event_route(
                self, 
                event_route_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete_model(
                self, 
                model_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete_relationship(
                self, 
                digital_twin_id: str, 
                relationship_id: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_component(
                self, 
                digital_twin_id: str, 
                component_name: str, 
                **kwargs
            ) -> MutableMapping[str, Any]: ...

        @distributed_trace_async
        async def get_digital_twin(
                self, 
                digital_twin_id: str, 
                **kwargs
            ) -> MutableMapping[str, Any]: ...

        @distributed_trace_async
        async def get_event_route(
                self, 
                event_route_id: str, 
                **kwargs
            ) -> DigitalTwinsEventRoute: ...

        @distributed_trace_async
        async def get_model(
                self, 
                model_id: str, 
                *, 
                include_model_definition: Optional[bool] = ..., 
                **kwargs
            ) -> DigitalTwinsModelData: ...

        @distributed_trace_async
        async def get_relationship(
                self, 
                digital_twin_id: str, 
                relationship_id: str, 
                **kwargs
            ) -> MutableMapping[str, Any]: ...

        @distributed_trace
        def list_event_routes(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs
            ) -> AsyncItemPaged[DigitalTwinsEventRoute]: ...

        @distributed_trace
        def list_incoming_relationships(
                self, 
                digital_twin_id: str, 
                **kwargs
            ) -> AsyncItemPaged[IncomingRelationship]: ...

        @distributed_trace
        def list_models(
                self, 
                dependencies_for: Optional[List[str]] = None, 
                *, 
                include_model_definition: Optional[bool] = ..., 
                results_per_page: Optional[int] = ..., 
                **kwargs
            ) -> AsyncItemPaged[DigitalTwinsModelData]: ...

        @distributed_trace
        def list_relationships(
                self, 
                digital_twin_id: str, 
                relationship_id: Optional[str] = None, 
                **kwargs
            ) -> AsyncItemPaged[MutableMapping[str, Any]]: ...

        @distributed_trace_async
        async def publish_component_telemetry(
                self, 
                digital_twin_id: str, 
                component_name: str, 
                telemetry: MutableMapping[str, Any], 
                *, 
                message_id: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def publish_telemetry(
                self, 
                digital_twin_id: str, 
                telemetry: MutableMapping[str, Any], 
                *, 
                message_id: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def query_twins(
                self, 
                query_expression: str, 
                **kwargs
            ) -> AsyncItemPaged[Dict[str, object]]: ...

        @distributed_trace_async
        async def update_component(
                self, 
                digital_twin_id: str, 
                component_name: str, 
                json_patch: Sequence[MutableMapping[str, Any]], 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def update_digital_twin(
                self, 
                digital_twin_id: str, 
                json_patch: Sequence[MutableMapping[str, Any]], 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def update_relationship(
                self, 
                digital_twin_id: str, 
                relationship_id: str, 
                json_patch: Sequence[MutableMapping[str, Any]], 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def upsert_digital_twin(
                self, 
                digital_twin_id: str, 
                digital_twin: Dict[str, object], 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs
            ) -> MutableMapping[str, Any]: ...

        @distributed_trace_async
        async def upsert_event_route(
                self, 
                event_route_id: str, 
                event_route: DigitalTwinsEventRoute, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def upsert_relationship(
                self, 
                digital_twin_id: str, 
                relationship_id: str, 
                relationship: Dict[str, object], 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs
            ) -> MutableMapping[str, Any]: ...


```