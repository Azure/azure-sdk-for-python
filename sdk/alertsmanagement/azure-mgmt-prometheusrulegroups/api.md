```py
namespace azure.mgmt.prometheusrulegroups

    class azure.mgmt.prometheusrulegroups.PrometheusRuleGroupsMgmtClient: implements ContextManager 
        prometheus_rule_groups: PrometheusRuleGroupsOperations

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


namespace azure.mgmt.prometheusrulegroups.aio

    class azure.mgmt.prometheusrulegroups.aio.PrometheusRuleGroupsMgmtClient: implements AsyncContextManager 
        prometheus_rule_groups: PrometheusRuleGroupsOperations

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


namespace azure.mgmt.prometheusrulegroups.aio.operations

    class azure.mgmt.prometheusrulegroups.aio.operations.PrometheusRuleGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: PrometheusRuleGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: PrometheusRuleGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrometheusRuleGroupResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[PrometheusRuleGroupResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: PrometheusRuleGroupResourcePatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: PrometheusRuleGroupResourcePatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...


namespace azure.mgmt.prometheusrulegroups.models

    class azure.mgmt.prometheusrulegroups.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.prometheusrulegroups.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.prometheusrulegroups.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.prometheusrulegroups.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.prometheusrulegroups.models.PrometheusRule(_Model):
        actions: Optional[list[PrometheusRuleGroupAction]]
        alert: Optional[str]
        annotations: Optional[dict[str, str]]
        enabled: Optional[bool]
        expression: str
        for_property: Optional[timedelta]
        labels: Optional[dict[str, str]]
        record: Optional[str]
        resolve_configuration: Optional[PrometheusRuleResolveConfiguration]
        severity: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[PrometheusRuleGroupAction]] = ..., 
                alert: Optional[str] = ..., 
                annotations: Optional[dict[str, str]] = ..., 
                enabled: Optional[bool] = ..., 
                expression: str, 
                for_property: Optional[timedelta] = ..., 
                labels: Optional[dict[str, str]] = ..., 
                record: Optional[str] = ..., 
                resolve_configuration: Optional[PrometheusRuleResolveConfiguration] = ..., 
                severity: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.prometheusrulegroups.models.PrometheusRuleGroupAction(_Model):
        action_group_id: Optional[str]
        action_properties: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                action_group_id: Optional[str] = ..., 
                action_properties: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.prometheusrulegroups.models.PrometheusRuleGroupProperties(_Model):
        cluster_name: Optional[str]
        description: Optional[str]
        enabled: Optional[bool]
        interval: Optional[timedelta]
        rules: list[PrometheusRule]
        scopes: list[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_name: Optional[str] = ..., 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                interval: Optional[timedelta] = ..., 
                rules: list[PrometheusRule], 
                scopes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.prometheusrulegroups.models.PrometheusRuleGroupResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: PrometheusRuleGroupProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: PrometheusRuleGroupProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.prometheusrulegroups.models.PrometheusRuleGroupResourcePatchParameters(_Model):
        properties: Optional[PrometheusRuleGroupResourcePatchParametersProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrometheusRuleGroupResourcePatchParametersProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.prometheusrulegroups.models.PrometheusRuleGroupResourcePatchParametersProperties(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.prometheusrulegroups.models.PrometheusRuleResolveConfiguration(_Model):
        auto_resolved: Optional[bool]
        time_to_resolve: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                auto_resolved: Optional[bool] = ..., 
                time_to_resolve: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.prometheusrulegroups.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.prometheusrulegroups.models.SystemData(_Model):
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


    class azure.mgmt.prometheusrulegroups.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.prometheusrulegroups.operations

    class azure.mgmt.prometheusrulegroups.operations.PrometheusRuleGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: PrometheusRuleGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: PrometheusRuleGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrometheusRuleGroupResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[PrometheusRuleGroupResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: PrometheusRuleGroupResourcePatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: PrometheusRuleGroupResourcePatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...


namespace azure.mgmt.prometheusrulegroups.types

    class azure.mgmt.prometheusrulegroups.types.PrometheusRule(TypedDict):
        key "alert": str
        key "enabled": bool
        key "expression": Required[str]
        key "for": str
        key "record": str
        key "resolveConfiguration": ForwardRef('PrometheusRuleResolveConfiguration', module='types')
        key "severity": int
        actions: list[PrometheusRuleGroupAction]
        alert: str
        annotations: dict[str, str]
        enabled: bool
        expression: str
        for_property: str
        labels: dict[str, str]
        record: str
        resolve_configuration: PrometheusRuleResolveConfiguration
        severity: int


    class azure.mgmt.prometheusrulegroups.types.PrometheusRuleGroupAction(TypedDict, total=False):
        key "actionGroupId": str
        actionProperties: dict[str, str]
        action_group_id: str
        action_properties: dict[str, str]


    class azure.mgmt.prometheusrulegroups.types.PrometheusRuleGroupProperties(TypedDict, total=False):
        key "clusterName": str
        key "description": str
        key "enabled": bool
        key "interval": str
        key "rules": Required[list[PrometheusRule]]
        key "scopes": Required[list[str]]
        cluster_name: str
        description: str
        enabled: bool
        interval: str
        rules: list[PrometheusRule]
        scopes: list[str]


    class azure.mgmt.prometheusrulegroups.types.PrometheusRuleGroupResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[PrometheusRuleGroupProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: PrometheusRuleGroupProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.prometheusrulegroups.types.PrometheusRuleGroupResourcePatchParameters(TypedDict, total=False):
        key "properties": ForwardRef('PrometheusRuleGroupResourcePatchParametersProperties', module='types')
        properties: PrometheusRuleGroupResourcePatchParametersProperties
        tags: dict[str, str]


    class azure.mgmt.prometheusrulegroups.types.PrometheusRuleGroupResourcePatchParametersProperties(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.prometheusrulegroups.types.PrometheusRuleResolveConfiguration(TypedDict, total=False):
        key "autoResolved": bool
        key "timeToResolve": str
        auto_resolved: bool
        time_to_resolve: str


    class azure.mgmt.prometheusrulegroups.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.prometheusrulegroups.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.prometheusrulegroups.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


```