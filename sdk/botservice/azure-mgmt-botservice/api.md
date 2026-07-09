```py
namespace azure.mgmt.botservice

    class azure.mgmt.botservice.AzureBotServiceMgmtClient: implements ContextManager 
        bot_connection: BotConnectionOperations
        bots: BotsOperations
        channels: ChannelsOperations
        direct_line: DirectLineOperations
        email: EmailOperations
        host_settings: HostSettingsOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operation_results: OperationResultsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        qn_amaker_endpoint_keys: QnAMakerEndpointKeysOperations

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


namespace azure.mgmt.botservice.aio

    class azure.mgmt.botservice.aio.AzureBotServiceMgmtClient: implements AsyncContextManager 
        bot_connection: BotConnectionOperations
        bots: BotsOperations
        channels: ChannelsOperations
        direct_line: DirectLineOperations
        email: EmailOperations
        host_settings: HostSettingsOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operation_results: OperationResultsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        qn_amaker_endpoint_keys: QnAMakerEndpointKeysOperations

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


namespace azure.mgmt.botservice.aio.operations

    class azure.mgmt.botservice.aio.operations.BotConnectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                parameters: ConnectionSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                parameters: ConnectionSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @distributed_trace
        def list_by_bot_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConnectionSetting]: ...

        @distributed_trace_async
        async def list_service_providers(self, **kwargs: Any) -> ServiceProviderResponseList: ...

        @distributed_trace_async
        async def list_with_secrets(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                parameters: ConnectionSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                parameters: ConnectionSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...


    class azure.mgmt.botservice.aio.operations.BotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Bot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Bot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> Bot: ...

        @overload
        async def get_check_name_availability(
                self, 
                parameters: CheckNameAvailabilityRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseBody: ...

        @overload
        async def get_check_name_availability(
                self, 
                parameters: CheckNameAvailabilityRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseBody: ...

        @overload
        async def get_check_name_availability(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseBody: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Bot]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Bot]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Bot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Bot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...


    class azure.mgmt.botservice.aio.operations.ChannelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                parameters: BotChannel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                parameters: BotChannel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> BotChannel: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BotChannel]: ...

        @distributed_trace_async
        async def list_with_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                **kwargs: Any
            ) -> ListChannelWithKeysResponse: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                parameters: BotChannel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                parameters: BotChannel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...


    class azure.mgmt.botservice.aio.operations.DirectLineOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, RegenerateKeysChannelName], 
                parameters: SiteInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, RegenerateKeysChannelName], 
                parameters: SiteInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, RegenerateKeysChannelName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...


    class azure.mgmt.botservice.aio.operations.EmailOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def create_sign_in_url(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> CreateEmailSignInUrlResponse: ...


    class azure.mgmt.botservice.aio.operations.HostSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(self, **kwargs: Any) -> HostSettingsResponse: ...


    class azure.mgmt.botservice.aio.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_reconcile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSecurityPerimeterConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.botservice.aio.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_get(
                self, 
                operation_result_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResultsDescription]: ...


    class azure.mgmt.botservice.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationEntity]: ...


    class azure.mgmt.botservice.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.botservice.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_by_bot_resource(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.botservice.aio.operations.QnAMakerEndpointKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def get(
                self, 
                parameters: QnAMakerEndpointKeysRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QnAMakerEndpointKeysResponse: ...

        @overload
        async def get(
                self, 
                parameters: QnAMakerEndpointKeysRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QnAMakerEndpointKeysResponse: ...

        @overload
        async def get(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QnAMakerEndpointKeysResponse: ...


namespace azure.mgmt.botservice.models

    class azure.mgmt.botservice.models.AccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCED = "Enforced"
        LEARNING = "Learning"


    class azure.mgmt.botservice.models.AcsChatChannel(Channel, discriminator='AcsChatChannel'):
        channel_name: Literal["AcsChatChannel"]
        etag: str
        location: str
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.AlexaChannel(Channel, discriminator='AlexaChannel'):
        channel_name: Literal["AlexaChannel"]
        etag: str
        location: str
        properties: Optional[AlexaChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[AlexaChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.AlexaChannelProperties(_Model):
        alexa_skill_id: str
        is_enabled: bool
        service_endpoint_uri: Optional[str]
        url_fragment: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                alexa_skill_id: str, 
                is_enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.Bot(ProxyResource):
        etag: Optional[str]
        id: str
        kind: Optional[Union[str, Kind]]
        location: Optional[str]
        name: str
        properties: Optional[BotProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[BotProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.BotChannel(ProxyResource):
        etag: Optional[str]
        id: str
        kind: Optional[Union[str, Kind]]
        location: Optional[str]
        name: str
        properties: Optional[Channel]
        sku: Optional[Sku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[Channel] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.BotProperties(_Model):
        all_settings: Optional[dict[str, str]]
        app_password_hint: Optional[str]
        cmek_encryption_status: Optional[str]
        cmek_key_vault_url: Optional[str]
        configured_channels: Optional[list[str]]
        description: Optional[str]
        developer_app_insight_key: Optional[str]
        developer_app_insights_api_key: Optional[str]
        developer_app_insights_application_id: Optional[str]
        disable_local_auth: Optional[bool]
        display_name: str
        enabled_channels: Optional[list[str]]
        endpoint: str
        endpoint_version: Optional[str]
        icon_url: Optional[str]
        is_cmek_enabled: Optional[bool]
        is_developer_app_insights_api_key_set: Optional[bool]
        is_streaming_supported: Optional[bool]
        luis_app_ids: Optional[list[str]]
        luis_key: Optional[str]
        manifest_url: Optional[str]
        migration_token: Optional[str]
        msa_app_id: str
        msa_app_msi_resource_id: Optional[str]
        msa_app_tenant_id: Optional[str]
        msa_app_type: Optional[Union[str, MsaAppType]]
        network_security_perimeter_configurations: Optional[list[NetworkSecurityPerimeterConfiguration]]
        open_with_hint: Optional[str]
        parameters: Optional[dict[str, str]]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        publishing_credentials: Optional[str]
        schema_transformation_version: Optional[str]
        storage_resource_id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                all_settings: Optional[dict[str, str]] = ..., 
                app_password_hint: Optional[str] = ..., 
                cmek_key_vault_url: Optional[str] = ..., 
                description: Optional[str] = ..., 
                developer_app_insight_key: Optional[str] = ..., 
                developer_app_insights_api_key: Optional[str] = ..., 
                developer_app_insights_application_id: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                display_name: str, 
                endpoint: str, 
                icon_url: Optional[str] = ..., 
                is_cmek_enabled: Optional[bool] = ..., 
                is_streaming_supported: Optional[bool] = ..., 
                luis_app_ids: Optional[list[str]] = ..., 
                luis_key: Optional[str] = ..., 
                manifest_url: Optional[str] = ..., 
                msa_app_id: str, 
                msa_app_msi_resource_id: Optional[str] = ..., 
                msa_app_tenant_id: Optional[str] = ..., 
                msa_app_type: Optional[Union[str, MsaAppType]] = ..., 
                open_with_hint: Optional[str] = ..., 
                parameters: Optional[dict[str, str]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                publishing_credentials: Optional[str] = ..., 
                schema_transformation_version: Optional[str] = ..., 
                storage_resource_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.Channel(_Model):
        channel_name: str
        etag: Optional[str]
        location: Optional[str]
        provisioning_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                channel_name: str, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ChannelName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACS_CHAT_CHANNEL = "AcsChatChannel"
        ALEXA_CHANNEL = "AlexaChannel"
        DIRECT_LINE_CHANNEL = "DirectLineChannel"
        DIRECT_LINE_SPEECH_CHANNEL = "DirectLineSpeechChannel"
        EMAIL_CHANNEL = "EmailChannel"
        FACEBOOK_CHANNEL = "FacebookChannel"
        KIK_CHANNEL = "KikChannel"
        LINE_CHANNEL = "LineChannel"
        M365_EXTENSIONS = "M365Extensions"
        MS_TEAMS_CHANNEL = "MsTeamsChannel"
        OMNICHANNEL = "Omnichannel"
        OUTLOOK_CHANNEL = "OutlookChannel"
        SEARCH_ASSISTANT = "SearchAssistant"
        SKYPE_CHANNEL = "SkypeChannel"
        SLACK_CHANNEL = "SlackChannel"
        SMS_CHANNEL = "SmsChannel"
        TELEGRAM_CHANNEL = "TelegramChannel"
        TELEPHONY_CHANNEL = "TelephonyChannel"
        WEB_CHAT_CHANNEL = "WebChatChannel"


    class azure.mgmt.botservice.models.ChannelSettings(_Model):
        bot_icon_url: Optional[str]
        bot_id: Optional[str]
        channel_display_name: Optional[str]
        channel_id: Optional[str]
        disable_local_auth: Optional[bool]
        extension_key1: Optional[str]
        extension_key2: Optional[str]
        is_enabled: Optional[bool]
        require_terms_agreement: Optional[bool]
        sites: Optional[list[Site]]

        @overload
        def __init__(
                self, 
                *, 
                bot_icon_url: Optional[str] = ..., 
                bot_id: Optional[str] = ..., 
                channel_display_name: Optional[str] = ..., 
                channel_id: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                extension_key1: Optional[str] = ..., 
                extension_key2: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                require_terms_agreement: Optional[bool] = ..., 
                sites: Optional[list[Site]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.CheckNameAvailabilityRequestBody(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.CheckNameAvailabilityResponseBody(_Model):
        abs_code: Optional[str]
        message: Optional[str]
        valid: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                abs_code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                valid: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ConnectionSetting(ProxyResource):
        etag: Optional[str]
        id: str
        kind: Optional[Union[str, Kind]]
        location: Optional[str]
        name: str
        properties: Optional[ConnectionSettingProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ConnectionSettingProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ConnectionSettingParameter(_Model):
        key: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ConnectionSettingProperties(_Model):
        client_id: Optional[str]
        client_secret: Optional[str]
        id: Optional[str]
        name: Optional[str]
        parameters: Optional[list[ConnectionSettingParameter]]
        provisioning_state: Optional[str]
        scopes: Optional[str]
        service_provider_display_name: Optional[str]
        service_provider_id: Optional[str]
        setting_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                parameters: Optional[list[ConnectionSettingParameter]] = ..., 
                provisioning_state: Optional[str] = ..., 
                scopes: Optional[str] = ..., 
                service_provider_display_name: Optional[str] = ..., 
                service_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.CreateEmailSignInUrlResponse(_Model):
        id: Optional[str]
        location: Optional[str]
        properties: Optional[CreateEmailSignInUrlResponseProperties]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[CreateEmailSignInUrlResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.CreateEmailSignInUrlResponseProperties(_Model):
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.botservice.models.DirectLineChannel(Channel, discriminator='DirectLineChannel'):
        channel_name: Literal["DirectLineChannel"]
        etag: str
        location: str
        properties: Optional[DirectLineChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[DirectLineChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.DirectLineChannelProperties(_Model):
        direct_line_embed_code: Optional[str]
        extension_key1: Optional[str]
        extension_key2: Optional[str]
        sites: Optional[list[DirectLineSite]]

        @overload
        def __init__(
                self, 
                *, 
                direct_line_embed_code: Optional[str] = ..., 
                extension_key1: Optional[str] = ..., 
                extension_key2: Optional[str] = ..., 
                sites: Optional[list[DirectLineSite]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.DirectLineSite(Site):
        app_id: str
        e_tag: str
        is_block_user_upload_enabled: bool
        is_detailed_logging_enabled: bool
        is_enabled: bool
        is_endpoint_parameters_enabled: bool
        is_no_storage_enabled: bool
        is_secure_site_enabled: bool
        is_token_enabled: bool
        is_v1_enabled: bool
        is_v3_enabled: bool
        is_web_chat_speech_enabled: bool
        is_webchat_preview_enabled: bool
        key: str
        key2: str
        site_id: str
        site_name: str
        tenant_id: str
        trusted_origins: list[str]

        @overload
        def __init__(
                self, 
                *, 
                app_id: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                is_block_user_upload_enabled: Optional[bool] = ..., 
                is_detailed_logging_enabled: Optional[bool] = ..., 
                is_enabled: bool, 
                is_endpoint_parameters_enabled: Optional[bool] = ..., 
                is_no_storage_enabled: Optional[bool] = ..., 
                is_secure_site_enabled: Optional[bool] = ..., 
                is_v1_enabled: Optional[bool] = ..., 
                is_v3_enabled: Optional[bool] = ..., 
                is_web_chat_speech_enabled: Optional[bool] = ..., 
                is_webchat_preview_enabled: Optional[bool] = ..., 
                site_name: str, 
                tenant_id: Optional[str] = ..., 
                trusted_origins: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.DirectLineSpeechChannel(Channel, discriminator='DirectLineSpeechChannel'):
        channel_name: Literal["DirectLineSpeechChannel"]
        etag: str
        location: str
        properties: Optional[DirectLineSpeechChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[DirectLineSpeechChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.DirectLineSpeechChannelProperties(_Model):
        cognitive_service_region: Optional[str]
        cognitive_service_resource_id: Optional[str]
        cognitive_service_subscription_key: Optional[str]
        custom_speech_model_id: Optional[str]
        custom_voice_deployment_id: Optional[str]
        is_default_bot_for_cog_svc_account: Optional[bool]
        is_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cognitive_service_region: Optional[str] = ..., 
                cognitive_service_resource_id: Optional[str] = ..., 
                cognitive_service_subscription_key: Optional[str] = ..., 
                custom_speech_model_id: Optional[str] = ..., 
                custom_voice_deployment_id: Optional[str] = ..., 
                is_default_bot_for_cog_svc_account: Optional[bool] = ..., 
                is_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.EmailChannel(Channel, discriminator='EmailChannel'):
        channel_name: Literal["EmailChannel"]
        etag: str
        location: str
        properties: Optional[EmailChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[EmailChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.EmailChannelAuthMethod(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRAPH = 1
        PASSWORD = 0


    class azure.mgmt.botservice.models.EmailChannelProperties(_Model):
        auth_method: Optional[Union[int, EmailChannelAuthMethod]]
        email_address: str
        is_enabled: bool
        magic_code: Optional[str]
        password: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auth_method: Optional[Union[int, EmailChannelAuthMethod]] = ..., 
                email_address: str, 
                is_enabled: bool, 
                magic_code: Optional[str] = ..., 
                password: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.Error(_Model):
        error: Optional[ErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.botservice.models.ErrorBody(_Model):
        code: str
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.botservice.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.FacebookChannel(Channel, discriminator='FacebookChannel'):
        channel_name: Literal["FacebookChannel"]
        etag: str
        location: str
        properties: Optional[FacebookChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[FacebookChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.FacebookChannelProperties(_Model):
        app_id: str
        app_secret: Optional[str]
        callback_url: Optional[str]
        is_enabled: bool
        pages: Optional[list[FacebookPage]]
        verify_token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                app_id: str, 
                app_secret: Optional[str] = ..., 
                is_enabled: bool, 
                pages: Optional[list[FacebookPage]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.FacebookPage(_Model):
        access_token: Optional[str]
        id: str

        @overload
        def __init__(
                self, 
                *, 
                access_token: Optional[str] = ..., 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.HostSettingsResponse(_Model):
        bot_open_id_metadata: Optional[str]
        o_auth_url: Optional[str]
        to_bot_from_channel_open_id_metadata_url: Optional[str]
        to_bot_from_channel_token_issuer: Optional[str]
        to_bot_from_emulator_open_id_metadata_url: Optional[str]
        to_channel_from_bot_login_url: Optional[str]
        to_channel_from_bot_o_auth_scope: Optional[str]
        validate_authority: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                bot_open_id_metadata: Optional[str] = ..., 
                o_auth_url: Optional[str] = ..., 
                to_bot_from_channel_open_id_metadata_url: Optional[str] = ..., 
                to_bot_from_channel_token_issuer: Optional[str] = ..., 
                to_bot_from_emulator_open_id_metadata_url: Optional[str] = ..., 
                to_channel_from_bot_login_url: Optional[str] = ..., 
                to_channel_from_bot_o_auth_scope: Optional[str] = ..., 
                validate_authority: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.Key(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY1 = "key1"
        KEY2 = "key2"


    class azure.mgmt.botservice.models.KikChannel(Channel, discriminator='KikChannel'):
        channel_name: Literal["KikChannel"]
        etag: str
        location: str
        properties: Optional[KikChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[KikChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.KikChannelProperties(_Model):
        api_key: Optional[str]
        is_enabled: bool
        is_validated: Optional[bool]
        user_name: str

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                is_enabled: bool, 
                is_validated: Optional[bool] = ..., 
                user_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZUREBOT = "azurebot"
        BOT = "bot"
        DESIGNER = "designer"
        FUNCTION = "function"
        SDK = "sdk"


    class azure.mgmt.botservice.models.LineChannel(Channel, discriminator='LineChannel'):
        channel_name: Literal["LineChannel"]
        etag: str
        location: str
        properties: Optional[LineChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[LineChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.LineChannelProperties(_Model):
        callback_url: Optional[str]
        is_validated: Optional[bool]
        line_registrations: list[LineRegistration]

        @overload
        def __init__(
                self, 
                *, 
                line_registrations: list[LineRegistration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.LineRegistration(_Model):
        channel_access_token: Optional[str]
        channel_secret: Optional[str]
        generated_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                channel_access_token: Optional[str] = ..., 
                channel_secret: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ListChannelWithKeysResponse(BotChannel):
        changed_time: Optional[str]
        entity_tag: Optional[str]
        etag: str
        id: str
        kind: Union[str, Kind]
        location: str
        name: str
        properties: Channel
        provisioning_state: Optional[str]
        resource: Optional[Channel]
        setting: Optional[ChannelSettings]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: list[str]

        @overload
        def __init__(
                self, 
                *, 
                changed_time: Optional[str] = ..., 
                entity_tag: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[Channel] = ..., 
                provisioning_state: Optional[str] = ..., 
                resource: Optional[Channel] = ..., 
                setting: Optional[ChannelSettings] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.M365Extensions(Channel, discriminator='M365Extensions'):
        channel_name: Literal["M365Extensions"]
        etag: str
        location: str
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.MsTeamsChannel(Channel, discriminator='MsTeamsChannel'):
        channel_name: Literal["MsTeamsChannel"]
        etag: str
        location: str
        properties: Optional[MsTeamsChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[MsTeamsChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.MsTeamsChannelProperties(_Model):
        accepted_terms: Optional[bool]
        calling_webhook: Optional[str]
        deployment_environment: Optional[str]
        enable_calling: Optional[bool]
        incoming_call_route: Optional[str]
        is_enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                accepted_terms: Optional[bool] = ..., 
                calling_webhook: Optional[str] = ..., 
                deployment_environment: Optional[str] = ..., 
                enable_calling: Optional[bool] = ..., 
                incoming_call_route: Optional[str] = ..., 
                is_enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.MsaAppType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTI_TENANT = "MultiTenant"
        SINGLE_TENANT = "SingleTenant"
        USER_ASSIGNED_MSI = "UserAssignedMSI"


    class azure.mgmt.botservice.models.NetworkSecurityPerimeter(_Model):
        id: Optional[str]
        location: Optional[str]
        perimeter_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                perimeter_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.NetworkSecurityPerimeterConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[NetworkSecurityPerimeterConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkSecurityPerimeterConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.NetworkSecurityPerimeterConfigurationProperties(_Model):
        network_security_perimeter: Optional[NetworkSecurityPerimeter]
        profile: Optional[Profile]
        provisioning_issues: Optional[list[ProvisioningIssue]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_association: Optional[ResourceAssociation]

        @overload
        def __init__(
                self, 
                *, 
                provisioning_issues: Optional[list[ProvisioningIssue]] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.NspAccessRule(_Model):
        name: Optional[str]
        properties: Optional[NspAccessRuleProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.NspAccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.botservice.models.NspAccessRuleProperties(_Model):
        address_prefixes: Optional[list[str]]
        direction: Optional[Union[str, NspAccessRuleDirection]]
        email_addresses: Optional[list[str]]
        fully_qualified_domain_names: Optional[list[str]]
        network_security_perimeters: Optional[list[NetworkSecurityPerimeter]]
        phone_numbers: Optional[list[str]]
        subscriptions: Optional[list[NspAccessRulePropertiesSubscriptionsItem]]

        @overload
        def __init__(
                self, 
                *, 
                address_prefixes: Optional[list[str]] = ..., 
                direction: Optional[Union[str, NspAccessRuleDirection]] = ..., 
                subscriptions: Optional[list[NspAccessRulePropertiesSubscriptionsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.NspAccessRulePropertiesSubscriptionsItem(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.Omnichannel(Channel, discriminator='Omnichannel'):
        channel_name: Literal["Omnichannel"]
        etag: str
        location: str
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.OperationDisplayInfo(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.OperationEntity(_Model):
        display: Optional[OperationDisplayInfo]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplayInfo] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.OperationResultStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        REQUESTED = "Requested"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.botservice.models.OperationResultsDescription(_Model):
        id: Optional[str]
        name: Optional[str]
        start_time: Optional[datetime]
        status: Optional[Union[str, OperationResultStatus]]


    class azure.mgmt.botservice.models.OutlookChannel(Channel, discriminator='OutlookChannel'):
        channel_name: Literal["OutlookChannel"]
        etag: str
        location: str
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.botservice.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.botservice.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                group_ids: Optional[list[str]] = ..., 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.botservice.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.botservice.models.PrivateLinkResource(PrivateLinkResourceBase):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.botservice.models.PrivateLinkResourceBase(_Model):
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]


    class azure.mgmt.botservice.models.PrivateLinkResourceListResult(_Model):
        value: Optional[list[PrivateLinkResource]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateLinkResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.Profile(_Model):
        access_rules: Optional[list[NspAccessRule]]
        access_rules_version: Optional[int]
        diagnostic_settings_version: Optional[int]
        enabled_log_categories: Optional[list[str]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_rules: Optional[list[NspAccessRule]] = ..., 
                access_rules_version: Optional[int] = ..., 
                diagnostic_settings_version: Optional[int] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ProvisioningIssue(_Model):
        name: Optional[str]
        properties: Optional[ProvisioningIssueProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ProvisioningIssueProperties(_Model):
        description: Optional[str]
        issue_type: Optional[str]
        severity: Optional[Union[str, Severity]]
        suggested_access_rules: Optional[list[NspAccessRule]]
        suggested_resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                issue_type: Optional[str] = ..., 
                severity: Optional[Union[str, Severity]] = ..., 
                suggested_access_rules: Optional[list[NspAccessRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.botservice.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.botservice.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.botservice.models.QnAMakerEndpointKeysRequestBody(_Model):
        authkey: Optional[str]
        hostname: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authkey: Optional[str] = ..., 
                hostname: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.QnAMakerEndpointKeysResponse(_Model):
        installed_version: Optional[str]
        last_stable_version: Optional[str]
        primary_endpoint_key: Optional[str]
        secondary_endpoint_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                installed_version: Optional[str] = ..., 
                last_stable_version: Optional[str] = ..., 
                primary_endpoint_key: Optional[str] = ..., 
                secondary_endpoint_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.RegenerateKeysChannelName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT_LINE_CHANNEL = "DirectLineChannel"
        WEB_CHAT_CHANNEL = "WebChatChannel"


    class azure.mgmt.botservice.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.botservice.models.ResourceAssociation(_Model):
        access_mode: Optional[Union[str, AccessMode]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, AccessMode]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.SearchAssistant(Channel, discriminator='SearchAssistant'):
        channel_name: Literal["SearchAssistant"]
        etag: str
        location: str
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ServiceProvider(_Model):
        properties: Optional[ServiceProviderProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceProviderProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ServiceProviderParameter(_Model):
        default: Optional[str]
        description: Optional[str]
        display_name: Optional[str]
        help_url: Optional[str]
        metadata: Optional[ServiceProviderParameterMetadata]
        name: Optional[str]
        type: Optional[str]


    class azure.mgmt.botservice.models.ServiceProviderParameterMetadata(_Model):
        constraints: Optional[ServiceProviderParameterMetadataConstraints]

        @overload
        def __init__(
                self, 
                *, 
                constraints: Optional[ServiceProviderParameterMetadataConstraints] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ServiceProviderParameterMetadataConstraints(_Model):
        required: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                required: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ServiceProviderProperties(_Model):
        dev_portal_url: Optional[str]
        display_name: Optional[str]
        icon_url: Optional[str]
        id: Optional[str]
        parameters: Optional[list[ServiceProviderParameter]]
        service_provider_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                icon_url: Optional[str] = ..., 
                parameters: Optional[list[ServiceProviderParameter]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.ServiceProviderResponseList(_Model):
        next_link: Optional[str]
        value: Optional[list[ServiceProvider]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        WARNING = "Warning"


    class azure.mgmt.botservice.models.Site(_Model):
        app_id: Optional[str]
        e_tag: Optional[str]
        is_block_user_upload_enabled: Optional[bool]
        is_detailed_logging_enabled: Optional[bool]
        is_enabled: bool
        is_endpoint_parameters_enabled: Optional[bool]
        is_no_storage_enabled: Optional[bool]
        is_secure_site_enabled: Optional[bool]
        is_token_enabled: Optional[bool]
        is_v1_enabled: Optional[bool]
        is_v3_enabled: Optional[bool]
        is_web_chat_speech_enabled: Optional[bool]
        is_webchat_preview_enabled: Optional[bool]
        key: Optional[str]
        key2: Optional[str]
        site_id: Optional[str]
        site_name: str
        tenant_id: Optional[str]
        trusted_origins: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                app_id: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                is_block_user_upload_enabled: Optional[bool] = ..., 
                is_detailed_logging_enabled: Optional[bool] = ..., 
                is_enabled: bool, 
                is_endpoint_parameters_enabled: Optional[bool] = ..., 
                is_no_storage_enabled: Optional[bool] = ..., 
                is_secure_site_enabled: Optional[bool] = ..., 
                is_v1_enabled: Optional[bool] = ..., 
                is_v3_enabled: Optional[bool] = ..., 
                is_web_chat_speech_enabled: Optional[bool] = ..., 
                is_webchat_preview_enabled: Optional[bool] = ..., 
                site_name: str, 
                tenant_id: Optional[str] = ..., 
                trusted_origins: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.SiteInfo(_Model):
        key: Union[str, Key]
        site_name: str

        @overload
        def __init__(
                self, 
                *, 
                key: Union[str, Key], 
                site_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.Sku(_Model):
        name: Union[str, SkuName]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, SkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        F0 = "F0"
        S1 = "S1"


    class azure.mgmt.botservice.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREE = "Free"
        STANDARD = "Standard"


    class azure.mgmt.botservice.models.SkypeChannel(Channel, discriminator='SkypeChannel'):
        channel_name: Literal["SkypeChannel"]
        etag: str
        location: str
        properties: Optional[SkypeChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[SkypeChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.SkypeChannelProperties(_Model):
        calling_web_hook: Optional[str]
        enable_calling: Optional[bool]
        enable_groups: Optional[bool]
        enable_media_cards: Optional[bool]
        enable_messaging: Optional[bool]
        enable_screen_sharing: Optional[bool]
        enable_video: Optional[bool]
        groups_mode: Optional[str]
        incoming_call_route: Optional[str]
        is_enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                calling_web_hook: Optional[str] = ..., 
                enable_calling: Optional[bool] = ..., 
                enable_groups: Optional[bool] = ..., 
                enable_media_cards: Optional[bool] = ..., 
                enable_messaging: Optional[bool] = ..., 
                enable_screen_sharing: Optional[bool] = ..., 
                enable_video: Optional[bool] = ..., 
                groups_mode: Optional[str] = ..., 
                incoming_call_route: Optional[str] = ..., 
                is_enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.SlackChannel(Channel, discriminator='SlackChannel'):
        channel_name: Literal["SlackChannel"]
        etag: str
        location: str
        properties: Optional[SlackChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[SlackChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.SlackChannelProperties(_Model):
        client_id: Optional[str]
        client_secret: Optional[str]
        is_enabled: bool
        is_validated: Optional[bool]
        landing_page_url: Optional[str]
        last_submission_id: Optional[str]
        redirect_action: Optional[str]
        register_before_o_auth_flow: Optional[bool]
        scopes: Optional[str]
        signing_secret: Optional[str]
        verification_token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                is_enabled: bool, 
                landing_page_url: Optional[str] = ..., 
                register_before_o_auth_flow: Optional[bool] = ..., 
                scopes: Optional[str] = ..., 
                signing_secret: Optional[str] = ..., 
                verification_token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.SmsChannel(Channel, discriminator='SmsChannel'):
        channel_name: Literal["SmsChannel"]
        etag: str
        location: str
        properties: Optional[SmsChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[SmsChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.SmsChannelProperties(_Model):
        account_sid: str
        auth_token: Optional[str]
        is_enabled: bool
        is_validated: Optional[bool]
        phone: str

        @overload
        def __init__(
                self, 
                *, 
                account_sid: str, 
                auth_token: Optional[str] = ..., 
                is_enabled: bool, 
                is_validated: Optional[bool] = ..., 
                phone: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.SystemData(_Model):
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


    class azure.mgmt.botservice.models.TelegramChannel(Channel, discriminator='TelegramChannel'):
        channel_name: Literal["TelegramChannel"]
        etag: str
        location: str
        properties: Optional[TelegramChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[TelegramChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.TelegramChannelProperties(_Model):
        access_token: Optional[str]
        is_enabled: bool
        is_validated: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                access_token: Optional[str] = ..., 
                is_enabled: bool, 
                is_validated: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.TelephonyChannel(Channel, discriminator='TelephonyChannel'):
        channel_name: Literal["TelephonyChannel"]
        etag: str
        location: str
        properties: Optional[TelephonyChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[TelephonyChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.TelephonyChannelProperties(_Model):
        api_configurations: Optional[list[TelephonyChannelResourceApiConfiguration]]
        cognitive_service_region: Optional[str]
        cognitive_service_subscription_key: Optional[str]
        default_locale: Optional[str]
        is_enabled: Optional[bool]
        phone_numbers: Optional[list[TelephonyPhoneNumbers]]
        premium_sku: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_configurations: Optional[list[TelephonyChannelResourceApiConfiguration]] = ..., 
                cognitive_service_region: Optional[str] = ..., 
                cognitive_service_subscription_key: Optional[str] = ..., 
                default_locale: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                phone_numbers: Optional[list[TelephonyPhoneNumbers]] = ..., 
                premium_sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.TelephonyChannelResourceApiConfiguration(_Model):
        cognitive_service_region: Optional[str]
        cognitive_service_resource_id: Optional[str]
        cognitive_service_subscription_key: Optional[str]
        default_locale: Optional[str]
        id: Optional[str]
        provider_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cognitive_service_region: Optional[str] = ..., 
                cognitive_service_resource_id: Optional[str] = ..., 
                cognitive_service_subscription_key: Optional[str] = ..., 
                default_locale: Optional[str] = ..., 
                id: Optional[str] = ..., 
                provider_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.TelephonyPhoneNumbers(_Model):
        acs_endpoint: Optional[str]
        acs_resource_id: Optional[str]
        acs_secret: Optional[str]
        cognitive_service_region: Optional[str]
        cognitive_service_resource_id: Optional[str]
        cognitive_service_subscription_key: Optional[str]
        default_locale: Optional[str]
        id: Optional[str]
        offer_type: Optional[str]
        phone_number: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                acs_endpoint: Optional[str] = ..., 
                acs_resource_id: Optional[str] = ..., 
                acs_secret: Optional[str] = ..., 
                cognitive_service_region: Optional[str] = ..., 
                cognitive_service_resource_id: Optional[str] = ..., 
                cognitive_service_subscription_key: Optional[str] = ..., 
                default_locale: Optional[str] = ..., 
                id: Optional[str] = ..., 
                offer_type: Optional[str] = ..., 
                phone_number: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.WebChatChannel(Channel, discriminator='WebChatChannel'):
        channel_name: Literal["WebChatChannel"]
        etag: str
        location: str
        properties: Optional[WebChatChannelProperties]
        provisioning_state: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[WebChatChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.WebChatChannelProperties(_Model):
        sites: Optional[list[WebChatSite]]
        web_chat_embed_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                sites: Optional[list[WebChatSite]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.botservice.models.WebChatSite(Site):
        app_id: str
        e_tag: str
        is_block_user_upload_enabled: bool
        is_detailed_logging_enabled: bool
        is_enabled: bool
        is_endpoint_parameters_enabled: bool
        is_no_storage_enabled: bool
        is_secure_site_enabled: bool
        is_token_enabled: bool
        is_v1_enabled: bool
        is_v3_enabled: bool
        is_web_chat_speech_enabled: bool
        is_webchat_preview_enabled: bool
        key: str
        key2: str
        site_id: str
        site_name: str
        tenant_id: str
        trusted_origins: list[str]

        @overload
        def __init__(
                self, 
                *, 
                app_id: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                is_block_user_upload_enabled: Optional[bool] = ..., 
                is_detailed_logging_enabled: Optional[bool] = ..., 
                is_enabled: bool, 
                is_endpoint_parameters_enabled: Optional[bool] = ..., 
                is_no_storage_enabled: Optional[bool] = ..., 
                is_secure_site_enabled: Optional[bool] = ..., 
                is_v1_enabled: Optional[bool] = ..., 
                is_v3_enabled: Optional[bool] = ..., 
                is_web_chat_speech_enabled: Optional[bool] = ..., 
                is_webchat_preview_enabled: Optional[bool] = ..., 
                site_name: str, 
                tenant_id: Optional[str] = ..., 
                trusted_origins: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.botservice.operations

    class azure.mgmt.botservice.operations.BotConnectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                parameters: ConnectionSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                parameters: ConnectionSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @distributed_trace
        def list_by_bot_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ConnectionSetting]: ...

        @distributed_trace
        def list_service_providers(self, **kwargs: Any) -> ServiceProviderResponseList: ...

        @distributed_trace
        def list_with_secrets(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                parameters: ConnectionSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                parameters: ConnectionSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...


    class azure.mgmt.botservice.operations.BotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Bot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Bot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> Bot: ...

        @overload
        def get_check_name_availability(
                self, 
                parameters: CheckNameAvailabilityRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseBody: ...

        @overload
        def get_check_name_availability(
                self, 
                parameters: CheckNameAvailabilityRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseBody: ...

        @overload
        def get_check_name_availability(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseBody: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Bot]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Bot]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Bot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Bot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...


    class azure.mgmt.botservice.operations.ChannelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                parameters: BotChannel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                parameters: BotChannel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> BotChannel: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BotChannel]: ...

        @distributed_trace
        def list_with_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                **kwargs: Any
            ) -> ListChannelWithKeysResponse: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                parameters: BotChannel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                parameters: BotChannel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...


    class azure.mgmt.botservice.operations.DirectLineOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, RegenerateKeysChannelName], 
                parameters: SiteInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, RegenerateKeysChannelName], 
                parameters: SiteInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, RegenerateKeysChannelName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...


    class azure.mgmt.botservice.operations.EmailOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def create_sign_in_url(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> CreateEmailSignInUrlResponse: ...


    class azure.mgmt.botservice.operations.HostSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(self, **kwargs: Any) -> HostSettingsResponse: ...


    class azure.mgmt.botservice.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_reconcile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkSecurityPerimeterConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.botservice.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_get(
                self, 
                operation_result_id: str, 
                **kwargs: Any
            ) -> LROPoller[OperationResultsDescription]: ...


    class azure.mgmt.botservice.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationEntity]: ...


    class azure.mgmt.botservice.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.botservice.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_bot_resource(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.botservice.operations.QnAMakerEndpointKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def get(
                self, 
                parameters: QnAMakerEndpointKeysRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QnAMakerEndpointKeysResponse: ...

        @overload
        def get(
                self, 
                parameters: QnAMakerEndpointKeysRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QnAMakerEndpointKeysResponse: ...

        @overload
        def get(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QnAMakerEndpointKeysResponse: ...


namespace azure.mgmt.botservice.types

    class azure.mgmt.botservice.types.AcsChatChannel(TypedDict, total=False):
        key "channelName": Required[Literal["AcsChatChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "provisioningState": str
        channel_name: Literal[AcsChatChannel]
        etag: str
        location: str
        provisioning_state: str


    class azure.mgmt.botservice.types.AlexaChannel(TypedDict, total=False):
        key "channelName": Required[Literal["AlexaChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('AlexaChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[AlexaChannel]
        etag: str
        location: str
        properties: AlexaChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.AlexaChannelProperties(TypedDict, total=False):
        key "alexaSkillId": Required[str]
        key "isEnabled": Required[bool]
        key "serviceEndpointUri": str
        key "urlFragment": str
        alexa_skill_id: str
        is_enabled: bool
        service_endpoint_uri: str
        url_fragment: str


    class azure.mgmt.botservice.types.Bot(ProxyResource):
        key "etag": str
        key "id": str
        key "kind": Union[str, Kind]
        key "location": str
        key "name": str
        key "properties": ForwardRef('BotProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Union[str, Kind]
        location: str
        name: str
        properties: BotProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: list[str]


    class azure.mgmt.botservice.types.BotChannel(ProxyResource):
        key "etag": str
        key "id": str
        key "kind": Union[str, Kind]
        key "location": str
        key "name": str
        key "properties": ForwardRef('Channel', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Union[str, Kind]
        location: str
        name: str
        properties: Channel
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: list[str]


    class azure.mgmt.botservice.types.BotProperties(TypedDict, total=False):
        key "appPasswordHint": str
        key "cmekEncryptionStatus": str
        key "cmekKeyVaultUrl": str
        key "description": str
        key "developerAppInsightKey": str
        key "developerAppInsightsApiKey": str
        key "developerAppInsightsApplicationId": str
        key "disableLocalAuth": bool
        key "displayName": Required[str]
        key "endpoint": Required[Optional[str]]
        key "endpointVersion": str
        key "iconUrl": str
        key "isCmekEnabled": bool
        key "isDeveloperAppInsightsApiKeySet": bool
        key "isStreamingSupported": bool
        key "luisKey": str
        key "manifestUrl": str
        key "migrationToken": str
        key "msaAppId": Required[str]
        key "msaAppMSIResourceId": str
        key "msaAppTenantId": str
        key "msaAppType": Union[str, MsaAppType]
        key "openWithHint": str
        key "provisioningState": str
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "publishingCredentials": str
        key "schemaTransformationVersion": Optional[str]
        key "storageResourceId": str
        key "tenantId": str
        allSettings: dict[str, str]
        all_settings: dict[str, str]
        app_password_hint: str
        cmek_encryption_status: str
        cmek_key_vault_url: str
        configuredChannels: list[str]
        configured_channels: list[str]
        description: str
        developer_app_insight_key: str
        developer_app_insights_api_key: str
        developer_app_insights_application_id: str
        disable_local_auth: bool
        display_name: str
        enabledChannels: list[str]
        enabled_channels: list[str]
        endpoint: str
        endpoint_version: str
        icon_url: str
        is_cmek_enabled: bool
        is_developer_app_insights_api_key_set: bool
        is_streaming_supported: bool
        luisAppIds: list[str]
        luis_app_ids: list[str]
        luis_key: str
        manifest_url: str
        migration_token: str
        msa_app_id: str
        msa_app_msi_resource_id: str
        msa_app_tenant_id: str
        msa_app_type: Union[str, MsaAppType]
        networkSecurityPerimeterConfigurations: list[NetworkSecurityPerimeterConfiguration]
        network_security_perimeter_configurations: list[NetworkSecurityPerimeterConfiguration]
        open_with_hint: str
        parameters: dict[str, str]
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        public_network_access: Union[str, PublicNetworkAccess]
        publishing_credentials: str
        schema_transformation_version: str
        storage_resource_id: str
        tenant_id: str


    class azure.mgmt.botservice.types.ChannelSettings(TypedDict, total=False):
        key "botIconUrl": str
        key "botId": str
        key "channelDisplayName": str
        key "channelId": str
        key "disableLocalAuth": bool
        key "extensionKey1": str
        key "extensionKey2": str
        key "isEnabled": bool
        key "requireTermsAgreement": bool
        bot_icon_url: str
        bot_id: str
        channel_display_name: str
        channel_id: str
        disable_local_auth: bool
        extension_key1: str
        extension_key2: str
        is_enabled: bool
        require_terms_agreement: bool
        sites: list[Site]


    class azure.mgmt.botservice.types.CheckNameAvailabilityRequestBody(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.botservice.types.CheckNameAvailabilityResponseBody(TypedDict, total=False):
        key "absCode": str
        key "message": str
        key "valid": bool
        abs_code: str
        message: str
        valid: bool


    class azure.mgmt.botservice.types.ConnectionSetting(ProxyResource):
        key "etag": str
        key "id": str
        key "kind": Union[str, Kind]
        key "location": str
        key "name": str
        key "properties": ForwardRef('ConnectionSettingProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Union[str, Kind]
        location: str
        name: str
        properties: ConnectionSettingProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: list[str]


    class azure.mgmt.botservice.types.ConnectionSettingParameter(TypedDict, total=False):
        key "key": str
        key "value": Optional[str]
        key: str
        value: str


    class azure.mgmt.botservice.types.ConnectionSettingProperties(TypedDict, total=False):
        key "clientId": str
        key "clientSecret": str
        key "id": str
        key "name": str
        key "provisioningState": str
        key "scopes": str
        key "serviceProviderDisplayName": str
        key "serviceProviderId": str
        key "settingId": str
        client_id: str
        client_secret: str
        id: str
        name: str
        parameters: list[ConnectionSettingParameter]
        provisioning_state: str
        scopes: str
        service_provider_display_name: str
        service_provider_id: str
        setting_id: str


    class azure.mgmt.botservice.types.CreateEmailSignInUrlResponse(TypedDict, total=False):
        key "id": str
        key "location": str
        key "properties": ForwardRef('CreateEmailSignInUrlResponseProperties', module='types')
        id: str
        location: str
        properties: CreateEmailSignInUrlResponseProperties


    class azure.mgmt.botservice.types.CreateEmailSignInUrlResponseProperties(TypedDict, total=False):
        key "url": str
        url: str


    class azure.mgmt.botservice.types.DirectLineChannel(TypedDict, total=False):
        key "channelName": Required[Literal["DirectLineChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('DirectLineChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[DirectLineChannel]
        etag: str
        location: str
        properties: DirectLineChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.DirectLineChannelProperties(TypedDict, total=False):
        key "DirectLineEmbedCode": str
        key "extensionKey1": str
        key "extensionKey2": str
        direct_line_embed_code: str
        extension_key1: str
        extension_key2: str
        sites: list[DirectLineSite]


    class azure.mgmt.botservice.types.DirectLineSite(Site):
        key "appId": str
        key "eTag": str
        key "isBlockUserUploadEnabled": Optional[bool]
        key "isDetailedLoggingEnabled": bool
        key "isEnabled": Required[bool]
        key "isEndpointParametersEnabled": bool
        key "isNoStorageEnabled": bool
        key "isSecureSiteEnabled": bool
        key "isTokenEnabled": bool
        key "isV1Enabled": bool
        key "isV3Enabled": bool
        key "isWebChatSpeechEnabled": bool
        key "isWebchatPreviewEnabled": bool
        key "key": str
        key "key2": str
        key "siteId": str
        key "siteName": Required[str]
        key "tenantId": str
        app_id: str
        e_tag: str
        is_block_user_upload_enabled: bool
        is_detailed_logging_enabled: bool
        is_enabled: bool
        is_endpoint_parameters_enabled: bool
        is_no_storage_enabled: bool
        is_secure_site_enabled: bool
        is_token_enabled: bool
        is_v1_enabled: bool
        is_v3_enabled: bool
        is_web_chat_speech_enabled: bool
        is_webchat_preview_enabled: bool
        key: str
        key2: str
        site_id: str
        site_name: str
        tenant_id: str
        trustedOrigins: list[str]
        trusted_origins: list[str]


    class azure.mgmt.botservice.types.DirectLineSpeechChannel(TypedDict, total=False):
        key "channelName": Required[Literal["DirectLineSpeechChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('DirectLineSpeechChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[DirectLineSpeechChannel]
        etag: str
        location: str
        properties: DirectLineSpeechChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.DirectLineSpeechChannelProperties(TypedDict, total=False):
        key "cognitiveServiceRegion": Optional[str]
        key "cognitiveServiceResourceId": str
        key "cognitiveServiceSubscriptionKey": Optional[str]
        key "customSpeechModelId": str
        key "customVoiceDeploymentId": str
        key "isDefaultBotForCogSvcAccount": bool
        key "isEnabled": bool
        cognitive_service_region: str
        cognitive_service_resource_id: str
        cognitive_service_subscription_key: str
        custom_speech_model_id: str
        custom_voice_deployment_id: str
        is_default_bot_for_cog_svc_account: bool
        is_enabled: bool


    class azure.mgmt.botservice.types.EmailChannel(TypedDict, total=False):
        key "channelName": Required[Literal["EmailChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('EmailChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[EmailChannel]
        etag: str
        location: str
        properties: EmailChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.EmailChannelProperties(TypedDict, total=False):
        key "authMethod": Union[int, EmailChannelAuthMethod]
        key "emailAddress": Required[str]
        key "isEnabled": Required[bool]
        key "magicCode": str
        key "password": str
        auth_method: Union[int, EmailChannelAuthMethod]
        email_address: str
        is_enabled: bool
        magic_code: str
        password: str


    class azure.mgmt.botservice.types.Error(TypedDict, total=False):
        key "error": ForwardRef('ErrorBody', module='types')
        error: ErrorBody


    class azure.mgmt.botservice.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.botservice.types.ErrorBody(TypedDict, total=False):
        key "code": Required[str]
        key "message": Required[str]
        code: str
        message: str


    class azure.mgmt.botservice.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.botservice.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.botservice.types.FacebookChannel(TypedDict, total=False):
        key "channelName": Required[Literal["FacebookChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('FacebookChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[FacebookChannel]
        etag: str
        location: str
        properties: FacebookChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.FacebookChannelProperties(TypedDict, total=False):
        key "appId": Required[str]
        key "appSecret": str
        key "callbackUrl": str
        key "isEnabled": Required[bool]
        key "verifyToken": str
        app_id: str
        app_secret: str
        callback_url: str
        is_enabled: bool
        pages: list[FacebookPage]
        verify_token: str


    class azure.mgmt.botservice.types.FacebookPage(TypedDict, total=False):
        key "accessToken": str
        key "id": Required[str]
        access_token: str
        id: str


    class azure.mgmt.botservice.types.HostSettingsResponse(TypedDict, total=False):
        key "BotOpenIdMetadata": str
        key "OAuthUrl": str
        key "ToBotFromChannelOpenIdMetadataUrl": str
        key "ToBotFromChannelTokenIssuer": str
        key "ToBotFromEmulatorOpenIdMetadataUrl": str
        key "ToChannelFromBotLoginUrl": str
        key "ToChannelFromBotOAuthScope": str
        key "ValidateAuthority": bool
        bot_open_id_metadata: str
        o_auth_url: str
        to_bot_from_channel_open_id_metadata_url: str
        to_bot_from_channel_token_issuer: str
        to_bot_from_emulator_open_id_metadata_url: str
        to_channel_from_bot_login_url: str
        to_channel_from_bot_o_auth_scope: str
        validate_authority: bool


    class azure.mgmt.botservice.types.KikChannel(TypedDict, total=False):
        key "channelName": Required[Literal["KikChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('KikChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[KikChannel]
        etag: str
        location: str
        properties: KikChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.KikChannelProperties(TypedDict, total=False):
        key "apiKey": str
        key "isEnabled": Required[bool]
        key "isValidated": bool
        key "userName": Required[str]
        api_key: str
        is_enabled: bool
        is_validated: bool
        user_name: str


    class azure.mgmt.botservice.types.LineChannel(TypedDict, total=False):
        key "channelName": Required[Literal["LineChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('LineChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[LineChannel]
        etag: str
        location: str
        properties: LineChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.LineChannelProperties(TypedDict, total=False):
        key "callbackUrl": str
        key "isValidated": bool
        key "lineRegistrations": Required[list[LineRegistration]]
        callback_url: str
        is_validated: bool
        line_registrations: list[LineRegistration]


    class azure.mgmt.botservice.types.LineRegistration(TypedDict, total=False):
        key "channelAccessToken": str
        key "channelSecret": str
        key "generatedId": str
        channel_access_token: str
        channel_secret: str
        generated_id: str


    class azure.mgmt.botservice.types.ListChannelWithKeysResponse(BotChannel):
        key "changedTime": str
        key "entityTag": str
        key "etag": str
        key "id": str
        key "kind": Union[str, Kind]
        key "location": str
        key "name": str
        key "properties": ForwardRef('Channel', module='types')
        key "provisioningState": str
        key "resource": ForwardRef('Channel', module='types')
        key "setting": ForwardRef('ChannelSettings', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        changed_time: str
        entity_tag: str
        etag: str
        id: str
        kind: Union[str, Kind]
        location: str
        name: str
        properties: Channel
        provisioning_state: str
        resource: Channel
        setting: ChannelSettings
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: list[str]


    class azure.mgmt.botservice.types.M365Extensions(TypedDict, total=False):
        key "channelName": Required[Literal["M365Extensions"]]
        key "etag": Optional[str]
        key "location": str
        key "provisioningState": str
        channel_name: Literal[M365Extensions]
        etag: str
        location: str
        provisioning_state: str


    class azure.mgmt.botservice.types.MsTeamsChannel(TypedDict, total=False):
        key "channelName": Required[Literal["MsTeamsChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('MsTeamsChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[MsTeamsChannel]
        etag: str
        location: str
        properties: MsTeamsChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.MsTeamsChannelProperties(TypedDict, total=False):
        key "acceptedTerms": Optional[bool]
        key "callingWebhook": str
        key "deploymentEnvironment": str
        key "enableCalling": bool
        key "incomingCallRoute": str
        key "isEnabled": Required[bool]
        accepted_terms: bool
        calling_webhook: str
        deployment_environment: str
        enable_calling: bool
        incoming_call_route: str
        is_enabled: bool


    class azure.mgmt.botservice.types.NetworkSecurityPerimeter(TypedDict, total=False):
        key "id": str
        key "location": str
        key "perimeterGuid": str
        id: str
        location: str
        perimeter_guid: str


    class azure.mgmt.botservice.types.NetworkSecurityPerimeterConfiguration(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('NetworkSecurityPerimeterConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: NetworkSecurityPerimeterConfigurationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.botservice.types.NetworkSecurityPerimeterConfigurationProperties(TypedDict, total=False):
        key "networkSecurityPerimeter": ForwardRef('NetworkSecurityPerimeter', module='types')
        key "profile": ForwardRef('Profile', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "resourceAssociation": ForwardRef('ResourceAssociation', module='types')
        network_security_perimeter: NetworkSecurityPerimeter
        profile: Profile
        provisioningIssues: list[ProvisioningIssue]
        provisioning_issues: list[ProvisioningIssue]
        provisioning_state: Union[str, ProvisioningState]
        resource_association: ResourceAssociation


    class azure.mgmt.botservice.types.NspAccessRule(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('NspAccessRuleProperties', module='types')
        name: str
        properties: NspAccessRuleProperties


    class azure.mgmt.botservice.types.NspAccessRuleProperties(TypedDict, total=False):
        key "direction": Union[str, NspAccessRuleDirection]
        addressPrefixes: list[str]
        address_prefixes: list[str]
        direction: Union[str, NspAccessRuleDirection]
        emailAddresses: list[str]
        email_addresses: list[str]
        fullyQualifiedDomainNames: list[str]
        fully_qualified_domain_names: list[str]
        networkSecurityPerimeters: list[NetworkSecurityPerimeter]
        network_security_perimeters: list[NetworkSecurityPerimeter]
        phoneNumbers: list[str]
        phone_numbers: list[str]
        subscriptions: list[NspAccessRulePropertiesSubscriptionsItem]


    class azure.mgmt.botservice.types.NspAccessRulePropertiesSubscriptionsItem(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.botservice.types.Omnichannel(TypedDict, total=False):
        key "channelName": Required[Literal["Omnichannel"]]
        key "etag": Optional[str]
        key "location": str
        key "provisioningState": str
        channel_name: Literal[Omnichannel]
        etag: str
        location: str
        provisioning_state: str


    class azure.mgmt.botservice.types.OperationDisplayInfo(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.botservice.types.OperationEntity(TypedDict, total=False):
        key "display": ForwardRef('OperationDisplayInfo', module='types')
        key "name": str
        key "origin": str
        key "properties": Any
        display: OperationDisplayInfo
        name: str
        origin: str
        properties: Any


    class azure.mgmt.botservice.types.OperationResultsDescription(TypedDict, total=False):
        key "id": str
        key "name": str
        key "startTime": str
        key "status": Union[str, OperationResultStatus]
        id: str
        name: str
        start_time: str
        status: Union[str, OperationResultStatus]


    class azure.mgmt.botservice.types.OutlookChannel(TypedDict, total=False):
        key "channelName": Required[Literal["OutlookChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "provisioningState": str
        channel_name: Literal[OutlookChannel]
        etag: str
        location: str
        provisioning_state: str


    class azure.mgmt.botservice.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.botservice.types.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.botservice.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        group_ids: list[str]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.botservice.types.PrivateLinkResource(PrivateLinkResourceBase):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateLinkResourceProperties', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateLinkResourceProperties
        type: str


    class azure.mgmt.botservice.types.PrivateLinkResourceBase(TypedDict, total=False):
        key "id": str
        key "name": str
        key "type": str
        id: str
        name: str
        type: str


    class azure.mgmt.botservice.types.PrivateLinkResourceListResult(TypedDict, total=False):
        value: list[PrivateLinkResource]


    class azure.mgmt.botservice.types.PrivateLinkResourceProperties(TypedDict, total=False):
        key "groupId": str
        group_id: str
        requiredMembers: list[str]
        requiredZoneNames: list[str]
        required_members: list[str]
        required_zone_names: list[str]


    class azure.mgmt.botservice.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.botservice.types.Profile(TypedDict, total=False):
        key "accessRulesVersion": int
        key "diagnosticSettingsVersion": int
        key "name": str
        accessRules: list[NspAccessRule]
        access_rules: list[NspAccessRule]
        access_rules_version: int
        diagnostic_settings_version: int
        enabledLogCategories: list[str]
        enabled_log_categories: list[str]
        name: str


    class azure.mgmt.botservice.types.ProvisioningIssue(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('ProvisioningIssueProperties', module='types')
        name: str
        properties: ProvisioningIssueProperties


    class azure.mgmt.botservice.types.ProvisioningIssueProperties(TypedDict, total=False):
        key "description": str
        key "issueType": str
        key "severity": Union[str, Severity]
        description: str
        issue_type: str
        severity: Union[str, Severity]
        suggestedAccessRules: list[NspAccessRule]
        suggestedResourceIds: list[str]
        suggested_access_rules: list[NspAccessRule]
        suggested_resource_ids: list[str]


    class azure.mgmt.botservice.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.botservice.types.QnAMakerEndpointKeysRequestBody(TypedDict, total=False):
        key "authkey": str
        key "hostname": str
        authkey: str
        hostname: str


    class azure.mgmt.botservice.types.QnAMakerEndpointKeysResponse(TypedDict, total=False):
        key "installedVersion": str
        key "lastStableVersion": str
        key "primaryEndpointKey": str
        key "secondaryEndpointKey": str
        installed_version: str
        last_stable_version: str
        primary_endpoint_key: str
        secondary_endpoint_key: str


    class azure.mgmt.botservice.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.botservice.types.ResourceAssociation(TypedDict, total=False):
        key "accessMode": Union[str, AccessMode]
        key "name": str
        access_mode: Union[str, AccessMode]
        name: str


    class azure.mgmt.botservice.types.SearchAssistant(TypedDict, total=False):
        key "channelName": Required[Literal["SearchAssistant"]]
        key "etag": Optional[str]
        key "location": str
        key "provisioningState": str
        channel_name: Literal[SearchAssistant]
        etag: str
        location: str
        provisioning_state: str


    class azure.mgmt.botservice.types.ServiceProvider(TypedDict, total=False):
        key "properties": ForwardRef('ServiceProviderProperties', module='types')
        properties: ServiceProviderProperties


    class azure.mgmt.botservice.types.ServiceProviderParameter(TypedDict, total=False):
        key "default": str
        key "description": str
        key "displayName": str
        key "helpUrl": str
        key "metadata": ForwardRef('ServiceProviderParameterMetadata', module='types')
        key "name": str
        key "type": str
        default: str
        description: str
        display_name: str
        help_url: str
        metadata: ServiceProviderParameterMetadata
        name: str
        type: str


    class azure.mgmt.botservice.types.ServiceProviderParameterMetadata(TypedDict, total=False):
        key "constraints": ForwardRef('ServiceProviderParameterMetadataConstraints', module='types')
        constraints: ServiceProviderParameterMetadataConstraints


    class azure.mgmt.botservice.types.ServiceProviderParameterMetadataConstraints(TypedDict, total=False):
        key "required": bool
        required: bool


    class azure.mgmt.botservice.types.ServiceProviderProperties(TypedDict, total=False):
        key "devPortalUrl": str
        key "displayName": str
        key "iconUrl": str
        key "id": str
        key "serviceProviderName": str
        dev_portal_url: str
        display_name: str
        icon_url: str
        id: str
        parameters: list[ServiceProviderParameter]
        service_provider_name: str


    class azure.mgmt.botservice.types.ServiceProviderResponseList(TypedDict, total=False):
        key "nextLink": str
        next_link: str
        value: list[ServiceProvider]


    class azure.mgmt.botservice.types.Site(TypedDict, total=False):
        key "appId": str
        key "eTag": str
        key "isBlockUserUploadEnabled": Optional[bool]
        key "isDetailedLoggingEnabled": bool
        key "isEnabled": Required[bool]
        key "isEndpointParametersEnabled": bool
        key "isNoStorageEnabled": bool
        key "isSecureSiteEnabled": bool
        key "isTokenEnabled": bool
        key "isV1Enabled": bool
        key "isV3Enabled": bool
        key "isWebChatSpeechEnabled": bool
        key "isWebchatPreviewEnabled": bool
        key "key": str
        key "key2": str
        key "siteId": str
        key "siteName": Required[str]
        key "tenantId": str
        app_id: str
        e_tag: str
        is_block_user_upload_enabled: bool
        is_detailed_logging_enabled: bool
        is_enabled: bool
        is_endpoint_parameters_enabled: bool
        is_no_storage_enabled: bool
        is_secure_site_enabled: bool
        is_token_enabled: bool
        is_v1_enabled: bool
        is_v3_enabled: bool
        is_web_chat_speech_enabled: bool
        is_webchat_preview_enabled: bool
        key: str
        key2: str
        site_id: str
        site_name: str
        tenant_id: str
        trustedOrigins: list[str]
        trusted_origins: list[str]


    class azure.mgmt.botservice.types.SiteInfo(TypedDict, total=False):
        key "key": Required[Union[str, Key]]
        key "siteName": Required[str]
        key: Union[str, Key]
        site_name: str


    class azure.mgmt.botservice.types.Sku(TypedDict, total=False):
        key "name": Required[Union[str, SkuName]]
        key "tier": Union[str, SkuTier]
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]


    class azure.mgmt.botservice.types.SkypeChannel(TypedDict, total=False):
        key "channelName": Required[Literal["SkypeChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('SkypeChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[SkypeChannel]
        etag: str
        location: str
        properties: SkypeChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.SkypeChannelProperties(TypedDict, total=False):
        key "callingWebHook": str
        key "enableCalling": bool
        key "enableGroups": bool
        key "enableMediaCards": bool
        key "enableMessaging": bool
        key "enableScreenSharing": bool
        key "enableVideo": bool
        key "groupsMode": str
        key "incomingCallRoute": str
        key "isEnabled": Required[bool]
        calling_web_hook: str
        enable_calling: bool
        enable_groups: bool
        enable_media_cards: bool
        enable_messaging: bool
        enable_screen_sharing: bool
        enable_video: bool
        groups_mode: str
        incoming_call_route: str
        is_enabled: bool


    class azure.mgmt.botservice.types.SlackChannel(TypedDict, total=False):
        key "channelName": Required[Literal["SlackChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('SlackChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[SlackChannel]
        etag: str
        location: str
        properties: SlackChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.SlackChannelProperties(TypedDict, total=False):
        key "IsValidated": bool
        key "clientId": str
        key "clientSecret": str
        key "isEnabled": Required[bool]
        key "landingPageUrl": str
        key "lastSubmissionId": str
        key "redirectAction": str
        key "registerBeforeOAuthFlow": bool
        key "scopes": str
        key "signingSecret": str
        key "verificationToken": str
        client_id: str
        client_secret: str
        is_enabled: bool
        is_validated: bool
        landing_page_url: str
        last_submission_id: str
        redirect_action: str
        register_before_o_auth_flow: bool
        scopes: str
        signing_secret: str
        verification_token: str


    class azure.mgmt.botservice.types.SmsChannel(TypedDict, total=False):
        key "channelName": Required[Literal["SmsChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('SmsChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[SmsChannel]
        etag: str
        location: str
        properties: SmsChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.SmsChannelProperties(TypedDict, total=False):
        key "accountSID": Required[str]
        key "authToken": str
        key "isEnabled": Required[bool]
        key "isValidated": bool
        key "phone": Required[str]
        account_sid: str
        auth_token: str
        is_enabled: bool
        is_validated: bool
        phone: str


    class azure.mgmt.botservice.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.botservice.types.TelegramChannel(TypedDict, total=False):
        key "channelName": Required[Literal["TelegramChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('TelegramChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[TelegramChannel]
        etag: str
        location: str
        properties: TelegramChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.TelegramChannelProperties(TypedDict, total=False):
        key "accessToken": str
        key "isEnabled": Required[bool]
        key "isValidated": bool
        access_token: str
        is_enabled: bool
        is_validated: bool


    class azure.mgmt.botservice.types.TelephonyChannel(TypedDict, total=False):
        key "channelName": Required[Literal["TelephonyChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('TelephonyChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[TelephonyChannel]
        etag: str
        location: str
        properties: TelephonyChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.TelephonyChannelProperties(TypedDict, total=False):
        key "cognitiveServiceRegion": Optional[str]
        key "cognitiveServiceSubscriptionKey": Optional[str]
        key "defaultLocale": Optional[str]
        key "isEnabled": bool
        key "premiumSKU": Optional[str]
        apiConfigurations: list[TelephonyChannelResourceApiConfiguration]
        api_configurations: list[TelephonyChannelResourceApiConfiguration]
        cognitive_service_region: str
        cognitive_service_subscription_key: str
        default_locale: str
        is_enabled: bool
        phoneNumbers: list[TelephonyPhoneNumbers]
        phone_numbers: list[TelephonyPhoneNumbers]
        premium_sku: str


    class azure.mgmt.botservice.types.TelephonyChannelResourceApiConfiguration(TypedDict, total=False):
        key "cognitiveServiceRegion": Optional[str]
        key "cognitiveServiceResourceId": Optional[str]
        key "cognitiveServiceSubscriptionKey": Optional[str]
        key "defaultLocale": Optional[str]
        key "id": str
        key "providerName": Optional[str]
        cognitive_service_region: str
        cognitive_service_resource_id: str
        cognitive_service_subscription_key: str
        default_locale: str
        id: str
        provider_name: str


    class azure.mgmt.botservice.types.TelephonyPhoneNumbers(TypedDict, total=False):
        key "acsEndpoint": Optional[str]
        key "acsResourceId": Optional[str]
        key "acsSecret": Optional[str]
        key "cognitiveServiceRegion": Optional[str]
        key "cognitiveServiceResourceId": Optional[str]
        key "cognitiveServiceSubscriptionKey": Optional[str]
        key "defaultLocale": Optional[str]
        key "id": str
        key "offerType": Optional[str]
        key "phoneNumber": str
        acs_endpoint: str
        acs_resource_id: str
        acs_secret: str
        cognitive_service_region: str
        cognitive_service_resource_id: str
        cognitive_service_subscription_key: str
        default_locale: str
        id: str
        offer_type: str
        phone_number: str


    class azure.mgmt.botservice.types.WebChatChannel(TypedDict, total=False):
        key "channelName": Required[Literal["WebChatChannel"]]
        key "etag": Optional[str]
        key "location": str
        key "properties": ForwardRef('WebChatChannelProperties', module='types')
        key "provisioningState": str
        channel_name: Literal[WebChatChannel]
        etag: str
        location: str
        properties: WebChatChannelProperties
        provisioning_state: str


    class azure.mgmt.botservice.types.WebChatChannelProperties(TypedDict, total=False):
        key "webChatEmbedCode": str
        sites: list[WebChatSite]
        web_chat_embed_code: str


    class azure.mgmt.botservice.types.WebChatSite(Site):
        key "appId": str
        key "eTag": str
        key "isBlockUserUploadEnabled": Optional[bool]
        key "isDetailedLoggingEnabled": bool
        key "isEnabled": Required[bool]
        key "isEndpointParametersEnabled": bool
        key "isNoStorageEnabled": bool
        key "isSecureSiteEnabled": bool
        key "isTokenEnabled": bool
        key "isV1Enabled": bool
        key "isV3Enabled": bool
        key "isWebChatSpeechEnabled": bool
        key "isWebchatPreviewEnabled": bool
        key "key": str
        key "key2": str
        key "siteId": str
        key "siteName": Required[str]
        key "tenantId": str
        app_id: str
        e_tag: str
        is_block_user_upload_enabled: bool
        is_detailed_logging_enabled: bool
        is_enabled: bool
        is_endpoint_parameters_enabled: bool
        is_no_storage_enabled: bool
        is_secure_site_enabled: bool
        is_token_enabled: bool
        is_v1_enabled: bool
        is_v3_enabled: bool
        is_web_chat_speech_enabled: bool
        is_webchat_preview_enabled: bool
        key: str
        key2: str
        site_id: str
        site_name: str
        tenant_id: str
        trustedOrigins: list[str]
        trusted_origins: list[str]


```