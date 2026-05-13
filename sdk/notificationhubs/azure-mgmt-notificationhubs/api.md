```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.notificationhubs

    class azure.mgmt.notificationhubs.NotificationHubsManagementClient: implements ContextManager 
        namespaces: NamespacesOperations
        notification_hubs: NotificationHubsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations

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


namespace azure.mgmt.notificationhubs.aio

    class azure.mgmt.notificationhubs.aio.NotificationHubsManagementClient: implements AsyncContextManager 
        namespaces: NamespacesOperations
        notification_hubs: NotificationHubsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations

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


namespace azure.mgmt.notificationhubs.aio.operations

    class azure.mgmt.notificationhubs.aio.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: NamespaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceResource]: ...

        @overload
        async def check_availability(
                self, 
                parameters: CheckAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResult: ...

        @overload
        async def check_availability(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResult: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: SharedAccessAuthorizationRuleResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedAccessAuthorizationRuleResource: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedAccessAuthorizationRuleResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NamespaceResource: ...

        @distributed_trace_async
        async def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> SharedAccessAuthorizationRuleResource: ...

        @distributed_trace_async
        async def get_pns_credentials(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> PnsCredentialsResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                skip_token: Optional[str] = None, 
                top: int = 100, 
                **kwargs: Any
            ) -> AsyncIterable[NamespaceResource]: ...

        @distributed_trace
        def list_all(
                self, 
                skip_token: Optional[str] = None, 
                top: int = 100, 
                **kwargs: Any
            ) -> AsyncIterable[NamespaceResource]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SharedAccessAuthorizationRuleResource]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> ResourceListKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: PolicyKeyResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceListKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceListKeys: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: NamespacePatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NamespaceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NamespaceResource: ...


    class azure.mgmt.notificationhubs.aio.operations.NotificationHubsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_notification_hub_availability(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: CheckAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResult: ...

        @overload
        async def check_notification_hub_availability(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResult: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                parameters: NotificationHubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationHubResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationHubResource: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                parameters: SharedAccessAuthorizationRuleResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedAccessAuthorizationRuleResource: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedAccessAuthorizationRuleResource: ...

        @distributed_trace_async
        async def debug_send(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                **kwargs: Any
            ) -> DebugSendResponse: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                **kwargs: Any
            ) -> NotificationHubResource: ...

        @distributed_trace_async
        async def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> SharedAccessAuthorizationRuleResource: ...

        @distributed_trace_async
        async def get_pns_credentials(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                **kwargs: Any
            ) -> PnsCredentialsResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                skip_token: Optional[str] = None, 
                top: int = 100, 
                **kwargs: Any
            ) -> AsyncIterable[NotificationHubResource]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SharedAccessAuthorizationRuleResource]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> ResourceListKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                parameters: PolicyKeyResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceListKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceListKeys: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                parameters: NotificationHubPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationHubResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationHubResource: ...


    class azure.mgmt.notificationhubs.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.notificationhubs.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @distributed_trace_async
        async def get_group_id(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                sub_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateEndpointConnectionResource]: ...

        @distributed_trace
        def list_group_ids(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateLinkResource]: ...


namespace azure.mgmt.notificationhubs.models

    class azure.mgmt.notificationhubs.models.AccessRights(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LISTEN = "Listen"
        MANAGE = "Manage"
        SEND = "Send"


    class azure.mgmt.notificationhubs.models.AdmCredential(Model):
        auth_token_url: str
        client_id: str
        client_secret: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_token_url: str, 
                client_id: str, 
                client_secret: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.ApnsCredential(Model):
        apns_certificate: str
        app_id: str
        app_name: str
        certificate_key: str
        endpoint: str
        key_id: str
        thumbprint: str
        token: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                apns_certificate: Optional[str] = ..., 
                app_id: Optional[str] = ..., 
                app_name: Optional[str] = ..., 
                certificate_key: Optional[str] = ..., 
                endpoint: str, 
                key_id: Optional[str] = ..., 
                thumbprint: Optional[str] = ..., 
                token: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.Availability(Model):
        blob_duration: str
        time_grain: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.BaiduCredential(Model):
        baidu_api_key: str
        baidu_end_point: str
        baidu_secret_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                baidu_api_key: str, 
                baidu_end_point: str, 
                baidu_secret_key: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.BrowserCredential(Model):
        subject: str
        vapid_private_key: str
        vapid_public_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                subject: str, 
                vapid_private_key: str, 
                vapid_public_key: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.CheckAvailabilityParameters(Model):
        id: str
        is_availiable: bool
        location: str
        name: str
        sku: Sku
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_availiable: Optional[bool] = ..., 
                location: Optional[str] = ..., 
                name: str, 
                sku: Optional[Sku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.CheckAvailabilityResult(ProxyResource):
        id: str
        is_availiable: bool
        location: str
        name: str
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_availiable: Optional[bool] = ..., 
                location: Optional[str] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.ConnectionDetails(Model):
        group_id: str
        id: str
        link_identifier: str
        member_name: str
        private_ip_address: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.notificationhubs.models.DebugSendResponse(ProxyResource):
        failure: int
        id: str
        location: str
        name: str
        results: list[RegistrationResult]
        success: int
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.FcmV1Credential(Model):
        client_email: str
        private_key: str
        project_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_email: str, 
                private_key: str, 
                project_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.GcmCredential(Model):
        gcm_endpoint: str
        google_api_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                gcm_endpoint: Optional[str] = ..., 
                google_api_key: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.GroupConnectivityInformation(Model):
        customer_visible_fqdns: list[str]
        group_id: str
        internal_fqdn: str
        member_name: str
        private_link_service_arm_region: str
        redirect_map_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.IpRule(Model):
        ip_mask: str
        rights: Union[list[str, AccessRights]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_mask: str, 
                rights: List[Union[str, AccessRights]], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.LogSpecification(Model):
        blob_duration: str
        category_groups: list[str]
        display_name: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category_groups: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.MetricSpecification(Model):
        aggregation_type: str
        availabilities: list[Availability]
        display_description: str
        display_name: str
        fill_gap_with_zero: bool
        metric_filter_pattern: str
        name: str
        supported_time_grain_types: list[str]
        unit: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.MpnsCredential(Model):
        certificate_key: str
        mpns_certificate: str
        thumbprint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_key: str, 
                mpns_certificate: str, 
                thumbprint: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.NamespaceListResult(Model):
        next_link: str
        value: list[NamespaceResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.NamespacePatchParameters(Model):
        properties: NamespaceProperties
        sku: Sku
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[NamespaceProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.NamespaceProperties(Model):
        created_at: datetime
        critical: bool
        data_center: str
        enabled: bool
        metric_id: str
        name: str
        namespace_type: Union[str, NamespaceType]
        network_acls: NetworkAcls
        pns_credentials: PnsCredentials
        private_endpoint_connections: list[PrivateEndpointConnectionResource]
        provisioning_state: Union[str, OperationProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        region: str
        replication_region: Union[str, ReplicationRegion]
        scale_unit: str
        service_bus_endpoint: str
        status: Union[str, NamespaceStatus]
        subscription_id: str
        updated_at: datetime
        zone_redundancy: Union[str, ZoneRedundancyPreference]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_center: Optional[str] = ..., 
                namespace_type: Optional[Union[str, NamespaceType]] = ..., 
                network_acls: Optional[NetworkAcls] = ..., 
                pns_credentials: Optional[PnsCredentials] = ..., 
                provisioning_state: Optional[Union[str, OperationProvisioningState]] = ..., 
                public_network_access: Union[str, PublicNetworkAccess] = "Enabled", 
                replication_region: Optional[Union[str, ReplicationRegion]] = ..., 
                scale_unit: Optional[str] = ..., 
                status: Optional[Union[str, NamespaceStatus]] = ..., 
                zone_redundancy: Union[str, ZoneRedundancyPreference] = "Disabled", 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.NamespaceResource(TrackedResource):
        created_at: datetime
        critical: bool
        data_center: str
        enabled: bool
        id: str
        location: str
        metric_id: str
        name: str
        name_properties_name: str
        namespace_type: Union[str, NamespaceType]
        network_acls: NetworkAcls
        pns_credentials: PnsCredentials
        private_endpoint_connections: list[PrivateEndpointConnectionResource]
        provisioning_state: Union[str, OperationProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        region: str
        replication_region: Union[str, ReplicationRegion]
        scale_unit: str
        service_bus_endpoint: str
        sku: Sku
        status: Union[str, NamespaceStatus]
        subscription_id: str
        system_data: SystemData
        tags: dict[str, str]
        type: str
        updated_at: datetime
        zone_redundancy: Union[str, ZoneRedundancyPreference]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_center: Optional[str] = ..., 
                location: str, 
                namespace_type: Optional[Union[str, NamespaceType]] = ..., 
                network_acls: Optional[NetworkAcls] = ..., 
                pns_credentials: Optional[PnsCredentials] = ..., 
                provisioning_state: Optional[Union[str, OperationProvisioningState]] = ..., 
                public_network_access: Union[str, PublicNetworkAccess] = "Enabled", 
                replication_region: Optional[Union[str, ReplicationRegion]] = ..., 
                scale_unit: Optional[str] = ..., 
                sku: Sku, 
                status: Optional[Union[str, NamespaceStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                zone_redundancy: Union[str, ZoneRedundancyPreference] = "Disabled", 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.NamespaceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED = "Created"
        CREATING = "Creating"
        DELETING = "Deleting"
        SUSPENDED = "Suspended"


    class azure.mgmt.notificationhubs.models.NamespaceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MESSAGING = "Messaging"
        NOTIFICATION_HUB = "NotificationHub"


    class azure.mgmt.notificationhubs.models.NetworkAcls(Model):
        ip_rules: list[IpRule]
        public_network_rule: PublicInternetAuthorizationRule

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_rules: Optional[List[IpRule]] = ..., 
                public_network_rule: Optional[PublicInternetAuthorizationRule] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.NotificationHubListResult(Model):
        next_link: str
        value: list[NotificationHubResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.NotificationHubPatchParameters(Model):
        adm_credential: AdmCredential
        apns_credential: ApnsCredential
        authorization_rules: list[SharedAccessAuthorizationRuleProperties]
        baidu_credential: BaiduCredential
        browser_credential: BrowserCredential
        daily_max_active_devices: int
        fcm_v1_credential: FcmV1Credential
        gcm_credential: GcmCredential
        mpns_credential: MpnsCredential
        name: str
        registration_ttl: str
        sku: Sku
        tags: dict[str, str]
        wns_credential: WnsCredential
        xiaomi_credential: XiaomiCredential

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                adm_credential: Optional[AdmCredential] = ..., 
                apns_credential: Optional[ApnsCredential] = ..., 
                baidu_credential: Optional[BaiduCredential] = ..., 
                browser_credential: Optional[BrowserCredential] = ..., 
                fcm_v1_credential: Optional[FcmV1Credential] = ..., 
                gcm_credential: Optional[GcmCredential] = ..., 
                mpns_credential: Optional[MpnsCredential] = ..., 
                name: Optional[str] = ..., 
                registration_ttl: Optional[str] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                wns_credential: Optional[WnsCredential] = ..., 
                xiaomi_credential: Optional[XiaomiCredential] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.NotificationHubResource(TrackedResource):
        adm_credential: AdmCredential
        apns_credential: ApnsCredential
        authorization_rules: list[SharedAccessAuthorizationRuleProperties]
        baidu_credential: BaiduCredential
        browser_credential: BrowserCredential
        daily_max_active_devices: int
        fcm_v1_credential: FcmV1Credential
        gcm_credential: GcmCredential
        id: str
        location: str
        mpns_credential: MpnsCredential
        name: str
        name_properties_name: str
        registration_ttl: str
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        wns_credential: WnsCredential
        xiaomi_credential: XiaomiCredential

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                adm_credential: Optional[AdmCredential] = ..., 
                apns_credential: Optional[ApnsCredential] = ..., 
                baidu_credential: Optional[BaiduCredential] = ..., 
                browser_credential: Optional[BrowserCredential] = ..., 
                fcm_v1_credential: Optional[FcmV1Credential] = ..., 
                gcm_credential: Optional[GcmCredential] = ..., 
                location: str, 
                mpns_credential: Optional[MpnsCredential] = ..., 
                name_properties_name: Optional[str] = ..., 
                registration_ttl: Optional[str] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                wns_credential: Optional[WnsCredential] = ..., 
                xiaomi_credential: Optional[XiaomiCredential] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.Operation(Model):
        display: OperationDisplay
        is_data_action: bool
        name: str
        properties: OperationProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                properties: Optional[OperationProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.OperationProperties(Model):
        service_specification: ServiceSpecification

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.OperationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DISABLED = "Disabled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.notificationhubs.models.PnsCredentials(Model):
        adm_credential: AdmCredential
        apns_credential: ApnsCredential
        baidu_credential: BaiduCredential
        browser_credential: BrowserCredential
        fcm_v1_credential: FcmV1Credential
        gcm_credential: GcmCredential
        mpns_credential: MpnsCredential
        wns_credential: WnsCredential
        xiaomi_credential: XiaomiCredential

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                adm_credential: Optional[AdmCredential] = ..., 
                apns_credential: Optional[ApnsCredential] = ..., 
                baidu_credential: Optional[BaiduCredential] = ..., 
                browser_credential: Optional[BrowserCredential] = ..., 
                fcm_v1_credential: Optional[FcmV1Credential] = ..., 
                gcm_credential: Optional[GcmCredential] = ..., 
                mpns_credential: Optional[MpnsCredential] = ..., 
                wns_credential: Optional[WnsCredential] = ..., 
                xiaomi_credential: Optional[XiaomiCredential] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.PnsCredentialsResource(ProxyResource):
        adm_credential: AdmCredential
        apns_credential: ApnsCredential
        baidu_credential: BaiduCredential
        browser_credential: BrowserCredential
        fcm_v1_credential: FcmV1Credential
        gcm_credential: GcmCredential
        id: str
        location: str
        mpns_credential: MpnsCredential
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str
        wns_credential: WnsCredential
        xiaomi_credential: XiaomiCredential

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                adm_credential: Optional[AdmCredential] = ..., 
                apns_credential: Optional[ApnsCredential] = ..., 
                baidu_credential: Optional[BaiduCredential] = ..., 
                browser_credential: Optional[BrowserCredential] = ..., 
                fcm_v1_credential: Optional[FcmV1Credential] = ..., 
                gcm_credential: Optional[GcmCredential] = ..., 
                location: Optional[str] = ..., 
                mpns_credential: Optional[MpnsCredential] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                wns_credential: Optional[WnsCredential] = ..., 
                xiaomi_credential: Optional[XiaomiCredential] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.PolicyKeyResource(Model):
        policy_key: Union[str, PolicyKeyType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                policy_key: Union[str, PolicyKeyType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.PolicyKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY_KEY = "PrimaryKey"
        SECONDARY_KEY = "SecondaryKey"


    class azure.mgmt.notificationhubs.models.PrivateEndpointConnectionProperties(Model):
        group_ids: list[str]
        private_endpoint: RemotePrivateEndpointConnection
        private_link_service_connection_state: RemotePrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[RemotePrivateEndpointConnection] = ..., 
                private_link_service_connection_state: Optional[RemotePrivateLinkServiceConnectionState] = ..., 
                provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        DELETING_BY_PROXY = "DeletingByProxy"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"
        UPDATING_BY_PROXY = "UpdatingByProxy"


    class azure.mgmt.notificationhubs.models.PrivateEndpointConnectionResource(ProxyResource):
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.PrivateEndpointConnectionResourceListResult(Model):
        next_link: str
        value: list[PrivateEndpointConnectionResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.PrivateLinkConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.notificationhubs.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: PrivateLinkResourceProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.PrivateLinkResourceListResult(Model):
        next_link: str
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.PrivateLinkResourceProperties(Model):
        group_id: str
        required_members: list[str]
        required_zone_names: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.PrivateLinkServiceConnection(Model):
        group_ids: list[str]
        name: str
        request_message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                group_ids: Optional[List[str]] = ..., 
                name: Optional[str] = ..., 
                request_message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.PublicInternetAuthorizationRule(Model):
        rights: Union[list[str, AccessRights]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                rights: List[Union[str, AccessRights]], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.notificationhubs.models.RegistrationResult(Model):
        application_platform: str
        outcome: str
        pns_handle: str
        registration_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.RemotePrivateEndpointConnection(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.RemotePrivateLinkServiceConnectionState(Model):
        actions_required: str
        description: str
        status: Union[str, PrivateLinkConnectionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                status: Optional[Union[str, PrivateLinkConnectionStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.ReplicationRegion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUSTRALIA_EAST = "AustraliaEast"
        BRAZIL_SOUTH = "BrazilSouth"
        DEFAULT = "Default"
        NONE = "None"
        NORTH_EUROPE = "NorthEurope"
        SOUTH_AFRICA_NORTH = "SouthAfricaNorth"
        SOUTH_EAST_ASIA = "SouthEastAsia"
        WEST_US2 = "WestUs2"


    class azure.mgmt.notificationhubs.models.Resource(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.ResourceListKeys(Model):
        key_name: str
        primary_connection_string: str
        primary_key: str
        secondary_connection_string: str
        secondary_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.ServiceSpecification(Model):
        log_specifications: list[LogSpecification]
        metric_specifications: list[MetricSpecification]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.SharedAccessAuthorizationRuleListResult(Model):
        next_link: str
        value: list[SharedAccessAuthorizationRuleResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.SharedAccessAuthorizationRuleProperties(Model):
        claim_type: str
        claim_value: str
        created_time: datetime
        key_name: str
        modified_time: datetime
        primary_key: str
        revision: int
        rights: Union[list[str, AccessRights]]
        secondary_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                primary_key: Optional[str] = ..., 
                rights: List[Union[str, AccessRights]], 
                secondary_key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.SharedAccessAuthorizationRuleResource(ProxyResource):
        claim_type: str
        claim_value: str
        created_time: datetime
        id: str
        key_name: str
        location: str
        modified_time: datetime
        name: str
        primary_key: str
        revision: int
        rights: Union[list[str, AccessRights]]
        secondary_key: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                primary_key: Optional[str] = ..., 
                rights: Optional[List[Union[str, AccessRights]]] = ..., 
                secondary_key: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.Sku(Model):
        capacity: int
        family: str
        name: Union[str, SkuName]
        size: str
        tier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: Union[str, SkuName], 
                size: Optional[str] = ..., 
                tier: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        STANDARD = "Standard"


    class azure.mgmt.notificationhubs.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.WnsCredential(Model):
        certificate_key: str
        package_sid: str
        secret_key: str
        windows_live_endpoint: str
        wns_certificate: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_key: Optional[str] = ..., 
                package_sid: Optional[str] = ..., 
                secret_key: Optional[str] = ..., 
                windows_live_endpoint: Optional[str] = ..., 
                wns_certificate: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.XiaomiCredential(Model):
        app_secret: str
        endpoint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_secret: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.notificationhubs.models.ZoneRedundancyPreference(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


namespace azure.mgmt.notificationhubs.operations

    class azure.mgmt.notificationhubs.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: NamespaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceResource]: ...

        @overload
        def check_availability(
                self, 
                parameters: CheckAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResult: ...

        @overload
        def check_availability(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResult: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: SharedAccessAuthorizationRuleResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedAccessAuthorizationRuleResource: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedAccessAuthorizationRuleResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NamespaceResource: ...

        @distributed_trace
        def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> SharedAccessAuthorizationRuleResource: ...

        @distributed_trace
        def get_pns_credentials(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> PnsCredentialsResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                skip_token: Optional[str] = None, 
                top: int = 100, 
                **kwargs: Any
            ) -> Iterable[NamespaceResource]: ...

        @distributed_trace
        def list_all(
                self, 
                skip_token: Optional[str] = None, 
                top: int = 100, 
                **kwargs: Any
            ) -> Iterable[NamespaceResource]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Iterable[SharedAccessAuthorizationRuleResource]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> ResourceListKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: PolicyKeyResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceListKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceListKeys: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: NamespacePatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NamespaceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NamespaceResource: ...


    class azure.mgmt.notificationhubs.operations.NotificationHubsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def check_notification_hub_availability(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: CheckAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResult: ...

        @overload
        def check_notification_hub_availability(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResult: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                parameters: NotificationHubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationHubResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationHubResource: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                parameters: SharedAccessAuthorizationRuleResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedAccessAuthorizationRuleResource: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedAccessAuthorizationRuleResource: ...

        @distributed_trace
        def debug_send(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                **kwargs: Any
            ) -> DebugSendResponse: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                **kwargs: Any
            ) -> NotificationHubResource: ...

        @distributed_trace
        def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> SharedAccessAuthorizationRuleResource: ...

        @distributed_trace
        def get_pns_credentials(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                **kwargs: Any
            ) -> PnsCredentialsResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                skip_token: Optional[str] = None, 
                top: int = 100, 
                **kwargs: Any
            ) -> Iterable[NotificationHubResource]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                **kwargs: Any
            ) -> Iterable[SharedAccessAuthorizationRuleResource]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> ResourceListKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                parameters: PolicyKeyResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceListKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceListKeys: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                parameters: NotificationHubPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationHubResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationHubResource: ...


    class azure.mgmt.notificationhubs.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.notificationhubs.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @distributed_trace
        def get_group_id(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                sub_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Iterable[PrivateEndpointConnectionResource]: ...

        @distributed_trace
        def list_group_ids(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Iterable[PrivateLinkResource]: ...


```