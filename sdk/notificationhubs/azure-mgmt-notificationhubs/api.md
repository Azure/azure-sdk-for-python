```py
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
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
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
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
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
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NamespaceResource]: ...

        @distributed_trace
        def list_all(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NamespaceResource]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SharedAccessAuthorizationRuleResource]: ...

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
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NotificationHubResource]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SharedAccessAuthorizationRuleResource]: ...

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
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


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
            ) -> AsyncItemPaged[PrivateEndpointConnectionResource]: ...

        @distributed_trace
        def list_group_ids(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


namespace azure.mgmt.notificationhubs.models

    class azure.mgmt.notificationhubs.models.AccessRights(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LISTEN = "Listen"
        MANAGE = "Manage"
        SEND = "Send"


    class azure.mgmt.notificationhubs.models.AdmCredential(_Model):
        properties: AdmCredentialProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: AdmCredentialProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.AdmCredentialProperties(_Model):
        auth_token_url: str
        client_id: str
        client_secret: str

        @overload
        def __init__(
                self, 
                *, 
                auth_token_url: str, 
                client_id: str, 
                client_secret: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.ApnsCredential(_Model):
        properties: ApnsCredentialProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ApnsCredentialProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.ApnsCredentialProperties(_Model):
        apns_certificate: Optional[str]
        app_id: Optional[str]
        app_name: Optional[str]
        certificate_key: Optional[str]
        endpoint: str
        key_id: Optional[str]
        thumbprint: Optional[str]
        token: Optional[str]

        @overload
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
                token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.Availability(_Model):
        blob_duration: Optional[str]
        time_grain: Optional[str]


    class azure.mgmt.notificationhubs.models.BaiduCredential(_Model):
        properties: BaiduCredentialProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: BaiduCredentialProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.BaiduCredentialProperties(_Model):
        baidu_api_key: str
        baidu_end_point: str
        baidu_secret_key: str

        @overload
        def __init__(
                self, 
                *, 
                baidu_api_key: str, 
                baidu_end_point: str, 
                baidu_secret_key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.BrowserCredential(_Model):
        properties: BrowserCredentialProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: BrowserCredentialProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.BrowserCredentialProperties(_Model):
        subject: str
        vapid_private_key: str
        vapid_public_key: str

        @overload
        def __init__(
                self, 
                *, 
                subject: str, 
                vapid_private_key: str, 
                vapid_public_key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.CheckAvailabilityParameters(_Model):
        id: Optional[str]
        is_availiable: Optional[bool]
        location: Optional[str]
        name: str
        sku: Optional[Sku]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_availiable: Optional[bool] = ..., 
                location: Optional[str] = ..., 
                name: str, 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.CheckAvailabilityResult(ProxyResource):
        id: str
        is_availiable: Optional[bool]
        location: Optional[str]
        name: str
        sku: Optional[Sku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                is_availiable: Optional[bool] = ..., 
                location: Optional[str] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.notificationhubs.models.DebugSendResponse(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[DebugSendResult]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[DebugSendResult] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.DebugSendResult(_Model):
        failure: Optional[int]
        results: Optional[list[RegistrationResult]]
        success: Optional[int]


    class azure.mgmt.notificationhubs.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.notificationhubs.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.notificationhubs.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.FcmV1Credential(_Model):
        properties: FcmV1CredentialProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: FcmV1CredentialProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.FcmV1CredentialProperties(_Model):
        client_email: str
        private_key: str
        project_id: str

        @overload
        def __init__(
                self, 
                *, 
                client_email: str, 
                private_key: str, 
                project_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.GcmCredential(_Model):
        properties: GcmCredentialProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: GcmCredentialProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.GcmCredentialProperties(_Model):
        gcm_endpoint: Optional[str]
        google_api_key: str

        @overload
        def __init__(
                self, 
                *, 
                gcm_endpoint: Optional[str] = ..., 
                google_api_key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.IpRule(_Model):
        ip_mask: str
        rights: list[Union[str, AccessRights]]

        @overload
        def __init__(
                self, 
                *, 
                ip_mask: str, 
                rights: list[Union[str, AccessRights]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.LogSpecification(_Model):
        blob_duration: Optional[str]
        category_groups: Optional[list[str]]
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category_groups: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        availabilities: Optional[list[Availability]]
        display_description: Optional[str]
        display_name: Optional[str]
        fill_gap_with_zero: Optional[bool]
        metric_filter_pattern: Optional[str]
        name: Optional[str]
        supported_time_grain_types: Optional[list[str]]
        unit: Optional[str]


    class azure.mgmt.notificationhubs.models.MpnsCredential(_Model):
        properties: MpnsCredentialProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: MpnsCredentialProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.MpnsCredentialProperties(_Model):
        certificate_key: str
        mpns_certificate: str
        thumbprint: str

        @overload
        def __init__(
                self, 
                *, 
                certificate_key: str, 
                mpns_certificate: str, 
                thumbprint: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.NamespacePatchParameters(_Model):
        properties: Optional[NamespaceProperties]
        sku: Optional[Sku]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NamespaceProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.NamespaceProperties(_Model):
        created_at: Optional[datetime]
        critical: Optional[bool]
        data_center: Optional[str]
        enabled: Optional[bool]
        metric_id: Optional[str]
        name: Optional[str]
        namespace_type: Optional[Union[str, NamespaceType]]
        network_acls: Optional[NetworkAcls]
        pns_credentials: Optional[PnsCredentials]
        private_endpoint_connections: Optional[list[PrivateEndpointConnectionResource]]
        provisioning_state: Optional[Union[str, OperationProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        region: Optional[str]
        replication_region: Optional[Union[str, ReplicationRegion]]
        scale_unit: Optional[str]
        service_bus_endpoint: Optional[str]
        status: Optional[Union[str, NamespaceStatus]]
        subscription_id: Optional[str]
        updated_at: Optional[datetime]
        zone_redundancy: Optional[Union[str, ZoneRedundancyPreference]]

        @overload
        def __init__(
                self, 
                *, 
                data_center: Optional[str] = ..., 
                namespace_type: Optional[Union[str, NamespaceType]] = ..., 
                network_acls: Optional[NetworkAcls] = ..., 
                pns_credentials: Optional[PnsCredentials] = ..., 
                provisioning_state: Optional[Union[str, OperationProvisioningState]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                replication_region: Optional[Union[str, ReplicationRegion]] = ..., 
                scale_unit: Optional[str] = ..., 
                status: Optional[Union[str, NamespaceStatus]] = ..., 
                zone_redundancy: Optional[Union[str, ZoneRedundancyPreference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.NamespaceResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[NamespaceProperties]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[NamespaceProperties] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.NamespaceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED = "Created"
        CREATING = "Creating"
        DELETING = "Deleting"
        SUSPENDED = "Suspended"


    class azure.mgmt.notificationhubs.models.NamespaceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MESSAGING = "Messaging"
        NOTIFICATION_HUB = "NotificationHub"


    class azure.mgmt.notificationhubs.models.NetworkAcls(_Model):
        ip_rules: Optional[list[IpRule]]
        public_network_rule: Optional[PublicInternetAuthorizationRule]

        @overload
        def __init__(
                self, 
                *, 
                ip_rules: Optional[list[IpRule]] = ..., 
                public_network_rule: Optional[PublicInternetAuthorizationRule] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.NotificationHubPatchParameters(_Model):
        properties: Optional[NotificationHubProperties]
        sku: Optional[Sku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NotificationHubProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.NotificationHubProperties(_Model):
        adm_credential: Optional[AdmCredential]
        apns_credential: Optional[ApnsCredential]
        authorization_rules: Optional[list[SharedAccessAuthorizationRuleProperties]]
        baidu_credential: Optional[BaiduCredential]
        browser_credential: Optional[BrowserCredential]
        daily_max_active_devices: Optional[int]
        fcm_v1_credential: Optional[FcmV1Credential]
        gcm_credential: Optional[GcmCredential]
        mpns_credential: Optional[MpnsCredential]
        name: Optional[str]
        registration_ttl: Optional[str]
        wns_credential: Optional[WnsCredential]
        xiaomi_credential: Optional[XiaomiCredential]

        @overload
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
                wns_credential: Optional[WnsCredential] = ..., 
                xiaomi_credential: Optional[XiaomiCredential] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.NotificationHubResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[NotificationHubProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[NotificationHubProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        properties: Optional[OperationProperties]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                properties: Optional[OperationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.notificationhubs.models.OperationProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.OperationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DISABLED = "Disabled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.notificationhubs.models.PnsCredentials(_Model):
        adm_credential: Optional[AdmCredential]
        apns_credential: Optional[ApnsCredential]
        baidu_credential: Optional[BaiduCredential]
        browser_credential: Optional[BrowserCredential]
        fcm_v1_credential: Optional[FcmV1Credential]
        gcm_credential: Optional[GcmCredential]
        mpns_credential: Optional[MpnsCredential]
        wns_credential: Optional[WnsCredential]
        xiaomi_credential: Optional[XiaomiCredential]

        @overload
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
                xiaomi_credential: Optional[XiaomiCredential] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.PnsCredentialsResource(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[PnsCredentials]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[PnsCredentials] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.PolicyKeyResource(_Model):
        policy_key: Union[str, PolicyKeyType]

        @overload
        def __init__(
                self, 
                *, 
                policy_key: Union[str, PolicyKeyType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.PolicyKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY_KEY = "PrimaryKey"
        SECONDARY_KEY = "SecondaryKey"


    class azure.mgmt.notificationhubs.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[RemotePrivateEndpointConnection]
        private_link_service_connection_state: Optional[RemotePrivateLinkServiceConnectionState]
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[RemotePrivateEndpointConnection] = ..., 
                private_link_service_connection_state: Optional[RemotePrivateLinkServiceConnectionState] = ..., 
                provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.PrivateLinkConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.notificationhubs.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]


    class azure.mgmt.notificationhubs.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.notificationhubs.models.PublicInternetAuthorizationRule(_Model):
        rights: list[Union[str, AccessRights]]

        @overload
        def __init__(
                self, 
                *, 
                rights: list[Union[str, AccessRights]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.notificationhubs.models.RegistrationResult(_Model):
        application_platform: Optional[str]
        outcome: Optional[str]
        pns_handle: Optional[str]
        registration_id: Optional[str]


    class azure.mgmt.notificationhubs.models.RemotePrivateEndpointConnection(_Model):
        id: Optional[str]


    class azure.mgmt.notificationhubs.models.RemotePrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateLinkConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[Union[str, PrivateLinkConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.ReplicationRegion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUSTRALIA_EAST = "AustraliaEast"
        BRAZIL_SOUTH = "BrazilSouth"
        DEFAULT = "Default"
        NONE = "None"
        NORTH_EUROPE = "NorthEurope"
        SOUTH_AFRICA_NORTH = "SouthAfricaNorth"
        SOUTH_EAST_ASIA = "SouthEastAsia"
        WEST_US2 = "WestUs2"


    class azure.mgmt.notificationhubs.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.notificationhubs.models.ResourceListKeys(_Model):
        key_name: Optional[str]
        primary_connection_string: Optional[str]
        primary_key: Optional[str]
        secondary_connection_string: Optional[str]
        secondary_key: Optional[str]


    class azure.mgmt.notificationhubs.models.ServiceSpecification(_Model):
        log_specifications: Optional[list[LogSpecification]]
        metric_specifications: Optional[list[MetricSpecification]]


    class azure.mgmt.notificationhubs.models.SharedAccessAuthorizationRuleProperties(_Model):
        claim_type: Optional[str]
        claim_value: Optional[str]
        created_time: Optional[datetime]
        key_name: Optional[str]
        modified_time: Optional[datetime]
        primary_key: Optional[str]
        revision: Optional[int]
        rights: list[Union[str, AccessRights]]
        secondary_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_key: Optional[str] = ..., 
                rights: list[Union[str, AccessRights]], 
                secondary_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.SharedAccessAuthorizationRuleResource(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[SharedAccessAuthorizationRuleProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[SharedAccessAuthorizationRuleProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.Sku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: Union[str, SkuName]
        size: Optional[str]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: Union[str, SkuName], 
                size: Optional[str] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        STANDARD = "Standard"


    class azure.mgmt.notificationhubs.models.SystemData(_Model):
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


    class azure.mgmt.notificationhubs.models.TrackedResource(Resource):
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


    class azure.mgmt.notificationhubs.models.WnsCredential(_Model):
        properties: WnsCredentialProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: WnsCredentialProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.WnsCredentialProperties(_Model):
        certificate_key: Optional[str]
        package_sid: Optional[str]
        secret_key: Optional[str]
        windows_live_endpoint: Optional[str]
        wns_certificate: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate_key: Optional[str] = ..., 
                package_sid: Optional[str] = ..., 
                secret_key: Optional[str] = ..., 
                windows_live_endpoint: Optional[str] = ..., 
                wns_certificate: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.XiaomiCredential(_Model):
        properties: XiaomiCredentialProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: XiaomiCredentialProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.notificationhubs.models.XiaomiCredentialProperties(_Model):
        app_secret: Optional[str]
        endpoint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                app_secret: Optional[str] = ..., 
                endpoint: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.notificationhubs.models.ZoneRedundancyPreference(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


namespace azure.mgmt.notificationhubs.operations

    class azure.mgmt.notificationhubs.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NamespaceResource]: ...

        @distributed_trace
        def list_all(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NamespaceResource]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SharedAccessAuthorizationRuleResource]: ...

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
            ) -> None: ...

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
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NotificationHubResource]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                notification_hub_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SharedAccessAuthorizationRuleResource]: ...

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
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.notificationhubs.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[PrivateEndpointConnectionResource]: ...

        @distributed_trace
        def list_group_ids(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


namespace azure.mgmt.notificationhubs.types

    class azure.mgmt.notificationhubs.types.AdmCredential(TypedDict, total=False):
        key "properties": Required[AdmCredentialProperties]
        properties: AdmCredentialProperties


    class azure.mgmt.notificationhubs.types.AdmCredentialProperties(TypedDict, total=False):
        key "authTokenUrl": Required[str]
        key "clientId": Required[str]
        key "clientSecret": Required[str]
        auth_token_url: str
        client_id: str
        client_secret: str


    class azure.mgmt.notificationhubs.types.ApnsCredential(TypedDict, total=False):
        key "properties": Required[ApnsCredentialProperties]
        properties: ApnsCredentialProperties


    class azure.mgmt.notificationhubs.types.ApnsCredentialProperties(TypedDict, total=False):
        key "apnsCertificate": str
        key "appId": str
        key "appName": str
        key "certificateKey": str
        key "endpoint": Required[str]
        key "keyId": str
        key "thumbprint": str
        key "token": str
        apns_certificate: str
        app_id: str
        app_name: str
        certificate_key: str
        endpoint: str
        key_id: str
        thumbprint: str
        token: str


    class azure.mgmt.notificationhubs.types.BaiduCredential(TypedDict, total=False):
        key "properties": Required[BaiduCredentialProperties]
        properties: BaiduCredentialProperties


    class azure.mgmt.notificationhubs.types.BaiduCredentialProperties(TypedDict, total=False):
        key "baiduApiKey": Required[str]
        key "baiduEndPoint": Required[str]
        key "baiduSecretKey": Required[str]
        baidu_api_key: str
        baidu_end_point: str
        baidu_secret_key: str


    class azure.mgmt.notificationhubs.types.BrowserCredential(TypedDict, total=False):
        key "properties": Required[BrowserCredentialProperties]
        properties: BrowserCredentialProperties


    class azure.mgmt.notificationhubs.types.BrowserCredentialProperties(TypedDict, total=False):
        key "subject": Required[str]
        key "vapidPrivateKey": Required[str]
        key "vapidPublicKey": Required[str]
        subject: str
        vapid_private_key: str
        vapid_public_key: str


    class azure.mgmt.notificationhubs.types.CheckAvailabilityParameters(TypedDict, total=False):
        key "id": str
        key "isAvailiable": bool
        key "location": str
        key "name": Required[str]
        key "sku": ForwardRef('Sku', module='types')
        key "type": str
        id: str
        is_availiable: bool
        location: str
        name: str
        sku: Sku
        tags: dict[str, str]
        type: str


    class azure.mgmt.notificationhubs.types.FcmV1Credential(TypedDict, total=False):
        key "properties": Required[FcmV1CredentialProperties]
        properties: FcmV1CredentialProperties


    class azure.mgmt.notificationhubs.types.FcmV1CredentialProperties(TypedDict, total=False):
        key "clientEmail": Required[str]
        key "privateKey": Required[str]
        key "projectId": Required[str]
        client_email: str
        private_key: str
        project_id: str


    class azure.mgmt.notificationhubs.types.GcmCredential(TypedDict, total=False):
        key "properties": Required[GcmCredentialProperties]
        properties: GcmCredentialProperties


    class azure.mgmt.notificationhubs.types.GcmCredentialProperties(TypedDict, total=False):
        key "gcmEndpoint": str
        key "googleApiKey": Required[str]
        gcm_endpoint: str
        google_api_key: str


    class azure.mgmt.notificationhubs.types.IpRule(TypedDict, total=False):
        key "ipMask": Required[str]
        key "rights": Required[list[Union[str, AccessRights]]]
        ip_mask: str
        rights: list[Union[str, AccessRights]]


    class azure.mgmt.notificationhubs.types.MpnsCredential(TypedDict, total=False):
        key "properties": Required[MpnsCredentialProperties]
        properties: MpnsCredentialProperties


    class azure.mgmt.notificationhubs.types.MpnsCredentialProperties(TypedDict, total=False):
        key "certificateKey": Required[str]
        key "mpnsCertificate": Required[str]
        key "thumbprint": Required[str]
        certificate_key: str
        mpns_certificate: str
        thumbprint: str


    class azure.mgmt.notificationhubs.types.NamespacePatchParameters(TypedDict, total=False):
        key "properties": ForwardRef('NamespaceProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        properties: NamespaceProperties
        sku: Sku
        tags: dict[str, str]


    class azure.mgmt.notificationhubs.types.NamespaceProperties(TypedDict, total=False):
        key "createdAt": str
        key "critical": bool
        key "dataCenter": str
        key "enabled": bool
        key "metricId": str
        key "name": str
        key "namespaceType": Union[str, NamespaceType]
        key "networkAcls": ForwardRef('NetworkAcls', module='types')
        key "pnsCredentials": ForwardRef('PnsCredentials', module='types')
        key "provisioningState": Union[str, OperationProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "region": str
        key "replicationRegion": Union[str, ReplicationRegion]
        key "scaleUnit": str
        key "serviceBusEndpoint": str
        key "status": Union[str, NamespaceStatus]
        key "subscriptionId": str
        key "updatedAt": str
        key "zoneRedundancy": Union[str, ZoneRedundancyPreference]
        created_at: str
        critical: bool
        data_center: str
        enabled: bool
        metric_id: str
        name: str
        namespace_type: Union[str, NamespaceType]
        network_acls: NetworkAcls
        pns_credentials: PnsCredentials
        privateEndpointConnections: list[PrivateEndpointConnectionResource]
        private_endpoint_connections: list[PrivateEndpointConnectionResource]
        provisioning_state: Union[str, OperationProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        region: str
        replication_region: Union[str, ReplicationRegion]
        scale_unit: str
        service_bus_endpoint: str
        status: Union[str, NamespaceStatus]
        subscription_id: str
        updated_at: str
        zone_redundancy: Union[str, ZoneRedundancyPreference]


    class azure.mgmt.notificationhubs.types.NamespaceResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NamespaceProperties', module='types')
        key "sku": Required[Sku]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: NamespaceProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.notificationhubs.types.NetworkAcls(TypedDict, total=False):
        key "publicNetworkRule": ForwardRef('PublicInternetAuthorizationRule', module='types')
        ipRules: list[IpRule]
        ip_rules: list[IpRule]
        public_network_rule: PublicInternetAuthorizationRule


    class azure.mgmt.notificationhubs.types.NotificationHubPatchParameters(TypedDict, total=False):
        key "properties": ForwardRef('NotificationHubProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        properties: NotificationHubProperties
        sku: Sku
        tags: dict[str, str]


    class azure.mgmt.notificationhubs.types.NotificationHubProperties(TypedDict, total=False):
        key "admCredential": ForwardRef('AdmCredential', module='types')
        key "apnsCredential": ForwardRef('ApnsCredential', module='types')
        key "baiduCredential": ForwardRef('BaiduCredential', module='types')
        key "browserCredential": ForwardRef('BrowserCredential', module='types')
        key "dailyMaxActiveDevices": int
        key "fcmV1Credential": ForwardRef('FcmV1Credential', module='types')
        key "gcmCredential": ForwardRef('GcmCredential', module='types')
        key "mpnsCredential": ForwardRef('MpnsCredential', module='types')
        key "name": str
        key "registrationTtl": str
        key "wnsCredential": ForwardRef('WnsCredential', module='types')
        key "xiaomiCredential": ForwardRef('XiaomiCredential', module='types')
        adm_credential: AdmCredential
        apns_credential: ApnsCredential
        authorizationRules: list[SharedAccessAuthorizationRuleProperties]
        authorization_rules: list[SharedAccessAuthorizationRuleProperties]
        baidu_credential: BaiduCredential
        browser_credential: BrowserCredential
        daily_max_active_devices: int
        fcm_v1_credential: FcmV1Credential
        gcm_credential: GcmCredential
        mpns_credential: MpnsCredential
        name: str
        registration_ttl: str
        wns_credential: WnsCredential
        xiaomi_credential: XiaomiCredential


    class azure.mgmt.notificationhubs.types.NotificationHubResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NotificationHubProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: NotificationHubProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.notificationhubs.types.PnsCredentials(TypedDict, total=False):
        key "admCredential": ForwardRef('AdmCredential', module='types')
        key "apnsCredential": ForwardRef('ApnsCredential', module='types')
        key "baiduCredential": ForwardRef('BaiduCredential', module='types')
        key "browserCredential": ForwardRef('BrowserCredential', module='types')
        key "fcmV1Credential": ForwardRef('FcmV1Credential', module='types')
        key "gcmCredential": ForwardRef('GcmCredential', module='types')
        key "mpnsCredential": ForwardRef('MpnsCredential', module='types')
        key "wnsCredential": ForwardRef('WnsCredential', module='types')
        key "xiaomiCredential": ForwardRef('XiaomiCredential', module='types')
        adm_credential: AdmCredential
        apns_credential: ApnsCredential
        baidu_credential: BaiduCredential
        browser_credential: BrowserCredential
        fcm_v1_credential: FcmV1Credential
        gcm_credential: GcmCredential
        mpns_credential: MpnsCredential
        wns_credential: WnsCredential
        xiaomi_credential: XiaomiCredential


    class azure.mgmt.notificationhubs.types.PolicyKeyResource(TypedDict, total=False):
        key "policyKey": Required[Union[str, PolicyKeyType]]
        policy_key: Union[str, PolicyKeyType]


    class azure.mgmt.notificationhubs.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('RemotePrivateEndpointConnection', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('RemotePrivateLinkServiceConnectionState', module='types')
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        group_ids: list[str]
        private_endpoint: RemotePrivateEndpointConnection
        private_link_service_connection_state: RemotePrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.notificationhubs.types.PrivateEndpointConnectionResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.notificationhubs.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.notificationhubs.types.PublicInternetAuthorizationRule(TypedDict, total=False):
        key "rights": Required[list[Union[str, AccessRights]]]
        rights: list[Union[str, AccessRights]]


    class azure.mgmt.notificationhubs.types.RemotePrivateEndpointConnection(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.notificationhubs.types.RemotePrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateLinkConnectionStatus]
        actions_required: str
        description: str
        status: Union[str, PrivateLinkConnectionStatus]


    class azure.mgmt.notificationhubs.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.notificationhubs.types.SharedAccessAuthorizationRuleProperties(TypedDict, total=False):
        key "claimType": str
        key "claimValue": str
        key "createdTime": str
        key "keyName": str
        key "modifiedTime": str
        key "primaryKey": str
        key "revision": int
        key "rights": Required[list[Union[str, AccessRights]]]
        key "secondaryKey": str
        claim_type: str
        claim_value: str
        created_time: str
        key_name: str
        modified_time: str
        primary_key: str
        revision: int
        rights: list[Union[str, AccessRights]]
        secondary_key: str


    class azure.mgmt.notificationhubs.types.SharedAccessAuthorizationRuleResource(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('SharedAccessAuthorizationRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SharedAccessAuthorizationRuleProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.notificationhubs.types.Sku(TypedDict, total=False):
        key "capacity": int
        key "family": str
        key "name": Required[Union[str, SkuName]]
        key "size": str
        key "tier": str
        capacity: int
        family: str
        name: Union[str, SkuName]
        size: str
        tier: str


    class azure.mgmt.notificationhubs.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.notificationhubs.types.TrackedResource(Resource):
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


    class azure.mgmt.notificationhubs.types.WnsCredential(TypedDict, total=False):
        key "properties": Required[WnsCredentialProperties]
        properties: WnsCredentialProperties


    class azure.mgmt.notificationhubs.types.WnsCredentialProperties(TypedDict, total=False):
        key "certificateKey": str
        key "packageSid": str
        key "secretKey": str
        key "windowsLiveEndpoint": str
        key "wnsCertificate": str
        certificate_key: str
        package_sid: str
        secret_key: str
        windows_live_endpoint: str
        wns_certificate: str


    class azure.mgmt.notificationhubs.types.XiaomiCredential(TypedDict, total=False):
        key "properties": Required[XiaomiCredentialProperties]
        properties: XiaomiCredentialProperties


    class azure.mgmt.notificationhubs.types.XiaomiCredentialProperties(TypedDict, total=False):
        key "appSecret": str
        key "endpoint": str
        app_secret: str
        endpoint: str


```