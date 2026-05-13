```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.alertsmanagement

    class azure.mgmt.alertsmanagement.AlertsManagementClient: implements ContextManager 
        alert_processing_rules: AlertProcessingRulesOperations
        alerts: AlertsOperations
        operations: Operations
        prometheus_rule_groups: PrometheusRuleGroupsOperations
        smart_groups: SmartGroupsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.alertsmanagement.aio

    class azure.mgmt.alertsmanagement.aio.AlertsManagementClient: implements AsyncContextManager 
        alert_processing_rules: AlertProcessingRulesOperations
        alerts: AlertsOperations
        operations: Operations
        prometheus_rule_groups: PrometheusRuleGroupsOperations
        smart_groups: SmartGroupsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.alertsmanagement.aio.operations

    class azure.mgmt.alertsmanagement.aio.operations.AlertProcessingRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule: AlertProcessingRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_by_name(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AlertProcessingRule]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AlertProcessingRule]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule_patch: PatchObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule_patch: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...


    class azure.mgmt.alertsmanagement.aio.operations.AlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def change_state(
                self, 
                alert_id: str, 
                new_state: Union[str, AlertState], 
                comment: Optional[Comments] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @overload
        async def change_state(
                self, 
                alert_id: str, 
                new_state: Union[str, AlertState], 
                comment: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def get_all(
                self, 
                target_resource: Optional[str] = None, 
                target_resource_type: Optional[str] = None, 
                target_resource_group: Optional[str] = None, 
                monitor_service: Optional[Union[str, MonitorService]] = None, 
                monitor_condition: Optional[Union[str, MonitorCondition]] = None, 
                severity: Optional[Union[str, Severity]] = None, 
                alert_state: Optional[Union[str, AlertState]] = None, 
                alert_rule: Optional[str] = None, 
                smart_group_id: Optional[str] = None, 
                include_context: Optional[bool] = None, 
                include_egress_config: Optional[bool] = None, 
                page_count: Optional[int] = None, 
                sort_by: Optional[Union[str, AlertsSortByFields]] = None, 
                sort_order: Optional[Union[str, SortOrder]] = None, 
                select: Optional[str] = None, 
                time_range: Optional[Union[str, TimeRange]] = None, 
                custom_time_range: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Alert]: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                alert_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace_async
        async def get_history(
                self, 
                alert_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertModification: ...

        @distributed_trace_async
        async def get_summary(
                self, 
                groupby: Union[str, AlertsSummaryGroupByFields], 
                include_smart_groups_count: Optional[bool] = None, 
                target_resource: Optional[str] = None, 
                target_resource_type: Optional[str] = None, 
                target_resource_group: Optional[str] = None, 
                monitor_service: Optional[Union[str, MonitorService]] = None, 
                monitor_condition: Optional[Union[str, MonitorCondition]] = None, 
                severity: Optional[Union[str, Severity]] = None, 
                alert_state: Optional[Union[str, AlertState]] = None, 
                alert_rule: Optional[str] = None, 
                time_range: Optional[Union[str, TimeRange]] = None, 
                custom_time_range: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertsSummary: ...

        @distributed_trace_async
        async def meta_data(
                self, 
                identifier: Union[str, Identifier], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertsMetaData: ...


    class azure.mgmt.alertsmanagement.aio.operations.Operations:

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


    class azure.mgmt.alertsmanagement.aio.operations.PrometheusRuleGroupsOperations:

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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PrometheusRuleGroupResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PrometheusRuleGroupResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: PrometheusRuleGroupResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...


    class azure.mgmt.alertsmanagement.aio.operations.SmartGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def change_state(
                self, 
                smart_group_id: str, 
                new_state: Union[str, AlertState], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SmartGroup: ...

        @distributed_trace
        def get_all(
                self, 
                target_resource: Optional[str] = None, 
                target_resource_group: Optional[str] = None, 
                target_resource_type: Optional[str] = None, 
                monitor_service: Optional[Union[str, MonitorService]] = None, 
                monitor_condition: Optional[Union[str, MonitorCondition]] = None, 
                severity: Optional[Union[str, Severity]] = None, 
                smart_group_state: Optional[Union[str, AlertState]] = None, 
                time_range: Optional[Union[str, TimeRange]] = None, 
                page_count: Optional[int] = None, 
                sort_by: Optional[Union[str, SmartGroupsSortByFields]] = None, 
                sort_order: Optional[Union[str, SortOrder]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SmartGroup]: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                smart_group_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SmartGroup: ...

        @distributed_trace_async
        async def get_history(
                self, 
                smart_group_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SmartGroupModification: ...


namespace azure.mgmt.alertsmanagement.models

    class azure.mgmt.alertsmanagement.models.Action(Model):
        action_type: Union[str, ActionType]

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


    class azure.mgmt.alertsmanagement.models.ActionStatus(Model):
        is_suppressed: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                is_suppressed: Optional[bool] = ..., 
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


    class azure.mgmt.alertsmanagement.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_ACTION_GROUPS = "AddActionGroups"
        REMOVE_ALL_ACTION_GROUPS = "RemoveAllActionGroups"


    class azure.mgmt.alertsmanagement.models.AddActionGroups(Action):
        action_group_ids: list[str]
        action_type: Union[str, ActionType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                action_group_ids: List[str], 
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


    class azure.mgmt.alertsmanagement.models.Alert(Resource):
        id: str
        name: str
        properties: AlertProperties
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[AlertProperties] = ..., 
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


    class azure.mgmt.alertsmanagement.models.AlertModification(Resource):
        id: str
        name: str
        properties: AlertModificationProperties
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[AlertModificationProperties] = ..., 
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


    class azure.mgmt.alertsmanagement.models.AlertModificationEvent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIONS_FAILED = "ActionsFailed"
        ACTIONS_SUPPRESSED = "ActionsSuppressed"
        ACTIONS_TRIGGERED = "ActionsTriggered"
        ACTION_RULE_SUPPRESSED = "ActionRuleSuppressed"
        ACTION_RULE_TRIGGERED = "ActionRuleTriggered"
        ALERT_CREATED = "AlertCreated"
        MONITOR_CONDITION_CHANGE = "MonitorConditionChange"
        SEVERITY_CHANGE = "SeverityChange"
        STATE_CHANGE = "StateChange"


    class azure.mgmt.alertsmanagement.models.AlertModificationItem(Model):
        comments: str
        description: str
        modification_event: Union[str, AlertModificationEvent]
        modified_at: str
        modified_by: str
        new_value: str
        old_value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                comments: Optional[str] = ..., 
                description: Optional[str] = ..., 
                modification_event: Optional[Union[str, AlertModificationEvent]] = ..., 
                modified_at: Optional[str] = ..., 
                modified_by: Optional[str] = ..., 
                new_value: Optional[str] = ..., 
                old_value: Optional[str] = ..., 
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


    class azure.mgmt.alertsmanagement.models.AlertModificationProperties(Model):
        alert_id: str
        modifications: list[AlertModificationItem]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                modifications: Optional[List[AlertModificationItem]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.AlertProcessingRule(ManagedResource):
        id: str
        location: str
        name: str
        properties: AlertProcessingRuleProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AlertProcessingRuleProperties] = ..., 
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


    class azure.mgmt.alertsmanagement.models.AlertProcessingRuleProperties(Model):
        actions: list[Action]
        conditions: list[Condition]
        description: str
        enabled: bool
        schedule: Schedule
        scopes: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                actions: List[Action], 
                conditions: Optional[List[Condition]] = ..., 
                description: Optional[str] = ..., 
                enabled: bool = True, 
                schedule: Optional[Schedule] = ..., 
                scopes: List[str], 
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


    class azure.mgmt.alertsmanagement.models.AlertProcessingRulesList(Model):
        next_link: str
        value: list[AlertProcessingRule]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AlertProcessingRule]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.AlertProperties(Model):
        context: JSON
        egress_config: JSON
        essentials: Essentials

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                essentials: Optional[Essentials] = ..., 
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


    class azure.mgmt.alertsmanagement.models.AlertState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACKNOWLEDGED = "Acknowledged"
        CLOSED = "Closed"
        NEW = "New"


    class azure.mgmt.alertsmanagement.models.AlertsList(Model):
        next_link: str
        value: list[Alert]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Alert]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.AlertsMetaData(Model):
        properties: AlertsMetaDataProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[AlertsMetaDataProperties] = ..., 
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


    class azure.mgmt.alertsmanagement.models.AlertsMetaDataProperties(Model):
        metadata_identifier: Union[str, MetadataIdentifier]

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


    class azure.mgmt.alertsmanagement.models.AlertsSortByFields(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT_STATE = "alertState"
        LAST_MODIFIED_DATE_TIME = "lastModifiedDateTime"
        MONITOR_CONDITION = "monitorCondition"
        NAME = "name"
        SEVERITY = "severity"
        START_DATE_TIME = "startDateTime"
        TARGET_RESOURCE = "targetResource"
        TARGET_RESOURCE_GROUP = "targetResourceGroup"
        TARGET_RESOURCE_NAME = "targetResourceName"
        TARGET_RESOURCE_TYPE = "targetResourceType"


    class azure.mgmt.alertsmanagement.models.AlertsSummary(Resource):
        id: str
        name: str
        properties: AlertsSummaryGroup
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[AlertsSummaryGroup] = ..., 
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


    class azure.mgmt.alertsmanagement.models.AlertsSummaryGroup(Model):
        groupedby: str
        smart_groups_count: int
        total: int
        values: list[AlertsSummaryGroupItem]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                groupedby: Optional[str] = ..., 
                smart_groups_count: Optional[int] = ..., 
                total: Optional[int] = ..., 
                values: Optional[List[AlertsSummaryGroupItem]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.AlertsSummaryGroupByFields(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT_RULE = "alertRule"
        ALERT_STATE = "alertState"
        MONITOR_CONDITION = "monitorCondition"
        MONITOR_SERVICE = "monitorService"
        SEVERITY = "severity"
        SIGNAL_TYPE = "signalType"


    class azure.mgmt.alertsmanagement.models.AlertsSummaryGroupItem(Model):
        count: int
        groupedby: str
        name: str
        values: list[AlertsSummaryGroupItem]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                groupedby: Optional[str] = ..., 
                name: Optional[str] = ..., 
                values: Optional[List[AlertsSummaryGroupItem]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.Comments(Model):
        comments: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                comments: Optional[str] = ..., 
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


    class azure.mgmt.alertsmanagement.models.Condition(Model):
        field: Union[str, Field]
        operator: Union[str, Operator]
        values: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                field: Optional[Union[str, Field]] = ..., 
                operator: Optional[Union[str, Operator]] = ..., 
                values: Optional[List[str]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.alertsmanagement.models.DailyRecurrence(Recurrence):
        end_time: str
        recurrence_type: Union[str, RecurrenceType]
        start_time: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
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


    class azure.mgmt.alertsmanagement.models.DaysOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.alertsmanagement.models.ErrorAdditionalInfo(Model):
        info: JSON
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


    class azure.mgmt.alertsmanagement.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

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


    class azure.mgmt.alertsmanagement.models.ErrorResponse(Model):
        error: ErrorResponseBody

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseBody] = ..., 
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


    class azure.mgmt.alertsmanagement.models.ErrorResponseAutoGenerated(Model):
        error: ErrorDetail

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
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


    class azure.mgmt.alertsmanagement.models.ErrorResponseAutoGenerated2(Model):
        error: ErrorResponseBodyAutoGenerated

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseBodyAutoGenerated] = ..., 
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


    class azure.mgmt.alertsmanagement.models.ErrorResponseAutoGenerated3(Model):
        error: ErrorResponseBodyAutoGenerated2

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseBodyAutoGenerated2] = ..., 
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


    class azure.mgmt.alertsmanagement.models.ErrorResponseBody(Model):
        code: str
        details: list[ErrorResponseBody]
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[ErrorResponseBody]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.ErrorResponseBodyAutoGenerated(Model):
        code: str
        details: list[ErrorResponseBodyAutoGenerated]
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[ErrorResponseBodyAutoGenerated]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.ErrorResponseBodyAutoGenerated2(Model):
        code: str
        details: list[ErrorResponseBodyAutoGenerated2]
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[ErrorResponseBodyAutoGenerated2]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.Essentials(Model):
        action_status: ActionStatus
        alert_rule: str
        alert_state: Union[str, AlertState]
        description: str
        last_modified_date_time: datetime
        last_modified_user_name: str
        monitor_condition: Union[str, MonitorCondition]
        monitor_condition_resolved_date_time: datetime
        monitor_service: Union[str, MonitorService]
        severity: Union[str, Severity]
        signal_type: Union[str, SignalType]
        smart_group_id: str
        smart_grouping_reason: str
        source_created_id: str
        start_date_time: datetime
        target_resource: str
        target_resource_group: str
        target_resource_name: str
        target_resource_type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                action_status: Optional[ActionStatus] = ..., 
                description: Optional[str] = ..., 
                target_resource: Optional[str] = ..., 
                target_resource_group: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                target_resource_type: Optional[str] = ..., 
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


    class azure.mgmt.alertsmanagement.models.Field(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT_CONTEXT = "AlertContext"
        ALERT_RULE_ID = "AlertRuleId"
        ALERT_RULE_NAME = "AlertRuleName"
        DESCRIPTION = "Description"
        MONITOR_CONDITION = "MonitorCondition"
        MONITOR_SERVICE = "MonitorService"
        SEVERITY = "Severity"
        SIGNAL_TYPE = "SignalType"
        TARGET_RESOURCE = "TargetResource"
        TARGET_RESOURCE_GROUP = "TargetResourceGroup"
        TARGET_RESOURCE_TYPE = "TargetResourceType"


    class azure.mgmt.alertsmanagement.models.Identifier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONITOR_SERVICE_LIST = "MonitorServiceList"


    class azure.mgmt.alertsmanagement.models.ManagedResource(Resource):
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


    class azure.mgmt.alertsmanagement.models.MetadataIdentifier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONITOR_SERVICE_LIST = "MonitorServiceList"


    class azure.mgmt.alertsmanagement.models.MonitorCondition(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIRED = "Fired"
        RESOLVED = "Resolved"


    class azure.mgmt.alertsmanagement.models.MonitorService(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY_LOG_ADMINISTRATIVE = "ActivityLog Administrative"
        ACTIVITY_LOG_AUTOSCALE = "ActivityLog Autoscale"
        ACTIVITY_LOG_POLICY = "ActivityLog Policy"
        ACTIVITY_LOG_RECOMMENDATION = "ActivityLog Recommendation"
        ACTIVITY_LOG_SECURITY = "ActivityLog Security"
        APPLICATION_INSIGHTS = "Application Insights"
        LOG_ANALYTICS = "Log Analytics"
        NAGIOS = "Nagios"
        PLATFORM = "Platform"
        SCOM = "SCOM"
        SERVICE_HEALTH = "ServiceHealth"
        SMART_DETECTOR = "SmartDetector"
        VM_INSIGHTS = "VM Insights"
        ZABBIX = "Zabbix"


    class azure.mgmt.alertsmanagement.models.MonitorServiceDetails(Model):
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


    class azure.mgmt.alertsmanagement.models.MonitorServiceList(AlertsMetaDataProperties):
        data: list[MonitorServiceDetails]
        metadata_identifier: Union[str, MetadataIdentifier]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data: List[MonitorServiceDetails], 
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


    class azure.mgmt.alertsmanagement.models.MonthlyRecurrence(Recurrence):
        days_of_month: list[int]
        end_time: str
        recurrence_type: Union[str, RecurrenceType]
        start_time: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                days_of_month: List[int], 
                end_time: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
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


    class azure.mgmt.alertsmanagement.models.Operation(Model):
        display: OperationDisplay
        name: str
        origin: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
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


    class azure.mgmt.alertsmanagement.models.OperationDisplay(Model):
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


    class azure.mgmt.alertsmanagement.models.OperationsList(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Operation], 
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


    class azure.mgmt.alertsmanagement.models.Operator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "Contains"
        DOES_NOT_CONTAIN = "DoesNotContain"
        EQUALS = "Equals"
        NOT_EQUALS = "NotEquals"


    class azure.mgmt.alertsmanagement.models.PatchObject(Model):
        enabled: bool
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
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


    class azure.mgmt.alertsmanagement.models.PrometheusRule(Model):
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

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                actions: Optional[List[PrometheusRuleGroupAction]] = ..., 
                alert: Optional[str] = ..., 
                annotations: Optional[Dict[str, str]] = ..., 
                enabled: Optional[bool] = ..., 
                expression: str, 
                for_property: Optional[str] = ..., 
                labels: Optional[Dict[str, str]] = ..., 
                record: Optional[str] = ..., 
                resolve_configuration: Optional[PrometheusRuleResolveConfiguration] = ..., 
                severity: Optional[int] = ..., 
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


    class azure.mgmt.alertsmanagement.models.PrometheusRuleGroupAction(Model):
        action_group_id: str
        action_properties: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                action_group_id: Optional[str] = ..., 
                action_properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.PrometheusRuleGroupResource(TrackedResource):
        cluster_name: str
        description: str
        enabled: bool
        id: str
        interval: str
        location: str
        name: str
        rules: list[PrometheusRule]
        scopes: list[str]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                cluster_name: Optional[str] = ..., 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                interval: Optional[str] = ..., 
                location: str, 
                rules: List[PrometheusRule], 
                scopes: List[str], 
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


    class azure.mgmt.alertsmanagement.models.PrometheusRuleGroupResourceCollection(Model):
        value: list[PrometheusRuleGroupResource]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrometheusRuleGroupResource]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.PrometheusRuleGroupResourcePatch(Model):
        properties: PrometheusRuleGroupResourcePatchProperties
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[PrometheusRuleGroupResourcePatchProperties] = ..., 
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


    class azure.mgmt.alertsmanagement.models.PrometheusRuleGroupResourcePatchProperties(Model):
        enabled: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
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


    class azure.mgmt.alertsmanagement.models.PrometheusRuleResolveConfiguration(Model):
        auto_resolved: bool
        time_to_resolve: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                auto_resolved: Optional[bool] = ..., 
                time_to_resolve: Optional[str] = ..., 
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


    class azure.mgmt.alertsmanagement.models.Recurrence(Model):
        end_time: str
        recurrence_type: Union[str, RecurrenceType]
        start_time: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
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


    class azure.mgmt.alertsmanagement.models.RecurrenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        MONTHLY = "Monthly"
        WEEKLY = "Weekly"


    class azure.mgmt.alertsmanagement.models.RemoveAllActionGroups(Action):
        action_type: Union[str, ActionType]

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


    class azure.mgmt.alertsmanagement.models.Resource(Model):
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


    class azure.mgmt.alertsmanagement.models.ResourceAutoGenerated(Model):
        id: str
        name: str
        system_data: SystemData
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


    class azure.mgmt.alertsmanagement.models.Schedule(Model):
        effective_from: str
        effective_until: str
        recurrences: list[Recurrence]
        time_zone: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                effective_from: Optional[str] = ..., 
                effective_until: Optional[str] = ..., 
                recurrences: Optional[List[Recurrence]] = ..., 
                time_zone: Optional[str] = ..., 
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


    class azure.mgmt.alertsmanagement.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEV0 = "Sev0"
        SEV1 = "Sev1"
        SEV2 = "Sev2"
        SEV3 = "Sev3"
        SEV4 = "Sev4"


    class azure.mgmt.alertsmanagement.models.SignalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOG = "Log"
        METRIC = "Metric"
        UNKNOWN = "Unknown"


    class azure.mgmt.alertsmanagement.models.SmartGroup(Resource):
        alert_severities: list[SmartGroupAggregatedProperty]
        alert_states: list[SmartGroupAggregatedProperty]
        alerts_count: int
        id: str
        last_modified_date_time: datetime
        last_modified_user_name: str
        monitor_conditions: list[SmartGroupAggregatedProperty]
        monitor_services: list[SmartGroupAggregatedProperty]
        name: str
        next_link: str
        resource_groups: list[SmartGroupAggregatedProperty]
        resource_types: list[SmartGroupAggregatedProperty]
        resources: list[SmartGroupAggregatedProperty]
        severity: Union[str, Severity]
        smart_group_state: Union[str, State]
        start_date_time: datetime
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_severities: Optional[List[SmartGroupAggregatedProperty]] = ..., 
                alert_states: Optional[List[SmartGroupAggregatedProperty]] = ..., 
                alerts_count: Optional[int] = ..., 
                monitor_conditions: Optional[List[SmartGroupAggregatedProperty]] = ..., 
                monitor_services: Optional[List[SmartGroupAggregatedProperty]] = ..., 
                next_link: Optional[str] = ..., 
                resource_groups: Optional[List[SmartGroupAggregatedProperty]] = ..., 
                resource_types: Optional[List[SmartGroupAggregatedProperty]] = ..., 
                resources: Optional[List[SmartGroupAggregatedProperty]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.SmartGroupAggregatedProperty(Model):
        count: int
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
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


    class azure.mgmt.alertsmanagement.models.SmartGroupModification(Resource):
        id: str
        name: str
        properties: SmartGroupModificationProperties
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[SmartGroupModificationProperties] = ..., 
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


    class azure.mgmt.alertsmanagement.models.SmartGroupModificationEvent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT_ADDED = "AlertAdded"
        ALERT_REMOVED = "AlertRemoved"
        SMART_GROUP_CREATED = "SmartGroupCreated"
        STATE_CHANGE = "StateChange"


    class azure.mgmt.alertsmanagement.models.SmartGroupModificationItem(Model):
        comments: str
        description: str
        modification_event: Union[str, SmartGroupModificationEvent]
        modified_at: str
        modified_by: str
        new_value: str
        old_value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                comments: Optional[str] = ..., 
                description: Optional[str] = ..., 
                modification_event: Optional[Union[str, SmartGroupModificationEvent]] = ..., 
                modified_at: Optional[str] = ..., 
                modified_by: Optional[str] = ..., 
                new_value: Optional[str] = ..., 
                old_value: Optional[str] = ..., 
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


    class azure.mgmt.alertsmanagement.models.SmartGroupModificationProperties(Model):
        modifications: list[SmartGroupModificationItem]
        next_link: str
        smart_group_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                modifications: Optional[List[SmartGroupModificationItem]] = ..., 
                next_link: Optional[str] = ..., 
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


    class azure.mgmt.alertsmanagement.models.SmartGroupsList(Model):
        next_link: str
        value: list[SmartGroup]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SmartGroup]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.SmartGroupsSortByFields(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS_COUNT = "alertsCount"
        LAST_MODIFIED_DATE_TIME = "lastModifiedDateTime"
        SEVERITY = "severity"
        START_DATE_TIME = "startDateTime"
        STATE = "state"


    class azure.mgmt.alertsmanagement.models.SortOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASC = "asc"
        DESC = "desc"


    class azure.mgmt.alertsmanagement.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACKNOWLEDGED = "Acknowledged"
        CLOSED = "Closed"
        NEW = "New"


    class azure.mgmt.alertsmanagement.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
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


    class azure.mgmt.alertsmanagement.models.TimeRange(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE_D = "1d"
        ONE_H = "1h"
        SEVEN_D = "7d"
        THIRTY_D = "30d"


    class azure.mgmt.alertsmanagement.models.TrackedResource(ResourceAutoGenerated):
        id: str
        location: str
        name: str
        system_data: SystemData
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


    class azure.mgmt.alertsmanagement.models.WeeklyRecurrence(Recurrence):
        days_of_week: Union[list[str, DaysOfWeek]]
        end_time: str
        recurrence_type: Union[str, RecurrenceType]
        start_time: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                days_of_week: List[Union[str, DaysOfWeek]], 
                end_time: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
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


namespace azure.mgmt.alertsmanagement.operations

    class azure.mgmt.alertsmanagement.operations.AlertProcessingRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule: AlertProcessingRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_by_name(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AlertProcessingRule]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AlertProcessingRule]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule_patch: PatchObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule_patch: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...


    class azure.mgmt.alertsmanagement.operations.AlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def change_state(
                self, 
                alert_id: str, 
                new_state: Union[str, AlertState], 
                comment: Optional[Comments] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @overload
        def change_state(
                self, 
                alert_id: str, 
                new_state: Union[str, AlertState], 
                comment: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def get_all(
                self, 
                target_resource: Optional[str] = None, 
                target_resource_type: Optional[str] = None, 
                target_resource_group: Optional[str] = None, 
                monitor_service: Optional[Union[str, MonitorService]] = None, 
                monitor_condition: Optional[Union[str, MonitorCondition]] = None, 
                severity: Optional[Union[str, Severity]] = None, 
                alert_state: Optional[Union[str, AlertState]] = None, 
                alert_rule: Optional[str] = None, 
                smart_group_id: Optional[str] = None, 
                include_context: Optional[bool] = None, 
                include_egress_config: Optional[bool] = None, 
                page_count: Optional[int] = None, 
                sort_by: Optional[Union[str, AlertsSortByFields]] = None, 
                sort_order: Optional[Union[str, SortOrder]] = None, 
                select: Optional[str] = None, 
                time_range: Optional[Union[str, TimeRange]] = None, 
                custom_time_range: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Alert]: ...

        @distributed_trace
        def get_by_id(
                self, 
                alert_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def get_history(
                self, 
                alert_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertModification: ...

        @distributed_trace
        def get_summary(
                self, 
                groupby: Union[str, AlertsSummaryGroupByFields], 
                include_smart_groups_count: Optional[bool] = None, 
                target_resource: Optional[str] = None, 
                target_resource_type: Optional[str] = None, 
                target_resource_group: Optional[str] = None, 
                monitor_service: Optional[Union[str, MonitorService]] = None, 
                monitor_condition: Optional[Union[str, MonitorCondition]] = None, 
                severity: Optional[Union[str, Severity]] = None, 
                alert_state: Optional[Union[str, AlertState]] = None, 
                alert_rule: Optional[str] = None, 
                time_range: Optional[Union[str, TimeRange]] = None, 
                custom_time_range: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertsSummary: ...

        @distributed_trace
        def meta_data(
                self, 
                identifier: Union[str, Identifier], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertsMetaData: ...


    class azure.mgmt.alertsmanagement.operations.Operations:

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


    class azure.mgmt.alertsmanagement.operations.PrometheusRuleGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PrometheusRuleGroupResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PrometheusRuleGroupResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: PrometheusRuleGroupResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                rule_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrometheusRuleGroupResource: ...


    class azure.mgmt.alertsmanagement.operations.SmartGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def change_state(
                self, 
                smart_group_id: str, 
                new_state: Union[str, AlertState], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SmartGroup: ...

        @distributed_trace
        def get_all(
                self, 
                target_resource: Optional[str] = None, 
                target_resource_group: Optional[str] = None, 
                target_resource_type: Optional[str] = None, 
                monitor_service: Optional[Union[str, MonitorService]] = None, 
                monitor_condition: Optional[Union[str, MonitorCondition]] = None, 
                severity: Optional[Union[str, Severity]] = None, 
                smart_group_state: Optional[Union[str, AlertState]] = None, 
                time_range: Optional[Union[str, TimeRange]] = None, 
                page_count: Optional[int] = None, 
                sort_by: Optional[Union[str, SmartGroupsSortByFields]] = None, 
                sort_order: Optional[Union[str, SortOrder]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SmartGroup]: ...

        @distributed_trace
        def get_by_id(
                self, 
                smart_group_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SmartGroup: ...

        @distributed_trace
        def get_history(
                self, 
                smart_group_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SmartGroupModification: ...


```