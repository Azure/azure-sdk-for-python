```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.botservice

    class azure.mgmt.botservice.AzureBotService: implements ContextManager 
        bot_connection: BotConnectionOperations
        bots: BotsOperations
        channels: ChannelsOperations
        direct_line: DirectLineOperations
        email: EmailOperations
        host_settings: HostSettingsOperations
        operation_results: OperationResultsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        qn_amaker_endpoint_keys: QnAMakerEndpointKeysOperations

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


namespace azure.mgmt.botservice.aio

    class azure.mgmt.botservice.aio.AzureBotService: implements AsyncContextManager 
        bot_connection: BotConnectionOperations
        bots: BotsOperations
        channels: ChannelsOperations
        direct_line: DirectLineOperations
        email: EmailOperations
        host_settings: HostSettingsOperations
        operation_results: OperationResultsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        qn_amaker_endpoint_keys: QnAMakerEndpointKeysOperations

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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @distributed_trace
        def list_by_bot_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConnectionSetting]: ...

        @distributed_trace_async
        async def list_service_providers(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServiceProviderResponseList: ...

        @distributed_trace_async
        async def list_with_secrets(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseBody: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Bot]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Bot]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                location: Optional[str] = None, 
                tags: Optional[Dict[str, str]] = None, 
                sku: Optional[Sku] = None, 
                kind: Optional[Union[str, Kind]] = None, 
                etag: Optional[str] = None, 
                properties: Optional[BotProperties] = None, 
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BotChannel: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[BotChannel]: ...

        @distributed_trace_async
        async def list_with_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ListChannelWithKeysResponse: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                location: Optional[str] = None, 
                tags: Optional[Dict[str, str]] = None, 
                sku: Optional[Sku] = None, 
                kind: Optional[Union[str, Kind]] = None, 
                etag: Optional[str] = None, 
                properties: Optional[Channel] = None, 
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CreateEmailSignInUrlResponse: ...


    class azure.mgmt.botservice.aio.operations.HostSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> HostSettingsResponse: ...


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
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResultsDescription]: ...


    class azure.mgmt.botservice.aio.operations.Operations:

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
            ) -> AsyncIterable[OperationEntity]: ...


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
                properties: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PrivateEndpointConnection]: ...


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
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QnAMakerEndpointKeysResponse: ...


namespace azure.mgmt.botservice.models

    class azure.mgmt.botservice.models.AcsChatChannel(Channel):
        channel_name: str
        etag: str
        location: str
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
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


    class azure.mgmt.botservice.models.AlexaChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: AlexaChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[AlexaChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.AlexaChannelProperties(Model):
        alexa_skill_id: str
        is_enabled: bool
        service_endpoint_uri: str
        url_fragment: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alexa_skill_id: str, 
                is_enabled: bool, 
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


    class azure.mgmt.botservice.models.Bot(Resource):
        etag: str
        id: str
        kind: Union[str, Kind]
        location: str
        name: str
        properties: BotProperties
        sku: Sku
        tags: dict[str, str]
        type: str
        zones: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[BotProperties] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.botservice.models.BotChannel(Resource):
        etag: str
        id: str
        kind: Union[str, Kind]
        location: str
        name: str
        properties: Channel
        sku: Sku
        tags: dict[str, str]
        type: str
        zones: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[Channel] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.botservice.models.BotProperties(Model):
        all_settings: dict[str, str]
        app_password_hint: str
        cmek_encryption_status: str
        cmek_key_vault_url: str
        configured_channels: list[str]
        description: str
        developer_app_insight_key: str
        developer_app_insights_api_key: str
        developer_app_insights_application_id: str
        disable_local_auth: bool
        display_name: str
        enabled_channels: list[str]
        endpoint: str
        endpoint_version: str
        icon_url: str
        is_cmek_enabled: bool
        is_developer_app_insights_api_key_set: bool
        is_streaming_supported: bool
        luis_app_ids: list[str]
        luis_key: str
        manifest_url: str
        migration_token: str
        msa_app_id: str
        msa_app_msi_resource_id: str
        msa_app_tenant_id: str
        msa_app_type: Union[str, MsaAppType]
        open_with_hint: str
        parameters: dict[str, str]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        public_network_access: Union[str, PublicNetworkAccess]
        publishing_credentials: str
        schema_transformation_version: str
        storage_resource_id: str
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                all_settings: Optional[Dict[str, str]] = ..., 
                app_password_hint: Optional[str] = ..., 
                cmek_key_vault_url: Optional[str] = ..., 
                description: Optional[str] = ..., 
                developer_app_insight_key: Optional[str] = ..., 
                developer_app_insights_api_key: Optional[str] = ..., 
                developer_app_insights_application_id: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                display_name: str, 
                endpoint: str, 
                icon_url: str = "", 
                is_cmek_enabled: bool = False, 
                is_streaming_supported: bool = False, 
                luis_app_ids: Optional[List[str]] = ..., 
                luis_key: Optional[str] = ..., 
                manifest_url: Optional[str] = ..., 
                msa_app_id: str, 
                msa_app_msi_resource_id: Optional[str] = ..., 
                msa_app_tenant_id: Optional[str] = ..., 
                msa_app_type: Optional[Union[str, MsaAppType]] = ..., 
                open_with_hint: Optional[str] = ..., 
                parameters: Optional[Dict[str, str]] = ..., 
                public_network_access: Union[str, PublicNetworkAccess] = "Enabled", 
                publishing_credentials: Optional[str] = ..., 
                schema_transformation_version: Optional[str] = ..., 
                storage_resource_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.BotResponseList(Model):
        next_link: str
        value: list[Bot]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.botservice.models.Channel(Model):
        channel_name: str
        etag: str
        location: str
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
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


    class azure.mgmt.botservice.models.ChannelResponseList(Model):
        next_link: str
        value: list[BotChannel]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.botservice.models.ChannelSettings(Model):
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

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                bot_icon_url: Optional[str] = ..., 
                bot_id: Optional[str] = ..., 
                channel_display_name: Optional[str] = ..., 
                channel_id: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                extension_key1: str = "", 
                extension_key2: str = "", 
                is_enabled: Optional[bool] = ..., 
                require_terms_agreement: Optional[bool] = ..., 
                sites: Optional[List[Site]] = ..., 
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


    class azure.mgmt.botservice.models.CheckNameAvailabilityRequestBody(Model):
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.CheckNameAvailabilityResponseBody(Model):
        abs_code: str
        message: str
        valid: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                abs_code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                valid: Optional[bool] = ..., 
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


    class azure.mgmt.botservice.models.ConnectionItemName(Model):
        name: str

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


    class azure.mgmt.botservice.models.ConnectionSetting(Resource):
        etag: str
        id: str
        kind: Union[str, Kind]
        location: str
        name: str
        properties: ConnectionSettingProperties
        sku: Sku
        tags: dict[str, str]
        type: str
        zones: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ConnectionSettingProperties] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.botservice.models.ConnectionSettingParameter(Model):
        key: str
        value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.ConnectionSettingProperties(Model):
        client_id: str
        client_secret: str
        parameters: list[ConnectionSettingParameter]
        provisioning_state: str
        scopes: str
        service_provider_display_name: str
        service_provider_id: str
        setting_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                parameters: Optional[List[ConnectionSettingParameter]] = ..., 
                provisioning_state: Optional[str] = ..., 
                scopes: str = "", 
                service_provider_display_name: Optional[str] = ..., 
                service_provider_id: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.ConnectionSettingResponseList(Model):
        next_link: str
        value: list[ConnectionSetting]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.botservice.models.CreateEmailSignInUrlResponse(Model):
        id: str
        location: str
        properties: CreateEmailSignInUrlResponseProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[CreateEmailSignInUrlResponseProperties] = ..., 
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


    class azure.mgmt.botservice.models.CreateEmailSignInUrlResponseProperties(Model):
        url: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                url: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.DirectLineChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: DirectLineChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[DirectLineChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.DirectLineChannelProperties(Model):
        direct_line_embed_code: str
        extension_key1: str
        extension_key2: str
        sites: list[DirectLineSite]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                direct_line_embed_code: Optional[str] = ..., 
                extension_key1: str = "", 
                extension_key2: str = "", 
                sites: Optional[List[DirectLineSite]] = ..., 
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


    class azure.mgmt.botservice.models.DirectLineSite(Model):
        is_block_user_upload_enabled: bool
        is_enabled: bool
        is_secure_site_enabled: bool
        is_v1_enabled: bool
        is_v3_enabled: bool
        key: str
        key2: str
        site_id: str
        site_name: str
        trusted_origins: list[str]

        def __init__(
                self, 
                *, 
                is_block_user_upload_enabled: Optional[bool] = ..., 
                is_enabled: bool, 
                is_secure_site_enabled: Optional[bool] = ..., 
                is_v1_enabled: bool, 
                is_v3_enabled: bool, 
                site_name: str, 
                trusted_origins: Optional[List[str]] = ..., 
                **kwargs
            ): ...


    class azure.mgmt.botservice.models.DirectLineSpeechChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: DirectLineSpeechChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[DirectLineSpeechChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.DirectLineSpeechChannelProperties(Model):
        cognitive_service_region: str
        cognitive_service_resource_id: str
        cognitive_service_subscription_key: str
        custom_speech_model_id: str
        custom_voice_deployment_id: str
        is_default_bot_for_cog_svc_account: bool
        is_enabled: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                cognitive_service_region: Optional[str] = ..., 
                cognitive_service_resource_id: Optional[str] = ..., 
                cognitive_service_subscription_key: Optional[str] = ..., 
                custom_speech_model_id: Optional[str] = ..., 
                custom_voice_deployment_id: Optional[str] = ..., 
                is_default_bot_for_cog_svc_account: Optional[bool] = ..., 
                is_enabled: Optional[bool] = ..., 
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


    class azure.mgmt.botservice.models.EmailChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: EmailChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[EmailChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.EmailChannelAuthMethod(float, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRAPH = 1.0
        PASSWORD = 0.0


    class azure.mgmt.botservice.models.EmailChannelProperties(Model):
        auth_method: Union[float, EmailChannelAuthMethod]
        email_address: str
        is_enabled: bool
        magic_code: str
        password: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                auth_method: Optional[Union[float, EmailChannelAuthMethod]] = ..., 
                email_address: str, 
                is_enabled: bool, 
                magic_code: Optional[str] = ..., 
                password: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.Error(Model):
        error: ErrorBody

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorBody] = ..., 
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


    class azure.mgmt.botservice.models.ErrorBody(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: str, 
                message: str, 
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


    class azure.mgmt.botservice.models.FacebookChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: FacebookChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[FacebookChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.FacebookChannelProperties(Model):
        app_id: str
        app_secret: str
        callback_url: str
        is_enabled: bool
        pages: list[FacebookPage]
        verify_token: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                app_id: str, 
                app_secret: Optional[str] = ..., 
                is_enabled: bool, 
                pages: Optional[List[FacebookPage]] = ..., 
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


    class azure.mgmt.botservice.models.FacebookPage(Model):
        access_token: str
        id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                access_token: Optional[str] = ..., 
                id: str, 
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


    class azure.mgmt.botservice.models.HostSettingsResponse(Model):
        bot_open_id_metadata: str
        o_auth_url: str
        to_bot_from_channel_open_id_metadata_url: str
        to_bot_from_channel_token_issuer: str
        to_bot_from_emulator_open_id_metadata_url: str
        to_channel_from_bot_login_url: str
        to_channel_from_bot_o_auth_scope: str
        validate_authority: bool

        def __eq__(self, other): ...

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
                validate_authority: Optional[bool] = ..., 
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


    class azure.mgmt.botservice.models.Key(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY1 = "key1"
        KEY2 = "key2"


    class azure.mgmt.botservice.models.KikChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: KikChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[KikChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.KikChannelProperties(Model):
        api_key: str
        is_enabled: bool
        is_validated: bool
        user_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                is_enabled: bool, 
                is_validated: Optional[bool] = ..., 
                user_name: str, 
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


    class azure.mgmt.botservice.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZUREBOT = "azurebot"
        BOT = "bot"
        DESIGNER = "designer"
        FUNCTION = "function"
        SDK = "sdk"


    class azure.mgmt.botservice.models.LineChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: LineChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[LineChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.LineChannelProperties(Model):
        callback_url: str
        is_validated: bool
        line_registrations: list[LineRegistration]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                line_registrations: List[LineRegistration], 
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


    class azure.mgmt.botservice.models.LineRegistration(Model):
        channel_access_token: str
        channel_secret: str
        generated_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                channel_access_token: Optional[str] = ..., 
                channel_secret: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.ListChannelWithKeysResponse(BotChannel):
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
        tags: dict[str, str]
        type: str
        zones: list[str]

        def __eq__(self, other): ...

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


    class azure.mgmt.botservice.models.M365Extensions(Channel):
        channel_name: str
        etag: str
        location: str
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
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


    class azure.mgmt.botservice.models.MsTeamsChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: MsTeamsChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[MsTeamsChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.MsTeamsChannelProperties(Model):
        accepted_terms: bool
        calling_webhook: str
        deployment_environment: str
        enable_calling: bool
        incoming_call_route: str
        is_enabled: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                accepted_terms: Optional[bool] = ..., 
                calling_webhook: Optional[str] = ..., 
                deployment_environment: str = "FallbackDeploymentEnvironment", 
                enable_calling: bool = False, 
                incoming_call_route: Optional[str] = ..., 
                is_enabled: bool, 
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


    class azure.mgmt.botservice.models.MsaAppType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTI_TENANT = "MultiTenant"
        SINGLE_TENANT = "SingleTenant"
        USER_ASSIGNED_MSI = "UserAssignedMSI"


    class azure.mgmt.botservice.models.Omnichannel(Channel):
        channel_name: str
        etag: str
        location: str
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
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


    class azure.mgmt.botservice.models.OperationDisplayInfo(Model):
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


    class azure.mgmt.botservice.models.OperationEntity(Model):
        display: OperationDisplayInfo
        name: str
        origin: str
        properties: JSON

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplayInfo] = ..., 
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


    class azure.mgmt.botservice.models.OperationEntityListResult(Model):
        next_link: str
        value: list[OperationEntity]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[OperationEntity]] = ..., 
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


    class azure.mgmt.botservice.models.OperationResultStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        REQUESTED = "Requested"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.botservice.models.OperationResultsDescription(Model):
        id: str
        name: str
        start_time: datetime
        status: Union[str, OperationResultStatus]

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


    class azure.mgmt.botservice.models.OutlookChannel(Channel):
        channel_name: str
        etag: str
        location: str
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
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


    class azure.mgmt.botservice.models.PrivateEndpoint(Model):
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


    class azure.mgmt.botservice.models.PrivateEndpointConnection(PrivateLinkResourceBase):
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


    class azure.mgmt.botservice.models.PrivateEndpointConnectionListResult(Model):
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


    class azure.mgmt.botservice.models.PrivateLinkResourceBase(Model):
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


    class azure.mgmt.botservice.models.PrivateLinkResourceListResult(Model):
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


    class azure.mgmt.botservice.models.PrivateLinkServiceConnectionState(Model):
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


    class azure.mgmt.botservice.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.botservice.models.QnAMakerEndpointKeysRequestBody(Model):
        authkey: str
        hostname: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                authkey: Optional[str] = ..., 
                hostname: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.QnAMakerEndpointKeysResponse(Model):
        installed_version: str
        last_stable_version: str
        primary_endpoint_key: str
        secondary_endpoint_key: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                installed_version: Optional[str] = ..., 
                last_stable_version: Optional[str] = ..., 
                primary_endpoint_key: Optional[str] = ..., 
                secondary_endpoint_key: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.RegenerateKeysChannelName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT_LINE_CHANNEL = "DirectLineChannel"
        WEB_CHAT_CHANNEL = "WebChatChannel"


    class azure.mgmt.botservice.models.Resource(Model):
        etag: str
        id: str
        kind: Union[str, Kind]
        location: str
        name: str
        sku: Sku
        tags: dict[str, str]
        type: str
        zones: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                location: Optional[str] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.botservice.models.SearchAssistant(Channel):
        channel_name: str
        etag: str
        location: str
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
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


    class azure.mgmt.botservice.models.ServiceProvider(Model):
        properties: ServiceProviderProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[ServiceProviderProperties] = ..., 
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


    class azure.mgmt.botservice.models.ServiceProviderParameter(Model):
        default: str
        description: str
        display_name: str
        help_url: str
        metadata: ServiceProviderParameterMetadata
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


    class azure.mgmt.botservice.models.ServiceProviderParameterMetadata(Model):
        constraints: ServiceProviderParameterMetadataConstraints

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                constraints: Optional[ServiceProviderParameterMetadataConstraints] = ..., 
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


    class azure.mgmt.botservice.models.ServiceProviderParameterMetadataConstraints(Model):
        required: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                required: Optional[bool] = ..., 
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


    class azure.mgmt.botservice.models.ServiceProviderProperties(Model):
        dev_portal_url: str
        display_name: str
        icon_url: str
        id: str
        parameters: list[ServiceProviderParameter]
        service_provider_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                icon_url: str = "", 
                parameters: Optional[List[ServiceProviderParameter]] = ..., 
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


    class azure.mgmt.botservice.models.ServiceProviderResponseList(Model):
        next_link: str
        value: list[ServiceProvider]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.botservice.models.Site(WebChatSite, DirectLineSite):
        e_tag: str
        is_block_user_upload_enabled: bool
        is_enabled: bool
        is_secure_site_enabled: bool
        is_token_enabled: bool
        is_v1_enabled: bool
        is_v3_enabled: bool
        is_webchat_preview_enabled: bool
        key: str
        key2: str
        site_id: str
        site_name: str
        trusted_origins: list[str]

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                is_block_user_upload_enabled: Optional[bool] = ..., 
                is_enabled: bool, 
                is_secure_site_enabled: Optional[bool] = ..., 
                is_token_enabled: Optional[bool] = ..., 
                is_v1_enabled: bool, 
                is_v3_enabled: bool, 
                is_webchat_preview_enabled: bool, 
                site_name: str, 
                trusted_origins: Optional[List[str]] = ..., 
                **kwargs
            ): ...


    class azure.mgmt.botservice.models.SiteInfo(Model):
        key: Union[str, Key]
        site_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                key: Union[str, Key], 
                site_name: str, 
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


    class azure.mgmt.botservice.models.Sku(Model):
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.botservice.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        F0 = "F0"
        S1 = "S1"


    class azure.mgmt.botservice.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREE = "Free"
        STANDARD = "Standard"


    class azure.mgmt.botservice.models.SkypeChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: SkypeChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[SkypeChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.SkypeChannelProperties(Model):
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

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                calling_web_hook: Optional[str] = ..., 
                enable_calling: bool = False, 
                enable_groups: Optional[bool] = ..., 
                enable_media_cards: Optional[bool] = ..., 
                enable_messaging: Optional[bool] = ..., 
                enable_screen_sharing: Optional[bool] = ..., 
                enable_video: Optional[bool] = ..., 
                groups_mode: Optional[str] = ..., 
                incoming_call_route: Optional[str] = ..., 
                is_enabled: bool, 
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


    class azure.mgmt.botservice.models.SlackChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: SlackChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[SlackChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.SlackChannelProperties(Model):
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

        def __eq__(self, other): ...

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
                verification_token: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.SmsChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: SmsChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[SmsChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.SmsChannelProperties(Model):
        account_sid: str
        auth_token: str
        is_enabled: bool
        is_validated: bool
        phone: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                account_sid: str, 
                auth_token: Optional[str] = ..., 
                is_enabled: bool, 
                is_validated: Optional[bool] = ..., 
                phone: str, 
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


    class azure.mgmt.botservice.models.TelegramChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: TelegramChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[TelegramChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.TelegramChannelProperties(Model):
        access_token: str
        is_enabled: bool
        is_validated: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                access_token: Optional[str] = ..., 
                is_enabled: bool, 
                is_validated: Optional[bool] = ..., 
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


    class azure.mgmt.botservice.models.TelephonyChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: TelephonyChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[TelephonyChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.TelephonyChannelProperties(Model):
        api_configurations: list[TelephonyChannelResourceApiConfiguration]
        cognitive_service_region: str
        cognitive_service_subscription_key: str
        default_locale: str
        is_enabled: bool
        phone_numbers: list[TelephonyPhoneNumbers]
        premium_sku: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                api_configurations: Optional[List[TelephonyChannelResourceApiConfiguration]] = ..., 
                cognitive_service_region: Optional[str] = ..., 
                cognitive_service_subscription_key: Optional[str] = ..., 
                default_locale: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                phone_numbers: Optional[List[TelephonyPhoneNumbers]] = ..., 
                premium_sku: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.TelephonyChannelResourceApiConfiguration(Model):
        cognitive_service_region: str
        cognitive_service_resource_id: str
        cognitive_service_subscription_key: str
        default_locale: str
        id: str
        provider_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                cognitive_service_region: Optional[str] = ..., 
                cognitive_service_resource_id: Optional[str] = ..., 
                cognitive_service_subscription_key: Optional[str] = ..., 
                default_locale: Optional[str] = ..., 
                id: Optional[str] = ..., 
                provider_name: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.TelephonyPhoneNumbers(Model):
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

        def __eq__(self, other): ...

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
                phone_number: Optional[str] = ..., 
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


    class azure.mgmt.botservice.models.WebChatChannel(Channel):
        channel_name: str
        etag: str
        location: str
        properties: WebChatChannelProperties
        provisioning_state: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str = "global", 
                properties: Optional[WebChatChannelProperties] = ..., 
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


    class azure.mgmt.botservice.models.WebChatChannelProperties(Model):
        sites: list[WebChatSite]
        web_chat_embed_code: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                sites: Optional[List[WebChatSite]] = ..., 
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


    class azure.mgmt.botservice.models.WebChatSite(Model):
        is_enabled: bool
        is_webchat_preview_enabled: bool
        key: str
        key2: str
        site_id: str
        site_name: str

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                is_webchat_preview_enabled: bool, 
                site_name: str, 
                **kwargs
            ): ...


namespace azure.mgmt.botservice.operations

    class azure.mgmt.botservice.operations.BotConnectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConnectionSetting: ...

        @distributed_trace
        def list_by_bot_service(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConnectionSetting]: ...

        @distributed_trace
        def list_service_providers(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServiceProviderResponseList: ...

        @distributed_trace
        def list_with_secrets(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionSetting: ...


    class azure.mgmt.botservice.operations.BotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bot: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseBody: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Bot]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Bot]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                location: Optional[str] = None, 
                tags: Optional[Dict[str, str]] = None, 
                sku: Optional[Sku] = None, 
                kind: Optional[Union[str, Kind]] = None, 
                etag: Optional[str] = None, 
                properties: Optional[BotProperties] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Bot: ...


    class azure.mgmt.botservice.operations.ChannelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BotChannel: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[BotChannel]: ...

        @distributed_trace
        def list_with_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ListChannelWithKeysResponse: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                channel_name: Union[str, ChannelName], 
                location: Optional[str] = None, 
                tags: Optional[Dict[str, str]] = None, 
                sku: Optional[Sku] = None, 
                kind: Optional[Union[str, Kind]] = None, 
                etag: Optional[str] = None, 
                properties: Optional[Channel] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BotChannel: ...


    class azure.mgmt.botservice.operations.DirectLineOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BotChannel: ...


    class azure.mgmt.botservice.operations.EmailOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def create_sign_in_url(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CreateEmailSignInUrlResponse: ...


    class azure.mgmt.botservice.operations.HostSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> HostSettingsResponse: ...


    class azure.mgmt.botservice.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_get(
                self, 
                operation_result_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationResultsDescription]: ...


    class azure.mgmt.botservice.operations.Operations:

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
            ) -> Iterable[OperationEntity]: ...


    class azure.mgmt.botservice.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                properties: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PrivateEndpointConnection]: ...


    class azure.mgmt.botservice.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_bot_resource(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.botservice.operations.QnAMakerEndpointKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QnAMakerEndpointKeysResponse: ...


```