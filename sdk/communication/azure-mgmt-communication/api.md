```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.communication

    class azure.mgmt.communication.CommunicationServiceManagementClient: implements ContextManager 
        communication_services: CommunicationServicesOperations
        domains: DomainsOperations
        email_services: EmailServicesOperations
        operations: Operations
        sender_usernames: SenderUsernamesOperations
        smtp_usernames: SmtpUsernamesOperations
        suppression_list_addresses: SuppressionListAddressesOperations
        suppression_lists: SuppressionListsOperations

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


namespace azure.mgmt.communication.aio

    class azure.mgmt.communication.aio.CommunicationServiceManagementClient: implements AsyncContextManager 
        communication_services: CommunicationServicesOperations
        domains: DomainsOperations
        email_services: EmailServicesOperations
        operations: Operations
        sender_usernames: SenderUsernamesOperations
        smtp_usernames: SmtpUsernamesOperations
        suppression_list_addresses: SuppressionListAddressesOperations
        suppression_lists: SuppressionListsOperations

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


namespace azure.mgmt.communication.aio.operations

    class azure.mgmt.communication.aio.operations.CommunicationServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: CommunicationServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunicationServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunicationServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommunicationServiceResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def check_name_availability(
                self, 
                name_availability_parameters: NameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                name_availability_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                name_availability_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                **kwargs: Any
            ) -> CommunicationServiceResource: ...

        @overload
        async def link_notification_hub(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                link_notification_hub_parameters: Optional[LinkNotificationHubParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LinkedNotificationHub: ...

        @overload
        async def link_notification_hub(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                link_notification_hub_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LinkedNotificationHub: ...

        @overload
        async def link_notification_hub(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                link_notification_hub_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LinkedNotificationHub: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CommunicationServiceResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[CommunicationServiceResource]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                **kwargs: Any
            ) -> CommunicationServiceKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationServiceKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationServiceKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationServiceKeys: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: CommunicationServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationServiceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationServiceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationServiceResource: ...


    class azure.mgmt.communication.aio.operations.DomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_cancel_verification(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: VerificationParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_cancel_verification(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_cancel_verification(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: DomainResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_initiate_verification(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: VerificationParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_initiate_verification(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_initiate_verification(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: UpdateDomainRequestParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> DomainResource: ...

        @distributed_trace
        def list_by_email_service_resource(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DomainResource]: ...


    class azure.mgmt.communication.aio.operations.EmailServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                parameters: EmailServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EmailServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EmailServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EmailServiceResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                parameters: EmailServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EmailServiceResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EmailServiceResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EmailServiceResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                **kwargs: Any
            ) -> EmailServiceResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EmailServiceResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[EmailServiceResource]: ...

        @distributed_trace_async
        async def list_verified_exchange_online_domains(self, **kwargs: Any) -> List[str]: ...


    class azure.mgmt.communication.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.communication.aio.operations.SenderUsernamesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                sender_username: str, 
                parameters: SenderUsernameResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SenderUsernameResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                sender_username: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SenderUsernameResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                sender_username: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SenderUsernameResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                sender_username: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                sender_username: str, 
                **kwargs: Any
            ) -> SenderUsernameResource: ...

        @distributed_trace
        def list_by_domains(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SenderUsernameResource]: ...


    class azure.mgmt.communication.aio.operations.SmtpUsernamesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                smtp_username: str, 
                parameters: SmtpUsernameResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SmtpUsernameResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                smtp_username: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SmtpUsernameResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                smtp_username: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SmtpUsernameResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                smtp_username: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                smtp_username: str, 
                **kwargs: Any
            ) -> SmtpUsernameResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SmtpUsernameResource]: ...


    class azure.mgmt.communication.aio.operations.SuppressionListAddressesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                address_id: str, 
                parameters: SuppressionListAddressResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionListAddressResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                address_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionListAddressResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                address_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionListAddressResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                address_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                address_id: str, 
                **kwargs: Any
            ) -> SuppressionListAddressResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SuppressionListAddressResource]: ...


    class azure.mgmt.communication.aio.operations.SuppressionListsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                parameters: SuppressionListResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionListResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionListResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionListResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                **kwargs: Any
            ) -> SuppressionListResource: ...

        @distributed_trace
        def list_by_domain(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SuppressionListResource]: ...


namespace azure.mgmt.communication.models

    class azure.mgmt.communication.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.communication.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.communication.models.CheckNameAvailabilityRequest(_Model):
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


    class azure.mgmt.communication.models.CheckNameAvailabilityResponse(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, CheckNameAvailabilityReason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, CheckNameAvailabilityReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.CommunicationServiceKeys(_Model):
        primary_connection_string: Optional[str]
        primary_key: Optional[str]
        secondary_connection_string: Optional[str]
        secondary_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_connection_string: Optional[str] = ..., 
                primary_key: Optional[str] = ..., 
                secondary_connection_string: Optional[str] = ..., 
                secondary_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.CommunicationServiceProperties(_Model):
        data_location: str
        disable_local_auth: Optional[bool]
        host_name: Optional[str]
        immutable_resource_id: Optional[str]
        linked_domains: Optional[list[str]]
        notification_hub_id: Optional[str]
        provisioning_state: Optional[Union[str, CommunicationServicesProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_location: str, 
                disable_local_auth: Optional[bool] = ..., 
                linked_domains: Optional[list[str]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.CommunicationServiceResource(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[CommunicationServiceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[CommunicationServiceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.communication.models.CommunicationServiceResourceUpdate(TaggedResource):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[CommunicationServiceUpdateProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[CommunicationServiceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.communication.models.CommunicationServiceUpdateProperties(_Model):
        disable_local_auth: Optional[bool]
        linked_domains: Optional[list[str]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                disable_local_auth: Optional[bool] = ..., 
                linked_domains: Optional[list[str]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.CommunicationServicesProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.communication.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.communication.models.DnsRecord(_Model):
        name: Optional[str]
        ttl: Optional[int]
        type: Optional[str]
        value: Optional[str]


    class azure.mgmt.communication.models.DomainManagement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_MANAGED = "AzureManaged"
        CUSTOMER_MANAGED = "CustomerManaged"
        CUSTOMER_MANAGED_IN_EXCHANGE_ONLINE = "CustomerManagedInExchangeOnline"


    class azure.mgmt.communication.models.DomainProperties(_Model):
        data_location: Optional[str]
        domain_management: Union[str, DomainManagement]
        from_sender_domain: Optional[str]
        mail_from_sender_domain: Optional[str]
        provisioning_state: Optional[Union[str, DomainsProvisioningState]]
        user_engagement_tracking: Optional[Union[str, UserEngagementTracking]]
        verification_records: Optional[DomainPropertiesVerificationRecords]
        verification_states: Optional[DomainPropertiesVerificationStates]

        @overload
        def __init__(
                self, 
                *, 
                domain_management: Union[str, DomainManagement], 
                user_engagement_tracking: Optional[Union[str, UserEngagementTracking]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.DomainPropertiesVerificationRecords(_Model):
        dkim: Optional[DnsRecord]
        dkim2: Optional[DnsRecord]
        dmarc: Optional[DnsRecord]
        domain: Optional[DnsRecord]
        spf: Optional[DnsRecord]

        @overload
        def __init__(
                self, 
                *, 
                dkim: Optional[DnsRecord] = ..., 
                dkim2: Optional[DnsRecord] = ..., 
                dmarc: Optional[DnsRecord] = ..., 
                domain: Optional[DnsRecord] = ..., 
                spf: Optional[DnsRecord] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.DomainPropertiesVerificationStates(_Model):
        dkim: Optional[VerificationStatusRecord]
        dkim2: Optional[VerificationStatusRecord]
        dmarc: Optional[VerificationStatusRecord]
        domain: Optional[VerificationStatusRecord]
        spf: Optional[VerificationStatusRecord]

        @overload
        def __init__(
                self, 
                *, 
                dkim: Optional[VerificationStatusRecord] = ..., 
                dkim2: Optional[VerificationStatusRecord] = ..., 
                dmarc: Optional[VerificationStatusRecord] = ..., 
                domain: Optional[VerificationStatusRecord] = ..., 
                spf: Optional[VerificationStatusRecord] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.DomainResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[DomainProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[DomainProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.communication.models.DomainsProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.communication.models.EmailServiceProperties(_Model):
        data_location: str
        provisioning_state: Optional[Union[str, EmailServicesProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                data_location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.EmailServiceResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[EmailServiceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[EmailServiceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.communication.models.EmailServiceResourceUpdate(TaggedResource):
        tags: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.EmailServicesProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.communication.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.communication.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.communication.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.communication.models.LinkNotificationHubParameters(_Model):
        connection_string: str
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                connection_string: str, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.LinkedNotificationHub(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.communication.models.NameAvailabilityParameters(CheckNameAvailabilityRequest):
        name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.communication.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.communication.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.communication.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.communication.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.communication.models.RegenerateKeyParameters(_Model):
        key_type: Optional[Union[str, KeyType]]

        @overload
        def __init__(
                self, 
                *, 
                key_type: Optional[Union[str, KeyType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.communication.models.SenderUsernameProperties(_Model):
        data_location: Optional[str]
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        username: str

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                username: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.SenderUsernameResource(ProxyResource):
        id: str
        name: str
        properties: Optional[SenderUsernameProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SenderUsernameProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.communication.models.SmtpUsernameProperties(_Model):
        entra_application_id: str
        tenant_id: str
        username: str

        @overload
        def __init__(
                self, 
                *, 
                entra_application_id: str, 
                tenant_id: str, 
                username: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.SmtpUsernameResource(ProxyResource):
        id: str
        name: str
        properties: Optional[SmtpUsernameProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SmtpUsernameProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.communication.models.SuppressionListAddressProperties(_Model):
        data_location: Optional[str]
        email: str
        first_name: Optional[str]
        last_modified: Optional[datetime]
        last_name: Optional[str]
        notes: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                email: str, 
                first_name: Optional[str] = ..., 
                last_name: Optional[str] = ..., 
                notes: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.SuppressionListAddressResource(ProxyResource):
        id: str
        name: str
        properties: Optional[SuppressionListAddressProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SuppressionListAddressProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.communication.models.SuppressionListProperties(_Model):
        created_time_stamp: Optional[str]
        data_location: Optional[str]
        last_updated_time_stamp: Optional[str]
        list_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                list_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.SuppressionListResource(ProxyResource):
        id: str
        name: str
        properties: Optional[SuppressionListProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SuppressionListProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.communication.models.SystemData(_Model):
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


    class azure.mgmt.communication.models.TaggedResource(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.TrackedResource(Resource):
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


    class azure.mgmt.communication.models.UpdateDomainProperties(_Model):
        user_engagement_tracking: Optional[Union[str, UserEngagementTracking]]

        @overload
        def __init__(
                self, 
                *, 
                user_engagement_tracking: Optional[Union[str, UserEngagementTracking]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.UpdateDomainRequestParameters(TaggedResource):
        properties: Optional[UpdateDomainProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateDomainProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.communication.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.communication.models.UserEngagementTracking(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.communication.models.VerificationParameter(_Model):
        verification_type: Union[str, VerificationType]

        @overload
        def __init__(
                self, 
                *, 
                verification_type: Union[str, VerificationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.communication.models.VerificationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLATION_REQUESTED = "CancellationRequested"
        NOT_STARTED = "NotStarted"
        VERIFICATION_FAILED = "VerificationFailed"
        VERIFICATION_IN_PROGRESS = "VerificationInProgress"
        VERIFICATION_REQUESTED = "VerificationRequested"
        VERIFIED = "Verified"


    class azure.mgmt.communication.models.VerificationStatusRecord(_Model):
        error_code: Optional[str]
        status: Optional[Union[str, VerificationStatus]]


    class azure.mgmt.communication.models.VerificationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DKIM = "DKIM"
        DKIM2 = "DKIM2"
        DMARC = "DMARC"
        DOMAIN = "Domain"
        SPF = "SPF"


namespace azure.mgmt.communication.operations

    class azure.mgmt.communication.operations.CommunicationServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: CommunicationServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunicationServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunicationServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommunicationServiceResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def check_name_availability(
                self, 
                name_availability_parameters: NameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                name_availability_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                name_availability_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                **kwargs: Any
            ) -> CommunicationServiceResource: ...

        @overload
        def link_notification_hub(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                link_notification_hub_parameters: Optional[LinkNotificationHubParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LinkedNotificationHub: ...

        @overload
        def link_notification_hub(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                link_notification_hub_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LinkedNotificationHub: ...

        @overload
        def link_notification_hub(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                link_notification_hub_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LinkedNotificationHub: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CommunicationServiceResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[CommunicationServiceResource]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                **kwargs: Any
            ) -> CommunicationServiceKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationServiceKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationServiceKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationServiceKeys: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: CommunicationServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationServiceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationServiceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationServiceResource: ...


    class azure.mgmt.communication.operations.DomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_cancel_verification(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: VerificationParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_cancel_verification(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_cancel_verification(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: DomainResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DomainResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DomainResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DomainResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_initiate_verification(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: VerificationParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_initiate_verification(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_initiate_verification(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: UpdateDomainRequestParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DomainResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DomainResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DomainResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> DomainResource: ...

        @distributed_trace
        def list_by_email_service_resource(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DomainResource]: ...


    class azure.mgmt.communication.operations.EmailServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                parameters: EmailServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EmailServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EmailServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EmailServiceResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                parameters: EmailServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EmailServiceResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EmailServiceResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EmailServiceResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                **kwargs: Any
            ) -> EmailServiceResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EmailServiceResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[EmailServiceResource]: ...

        @distributed_trace
        def list_verified_exchange_online_domains(self, **kwargs: Any) -> List[str]: ...


    class azure.mgmt.communication.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.communication.operations.SenderUsernamesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                sender_username: str, 
                parameters: SenderUsernameResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SenderUsernameResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                sender_username: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SenderUsernameResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                sender_username: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SenderUsernameResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                sender_username: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                sender_username: str, 
                **kwargs: Any
            ) -> SenderUsernameResource: ...

        @distributed_trace
        def list_by_domains(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SenderUsernameResource]: ...


    class azure.mgmt.communication.operations.SmtpUsernamesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                smtp_username: str, 
                parameters: SmtpUsernameResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SmtpUsernameResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                smtp_username: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SmtpUsernameResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                smtp_username: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SmtpUsernameResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                smtp_username: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                smtp_username: str, 
                **kwargs: Any
            ) -> SmtpUsernameResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                communication_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SmtpUsernameResource]: ...


    class azure.mgmt.communication.operations.SuppressionListAddressesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                address_id: str, 
                parameters: SuppressionListAddressResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionListAddressResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                address_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionListAddressResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                address_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionListAddressResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                address_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                address_id: str, 
                **kwargs: Any
            ) -> SuppressionListAddressResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SuppressionListAddressResource]: ...


    class azure.mgmt.communication.operations.SuppressionListsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                parameters: SuppressionListResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionListResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionListResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SuppressionListResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                suppression_list_name: str, 
                **kwargs: Any
            ) -> SuppressionListResource: ...

        @distributed_trace
        def list_by_domain(
                self, 
                resource_group_name: str, 
                email_service_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SuppressionListResource]: ...


```