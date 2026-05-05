```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.purview.datamap

    class azure.purview.datamap.DataMapClient: implements ContextManager 
        discovery: DiscoveryOperations
        entity: EntityOperations
        glossary: GlossaryOperations
        lineage: LineageOperations
        relationship: RelationshipOperations
        type_definition: TypeDefinitionOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
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


namespace azure.purview.datamap.aio

    class azure.purview.datamap.aio.DataMapClient: implements AsyncContextManager 
        discovery: DiscoveryOperations
        entity: EntityOperations
        glossary: GlossaryOperations
        lineage: LineageOperations
        relationship: RelationshipOperations
        type_definition: TypeDefinitionOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
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


namespace azure.purview.datamap.aio.operations

    class azure.purview.datamap.aio.operations.DiscoveryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def auto_complete(
                self, 
                body: AutoCompleteOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoCompleteResult: ...

        @overload
        async def auto_complete(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoCompleteResult: ...

        @overload
        async def auto_complete(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoCompleteResult: ...

        @overload
        async def query(
                self, 
                body: QueryOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResult: ...

        @overload
        async def query(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResult: ...

        @overload
        async def query(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResult: ...

        @overload
        async def suggest(
                self, 
                body: SuggestOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuggestResult: ...

        @overload
        async def suggest(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuggestResult: ...

        @overload
        async def suggest(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuggestResult: ...


    class azure.purview.datamap.aio.operations.EntityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add_classification(
                self, 
                body: ClassificationAssociateOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_classification(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_classification(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_classifications(
                self, 
                guid: str, 
                body: List[AtlasClassification], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_classifications(
                self, 
                guid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_classifications_by_unique_attribute(
                self, 
                type_name: str, 
                body: List[AtlasClassification], 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_classifications_by_unique_attribute(
                self, 
                type_name: str, 
                body: IO[bytes], 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_label(
                self, 
                guid: str, 
                body: Optional[List[str]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_label(
                self, 
                guid: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_labels_by_unique_attribute(
                self, 
                type_name: str, 
                body: Optional[List[str]] = None, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_labels_by_unique_attribute(
                self, 
                type_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_or_update_business_metadata(
                self, 
                guid: str, 
                body: Dict[str, Dict[str, Any]], 
                *, 
                content_type: str = "application/json", 
                overwrite: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_or_update_business_metadata(
                self, 
                guid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                overwrite: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_or_update_business_metadata_attributes(
                self, 
                business_metadata_name: str, 
                guid: str, 
                body: Dict[str, Any], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_or_update_business_metadata_attributes(
                self, 
                business_metadata_name: str, 
                guid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def batch_create_or_update(
                self, 
                body: AtlasEntitiesWithExtInfo, 
                *, 
                business_attribute_update_behavior: Optional[Union[str, BusinessAttributeUpdateBehavior]] = ..., 
                collection_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        async def batch_create_or_update(
                self, 
                body: JSON, 
                *, 
                business_attribute_update_behavior: Optional[Union[str, BusinessAttributeUpdateBehavior]] = ..., 
                collection_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        async def batch_create_or_update(
                self, 
                body: IO[bytes], 
                *, 
                business_attribute_update_behavior: Optional[Union[str, BusinessAttributeUpdateBehavior]] = ..., 
                collection_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @distributed_trace_async
        async def batch_delete(
                self, 
                *, 
                guid: List[str], 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @distributed_trace_async
        async def batch_get_by_unique_attributes(
                self, 
                type_name: str, 
                *, 
                attr_n_qualified_name: Optional[str] = ..., 
                ignore_relationships: Optional[bool] = ..., 
                min_ext_info: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasEntitiesWithExtInfo: ...

        @overload
        async def batch_set_classifications(
                self, 
                body: AtlasEntityHeaders, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[str]: ...

        @overload
        async def batch_set_classifications(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[str]: ...

        @overload
        async def batch_set_classifications(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[str]: ...

        @overload
        async def create_or_update(
                self, 
                body: AtlasEntityWithExtInfo, 
                *, 
                business_attribute_update_behavior: Optional[Union[str, BusinessAttributeUpdateBehavior]] = ..., 
                collection_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        async def create_or_update(
                self, 
                body: JSON, 
                *, 
                business_attribute_update_behavior: Optional[Union[str, BusinessAttributeUpdateBehavior]] = ..., 
                collection_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        async def create_or_update(
                self, 
                body: IO[bytes], 
                *, 
                business_attribute_update_behavior: Optional[Union[str, BusinessAttributeUpdateBehavior]] = ..., 
                collection_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @distributed_trace_async
        async def delete(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @distributed_trace_async
        async def delete_by_unique_attribute(
                self, 
                type_name: str, 
                *, 
                attribute: Optional[str] = ..., 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @distributed_trace_async
        async def get(
                self, 
                guid: str, 
                *, 
                ignore_relationships: Optional[bool] = ..., 
                min_ext_info: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasEntityWithExtInfo: ...

        @distributed_trace_async
        async def get_business_metadata_template(self, **kwargs: Any) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_by_ids(
                self, 
                *, 
                guid: List[str], 
                ignore_relationships: Optional[bool] = ..., 
                min_ext_info: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasEntitiesWithExtInfo: ...

        @distributed_trace_async
        async def get_by_unique_attribute(
                self, 
                type_name: str, 
                *, 
                attribute: Optional[str] = ..., 
                ignore_relationships: Optional[bool] = ..., 
                min_ext_info: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasEntityWithExtInfo: ...

        @distributed_trace_async
        async def get_classification(
                self, 
                guid: str, 
                classification_name: str, 
                **kwargs: Any
            ) -> AtlasClassification: ...

        @distributed_trace_async
        async def get_classifications(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasClassifications: ...

        @distributed_trace_async
        async def get_header(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasEntityHeader: ...

        @overload
        async def import_business_metadata(
                self, 
                body: BusinessMetadataOptions, 
                **kwargs: Any
            ) -> BulkImportResult: ...

        @overload
        async def import_business_metadata(
                self, 
                body: JSON, 
                **kwargs: Any
            ) -> BulkImportResult: ...

        @overload
        async def move_entities_to_collection(
                self, 
                body: MoveEntitiesOptions, 
                *, 
                collection_id: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        async def move_entities_to_collection(
                self, 
                body: JSON, 
                *, 
                collection_id: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        async def move_entities_to_collection(
                self, 
                body: IO[bytes], 
                *, 
                collection_id: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        async def remove_business_metadata(
                self, 
                guid: str, 
                body: Dict[str, Dict[str, Any]], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def remove_business_metadata(
                self, 
                guid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def remove_business_metadata_attributes(
                self, 
                business_metadata_name: str, 
                guid: str, 
                body: Dict[str, Any], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def remove_business_metadata_attributes(
                self, 
                business_metadata_name: str, 
                guid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def remove_classification(
                self, 
                guid: str, 
                classification_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def remove_classification_by_unique_attribute(
                self, 
                type_name: str, 
                classification_name: str, 
                *, 
                attribute: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def remove_labels(
                self, 
                guid: str, 
                body: Optional[List[str]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def remove_labels(
                self, 
                guid: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def remove_labels_by_unique_attribute(
                self, 
                type_name: str, 
                body: Optional[List[str]] = None, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def remove_labels_by_unique_attribute(
                self, 
                type_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set_labels(
                self, 
                guid: str, 
                body: Optional[List[str]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set_labels(
                self, 
                guid: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set_labels_by_unique_attribute(
                self, 
                type_name: str, 
                body: Optional[List[str]] = None, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set_labels_by_unique_attribute(
                self, 
                type_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update_attribute_by_id(
                self, 
                guid: str, 
                body: Any, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        async def update_by_unique_attribute(
                self, 
                type_name: str, 
                body: AtlasEntityWithExtInfo, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        async def update_by_unique_attribute(
                self, 
                type_name: str, 
                body: JSON, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        async def update_by_unique_attribute(
                self, 
                type_name: str, 
                body: IO[bytes], 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        async def update_classifications(
                self, 
                guid: str, 
                body: List[AtlasClassification], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_classifications(
                self, 
                guid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_classifications_unique_by_attribute(
                self, 
                type_name: str, 
                body: List[AtlasClassification], 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_classifications_unique_by_attribute(
                self, 
                type_name: str, 
                body: IO[bytes], 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.purview.datamap.aio.operations.GlossaryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def assign_term_to_entities(
                self, 
                term_id: str, 
                body: List[AtlasRelatedObjectId], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def assign_term_to_entities(
                self, 
                term_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def batch_get(
                self, 
                *, 
                ignore_terms_and_categories: Optional[bool] = ..., 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasGlossary]: ...

        @overload
        async def create(
                self, 
                body: AtlasGlossary, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        async def create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        async def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        async def create_categories(
                self, 
                body: List[AtlasGlossaryCategory], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[AtlasGlossaryCategory]: ...

        @overload
        async def create_categories(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[AtlasGlossaryCategory]: ...

        @overload
        async def create_category(
                self, 
                body: AtlasGlossaryCategory, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        async def create_category(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        async def create_category(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        async def create_term(
                self, 
                body: AtlasGlossaryTerm, 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        async def create_term(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        async def create_term(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        async def create_terms(
                self, 
                body: List[AtlasGlossaryTerm], 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[AtlasGlossaryTerm]: ...

        @overload
        async def create_terms(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[AtlasGlossaryTerm]: ...

        @distributed_trace_async
        async def delete(
                self, 
                glossary_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_category(
                self, 
                category_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_term(
                self, 
                term_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def delete_term_assignment_from_entities(
                self, 
                term_id: str, 
                body: List[AtlasRelatedObjectId], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def delete_term_assignment_from_entities(
                self, 
                term_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                glossary_id: str, 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @distributed_trace_async
        async def get_categories(
                self, 
                glossary_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasGlossaryCategory]: ...

        @distributed_trace_async
        async def get_categories_headers(
                self, 
                glossary_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasRelatedCategoryHeader]: ...

        @distributed_trace_async
        async def get_category(
                self, 
                category_id: str, 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @distributed_trace_async
        async def get_category_terms(
                self, 
                category_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasRelatedTermHeader]: ...

        @distributed_trace_async
        async def get_detailed(
                self, 
                glossary_id: str, 
                **kwargs: Any
            ) -> AtlasGlossaryExtInfo: ...

        @distributed_trace_async
        async def get_entities_assigned_with_term(
                self, 
                term_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasRelatedObjectId]: ...

        @distributed_trace_async
        async def get_related_categories(
                self, 
                category_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, List[AtlasRelatedCategoryHeader]]: ...

        @distributed_trace_async
        async def get_related_terms(
                self, 
                term_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, List[AtlasRelatedTermHeader]]: ...

        @distributed_trace_async
        async def get_term(
                self, 
                term_id: str, 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @distributed_trace_async
        async def get_term_headers(
                self, 
                glossary_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasRelatedTermHeader]: ...

        @distributed_trace_async
        async def get_terms(
                self, 
                glossary_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasGlossaryTerm]: ...

        @overload
        async def partial_update(
                self, 
                glossary_id: str, 
                body: Dict[str, str], 
                *, 
                content_type: str = "application/json", 
                ignore_terms_and_categories: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        async def partial_update(
                self, 
                glossary_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                ignore_terms_and_categories: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        async def partial_update_category(
                self, 
                category_id: str, 
                body: Dict[str, str], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        async def partial_update_category(
                self, 
                category_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        async def partial_update_term(
                self, 
                term_id: str, 
                body: Dict[str, str], 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        async def partial_update_term(
                self, 
                term_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        async def update(
                self, 
                glossary_id: str, 
                body: AtlasGlossary, 
                *, 
                content_type: str = "application/json", 
                ignore_terms_and_categories: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        async def update(
                self, 
                glossary_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                ignore_terms_and_categories: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        async def update(
                self, 
                glossary_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                ignore_terms_and_categories: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        async def update_category(
                self, 
                category_id: str, 
                body: AtlasGlossaryCategory, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        async def update_category(
                self, 
                category_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        async def update_category(
                self, 
                category_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        async def update_term(
                self, 
                term_id: str, 
                body: AtlasGlossaryTerm, 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        async def update_term(
                self, 
                term_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        async def update_term(
                self, 
                term_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...


    class azure.purview.datamap.aio.operations.LineageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                guid: str, 
                *, 
                depth: Optional[int] = ..., 
                direction: Union[str, LineageDirection], 
                **kwargs: Any
            ) -> AtlasLineageInfo: ...

        @distributed_trace_async
        async def get_by_unique_attribute(
                self, 
                type_name: str, 
                *, 
                attribute: Optional[str] = ..., 
                depth: Optional[int] = ..., 
                direction: Union[str, LineageDirection], 
                **kwargs: Any
            ) -> AtlasLineageInfo: ...

        @distributed_trace_async
        async def get_next_page(
                self, 
                guid: str, 
                *, 
                direction: Union[str, LineageDirection], 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                **kwargs: Any
            ) -> AtlasLineageInfo: ...


    class azure.purview.datamap.aio.operations.RelationshipOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                body: AtlasRelationship, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasRelationship: ...

        @overload
        async def create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasRelationship: ...

        @overload
        async def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasRelationship: ...

        @distributed_trace_async
        async def delete(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                guid: str, 
                *, 
                extended_info: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasRelationshipWithExtInfo: ...

        @overload
        async def update(
                self, 
                body: AtlasRelationship, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasRelationship: ...

        @overload
        async def update(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasRelationship: ...

        @overload
        async def update(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasRelationship: ...


    class azure.purview.datamap.aio.operations.TypeDefinitionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def batch_create(
                self, 
                body: AtlasTypesDef, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @overload
        async def batch_create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @overload
        async def batch_create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @overload
        async def batch_delete(
                self, 
                body: AtlasTypesDef, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def batch_delete(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def batch_delete(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def batch_update(
                self, 
                body: AtlasTypesDef, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @overload
        async def batch_update(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @overload
        async def batch_update(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                *, 
                include_term_template: Optional[bool] = ..., 
                type: Optional[Union[str, TypeCategory]] = ..., 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @distributed_trace_async
        async def get_business_metadata_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasBusinessMetadataDef: ...

        @distributed_trace_async
        async def get_business_metadata_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasBusinessMetadataDef: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasTypeDef: ...

        @distributed_trace_async
        async def get_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasTypeDef: ...

        @distributed_trace_async
        async def get_classification_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasClassificationDef: ...

        @distributed_trace_async
        async def get_classification_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasClassificationDef: ...

        @distributed_trace_async
        async def get_entity_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasEntityDef: ...

        @distributed_trace_async
        async def get_entity_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasEntityDef: ...

        @distributed_trace_async
        async def get_enum_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasEnumDef: ...

        @distributed_trace_async
        async def get_enum_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasEnumDef: ...

        @distributed_trace_async
        async def get_headers(
                self, 
                *, 
                include_term_template: Optional[bool] = ..., 
                type: Optional[Union[str, TypeCategory]] = ..., 
                **kwargs: Any
            ) -> List[AtlasTypeDefHeader]: ...

        @distributed_trace_async
        async def get_relationship_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasRelationshipDef: ...

        @distributed_trace_async
        async def get_relationship_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasRelationshipDef: ...

        @distributed_trace_async
        async def get_struct_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasStructDef: ...

        @distributed_trace_async
        async def get_struct_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasStructDef: ...

        @distributed_trace_async
        async def get_term_template_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> TermTemplateDef: ...

        @distributed_trace_async
        async def get_term_template_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> TermTemplateDef: ...


namespace azure.purview.datamap.models

    class azure.purview.datamap.models.AtlasAttributeDef(Model):
        cardinality: Optional[Union[str, CardinalityValue]]
        constraints: Optional[List[AtlasConstraintDef]]
        default_value: Optional[str]
        description: Optional[str]
        include_in_notification: Optional[bool]
        is_indexable: Optional[bool]
        is_optional: Optional[bool]
        is_unique: Optional[bool]
        name: Optional[str]
        options: Optional[Dict[str, str]]
        type_name: Optional[str]
        values_max_count: Optional[int]
        values_min_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cardinality: Optional[Union[str, CardinalityValue]] = ..., 
                constraints: Optional[List[AtlasConstraintDef]] = ..., 
                default_value: Optional[str] = ..., 
                description: Optional[str] = ..., 
                include_in_notification: Optional[bool] = ..., 
                is_indexable: Optional[bool] = ..., 
                is_optional: Optional[bool] = ..., 
                is_unique: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                options: Optional[Dict[str, str]] = ..., 
                type_name: Optional[str] = ..., 
                values_max_count: Optional[int] = ..., 
                values_min_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasBusinessMetadataDef(Model):
        attribute_defs: Optional[List[AtlasAttributeDef]]
        category: Optional[Union[str, TypeCategory]]
        create_time: Optional[int]
        created_by: Optional[str]
        date_formatter: Optional[DateFormat]
        description: Optional[str]
        guid: Optional[str]
        last_modified_ts: Optional[str]
        name: Optional[str]
        options: Optional[Dict[str, str]]
        service_type: Optional[str]
        type_version: Optional[str]
        update_time: Optional[int]
        updated_by: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                attribute_defs: Optional[List[AtlasAttributeDef]] = ..., 
                category: Optional[Union[str, TypeCategory]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                date_formatter: Optional[DateFormat] = ..., 
                description: Optional[str] = ..., 
                guid: Optional[str] = ..., 
                last_modified_ts: Optional[str] = ..., 
                name: Optional[str] = ..., 
                options: Optional[Dict[str, str]] = ..., 
                service_type: Optional[str] = ..., 
                type_version: Optional[str] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasClassification(Model):
        attributes: Optional[Dict[str, Any]]
        entity_guid: Optional[str]
        entity_status: Optional[Union[str, EntityStatus]]
        last_modified_ts: Optional[str]
        remove_propagations_on_entity_delete: Optional[bool]
        type_name: Optional[str]
        validity_periods: Optional[List[TimeBoundary]]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[Dict[str, Any]] = ..., 
                entity_guid: Optional[str] = ..., 
                entity_status: Optional[Union[str, EntityStatus]] = ..., 
                last_modified_ts: Optional[str] = ..., 
                remove_propagations_on_entity_delete: Optional[bool] = ..., 
                type_name: Optional[str] = ..., 
                validity_periods: Optional[List[TimeBoundary]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasClassificationDef(Model):
        attribute_defs: Optional[List[AtlasAttributeDef]]
        category: Optional[Union[str, TypeCategory]]
        create_time: Optional[int]
        created_by: Optional[str]
        date_formatter: Optional[DateFormat]
        description: Optional[str]
        entity_types: Optional[List[str]]
        guid: Optional[str]
        last_modified_ts: Optional[str]
        name: Optional[str]
        options: Optional[Dict[str, str]]
        service_type: Optional[str]
        sub_types: Optional[List[str]]
        super_types: Optional[List[str]]
        type_version: Optional[str]
        update_time: Optional[int]
        updated_by: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                attribute_defs: Optional[List[AtlasAttributeDef]] = ..., 
                category: Optional[Union[str, TypeCategory]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                date_formatter: Optional[DateFormat] = ..., 
                description: Optional[str] = ..., 
                entity_types: Optional[List[str]] = ..., 
                guid: Optional[str] = ..., 
                last_modified_ts: Optional[str] = ..., 
                name: Optional[str] = ..., 
                options: Optional[Dict[str, str]] = ..., 
                service_type: Optional[str] = ..., 
                sub_types: Optional[List[str]] = ..., 
                super_types: Optional[List[str]] = ..., 
                type_version: Optional[str] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasClassifications(Model):
        list: Optional[List[Any]]
        page_size: Optional[int]
        sort_by: Optional[str]
        sort_type: Optional[Union[str, SortType]]
        start_index: Optional[int]
        total_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                list: Optional[List[Any]] = ..., 
                page_size: Optional[int] = ..., 
                sort_by: Optional[str] = ..., 
                sort_type: Optional[Union[str, SortType]] = ..., 
                start_index: Optional[int] = ..., 
                total_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasConstraintDef(Model):
        params: Optional[Dict[str, Any]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                params: Optional[Dict[str, Any]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasEntitiesWithExtInfo(Model):
        entities: Optional[List[AtlasEntity]]
        referred_entities: Optional[Dict[str, AtlasEntity]]

        @overload
        def __init__(
                self, 
                *, 
                entities: Optional[List[AtlasEntity]] = ..., 
                referred_entities: Optional[Dict[str, AtlasEntity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasEntity(Model):
        attributes: Optional[Dict[str, Any]]
        business_attributes: Optional[Dict[str, Any]]
        classifications: Optional[List[AtlasClassification]]
        collection_id: Optional[str]
        contacts: Optional[Dict[str, List[ContactInfo]]]
        create_time: Optional[int]
        created_by: Optional[str]
        custom_attributes: Optional[Dict[str, str]]
        guid: Optional[str]
        home_id: Optional[str]
        is_incomplete: Optional[bool]
        labels: Optional[List[str]]
        last_modified_ts: Optional[str]
        meanings: Optional[List[AtlasTermAssignmentHeader]]
        provenance_type: Optional[int]
        proxy: Optional[bool]
        relationship_attributes: Optional[Dict[str, Any]]
        status: Optional[Union[str, EntityStatus]]
        type_name: Optional[str]
        update_time: Optional[int]
        updated_by: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[Dict[str, Any]] = ..., 
                business_attributes: Optional[Dict[str, Any]] = ..., 
                classifications: Optional[List[AtlasClassification]] = ..., 
                contacts: Optional[Dict[str, List[ContactInfo]]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                custom_attributes: Optional[Dict[str, str]] = ..., 
                guid: Optional[str] = ..., 
                home_id: Optional[str] = ..., 
                is_incomplete: Optional[bool] = ..., 
                labels: Optional[List[str]] = ..., 
                last_modified_ts: Optional[str] = ..., 
                meanings: Optional[List[AtlasTermAssignmentHeader]] = ..., 
                provenance_type: Optional[int] = ..., 
                proxy: Optional[bool] = ..., 
                relationship_attributes: Optional[Dict[str, Any]] = ..., 
                status: Optional[Union[str, EntityStatus]] = ..., 
                type_name: Optional[str] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasEntityDef(Model):
        attribute_defs: Optional[List[AtlasAttributeDef]]
        category: Optional[Union[str, TypeCategory]]
        create_time: Optional[int]
        created_by: Optional[str]
        date_formatter: Optional[DateFormat]
        description: Optional[str]
        guid: Optional[str]
        last_modified_ts: Optional[str]
        name: Optional[str]
        options: Optional[Dict[str, str]]
        relationship_attribute_defs: Optional[List[AtlasRelationshipAttributeDef]]
        service_type: Optional[str]
        sub_types: Optional[List[str]]
        super_types: Optional[List[str]]
        type_version: Optional[str]
        update_time: Optional[int]
        updated_by: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                attribute_defs: Optional[List[AtlasAttributeDef]] = ..., 
                category: Optional[Union[str, TypeCategory]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                date_formatter: Optional[DateFormat] = ..., 
                description: Optional[str] = ..., 
                guid: Optional[str] = ..., 
                last_modified_ts: Optional[str] = ..., 
                name: Optional[str] = ..., 
                options: Optional[Dict[str, str]] = ..., 
                relationship_attribute_defs: Optional[List[AtlasRelationshipAttributeDef]] = ..., 
                service_type: Optional[str] = ..., 
                sub_types: Optional[List[str]] = ..., 
                super_types: Optional[List[str]] = ..., 
                type_version: Optional[str] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasEntityHeader(Model):
        attributes: Optional[Dict[str, Any]]
        classification_names: Optional[List[str]]
        classifications: Optional[List[AtlasClassification]]
        display_text: Optional[str]
        guid: Optional[str]
        is_incomplete: Optional[bool]
        labels: Optional[List[str]]
        last_modified_ts: Optional[str]
        meaning_names: Optional[List[str]]
        meanings: Optional[List[AtlasTermAssignmentHeader]]
        status: Optional[Union[str, EntityStatus]]
        type_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[Dict[str, Any]] = ..., 
                classification_names: Optional[List[str]] = ..., 
                classifications: Optional[List[AtlasClassification]] = ..., 
                display_text: Optional[str] = ..., 
                guid: Optional[str] = ..., 
                is_incomplete: Optional[bool] = ..., 
                labels: Optional[List[str]] = ..., 
                last_modified_ts: Optional[str] = ..., 
                meaning_names: Optional[List[str]] = ..., 
                meanings: Optional[List[AtlasTermAssignmentHeader]] = ..., 
                status: Optional[Union[str, EntityStatus]] = ..., 
                type_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasEntityHeaders(Model):
        guid_header_map: Optional[Dict[str, AtlasEntityHeader]]

        @overload
        def __init__(
                self, 
                *, 
                guid_header_map: Optional[Dict[str, AtlasEntityHeader]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasEntityWithExtInfo(Model):
        entity: Optional[AtlasEntity]
        referred_entities: Optional[Dict[str, AtlasEntity]]

        @overload
        def __init__(
                self, 
                *, 
                entity: Optional[AtlasEntity] = ..., 
                referred_entities: Optional[Dict[str, AtlasEntity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasEnumDef(Model):
        category: Optional[Union[str, TypeCategory]]
        create_time: Optional[int]
        created_by: Optional[str]
        date_formatter: Optional[DateFormat]
        default_value: Optional[str]
        description: Optional[str]
        element_defs: Optional[List[AtlasEnumElementDef]]
        guid: Optional[str]
        last_modified_ts: Optional[str]
        name: Optional[str]
        options: Optional[Dict[str, str]]
        service_type: Optional[str]
        type_version: Optional[str]
        update_time: Optional[int]
        updated_by: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, TypeCategory]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                date_formatter: Optional[DateFormat] = ..., 
                default_value: Optional[str] = ..., 
                description: Optional[str] = ..., 
                element_defs: Optional[List[AtlasEnumElementDef]] = ..., 
                guid: Optional[str] = ..., 
                last_modified_ts: Optional[str] = ..., 
                name: Optional[str] = ..., 
                options: Optional[Dict[str, str]] = ..., 
                service_type: Optional[str] = ..., 
                type_version: Optional[str] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasEnumElementDef(Model):
        description: Optional[str]
        ordinal: Optional[int]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                ordinal: Optional[int] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasErrorResponse(Model):
        error_code: Optional[str]
        error_message: Optional[str]
        request_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                request_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasGlossary(Model):
        categories: Optional[List[AtlasRelatedCategoryHeader]]
        classifications: Optional[List[AtlasClassification]]
        create_time: Optional[int]
        created_by: Optional[str]
        guid: Optional[str]
        language: Optional[str]
        last_modified_ts: Optional[str]
        long_description: Optional[str]
        name: Optional[str]
        qualified_name: Optional[str]
        short_description: Optional[str]
        terms: Optional[List[AtlasRelatedTermHeader]]
        update_time: Optional[int]
        updated_by: Optional[str]
        usage: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                categories: Optional[List[AtlasRelatedCategoryHeader]] = ..., 
                classifications: Optional[List[AtlasClassification]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                guid: Optional[str] = ..., 
                language: Optional[str] = ..., 
                last_modified_ts: Optional[str] = ..., 
                long_description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                qualified_name: Optional[str] = ..., 
                short_description: Optional[str] = ..., 
                terms: Optional[List[AtlasRelatedTermHeader]] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                usage: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasGlossaryCategory(Model):
        anchor: Optional[AtlasGlossaryHeader]
        children_categories: Optional[List[AtlasRelatedCategoryHeader]]
        classifications: Optional[List[AtlasClassification]]
        create_time: Optional[int]
        created_by: Optional[str]
        guid: Optional[str]
        last_modified_ts: Optional[str]
        long_description: Optional[str]
        name: Optional[str]
        parent_category: Optional[AtlasRelatedCategoryHeader]
        qualified_name: Optional[str]
        short_description: Optional[str]
        terms: Optional[List[AtlasRelatedTermHeader]]
        update_time: Optional[int]
        updated_by: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                anchor: Optional[AtlasGlossaryHeader] = ..., 
                children_categories: Optional[List[AtlasRelatedCategoryHeader]] = ..., 
                classifications: Optional[List[AtlasClassification]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                guid: Optional[str] = ..., 
                last_modified_ts: Optional[str] = ..., 
                long_description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                parent_category: Optional[AtlasRelatedCategoryHeader] = ..., 
                qualified_name: Optional[str] = ..., 
                short_description: Optional[str] = ..., 
                terms: Optional[List[AtlasRelatedTermHeader]] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasGlossaryExtInfo(Model):
        categories: Optional[List[AtlasRelatedCategoryHeader]]
        category_info: Optional[Dict[str, AtlasGlossaryCategory]]
        classifications: Optional[List[AtlasClassification]]
        create_time: Optional[int]
        created_by: Optional[str]
        guid: Optional[str]
        language: Optional[str]
        last_modified_ts: Optional[str]
        long_description: Optional[str]
        name: Optional[str]
        qualified_name: Optional[str]
        short_description: Optional[str]
        term_info: Optional[Dict[str, AtlasGlossaryTerm]]
        terms: Optional[List[AtlasRelatedTermHeader]]
        update_time: Optional[int]
        updated_by: Optional[str]
        usage: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                categories: Optional[List[AtlasRelatedCategoryHeader]] = ..., 
                category_info: Optional[Dict[str, AtlasGlossaryCategory]] = ..., 
                classifications: Optional[List[AtlasClassification]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                guid: Optional[str] = ..., 
                language: Optional[str] = ..., 
                last_modified_ts: Optional[str] = ..., 
                long_description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                qualified_name: Optional[str] = ..., 
                short_description: Optional[str] = ..., 
                term_info: Optional[Dict[str, AtlasGlossaryTerm]] = ..., 
                terms: Optional[List[AtlasRelatedTermHeader]] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                usage: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasGlossaryHeader(Model):
        display_text: Optional[str]
        glossary_guid: Optional[str]
        relation_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_text: Optional[str] = ..., 
                glossary_guid: Optional[str] = ..., 
                relation_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasGlossaryTerm(Model):
        abbreviation: Optional[str]
        anchor: Optional[AtlasGlossaryHeader]
        antonyms: Optional[List[AtlasRelatedTermHeader]]
        assigned_entities: Optional[List[AtlasRelatedObjectId]]
        attributes: Optional[Dict[str, Dict[str, Any]]]
        categories: Optional[List[AtlasTermCategorizationHeader]]
        classifications: Optional[List[AtlasClassification]]
        classifies: Optional[List[AtlasRelatedTermHeader]]
        contacts: Optional[Dict[str, List[ContactInfo]]]
        create_time: Optional[int]
        created_by: Optional[str]
        examples: Optional[List[str]]
        guid: Optional[str]
        hierarchy_info: Optional[List[PurviewObjectId]]
        is_a: Optional[List[AtlasRelatedTermHeader]]
        last_modified_ts: Optional[str]
        long_description: Optional[str]
        name: Optional[str]
        nick_name: Optional[str]
        preferred_terms: Optional[List[AtlasRelatedTermHeader]]
        preferred_to_terms: Optional[List[AtlasRelatedTermHeader]]
        qualified_name: Optional[str]
        replaced_by: Optional[List[AtlasRelatedTermHeader]]
        replacement_terms: Optional[List[AtlasRelatedTermHeader]]
        resources: Optional[List[ResourceLink]]
        see_also: Optional[List[AtlasRelatedTermHeader]]
        short_description: Optional[str]
        status: Optional[Union[str, TermStatus]]
        synonyms: Optional[List[AtlasRelatedTermHeader]]
        template_name: Optional[List[Any]]
        translated_terms: Optional[List[AtlasRelatedTermHeader]]
        translation_terms: Optional[List[AtlasRelatedTermHeader]]
        update_time: Optional[int]
        updated_by: Optional[str]
        usage: Optional[str]
        valid_values: Optional[List[AtlasRelatedTermHeader]]
        valid_values_for: Optional[List[AtlasRelatedTermHeader]]

        @overload
        def __init__(
                self, 
                *, 
                abbreviation: Optional[str] = ..., 
                anchor: Optional[AtlasGlossaryHeader] = ..., 
                antonyms: Optional[List[AtlasRelatedTermHeader]] = ..., 
                assigned_entities: Optional[List[AtlasRelatedObjectId]] = ..., 
                attributes: Optional[Dict[str, Dict[str, Any]]] = ..., 
                categories: Optional[List[AtlasTermCategorizationHeader]] = ..., 
                classifications: Optional[List[AtlasClassification]] = ..., 
                classifies: Optional[List[AtlasRelatedTermHeader]] = ..., 
                contacts: Optional[Dict[str, List[ContactInfo]]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                examples: Optional[List[str]] = ..., 
                guid: Optional[str] = ..., 
                hierarchy_info: Optional[List[PurviewObjectId]] = ..., 
                is_a: Optional[List[AtlasRelatedTermHeader]] = ..., 
                last_modified_ts: Optional[str] = ..., 
                long_description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                nick_name: Optional[str] = ..., 
                preferred_terms: Optional[List[AtlasRelatedTermHeader]] = ..., 
                preferred_to_terms: Optional[List[AtlasRelatedTermHeader]] = ..., 
                qualified_name: Optional[str] = ..., 
                replaced_by: Optional[List[AtlasRelatedTermHeader]] = ..., 
                replacement_terms: Optional[List[AtlasRelatedTermHeader]] = ..., 
                resources: Optional[List[ResourceLink]] = ..., 
                see_also: Optional[List[AtlasRelatedTermHeader]] = ..., 
                short_description: Optional[str] = ..., 
                status: Optional[Union[str, TermStatus]] = ..., 
                synonyms: Optional[List[AtlasRelatedTermHeader]] = ..., 
                template_name: Optional[List[Any]] = ..., 
                translated_terms: Optional[List[AtlasRelatedTermHeader]] = ..., 
                translation_terms: Optional[List[AtlasRelatedTermHeader]] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                usage: Optional[str] = ..., 
                valid_values: Optional[List[AtlasRelatedTermHeader]] = ..., 
                valid_values_for: Optional[List[AtlasRelatedTermHeader]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasLineageInfo(Model):
        base_entity_guid: Optional[str]
        children_count: Optional[int]
        guid_entity_map: Optional[Dict[str, AtlasEntityHeader]]
        lineage_depth: Optional[int]
        lineage_direction: Optional[Union[str, LineageDirection]]
        lineage_width: Optional[int]
        parent_relations: Optional[List[ParentRelation]]
        relations: Optional[List[LineageRelation]]
        width_counts: Optional[Dict[str, Dict[str, Any]]]

        @overload
        def __init__(
                self, 
                *, 
                base_entity_guid: Optional[str] = ..., 
                children_count: Optional[int] = ..., 
                guid_entity_map: Optional[Dict[str, AtlasEntityHeader]] = ..., 
                lineage_depth: Optional[int] = ..., 
                lineage_direction: Optional[Union[str, LineageDirection]] = ..., 
                lineage_width: Optional[int] = ..., 
                parent_relations: Optional[List[ParentRelation]] = ..., 
                relations: Optional[List[LineageRelation]] = ..., 
                width_counts: Optional[Dict[str, Dict[str, Any]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasObjectId(Model):
        guid: Optional[str]
        type_name: Optional[str]
        unique_attributes: Optional[Dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                guid: Optional[str] = ..., 
                type_name: Optional[str] = ..., 
                unique_attributes: Optional[Dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasRelatedCategoryHeader(Model):
        category_guid: Optional[str]
        description: Optional[str]
        display_text: Optional[str]
        parent_category_guid: Optional[str]
        relation_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category_guid: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_text: Optional[str] = ..., 
                parent_category_guid: Optional[str] = ..., 
                relation_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasRelatedObjectId(Model):
        display_text: Optional[str]
        entity_status: Optional[Union[str, EntityStatus]]
        guid: Optional[str]
        relationship_attributes: Optional[AtlasStruct]
        relationship_guid: Optional[str]
        relationship_status: Optional[Union[str, StatusAtlasRelationship]]
        relationship_type: Optional[str]
        type_name: Optional[str]
        unique_attributes: Optional[Dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                display_text: Optional[str] = ..., 
                entity_status: Optional[Union[str, EntityStatus]] = ..., 
                guid: Optional[str] = ..., 
                relationship_attributes: Optional[AtlasStruct] = ..., 
                relationship_guid: Optional[str] = ..., 
                relationship_status: Optional[Union[str, StatusAtlasRelationship]] = ..., 
                relationship_type: Optional[str] = ..., 
                type_name: Optional[str] = ..., 
                unique_attributes: Optional[Dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasRelatedTermHeader(Model):
        description: Optional[str]
        display_text: Optional[str]
        expression: Optional[str]
        relation_guid: Optional[str]
        status: Optional[Union[str, AtlasTermRelationshipStatus]]
        steward: Optional[str]
        term_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_text: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                relation_guid: Optional[str] = ..., 
                status: Optional[Union[str, AtlasTermRelationshipStatus]] = ..., 
                steward: Optional[str] = ..., 
                term_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasRelationship(Model):
        attributes: Optional[Dict[str, Any]]
        create_time: Optional[int]
        created_by: Optional[str]
        end1: Optional[AtlasObjectId]
        end2: Optional[AtlasObjectId]
        guid: Optional[str]
        home_id: Optional[str]
        label: Optional[str]
        last_modified_ts: Optional[str]
        provenance_type: Optional[int]
        status: Optional[Union[str, StatusAtlasRelationship]]
        type_name: Optional[str]
        update_time: Optional[int]
        updated_by: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[Dict[str, Any]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                end1: Optional[AtlasObjectId] = ..., 
                end2: Optional[AtlasObjectId] = ..., 
                guid: Optional[str] = ..., 
                home_id: Optional[str] = ..., 
                label: Optional[str] = ..., 
                last_modified_ts: Optional[str] = ..., 
                provenance_type: Optional[int] = ..., 
                status: Optional[Union[str, StatusAtlasRelationship]] = ..., 
                type_name: Optional[str] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasRelationshipAttributeDef(Model):
        cardinality: Optional[Union[str, CardinalityValue]]
        constraints: Optional[List[AtlasConstraintDef]]
        default_value: Optional[str]
        description: Optional[str]
        include_in_notification: Optional[bool]
        is_indexable: Optional[bool]
        is_legacy_attribute: Optional[bool]
        is_optional: Optional[bool]
        is_unique: Optional[bool]
        name: Optional[str]
        options: Optional[Dict[str, str]]
        relationship_type_name: Optional[str]
        type_name: Optional[str]
        values_max_count: Optional[int]
        values_min_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cardinality: Optional[Union[str, CardinalityValue]] = ..., 
                constraints: Optional[List[AtlasConstraintDef]] = ..., 
                default_value: Optional[str] = ..., 
                description: Optional[str] = ..., 
                include_in_notification: Optional[bool] = ..., 
                is_indexable: Optional[bool] = ..., 
                is_legacy_attribute: Optional[bool] = ..., 
                is_optional: Optional[bool] = ..., 
                is_unique: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                options: Optional[Dict[str, str]] = ..., 
                relationship_type_name: Optional[str] = ..., 
                type_name: Optional[str] = ..., 
                values_max_count: Optional[int] = ..., 
                values_min_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasRelationshipDef(Model):
        attribute_defs: Optional[List[AtlasAttributeDef]]
        category: Optional[Union[str, TypeCategory]]
        create_time: Optional[int]
        created_by: Optional[str]
        date_formatter: Optional[DateFormat]
        description: Optional[str]
        end_def1: Optional[AtlasRelationshipEndDef]
        end_def2: Optional[AtlasRelationshipEndDef]
        guid: Optional[str]
        last_modified_ts: Optional[str]
        name: Optional[str]
        options: Optional[Dict[str, str]]
        relationship_category: Optional[Union[str, RelationshipCategory]]
        relationship_label: Optional[str]
        service_type: Optional[str]
        type_version: Optional[str]
        update_time: Optional[int]
        updated_by: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                attribute_defs: Optional[List[AtlasAttributeDef]] = ..., 
                category: Optional[Union[str, TypeCategory]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                date_formatter: Optional[DateFormat] = ..., 
                description: Optional[str] = ..., 
                end_def1: Optional[AtlasRelationshipEndDef] = ..., 
                end_def2: Optional[AtlasRelationshipEndDef] = ..., 
                guid: Optional[str] = ..., 
                last_modified_ts: Optional[str] = ..., 
                name: Optional[str] = ..., 
                options: Optional[Dict[str, str]] = ..., 
                relationship_category: Optional[Union[str, RelationshipCategory]] = ..., 
                relationship_label: Optional[str] = ..., 
                service_type: Optional[str] = ..., 
                type_version: Optional[str] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasRelationshipEndDef(Model):
        cardinality: Optional[Union[str, CardinalityValue]]
        description: Optional[str]
        is_container: Optional[bool]
        is_legacy_attribute: Optional[bool]
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cardinality: Optional[Union[str, CardinalityValue]] = ..., 
                description: Optional[str] = ..., 
                is_container: Optional[bool] = ..., 
                is_legacy_attribute: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasRelationshipWithExtInfo(Model):
        referred_entities: Optional[Dict[str, AtlasEntityHeader]]
        relationship: Optional[AtlasRelationship]

        @overload
        def __init__(
                self, 
                *, 
                referred_entities: Optional[Dict[str, AtlasEntityHeader]] = ..., 
                relationship: Optional[AtlasRelationship] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasStruct(Model):
        attributes: Optional[Dict[str, Any]]
        last_modified_ts: Optional[str]
        type_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[Dict[str, Any]] = ..., 
                last_modified_ts: Optional[str] = ..., 
                type_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasStructDef(Model):
        attribute_defs: Optional[List[AtlasAttributeDef]]
        category: Optional[Union[str, TypeCategory]]
        create_time: Optional[int]
        created_by: Optional[str]
        date_formatter: Optional[DateFormat]
        description: Optional[str]
        guid: Optional[str]
        last_modified_ts: Optional[str]
        name: Optional[str]
        options: Optional[Dict[str, str]]
        service_type: Optional[str]
        type_version: Optional[str]
        update_time: Optional[int]
        updated_by: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                attribute_defs: Optional[List[AtlasAttributeDef]] = ..., 
                category: Optional[Union[str, TypeCategory]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                date_formatter: Optional[DateFormat] = ..., 
                description: Optional[str] = ..., 
                guid: Optional[str] = ..., 
                last_modified_ts: Optional[str] = ..., 
                name: Optional[str] = ..., 
                options: Optional[Dict[str, str]] = ..., 
                service_type: Optional[str] = ..., 
                type_version: Optional[str] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasTermAssignmentHeader(Model):
        confidence: Optional[int]
        created_by: Optional[str]
        description: Optional[str]
        display_text: Optional[str]
        expression: Optional[str]
        relation_guid: Optional[str]
        status: Optional[Union[str, AtlasTermAssignmentStatus]]
        steward: Optional[str]
        term_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_text: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                relation_guid: Optional[str] = ..., 
                status: Optional[Union[str, AtlasTermAssignmentStatus]] = ..., 
                steward: Optional[str] = ..., 
                term_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasTermAssignmentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPRECATED = "DEPRECATED"
        DISCOVERED = "DISCOVERED"
        IMPORTED = "IMPORTED"
        OBSOLETE = "OBSOLETE"
        OTHER = "OTHER"
        PROPOSED = "PROPOSED"
        VALIDATED = "VALIDATED"


    class azure.purview.datamap.models.AtlasTermCategorizationHeader(Model):
        category_guid: Optional[str]
        description: Optional[str]
        display_text: Optional[str]
        relation_guid: Optional[str]
        status: Optional[Union[str, AtlasTermRelationshipStatus]]

        @overload
        def __init__(
                self, 
                *, 
                category_guid: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_text: Optional[str] = ..., 
                relation_guid: Optional[str] = ..., 
                status: Optional[Union[str, AtlasTermRelationshipStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasTermRelationshipStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "ACTIVE"
        DEPRECATED = "DEPRECATED"
        DRAFT = "DRAFT"
        OBSOLETE = "OBSOLETE"
        OTHER = "OTHER"


    class azure.purview.datamap.models.AtlasTypeDef(Model):
        attribute_defs: Optional[List[AtlasAttributeDef]]
        category: Optional[Union[str, TypeCategory]]
        create_time: Optional[int]
        created_by: Optional[str]
        date_formatter: Optional[DateFormat]
        default_value: Optional[str]
        description: Optional[str]
        element_defs: Optional[List[AtlasEnumElementDef]]
        end_def1: Optional[AtlasRelationshipEndDef]
        end_def2: Optional[AtlasRelationshipEndDef]
        entity_types: Optional[List[str]]
        guid: Optional[str]
        last_modified_ts: Optional[str]
        name: Optional[str]
        options: Optional[Dict[str, str]]
        relationship_attribute_defs: Optional[List[AtlasRelationshipAttributeDef]]
        relationship_category: Optional[Union[str, RelationshipCategory]]
        relationship_label: Optional[str]
        service_type: Optional[str]
        sub_types: Optional[List[str]]
        super_types: Optional[List[str]]
        type_version: Optional[str]
        update_time: Optional[int]
        updated_by: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                attribute_defs: Optional[List[AtlasAttributeDef]] = ..., 
                category: Optional[Union[str, TypeCategory]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                date_formatter: Optional[DateFormat] = ..., 
                default_value: Optional[str] = ..., 
                description: Optional[str] = ..., 
                element_defs: Optional[List[AtlasEnumElementDef]] = ..., 
                end_def1: Optional[AtlasRelationshipEndDef] = ..., 
                end_def2: Optional[AtlasRelationshipEndDef] = ..., 
                entity_types: Optional[List[str]] = ..., 
                guid: Optional[str] = ..., 
                last_modified_ts: Optional[str] = ..., 
                name: Optional[str] = ..., 
                options: Optional[Dict[str, str]] = ..., 
                relationship_attribute_defs: Optional[List[AtlasRelationshipAttributeDef]] = ..., 
                relationship_category: Optional[Union[str, RelationshipCategory]] = ..., 
                relationship_label: Optional[str] = ..., 
                service_type: Optional[str] = ..., 
                sub_types: Optional[List[str]] = ..., 
                super_types: Optional[List[str]] = ..., 
                type_version: Optional[str] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasTypeDefHeader(Model):
        category: Optional[Union[str, TypeCategory]]
        guid: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, TypeCategory]] = ..., 
                guid: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AtlasTypesDef(Model):
        business_metadata_defs: Optional[List[AtlasBusinessMetadataDef]]
        classification_defs: Optional[List[AtlasClassificationDef]]
        entity_defs: Optional[List[AtlasEntityDef]]
        enum_defs: Optional[List[AtlasEnumDef]]
        relationship_defs: Optional[List[AtlasRelationshipDef]]
        struct_defs: Optional[List[AtlasStructDef]]
        term_template_defs: Optional[List[TermTemplateDef]]

        @overload
        def __init__(
                self, 
                *, 
                business_metadata_defs: Optional[List[AtlasBusinessMetadataDef]] = ..., 
                classification_defs: Optional[List[AtlasClassificationDef]] = ..., 
                entity_defs: Optional[List[AtlasEntityDef]] = ..., 
                enum_defs: Optional[List[AtlasEnumDef]] = ..., 
                relationship_defs: Optional[List[AtlasRelationshipDef]] = ..., 
                struct_defs: Optional[List[AtlasStructDef]] = ..., 
                term_template_defs: Optional[List[TermTemplateDef]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AutoCompleteOptions(Model):
        filter: Optional[Any]
        keywords: Optional[str]
        limit: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[Any] = ..., 
                keywords: Optional[str] = ..., 
                limit: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AutoCompleteResult(Model):
        value: Optional[List[AutoCompleteResultValue]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[List[AutoCompleteResultValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.AutoCompleteResultValue(Model):
        query_plus_text: Optional[str]
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                query_plus_text: Optional[str] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.BulkImportResult(Model):
        failed_import_info_list: Optional[List[ImportInfo]]
        success_import_info_list: Optional[List[ImportInfo]]

        @overload
        def __init__(
                self, 
                *, 
                failed_import_info_list: Optional[List[ImportInfo]] = ..., 
                success_import_info_list: Optional[List[ImportInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.BusinessAttributeUpdateBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IGNORE = "ignore"
        MERGE = "merge"
        REPLACE = "replace"


    class azure.purview.datamap.models.BusinessMetadataOptions(Model):
        file: Union[str, bytes, IO[str], IO[bytes], Tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], Tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]

        @overload
        def __init__(
                self, 
                *, 
                file: FileType
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.CardinalityValue(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIST = "LIST"
        SET = "SET"
        SINGLE = "SINGLE"


    class azure.purview.datamap.models.ClassificationAssociateOptions(Model):
        classification: Optional[AtlasClassification]
        entity_guids: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                classification: Optional[AtlasClassification] = ..., 
                entity_guids: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.ContactInfo(Model):
        id: Optional[str]
        info: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                info: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.ContactSearchResultValue(Model):
        contact_type: Optional[str]
        id: Optional[str]
        info: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                contact_type: Optional[str] = ..., 
                id: Optional[str] = ..., 
                info: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.DateFormat(Model):
        available_locales: Optional[List[str]]
        calendar: Optional[float]
        date_instance: Optional[DateFormat]
        date_time_instance: Optional[DateFormat]
        instance: Optional[DateFormat]
        lenient: Optional[bool]
        number_format: Optional[NumberFormat]
        time_instance: Optional[DateFormat]
        time_zone: Optional[TimeZone]

        @overload
        def __init__(
                self, 
                *, 
                available_locales: Optional[List[str]] = ..., 
                calendar: Optional[float] = ..., 
                date_instance: Optional[DateFormat] = ..., 
                date_time_instance: Optional[DateFormat] = ..., 
                instance: Optional[DateFormat] = ..., 
                lenient: Optional[bool] = ..., 
                number_format: Optional[NumberFormat] = ..., 
                time_instance: Optional[DateFormat] = ..., 
                time_zone: Optional[TimeZone] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.EntityMutationResult(Model):
        guid_assignments: Optional[Dict[str, str]]
        mutated_entities: Optional[Dict[str, List[AtlasEntityHeader]]]
        partial_updated_entities: Optional[List[AtlasEntityHeader]]

        @overload
        def __init__(
                self, 
                *, 
                guid_assignments: Optional[Dict[str, str]] = ..., 
                mutated_entities: Optional[Dict[str, List[AtlasEntityHeader]]] = ..., 
                partial_updated_entities: Optional[List[AtlasEntityHeader]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.EntityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "ACTIVE"
        DELETED = "DELETED"


    class azure.purview.datamap.models.ImportInfo(Model):
        child_object_name: Optional[str]
        import_status: Optional[Union[str, ImportStatus]]
        parent_object_name: Optional[str]
        remarks: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                child_object_name: Optional[str] = ..., 
                import_status: Optional[Union[str, ImportStatus]] = ..., 
                parent_object_name: Optional[str] = ..., 
                remarks: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.ImportStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "FAILED"
        SUCCESS = "SUCCESS"


    class azure.purview.datamap.models.LineageDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOTH = "BOTH"
        INPUT = "INPUT"
        OUTPUT = "OUTPUT"


    class azure.purview.datamap.models.LineageRelation(Model):
        from_entity_id: Optional[str]
        relationship_id: Optional[str]
        to_entity_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                from_entity_id: Optional[str] = ..., 
                relationship_id: Optional[str] = ..., 
                to_entity_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.MoveEntitiesOptions(Model):
        entity_guids: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                entity_guids: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.NumberFormat(Model):
        available_locales: Optional[List[str]]
        currency: Optional[str]
        currency_instance: Optional[NumberFormat]
        grouping_used: Optional[bool]
        instance: Optional[NumberFormat]
        integer_instance: Optional[NumberFormat]
        maximum_fraction_digits: Optional[int]
        maximum_integer_digits: Optional[int]
        minimum_fraction_digits: Optional[int]
        minimum_integer_digits: Optional[int]
        number_instance: Optional[NumberFormat]
        parse_integer_only: Optional[bool]
        percent_instance: Optional[NumberFormat]
        rounding_mode: Optional[Union[str, RoundingMode]]

        @overload
        def __init__(
                self, 
                *, 
                available_locales: Optional[List[str]] = ..., 
                currency: Optional[str] = ..., 
                currency_instance: Optional[NumberFormat] = ..., 
                grouping_used: Optional[bool] = ..., 
                instance: Optional[NumberFormat] = ..., 
                integer_instance: Optional[NumberFormat] = ..., 
                maximum_fraction_digits: Optional[int] = ..., 
                maximum_integer_digits: Optional[int] = ..., 
                minimum_fraction_digits: Optional[int] = ..., 
                minimum_integer_digits: Optional[int] = ..., 
                number_instance: Optional[NumberFormat] = ..., 
                parse_integer_only: Optional[bool] = ..., 
                percent_instance: Optional[NumberFormat] = ..., 
                rounding_mode: Optional[Union[str, RoundingMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.ParentRelation(Model):
        child_entity_id: Optional[str]
        parent_entity_id: Optional[str]
        relationship_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                child_entity_id: Optional[str] = ..., 
                parent_entity_id: Optional[str] = ..., 
                relationship_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.PurviewObjectId(Model):
        display_text: Optional[str]
        guid: Optional[str]
        item_path: Optional[str]
        name: Optional[str]
        properties: Optional[Dict[str, Any]]
        resource_id: Optional[str]
        type_name: Optional[str]
        unique_attributes: Optional[Dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                display_text: Optional[str] = ..., 
                guid: Optional[str] = ..., 
                item_path: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[Dict[str, Any]] = ..., 
                resource_id: Optional[str] = ..., 
                type_name: Optional[str] = ..., 
                unique_attributes: Optional[Dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.QueryOptions(Model):
        continuation_token: Optional[str]
        facets: Optional[List[SearchFacetItem]]
        filter: Optional[Any]
        keywords: Optional[str]
        limit: Optional[int]
        orderby: Optional[List[Any]]
        taxonomy_setting: Optional[SearchTaxonomySetting]

        @overload
        def __init__(
                self, 
                *, 
                continuation_token: Optional[str] = ..., 
                facets: Optional[List[SearchFacetItem]] = ..., 
                filter: Optional[Any] = ..., 
                keywords: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                orderby: Optional[List[Any]] = ..., 
                taxonomy_setting: Optional[SearchTaxonomySetting] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.QueryResult(Model):
        continuation_token: Optional[str]
        search_count: Optional[int]
        search_count_approximate: Optional[bool]
        search_facets: Optional[SearchFacetResultValue]
        value: Optional[List[SearchResultValue]]

        @overload
        def __init__(
                self, 
                *, 
                continuation_token: Optional[str] = ..., 
                search_count: Optional[int] = ..., 
                search_count_approximate: Optional[bool] = ..., 
                search_facets: Optional[SearchFacetResultValue] = ..., 
                value: Optional[List[SearchResultValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.RelationshipCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGGREGATION = "AGGREGATION"
        ASSOCIATION = "ASSOCIATION"
        COMPOSITION = "COMPOSITION"


    class azure.purview.datamap.models.ResourceLink(Model):
        display_name: Optional[str]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.RoundingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CEILING = "CEILING"
        DOWN = "DOWN"
        FLOOR = "FLOOR"
        HALF_DOWN = "HALF_DOWN"
        HALF_EVEN = "HALF_EVEN"
        HALF_UP = "HALF_UP"
        UNNECESSARY = "UNNECESSARY"
        UP = "UP"


    class azure.purview.datamap.models.SearchFacetItem(Model):
        count: Optional[int]
        facet: Optional[str]
        sort: Optional[SearchFacetSort]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                facet: Optional[str] = ..., 
                sort: Optional[SearchFacetSort] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.SearchFacetItemValue(Model):
        count: Optional[int]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.SearchFacetResultValue(Model):
        asset_type: Optional[List[SearchFacetItemValue]]
        classification: Optional[List[SearchFacetItemValue]]
        contact_id: Optional[List[SearchFacetItemValue]]
        contact_type: Optional[List[SearchFacetItemValue]]
        entity_type: Optional[List[SearchFacetItemValue]]
        glossary_type: Optional[List[SearchFacetItemValue]]
        label: Optional[List[SearchFacetItemValue]]
        term: Optional[List[SearchFacetItemValue]]
        term_status: Optional[List[SearchFacetItemValue]]
        term_template: Optional[List[SearchFacetItemValue]]

        @overload
        def __init__(
                self, 
                *, 
                asset_type: Optional[List[SearchFacetItemValue]] = ..., 
                classification: Optional[List[SearchFacetItemValue]] = ..., 
                contact_id: Optional[List[SearchFacetItemValue]] = ..., 
                contact_type: Optional[List[SearchFacetItemValue]] = ..., 
                entity_type: Optional[List[SearchFacetItemValue]] = ..., 
                glossary_type: Optional[List[SearchFacetItemValue]] = ..., 
                label: Optional[List[SearchFacetItemValue]] = ..., 
                term: Optional[List[SearchFacetItemValue]] = ..., 
                term_status: Optional[List[SearchFacetItemValue]] = ..., 
                term_template: Optional[List[SearchFacetItemValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.SearchFacetSort(Model):
        count: Optional[Union[str, SearchSortOrder]]
        value: Optional[Union[str, SearchSortOrder]]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[Union[str, SearchSortOrder]] = ..., 
                value: Optional[Union[str, SearchSortOrder]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.SearchHighlights(Model):
        description: Optional[List[str]]
        entity_type: Optional[List[str]]
        id: Optional[List[str]]
        name: Optional[List[str]]
        qualified_name: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[List[str]] = ..., 
                entity_type: Optional[List[str]] = ..., 
                id: Optional[List[str]] = ..., 
                name: Optional[List[str]] = ..., 
                qualified_name: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.SearchResultValue(Model):
        asset_type: Optional[List[str]]
        classification: Optional[List[str]]
        contact: Optional[List[ContactSearchResultValue]]
        create_time: Optional[int]
        description: Optional[str]
        endorsement: Optional[List[str]]
        entity_type: Optional[str]
        glossary: Optional[str]
        glossary_type: Optional[str]
        id: Optional[str]
        label: Optional[List[str]]
        long_description: Optional[str]
        name: Optional[str]
        object_type: Optional[str]
        owner: Optional[str]
        qualified_name: Optional[str]
        search_highlights: Optional[SearchHighlights]
        search_score: Optional[float]
        term: Optional[List[TermSearchResultValue]]
        term_status: Optional[str]
        term_template: Optional[List[str]]
        update_time: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                asset_type: Optional[List[str]] = ..., 
                classification: Optional[List[str]] = ..., 
                contact: Optional[List[ContactSearchResultValue]] = ..., 
                create_time: Optional[int] = ..., 
                description: Optional[str] = ..., 
                endorsement: Optional[List[str]] = ..., 
                entity_type: Optional[str] = ..., 
                glossary: Optional[str] = ..., 
                glossary_type: Optional[str] = ..., 
                id: Optional[str] = ..., 
                label: Optional[List[str]] = ..., 
                long_description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                object_type: Optional[str] = ..., 
                owner: Optional[str] = ..., 
                qualified_name: Optional[str] = ..., 
                search_highlights: Optional[SearchHighlights] = ..., 
                search_score: Optional[float] = ..., 
                term: Optional[List[TermSearchResultValue]] = ..., 
                term_status: Optional[str] = ..., 
                term_template: Optional[List[str]] = ..., 
                update_time: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.SearchSortOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASCEND = "asc"
        DESCEND = "desc"


    class azure.purview.datamap.models.SearchTaxonomySetting(Model):
        asset_types: Optional[List[str]]
        facet: Optional[SearchFacetItem]

        @overload
        def __init__(
                self, 
                *, 
                asset_types: Optional[List[str]] = ..., 
                facet: Optional[SearchFacetItem] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.SortType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASCEND = "ASC"
        DESCEND = "DESC"
        NONE = "NONE"


    class azure.purview.datamap.models.StatusAtlasRelationship(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "ACTIVE"
        DELETED = "DELETED"


    class azure.purview.datamap.models.SuggestOptions(Model):
        filter: Optional[Any]
        keywords: Optional[str]
        limit: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[Any] = ..., 
                keywords: Optional[str] = ..., 
                limit: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.SuggestResult(Model):
        value: Optional[List[SuggestResultValue]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[List[SuggestResultValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.SuggestResultValue(Model):
        asset_type: Optional[List[str]]
        classification: Optional[List[str]]
        contact: Optional[List[ContactSearchResultValue]]
        create_time: Optional[int]
        description: Optional[str]
        endorsement: Optional[List[str]]
        entity_type: Optional[str]
        glossary: Optional[str]
        glossary_type: Optional[str]
        id: Optional[str]
        label: Optional[List[str]]
        long_description: Optional[str]
        name: Optional[str]
        object_type: Optional[str]
        owner: Optional[str]
        qualified_name: Optional[str]
        search_score: Optional[float]
        search_text: Optional[str]
        term: Optional[List[TermSearchResultValue]]
        term_status: Optional[str]
        term_template: Optional[List[str]]
        update_time: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                asset_type: Optional[List[str]] = ..., 
                classification: Optional[List[str]] = ..., 
                contact: Optional[List[ContactSearchResultValue]] = ..., 
                create_time: Optional[int] = ..., 
                description: Optional[str] = ..., 
                endorsement: Optional[List[str]] = ..., 
                entity_type: Optional[str] = ..., 
                glossary: Optional[str] = ..., 
                glossary_type: Optional[str] = ..., 
                id: Optional[str] = ..., 
                label: Optional[List[str]] = ..., 
                long_description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                object_type: Optional[str] = ..., 
                owner: Optional[str] = ..., 
                qualified_name: Optional[str] = ..., 
                search_score: Optional[float] = ..., 
                search_text: Optional[str] = ..., 
                term: Optional[List[TermSearchResultValue]] = ..., 
                term_status: Optional[str] = ..., 
                term_template: Optional[List[str]] = ..., 
                update_time: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.TermSearchResultValue(Model):
        glossary_name: Optional[str]
        guid: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                glossary_name: Optional[str] = ..., 
                guid: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.TermStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT = "Alert"
        APPROVED = "Approved"
        DRAFT = "Draft"
        EXPIRED = "Expired"


    class azure.purview.datamap.models.TermTemplateDef(Model):
        attribute_defs: Optional[List[AtlasAttributeDef]]
        category: Optional[Union[str, TypeCategory]]
        create_time: Optional[int]
        created_by: Optional[str]
        date_formatter: Optional[DateFormat]
        description: Optional[str]
        guid: Optional[str]
        last_modified_ts: Optional[str]
        name: Optional[str]
        options: Optional[Dict[str, str]]
        service_type: Optional[str]
        type_version: Optional[str]
        update_time: Optional[int]
        updated_by: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                attribute_defs: Optional[List[AtlasAttributeDef]] = ..., 
                category: Optional[Union[str, TypeCategory]] = ..., 
                create_time: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                date_formatter: Optional[DateFormat] = ..., 
                description: Optional[str] = ..., 
                guid: Optional[str] = ..., 
                last_modified_ts: Optional[str] = ..., 
                name: Optional[str] = ..., 
                options: Optional[Dict[str, str]] = ..., 
                service_type: Optional[str] = ..., 
                type_version: Optional[str] = ..., 
                update_time: Optional[int] = ..., 
                updated_by: Optional[str] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.TimeBoundary(Model):
        end_time: Optional[str]
        start_time: Optional[str]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.TimeZone(Model):
        available_ids: Optional[List[str]]
        default: Optional[TimeZone]
        display_name: Optional[str]
        dst_savings: Optional[int]
        id: Optional[str]
        raw_offset: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                available_ids: Optional[List[str]] = ..., 
                default: Optional[TimeZone] = ..., 
                display_name: Optional[str] = ..., 
                dst_savings: Optional[int] = ..., 
                id: Optional[str] = ..., 
                raw_offset: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.purview.datamap.models.TypeCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "ARRAY"
        CLASSIFICATION = "CLASSIFICATION"
        ENTITY = "ENTITY"
        ENUM = "ENUM"
        MAP = "MAP"
        OBJECT_ID_TYPE = "OBJECT_ID_TYPE"
        PRIMITIVE = "PRIMITIVE"
        RELATIONSHIP = "RELATIONSHIP"
        STRUCT = "STRUCT"
        TERM_TEMPLATE = "TERM_TEMPLATE"


namespace azure.purview.datamap.operations

    class azure.purview.datamap.operations.DiscoveryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def auto_complete(
                self, 
                body: AutoCompleteOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoCompleteResult: ...

        @overload
        def auto_complete(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoCompleteResult: ...

        @overload
        def auto_complete(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoCompleteResult: ...

        @overload
        def query(
                self, 
                body: QueryOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResult: ...

        @overload
        def query(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResult: ...

        @overload
        def query(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResult: ...

        @overload
        def suggest(
                self, 
                body: SuggestOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuggestResult: ...

        @overload
        def suggest(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuggestResult: ...

        @overload
        def suggest(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuggestResult: ...


    class azure.purview.datamap.operations.EntityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def add_classification(
                self, 
                body: ClassificationAssociateOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_classification(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_classification(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_classifications(
                self, 
                guid: str, 
                body: List[AtlasClassification], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_classifications(
                self, 
                guid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_classifications_by_unique_attribute(
                self, 
                type_name: str, 
                body: List[AtlasClassification], 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_classifications_by_unique_attribute(
                self, 
                type_name: str, 
                body: IO[bytes], 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_label(
                self, 
                guid: str, 
                body: Optional[List[str]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_label(
                self, 
                guid: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_labels_by_unique_attribute(
                self, 
                type_name: str, 
                body: Optional[List[str]] = None, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_labels_by_unique_attribute(
                self, 
                type_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_or_update_business_metadata(
                self, 
                guid: str, 
                body: Dict[str, Dict[str, Any]], 
                *, 
                content_type: str = "application/json", 
                overwrite: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_or_update_business_metadata(
                self, 
                guid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                overwrite: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_or_update_business_metadata_attributes(
                self, 
                business_metadata_name: str, 
                guid: str, 
                body: Dict[str, Any], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_or_update_business_metadata_attributes(
                self, 
                business_metadata_name: str, 
                guid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def batch_create_or_update(
                self, 
                body: AtlasEntitiesWithExtInfo, 
                *, 
                business_attribute_update_behavior: Optional[Union[str, BusinessAttributeUpdateBehavior]] = ..., 
                collection_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        def batch_create_or_update(
                self, 
                body: JSON, 
                *, 
                business_attribute_update_behavior: Optional[Union[str, BusinessAttributeUpdateBehavior]] = ..., 
                collection_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        def batch_create_or_update(
                self, 
                body: IO[bytes], 
                *, 
                business_attribute_update_behavior: Optional[Union[str, BusinessAttributeUpdateBehavior]] = ..., 
                collection_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @distributed_trace
        def batch_delete(
                self, 
                *, 
                guid: List[str], 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @distributed_trace
        def batch_get_by_unique_attributes(
                self, 
                type_name: str, 
                *, 
                attr_n_qualified_name: Optional[str] = ..., 
                ignore_relationships: Optional[bool] = ..., 
                min_ext_info: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasEntitiesWithExtInfo: ...

        @overload
        def batch_set_classifications(
                self, 
                body: AtlasEntityHeaders, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[str]: ...

        @overload
        def batch_set_classifications(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[str]: ...

        @overload
        def batch_set_classifications(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[str]: ...

        @overload
        def create_or_update(
                self, 
                body: AtlasEntityWithExtInfo, 
                *, 
                business_attribute_update_behavior: Optional[Union[str, BusinessAttributeUpdateBehavior]] = ..., 
                collection_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        def create_or_update(
                self, 
                body: JSON, 
                *, 
                business_attribute_update_behavior: Optional[Union[str, BusinessAttributeUpdateBehavior]] = ..., 
                collection_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        def create_or_update(
                self, 
                body: IO[bytes], 
                *, 
                business_attribute_update_behavior: Optional[Union[str, BusinessAttributeUpdateBehavior]] = ..., 
                collection_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @distributed_trace
        def delete(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @distributed_trace
        def delete_by_unique_attribute(
                self, 
                type_name: str, 
                *, 
                attribute: Optional[str] = ..., 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @distributed_trace
        def get(
                self, 
                guid: str, 
                *, 
                ignore_relationships: Optional[bool] = ..., 
                min_ext_info: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasEntityWithExtInfo: ...

        @distributed_trace
        def get_business_metadata_template(self, **kwargs: Any) -> Iterator[bytes]: ...

        @distributed_trace
        def get_by_ids(
                self, 
                *, 
                guid: List[str], 
                ignore_relationships: Optional[bool] = ..., 
                min_ext_info: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasEntitiesWithExtInfo: ...

        @distributed_trace
        def get_by_unique_attribute(
                self, 
                type_name: str, 
                *, 
                attribute: Optional[str] = ..., 
                ignore_relationships: Optional[bool] = ..., 
                min_ext_info: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasEntityWithExtInfo: ...

        @distributed_trace
        def get_classification(
                self, 
                guid: str, 
                classification_name: str, 
                **kwargs: Any
            ) -> AtlasClassification: ...

        @distributed_trace
        def get_classifications(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasClassifications: ...

        @distributed_trace
        def get_header(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasEntityHeader: ...

        @overload
        def import_business_metadata(
                self, 
                body: BusinessMetadataOptions, 
                **kwargs: Any
            ) -> BulkImportResult: ...

        @overload
        def import_business_metadata(
                self, 
                body: JSON, 
                **kwargs: Any
            ) -> BulkImportResult: ...

        @overload
        def move_entities_to_collection(
                self, 
                body: MoveEntitiesOptions, 
                *, 
                collection_id: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        def move_entities_to_collection(
                self, 
                body: JSON, 
                *, 
                collection_id: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        def move_entities_to_collection(
                self, 
                body: IO[bytes], 
                *, 
                collection_id: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        def remove_business_metadata(
                self, 
                guid: str, 
                body: Dict[str, Dict[str, Any]], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def remove_business_metadata(
                self, 
                guid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def remove_business_metadata_attributes(
                self, 
                business_metadata_name: str, 
                guid: str, 
                body: Dict[str, Any], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def remove_business_metadata_attributes(
                self, 
                business_metadata_name: str, 
                guid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def remove_classification(
                self, 
                guid: str, 
                classification_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def remove_classification_by_unique_attribute(
                self, 
                type_name: str, 
                classification_name: str, 
                *, 
                attribute: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def remove_labels(
                self, 
                guid: str, 
                body: Optional[List[str]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def remove_labels(
                self, 
                guid: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def remove_labels_by_unique_attribute(
                self, 
                type_name: str, 
                body: Optional[List[str]] = None, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def remove_labels_by_unique_attribute(
                self, 
                type_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set_labels(
                self, 
                guid: str, 
                body: Optional[List[str]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set_labels(
                self, 
                guid: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set_labels_by_unique_attribute(
                self, 
                type_name: str, 
                body: Optional[List[str]] = None, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set_labels_by_unique_attribute(
                self, 
                type_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_attribute_by_id(
                self, 
                guid: str, 
                body: Any, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        def update_by_unique_attribute(
                self, 
                type_name: str, 
                body: AtlasEntityWithExtInfo, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        def update_by_unique_attribute(
                self, 
                type_name: str, 
                body: JSON, 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        def update_by_unique_attribute(
                self, 
                type_name: str, 
                body: IO[bytes], 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityMutationResult: ...

        @overload
        def update_classifications(
                self, 
                guid: str, 
                body: List[AtlasClassification], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_classifications(
                self, 
                guid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_classifications_unique_by_attribute(
                self, 
                type_name: str, 
                body: List[AtlasClassification], 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_classifications_unique_by_attribute(
                self, 
                type_name: str, 
                body: IO[bytes], 
                *, 
                attribute: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.purview.datamap.operations.GlossaryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def assign_term_to_entities(
                self, 
                term_id: str, 
                body: List[AtlasRelatedObjectId], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def assign_term_to_entities(
                self, 
                term_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def batch_get(
                self, 
                *, 
                ignore_terms_and_categories: Optional[bool] = ..., 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasGlossary]: ...

        @overload
        def create(
                self, 
                body: AtlasGlossary, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        def create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        def create_categories(
                self, 
                body: List[AtlasGlossaryCategory], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[AtlasGlossaryCategory]: ...

        @overload
        def create_categories(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[AtlasGlossaryCategory]: ...

        @overload
        def create_category(
                self, 
                body: AtlasGlossaryCategory, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        def create_category(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        def create_category(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        def create_term(
                self, 
                body: AtlasGlossaryTerm, 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        def create_term(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        def create_term(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        def create_terms(
                self, 
                body: List[AtlasGlossaryTerm], 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[AtlasGlossaryTerm]: ...

        @overload
        def create_terms(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> List[AtlasGlossaryTerm]: ...

        @distributed_trace
        def delete(
                self, 
                glossary_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_category(
                self, 
                category_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_term(
                self, 
                term_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def delete_term_assignment_from_entities(
                self, 
                term_id: str, 
                body: List[AtlasRelatedObjectId], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def delete_term_assignment_from_entities(
                self, 
                term_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                glossary_id: str, 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @distributed_trace
        def get_categories(
                self, 
                glossary_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasGlossaryCategory]: ...

        @distributed_trace
        def get_categories_headers(
                self, 
                glossary_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasRelatedCategoryHeader]: ...

        @distributed_trace
        def get_category(
                self, 
                category_id: str, 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @distributed_trace
        def get_category_terms(
                self, 
                category_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasRelatedTermHeader]: ...

        @distributed_trace
        def get_detailed(
                self, 
                glossary_id: str, 
                **kwargs: Any
            ) -> AtlasGlossaryExtInfo: ...

        @distributed_trace
        def get_entities_assigned_with_term(
                self, 
                term_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasRelatedObjectId]: ...

        @distributed_trace
        def get_related_categories(
                self, 
                category_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, List[AtlasRelatedCategoryHeader]]: ...

        @distributed_trace
        def get_related_terms(
                self, 
                term_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> Dict[str, List[AtlasRelatedTermHeader]]: ...

        @distributed_trace
        def get_term(
                self, 
                term_id: str, 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @distributed_trace
        def get_term_headers(
                self, 
                glossary_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasRelatedTermHeader]: ...

        @distributed_trace
        def get_terms(
                self, 
                glossary_id: str, 
                *, 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                sort: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[AtlasGlossaryTerm]: ...

        @overload
        def partial_update(
                self, 
                glossary_id: str, 
                body: Dict[str, str], 
                *, 
                content_type: str = "application/json", 
                ignore_terms_and_categories: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        def partial_update(
                self, 
                glossary_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                ignore_terms_and_categories: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        def partial_update_category(
                self, 
                category_id: str, 
                body: Dict[str, str], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        def partial_update_category(
                self, 
                category_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        def partial_update_term(
                self, 
                term_id: str, 
                body: Dict[str, str], 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        def partial_update_term(
                self, 
                term_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        def update(
                self, 
                glossary_id: str, 
                body: AtlasGlossary, 
                *, 
                content_type: str = "application/json", 
                ignore_terms_and_categories: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        def update(
                self, 
                glossary_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                ignore_terms_and_categories: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        def update(
                self, 
                glossary_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                ignore_terms_and_categories: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossary: ...

        @overload
        def update_category(
                self, 
                category_id: str, 
                body: AtlasGlossaryCategory, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        def update_category(
                self, 
                category_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        def update_category(
                self, 
                category_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasGlossaryCategory: ...

        @overload
        def update_term(
                self, 
                term_id: str, 
                body: AtlasGlossaryTerm, 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        def update_term(
                self, 
                term_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...

        @overload
        def update_term(
                self, 
                term_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                include_term_hierarchy: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasGlossaryTerm: ...


    class azure.purview.datamap.operations.LineageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                guid: str, 
                *, 
                depth: Optional[int] = ..., 
                direction: Union[str, LineageDirection], 
                **kwargs: Any
            ) -> AtlasLineageInfo: ...

        @distributed_trace
        def get_by_unique_attribute(
                self, 
                type_name: str, 
                *, 
                attribute: Optional[str] = ..., 
                depth: Optional[int] = ..., 
                direction: Union[str, LineageDirection], 
                **kwargs: Any
            ) -> AtlasLineageInfo: ...

        @distributed_trace
        def get_next_page(
                self, 
                guid: str, 
                *, 
                direction: Union[str, LineageDirection], 
                limit: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                **kwargs: Any
            ) -> AtlasLineageInfo: ...


    class azure.purview.datamap.operations.RelationshipOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                body: AtlasRelationship, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasRelationship: ...

        @overload
        def create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasRelationship: ...

        @overload
        def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasRelationship: ...

        @distributed_trace
        def delete(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                guid: str, 
                *, 
                extended_info: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AtlasRelationshipWithExtInfo: ...

        @overload
        def update(
                self, 
                body: AtlasRelationship, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasRelationship: ...

        @overload
        def update(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasRelationship: ...

        @overload
        def update(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasRelationship: ...


    class azure.purview.datamap.operations.TypeDefinitionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def batch_create(
                self, 
                body: AtlasTypesDef, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @overload
        def batch_create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @overload
        def batch_create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @overload
        def batch_delete(
                self, 
                body: AtlasTypesDef, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def batch_delete(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def batch_delete(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def batch_update(
                self, 
                body: AtlasTypesDef, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @overload
        def batch_update(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @overload
        def batch_update(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                *, 
                include_term_template: Optional[bool] = ..., 
                type: Optional[Union[str, TypeCategory]] = ..., 
                **kwargs: Any
            ) -> AtlasTypesDef: ...

        @distributed_trace
        def get_business_metadata_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasBusinessMetadataDef: ...

        @distributed_trace
        def get_business_metadata_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasBusinessMetadataDef: ...

        @distributed_trace
        def get_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasTypeDef: ...

        @distributed_trace
        def get_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasTypeDef: ...

        @distributed_trace
        def get_classification_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasClassificationDef: ...

        @distributed_trace
        def get_classification_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasClassificationDef: ...

        @distributed_trace
        def get_entity_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasEntityDef: ...

        @distributed_trace
        def get_entity_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasEntityDef: ...

        @distributed_trace
        def get_enum_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasEnumDef: ...

        @distributed_trace
        def get_enum_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasEnumDef: ...

        @distributed_trace
        def get_headers(
                self, 
                *, 
                include_term_template: Optional[bool] = ..., 
                type: Optional[Union[str, TypeCategory]] = ..., 
                **kwargs: Any
            ) -> List[AtlasTypeDefHeader]: ...

        @distributed_trace
        def get_relationship_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasRelationshipDef: ...

        @distributed_trace
        def get_relationship_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasRelationshipDef: ...

        @distributed_trace
        def get_struct_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> AtlasStructDef: ...

        @distributed_trace
        def get_struct_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AtlasStructDef: ...

        @distributed_trace
        def get_term_template_by_id(
                self, 
                guid: str, 
                **kwargs: Any
            ) -> TermTemplateDef: ...

        @distributed_trace
        def get_term_template_by_name(
                self, 
                name: str, 
                **kwargs: Any
            ) -> TermTemplateDef: ...


```