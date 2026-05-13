```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.data.tables

    def azure.data.tables.generate_account_sas(
            credential: AzureNamedKeyCredential, 
            resource_types: ResourceTypes, 
            permission: Union[str, AccountSasPermissions], 
            expiry: Union[datetime, str], 
            *, 
            ip_address_or_range: Optional[str] = ..., 
            protocol: Optional[Union[SASProtocol, str]] = ..., 
            start: Optional[Union[datetime, str]] = ...
        ) -> str: ...


    def azure.data.tables.generate_table_sas(
            credential: AzureNamedKeyCredential, 
            table_name: str, 
            *, 
            end_pk: Optional[str] = ..., 
            end_rk: Optional[str] = ..., 
            expiry: Optional[Union[datetime, str]] = ..., 
            ip_address_or_range: Optional[str] = ..., 
            permission: Optional[Union[TableSasPermissions, str]] = ..., 
            policy_id: Optional[str] = ..., 
            protocol: Optional[Union[SASProtocol, str]] = ..., 
            start: Optional[Union[datetime, str]] = ..., 
            start_pk: Optional[str] = ..., 
            start_rk: Optional[str] = ...
        ) -> str: ...


    class azure.data.tables.AccountSasPermissions:
        add: bool
        create: bool
        delete: bool
        list: bool
        process: bool
        read: bool
        update: bool
        write: bool

        def __init__(
                self, 
                *, 
                add: Optional[bool] = ..., 
                create: Optional[bool] = ..., 
                delete: Optional[bool] = ..., 
                list: Optional[bool] = ..., 
                process: Optional[bool] = ..., 
                read: Optional[bool] = ..., 
                update: Optional[bool] = ..., 
                write: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        @classmethod
        def from_string(
                cls, 
                permission: str, 
                **kwargs: Any
            ) -> AccountSasPermissions: ...


    class azure.data.tables.EdmType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BINARY = "Edm.Binary"
        BOOLEAN = "Edm.Boolean"
        DATETIME = "Edm.DateTime"
        DOUBLE = "Edm.Double"
        GUID = "Edm.Guid"
        INT32 = "Edm.Int32"
        INT64 = "Edm.Int64"
        STRING = "Edm.String"


    class azure.data.tables.EntityMetadata(TypedDict, total=False):
        key "editLink": str
        key "etag": Required[Optional[str]]
        key "id": str
        key "timestamp": Required[Optional[datetime]]
        key "type": str


    class azure.data.tables.EntityProperty(tuple):
        edm_type: Union[str, EdmType]
        value: Any


    class azure.data.tables.RequestTooLargeError(TableTransactionError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.data.tables.ResourceTypes:
        container: bool
        object: bool
        service: bool

        def __init__(
                self, 
                *, 
                container: Optional[bool] = ..., 
                object: Optional[bool] = ..., 
                service: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        @classmethod
        def from_string(cls, string: str) -> ResourceTypes: ...


    class azure.data.tables.SASProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "http"
        HTTPS = "https"


    class azure.data.tables.TableAccessPolicy(GenAccessPolicy):
        expiry: Optional[Union[datetime, str]]
        permission: Optional[str]
        start: Optional[Union[datetime, str]]

        def __init__(
                self, 
                *, 
                expiry: Union[datetime, str] = ..., 
                permission: Optional[str] = ..., 
                start: Union[datetime, str] = ..., 
                **kwargs
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.data.tables.TableAnalyticsLogging(GeneratedLogging):
        delete: bool
        read: bool
        retention_policy: TableRetentionPolicy
        version: str
        write: bool

        def __init__(
                self, 
                *, 
                delete: Optional[bool] = ..., 
                read: Optional[bool] = ..., 
                retention_policy: Optional[TableRetentionPolicy] = ..., 
                version: Optional[str] = ..., 
                write: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.data.tables.TableClient(TablesBaseClient): implements ContextManager 
        property api_version: str    # Read-only
        property url: str    # Read-only
        account_name: str
        api_version: str
        credential: AzureNamedKeyCredential or
        decoder_map: Union[dict[EdmType, Callable[[Any], Tuple[Optional[EdmType], Union[str, bool, int]]]], None]
        encoder_map: Union[dict[Union[Type, EdmType], Callable[[Any], Tuple[Optional[EdmType], Union[str, bool, int]]]], None]
        flatten_result_entity: bool
        scheme: str
        table_name: str
        url: str

        def __init__(
                self, 
                endpoint: str, 
                table_name: str, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[AudienceType] = ..., 
                credential: Optional[Union[AzureSasCredential, AzureNamedKeyCredential, TokenCredential]] = ..., 
                decoder_map: Optional[DecoderMapType] = ..., 
                encoder_map: Optional[EncoderMapType] = ..., 
                flatten_result_entity: bool = False, 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                table_name: str, 
                **kwargs: Any
            ) -> TableClient: ...

        @classmethod
        def from_table_url(
                cls, 
                table_url: str, 
                *, 
                credential: Optional[Union[AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = ..., 
                **kwargs: Any
            ) -> TableClient: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_entity(
                self, 
                entity: EntityType, 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def create_table(self, **kwargs) -> TableItem: ...

        @overload
        def delete_entity(
                self, 
                partition_key: str, 
                row_key: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def delete_entity(
                self, 
                entity: EntityType, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_table(self, **kwargs) -> None: ...

        @distributed_trace
        def get_entity(
                self, 
                partition_key: str, 
                row_key: str, 
                *, 
                select: Optional[Union[str, List[str]]] = ..., 
                **kwargs
            ) -> TableEntity: ...

        @distributed_trace
        def get_table_access_policy(self, **kwargs) -> Dict[str, Optional[TableAccessPolicy]]: ...

        @distributed_trace
        def list_entities(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                select: Optional[Union[str, List[str]]] = ..., 
                **kwargs
            ) -> ItemPaged[TableEntity]: ...

        @distributed_trace
        def query_entities(
                self, 
                query_filter: str, 
                *, 
                parameters: Optional[Dict[str, Any]] = ..., 
                results_per_page: Optional[int] = ..., 
                select: Optional[Union[str, List[str]]] = ..., 
                **kwargs
            ) -> ItemPaged[TableEntity]: ...

        @distributed_trace
        def set_table_access_policy(
                self, 
                signed_identifiers: Mapping[str, Optional[TableAccessPolicy]], 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def submit_transaction(
                self, 
                operations: Iterable[TransactionOperationType], 
                **kwargs
            ) -> List[Mapping[str, Any]]: ...

        @distributed_trace
        def update_entity(
                self, 
                entity: EntityType, 
                mode: Union[str, UpdateMode] = UpdateMode.MERGE, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def upsert_entity(
                self, 
                entity: EntityType, 
                mode: Union[str, UpdateMode] = UpdateMode.MERGE, 
                **kwargs
            ) -> Dict[str, Any]: ...


    class azure.data.tables.TableCorsRule:
        allowed_headers: List[str]
        allowed_methods: List[str]
        allowed_origins: List[str]
        exposed_headers: List[str]
        max_age_in_seconds: int

        def __init__(
                self, 
                allowed_origins: List[str], 
                allowed_methods: List[str], 
                *, 
                allowed_headers: Optional[list[str]] = ..., 
                exposed_headers: Optional[list[str]] = ..., 
                max_age_in_seconds: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.data.tables.TableEntity(dict):
        property metadata: EntityMetadata    # Read-only


    class azure.data.tables.TableErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT_ALREADY_EXISTS = "AccountAlreadyExists"
        ACCOUNT_BEING_CREATED = "AccountBeingCreated"
        ACCOUNT_IS_DISABLED = "AccountIsDisabled"
        AUTHENTICATION_FAILED = "AuthenticationFailed"
        AUTHORIZATION_FAILURE = "AuthorizationFailure"
        CONDITION_HEADERS_NOT_SUPPORTED = "ConditionHeadersNotSupported"
        CONDITION_NOT_MET = "ConditionNotMet"
        DUPLICATE_PROPERTIES_SPECIFIED = "DuplicatePropertiesSpecified"
        EMPTY_METADATA_KEY = "EmptyMetadataKey"
        ENTITY_ALREADY_EXISTS = "EntityAlreadyExists"
        ENTITY_NOT_FOUND = "EntityNotFound"
        ENTITY_TOO_LARGE = "EntityTooLarge"
        HOST_INFORMATION_NOT_PRESENT = "HostInformationNotPresent"
        INSUFFICIENT_ACCOUNT_PERMISSIONS = "InsufficientAccountPermissions"
        INTERNAL_ERROR = "InternalError"
        INVALID_AUTHENTICATION_INFO = "InvalidAuthenticationInfo"
        INVALID_DUPLICATE_ROW = "InvalidDuplicateRow"
        INVALID_HEADER_VALUE = "InvalidHeaderValue"
        INVALID_HTTP_VERB = "InvalidHttpVerb"
        INVALID_INPUT = "InvalidInput"
        INVALID_MD5 = "InvalidMd5"
        INVALID_METADATA = "InvalidMetadata"
        INVALID_QUERY_PARAMETER_VALUE = "InvalidQueryParameterValue"
        INVALID_RANGE = "InvalidRange"
        INVALID_RESOURCE_NAME = "InvalidResourceName"
        INVALID_URI = "InvalidUri"
        INVALID_VALUE_TYPE = "InvalidValueType"
        INVALID_XML_DOCUMENT = "InvalidXmlDocument"
        INVALID_XML_NODE_VALUE = "InvalidXmlNodeValue"
        JSON_FORMAT_NOT_SUPPORTED = "JsonFormatNotSupported"
        MD5_MISMATCH = "Md5Mismatch"
        METADATA_TOO_LARGE = "MetadataTooLarge"
        METHOD_NOT_ALLOWED = "MethodNotAllowed"
        MISSING_CONTENT_LENGTH_HEADER = "MissingContentLengthHeader"
        MISSING_REQUIRED_HEADER = "MissingRequiredHeader"
        MISSING_REQUIRED_QUERY_PARAMETER = "MissingRequiredQueryParameter"
        MISSING_REQUIRED_XML_NODE = "MissingRequiredXmlNode"
        MULTIPLE_CONDITION_HEADERS_NOT_SUPPORTED = "MultipleConditionHeadersNotSupported"
        NOT_IMPLEMENTED = "NotImplemented"
        NO_AUTHENTICATION_INFORMATION = "NoAuthenticationInformation"
        OPERATION_TIMED_OUT = "OperationTimedOut"
        OUT_OF_RANGE_INPUT = "OutOfRangeInput"
        OUT_OF_RANGE_QUERY_PARAMETER_VALUE = "OutOfRangeQueryParameterValue"
        PROPERTIES_NEED_VALUE = "PropertiesNeedValue"
        PROPERTY_NAME_INVALID = "PropertyNameInvalid"
        PROPERTY_NAME_TOO_LONG = "PropertyNameTooLong"
        PROPERTY_VALUE_TOO_LARGE = "PropertyValueTooLarge"
        REQUEST_BODY_TOO_LARGE = "RequestBodyTooLarge"
        REQUEST_URL_FAILED_TO_PARSE = "RequestUrlFailedToParse"
        RESOURCE_ALREADY_EXISTS = "ResourceAlreadyExists"
        RESOURCE_NOT_FOUND = "ResourceNotFound"
        RESOURCE_TYPE_MISMATCH = "ResourceTypeMismatch"
        SERVER_BUSY = "ServerBusy"
        TABLE_ALREADY_EXISTS = "TableAlreadyExists"
        TABLE_BEING_DELETED = "TableBeingDeleted"
        TABLE_NOT_FOUND = "TableNotFound"
        TOO_MANY_PROPERTIES = "TooManyProperties"
        UNSUPPORTED_HEADER = "UnsupportedHeader"
        UNSUPPORTED_HTTP_VERB = "UnsupportedHttpVerb"
        UNSUPPORTED_QUERY_PARAMETER = "UnsupportedQueryParameter"
        UNSUPPORTED_XML_NODE = "UnsupportedXmlNode"
        UPDATE_CONDITION_NOT_SATISFIED = "UpdateConditionNotSatisfied"
        X_METHOD_INCORRECT_COUNT = "XMethodIncorrectCount"
        X_METHOD_INCORRECT_VALUE = "XMethodIncorrectValue"
        X_METHOD_NOT_USING_POST = "XMethodNotUsingPost"


    class azure.data.tables.TableItem:
        name: str

        def __init__(self, name: str) -> None: ...

        def __repr__(self) -> str: ...


    class azure.data.tables.TableMetrics(GeneratedMetrics):
        enabled: bool
        include_apis: Optional[bool]
        retention_policy: TableRetentionPolicy
        version: str

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                include_apis: Optional[bool] = ..., 
                retention_policy: Optional[TableRetentionPolicy] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.data.tables.TableRetentionPolicy(GeneratedRetentionPolicy):
        days: Optional[int]
        enabled: bool

        def __init__(
                self, 
                *, 
                days: Optional[int] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.data.tables.TableSasPermissions:
        add: bool
        delete: bool
        read: bool
        update: bool

        def __add__(self, other: TableSasPermissions) -> TableSasPermissions: ...

        def __init__(
                self, 
                *, 
                add: Optional[bool] = ..., 
                delete: Optional[bool] = ..., 
                read: Optional[bool] = ..., 
                update: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __or__(self, other: TableSasPermissions) -> TableSasPermissions: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        @classmethod
        def from_string(
                cls, 
                permission: str, 
                **kwargs: Any
            ) -> TableSasPermissions: ...


    class azure.data.tables.TableServiceClient(TablesBaseClient): implements ContextManager 
        property api_version: str    # Read-only
        property url: str    # Read-only
        account_name: str
        url: str

        def __init__(
                self, 
                endpoint: str, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[AudienceType] = ..., 
                credential: Optional[Union[AzureSasCredential, AzureNamedKeyCredential, TokenCredential]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> TableServiceClient: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_table(
                self, 
                table_name: str, 
                **kwargs
            ) -> TableClient: ...

        @distributed_trace
        def create_table_if_not_exists(
                self, 
                table_name: str, 
                **kwargs
            ) -> TableClient: ...

        @distributed_trace
        def delete_table(
                self, 
                table_name: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_service_properties(self, **kwargs) -> Dict[str, object]: ...

        @distributed_trace
        def get_service_stats(self, **kwargs) -> Dict[str, object]: ...

        def get_table_client(
                self, 
                table_name: str, 
                **kwargs: Any
            ) -> TableClient: ...

        @distributed_trace
        def list_tables(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs
            ) -> ItemPaged[TableItem]: ...

        @distributed_trace
        def query_tables(
                self, 
                query_filter: str, 
                *, 
                parameters: Optional[Dict[str, Any]] = ..., 
                results_per_page: Optional[int] = ..., 
                **kwargs
            ) -> ItemPaged[TableItem]: ...

        @distributed_trace
        def set_service_properties(
                self, 
                *, 
                analytics_logging: Optional[TableAnalyticsLogging] = ..., 
                cors: Optional[List[TableCorsRule]] = ..., 
                hour_metrics: Optional[TableMetrics] = ..., 
                minute_metrics: Optional[TableMetrics] = ..., 
                **kwargs
            ) -> None: ...


    class azure.data.tables.TableTransactionError(HttpResponseError):
        additional_info: Mapping[str, Any]
        error_code: TableErrorCode
        index: int
        message: str

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.data.tables.TransactionOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "create"
        DELETE = "delete"
        UPDATE = "update"
        UPSERT = "upsert"


    class azure.data.tables.UpdateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MERGE = "merge"
        REPLACE = "replace"


namespace azure.data.tables.aio

    class azure.data.tables.aio.TableClient(AsyncTablesBaseClient): implements AsyncContextManager 
        property api_version: str    # Read-only
        property url: str    # Read-only
        account_name: str
        api_version: str
        credential: AzureNamedKeyCredential or
        decoder_map: Union[dict[EdmType, Callable[[Any], Tuple[Optional[EdmType], Union[str, bool, int]]]], None]
        encoder_map: Union[dict[Union[Type, EdmType], Callable[[Any], Tuple[Optional[EdmType], Union[str, bool, int]]]], None]
        flatten_result_entity: bool
        scheme: str
        table_name: str
        url: str

        def __init__(
                self, 
                endpoint: str, 
                table_name: str, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[AudienceType] = ..., 
                credential: Optional[Union[AzureSasCredential, AzureNamedKeyCredential, AsyncTokenCredential]] = ..., 
                decoder_map: Optional[DecoderMapType] = ..., 
                encoder_map: Optional[EncoderMapType] = ..., 
                flatten_result_entity: bool = False, 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                table_name: str, 
                **kwargs: Any
            ) -> TableClient: ...

        @classmethod
        def from_table_url(
                cls, 
                table_url: str, 
                *, 
                credential: Optional[Union[AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]] = ..., 
                **kwargs: Any
            ) -> TableClient: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_entity(
                self, 
                entity: EntityType, 
                **kwargs
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def create_table(self, **kwargs) -> TableItem: ...

        @overload
        async def delete_entity(
                self, 
                partition_key: str, 
                row_key: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def delete_entity(
                self, 
                entity: EntityType, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_table(self, **kwargs) -> None: ...

        @distributed_trace_async
        async def get_entity(
                self, 
                partition_key: str, 
                row_key: str, 
                *, 
                select: Optional[Union[str, List[str]]] = ..., 
                **kwargs
            ) -> TableEntity: ...

        @distributed_trace_async
        async def get_table_access_policy(self, **kwargs) -> Mapping[str, Optional[TableAccessPolicy]]: ...

        @distributed_trace
        def list_entities(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                select: Optional[Union[str, List[str]]] = ..., 
                **kwargs
            ) -> AsyncItemPaged[TableEntity]: ...

        @distributed_trace
        def query_entities(
                self, 
                query_filter: str, 
                *, 
                parameters: Optional[Dict[str, Any]] = ..., 
                results_per_page: Optional[int] = ..., 
                select: Optional[Union[str, List[str]]] = ..., 
                **kwargs
            ) -> AsyncItemPaged[TableEntity]: ...

        @distributed_trace_async
        async def set_table_access_policy(
                self, 
                signed_identifiers: Mapping[str, Optional[TableAccessPolicy]], 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def submit_transaction(
                self, 
                operations: Iterable[TransactionOperationType], 
                **kwargs
            ) -> List[Mapping[str, Any]]: ...

        @distributed_trace_async
        async def update_entity(
                self, 
                entity: EntityType, 
                mode: Union[str, UpdateMode] = UpdateMode.MERGE, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def upsert_entity(
                self, 
                entity: EntityType, 
                mode: Union[str, UpdateMode] = UpdateMode.MERGE, 
                **kwargs
            ) -> Dict[str, Any]: ...


    class azure.data.tables.aio.TableServiceClient(AsyncTablesBaseClient): implements AsyncContextManager 
        property api_version: str    # Read-only
        property url: str    # Read-only
        account_name: str
        url: str

        def __init__(
                self, 
                endpoint: str, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[AudienceType] = ..., 
                credential: Optional[Union[AzureSasCredential, AzureNamedKeyCredential, AsyncTokenCredential]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> TableServiceClient: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_table(
                self, 
                table_name: str, 
                **kwargs
            ) -> TableClient: ...

        @distributed_trace_async
        async def create_table_if_not_exists(
                self, 
                table_name: str, 
                **kwargs
            ) -> TableClient: ...

        @distributed_trace_async
        async def delete_table(
                self, 
                table_name: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_service_properties(self, **kwargs) -> Dict[str, object]: ...

        @distributed_trace_async
        async def get_service_stats(self, **kwargs) -> Dict[str, object]: ...

        def get_table_client(
                self, 
                table_name: str, 
                **kwargs: Any
            ) -> TableClient: ...

        @distributed_trace
        def list_tables(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs
            ) -> AsyncItemPaged[TableItem]: ...

        @distributed_trace
        def query_tables(
                self, 
                query_filter: str, 
                *, 
                parameters: Optional[Dict[str, Any]] = ..., 
                results_per_page: Optional[int] = ..., 
                **kwargs
            ) -> AsyncItemPaged[TableItem]: ...

        @distributed_trace_async
        async def set_service_properties(
                self, 
                *, 
                analytics_logging: Optional[TableAnalyticsLogging] = ..., 
                cors: Optional[List[TableCorsRule]] = ..., 
                hour_metrics: Optional[TableMetrics] = ..., 
                minute_metrics: Optional[TableMetrics] = ..., 
                **kwargs
            ) -> None: ...


```